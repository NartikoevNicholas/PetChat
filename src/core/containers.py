from dependency_injector import containers, providers

from src.services.uow import (
    RedisUOW,
    RabbitmqUOW,
    UserServiceRepositoryUOW,
)

from src.services.use_case import (
    UserService,
    RateLimiterService
)

from .redis_core import get_async_redis_client
from .sqlalchemy_core import get_async_session
from .rabbitmq_core import get_rabbitmq_channel


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=['src.endpoints'])
    config = providers.Configuration()

    # connection to interface
    redis_client = providers.Factory(get_async_redis_client)
    rabbitmq_channel = providers.Factory(get_rabbitmq_channel)
    sqlalchemy_async_sessionmaker = providers.Factory(get_async_session)

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
        async_session=sqlalchemy_async_sessionmaker
    )

    # use case
    user_service: UserService = providers.Factory(
        UserService,
        config=config,
        memory_uow=redis_uow,
        repository_uow=user_repository_uow,
        broker_uow=rabbitmq_uow
    )
    rate_limiter_service: RateLimiterService = providers.Factory(
        RateLimiterService,
        config=config,
        memory_uow=redis_uow,
    )
