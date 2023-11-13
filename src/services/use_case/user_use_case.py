import asyncio

import datetime

from uuid import UUID

from fastapi import Request

from src.endpoints.exceptions import DuplicateHTTPException
from src.services.entities import (
    UserEntity,
    UserCreateEntity,
    BrokerUserEmailEntity
)
from src.services.uow.abstract_uow import (
    AbstractBrokerUOW,
    AbstractMemoryStorageUOW,
    AbstractUserServiceRepositoryUOW,
)
from src.utils import (
    generate_code,
    hash_string
)


class UserService:
    def __init__(
        self,
        config,
        broker_uow: AbstractBrokerUOW,
        memory_uow: AbstractMemoryStorageUOW,
        repository_uow: AbstractUserServiceRepositoryUOW,
    ):
        self.config = config
        self.broker_uow = broker_uow
        self.memory_uow = memory_uow
        self.repository_uow = repository_uow

    async def registration(self, request: Request,  schema: UserCreateEntity) -> None:
        """
        User registration
        """
        async with self.repository_uow, self.memory_uow, self.broker_uow:
            try:
                # create hash user and generate code
                schema.hashed_password = hash_string(schema.hashed_password)
                code = generate_code(
                    code_length=self.config['LENGTH_USER_CODE'],
                    is_punctuation=False
                )

                # create user, if a possible
                user = await self.repository_uow.user.find_by_email(schema.email)
                if user:
                    dt_now = datetime.datetime.now(user.dt_created.tzinfo)
                    expire_time = dt_now - user.dt_created
                    if expire_time.total_seconds() < self.config['EXPIRE_TIME']:
                        raise DuplicateHTTPException('email already exists')

                    user.dt_created = dt_now
                    user = await self.repository_uow.user.update_by_pk(user.id, user)
                else:
                    user = await self.repository_uow.user.add(schema)

                # save code and send email
                user_email = BrokerUserEmailEntity(
                    username=user.username,
                    email=user.email,
                    link=f'{request.url}/verify/{user.id}/{code}'
                )
                await asyncio.gather(
                    self.broker_uow.broker.send_registration_queue(user_email),
                    self.memory_uow.storage.set(user.id.hex, code, self.config['EXPIRE_TIME']),
                )
            except DuplicateHTTPException:
                raise

    async def email_verify(self, user_id: UUID, user_code: str) -> bool:
        async with self.repository_uow, self.memory_uow:
            value = await self.memory_uow.storage.get(key=user_id.hex)
            if not value or value.decode() != user_code: return False
            await self.memory_uow.storage.delete_one(user_id.hex)

            user = await self.repository_uow.user.find_by_pk(user_id)
            if not user or user.is_active: return False

            patch = {'is_active': True}
            await asyncio.gather(
                self.repository_uow.user_history.patch(user, patch),
                self.repository_uow.user.update_by_pk(user_id, UserEntity(**patch))
            )
            return True

    async def available_email(self, email: str) -> bool:
        async with self.repository_uow:
            user = await self.repository_uow.user.find_by_email(email)
            if not user: return True

            expire_time = datetime.datetime.now(user.dt_created.tzinfo) - user.dt_created
            if not user.is_active and expire_time.total_seconds() > self.config['EXPIRE_TIME']:
                return True
            return False

    async def available_username(self, username: str) -> bool:
        async with self.repository_uow:
            user = await self.repository_uow.user.find_by_username(username)
            return False if user else True
