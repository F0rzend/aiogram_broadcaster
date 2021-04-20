from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.environment import EnvironmentMiddleware

from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import MessageBroadcast

import asyncio
import logging


async def message_handler(msg: types.Message, broadcaster: AiogramBroadcaster):
    """
    The broadcaster will flood to a user whenever it receives a message
    """
    users = [msg.from_user.id] * 5  # Your users list
    await broadcaster.run(MessageBroadcast(users, msg))  # run mailing


async def main():
    bot = Bot(token='BOT TOKEN HERE')
    dp = Dispatcher(bot=bot)
    broadcaster = AiogramBroadcaster(bot=bot)

    # Use EnvironmentMiddleware to pass your AiogramBroadcaster to the handler
    dp.setup_middleware(EnvironmentMiddleware(dict(broadcaster=broadcaster)))

    dp.register_message_handler(message_handler, content_types=types.ContentTypes.ANY)
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level='DEBUG')
    asyncio.run(main())
