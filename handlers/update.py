"""стой не смотри Ш
ооооооохх бляяя
можешь смотреть я застрял
wow"""
import difflib
import os
import shutil

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from pkld import pkld

from database.requests import delete_group


@pkld
def last_file():
    return open("CHANGELOG.md", "rt").readlines()


def get_changes():
    new_file = open("CHANGELOG.md", "rt").readlines()

    d = difflib.Differ()
    diffs = d.compare(last_file(), new_file)

    s = ""

    for line in diffs:
        code = line[:2]
        if code == "+ ":
            s += "" + line[2:].strip() + "\n"

    last_file.clear()
    last_file()

    return s


async def update_broadcast(bot: Bot) -> None:
    changes = get_changes()
    if changes != "":
        chats = [
            int(n)
            for n in os.listdir("chats")
            if os.path.isdir(os.path.join("chats", n))
        ]
        for chat_id in chats:
            try:
                await bot.send_message(
                    chat_id,
                    text="Бот обновился!\nВот, что нового было добавлено или исправлено:\n\n"
                    + changes,
                )
            except TelegramForbiddenError as e:
                if "the group chat was deleted" in str(e):
                    shutil.rmtree(f"chats/{chat_id}")
                    await delete_group(chat_id)