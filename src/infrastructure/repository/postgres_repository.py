from src.services.abstract_interfase import (
    AbstractUserRepository,
    AbstractUserHistoryRepository
)
from src.infrastructure.repository.adapters import SQLAlchemyAdapter
from src.infrastructure.repository.postgres_models import (
    User,
    UserHistory
)


class UserRepository(AbstractUserRepository, SQLAlchemyAdapter):
    model = User


class UserHistoryRepository(AbstractUserHistoryRepository, SQLAlchemyAdapter):
    model = UserHistory
