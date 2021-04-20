import asyncio
import logging
from typing import Optional, Dict, Tuple

from aiogram import Bot
from aiogram.utils import exceptions

from aiogram_broadcaster.broadcast.base_broadcast import BaseBroadcast
from aiogram_broadcaster.storage import BaseStorage, MemoryStorage
from aiogram_broadcaster.types import ChatIdType


class AiogramBroadcaster:
    def __init__(
        self,
        storage: Optional[BaseStorage] = None,
        bot: Optional[Bot] = None,
        bot_token: Optional[str] = None,
        logger=__name__,
    ):
        self._setup_storage(storage)
        self._setup_bot(bot, bot_token)
        self._setup_logger(logger)

    def _setup_storage(self, storage: Optional[BaseStorage]):
        self.storage = storage if storage else MemoryStorage()

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

    def _setup_logger(self, logger):
        if isinstance(logger, str):
            logger = logging.getLogger(logger)

        self.logger = logger

    async def close_bot(self) -> None:
        logging.warning('GOODBYE')
        await self.bot.session.close()

    @staticmethod
    def _parse_args(chat: Dict) -> Tuple[ChatIdType, dict]:
        chat_id = chat.get('chat_id')
        text_args = chat
        return chat_id, text_args

    async def run(self, broadcast: BaseBroadcast) -> Tuple[list, list]:
        broadcast_id = await self.storage.add_broadcast(broadcast=broadcast)
        while await self.storage.get_chats(broadcast_id):
            chat = await self.storage.pop_chat(broadcast_id)
            chat_id, chat_args = self._parse_args(chat)
            message_id = None
            try:
                message_id = await broadcast.send(bot=self.bot, chat_id=chat_id, chat_args=chat_args)
            except exceptions.RetryAfter as e:
                self.logger.debug(
                    f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
                )
                await asyncio.sleep(e.timeout)
                await self.storage.append_chat(broadcast_id, chat)
            except (
                    exceptions.BotBlocked,
                    exceptions.ChatNotFound,
                    exceptions.UserDeactivated,
                    exceptions.ChatNotFound
            ) as e:
                self.logger.debug(f"Target [ID:{chat_id}]: {e.match}")
            except exceptions.TelegramAPIError:
                self.logger.exception(f"Target [ID:{chat_id}]: failed")
            else:
                self.logger.debug(f"Target [ID:{chat_id}]: success")

            if not message_id:
                await self.storage.add_failure(broadcast_id, chat)
            else:
                await self.storage.add_successful(broadcast_id, chat, message_id)

            await asyncio.sleep(broadcast.timeout)
        successful = await self.storage.get_successful(broadcast_id)
        failure = await self.storage.get_failure(broadcast_id)
        logging.debug(
            f"{broadcast} finished [{len(successful)}/{len(failure)}]"
        )
        return successful, failure
