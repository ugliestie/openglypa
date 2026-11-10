from aiogram.types import Message

from database.requests import set_setting


async def handle_rights(message: Message, type_setting: str, kind_setting: str):
    await set_setting(type_setting, kind_setting, False, message.chat.id)
    if (
        kind_setting == "topor"
        or kind_setting == "demotivators"
        or kind_setting == "memes"
    ):
        a, b = "прислать картинку", "присылать"
    elif kind_setting == "polls":
        a, b = "прислать опрос", "присылать"
    elif kind_setting == "reactions":
        a, b = "поставить реакцию", "ставить"
    elif kind_setting == "stickers":
        a, b = "прислать стикер", "присылать"
    elif kind_setting == "animations":
        a, b = "прислать гифку", "присылать"
    await message.reply(
        f"<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу {a} из-за того, что мне нельзя их присылать.\n\nЯ больше не буду пытаться. Чтобы исправить это, разрешите боту их {b} и в настройках бота включите настройку обратно."
    )
