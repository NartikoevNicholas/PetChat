import asyncio
import secrets
from uuid import UUID
from datetime import datetime
from typing import (
    Any,
    Union
)

from fastapi import Request
from passlib.context import CryptContext

from src.core.config import API
from src.services.entities import (
    UserDTO,
    UserEmailDTO,
    UserRequestDTO,
    UserUsernameDTO,
    UserPasswordDTO,
    UserResponseDTO,
    UserUpdatePassword,
    UserEmailPasswordDTO,
    UserUsernamePasswordDTO,
    BrokerUserEmailUpdate,
    BrokerUserReg,
    JWTPayload
)
from src.services.uow import abstract_uow as uow
from src.endpoints.exceptions import (
    BadRequestHTTPException,
    InvalidPasswordHTTPException,
    InvalidLinkHTTPException,
    UserNotFoundHTTPException,
    EmailBusyHTTPException,
    UsernameBusyHTTPException,

)


class UserService:
    def __init__(self,
                 config: dict,
                 crypt_context: CryptContext,
                 broker_uow: uow.AbstractBrokerUOW,
                 memory_uow: uow.AbstractMemoryStorageUOW,
                 repository_uow: uow.AbstractUserServiceRepositoryUOW) -> None:
        self.config = config
        self.crypt_context = crypt_context
        self.broker_uow = broker_uow
        self.memory_uow = memory_uow
        self.repository_uow = repository_uow

    async def me(self,
                 user_id: UUID) -> UserResponseDTO:
        async with self.repository_uow as repo:
            user = await repo.user.find_by_pk(user_id)
            return UserResponseDTO(**user.model_dump())

    async def registration(self,
                           request: Request,
                           schema: UserRequestDTO) -> None:
        """
        User registration, how it works:
        1. Check available username and email, if username or email exist, then call
           error 'Username is busy!' or 'Email is busy!'.
        2. Hashed password
        3. Save user in table
        4. Send email message for verify email
        5. Save 'is_active{separation}True' in memory storage for verify email
        """
        async with self.repository_uow as repo, self.memory_uow as mem, self.broker_uow as brok:
            # check data
            await self.available(UserEmailDTO(email=schema.email))
            await self.available(UserUsernameDTO(username=schema.username))

            # create user
            schema.hashed_password = self.crypt_context.hash(schema.hashed_password)

            user = await repo.user.add(schema)
            code = secrets.token_urlsafe(self.config['LENGTH_CODE'])
            link = f'{str(request.base_url)[:-1]}{API.user_email_verify_v1}/{user.id}/{code}'
            await asyncio.gather(
                brok.broker.email_reg(BrokerUserReg(username=user.username,
                                                    email=user.email,
                                                    link=link)),
                mem.storage.set(name=user.id.hex,
                                value=self._get_code('is_active', True, code),
                                ex=self.config['REG_EXP_TIME'])
            )

    async def email_verify(self,
                           user_id: UUID,
                           user_code: str) -> None:
        """
        Email verify, how it works:
        1. Get code from memory storage, if none, then call error 'Bad request!'
        2. Parse code 'field {separation} value {separation} code'
        3. Check url parameter 'user_code' with 'code', if they different, then
           call error 'Invalid link!'
        4.
        """
        async with self.repository_uow as repo, self.memory_uow as mem:
            code = await mem.storage.get(user_id.hex)
            if code is None: raise BadRequestHTTPException

            field, value, code = code.decode().split(self.config['SEP'])
            if code != user_code: raise InvalidLinkHTTPException
            await mem.storage.delete_one(user_id.hex)

            user = await repo.user.find_by_pk(user_id)
            patch = UserDTO(**{field: value})
            await asyncio.gather(
                repo.user_history.patch(user, patch.model_dump(exclude_none=True)),
                repo.user.update_by_pk(user_id, patch)
            )

    async def update_username(self,
                              user_id: UUID,
                              schema: UserUsernamePasswordDTO) -> UserResponseDTO:
        """
        1. Get user, check password
        2. Check available username
        3. Initialize UserDto() for update username
        4. Update user and log changes in 'user_history' table
        """
        async with self.repository_uow as repo:
            user = await repo.user.find_by_pk(user_id)
            if not self.crypt_context.verify(schema.password, user.hashed_password):
                raise InvalidPasswordHTTPException

            await self.available(UserUsernameDTO(username=schema.username))
            patch = UserDTO(username=schema.username)
            user, user_history = await asyncio.gather(
                repo.user.update_by_pk(user.id, patch),
                repo.user_history.patch(user, patch.model_dump(exclude_none=True))
            )
        return UserResponseDTO.model_validate(user.model_dump())

    async def update_email(self,
                           request: Request,
                           user_id: UUID,
                           schema: UserEmailPasswordDTO) -> UserResponseDTO:
        """
        1. Get user, check password
        2. Check available email
        3. Initialize UserDto() for update email
        4. Send message to email and save 'email{separation}{schema.email}' in memory storage
        """
        async with self.repository_uow as repo, self.memory_uow as mem, self.broker_uow as brok:
            user = await repo.user.find_by_pk(user_id)
            if not self.crypt_context.verify(schema.password, user.hashed_password):
                raise InvalidPasswordHTTPException

            await self.available(UserEmailDTO(email=schema.email))
            code = secrets.token_urlsafe(self.config['LENGTH_CODE'])
            link = f'{str(request.base_url)[:-1]}{API.user_email_verify_v1}/{user_id}/{code}'

            ex = self.config['REG_EXP_TIME']
            value = self._get_code('email', schema.email, code)
            send_email = BrokerUserEmailUpdate(email=schema.email, link=link)
            await asyncio.gather(
                brok.broker.email_upd(send_email),
                mem.storage.set(user_id.hex, value, ex)
            )
        return UserResponseDTO.model_validate(user.model_dump())

    async def update_password(self,
                              user_id: UUID,
                              schema: UserUpdatePassword) -> UserResponseDTO:
        """
        1. Get user, check password
        2. Hashed password
        3. Update user and log changes in 'user_history' table
        """
        async with self.repository_uow as repo:
            user = await repo.user.find_by_pk(user_id)
            if not self.crypt_context.verify(schema.password, user.hashed_password):
                raise InvalidPasswordHTTPException

            patch = UserDTO(hashed_password=self.crypt_context.hash(schema.new_password))
            user, user_history = await asyncio.gather(
                repo.user.update_by_pk(user.id, patch),
                repo.user_history.patch(user, patch.model_dump(exclude_none=True))
            )
        return UserResponseDTO.model_validate(user.model_dump())

    async def available(self,
                        schema: Union[UserEmailDTO, UserUsernameDTO]) -> None:
        """
        Check available username or email
        """
        async with self.repository_uow as repo:
            user: UserDTO = await repo.user.find_one(schema.model_dump())
            if not user: return

            exp = datetime.now(user.dt_created.tzinfo) - user.dt_created
            if not user.is_active and exp.total_seconds() > self.config['REG_EXP_TIME']:
                await repo.user.remove_one(schema.model_dump())
                return

            exp = datetime.now(user.dt_created.tzinfo) - user.dt_update
            if user.is_deleted and exp.total_seconds() > self.config['DEL_EXP_TIME']:
                await repo.user.remove_one(schema.model_dump())
                return

            if isinstance(schema, UserEmailDTO):
                raise EmailBusyHTTPException
            raise UsernameBusyHTTPException

    async def remove(self,
                     payload: JWTPayload,
                     access_token: str,
                     schema: UserPasswordDTO) -> None:
        """
        Remove user, how it works:
        1. Get user
        2. If user is None or user is deleted, then we call error
           'User not found!'
        3. Update field 'is_deleted'
        4. Log changes in 'user_history' table
        5. Save deleted token in memory storage
        """
        user_id = payload.user_id
        async with self.repository_uow as repo, self.memory_uow as mem:
            user = await repo.user.find_by_pk(user_id)

            if user is None or user.is_deleted:
                raise UserNotFoundHTTPException

            if not self.crypt_context.verify(schema.password, user.hashed_password):
                raise InvalidPasswordHTTPException

            patch = UserDTO(is_deleted=True)
            patch_dict = patch.model_dump(exclude_none=True)
            dt_ex = payload.exp - datetime.now(tz=payload.exp.tzinfo)
            total_seconds = int(dt_ex.total_seconds())

            await asyncio.gather(
                repo.user.update_by_pk(user_id, patch),
                repo.user_history.patch(user, patch_dict),
                mem.storage.set(access_token, user_id.hex, total_seconds)
            )

    def _get_code(self,
                  key: str,
                  value: Any,
                  code: str) -> str:
        return f'{key}{self.config["SEP"]}{value}{self.config["SEP"]}{code}'
