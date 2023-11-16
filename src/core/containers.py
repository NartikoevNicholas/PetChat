from dependency_injector import containers, providers

from src.services import uow
from src.services import use_case as uc

from .config import get_config
from .redis_core import get_async_redis_client
from .sqlalchemy_core import get_async_session
from .rabbitmq_core import get_rabbitmq_channel


class Container(containers.DeclarativeContainer):
    config = get_config()
    wiring_config = containers.WiringConfiguration(packages=['src.endpoints'])

    # connection to interface
    redis_client = providers.Factory(get_async_redis_client)
    rabbitmq_channel = providers.Factory(get_rabbitmq_channel)
    sqlalchemy_async_sessionmaker = providers.Factory(get_async_session)

    # uow
    redis_uow = providers.Factory(
        uow.RedisUOW,
        redis=redis_client
    )
    rabbitmq_uow = providers.Factory(
        uow.RabbitmqUOW,
        channel=rabbitmq_channel
    )
    user_repository_uow = providers.Factory(
        uow.UserServiceRepositoryUOW,
        async_session=sqlalchemy_async_sessionmaker
    )
    auth_repository_uow = providers.Factory(
        uow.AuthServiceRepositoryUOW,
        async_session=sqlalchemy_async_sessionmaker
    )

    # use case
    user_service = providers.Factory(
        uc.UserService,
        config=config,
        memory_uow=redis_uow,
        repository_uow=user_repository_uow,
        broker_uow=rabbitmq_uow
    )
    rate_limiter_service = providers.Factory(
        uc.RateLimiterService,
        config=config,
        memory_uow=redis_uow,
    )
    auth_service = providers.Factory(
        uc.AuthService,
        config=config,
        memory_uow=redis_uow,
        repository_uow=user_repository_uow,
    )
