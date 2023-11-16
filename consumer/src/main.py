import asyncio

from src.core.container import Container


async def main():
    container = Container()

    broker = container.consumer()
    await broker.listening()


if __name__ == '__main__':
    asyncio.run(main())
