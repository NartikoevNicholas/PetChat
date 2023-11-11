import asyncio

from src.core.containers import Container


async def main():
    container = Container()

    broker = container.broker()
    await broker.listening()


if __name__ == '__main__':
    asyncio.run(main())
