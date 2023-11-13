from src.infrastructure.repository import (
    UserRepository,
    UserHistoryRepository
)

from .abstract_uow import AbstractUserServiceRepositoryUOW


class UserServiceRepositoryUOW(AbstractUserServiceRepositoryUOW):
    async def __aenter__(self):
        self.user = UserRepository(self.session)
        self.user_history = UserHistoryRepository(self.session)
