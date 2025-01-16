from datetime import datetime  # Импорт модуля datetime для работы с датой и временем
from sqlalchemy.orm import Session
from . import models, schemas
from .auth import get_password_hash  # Импорт функции get_password_hash для хэширования пароля

def get_user_by_email(db: Session, email: str):
    """
    Возвращает пользователя по email.
    Если пользователь не найден, возвращает None.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Создает нового пользователя в базе данных.
    Хэширует пароль перед сохранением.
    """
    hashed_password = get_password_hash(user.password)  # Хэширование пароля
    db_user = models.User(email=user.email, password_hash=hashed_password)  # Создание объекта пользователя
    db.add(db_user)  # Добавление пользователя в сессию
    db.commit()  # Сохранение изменений в базе данных
    db.refresh(db_user)  # Обновление объекта пользователя
    return db_user

def update_user(db: Session, user: models.User, user_data: schemas.UserUpdate):
    """
    Обновляет данные пользователя (email и/или пароль).
    Если пароль изменен, он хэшируется перед сохранением.
    """
    if user_data.email:
        user.email = user_data.email  # Обновление email
    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)  # Хэширование нового пароля
    db.commit()  # Сохранение изменений в базе данных
    db.refresh(user)  # Обновление объекта пользователя
    return user

def add_login_history(db: Session, user_id: int, user_agent: str):
    """
    Добавляет запись в историю входов пользователя.
    """
    db_history = models.LoginHistory(
        user_id=user_id,  # ID пользователя
        user_agent=user_agent,  # Информация о браузере или устройстве
        login_time=datetime.utcnow()  # Время входа (текущее время в UTC)
    )
    db.add(db_history)  # Добавление записи в сессию
    db.commit()  # Сохранение изменений в базе данных
    db.refresh(db_history)  # Обновление объекта записи
    return db_history

def get_login_history(db: Session, user_id: int):
    """
    Возвращает историю входов пользователя по его ID.
    """
    return db.query(models.LoginHistory).filter(models.LoginHistory.user_id == user_id).all()