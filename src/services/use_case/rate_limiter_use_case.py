from fastapi import Request

from src.endpoints.exceptions import ManyRequestsHTTPException
from src.services.uow.abstract_uow import AbstractMemoryStorageUOW


class RateLimiterService:
    def __init__(
        self,
        config,
        memory_uow: AbstractMemoryStorageUOW,
    ):
        self.config = config
        self.memory_uow = memory_uow

    async def __call__(self, request: Request, *args, **kwargs):
        if not self.config['DEBUG']:
            async with self.memory_uow:
                ip = request.client.host
                separation = 1 / self.config['REQUEST_PER_SECOND']
                redis_time = await self.memory_uow.storage.get_time()

                last_request = await self.memory_uow.storage.get(ip)
                if last_request is None:
                    last_request = redis_time
                else:
                    last_request = float(last_request)

                if last_request - redis_time <= separation:
                    new_last_request = max(last_request, redis_time) + separation
                    await self.memory_uow.storage.set(ip, new_last_request)
                else:
                    raise ManyRequestsHTTPException
