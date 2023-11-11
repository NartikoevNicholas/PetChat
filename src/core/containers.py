from dependency_injector import containers, providers

from src.services.uow import (
    RedisUOW,
    RabbitmqUOW,
    UserUseCaseRepositoryUOW,
)

from src.services.use_case import UserUseCase

from .redis_core import get_async_redis_client
from .sqlalchemy_core import get_async_session
from .rabbitmq_core import get_rabbitmq_channel


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            'src.endpoints.api',
            'src.services.use_case'
        ]
    )
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
        UserUseCaseRepositoryUOW,
        async_session=sqlalchemy_async_sessionmaker
    )

    # use case
    user_use_case: UserUseCase = providers.Factory(
        UserUseCase,
        config=config,
        memory_storage_uow=redis_uow,
        user_repository_uow=user_repository_uow,
        broker_uow=rabbitmq_uow
    )
