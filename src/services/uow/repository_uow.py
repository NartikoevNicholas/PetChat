import typing as tp

from src.infrastructure.repository import (
    UserRepository,
    UserHistoryRepository
)
from src.services.uow.abstract_uow import (
    AbstractUserServiceRepositoryUOW,
    AbstractAuthServiceRepositoryUOW
)


class UserServiceRepositoryUOW(AbstractUserServiceRepositoryUOW):
    async def __aenter__(self) -> tp.Self:
        self.user = UserRepository(self.session)
        self.user_history = UserHistoryRepository(self.session)
        return self


class AuthServiceRepositoryUOW(AbstractAuthServiceRepositoryUOW):
    async def __aenter__(self) -> tp.Self:
        self.user = UserRepository(self.session)
        return self
