from aiogram import Bot, Dispatcher, types

from aiogram_broadcaster import MessageBroadcaster

import asyncio
import logging


async def message_handler(msg: types.Message):
    """
    On any msg bot will be flood to user
    """
    users = [msg.from_user.id] * 5  # Your users list
    await MessageBroadcaster(users, msg).run()  # run mailing


async def main():
    bot = Bot(token='BOT TOKEN HERE')
    dp = Dispatcher(bot=bot)

    dp.register_message_handler(message_handler, content_types=types.ContentTypes.ANY)
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
