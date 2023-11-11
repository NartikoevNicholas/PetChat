from redis.asyncio import from_url

from .config import get_config


settings = get_config()


async def get_async_redis_client():
    return from_url(settings.REDIS.get_url)
