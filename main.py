import asyncio
import logging
import random

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from handlers import commands, different_types, group_join, settings
from utils.chat_data import delete_image, read_images
from utils.config import TOKEN
from utils.sqlite import db_start

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
