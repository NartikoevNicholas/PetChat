import asyncio

import logging

from typing import (
    List,
    Tuple,
    Callable
)

from aio_pika import (
    logger,
    connect_robust
)
from aio_pika.abc import AbstractQueue

from src.services.use_cases.user_use_case import UserUseCase


class BrokerUseCase:
    def __init__(
        self,
        credentials: str,
        user: UserUseCase
    ):
        self._credentials = credentials
        self._user = user
        logger.setLevel(logging.ERROR)

    async def listening(self):
        connection = await connect_robust(self._credentials)
        async with connection, connection.channel() as channel:
            queues = await self.init_queues(channel)

            for queue, callback in queues:
                await queue.consume(callback)

            await asyncio.Future()

    async def init_queues(self, channel) -> List[Tuple[AbstractQueue, Callable]]:
        user_registration = await channel.declare_queue(
            'send_registration_email',
            durable=True,
        )
        return [
            (
                user_registration,
                self.callback(self._user.send_registration_email)
            )
        ]

    @staticmethod
    def callback(func):
        async def wrapper(message):
            try:
                await func(message)
                await message.channel.basic_ack(delivery_tag=message.delivery_tag)
            except Exception as e:
                raise e

        return wrapper
