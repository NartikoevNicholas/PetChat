import os
import typing as tp
from pathlib import Path
from functools import lru_cache

from starlette.datastructures import URL
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

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


class APISettings(Settings):
    API_VERSION: str

    ROUTER_HEALTH: str
    ROUTER_USER: str
    ROUTER_AUTH: str

    HEALTH_PING: str

    USER_REGISTRATION: str
    USER_REGISTRATION_VERIFY: str
    USER_AVAILABLE_USERNAME: str
    USER_AVAILABLE_EMAIL: str

    AUTH_LOGIN: str
    AUTH_REFRESH: str
    AUTH_LOGOUT: str

    def email_verify_api(self, base_url: URL, user_id: str, code: str):
        api = self.USER_REGISTRATION_VERIFY
        router = self.ROUTER_USER
        api_version = self.API_VERSION
        return f'{base_url}{api_version}/{router}/{api}/{user_id}/{code}'


class DefaultSettings(Settings):
    # project
    DEBUG: bool
    ALGORITHM: str
    TOKEN_ALGORITHM: str
    SECRET_KEY: str
    EXPIRE_TIME: int
    LENGTH_USER_CODE: int
    REDIRECT_AFTER_VERIFY_EMAIL: str
    REQUEST_PER_SECOND: tp.Union[int, float]
    EXPIRE_ACCESS_TOKEN: int
    EXPIRE_REFRESH_TOKEN: int

    # fastapi
    PROJECT_NAME: str
    DOCS_URL: str
    OPENAPI_URL: str

    # uvicorn
    UVICORN_HOST: str
    UVICORN_PORT: int

    # infrastructure
    REDIS: RedisSettings = RedisSettings()
    POSTGRES: PostgresSettings = PostgresSettings()
    RABBITMQ: RabbitmqSettings = RabbitmqSettings()

    # api
    API: APISettings = APISettings()

    def pwd_context(self) -> CryptContext:
        return CryptContext(schemes=[self.ALGORITHM], deprecated="auto")

    def oauth2_schema(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=f'{self.UVICORN_HOST}:'
                     f'{self.UVICORN_PORT}/'
                     f'{self.API.ROUTER_AUTH}/'
                     f'{self.API.AUTH_LOGOUT}'
        )


@lru_cache
def get_config():
    return DefaultSettings()
