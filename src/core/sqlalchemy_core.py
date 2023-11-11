from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine
)

from .config import get_config


settings = get_config()
engine = create_async_engine(settings.POSTGRES.async_url)


def get_async_session():
    return async_sessionmaker(bind=engine, expire_on_commit=False)
