from abc import (
    ABC,
    abstractmethod
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker
)

from src.services import abstract_interfase


class AbstractUOW(ABC):
    @abstractmethod
    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass


class SQLAlchemyAdapterUOW(AbstractUOW, ABC):
    def __init__(self, async_session: async_sessionmaker):
        self.session: AsyncSession = async_session()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def close(self) -> None:
        await self.session.aclose()


class AbstractMemoryStorageUOW(AbstractUOW, ABC):
    storage: abstract_interfase.AbstractMemoryStorage


class AbstractBrokerUOW(AbstractUOW, ABC):
    broker: abstract_interfase.AbstractBroker


class AbstractUserServiceRepositoryUOW(SQLAlchemyAdapterUOW, ABC):
    user: abstract_interfase.AbstractUserRepository
    user_history: abstract_interfase.AbstractUserHistoryRepository
