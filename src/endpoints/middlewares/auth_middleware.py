from typing import Tuple

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from dependency_injector.wiring import (
    inject,
    Provide
)

from src.core.containers import Container
from src.services.entities import JWTPayload
from src.services.use_case import AuthService


oauth2_schema = OAuth2PasswordBearer(tokenUrl='')


class AuthMiddleware:
    @inject
    async def __call__(self,
                       auth_service: AuthService = Depends(Provide[Container.auth_service]),
                       token: str = Depends(oauth2_schema)) -> Tuple[str, JWTPayload]:
        """
        The AuthMiddleware check token
        """
        payload = await auth_service.verify_token(token)
        return token, payload
