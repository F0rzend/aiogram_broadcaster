from aiogram import Bot

from aiogram_broadcaster import TextBroadcaster

import asyncio
import logging


async def main():
    # Bot, storage and dispatcher instances
    bot = Bot(token='BOT TOKEN HERE')
    try:
        await TextBroadcaster('USERS_ID HERE', 'hello!', bot=bot).run()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
