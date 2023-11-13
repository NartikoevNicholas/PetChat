from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from src.services.abstract_interfase import (
    SetType,
    AbstractMemoryStorage
)


class RedisMemoryStorage(AbstractMemoryStorage):
    def __init__(self, redis: Redis, pipeline: Pipeline):
        self.redis = redis
        self.pipeline = pipeline

    def lock(self, name: str, timeout: int = 5):
        self.redis.lock(f'Lock:{name}', timeout)

    async def get_time(self) -> float:
        t = await self.redis.time()
        return float(f'{t[0]}.{t[1]}')

    async def set(self, name: str, value: SetType, ex: int = None) -> None:
        if ex and ex > 0:
            await self.pipeline.set(name=name, value=value, ex=ex)
        else:
            await self.pipeline.set(name=name, value=value)

    async def get(self, key: str) -> bytes:
        return await self.redis.get(key)

    async def delete_one(self, key: str) -> None:
        await self.pipeline.delete(key)
