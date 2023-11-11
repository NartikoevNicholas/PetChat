from abc import (
    ABC,
    abstractmethod
)

from src.services.entities import EmailMessageEntity


class AbstractEmail(ABC):
    _host: str
    _port: int

    @abstractmethod
    async def send(self, email_message: EmailMessageEntity) -> None:
        raise NotImplementedError
