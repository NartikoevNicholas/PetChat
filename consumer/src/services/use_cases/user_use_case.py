import os
import json
import aiofiles

from aiormq.abc import DeliveredMessage

from src.core import get_default_settings
from src.services.abstract_interface import AbstractEmail
from src.services.entities import (
    BrokerUserEmailEntity,
    EmailMessageEntity
)


settings = get_default_settings()


class UserUseCase:
    def __init__(
        self,
        email: AbstractEmail
    ):
        self._email: AbstractEmail = email

    async def send_registration_email(self, message: DeliveredMessage):
        body = json.loads(message.body)
        params = BrokerUserEmailEntity(**body)

        path = os.path.join(settings.DIR, settings.DIR_HTML, 'registration.html')
        async with aiofiles.open(path) as file:
            content = await file.read()

        content = content.format(**params.model_dump())
        email_message = EmailMessageEntity(
            to=[params.email],
            subject='Registration',
            content=content
        )

        await self._email.send(email_message)
