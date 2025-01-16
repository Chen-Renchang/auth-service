from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import models, schemas, crud, auth
from .database import SessionLocal, engine, get_db
from .config import settings
from .redis import redis_client

app = FastAPI()

# Создание таблиц в базе данных при запуске приложения
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Регистрация нового пользователя
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Регистрирует нового пользователя.
    Если email уже зарегистрирован, возвращает ошибку.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    return crud.create_user(db=db, user=user)

# Вход пользователя в систему
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Аутентифицирует пользователя и возвращает access и refresh токены.
    Если email или пароль неверны, возвращает ошибку.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный email или пароль")
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=15))
    refresh_token = auth.create_access_token(data={"sub": user.email}, expires_delta=timedelta(days=7))
    crud.add_login_history(db, user_id=user.id, user_agent="some_user_agent")  # Добавление записи в историю входов
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

# Схема OAuth2 для аутентификации через Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Создание access токена
def create_access_token(data: dict, expires_delta: timedelta):
    """
    Создает JWT токен с указанными данными и сроком действия.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Обновление access токена
@app.post("/refresh")
def refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    """
    Обновляет access токен с использованием refresh токена.
    Если refresh токен недействителен, возвращает ошибку.
    """
    try:
        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": token_data.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Обновление данных пользователя
@app.put("/user/update")
def update_user_data(user_data: schemas.UserUpdate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Обновляет email и/или пароль пользователя.
    Если токен недействителен, возвращает ошибку.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    db_user = crud.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    updated_user = crud.update_user(db, db_user, user_data)
    return updated_user

# Получение истории входов пользователя
@app.get("/user/history")
def get_user_history(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Возвращает историю входов пользователя.
    Если токен недействителен, возвращает ошибку.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    # Получение пользователя по email
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # Получение истории входов по user_id
    history = crud.get_login_history(db, user_id=user.id)
    return history

# Выход пользователя из системы
@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme)):
    """
    Добавляет токен в черный список Redis.
    Если токен недействителен, возвращает ошибку.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен")

    # Добавление токена в Redis как недействительного
    redis_client.set(token, "invalid", ex=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    return {"message": "Выход выполнен успешно"}