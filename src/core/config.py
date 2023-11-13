import os

from pathlib import Path

from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=os.path.join(BASE_DIR, '.env'),
        env_file_encoding="utf-8"
    )


class PostgresSettings(Settings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    @property
    def settings_dict(self) -> dict:
        return {
            'user': self.POSTGRES_USER,
            'pwd': self.POSTGRES_PASSWORD,
            'db': self.POSTGRES_DB,
            'host': self.POSTGRES_HOST,
            'port': self.POSTGRES_PORT
        }

    @property
    def async_url(self) -> str:
        return 'postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}'.format(
            **self.settings_dict
        )

    @property
    def sync_url(self) -> str:
        return 'postgresql://{user}:{pwd}@{host}:{port}/{db}'.format(
            **self.settings_dict
        )


class RedisSettings(Settings):
    REDIS_HOST: str
    REDIS_PORT: int

    @property
    def get_url(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'


class RabbitmqSettings(Settings):
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_MESSAGE_TTL: int

    @property
    def settings_dict(self) -> dict:
        return {
            'user': self.RABBITMQ_DEFAULT_USER,
            'pwd': self.RABBITMQ_DEFAULT_PASS,
            'host': self.RABBITMQ_HOST,
            'port': self.RABBITMQ_PORT
        }

    @property
    def get_url(self) -> str:
        return 'amqp://{user}:{pwd}@{host}:{port}/'.format(
            **self.settings_dict
        )


class DefaultSettings(Settings):
    # project
    DEBUG: bool
    ALGORITHM: str
    SECRET_KEY: str
    EXPIRE_TIME: int
    LENGTH_USER_CODE: int
    REDIRECT_AFTER_VERIFY_EMAIL: str
    REQUEST_PER_SECOND: int

    # fastapi
    PROJECT_NAME: str
    DOCS_URL: str
    OPENAPI_URL: str
    API_VERSION: str

    # uvicorn
    UVICORN_HOST: str
    UVICORN_PORT: int

    # infrastructure
    REDIS: RedisSettings = RedisSettings()
    POSTGRES: PostgresSettings = PostgresSettings()
    RABBITMQ: RabbitmqSettings = RabbitmqSettings()


@lru_cache
def get_config():
    return DefaultSettings()
