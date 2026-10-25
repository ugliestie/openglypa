import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from alembic.config import Config
from rich.logging import RichHandler

from alembic import command
from database.models import async_main
from handlers import commands, different_types, group_join, settings
from utils.config import TOKEN

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING", format=FORMAT, datefmt="[%X]", handlers=[RichHandler(
				rich_tracebacks=True,
				tracebacks_show_locals=True,
				show_time=False)]
)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

class RandomImageNotFound(BaseException):
    pass

async def on_startup():
	await async_main()
	alembic_cfg = Config("alembic.ini")
	await asyncio.to_thread(command.upgrade, alembic_cfg, "head")

# Запуск процесса поллинга новых апдейтов
async def main():
	dp.startup.register(on_startup)

	dp.include_routers(commands.router, different_types.router, settings.router, group_join.router)

	await bot.delete_webhook(drop_pending_updates=True)

	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
