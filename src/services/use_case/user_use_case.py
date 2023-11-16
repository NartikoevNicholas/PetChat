import asyncio
import datetime as dt
import secrets
from uuid import UUID

from fastapi import Request

from src.core.config import DefaultSettings
from src.services import entities as et
from src.services.uow import abstract_uow as uow
from src.endpoints import exceptions as exc


class UserService:
    def __init__(
        self,
        config: DefaultSettings,
        broker_uow: uow.AbstractBrokerUOW,
        memory_uow: uow.AbstractMemoryStorageUOW,
        repository_uow: uow.AbstractUserServiceRepositoryUOW,
    ):
        self.config = config
        self.broker_uow = broker_uow
        self.memory_uow = memory_uow
        self.repository_uow = repository_uow

    async def registration(self, request: Request, schema: et.UserDTO) -> None:
        """
        User registration
        """
        async with self.repository_uow as repo, self.memory_uow, self.broker_uow:
            try:
                # create user, if a possible
                user = await repo.user.find_one(schema.model_dump(include={'email'}))
                if user:
                    dt_now = dt.datetime.now(user.dt_created.tzinfo)
                    expire_time = dt_now - user.dt_created
                    if expire_time.total_seconds() < self.config.EXPIRE_TIME:
                        raise exc.DuplicateUserEmailHTTPException

                    user.dt_created = dt_now
                    user = await repo.user.update_by_pk(user.id, user)
                else:
                    user = await repo.user.add(schema)

                # save code and send email
                code = secrets.token_urlsafe(self.config.LENGTH_USER_CODE)
                user_email = et.BrokerUserEmail(
                    username=user.username,
                    email=user.email,
                    link=self.config.API.email_verify_api(request.base_url, user.id, code)
                )
                await asyncio.gather(
                    self.broker_uow.broker.send_registration_queue(user_email),
                    self.memory_uow.storage.set(user.id.hex, code, self.config.EXPIRE_TIME),
                )

            except [
                exc.DuplicateUserEmailHTTPException,
                exc.DuplicateUserUsernameHTTPException
            ] as e:
                raise e

    async def email_verify(self, user_id: UUID, user_code: str) -> bool:
        async with self.repository_uow as repo, self.memory_uow as mem:
            value = await mem.storage.get(user_id.hex)
            if not value or value.decode() != user_code: return False
            await mem.storage.delete_one(user_id.hex)

            user = await repo.user.find_by_pk(user_id)
            if not user or user.is_active: return False

            patch = {'is_active': True}
            await asyncio.gather(
                repo.user_history.patch(user, patch),
                repo.user.update_by_pk(user_id, et.User(**patch))
            )
            return True

    async def available_email(self, schema: et.UserEmail) -> bool:
        async with self.repository_uow as repo:
            user = await repo.user.find_one(schema.model_dump())
            if not user: return True

            expire_time = dt.datetime.now(user.dt_created.tzinfo) - user.dt_created
            if not user.is_active and expire_time.total_seconds() > self.config.EXPIRE_TIME:
                return True
            return False

    async def available_username(self, schema: et.UserUsername) -> bool:
        async with self.repository_uow as repo:
            user = await repo.user.find_one(schema.model_dump())
            return False if user else True
