import asyncio
import logging
import subprocess

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

def get_repo_state() -> str:
	try:
		commit = subprocess.check_output(["git", "rev-parse", "HEAD"],text=True).strip()
		status_output = subprocess.check_output(["git", "status", "--porcelain"],text=True).splitlines()
		local_changes = [line for line in status_output if line and not line.startswith("??")]
		url = subprocess.check_output(["git", "config", "remote.origin.url"],text=True).strip().replace('.git', '')
		repo_name = url.split('/')[-1]
		message = f"""Выполняется из <a href="{url}/commit/{commit}">{commit[:7]}@{repo_name}</a>"""
		if local_changes:
			message += " с изменениями"
		return message
	except subprocess.CalledProcessError:
		return 'Выполняется не из репозитория'

state = get_repo_state()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

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
