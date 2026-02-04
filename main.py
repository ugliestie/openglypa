import asyncio
import logging
from aiogram import Bot, Dispatcher

import random

from utils.sqlite import db_start
from utils.db import read_images

from utils.config import TOKEN
from handlers import commands, different_types, settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Объект бота
bot = Bot(token=TOKEN)

# Диспетчер
dp = Dispatcher()

async def random_image(chat_id):
	photos_model = await read_images(chat_id)
	return await bot.download(file=f"{random.choice(photos_model)}")

async def on_startup():
	await db_start()

# Запуск процесса поллинга новых апдейтов
async def main():
	dp.startup.register(on_startup)

	dp.include_routers(commands.router, different_types.router, settings.router)

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
