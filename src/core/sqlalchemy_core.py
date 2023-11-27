from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine
)


def get_async_postgres_url(postgres_settings: dict) -> str:
    #  pattern: postgres+asyncpg://user:password@host:port/db_name
    return 'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@' \
           '{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'.format(**postgres_settings)


def get_sync_postgres_url(postgres_settings: dict) -> str:
    #  pattern: postgres://user:password@host:port/db_name
    return 'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:' \
           '{POSTGRES_PORT}/{POSTGRES_DB}'.format(**postgres_settings)


def get_engine(postgres_settings: dict):
    return create_async_engine(get_async_postgres_url(postgres_settings))


def get_async_session(engine):
    return async_sessionmaker(bind=engine, expire_on_commit=False)
