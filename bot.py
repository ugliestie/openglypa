import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiofile import AIOFile
import re
import random

from utils.config import TOKEN, RANDOM_SEND, USUAL_SYNTAX, CHANCE

import mc
from mc.builtin import validators

import os

from PIL import Image, ImageOps
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


link_pattern = re.compile(
	r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
commands_pattern = re.compile(
	r"h j [a-z] [a-z]+|h j [a-z] \d+\Z"
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

async def gen(file, chars=None, words=None):
	async with AIOFile(file, encoding="utf-8") as f:
		text = await f.read()
		text_model = [sample.strip() for sample in text.split(",")]
	generator = mc.PhraseGenerator(samples=text_model)
	if chars is not None:
		message = generator.generate_phrase(
		attempts=5000,
		validators=[
			validators.chars_count(minimal=chars-10, maximal=chars+10),
		],
		)
	elif words is not None:
		message = generator.generate_phrase(
		attempts=5000,
		validators=[
			validators.words_count(minimal=words-1, maximal=words+5)
		],
		)
	else:
		message = generator.generate_phrase(
		validators=[
			validators.words_count(minimal=4, maximal=10),
			validators.chars_count(minimal=10, maximal=100),
		],
		)
	return message

async def gen_topor(path):
	async with AIOFile(f"{path}/text.txt", encoding="utf-8") as f:
		text = await f.read()
		text_model = [sample.strip() for sample in text.split(",")]
	emojis = ['📣', '‼️', '❗️', '❓', '⚡️']

	async with AIOFile(f"{path}/photos.txt", encoding="utf-8") as f:
		photos = await f.read()
		photos_model = [sample for sample in photos.split(",") if sample != ""]

	img = Image.open(await bot.download(file=f"{random.choice(photos_model)}"))
	w, h = img.size
	border = (random.randint(0, int(w*0.25)), random.randint(0, int(h*0.25)), random.randint(0, int(w*0.25)), random.randint(0, int(h*0.25)))
	img = ImageOps.crop(img, border)
	
	byte_io = BytesIO()
	byte_io.name = 'image.jpg'

	img.save(byte_io, 'JPEG')
	byte_io.seek(0)

	return str(random.choice(emojis) + ' ' + random.choice(text_model)[:random.randrange(2,8)]), byte_io.read()

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
	await message.answer("Привет, я Openglypa! Я анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!")

@dp.message(F.text.lower().contains('h j g'))
async def force_generate(message: types.Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		try:
			if message.text.lower() != "h j g":
				arg = message.text[6:]
				if arg.isdigit() and int(arg) > 10:
					gen_message = await gen(file=f"chats/{message.chat.id}/text.txt", count=int(arg))
				elif arg == 'l':
					gen_message = await gen(file=f"chats/{message.chat.id}/text.txt", words=30) 
				else:
					return
			else:
				gen_message = await gen(file=f"chats/{message.chat.id}/text.txt")
			await bot.send_message(message.chat.id, gen_message)
		except:
			await bot.send_message(message.chat.id, "База слов слишком мала для генерации")
	else:
		return

@dp.message(F.text.lower() == 'h j p')
async def generate_poll(message: types.Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		await bot.send_poll(
			chat_id=message.chat.id,
			question=await gen(file=f"chats/{message.chat.id}/text.txt"),
			options=[await gen(file=f"chats/{message.chat.id}/text.txt"), await gen(file=f"chats/{message.chat.id}/text.txt"), await gen(file=f"chats/{message.chat.id}/text.txt"), await gen(file=f"chats/{message.chat.id}/text.txt")],
			explanation=await gen(file=f"chats/{message.chat.id}/text.txt"),
			is_anonymous=False,
		)
	else:
		return

@dp.message(F.text.lower() == 'h j t')
async def generate_topor(message: types.Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		topor = await gen_topor(f"chats/{message.chat.id}")
		await bot.send_photo(
			chat_id=message.chat.id,
			photo=BufferedInputFile(topor[1], filename="topor.jpg"),
			caption=topor[0])
	else:
		return


@dp.message(F.text)
async def any_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if not os.path.exists(f"chats/{message.chat.id}"):
			os.mkdir(f"chats/{message.chat.id}")
		if RANDOM_SEND and chance_hit(CHANCE):
			try:
				if chance_hit(10):
					topor = await gen_topor(f"chats/{message.chat.id}")
					await bot.send_photo(
						chat_id=message.chat.id,
						photo=BufferedInputFile(topor[1], filename="topor.jpg"),
						caption=topor[0])
				else:
					gen_message = await gen(f"chats/{message.chat.id}/text.txt")
				await bot.send_message(message.chat.id, gen_message)
			except:
				pass
		if not re.findall(link_pattern, message.text) and not re.findall(commands_pattern, message.text):
			await write_words(message.text, f"chats/{message.chat.id}/text.txt")
	else:
		return

@dp.message(F.photo)
async def any_photo(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if not os.path.exists(f"chats/{message.chat.id}"):
			os.mkdir(f"chats/{message.chat.id}")
		async with AIOFile(f"chats/{message.chat.id}/photos.txt", "a", encoding="utf-8") as f:
			await f.write(message.photo[-1].file_id + ",")
	else:
		return

# Запуск процесса поллинга новых апдейтов
async def main():
	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
