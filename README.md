[![PyPI version](https://img.shields.io/pypi/v/aiogram-broadcaster.svg)](https://pypi.org/project/aiogram-broadcaster/0.0.2/) [![Python](https://img.shields.io/badge/Python-3.7+-green)](https://www.python.org/downloads/) [![Aiogram](https://img.shields.io/badge/aiogram-2.12+-blue)](https://pypi.org/project/aiogram/) 

# Aiogram Broadcaster

A simple and straightforward broadcasting implementation for aiogram

## Installaiton

    $ pip install aiogram-broadcaster

## Examples

**Few steps before getting started...**

- First, you should obtain token for your bot from [BotFather](https://t.me/BotFather)
and make sure you started a conversation with the bot.
- Obtain your user id from [JSON Dump Bot](https://t.me/JsonDumpBot) in order to test out broadcaster.

**Note:** These and even more examples can found in [`examples/`](https://github.com/fonco/aiogram_broadcaster/tree/main/examples) directory

### Base usage
```python
from aiogram_broadcaster import TextBroadcaster

import asyncio


async def main():

    # Initialize a text broadcaster (you can directly pass a token)
    broadcaster = TextBroadcaster('USERS IDS HERE', 'hello!', bot_token='BOT TOKEN HERE')
    
    # Run the broadcaster and close it afterwards
    try:
        await broadcaster.run()
    finally:
        await broadcaster.close_bot()


if __name__ == '__main__':
    asyncio.run(main())
```

### Embed a broadcaster in a message handler
```python
from aiogram import Bot, Dispatcher, types

from aiogram_broadcaster import MessageBroadcaster

import asyncio


async def message_handler(msg: types.Message):
    """
    The broadcaster will flood to a user whenever it receives a message
    """
    
    users = [msg.from_user.id] * 5  # Your users list
    await MessageBroadcaster(users, msg).run()  # Run the broadcaster


async def main():

    # Initialize a bot and a dispatcher
    bot = Bot(token='BOT TOKEN HERE')
    dp = Dispatcher(bot=bot)

    # Register a message handler
    dp.register_message_handler(message_handler, content_types=types.ContentTypes.ANY)
    
    # Run the bot and close it afterwards
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
```

