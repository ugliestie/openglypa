import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

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

	dp.include_routers(commands.router, different_types.router, settings.router, group_join.router)

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
