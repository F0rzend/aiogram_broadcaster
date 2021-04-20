from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import TextBroadcast

import asyncio
import logging


async def main():
    """
    You can pass arguments to chats.
    Thus, you don’t need to generate a list on your own
    """
    broadcaster = AiogramBroadcaster(bot_token='BOT TOKEN HERE')
    try:
        await broadcaster.run(
            TextBroadcast(
                'USERS IDS HERE',
                'Hello, we are <b>$service</b>\nYour id: <code>$chat_id</code>',
                parse_mode='HTML',
                kwargs=dict(service='fonco'),  # You can pass arguments, that will be used in all chats
            )
        )
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
