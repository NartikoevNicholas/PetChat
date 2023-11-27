from redis.asyncio import Redis
from fastapi import (
    APIRouter,
    Depends,
    status
)
from fastapi.exceptions import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker
from dependency_injector.wiring import (
    inject,
    Provide
)

from src.core.config import API
from src.core.containers import Container


router = APIRouter(
    tags=['health']
)


@router.get(path=API.health_ping_app_v1)
async def ping_app():
    return {"message": "Application worked!"}


@router.get(path=API.health_ping_db_v1)
@inject
async def ping_db(connection: async_sessionmaker = Depends(Provide[Container.async_session])):
    async with connection() as session:
        response = await session.scalars(text('SELECT 1;'))

    if response:
        return {"message": "Database worked!"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database isn't working",
    )


@router.get(path=API.health_ping_memory_cache_v1)
@inject
async def ping_mem_cache(redis_client: Redis = Depends(Provide[Container.redis_client])):
    if await redis_client.ping():
        return {"message": "Memory cache worked!"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Memory cache isn't working",
    )
