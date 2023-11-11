import json

from aio_pika import (
    Message,
    RobustChannel
)

from src.services.entities import BrokerUserEmailEntity
from src.services.abstract_interfase import AbstractBroker


class RabbitmqBroker(AbstractBroker):
    def __init__(self, channel: RobustChannel):
        self.channel = channel

    async def send_registration_queue(self, schema: BrokerUserEmailEntity) -> None:
        message = json.dumps(schema.model_dump())
        queue = await self.channel.declare_queue(
            name=self.send_registration_queue_name,
            durable=True
        )
        await self.channel.default_exchange.publish(
            message=Message(message.encode()),
            routing_key=queue.name
        )
