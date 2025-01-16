from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# URL для подключения к базе данных
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# Создание движка базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для декларативных моделей
Base = declarative_base()

# Зависимость для получения сессии базы данных
def get_db():
    """
    Генератор, который предоставляет сессию базы данных.
    После завершения работы сессия автоматически закрывается.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()