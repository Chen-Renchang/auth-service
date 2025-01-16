from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """
    Модель пользователя.
    Хранит информацию о пользователях, включая email и хэшированный пароль.
    """
    __tablename__ = "users"  # Название таблицы в базе данных
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор пользователя
    email = Column(String, unique=True, index=True)  # Уникальный email пользователя
    password_hash = Column(String)  # Хэшированный пароль пользователя

class LoginHistory(Base):
    """
    Модель истории входов.
    Хранит информацию о входах пользователей в систему.
    """
    __tablename__ = "login_history"  # Название таблицы в базе данных
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор записи
    user_id = Column(Integer, ForeignKey("users.id"))  # Внешний ключ на таблицу users
    user_agent = Column(String)  # Информация о браузере или устройстве пользователя
    login_time = Column(DateTime)  # Время входа пользователя