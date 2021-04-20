from . import BaseStorage
from ..broadcast.base_broadcast import BaseBroadcast


class MemoryStorage(BaseStorage):
    def __init__(self):
        self.broadcasts: dict = {}
        self.data: dict = {}

    async def close(self):
        self.broadcasts.clear()
        self.data.clear()

    async def wait_closed(self):
        pass

    async def add_broadcast(self, broadcast: BaseBroadcast) -> int:
        broadcast_id: int = len(self.broadcasts)
        broadcast.id = broadcast_id
        self.broadcasts[broadcast_id] = broadcast
        self.data[broadcast_id] = {}
        self.data[broadcast_id]['chats'] = broadcast.chats
        return broadcast_id

    async def get_chats(self, broadcast_id: int) -> list:
        return self.data[broadcast_id]['chats']

    async def pop_chat(self, broadcast_id) -> dict:
        return self.data[broadcast_id]['chats'].pop()

    async def append_chat(self, broadcast_id: int, chat: dict):
        self.data[broadcast_id]['chats'].append(chat)

    async def add_successful(self, broadcast_id: int, chat: dict, message_id: int):
        self.data[broadcast_id].get('successful', []).append(dict(chat=chat, message_id=message_id))

    async def add_failure(self, broadcast_id: int, chat: dict):
        self.data[broadcast_id].get('successful', []).append(dict(chat=chat))
