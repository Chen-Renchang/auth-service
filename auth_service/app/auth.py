from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .schemas import TokenData
from .config import settings
from .database import get_db
from .models import User

# Контекст для хэширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема OAuth2 для аутентификации через Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Проверка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Сравнивает введенный пароль с хэшированным паролем в базе данных.
    """
    return pwd_context.verify(plain_password, hashed_password)

# Генерация хэша пароля
def get_password_hash(password: str) -> str:
    """
    Хэширует пароль для безопасного хранения в базе данных.
    """
    return pwd_context.hash(password)

# Создание access токена
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    """
    Создает JWT токен с указанными данными и сроком действия.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})  # Устанавливает срок действия токена
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# Декодирование токена
def decode_token(token: str) -> dict:
    """
    Декодирует JWT токен и возвращает его payload.
    Если токен недействителен, выбрасывает исключение.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Получение текущего пользователя (зависимость)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Возвращает текущего пользователя на основе JWT токена.
    Если токен недействителен или пользователь не найден, выбрасывает исключение.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")  # Извлекает email из payload токена
    if email is None:
        raise credentials_exception
    token_data = Token