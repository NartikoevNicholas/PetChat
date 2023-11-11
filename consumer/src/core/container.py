from dependency_injector import (
    containers,
    providers
)

from src.core import get_default_settings
from src.infrastructure.email import GmailEmail
from src.services.abstract_interface import AbstractEmail
from src.services.use_cases.user_use_case import UserUseCase
from src.services.use_cases.broker_use_case import BrokerUseCase


settings = get_default_settings()


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=["src.services.use_cases"]
    )

    # infrastructure
    email: AbstractEmail = providers.Factory(
        GmailEmail,
        username=settings.EMAIL_USERNAME,
        password=settings.EMAIL_PASSWORD
    )

    # use_case
    user: UserUseCase = providers.Factory(
        UserUseCase,
        email=email
    )

    # consumer
    broker: BrokerUseCase = providers.Factory(
        BrokerUseCase,
        credentials=settings.RABBITMQ.rabbitmq_url,
        user=user
    )
