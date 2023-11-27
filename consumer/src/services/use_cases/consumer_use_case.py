import os

import aiofiles

from aio_pika.abc import AbstractMessage

from src.core.settings import DefaultSettings
from src.services.entities import (
    EmailMessage,
    BrokerUserEmailUpdate,
    BrokerFunctions,
    BrokerUserEmail
)
from src.services.abstract_interface import (
    AbstractEmail,
    AbstractBroker
)


class ConsumerService:
    def __init__(self, config: DefaultSettings, broker: AbstractBroker, email: AbstractEmail):
        self.config = config
        self.email = email
        self.broker = broker

    def __call__(self, *args, **kwargs):
        pass

    async def listening(self) -> None:
        functions = BrokerFunctions(
            send_registration_email_func=self._send_registration_email,
            send_update_email_func=self._send_update_email
        )
        await self.broker.init_queues(functions)
        await self.broker.start_consume()

    async def _send_registration_email(self, message: AbstractMessage) -> None:
        params = BrokerUserEmail.model_validate_json(message.body)
        path = os.path.join(self.config.DIR, self.config.DIR_HTML, self.config.REG_USER_HTML)
        async with aiofiles.open(path) as file:
            content = await file.read()

        content = content.format(**params.model_dump())
        email_message = EmailMessage(
            to=[params.email],
            subject='Registration',
            content=content
        )
        await self.email.send(email_message)

    async def _send_update_email(self, message: AbstractMessage) -> None:
        params = BrokerUserEmailUpdate.model_validate_json(message.body)
        path = os.path.join(self.config.DIR, self.config.DIR_HTML, self.config.UPD_USER_EMAIL_HTML)
        async with aiofiles.open(path) as file:
            content = await file.read()

        content = content.format(**params.model_dump())

        email_message = EmailMessage(
            to=[params.email],
            subject='Update email',
            content=content
        )
        await self.email.send(email_message)
