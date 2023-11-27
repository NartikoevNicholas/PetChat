import abc

from src.services import entities as et


class AbstractBroker(abc.ABC):
    send_registration_email_name: str = 'user_reg'
    send_update_email_name: str = 'user_email_upd'

    @abc.abstractmethod
    async def init_queues(self, functions: et.BrokerFunctions) -> None:
        pass

    @abc.abstractmethod
    async def start_consume(self) -> None:
        pass
