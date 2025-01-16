from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения.
    Настройки загружаются из переменных окружения или файла .env.
    """
    REDIS_HOST: str  # Хост Redis
    REDIS_PORT: int  # Порт Redis
    DB_USER: str  # Имя пользователя базы данных
    DB_PASSWORD: str  # Пароль базы данных
    DB_NAME: str  # Название базы данных
    DB_HOST: str  # Хост базы данных
    DB_PORT: str  # Порт базы данных
    JWT_SECRET_KEY: str  # Секретный ключ для JWT
    JWT_ALGORITHM: str = "HS256"  # Алгоритм шифрования JWT (по умолчанию HS256)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Время жизни access токена в минутах (по умолчанию 15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Время жизни refresh токена в днях (по умолчанию 7)

    class Config:
        """
        Конфигурация для загрузки переменных окружения из файла .env.
        """
        env_file = ".env"

# Создание экземпляра настроек
settings = Settings()