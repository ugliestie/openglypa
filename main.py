import asyncio
from typing import Callable, Any, Awaitable, Union
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import BaseMiddleware
from aiogram.types import Message

import random

from utils.sqlite import db_start
from utils.chat_data import read_images, delete_image

from utils.config import TOKEN
from handlers import commands, different_types, settings, group_join

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Объект бота
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Диспетчер
dp = Dispatcher()

# Middleware для обработки альбомов в сообщении
# https://ru.stackoverflow.com/questions/1456135
class AlbumMiddleware(BaseMiddleware):
    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        self.latency = latency

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: dict[str, Any]
    ) -> Any:
        if not message.media_group_id:
            await handler(message, data)
            return
        try:
            self.album_data[message.media_group_id].append(message)
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            data['_is_last'] = True
            data["album"] = self.album_data[message.media_group_id]
            await handler(message, data)

        if message.media_group_id and data.get("_is_last"):
            del self.album_data[message.media_group_id]
            del data['_is_last']

async def random_image(chat_id):
	photos_model = await read_images(chat_id)
	for attempt_number in range(3):
		file_id = random.choice(photos_model)
		try:
			return await bot.download(file=file_id)
		except:
			await delete_image(file_id, chat_id)

async def on_startup():
	await db_start()

# Запуск процесса поллинга новых апдейтов
async def main():
	dp.startup.register(on_startup)

	dp.message.middleware(AlbumMiddleware())
	dp.include_routers(commands.router, different_types.router, settings.router, group_join.router)

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
