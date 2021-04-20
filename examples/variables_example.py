from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.environment import EnvironmentMiddleware

from aiogram_broadcaster import AiogramBroadcaster
from aiogram_broadcaster.broadcast import TextBroadcast

import asyncio
import logging


async def message_handler(msg: types.Message, broadcaster: AiogramBroadcaster):
    """
    On any msg bot will be return chat_id to user
    """
    users = [msg.from_user.id]
    await broadcaster.run(TextBroadcast(users, text="U'r id: $chat_id"))  # run mailing


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