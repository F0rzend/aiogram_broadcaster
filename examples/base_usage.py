from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import TextBroadcast

import asyncio
import logging


async def main():
    broadcaster = AiogramBroadcaster(bot_token='BOT TOKEN HERE')
    try:
        broadcast_id = await broadcaster.run(TextBroadcast(chats='USERS IDS HERE', text='test'))
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
