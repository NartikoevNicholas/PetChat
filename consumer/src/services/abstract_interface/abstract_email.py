import abc

from src.services.entities import EmailMessage


class AbstractEmail(abc.ABC):
    _host: str
    _port: int

    @abc.abstractmethod
    async def send(self, email_message: EmailMessage) -> None:
        raise NotImplementedError
