import redis
from app.core.config import settings

# singleton — same pattern as groq_client
_redis_client: redis.Redis | None = None

def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,  # return strings not bytes
        )
    return _redis_client

def is_redis_available() -> bool:
    try:
        get_redis_client().ping()
        return True
    except redis.ConnectionError:
        return False