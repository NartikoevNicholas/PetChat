import os
import typing as tp
from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent


@dataclass
class API:
    user_me_v1 = '/v1/user/me'
    user_update_v1 = '/v1/user/update'
    user_delete_v1 = '/v1/user/delete'
    user_email_verify_v1 = '/v1/user/email_verify'
    user_registration_v1 = '/v1/user/registration'
    user_available_v1 = '/v1/user/available'

    auth_login_v1 = '/v1/auth/login'
    auth_logout_v1 = '/v1/auth/logout'
    auth_refresh_v1 = '/v1/auth/refresh'

    health_ping_db_v1 = '/v1/health_ping/db'
    health_ping_app_v1 = '/v1/health_ping/app'
    health_ping_memory_cache_v1 = '/v1/health_ping/memory_cache'


class Settings(BaseSettings):
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


class RedisSettings(Settings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int


class RabbitmqSettings(Settings):
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_MESSAGE_TTL: int


class DefaultSettings(Settings):
    # project
    BASE_DIR: Path = BASE_DIR
    DEBUG: bool
    SEP: str
    ALGORITHM: str
    TOKEN_ALGORITHM: str
    SECRET_KEY: str
    REG_EXP_TIME: int
    DEL_EXP_TIME: int
    EXPIRE_TIME_EMAIL_VERIFY: int
    LENGTH_CODE: int
    REDIRECT_AFTER_VERIFY_EMAIL: str
    REQUEST_PER_SECOND: tp.Union[int, float]
    ACCESS_EXP_TIME: int
    REFRESH_EXP_TIME: int

    # logging
    LOG_DIR: str
    HTTP_LOG_NAME: str
    BUSINESS_LOGIC_LOG_NAME: str

    # fastapi
    DOCS_URL: str
    OPENAPI_URL: str
    PROJECT_NAME: str

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
