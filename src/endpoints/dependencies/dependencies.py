from typing import (
    Tuple,
    Annotated
)

from fastapi import Depends
from dependency_injector.wiring import Provide

from src.core.containers import Container
from src.endpoints.middlewares import AuthMiddleware
from src.services.entities import JWTPayload
from src.services.use_case import (
    UserService,
    AuthService
)


user_depends: UserService = Depends(Provide[Container.user_service])

auth_depends: AuthService = Depends(Provide[Container.auth_service])

AuthUser = Annotated[Tuple[str, JWTPayload], Depends(AuthMiddleware())]
