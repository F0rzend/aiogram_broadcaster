from aiogram import Bot, Dispatcher, types

from aiogram_broadcaster import TextBroadcaster

import asyncio
import logging


async def message_handler(msg: types.Message):
    """
    On any msg bot will be return chat_id to user
    """
    chats = [
        dict(
            chat_id=msg.from_user.id,
            mention=msg.from_user.get_mention(as_html=True)
        )

    ]
    await TextBroadcaster(chats, text="$mention, u'r id: <code>$chat_id</code>", parse_mode='HTML').run()  # run mailing


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
