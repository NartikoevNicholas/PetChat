import json

from aio_pika import (
    Message,
    RobustChannel,

)
from aio_pika.abc import AbstractRobustQueue

from src.services.entities import (
    BrokerUserReg,
    BrokerUserEmailUpdate
)
from src.services.abstract_interface import AbstractBroker


class RabbitmqBroker(AbstractBroker):
    def __init__(self, channel: RobustChannel):
        self.channel = channel

    async def email_reg(self, schema: BrokerUserReg) -> None:
        message = json.dumps(schema.model_dump())
        queue = await self.channel.declare_queue(
            name=self.user_reg_queue_name,
            durable=True
        )
        await self._send(message, queue)

    async def email_upd(self, schema: BrokerUserEmailUpdate) -> None:
        message = json.dumps(schema.model_dump())
        queue = await self.channel.declare_queue(
            name=self.user_email_upd_queue_name,
            durable=True
        )
        await self._send(message, queue)

    async def _send(self, message: str, queue: AbstractRobustQueue) -> None:
        await self.channel.default_exchange.publish(
            message=Message(message.encode()),
            routing_key=queue.name
        )
