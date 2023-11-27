import abc

from src.services import entities as et


class AbstractBroker(abc.ABC):
    user_reg_queue_name: str = 'user_reg'
    user_email_upd_queue_name: str = 'user_email_upd'

    @abc.abstractmethod
    async def email_reg(self, schema: et.BrokerUserReg) -> None:
        pass

    @abc.abstractmethod
    async def email_upd(self, schema: et.BrokerUserEmailUpdate) -> None:
        pass
