from collections.abc import Awaitable, Callable
from time import monotonic
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, default_rate: float = 7) -> None:
        self.default_rate = default_rate
        # scoped per (user, handler): one handler's throttle must not
        # suppress unrelated handlers, like v2's per-handler rate_limit
        self.last_call: dict[tuple[int, Any], float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        if event.from_user is None:  # channel posts have no sender
            return await handler(event, data)

        rate = self.default_rate
        flag = get_flag(data, "rate_limit")
        if flag is not None:
            rate = flag.get("rate", self.default_rate)

        key = (event.from_user.id, data["handler"].callback)
        now = monotonic()
        last = self.last_call.get(key)
        if last is not None and now - last < rate:
            return await event.reply(
                f"<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я устаю!\nПопробуй снова через {now - last:.2f} секунд."
            )
        self.last_call[key] = now
        return await handler(event, data)
