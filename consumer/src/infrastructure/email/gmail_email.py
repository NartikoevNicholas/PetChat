import aiosmtplib

from email.message import EmailMessage

from src.services.entities import EmailMessageEntity
from src.services.abstract_interface import AbstractEmail


class GmailEmail(AbstractEmail):
    _host: str = 'smtp.gmail.com'
    _port: int = 587

    def __init__(self, username: str, password: str):
        self._username: str = username
        self._password: str = password

    async def send(self, schema: EmailMessageEntity) -> None:
        mes = EmailMessage()
        mes['To'] = ''.join(schema.to)
        mes['From'] = self._username
        mes['Subject'] = schema.subject
        mes.set_content(schema.content, subtype='html')

        await aiosmtplib.send(
            message=mes,
            username=self._username,
            password=self._password,
            hostname=self._host,
            port=self._port,
        )
