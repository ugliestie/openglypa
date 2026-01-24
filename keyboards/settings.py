from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def kb_settings_main():
    inline_kb_list = [
        [InlineKeyboardButton(text="Генерация", callback_data='generate')],
        [InlineKeyboardButton(text="Статистика", callback_data='statistics')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate():
    inline_kb_list = [
        [
            InlineKeyboardButton(text="Обучение", callback_data='generate_learning'),
            InlineKeyboardButton(text="Лень", callback_data='generate_lazyness')
        ],
        [InlineKeyboardButton(text="Типы контента", callback_data='generate_types')],
        [InlineKeyboardButton(text="Назад", callback_data='settings')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_learning():
    inline_kb_list = [
        [InlineKeyboardButton(text="Удалить базу данных текста", callback_data='delete_text_db')],
        [InlineKeyboardButton(text="Удалить базу данных изображений", callback_data='delete_images_db')],
        [InlineKeyboardButton(text="Назад", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)

def kb_settings_generate_types():
    inline_kb_list = [
        [
            InlineKeyboardButton(text="Текст", callback_data='type_text'),
            InlineKeyboardButton(text="Топор 1+", callback_data='type_topor')
        ],
        [
            InlineKeyboardButton(text="Демотиваторы", callback_data='type_demotivators'),
            InlineKeyboardButton(text="Мемы", callback_data='type_memes')
        ],
        [InlineKeyboardButton(text="Назад", callback_data='generate')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_kb_list)