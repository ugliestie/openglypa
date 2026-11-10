import asyncio
import logging
import subprocess

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from alembic.config import Config
from rich import print
from rich.logging import RichHandler

from alembic import command
from database.models import async_close, async_main
from handlers import commands, different_types, group_join, settings
from handlers.update import update_broadcast
from utils.config import TOKEN

FORMAT = "%(message)s"
logging.basicConfig(
    level="WARNING",
    format=FORMAT,
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            # tracebacks_show_locals=True, # разкоменчивать только в случае если надо, а то вывод бешеный
            tracebacks_max_frames=1,
            show_time=True,
        )
    ],
)
logger = logging.getLogger(__name__)


def get_repo_state(kind: str = "") -> str:
    """Получение текущего репозиторияиз под которого запущен бот

    Args:
            kind (str): тип вывода

    Returns:
            str: если kind не console, то отпраляется заготовка для h j h, если console - для консоли
    """
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip()
        status_output = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True
        ).splitlines()
        local_changes = [
            line for line in status_output if line and not line.startswith("??")
        ]
        url = (
            subprocess.check_output(["git", "config", "remote.origin.url"], text=True)
            .strip()
            .replace(".git", "")
        )
        repo_name = url.split("/")[-1]
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], text=True
        ).strip()
        if kind != "console":
            message = f"""Выполняется из <a href="{url}/commit/{commit}">{repo_name}@{branch}-{commit[:7]}</a>"""
            if local_changes:
                message += " с изменениями"
        else:
            message = f"""Выполняется из {repo_name}@{branch}-{commit[:7]}"""
            if local_changes:
                message += " с изменениями"
        return message
    except subprocess.CalledProcessError:
        return "Выполняется не из репозитория"


state = get_repo_state()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


async def on_startup():
    await async_main()
    alembic_cfg = Config("alembic.ini")
    await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
    print("[green][b]База данных готова к работе![/b][/green]")
    print("[green][b]Запускаем бота...[/b][/green]")
    print("""[green]
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣤⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣻⠽⣷⣶⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⣤⣤⡄⠀⠛⣽⣶⣹⣿⡃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢀⣶⡇⠀⠀⠀⠀⠀⡀⣶⡎⠉⠉⣿⣷⣶⣶⣿⣿⡒⢯⣷⣶⣶⣶⣶⣶⣶⣶⣶⣶⣆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡭⣿⡿⠀⠀⢠⣼⠿⠀⢠⣤⠀⣤⡄⠀⠀⠀⠘⠙⠊⠛⠛⠛⠛⠛⠏⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡵⢫⢿⣶⣶⡏⢹⣙⣦⡲⣽⠀⣏⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⣵⣏⡞⣥⣋⡇⠀⠀⠀⠰⠹⠜⠀⠀⠀⠀⣤⣤⣤⠀⣤⣤⣤⣤⣤⣤⣤⣯⡿⠋⠀⠀⣤⣤⣤⣤⡄⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢵⣾⠀⠁⠁⠀⠀⢀⢀⠀⠀⠀⠀⢠⣶⠉⠉⠉⣶⣿⡿⡹⣶⣷⡎⠉⠉⠁⠀⠀⣶⡏⠉⠉⠉⢵⡆⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⡼⠿⠀⠀⠀⢠⣤⠿⠿⢿⣤⠄⢠⣬⢿⡄⠀⠀⠀⣯⠽⠿⣿⡇⠀⠀⠀⠀⢸⣿⣿⣿⣧⣤⠀⣺⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⢸⣿⡀⠀⠀⠉⡶⡆⠉⠈⣖⣶⣲⣶⡍⠀⢐⣿⡇⠀⠀⣶⣶⣾⣿⣿⣿⣿⣿⣶⡏⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢨⣽⠮⣤⢤⡤⡤⠿⠇⢀⡤⣤⡰⠿⠀⠀⢨⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢸⣿⣖⠁⠈⠀⠉⣷⡒⡾⡜⢦⡃⢀⣶⣶⡾⣽⣞⡿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠉⠁⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣇⡤⠀⠀⠀⠸⠿⣿⣧⣠⣠⠀⠨⢵⣭⢧⣻⣟⣮⢷⣻⠷⣾⣽⣿⣿⣿⣿⣿⣿⠿⠿⠯⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⠀⠀⠀⠀⠀⣿⣿⣿⡿⣶⣶⣾⢯⡟⣷⡻⣞⣯⡷⣿⣷⣿⡯⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⣤⣄⣸⣿⣯⣽⣽⣿⣿⣿⣿⣿⣧⣟⡾⣽⣯⣷⣿⣽⡿⢿⣿⣿⣿⣇⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡮⠉⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⡿⣷⣾⣿⣷⣿⣿⣿⢭⡹⣍⠯⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⢳⣯⡽⣿⣗⡣⣝⣿⣿⣿⣿⣿⡧⣛⠴⡿⢿⣿⣿⣇⡀⠀⠀⠀⢀⣠⣠⣠⣀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⢳⡖⠀⠉⢿⣿⣿⣿⣿⣿⡿⣼⣻⢾⣿⣿⣧⠹⣿⣿⣿⣿⣿⣏⠷⣩⠞⣱⢻⣿⣿⣿⡇⠀⠀⣶⣮⠙⠉⣹⣷⣶
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⠿⠿⠿⠿⠂⠸⢿⣿⣷⣯⣿⣿⠲⣌⡳⡱⢎⠿⣿⠱⣎⠳⣥⢛⡴⢻⠿⡿⣿⣿⣿⡿⡇⠀⠀⠿⠇⢸⣿
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⡛⡵⢪⠵⣙⢎⡳⢎⡳⣌⠷⣌⠳⣜⢣⠻⡴⢻⣹⢻⠚⠃⠀⠀⠀⣰⣞⠛
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⢜⡱⣋⢞⡱⢎⡵⣋⠶⣩⠞⣬⢓⢮⣹⣿⣿⣿⡇⠀⠀⠀⢀⣀⠿⠇⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⣿⣿⡟⣛⢮⡱⣍⠮⣕⢫⠖⣭⢚⣵⣿⣶⣿⣶⣿⣿⠛⠛⢳⣶⣶⣶⣞⠛⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⠿⠿⢿⣿⣲⣓⣮⣳⣿⣿⣿⢿⡿⣿⡿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠛⠛⠛⠛⠛⣿⣻⠟⠚⠚⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣰⠿⠄⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠛⠛⠛⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⣀⣸⣿⣀⣿⣇⣨⠿⠁⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠛⠛⠛⠛⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
	[/green]""")


async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()
    await async_close()
    print("[red][b]Пока![/b][/red]")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_routers(
        commands.router, different_types.router, settings.router, group_join.router
    )

    await bot.delete_webhook(drop_pending_updates=True)

    print(f"[yellow][b]{get_repo_state('console')}[/b][/yellow]")

    print(
        "[green][b]Проверяем нововведения и отправляем рассылку по чатам...[/b][/green]"
    )

    await update_broadcast(bot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
