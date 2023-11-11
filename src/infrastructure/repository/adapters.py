from abc import ABC

from typing import (
    Any,
    List,
    Optional
)

from pydantic import BaseModel

from sqlalchemy import (
    insert,
    delete,
    update,
    select
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.endpoints.exceptions import DuplicateHTTPException
from src.services.abstract_interfase import AbstractRepository


class SQLAlchemyAdapter(AbstractRepository, ABC):
    pydantic_model: BaseModel
    pydantic_create_model: BaseModel
    model: declarative_base

    def __init__(self, async_session: AsyncSession):
        self.async_session: AsyncSession = async_session

    async def add(self, schema: 'pydantic_create_model') -> 'pydantic_model':
        try:
            response = await self.async_session.execute(
                insert(self.model)
                .values(schema.model_dump(exclude_none=True))
                .returning(self.model)
            )
            obj = response.scalar_one()
            return self.pydantic_model.model_validate(obj)
        except IntegrityError as e:
            back, key, front = e.args[0].partition('DETAIL:')
            raise DuplicateHTTPException(content=front.strip())

    async def add_many(self, schemas: List['pydantic_create_model']) -> List['pydantic_model']:
        response = await self.async_session.execute(
            insert(self.model)
            .returning(self.model),
            [schema.model_dump(exclude_none=True) for schema in schemas]
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]

    async def remove_by_pk(self, pk: Any) -> 'pydantic_model':
        response = await self.async_session.execute(
            delete(self.model)
            .where(self.model.id.__eq__(pk))
            .returning(self.model)
        )
        obj = response.scalar_one()
        return self.pydantic_model.model_validate(obj)

    async def update_by_pk(self, pk: Any, schema: 'pydantic_model') -> 'pydantic_model':
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
            back, key, front = e.args[0].partition('DETAIL:')
            raise DuplicateHTTPException(content=front.strip())

    async def find_by_pk(self, pk: Any) -> Optional['pydantic_model']:
        response = await self.async_session.execute(
            select(self.model)
            .where(self.model.id.__eq__(pk))
            .with_for_update()
        )
        obj = response.scalar_one()
        return self.pydantic_model.model_validate(obj)

    async def find_all(self) -> List['pydantic_model']:
        response = await self.async_session.execute(
            select(self.model)
        )
        return [self.pydantic_model.model_validate(obj) for obj in response.scalars()]
