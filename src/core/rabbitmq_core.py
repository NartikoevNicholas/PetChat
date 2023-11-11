from aio_pika import connect_robust

from .config import get_config


settings = get_config()


async def get_rabbitmq_channel():
    connect = await connect_robust(settings.RABBITMQ.get_url)
    return await connect.channel(publisher_confirms=False)
