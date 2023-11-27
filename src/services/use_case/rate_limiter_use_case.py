import inspect

from fastapi import Request

from src.core.config import DefaultSettings
from src.endpoints.exceptions import ManyRequestsHTTPException
from src.services.uow.abstract_uow import AbstractMemoryStorageUOW


class RateLimiterService:
    def __init__(self,
                 config: DefaultSettings,
                 memory_uow: AbstractMemoryStorageUOW):
        self.period = 1
        self.config = config
        self.memory_uow = memory_uow

    async def __call__(self,
                       request: Request,
                       *args,
                       **kwargs) -> None:
        """
        __call__ makes sure that the user has not exceeded the allowed
        number of requests per second. If the user has exceeded allowed number request, then
        an error occurs '429 too many request'.
        Example: if count request equal 10 and period 60 sec, then rps equal
        1 request pre 6 second.
        Period is const and equal to 1
        """
        if not self.config['DEBUG']:
            async with self.memory_uow as mem:
                result = True
                ip = request.client.host
                separation = self.period / self.config['REQUEST_PER_SECOND']
                redis_time = await mem.storage.get_time()

                func_name = inspect.currentframe().f_code.co_name
                async with mem.storage.readlock(func_name + ip):
                    last_request = await mem.storage.get(ip)
                    if last_request is None:
                        last_request = redis_time
                    else:
                        last_request = float(last_request)

                    if last_request - redis_time <= separation:
                        new_last_request = max(last_request, redis_time) + separation
                        await mem.storage.set(ip, new_last_request)
                        result = False

                    if result:
                        raise ManyRequestsHTTPException
