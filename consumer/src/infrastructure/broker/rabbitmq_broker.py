import asyncio
import logging
import typing as tp

from aio_pika import (
    logger,
    connect_robust
)
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractRobustQueue
)

from src.services import entities as et
from src.services.abstract_interface import AbstractBroker


class RabbitmqBroker(AbstractBroker):
    queues: tp.List[tp.Tuple[AbstractRobustQueue, tp.Callable]] = []

    def __init__(self, url):
        self.url = url
        self.channel = None
        logger.setLevel(logging.ERROR)

    async def init_queues(self, functions: et.BrokerFunctions) -> None:
        connection = await connect_robust(self.url)
        channel = await connection.channel()

        # create queues
        send_registration_email_queue = await channel.declare_queue(
            self.send_registration_email_name,
            durable=True
        )

        # create list
        self.queues = [
            (send_registration_email_queue, self._callback(functions.send_registration_email_func))
        ]

    async def start_consume(self):
        for queue, func in self.queues:
            await queue.consume(func)
        await asyncio.Future()

    @staticmethod
    def _callback(func: tp.Callable):
        async def wrapper(message: AbstractIncomingMessage):
            try:
                await func(message)
                await message.channel.basic_ack(delivery_tag=message.delivery_tag)
            except Exception as e:
                raise e
        return wrapper
