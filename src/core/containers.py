from dependency_injector import containers, providers
from passlib.context import CryptContext

from src.services.uow import (
    RedisUOW,
    RabbitmqUOW,
    AuthServiceRepositoryUOW,
    UserServiceRepositoryUOW
)
from src.services.use_case import (
    AuthService,
    UserService,
    RateLimiterService
)

from .redis_core import get_async_redis_client
from .rabbitmq_core import get_rabbitmq_channel
from .sqlalchemy_core import get_engine, get_async_session


class Container(containers.DeclarativeContainer):
    # settings
    config = providers.Configuration()
    wiring_config = containers.WiringConfiguration(
        packages=['src.endpoints']
    )
    crypt_context = providers.Singleton(
        CryptContext,
        schemes=config.ALGORITHM,
        deprecated='auto'
    )

    # connection to interface
    redis_client = providers.Factory(
        get_async_redis_client,
        redis_settings=config.REDIS
    )
    rabbitmq_channel = providers.Factory(
        get_rabbitmq_channel,
        rabbitmq_settings=config.RABBITMQ
    )
    engine = providers.Singleton(
        get_engine,
        postgres_settings=config.POSTGRES
    )
    async_session = providers.Factory(
        get_async_session,
        engine
    )

    # uow
    redis_uow = providers.Factory(
        RedisUOW,
        redis=redis_client
    )
    rabbitmq_uow = providers.Factory(
        RabbitmqUOW,
        channel=rabbitmq_channel
    )
    user_repository_uow = providers.Factory(
        UserServiceRepositoryUOW,
        async_session=async_session
    )
    auth_repository_uow = providers.Factory(
        AuthServiceRepositoryUOW,
        async_session=async_session
    )

    # use case
    user_service = providers.Factory(
        UserService,
        config=config,
        crypt_context=crypt_context,
        memory_uow=redis_uow,
        repository_uow=user_repository_uow,
        broker_uow=rabbitmq_uow
    )
    rate_limiter_service = providers.Singleton(
        RateLimiterService,
        config=config,
        memory_uow=redis_uow,
    )
    auth_service = providers.Factory(
        AuthService,
        config=config,
        crypt_context=crypt_context,
        memory_uow=redis_uow,
        repository_uow=user_repository_uow,
    )
