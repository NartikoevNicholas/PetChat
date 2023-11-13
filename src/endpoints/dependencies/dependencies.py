from fastapi import Depends

from dependency_injector.wiring import Provide

from src.core.containers import Container
from src.services.use_case import (
    UserService,
    RateLimiterService
)


user_depends: UserService = Depends(Provide[Container.user_service])

rate_limiter_depends: RateLimiterService = Depends(Provide[Container.rate_limiter_service])