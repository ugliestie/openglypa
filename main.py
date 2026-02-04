import asyncio
import logging
from aiogram import Bot, Dispatcher

import random

from utils.sqlite import db_start

from utils.config import TOKEN
from handlers import commands, different_types, settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def on_startup():
	await db_start()

# Запуск процесса поллинга новых апдейтов
async def main():
	# Объект бота
	bot = Bot(token=TOKEN)

	# Диспетчер
	dp = Dispatcher()
	dp.startup.register(on_startup)

	dp.include_routers(commands.router, different_types.router, settings.router)

	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
