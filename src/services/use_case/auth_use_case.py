import asyncio
import inspect
from uuid import UUID
from typing import Union
from datetime import (
    datetime,
    timedelta
)

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError
)
from passlib.context import CryptContext

from src.core.config import DefaultSettings
from src.endpoints.exceptions import (
    UnauthorizedHTTPException,
    UserNotFoundHTTPException,
    TokenInvalidHTTPException,
    TokenExpiredHTTPException,
    TokenDeletedHTTPException,
    TokenLogoutHTTPException,
    TokenTypeInvalidHTTPException,
    NeedEmailVerifyHTTPException,
)
from src.services.entities import (
    UserDTO,
    JWTToken,
    JWTPayload,
    JWTTypeToken,
    JWTRefreshToken,
    LoginType,
)
from src.services.uow.abstract_uow import (
    AbstractMemoryStorageUOW,
    AbstractAuthServiceRepositoryUOW
)


class AuthService:
    def __init__(self,
                 config: DefaultSettings,
                 crypt_context: CryptContext,
                 memory_uow: AbstractMemoryStorageUOW,
                 repository_uow: AbstractAuthServiceRepositoryUOW) -> None:
        self.config = config
        self.crypt_context = crypt_context
        self.memory_uow = memory_uow
        self.repository_uow = repository_uow

    async def authenticate(self, schema: LoginType) -> JWTToken:
        """
        Authenticate user, how it works:
        1. Get user, if user is None or user is deleted, then
           call error 'Incorrect username or password!'
        2. Check user password and credentials, if they difference, then
           call error 'User not Found!'.
        3. If user isn't active, then we check time registration, if less
           'REG_EXP_TIME', then call error 'Need verify email!', else
           'Incorrect username or password!'
        4. Create access and refresh token
        5. Save refresh-token in memory storage
        6. Return token
        """
        async with self.repository_uow as repo, self.memory_uow as mem:
            credentials = schema.model_dump(exclude={'password'})
            user: UserDTO = await repo.user.find_one(credentials)

            if not user or user.is_deleted:
                raise UserNotFoundHTTPException

            if not self.crypt_context.verify(schema.password, user.hashed_password):
                raise UnauthorizedHTTPException

            if not user.is_active:
                expire = datetime.now(tz=user.dt_created.tzinfo) - user.dt_created
                if expire.total_seconds() < self.config['REG_EXP_TIME']:
                    raise NeedEmailVerifyHTTPException
                raise UnauthorizedHTTPException
            token = self._get_access_and_refresh_token(user.id)

            await mem.storage.set(name=token.refresh_token,
                                  value=user.id.hex,
                                  ex=self.config['REFRESH_EXP_TIME'])
            return token

    async def verify_token(self, token: str) -> JWTPayload:
        """
        Verify token, how it works:
        1. Get payload
        2. Check token type if type isn't access, then call error
           'Bad jwt token!'
        3. Get value in memory storage, if value isn't none, then call
           error 'Bad jwt token!'
        4. Return payload
        """
        async with self.memory_uow as mem:
            payload = self._get_payload(token)
            if payload.type != JWTTypeToken.access:
                raise TokenTypeInvalidHTTPException

            value = await mem.storage.get(token)
            if value is not None:
                raise TokenInvalidHTTPException
            return payload

    async def refresh_token(self, token: JWTRefreshToken) -> JWTToken:
        """
        Refresh token, how it works:
        1. Get payload and check your type. If your type isn't refresh-type,
           then call error 'Bad Jwt token!'
        2. Create readlock for memory storage
        3. Get from memory storage refresh-token value. If value is None, then
           call error 'Bad Jwt token!'
        4. Check value is deleted?. If token is deleted, then call error 'Bad Jwt token!'
        5. Check user. If user is deleted, then call error 'Token is deleted!'
        6. Create new access and refresh token
        7. Delete old refresh-token and save new token
        """
        async with self.repository_uow as repo, self.memory_uow as mem:
            payload = self._get_payload(token.refresh_token)
            user_id = payload.user_id
            if payload.type != JWTTypeToken.refresh:
                raise TokenTypeInvalidHTTPException

            func_name = inspect.currentframe().f_code.co_name
            async with mem.storage.readlock(func_name + user_id.hex):
                value = await mem.storage.get(token.refresh_token)
                if value is None:
                    raise TokenInvalidHTTPException

                user = await repo.user.find_by_pk(user_id)
                if not user or user.is_deleted:
                    raise TokenDeletedHTTPException

                ex = self.config['REFRESH_EXP_TIME']
                new_token = self._get_access_and_refresh_token(user_id)
                await asyncio.gather(
                    mem.storage.delete_one(token.refresh_token),
                    mem.storage.set(new_token.refresh_token, user_id.hex, ex)
                )
        return new_token

    async def logout(self, user_id: UUID, token: JWTToken) -> None:
        """
        1. Get access-payload and refresh-payload
        2. Check 'access-payload.user_id' == 'user_id' == 'refresh-payload.user_id',
           if they different, then call error 'Invalid logout'
        3. Create readlock for memory storage
        4. Check exist refresh-token, if not, then call error 'Bad jwt token!'
        4. Delete old refresh token
        5. Save access-token in memory storage
        """
        async with self.memory_uow as mem:
            refresh_payload = self._get_payload(token.refresh_token)
            access_payload = self._get_payload(token.access_token)

            if refresh_payload.user_id != access_payload.user_id != user_id:
                raise TokenLogoutHTTPException

            func_name = inspect.currentframe().f_code.co_name
            async with mem.storage.readlock(func_name + user_id.hex):
                if await mem.storage.get(token.refresh_token) is None:
                    raise TokenInvalidHTTPException

                dt_ex = access_payload.exp - datetime.now(tz=access_payload.exp.tzinfo)
                ex = int(dt_ex.total_seconds())
                await asyncio.gather(
                    mem.storage.delete_one(token.refresh_token),
                    mem.storage.set(token.access_token, user_id.hex, ex)
                )

    def _get_access_and_refresh_token(self, user_id: UUID) -> JWTToken:
        now = datetime.utcnow()
        timestamp = now.timestamp()

        data = [
            (JWTTypeToken.access, now + timedelta(seconds=self.config['ACCESS_EXP_TIME'])),
            (JWTTypeToken.refresh, now + timedelta(seconds=self.config['REFRESH_EXP_TIME']))
        ]

        token = {}
        for token_type, exp in data:
            tmp_payload = JWTPayload(user_id=user_id,
                                     type=token_type,
                                     exp=exp,
                                     iat=timestamp)
            token[token_type.value] = self._encode_token(tmp_payload)

        return JWTToken(**token)

    def _get_payload(self, token: Union[str | bytes]) -> JWTPayload:
        try:
            payload = self._decode_token(token)
            return JWTPayload(**payload)

        except ExpiredSignatureError:
            raise TokenExpiredHTTPException

        except InvalidSignatureError:
            raise TokenInvalidHTTPException

    def _encode_token(self, payload: JWTPayload) -> str:
        return jwt.encode(payload=payload.model_payload(),
                          key=self.config['SECRET_KEY'],
                          algorithm=self.config['TOKEN_ALGORITHM'])

    def _decode_token(self, jwt_token: Union[str | bytes]) -> dict:
        return jwt.decode(jwt=jwt_token,
                          key=self.config['SECRET_KEY'],
                          algorithms=self.config['TOKEN_ALGORITHM'])
