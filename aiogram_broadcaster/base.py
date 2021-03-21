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
            disable_notification: Optional[bool] = None,
            disable_web_page_preview: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            allow_sending_without_reply: Optional[bool] = None,
            reply_markup: MarkupType = None,
            bot: Optional[Bot] = None,
            timeout: float = 0.02,
            logger=__name__,
    ):
        self._setup_chats(chats)
        self.disable_notification = disable_notification
        self.disable_web_page_preview = disable_web_page_preview
        self.reply_to_message_id = reply_to_message_id
        self.allow_sending_without_reply = allow_sending_without_reply
        self.reply_markup = reply_markup
        bot = bot if bot else Bot.get_current()
        if bot:
            self.bot = bot
        else:
            raise ValueError('You need to pass bot')
        self.timeout = timeout

        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)

        self.logger = logger

    def _setup_chats(self, chats: ChatsType):
        if isinstance(chats, int) or isinstance(chats, str):
            self.chats = [{'chat_id': chats}]
        elif isinstance(chats, list):
            if all([
                isinstance(chat, int) or isinstance(chat, str)
                for chat in chats
            ]):
                self.chats = [
                    {'chat_id': chat} for chat in chats
                ]
            elif all([
                isinstance(chat, dict)
                for chat in chats
            ]):
                if not all([chat.get('chat_id') for chat in chats]):
                    raise ValueError('Not all dictionaries "chat_id" key')
                if not self._chek_identical_keys(dicts=chats):
                    raise ValueError('Not all dictionaries have identical keys')
                self.chats = [
                    {'chat_id': args.pop('chat_id'), **args} for args in chats if args.get('chat_id', None)
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
        logging.info(f'{count}/{len(self.chats)} messages sent out')
