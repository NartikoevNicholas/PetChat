from abc import (
    ABC,
    abstractmethod
)

from typing import (
    Any,
    List,
    Optional
)

from pydantic import BaseModel

from src.services.entities import (
    UserEntity,
    UserCreateEntity,
    UserHistoryEntity,
    UserHistoryCreateEntity
)


class AbstractRepository(ABC):
    pydantic_model: BaseModel
    pydantic_create_model: BaseModel


    @abstractmethod
    async def add(self, schema: 'pydantic_create_model') -> 'pydantic_model':
        pass

    @abstractmethod
    async def add_many(self, schema: List['pydantic_create_model']) -> List['pydantic_model']:
        pass

    async def remove_by_pk(self, pk: Any) -> 'pydantic_model':
        pass

    @abstractmethod
    async def update_by_pk(self, pk: Any, schema: 'pydantic_model') -> 'pydantic_model':
        pass

    @abstractmethod
    async def find_by_pk(self, pk: Any) -> Optional['pydantic_model']:
        pass

    @abstractmethod
    async def find_all(self) -> List['pydantic_model']:
        pass


class AbstractUserRepository(AbstractRepository, ABC):
    pydantic_model = UserEntity
    pydantic_create_model = UserCreateEntity

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[pydantic_model]:
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[pydantic_model]:
        pass


class AbstractUserHistoryRepository(AbstractRepository, ABC):
    pydantic_model = UserHistoryEntity
    pydantic_create_model = UserHistoryCreateEntity

    async def patch(self, user: UserEntity, patch: dict) -> List[pydantic_model]:
        result = []
        old_data = user.model_dump()
        for field, value in patch.items():
            result.append(
                self.pydantic_create_model(
                    user_id=user.id,
                    update_field=field,
                    old_value=str(old_data[field]),
                    new_value=str(value)
                )
            )
        return await self.add_many(result)
