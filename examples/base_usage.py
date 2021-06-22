from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import TextBroadcast
from aiogram_broadcaster.storage import MemoryStorage

import asyncio
import logging


async def main():
    storage = MemoryStorage()
    broadcaster = AiogramBroadcaster(bot_token='1474246112:AAGAZVxUuwZTaG7m7f1P3d1UR8M14KlY4y0', storage=storage)
    try:
        await broadcaster.run(TextBroadcast(chats='525340304', text='test'))
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
