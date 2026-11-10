# https://github.com/Vealke/ACHY-Plus/blob/1d3c8b53d96ee8d76890d2a59c2116e75d516416/src/telegram/middleware/ratelimit.py#L8
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    cache: TTLCache[int, Any]

    def __init__(self, time_limit: float = 2.5) -> None:
        super().__init__()
        self.cache = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Проверяем, что событие является сообщением (Message)
        if isinstance(event, Message):
            chat_id = event.chat.id

            # Если чат уже есть в кэше — игнорируем его сообщение
            if chat_id in self.cache:
                await event.reply(
                    "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я устаю!\nПопробуй попозже."
                )
                return

            self.cache[chat_id] = True

        return await handler(event, data)
