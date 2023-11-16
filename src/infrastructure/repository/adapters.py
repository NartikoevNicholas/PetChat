import abc
import typing as tp

from pydantic import BaseModel
import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.endpoints import exceptions as exc
from src.services.abstract_interfase import AbstractRepository


class SQLAlchemyAdapter(AbstractRepository, abc.ABC):
    pydantic_model: BaseModel
    pydantic_create_model: BaseModel
    model: declarative_base

    def __init__(self, async_session: AsyncSession):
        self.async_session: AsyncSession = async_session

    async def add(self, schema: 'pydantic_create_model') -> 'pydantic_model':
        try:
            response = await self.async_session.execute(
                sa.insert(self.model)
                .values(schema.model_dump(exclude_none=True))
                .returning(self.model)
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj)
        except IntegrityError as e:
            if e.args[0].contains('email'):
                raise exc.DuplicateUserEmailHTTPException
            else:
                raise exc.DuplicateUserUsernameHTTPException

    async def add_many(self, schemas: tp.List['pydantic_create_model']) -> tp.List['pydantic_model']:
        response = await self.async_session.execute(
            sa.insert(self.model)
            .returning(self.model),
            [schema.model_dump(exclude_none=True) for schema in schemas]
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]

    async def remove_by_pk(self, pk: tp.Any) -> 'pydantic_model':
        response = await self.async_session.execute(
            sa.delete(self.model)
            .where(self.model.id.__eq__(pk))
            .returning(self.model)
        )
        obj = response.scalar_one()
        return self.pydantic_model.model_validate(obj)

    async def update_by_pk(self, pk: tp.Any, schema: 'pydantic_model') -> 'pydantic_model':
        try:
            response = await self.async_session.execute(
                sa.update(self.model)
                .where(self.model.id.__eq__(pk))
                .values(schema.model_dump(exclude_none=True))
                .returning(self.model)
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj)
        except IntegrityError as e:
            if e.args[0].contains('email'):
                raise exc.DuplicateUserEmailHTTPException
            else:
                raise exc.DuplicateUserUsernameHTTPException

    async def find_one(self, data: tp.Dict[str, tp.Any]) -> tp.Optional['pydantic_model']:
        params = []
        for name in self.model.__table__.c:
            value = data.get(name.key)
            if value is not None:
                params.append(name.__eq__(value))

        response = await self.async_session.execute(
            sa.select(self.model)
            .where(sa.and_(*params))
        )
        obj = response.scalar()
        return self.pydantic_model.model_validate(obj) if obj else obj

    async def find_by_pk(self, pk: tp.Any) -> tp.Optional['pydantic_model']:
        response = await self.async_session.execute(
            sa.select(self.model)
            .where(self.model.id.__eq__(pk))
            .with_for_update()
        )
        obj = response.scalar_one()
        return self.pydantic_model.model_validate(obj)

    async def find_all(self) -> tp.List['pydantic_model']:
        response = await self.async_session.execute(
            sa.select(self.model)
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]
