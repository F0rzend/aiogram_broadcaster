from aiogram_broadcaster import TextBroadcaster

import asyncio
import logging


async def main():
    """
    You can pass arguments to chats.
    Thus, you don’t need to generate a list on your own
    """
    broadcaster = TextBroadcaster(
        'USERS IDS HERE',
        'Hello, we are <b>$service</b>\nYour id: <code>$chat_id</code>',
        args=dict(service='fonco'),  # You can pass arguments, that will be used in all chats
        bot_token='BOT TOKEN HERE'
    )
    try:
        await broadcaster.run()
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
