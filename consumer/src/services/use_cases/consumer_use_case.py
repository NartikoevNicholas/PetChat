import os
import json

import aiofiles

from aio_pika.abc import AbstractMessage

from src.core.settings import DefaultSettings
from src.services import entities as et
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
        functions = et.BrokerFunctions(
            send_registration_email_func=self._send_registration_email
        )
        await self.broker.init_queues(functions)
        await self.broker.start_consume()

    async def _send_registration_email(self, message: AbstractMessage) -> None:
        body = json.loads(message.body)
        params = et.BrokerUserEmail(**body)

        path = os.path.join(self.config.DIR, self.config.DIR_HTML, 'registration.html')
        async with aiofiles.open(path) as file:
            content = await file.read()

        content = content.format(**params.model_dump())
        email_message = et.EmailMessage(
            to=[params.email],
            subject='Registration',
            content=content
        )
        await self.email.send(email_message)
