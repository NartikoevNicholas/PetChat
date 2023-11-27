import abc
from typing import (
    Any,
    Dict,
    List,
    Optional
)

from sqlalchemy import (
    select,
    insert,
    update,
    delete,
    and_
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import (
    NoResultFound,
    IntegrityError,
    MultipleResultsFound,
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from src.endpoints.exceptions import (
    DuplicateUserEmailHTTPException,
    DuplicateUserUsernameHTTPException
)
from src.services.abstract_interfase import AbstractRepository


class SQLAlchemyAdapter(AbstractRepository, abc.ABC):
    pydantic_model: BaseModel
    pydantic_create_model: BaseModel
    model: declarative_base

    def __init__(self, async_session: AsyncSession):
        self.async_session: AsyncSession = async_session

    async def add(self,
                  schema: 'pydantic_create_model') -> 'pydantic_model':
        """

        :param schema:
        :return:
        """
        try:
            response = await self.async_session.execute(
                insert(self.model)
                .values(schema.model_dump(exclude_none=True))
                .returning(self.model)
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj)
        except IntegrityError as e:
            if e.args[0].__contains__('email'):
                raise DuplicateUserEmailHTTPException
            else:
                raise DuplicateUserUsernameHTTPException

    async def add_many(self,
                       schemas: List['pydantic_create_model']) -> List['pydantic_model']:
        """

        :param schemas:
        :return:
        """
        response = await self.async_session.execute(
            insert(self.model)
            .returning(self.model),
            [schema.model_dump(exclude_none=True) for schema in schemas]
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]

    async def remove_one(self,
                         data: Dict[str, Any]) -> Optional['pydantic_model']:
        """

        :param data:
        :return:
        """
        params = []
        for name in self.model.__table__.c:
            value = data.get(name.key)
            if value is not None:
                params.append(name.__eq__(value))
        try:
            response = await self.async_session.execute(
                delete(self.model)
                .where(and_(*params))
                .returning(self.model)
            )
            obj = response.scalar_one()

            return self.pydantic_model.model_validate(obj)

        except NoResultFound:
            return None

        except MultipleResultsFound:
            raise

    async def update_by_pk(self,
                           pk: Any,
                           schema: 'pydantic_model') -> 'pydantic_model':
        """

        :param pk:
        :param schema:
        :return:
        """
        try:
            response = await self.async_session.execute(
                update(self.model)
                .where(self.model.id.__eq__(pk))
                .values(schema.model_dump(exclude_none=True))
                .returning(self.model)
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj)
        except IntegrityError as e:
            if e.args[0].__contains__('email'):
                raise DuplicateUserEmailHTTPException
            else:
                raise DuplicateUserUsernameHTTPException

    async def find_one(self,
                       data: Dict[str, Any]) -> Optional['pydantic_model']:
        """

        :param data:
        :return:
        """
        params = []
        for name in self.model.__table__.c:
            value = data.get(name.key)
            if value is not None:
                params.append(name.__eq__(value))
        try:
            response = await self.async_session.execute(
                select(self.model)
                .where(and_(*params))
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj) if obj else obj

        except NoResultFound:
            return None

        except MultipleResultsFound:
            raise

    async def find_by_pk(self,
                         pk: Any) -> Optional['pydantic_model']:
        """

        :param pk:
        :return:
        """
        response = await self.async_session.execute(
            select(self.model)
            .where(self.model.id.__eq__(pk))
            .with_for_update()
        )
        obj = response.scalar_one()
        return self.pydantic_model.model_validate(obj)

    async def find_all(self) -> List['pydantic_model']:
        """

        :return:
        """
        response = await self.async_session.execute(
            select(self.model)
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]
