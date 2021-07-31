import abc
from typing import Dict, Optional, List, Union

from aiogram import Bot

from aiogram_broadcaster.defaults import DEFAULT_DELAY
from aiogram_broadcaster.types import ChatsType, MarkupType, ChatIdType
from aiogram_broadcaster.exceptions import RunningError


class BaseBroadcast(abc.ABC):
    def __init__(
        self,
        chats: ChatsType,
        kwargs: Optional[Dict] = None,
        disable_notification: Optional[bool] = None,
        disable_web_page_preview: Optional[bool] = None,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: MarkupType = None,
        delay: float = DEFAULT_DELAY,
    ):
        self._setup_chats(chats, kwargs)
        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_to_message_id = reply_to_message_id
        self.allow_sending_without_reply = allow_sending_without_reply
        self.reply_markup = reply_markup
        self._setup_delay(delay)

        self._is_running: bool = False
        self._successful: List[Dict] = []
        self._failure: List[Dict] = []
        self._id = None

    @property
    def id(self) -> int:
        if self._id is not None:
            return self._id
        raise ValueError("Broadcast hasn't id yet")

    @id.setter
    def id(self, value: int):
        if self._id is None:
            self._id = value
        else:
            raise ValueError("Broadcast already has id")

    def __str__(self) -> str:
        broadcast_id = getattr(self, 'id', None)
        if broadcast_id is not None:
            attributes = [
                ('id', broadcast_id)
            ]
        else:
            attributes = []
        if self._is_running:
            attributes.append(('is_running', self._is_running))
            attributes.append(('progress', f'{len(self.successful)}/{len(self.chats)}'))
        attributes = '; '.join((f'{key}={str(value)}' for key, value in attributes))
        return f'<{self.__class__.__name__}({attributes})>'

    @property
    def successful(self) -> List[Dict]:
        if not self._is_running:
            raise RunningError(self._is_running)
        else:
            return self._successful

    def get_successful(self, id_only: bool = False) -> Union[List[Dict], List[ChatIdType]]:
        if id_only:
            return [chat['chat_id'] for chat in self.successful]
        else:
            return self.successful

    @property
    def failure(self) -> List[Dict]:
        return self._failure

    def get_failure(self, id_only: bool = False) -> Union[List[Dict], List[ChatIdType]]:
        if id_only:
            return [chat['chat_id'] for chat in self.failure]
        else:
            return self.failure

    def _setup_chats(self, chats: ChatsType, kwargs: Optional[Dict] = None) -> None:
        if not kwargs:
            kwargs = {}
        if isinstance(chats, int) or isinstance(chats, str):
            self.chats = [{'chat_id': chats, **kwargs}]
        elif isinstance(chats, list):
            if all([
                isinstance(chat, int) or isinstance(chat, str)
                for chat in chats
            ]):
                self.chats = [
                    {'chat_id': chat, **kwargs} for chat in chats
                ]
            elif all([
                isinstance(chat, dict)
                for chat in chats
            ]):
                if not all([chat.get('chat_id') for chat in chats]):
                    raise ValueError('Not all dictionaries have the "chat_id" key')
                if not self._chek_identical_keys(dicts=chats):
                    raise ValueError('Not all dictionaries have identical keys')
                self.chats = [
                    {'chat_id': chat.pop('chat_id'), **chat, **kwargs}
                    for chat in chats if chat.get('chat_id', None)
                ]
        else:
            raise AttributeError(f'argument chats: expected {ChatsType}, got "{type(chats)}"')

    def _setup_delay(self, delay: Optional[float]):
        self.delay = delay if delay else DEFAULT_DELAY

    @staticmethod
    def _chek_identical_keys(dicts: List) -> bool:
        for d in dicts[1:]:
            if not sorted(d.keys()) == sorted(dicts[0].keys()):
                return False
        return True

    @abc.abstractmethod
    async def send(self, bot: Bot, chat_id: ChatIdType, chat_args: dict) -> Optional[int]:
        pass
