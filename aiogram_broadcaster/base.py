import abc
import asyncio
import logging
from typing import Dict, Optional, Tuple, List, Union

from aiogram import Bot

from .types import ChatsType, MarkupType, ChatIdType
from .exceptions import RunningError


class BaseBroadcaster(abc.ABC):
    running = []

    def __init__(
            self,
            chats: ChatsType,
            kwargs: Optional[Dict] = None,
            disable_notification: Optional[bool] = None,
            disable_web_page_preview: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            allow_sending_without_reply: Optional[bool] = None,
            reply_markup: MarkupType = None,
            bot: Optional[Bot] = None,
            bot_token: Optional[str] = None,
            timeout: float = 0.05,
            logger=__name__,
    ):
        self._setup_chats(chats, kwargs)
        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_to_message_id = reply_to_message_id
        self.allow_sending_without_reply = allow_sending_without_reply
        self.reply_markup = reply_markup
        self._setup_bot(bot, bot_token)
        self.timeout = timeout

        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)

        self.logger = logger

        self._id: int = len(BaseBroadcaster.running)
        self._is_running: bool = False
        self._successful: List[Dict] = []
        self._failure: List[Dict] = []

    def __str__(self) -> str:
        attributes = [
            ('id', self._id),
            ('is_running', self._is_running),
        ]
        if self._is_running:
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

    def _setup_bot(
            self,
            bot: Optional[Bot] = None,
            token: Optional[str] = None,
    ) -> Bot:
        if not (bot or token):
            bot = Bot.get_current()
            if bot:
                self.bot = bot
            else:
                raise AttributeError('You should either pass a bot instance or a token')
        if bot and token:
            raise AttributeError('You can’t pass both bot and token')
        if bot:
            self.bot = bot
        elif token:
            bot = Bot(token=token)
            self.bot = bot
        return bot

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

    @staticmethod
    def _chek_identical_keys(dicts: List) -> bool:
        for d in dicts[1:]:
            if not sorted(d.keys()) == sorted(dicts[0].keys()):
                return False
        return True

    @staticmethod
    def _parse_args(chat: Dict) -> Tuple[ChatIdType, dict]:
        chat_id = chat.get('chat_id')
        text_args = chat
        return chat_id, text_args

    @abc.abstractmethod
    async def send(self, chat_id: ChatIdType, chat_args: dict) -> bool:
        pass

    def _change_running_status(self, run: bool) -> None:
        self._is_running = run
        if run:
            BaseBroadcaster.running.append(self)
        else:
            BaseBroadcaster.running.remove(self)

    async def _start_broadcast(self) -> None:
        for chat in self.chats:
            logging.info(str(self))
            chat_id, chat_args = self._parse_args(chat)
            if await self.send(chat_id=chat_id, chat_args=chat_args):
                self._successful.append(chat)
            else:
                self._failure.append(chat)
            await asyncio.sleep(self.timeout)

    async def run(self) -> None:
        self._change_running_status(True)
        await self._start_broadcast()
        self._change_running_status(False)
        logging.info(f'{len(self._successful)}/{len(self.chats)} messages were sent out')

    async def close_bot(self) -> None:
        logging.warning('GOODBYE')
        await self.bot.session.close()
