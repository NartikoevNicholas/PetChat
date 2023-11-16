import asyncio
from uuid import UUID
import datetime as dt

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError
)

from src.core.config import DefaultSettings
from src.endpoints import exceptions as exc
from src.services import entities as et
from src.services.uow.abstract_uow import (
    AbstractMemoryStorageUOW,
    AbstractAuthServiceRepositoryUOW
)


class AuthService:
    def __init__(
        self,
        config: DefaultSettings,
        memory_uow: AbstractMemoryStorageUOW,
        repository_uow: AbstractAuthServiceRepositoryUOW
    ):
        self.config = config
        self.memory_uow = memory_uow
        self.repository_uow = repository_uow

    async def authenticate(self, schema: et.UserCredEmail) -> et.JWTToken:
        async with self.repository_uow as repo:
            user = await repo.user.find_one(schema.model_dump(exclude={'password'}))
            if not user or not self.config.pwd_context().verify(schema.password, user.hashed_password):
                raise exc.UnauthorizedHTTPException

            return self._get_access_and_refresh_token(user.id)

    async def verify_token(self, token: str) -> et.JWTPayload:
        async with self.memory_uow as mem:
            value = await mem.storage.get(token)
            if value is not None:
                raise exc.BadRequestJWTHTTPException
            return self._get_jwt_payload(token)

    async def refresh_token(self, token: et.JWTRefreshToken) -> et.JWTToken:
        async with self.memory_uow as mem:
            value = await mem.storage.get(token.refresh_token)
            if value is not None:
                raise exc.BadRequestJWTHTTPException

            payload = self._get_jwt_payload(token.refresh_token)
            if payload.token_type == et.JWTTypeToken.access:
                raise exc.BadRequestJWTHTTPException

            ex = payload.exp - dt.datetime.now(tz=payload.exp.tzinfo)
            await mem.storage.set(
                name=token.refresh_token,
                value='1',
                ex=ex.total_seconds().__ceil__()
            )
            return self._get_access_and_refresh_token(payload.user_id)

    async def logout(self, user_id: UUID, jwt_token: et.JWTToken):
        async with self.memory_uow as mem:
            access_payload = self._get_jwt_payload(jwt_token.access_token)
            refresh_payload = self._get_jwt_payload(jwt_token.refresh_token)

            if access_payload.user_id == refresh_payload.user_id == user_id:

                access_ex = access_payload.exp - dt.datetime.now(tz=access_payload.exp.tzinfo)
                refresh_ex = refresh_payload.exp - dt.datetime.now(tz=refresh_payload.exp.tzinfo)
                await asyncio.gather(
                    mem.storage.set(
                        name=jwt_token.access_token,
                        value='1',
                        ex=access_ex.total_seconds().__ceil__()
                    ),
                    mem.storage.set(
                        name=jwt_token.refresh_token,
                        value='1',
                        ex=refresh_ex.total_seconds().__ceil__()
                    )
                )
            else:
                raise exc.BadRequestLogoutHTTPException

    def _get_jwt_payload(self, jwt_token: str) -> et.JWTPayload:
        try:
            payload = self._decode_token(jwt_token)
            return et.JWTPayload(**payload)

        except ExpiredSignatureError:
            raise exc.BadRequestJWTExpiredHTTPException

        except InvalidSignatureError:
            raise exc.BadRequestJWTHTTPException

    def _get_access_and_refresh_token(self, user_id: UUID) -> et.JWTToken:
        now = dt.datetime.utcnow()

        access_token = self._encode_token(et.JWTPayload(
            user_id=user_id,
            token_type=et.JWTTypeToken.access,
            exp=now + dt.timedelta(seconds=self.config.EXPIRE_ACCESS_TOKEN)
        ))

        refresh_token = self._encode_token(et.JWTPayload(
            user_id=user_id,
            token_type=et.JWTTypeToken.refresh,
            exp=now + dt.timedelta(seconds=self.config.EXPIRE_REFRESH_TOKEN)
        ))

        return et.JWTToken(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def _encode_token(self, payload: et.JWTPayload) -> str:
        return jwt.encode(
            payload=payload.model_dump(),
            key=self.config.SECRET_KEY,
            algorithm=self.config.TOKEN_ALGORITHM,
        )

    def _decode_token(self, jwt_token: str) -> dict:
        return jwt.decode(
            jwt=jwt_token,
            key=self.config.SECRET_KEY,
            algorithms=self.config.TOKEN_ALGORITHM,
        )
