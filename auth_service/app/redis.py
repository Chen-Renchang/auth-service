import redis
from .config import settings

# Инициализация клиента Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,  # Хост Redis (например, localhost или IP-адрес)
    port=settings.REDIS_PORT,  # Порт Redis (по умолчанию 6379)
    db=0  # Номер базы данных Redis (по умолчанию 0)
)