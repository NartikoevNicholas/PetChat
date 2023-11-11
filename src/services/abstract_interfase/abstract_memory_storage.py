from abc import (
    ABC,
    abstractmethod
)

from typing import (
    Any,
    Union
)


class AbstractMemoryStorage(ABC):
    @abstractmethod
    async def set(self, name: str, value: Union[str, bytes, bytearray], ex: int = None) -> None:
        pass

    @abstractmethod
    async def get(self, key: str) -> bytes:
        pass

    @abstractmethod
    async def delete_one(self, key: str) -> None:
        pass
