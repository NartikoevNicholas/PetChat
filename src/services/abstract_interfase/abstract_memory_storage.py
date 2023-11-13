from abc import (
    ABC,
    abstractmethod
)

from typing import Union


SetType = Union[str, bytes, bytearray]


class AbstractMemoryStorage(ABC):

    @abstractmethod
    async def get_time(self) -> float:
        pass

    @abstractmethod
    async def set(self, name: str, value: SetType, ex: int = None) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> bytes:
        pass

    @abstractmethod
    async def delete_one(self, key: str) -> None:
        pass
