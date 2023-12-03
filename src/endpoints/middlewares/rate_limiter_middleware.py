from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from dependency_injector.wiring import inject, Provide

from src.core.containers import Container
from src.endpoints.exceptions import ManyRequestsHTTPException


class RateLimiterMiddleware:
    @inject
    async def __call__(self,
                       request: Request,
                       call_next: Callable,
                       rate_limiter_service=Provide[Container.rate_limiter_service]):
        try:
            await rate_limiter_service(request)
            response = await call_next(request)
        except ManyRequestsHTTPException as e:
            response = JSONResponse(e.detail, e.status_code, e.headers)
        except Exception as e:
            raise e

        return response
