from abc import ABC, abstractmethod

from aiogram_broadcaster.broadcast.base_broadcast import BaseBroadcast


class BaseStorage(ABC):
    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def wait_closed(self):
        pass

    @abstractmethod
    async def add_broadcast(self, broadcast: BaseBroadcast) -> int:
        pass

    @abstractmethod
    async def pop_chat(self, broadcast_id) -> dict:
        pass

    @abstractmethod
    async def append_chat(self, broadcast_id: int, chat: dict):
        pass

    @abstractmethod
    async def add_successful(self, broadcast_id: int, chat: dict, message_id: int):
        pass

    @abstractmethod
    async def add_failure(self, broadcast_id: int, chat: dict):
        pass
