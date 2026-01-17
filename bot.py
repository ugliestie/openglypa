import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from aiofile import AIOFile
import re
import random

from utils.config import TOKEN, RANDOM_SEND, USUAL_SYNTAX, CHANCE

import mc
from mc.builtin import validators

import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


link_pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
commands_pattern = re.compile(
    r"h j [a-z]\Z"
)

def chance_hit(percent):
    if random.random()*100 < percent:
        return True
    return False

async def write_words(*args):
    text, file = args
    async with AIOFile(file, "a", encoding="utf-8") as f:
        text = text.replace("\n", ". ").replace("\n\n", ". ")
        await f.write(text + ",")

async def gen(file):
    async with AIOFile(file, encoding="utf-8") as f:
        text = await f.read()
        text_model = [sample.strip() for sample in text.split(",")]
    generator = mc.PhraseGenerator(samples=text_model)
    message = generator.generate_phrase(
    validators=[
        validators.words_count(minimal=4, maximal=10),
        validators.chars_count(minimal=10, maximal=100),
    ],
    )
    return message

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

@dp.message(F.text.lower() == 'h j g')
async def force_generate(message: types.Message):
    try:
        gen_message = await gen(f"chats/{message.chat.id}.txt")
        await bot.send_message(message.chat.id, gen_message)
    except:
        await bot.send_message(message.chat.id, "База слов слишком мала для генерации")

@dp.message(F.text.lower() == 'h j p')
async def generate_poll(message: types.Message):
    await bot.send_poll(
        chat_id=message.chat.id,
        question=await gen(f"chats/{message.chat.id}.txt"),
        options=[await gen(f"chats/{message.chat.id}.txt"), await gen(f"chats/{message.chat.id}.txt"), await gen(f"chats/{message.chat.id}.txt"), await gen(f"chats/{message.chat.id}.txt")],
        explanation=await gen(f"chats/{message.chat.id}.txt"),
        is_anonymous=False,
    )

@dp.message(F.text.lower() == 'h j t')
async def generate_topor(message: types.Message):
    async with AIOFile(f"chats/{message.chat.id}.txt", encoding="utf-8") as f:
        text = await f.read()
        text_model = [sample.strip() for sample in text.split(",")]
    emojis = ['📣', '‼️', '❗️', '❓', '⚡️']
    phrase = random.choice(emojis) + ' ' + random.choice(text_model)[:random.randrange(1,5)]
    await bot.send_message(message.chat.id, phrase)


@dp.message(F.text)
async def any_message(message: Message):
    if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
        if RANDOM_SEND and chance_hit(CHANCE):
            try:
                gen_message = await gen(f"chats/{message.chat.id}.txt")
                await bot.send_message(message.chat.id, gen_message)
            except:
                await bot.send_message(message.chat.id, "База слов слишком мала для генерации")
        if not re.findall(link_pattern, message.text) and not re.findall(commands_pattern, message.text):
            await write_words(message.text, f"chats/{message.chat.id}.txt")
        

# Запуск процесса поллинга новых апдейтов
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not os.path.exists("chats/"):
        os.mkdir("chats/")
    asyncio.run(main())
