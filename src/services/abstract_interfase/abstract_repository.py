import abc
import typing as tp

from pydantic import BaseModel

from src.services import entities as et


class AbstractRepository(abc.ABC):
    pydantic_model: BaseModel
    pydantic_create_model: BaseModel

    @abc.abstractmethod
    async def add(self, schema: 'pydantic_create_model') -> 'pydantic_model':
        pass

    @abc.abstractmethod
    async def add_many(self, schema: tp.List['pydantic_create_model']) -> tp.List['pydantic_model']:
        pass

    async def remove_by_pk(self, pk: tp.Any) -> 'pydantic_model':
        pass

    @abc.abstractmethod
    async def update_by_pk(self, pk: tp.Any, schema: 'pydantic_model') -> 'pydantic_model':
        pass

    @abc.abstractmethod
    async def find_one(self, data: tp.Dict[str, tp.Any]) -> tp.Optional['pydantic_model']:
        pass

    @abc.abstractmethod
    async def find_by_pk(self, pk: tp.Any) -> tp.Optional['pydantic_model']:
        pass

    @abc.abstractmethod
    async def find_all(self) -> tp.List['pydantic_model']:
        pass


class AbstractUserRepository(AbstractRepository, abc.ABC):
    pydantic_model = et.User
    pydantic_create_model = et.UserDTO


class AbstractUserHistoryRepository(AbstractRepository, abc.ABC):
    pydantic_model = et.UserHistory
    pydantic_create_model = et.UserHistoryDTO

    async def patch(self, user: et.User, patch: dict) -> tp.List[pydantic_model]:
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
