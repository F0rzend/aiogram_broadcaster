from typing import List, Dict

from . import BaseStorage
from ..broadcast.base_broadcast import BaseBroadcast


class MemoryStorage(BaseStorage):
    def __init__(self):
        super().__init__()
        self.data: dict = {}

    async def close(self):
        self.broadcasts.clear()
        self.data.clear()

    async def wait_closed(self):
        pass

    async def _add_broadcast(self, broadcast: BaseBroadcast):
        self.broadcasts[broadcast.id] = broadcast
        self.data[broadcast.id] = {}
        self.data[broadcast.id]['chats'] = broadcast.chats
        return broadcast.id

    async def get_broadcast(self, broadcast_id: int) -> BaseBroadcast:
        return self.broadcasts[broadcast_id]

    async def get_chats(self, broadcast_id: int) -> List[Dict]:
        return self.data[broadcast_id]['chats']

    async def pop_chat(self, broadcast_id) -> Dict:
        return self.data[broadcast_id]['chats'].pop()

    async def append_chat(self, broadcast_id: int, chat: Dict):
        self.data[broadcast_id]['chats'].append(chat)

    async def add_successful(self, broadcast_id: int, chat: Dict, message_id: int):
        try:
            self.data[broadcast_id]['successful']
        except KeyError:
            self.data[broadcast_id]['successful'] = []
        finally:
            self.data[broadcast_id]['successful'].append(dict(chat=chat, message_id=message_id))

    async def get_successful(self, broadcast_id: int) -> List[Dict]:
        return self.data[broadcast_id].get('successful', [])

    async def add_failure(self, broadcast_id: int, chat: Dict):
        try:
            self.data[broadcast_id]['failure']
        except KeyError:
            self.data[broadcast_id]['failure'] = []
        finally:
            self.data[broadcast_id]['failure'].append(dict(chat=chat))

    async def get_failure(self, broadcast_id: int) -> List[Dict]:
        return self.data[broadcast_id].get('failure', [])
