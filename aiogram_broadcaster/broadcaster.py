import asyncio
import logging
from typing import Optional, Dict, Tuple, List, Union

from aiogram import Bot
from aiogram.utils import exceptions

from aiogram_broadcaster.broadcast.base_broadcast import BaseBroadcast
from aiogram_broadcaster.defaults import DEFAULT_DELAY
from aiogram_broadcaster.storage import BaseStorage, MemoryStorage
from aiogram_broadcaster.types import ChatIdType


logger = logging.getLogger('aiogram_broadcaster')

BROADCAST_TASK_NAME = 'broadcast:{id}'


class AiogramBroadcaster:
    def __init__(
        self,
        storage: Optional[BaseStorage] = None,
        bot: Optional[Bot] = None,
        bot_token: Optional[str] = None,
        max_retries: int = 200,
        delay: Optional[float] = None,
    ):
        self._setup_storage(storage)
        self._setup_bot(bot, bot_token)
        self._setup_delay(delay)
        self.max_retries = max_retries

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
                self.bot = Bot(token='', validate_token=False)
        if bot and token:
            raise AttributeError('You can’t pass both bot and token')
        if bot:
            self.bot = bot
        elif token:
            bot = Bot(token=token)
            self.bot = bot
        return bot

    def _setup_delay(self, delay: Optional[float]):
        self.delay = delay if delay else DEFAULT_DELAY

    async def close_bot(self) -> None:
        logging.warning('GOODBYE')
        await self.bot.session.close()

    @staticmethod
    async def _get_delay(*delays: int) -> int:
        return max(delays)

    @staticmethod
    def _parse_args(chat: Dict) -> Tuple[ChatIdType, Optional[str], dict]:
        chat_id = chat.get('chat_id')
        text_args = chat
        try:
            bot_token = chat.pop('bot_token')
        except KeyError:
            bot_token = None
        return chat_id, bot_token, text_args

    async def _run_broadcast(self, broadcast: BaseBroadcast) -> Tuple[List[Dict], List[Dict]]:
        while await self.storage.get_chats(broadcast.id):
            chat = await self.storage.pop_chat(broadcast.id)
            chat_id, bot_token, chat_args = self._parse_args(chat)
            message_id = None
            for _ in range(self.max_retries):
                try:
                    if bot_token:
                        async with self.bot.with_token(bot_token):
                            message_id = await broadcast.send(bot=self.bot, chat_id=chat_id, chat_args=chat_args)
                    else:
                        message_id = await broadcast.send(bot=self.bot, chat_id=chat_id, chat_args=chat_args)
                except exceptions.RetryAfter as e:
                    logger.debug(
                        f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
                    )
                    await asyncio.sleep(e.timeout)
                except (
                        exceptions.BotBlocked,
                        exceptions.ChatNotFound,
                        exceptions.UserDeactivated,
                        exceptions.ChatNotFound
                ) as e:
                    logger.debug(f"Target [ID:{chat_id}]: {e.match}")
                except exceptions.TelegramAPIError:
                    logger.exception(f"Target [ID:{chat_id}]: failed")
                else:
                    logger.debug(f"Target [ID:{chat_id}]: success")
                    break

            if message_id:
                await self.storage.add_successful(broadcast.id, chat, message_id)
            else:
                await self.storage.add_failure(broadcast.id, chat)

            await asyncio.sleep(await self._get_delay(self.delay, broadcast.delay))

        successful = await self.storage.get_successful(broadcast.id)
        failure = await self.storage.get_failure(broadcast.id)
        logging.debug(
            f"{broadcast} finished [{len(successful)}/{len(failure)}]"
        )
        return successful, failure

    async def _get_broadcast(self, broadcast: Union[BaseBroadcast, int]) -> BaseBroadcast:
        if isinstance(broadcast, BaseBroadcast):
            return broadcast
        return await self.storage.get_broadcast(broadcast)

    async def run(self, broadcast: BaseBroadcast, in_task: bool = False) -> int:
        broadcast_id = await self.storage.init_broadcast(broadcast=broadcast)
        if in_task:
            asyncio.create_task(self._run_broadcast(broadcast), name=BROADCAST_TASK_NAME.format(id=broadcast_id))
        else:
            await self._run_broadcast(broadcast)
        return broadcast_id

    async def stop(
            self, broadcast: Union[BaseBroadcast, int], return_chats: bool = True
    ) -> Optional[Tuple[List[Dict], List[Dict]]]:
        broadcast: BaseBroadcast = await self._get_broadcast(broadcast)
        await self.storage.clear_chats(broadcast.id)
        if return_chats:
            successful = await self.storage.get_successful(broadcast.id)
            failure = await self.storage.get_failure(broadcast.id)
            return successful, failure
