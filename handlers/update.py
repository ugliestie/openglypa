"""        стой не смотри Ш
        ооооооохх бляяя
        можешь смотреть я застрял
        wow """
        
from pkld import pkld
from aiogram import Bot
import difflib
import os

@pkld
def last_file():
    return open("CHANGELOG.md", "rt").readlines()

def get_changes():
    new_file = open("CHANGELOG.md", "rt").readlines()

    d = difflib.Differ()
    diffs = d.compare(last_file(), new_file)

    s = ''

    for line in diffs:
        code = line[:2]
        if code == '+ ':
            s += "" + line[2:].strip() + '\n'
    
    last_file.clear()
    last_file()
    
    return s

async def update_broadcast(bot: Bot) -> None:
    changes = get_changes()
    if changes != '':
        chats = [int(n) for n in os.listdir("chats") if os.path.isdir(os.path.join("chats", n))]
        for chat in chats:
            await bot.send_message(chat, text="Бот обновился!\nВот, что нового было добавлено или исправлено:\n\n" + changes)
    