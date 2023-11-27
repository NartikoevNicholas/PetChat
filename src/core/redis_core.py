from redis.asyncio import from_url


def get_redis_url(redis_settings: dict) -> str:
    return 'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'.format(**redis_settings)


def get_async_redis_client(redis_settings: dict):
    return from_url(get_redis_url(redis_settings))
