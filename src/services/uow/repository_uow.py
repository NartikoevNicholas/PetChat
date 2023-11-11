from src.infrastructure.repository import (
    UserRepository,
    UserHistoryRepository
)

from .abstract_uow import AbstractUserUseCaseRepositoryUOW


class UserUseCaseRepositoryUOW(AbstractUserUseCaseRepositoryUOW):
    async def __aenter__(self):
        self.user = UserRepository(self.session)
        self.user_history = UserHistoryRepository(self.session)
