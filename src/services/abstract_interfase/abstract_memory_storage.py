import abc
import typing as tp


SetType = tp.Union[int, float, str, bytes, bytearray]


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
    async def lock(self, name: str, timeout: int = 5) -> tp.Any:
        pass

    @abc.abstractmethod
    async def unlock(self, lock: tp.Any) -> None:
        pass
