from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import TextBroadcast
from aiogram_broadcaster.storage import MemoryStorage

import asyncio
import logging


async def main():
    storage = MemoryStorage()
    broadcaster = AiogramBroadcaster(bot_token='BOT_TOKEN_HERE', storage=storage)
    try:
        await broadcaster.run(TextBroadcast(chats='CHATS_IDS_HERE', text='test'))
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
