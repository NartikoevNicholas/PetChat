from dependency_injector import (
    containers,
    providers
)

from src.core.settings import get_default_settings
from src.infrastructure.broker import RabbitmqBroker
from src.infrastructure.email import GmailEmail
from src.services.abstract_interface import (
    AbstractEmail,
    AbstractBroker
)
from src.services.use_cases.consumer_use_case import ConsumerService


class Container(containers.DeclarativeContainer):
    config = get_default_settings()
    wiring_config = containers.WiringConfiguration(
        packages=["src.services.use_cases"]
    )

    # infrastructure
    email: AbstractEmail = providers.Factory(
        GmailEmail,
        username=config.EMAIL_USERNAME,
        password=config.EMAIL_PASSWORD
    )
    broker: AbstractBroker = providers.Factory(
        RabbitmqBroker,
        url=config.RABBITMQ.rabbitmq_url

    )

    # use_case
    consumer: ConsumerService = providers.Factory(
        ConsumerService,
        config=config,
        email=email,
        broker=broker,
    )
