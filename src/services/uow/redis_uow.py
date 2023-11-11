from redis.asyncio import Redis

from src.infrastructure.memory_storage import RedisMemoryStorage

from .abstract_uow import AbstractMemoryStorageUOW


class RedisUOW(AbstractMemoryStorageUOW):

    def __init__(self, redis: Redis):
        self.redis = redis
        self.pipeline = redis.pipeline(transaction=True)

    async def __aenter__(self):
        self.storage = RedisMemoryStorage(
            redis=self.redis,
            pipeline=self.pipeline
        )

    async def commit(self) -> None:
        await self.pipeline.execute()

    async def rollback(self) -> None:
        await self.pipeline.discard()

    async def close(self) -> None:
        await self.pipeline.aclose()