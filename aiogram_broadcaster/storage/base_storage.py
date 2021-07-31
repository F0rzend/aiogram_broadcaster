from abc import ABC, abstractmethod
from typing import List, Dict

from aiogram_broadcaster.broadcast.base_broadcast import BaseBroadcast


class BaseStorage(ABC):
    def __init__(self):
        self.broadcasts: dict = {}

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def wait_closed(self):
        pass

    @abstractmethod
    async def _add_broadcast(self, broadcast: BaseBroadcast):
        pass

    async def init_broadcast(self, broadcast: BaseBroadcast) -> int:
        broadcast_id = len(self.broadcasts)
        broadcast.id = broadcast_id
        await self._add_broadcast(broadcast)
        return broadcast_id

    @abstractmethod
    async def get_broadcast(self, broadcast_id: int) -> BaseBroadcast:
        pass

    @abstractmethod
    async def get_chats(self, broadcast_id: int) -> List[Dict]:
        pass

    @abstractmethod
    async def pop_chat(self, broadcast_id) -> Dict:
        pass

    @abstractmethod
    async def clear_chats(self, broadcast_id) -> None:
        pass

    @abstractmethod
    async def append_chat(self, broadcast_id: int, chat: Dict):
        pass

    @abstractmethod
    async def add_successful(self, broadcast_id: int, chat: Dict, message_id: int):
        pass

    @abstractmethod
    async def get_successful(self, broadcast_id: int) -> List[Dict]:
        pass

    @abstractmethod
    async def add_failure(self, broadcast_id: int, chat: Dict):
        pass

    @abstractmethod
    async def get_failure(self, broadcast_id: int) -> List[Dict]:
        pass
