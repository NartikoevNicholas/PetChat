from abc import (
    ABC,
    abstractmethod
)
from src.services.entities import BrokerUserEmailEntity


class AbstractBroker(ABC):
    send_registration_queue_name: str = 'send_registration_email'

    @abstractmethod
    async def send_registration_queue(self, schema: BrokerUserEmailEntity) -> None:
        pass
