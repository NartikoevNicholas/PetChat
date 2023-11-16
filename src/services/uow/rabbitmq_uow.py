import typing as tp

from aio_pika import RobustChannel

from src.infrastructure.broker import RabbitmqBroker
from src.services.uow.abstract_uow import AbstractBrokerUOW


class RabbitmqUOW(AbstractBrokerUOW):
    def __init__(self, channel: RobustChannel):
        self.channel = channel
        self.tx = channel.transaction()

    async def __aenter__(self) -> tp.Self:
        await self.tx.select()
        self.broker = RabbitmqBroker(self.channel)
        return self

    async def commit(self) -> None:
        await self.tx.commit()

    async def rollback(self) -> None:
        await self.tx.rollback()

    async def close(self) -> None:
        await self.channel.close()
