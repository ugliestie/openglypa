import asyncio
import random
from typing import BinaryIO

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from alembic.config import Config

from alembic import command
from database.models import async_main
from handlers import commands, different_types, group_join, settings
from utils.chat_data import delete_image, read_images
from utils.config import TOKEN
from utils.logs import setup_rich_logger

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

async def random_image(chat_id: int) -> BinaryIO | None:
	"""Скачивание случайного изображения в BinaryIO

	Args:
		chat_id (int): id группового чата

	Returns:
		bytes | None: изображение, или None, если его не получилось скачать
	"""
	photos_model = await read_images(chat_id)
	for _ in range(3):
		file_id = random.choice(photos_model)
		try:
			return await bot.download(file=file_id)
		except:
			await delete_image(file_id, chat_id)

async def on_startup():
	await async_main()
	alembic_cfg = Config("alembic.ini")
	await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
	setup_rich_logger()

# Запуск процесса поллинга новых апдейтов
async def main():
	dp.startup.register(on_startup)

	dp.include_routers(commands.router, different_types.router, settings.router, group_join.router)

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
