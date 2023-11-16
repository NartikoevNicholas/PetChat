from fastapi import Depends
from dependency_injector.wiring import inject

from src.core.config import get_config
from src.endpoints.dependencies import auth_depends
from src.endpoints.exceptions import BadRequestJWTHTTPException
from src.services import entities as et


settings = get_config()


class AuthMiddleware:
    @staticmethod
    @inject
    async def verify_access_token(
        token: str = Depends(settings.oauth2_schema()),
        auth_service=auth_depends
    ) -> et.JWTPayload:
        jwt_payload = await auth_service.verify_token(token)
        if jwt_payload.token_type != et.JWTTypeToken.access:
            raise BadRequestJWTHTTPException
        return jwt_payload
