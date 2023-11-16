import abc

from src.services import entities as et


class AbstractBroker(abc.ABC):
    send_registration_email_name: str = 'send_registration_email'

    @abc.abstractmethod
    async def init_queues(self, functions: et.BrokerFunctions) -> None:
        pass

    @abc.abstractmethod
    async def start_consume(self) -> None:
        pass
