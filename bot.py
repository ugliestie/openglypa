import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
import random
import os
import re

from utils.db import *
from utils.text import *
from utils.topor import *
from utils.images import *

from utils.config import RANDOM_SEND, CHANCE, TOKEN

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()

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

async def random_image(chat_id):
	photos_model = await read_images(chat_id)
	return await bot.download(file=f"{random.choice(photos_model)}")

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
	await message.answer("Привет, я Openglypa! Я анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!")

@dp.message(F.text.lower().startswith('h j g'))
async def force_generate(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		try:
			if message.text.lower() != "h j g":
				arg = message.text[6:]
				if arg.isdigit() and int(arg) > 10:
					gen_message = await generate_sentence(chat_id=message.chat.id, count=int(arg))
				elif arg == 'l':
					gen_message = await generate_sentence(chat_id=message.chat.id, words=30) 
				else:
					return
			else:
				gen_message = await generate_sentence(chat_id=message.chat.id)
			await bot.send_message(message.chat.id, gen_message)
		except:
			await bot.send_message(message.chat.id, "База слов слишком мала для генерации")
	else:
		return

@dp.message(F.text.lower() == 'h j p')
async def generate_poll_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		await bot.send_poll(
			chat_id=message.chat.id,
			question=await generate_sentence(message.chat.id),
			options=await generate_sentences(message.chat.id, random.randint(3,6)),
			explanation=await generate_sentence(message.chat.id),
			is_anonymous=False,
		)
	else:
		return

@dp.message(F.text.lower() == 'h j t')
async def generate_topor_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if message.reply_to_message:
			if message.reply_to_message.photo:
				if message.reply_to_message.caption:
					logger.warning("happened")
					topor = await generate_topor(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id), message.reply_to_message.caption.capitalize())
				else:
					topor = await generate_topor(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id))
				await message.answer_photo(
					photo=BufferedInputFile(topor[1], filename="topor.jpg"),
					caption=topor[0])
		else:
			topor = await generate_topor(message.chat.id, await random_image(message.chat.id))
			await message.answer_photo(
				photo=BufferedInputFile(topor[1], filename="topor.jpg"),
				caption=topor[0])
	else:
		return

# TODO: обрабатывать текст при ответе
@dp.message(F.text.lower() == 'h j d')
async def generate_demotivator_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if message.reply_to_message:
			if message.reply_to_message.photo:
				demotivator = await generate_demotivator(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id))
				await message.answer_photo(
					photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		else:
			demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id))
			await message.answer_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
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
					topor = await generate_topor(message.chat.id, await random_image(message.chat.id))
					await bot.send_photo(
						chat_id=message.chat.id,
						photo=BufferedInputFile(topor[1], filename="topor.jpg"),
						caption=topor[0])
				else:
					gen_message = await generate_sentence(message.chat.id)
				await bot.send_message(message.chat.id, gen_message)
			except:
				pass
		if not re.findall(link_pattern, message.text) and not re.findall(commands_pattern, message.text):
			await write_words(message.text, message.chat.id)
	else:
		return

@dp.message(F.photo)
async def any_photo(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		await write_images(message.chat.id, message.photo[-1].file_id)
		if message.caption == "h j d":
			demotivator = await generate_demotivator(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.answer_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		elif message.caption == "h j t":
			topor = await generate_topor(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.answer_photo(
				photo=BufferedInputFile(topor[1], filename="topor.jpg"),
				caption=topor[0])
	else:
		return
	
# Запуск процесса поллинга новых апдейтов
async def main():
	await bot.delete_webhook(drop_pending_updates=True)
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(main())
