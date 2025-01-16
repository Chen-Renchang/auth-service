from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class LoginHistoryResponse(BaseModel):
    """
    Модель для ответа с историей входов.
    Используется для возврата данных о входе пользователя.
    """
    id: int  # Уникальный идентификатор записи
    user_id: int  # Идентификатор пользователя
    user_agent: str  # Информация о браузере или устройстве
    login_time: datetime  # Время входа

    class Config:
        from_attributes = True  # Разрешает создание модели из ORM-объекта

class TokenData(BaseModel):
    """
    Модель для хранения данных из JWT токена.
    """
    email: Optional[str] = None  # Email пользователя (может быть None)

class UserBase(BaseModel):
    """
    Базовая модель пользователя.
    Содержит общие поля для всех моделей, связанных с пользователем.
    """
    email: str  # Email пользователя

class UserCreate(UserBase):
    """
    Модель для создания нового пользователя.
    Наследует UserBase и добавляет поле пароля.
    """
    password: str  # Пароль пользователя

class UserUpdate(BaseModel):
    """
    Модель для обновления данных пользователя.
    Поля email и password являются опциональными.
    """
    email: Optional[str] = None  # Новый email (опционально)
    password: Optional[str] = None  # Новый пароль (опционально)

class User(UserBase):
    """
    Модель пользователя для ответа.
    Наследует UserBase и добавляет поле id.
    """
    id: int  # Уникальный идентификатор пользователя

    class Config:
        from_attributes = True  # Разрешает создание модели из ORM-объекта