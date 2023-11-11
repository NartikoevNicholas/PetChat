from typing import Optional

from sqlalchemy import select

from src.services.entities import UserEntity
from src.services.abstract_interfase import (
    AbstractUserRepository,
    AbstractUserHistoryRepository
)
from src.infrastructure.repository.adapters import SQLAlchemyAdapter

from .postgres_models import (
    User,
    UserHistory
)


class UserRepository(AbstractUserRepository, SQLAlchemyAdapter):
    model = User
    pydantic_model = UserEntity

    async def find_by_email(self, email: str) -> Optional[pydantic_model]:
        response = await self.async_session.execute(
            select(self.model)
            .where(self.model.email.__eq__(email))
            .with_for_update()
        )
        obj = response.scalar_one_or_none()
        return self.pydantic_model.model_validate(obj) if obj else None

    async def find_by_username(self, username: str) -> Optional[pydantic_model]:
        response = await self.async_session.execute(
            select(self.model)
            .where(self.model.username.__eq__(username))
            .with_for_update()
        )
        obj = response.scalar_one_or_none()
        return self.pydantic_model.model_validate(obj) if obj else None


class UserHistoryRepository(AbstractUserHistoryRepository, SQLAlchemyAdapter):
    model = UserHistory
