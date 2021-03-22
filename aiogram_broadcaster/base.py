import abc
import asyncio
import logging
from typing import Dict, NoReturn, Optional

from aiogram import Bot

from .types import ChatsType, MarkupType


class BaseBroadcaster(abc.ABC):
    def __init__(
            self,
            chats: ChatsType,
            args: Optional[Dict] = None,
            disable_notification: Optional[bool] = None,
            disable_web_page_preview: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            allow_sending_without_reply: Optional[bool] = None,
            reply_markup: MarkupType = None,
            bot: Optional[Bot] = None,
            bot_token: Optional[str] = None,
            timeout: float = 0.02,
            logger=__name__,
    ):
        self._setup_chats(chats, args)
        print(self.chats)
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
                raise ValueError('You should either pass a bot instance or a token')
        if bot and token:
            raise ValueError('You can’t pass both bot and token')
        if bot:
            self.bot = bot
        elif token:
            bot = Bot(token=token)
            self.bot = bot
        return bot

    def _setup_chats(self, chats: ChatsType, args: Optional[Dict] = None):
        if isinstance(chats, int) or isinstance(chats, str):
            self.chats = [{'chat_id': chats, **args}]
        elif isinstance(chats, list):
            if all([
                isinstance(chat, int) or isinstance(chat, str)
                for chat in chats
            ]):
                self.chats = [
                    {'chat_id': chat, **args} for chat in chats
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
                    {'chat_id': chat.pop('chat_id'), **chat, **args}
                    for chat in chats if chat.get('chat_id', None)
                ]
        else:
            raise TypeError(f'argument chats: expected {ChatsType}, got "{type(chats)}"')

    @staticmethod
    def _chek_identical_keys(dicts: list) -> bool:
        for d in dicts[1:]:
            if not sorted(d.keys()) == sorted(dicts[0].keys()):
                return False
        return True

    @abc.abstractmethod
    async def send(
            self,
            chat: Dict,
    ) -> bool:
        pass

    async def run(self) -> NoReturn:
        count = 0
        for chat in self.chats:
            if await self.send(
                    chat=chat
            ):
                count += 1
            await asyncio.sleep(self.timeout)
        logging.info(f'{count}/{len(self.chats)} messages were sent out')

    async def close_bot(self):
        logging.warning('GOODBYE')
        await self.bot.session.close()
