import os

from pathlib import Path
from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict
)


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=os.path.join(BASE_DIR, '.env'),
        env_file_encoding='utf-8'
    )


class RabbitmqSettings(Settings):
    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    @property
    def rabbitmq_settings(self) -> dict:
        return {
            'user': self.RABBITMQ_DEFAULT_USER,
            'password': self.RABBITMQ_DEFAULT_PASS,
            'host': self.RABBITMQ_HOST,
            'port': self.RABBITMQ_PORT
        }

    @property
    def rabbitmq_url(self) -> str:
        return 'amqp://{user}:{password}@{host}:{port}/%2F'.format(**self.rabbitmq_settings)


class DefaultSettings(Settings):
    # project
    DIR: str = str(BASE_DIR)
    DIR_HTML: str = 'html'
    DEBUG: bool

    RABBITMQ: RabbitmqSettings = RabbitmqSettings()

    # email
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str


@lru_cache()
def get_default_settings() -> DefaultSettings:
    return DefaultSettings()
