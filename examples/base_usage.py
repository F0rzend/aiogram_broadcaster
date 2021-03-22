from aiogram_broadcaster import TextBroadcaster

import asyncio
import logging


async def main():
    broadcaster = TextBroadcaster('USERS IDS HERE', 'hello!', bot_token='BOT TOKEN HERE')
    try:
        await broadcaster.run()
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
