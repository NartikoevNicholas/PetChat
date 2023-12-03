import abc
import typing as tp


SetType = tp.Union[int, float, str, bytes, bytearray]


class AbstractReadlockMemoryStorage(abc.ABC):
    @abc.abstractmethod
    async def __aenter__(self):
        pass

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class AbstractMemoryStorage(abc.ABC):

    @abc.abstractmethod
    async def get_time(self) -> float:
        pass

    @abc.abstractmethod
    async def set(self, name: str, value: SetType, ex: int = None) -> None:
        pass

    @abc.abstractmethod
    async def get(self, key: str) -> bytes:
        pass

    @abc.abstractmethod
    async def delete_one(self, key: str) -> None:
        pass

    @abc.abstractmethod
    def readlock(self, name: str, timeout: int = 5) -> AbstractReadlockMemoryStorage:
        pass

