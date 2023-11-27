from aio_pika import connect_robust


def get_rabbitmq_url(rabbitmq_settings: dict):
    return 'amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@' \
           '{RABBITMQ_HOST}:{RABBITMQ_PORT}/'.format(**rabbitmq_settings)


async def get_rabbitmq_channel(rabbitmq_settings: dict):
    connect = await connect_robust(get_rabbitmq_url(rabbitmq_settings))
    return await connect.channel(publisher_confirms=False)
