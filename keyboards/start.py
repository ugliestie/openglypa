from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def kb_add(username: str):
    inline_kb_list = [
        [InlineKeyboardButton(text="Добавить в группу", url=f'https://t.me/{username}?startgroup=start')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)