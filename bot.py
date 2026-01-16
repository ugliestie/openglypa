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

from utils.config import TOKEN, RANDOM_SEND, USUAL_SYNTAX

import mc
from mc.builtin import validators

import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


link_pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

async def write_words(*args):
    text, file = args
    async with AIOFile(file, "a", encoding="utf-8") as f:
        text = text.replace("\n", ". ").replace("\n\n", ". ")
        await f.write(text + ",")

async def send_and_gen_sentence(*args):
    file, chat_id = args
    if not os.path.exists(file):
        message = "База слов для этой беседы ещё не существует"
        await bot.send_message(chat_id, message)
        return
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
    if not message:
        message = "База слов слишком мала для генерации"
    await bot.send_message(chat_id, message)

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
    await send_and_gen_sentence(
                f"chats/{message.chat.id}.txt", message.chat.id
            )

@dp.message(F.text.lower() == 'h j p')
async def force_generate(message: types.Message):
    await send_and_gen_sentence(
                f"chats/{message.chat.id}.txt", message.chat.id
            )

@dp.message(F.text)
async def any_message(message: Message):
    if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
        logger.log(1, "logged")
        if random.randint(0, 33) <= 24 and RANDOM_SEND:
            await send_and_gen_sentence(
                f"chats/{message.chat.id}.txt", message.chat.id
            )
        if not re.findall(link_pattern, message.text):
            await write_words(message.text, f"chats/{message.chat.id}.txt")
        

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if not os.path.exists("chats/"):
        os.mkdir("chats/")
    asyncio.run(main())
