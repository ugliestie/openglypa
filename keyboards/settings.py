from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.sqlite import *

def marker(flag):
    if flag == 1:
        return '✅'
    else:
        return '❌'

def kb_settings_main():
    inline_kb_list = [
        [InlineKeyboardButton(text="Генерация", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate():
    inline_kb_list = [
        [InlineKeyboardButton(text="🥱 Лень", callback_data='generate_lazyness')],
        [InlineKeyboardButton(text="🖌 Типы контента", callback_data='generate_types')],
        [InlineKeyboardButton(text="◀️ Назад", callback_data='settings')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_lazyness():
    inline_kb_list = [
        [InlineKeyboardButton(text="◀️ Назад", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_types():
    inline_kb_list = [
        [InlineKeyboardButton(text="🔑 Команды", callback_data='generate_types_commands')],
        [InlineKeyboardButton(text="🤖 Автоматический вызов", callback_data='generate_types_automatic')],
        [InlineKeyboardButton(text="◀️ Назад", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_types_commands(settings):
    inline_kb_list = [
        [
            InlineKeyboardButton(text=f"Текст | {marker(settings[0])}", callback_data='type_commands_text'),
            InlineKeyboardButton(text=f"Топор 1+ | {marker(settings[1])}", callback_data='type_commands_topor')
        ],
        [
            InlineKeyboardButton(text=f"Демотиваторы | {marker(settings[2])}", callback_data='type_commands_demotivators'),
            InlineKeyboardButton(text=f"Мемы | {marker(settings[3])}", callback_data='type_commands_memes')
        ],
        [InlineKeyboardButton(text=f"Опросы | {marker(settings[4])}", callback_data='type_commands_polls')],
        [InlineKeyboardButton(text="◀️ Назад", callback_data='generate_types')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_types_automatic(settings):
    inline_kb_list = [
        [
            InlineKeyboardButton(text=f"Текст | {marker(settings[0])}", callback_data='type_automatic_text'),
            InlineKeyboardButton(text=f"Топор 1+ | {marker(settings[1])}", callback_data='type_automatic_topor')
        ],
        [
            InlineKeyboardButton(text=f"Демотиваторы | {marker(settings[2])}", callback_data='type_automatic_demotivators'),
            InlineKeyboardButton(text=f"Мемы | {marker(settings[3])}", callback_data='type_automatic_memes')
        ],
        [
            InlineKeyboardButton(text=f"Опросы | {marker(settings[4])}", callback_data='type_automatic_polls'),
            InlineKeyboardButton(text=f"Реакции | {marker(settings[5])}", callback_data='type_automatic_reactions')
        ],
        [InlineKeyboardButton(text=f"Стикеры | {marker(settings[6])}", callback_data='type_automatic_stickers')],
        [InlineKeyboardButton(text="◀️ Назад", callback_data='generate_types')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)