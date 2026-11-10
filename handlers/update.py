"""стой не смотри Ш
ооооооохх бляяя
можешь смотреть я застрял
wow"""

import difflib
import logging
import os
import shutil

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from pkld import pkld

from database.requests import delete_group

logger = logging.getLogger(__name__)


@pkld
def last_file():
    return open("CHANGELOG.md", "rt").readlines()


def get_changes() -> str:
    new_file = open("CHANGELOG.md", "rt").readlines()

    d = difflib.Differ()
    diffs = d.compare(last_file(), new_file)

    s = ""

    for line in diffs:
        code = line[:2]
        if code == "+ ":
            s += line[2:].strip() + "\n"

    last_file.clear()
    last_file()

    return s.replace("\\n", "\n")


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
                else:
                    logger.error(
                        f"Ошибка при апдейтном сообщении в чате {chat_id}: {e!s}"
                    )
            except TelegramBadRequest as e:
                if "chat not found" in str(e):
                    shutil.rmtree(f"chats/{chat_id}")
                    await delete_group(chat_id)
                else:
                    logger.error(
                        f"Ошибка при апдейтном сообщении в чате {chat_id}: {e!s}"
                    )
            except Exception as e:
                logger.error(f"Ошибка при апдейтном сообщении в чате {chat_id}: {e!s}")
