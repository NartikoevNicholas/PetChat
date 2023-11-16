from src.services.abstract_interfase import (
    AbstractUserRepository,
    AbstractUserHistoryRepository
)
from src.infrastructure.repository.adapters import SQLAlchemyAdapter
from src.infrastructure.repository import postgres_models as md


class UserRepository(AbstractUserRepository, SQLAlchemyAdapter):
    model = md.User


class UserHistoryRepository(AbstractUserHistoryRepository, SQLAlchemyAdapter):
    model = md.UserHistory
