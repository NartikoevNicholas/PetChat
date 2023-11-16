import abc

from src.services.entities import BrokerUserEmail


class AbstractBroker(abc.ABC):
    send_registration_queue_name: str = 'send_registration_email'

    @abc.abstractmethod
    async def send_registration_queue(self, schema: BrokerUserEmail) -> None:
        pass
