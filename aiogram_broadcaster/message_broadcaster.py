import logging
from asyncio import sleep
from copy import deepcopy
from string import Template
from typing import Dict, Optional

from aiogram import Bot
from aiogram.types import Message, ParseMode
from aiogram.utils import exceptions

from .types import ChatsType, MarkupType, ChatIdType
from .base import BaseBroadcaster


class MessageBroadcaster(BaseBroadcaster):
    def __init__(
            self,
            chats: ChatsType,
            message: Message,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            allow_sending_without_reply: Optional[bool] = None,
            reply_markup: MarkupType = None,
            bot: Optional[Bot] = None,
            timeout: float = 0.02,
            logger=__name__
    ):
        super().__init__(
            chats=chats,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply,
            reply_markup=reply_markup,
            bot=bot,
            timeout=timeout,
            logger=logger,
        )
        self._setup_chats(chats)
        self.message = message
        self.bot = bot if bot else Bot.get_current()
        self.timeout = timeout

        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)

        self.logger = logger

    @staticmethod
    async def send_copy(
            message: Message,
            chat_id: ChatIdType,
            disable_notification: Optional[bool] = None,
            disable_web_page_preview: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            allow_sending_without_reply: Optional[bool] = None,
            reply_markup: MarkupType = None,
    ) -> Message:
        kwargs = {
            "chat_id": chat_id,
            "allow_sending_without_reply": allow_sending_without_reply,
            "reply_markup": reply_markup or message.reply_markup,
            "parse_mode": ParseMode.HTML,
            "disable_notification": disable_notification,
            "reply_to_message_id": reply_to_message_id,
        }
        if message.caption:
            text = message.caption
        elif message.text:
            text = message.text
        else:
            text = None

        if message.text:
            kwargs["disable_web_page_preview"] = disable_web_page_preview
            return await message.bot.send_message(text=text, **kwargs)
        elif message.audio:
            return await message.bot.send_audio(
                audio=message.audio.file_id,
                caption=text,
                title=message.audio.title,
                performer=message.audio.performer,
                duration=message.audio.duration,
                **kwargs,
            )
        elif message.animation:
            return await message.bot.send_animation(
                animation=message.animation.file_id, caption=text, **kwargs
            )
        elif message.document:
            return await message.bot.send_document(
                document=message.document.file_id, caption=text, **kwargs
            )
        elif message.photo:
            return await message.bot.send_photo(
                photo=message.photo[-1].file_id, caption=text, **kwargs
            )
        elif message.sticker:
            kwargs.pop("parse_mode")
            return await message.bot.send_sticker(sticker=message.sticker.file_id, **kwargs)
        elif message.video:
            return await message.bot.send_video(
                video=message.video.file_id, caption=text, **kwargs
            )
        elif message.video_note:
            kwargs.pop("parse_mode")
            return await message.bot.send_video_note(
                video_note=message.video_note.file_id, **kwargs
            )
        elif message.voice:
            return await message.bot.send_voice(voice=message.voice.file_id, **kwargs)
        elif message.contact:
            kwargs.pop("parse_mode")
            return await message.bot.send_contact(
                phone_number=message.contact.phone_number,
                first_name=message.contact.first_name,
                last_name=message.contact.last_name,
                vcard=message.contact.vcard,
                **kwargs,
            )
        elif message.venue:
            kwargs.pop("parse_mode")
            return await message.bot.send_venue(
                latitude=message.venue.location.latitude,
                longitude=message.venue.location.longitude,
                title=message.venue.title,
                address=message.venue.address,
                foursquare_id=message.venue.foursquare_id,
                foursquare_type=message.venue.foursquare_type,
                **kwargs,
            )
        elif message.location:
            kwargs.pop("parse_mode")
            return await message.bot.send_location(
                latitude=message.location.latitude,
                longitude=message.location.longitude,
                **kwargs,
            )
        elif message.poll:
            kwargs.pop("parse_mode")
            return await message.bot.send_poll(
                question=message.poll.question,
                options=[option.text for option in message.poll.options],
                is_anonymous=message.poll.is_anonymous,
                allows_multiple_answers=message.poll.allows_multiple_answers,
                **kwargs,
            )
        elif message.dice:
            kwargs.pop("parse_mode")
            return await message.bot.send_dice(
                emoji=message.dice.emoji,
                **kwargs,
            )
        else:
            raise TypeError("This type of message can't be copied.")

    @staticmethod
    def get_updated_message(message: Message, text_args: dict):
        msg = deepcopy(message)
        text = Template(msg.html_text).safe_substitute(text_args) if (msg.text or msg.caption) else None
        if msg.caption:
            msg.caption = text
        elif msg.text:
            msg.text = text
        else:
            return message

        return msg

    async def send(
            self,
            chat: Dict,
    ) -> bool:
        if isinstance(chat, Dict):
            chat_id = chat.get('chat_id')
            text_args = chat
        else:
            return False
        try:
            msg = self.get_updated_message(self.message, text_args)
            await self.send_copy(
                message=msg,
                chat_id=chat_id,
                disable_notification=self.disable_notification,
                disable_web_page_preview=self.disable_web_page_preview,
                reply_to_message_id=self.reply_to_message_id,
                allow_sending_without_reply=self.allow_sending_without_reply,
                reply_markup=self.reply_markup,
            )
        except exceptions.RetryAfter as e:
            self.logger.debug(
                f"Target [ID:{chat_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
            )
            await sleep(e.timeout)
            return await self.send(chat_id)  # Recursive call
        except (
                exceptions.BotBlocked,
                exceptions.ChatNotFound,
                exceptions.UserDeactivated,
                exceptions.ChatNotFound
        ) as e:
            self.logger.debug(f"Target [ID:{chat_id}]: {e.match}")
        except exceptions.TelegramAPIError:
            self.logger.exception(f"Target [ID:{chat_id}]: failed")
        else:
            self.logger.debug(f"Target [ID:{chat_id}]: success")
            return True
        return False
