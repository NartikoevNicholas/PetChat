from redis.asyncio import Redis
from redis.asyncio.client import Pipeline

from src.services.abstract_interface import (
    SetType,
    AbstractMemoryStorage,
    AbstractReadlockMemoryStorage
)


class ReadlockMemoryStorage(AbstractReadlockMemoryStorage):
    def __init__(self, redis: Redis, name: str, timeout: int):
        self.lock = redis.lock(name, timeout)

    async def __aenter__(self):
        await self.lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.lock.release()


class RedisMemoryStorage(AbstractMemoryStorage):
    def __init__(self, redis: Redis, pipeline: Pipeline):
        self.redis = redis
        self.pipeline = pipeline

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

    def readlock(self, name: str, timeout: int = 2) -> ReadlockMemoryStorage:
        return ReadlockMemoryStorage(self.redis, name, timeout)
