import os
import asyncio
from uuid import uuid4

import pytest
from mock import AsyncMock
from httpx import AsyncClient
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy_utils import (
    database_exists,
    drop_database,
    create_database
)

from src import get_application
from src.core.config import (
    get_config,
    DefaultSettings
)
from src.core.redis_core import get_async_redis_client
from src.core.sqlalchemy_core import get_sync_postgres_url, get_async_postgres_url
from src.services.uow import RabbitmqUOW

from tests.utils import run_upgrade


config = get_config()


@pytest.fixture(scope="session")
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def postgres():
    db_name = ".".join([uuid4().hex, "pytest"])
    config.POSTGRES.POSTGRES_DB = db_name

    postgres_settings = config.POSTGRES.model_dump()
    db_url = get_sync_postgres_url(postgres_settings)
    if not database_exists(db_url):
        create_database(db_url)
    yield get_async_postgres_url(postgres_settings)
    drop_database(db_url)


@pytest.fixture
async def redis():
    config.REDIS.REDIS_DB = 1
    async with get_async_redis_client(config.REDIS.model_dump()) as redis:
        yield redis


@pytest.fixture
async def migration(postgres):
    path_to_folder = config.BASE_DIR

    alembic_config = Config(file_=os.path.join(path_to_folder, "alembic.ini"))
    alembic_location = os.path.join(path_to_folder, alembic_config.get_main_option("script_location"))

    alembic_config.set_main_option("script_location", alembic_location)
    alembic_config.set_main_option("sqlalchemy.url", postgres)

    async_engine = create_async_engine(postgres)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, alembic_config)


@pytest.fixture
async def session(postgres) -> AsyncSession:
    engine = create_async_engine(postgres, future=True)
    session = async_sessionmaker(engine, expire_on_commit=False)
    yield session()
    await session().aclose()
    await engine.dispose()


@pytest.fixture
def settings() -> DefaultSettings:
    return config


@pytest.fixture
async def client(migration, redis) -> AsyncClient:
    config.DEBUG = True
    config.REG_EXP_TIME = 1
    config.ACCESS_EXP_TIME = 2
    config.REFRESH_EXP_TIME = 5
    async with AsyncClient(app=get_application(config), base_url="http://test") as app:
        RabbitmqUOW.commit = AsyncMock(return_value=None)
        yield app
