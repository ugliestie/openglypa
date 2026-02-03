import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.utils.chat_member import ADMINS
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import random
import os
import re

from utils.db import *
from utils.sqlite import *
from utils.text import *
from utils.topor import *
from utils.images import *

from utils.config import RANDOM_SEND, CHANCE, TOKEN

from keyboards.settings import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def on_startup():
	await db_start()

# Объект бота
bot = Bot(token=TOKEN)
# Диспетчер
dp = Dispatcher()
dp.startup.register(on_startup)

link_pattern = re.compile(
	r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
commands_pattern = re.compile(
	r"h j [a-z] [a-z]+|h j [a-z] \d+\Z"
)

class Settings(StatesGroup):
	waiting_for_lazyness = State()

def chance_hit(percent):
	if random.random()*100 < percent:
		return True
	return False

async def random_image(chat_id):
	photos_model = await read_images(chat_id)
	return await bot.download(file=f"{random.choice(photos_model)}")

async def is_message_admin(message: Message, user_id : int) -> bool:
	logger.warning(user_id)
	member = await message.bot.get_chat_member(message.chat.id, user_id)
	return isinstance(member, ADMINS)

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
	await message.reply("Привет, я Openglypa! Я анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!")

# Хэндлер на команду /start
@dp.message(Command("help"))
async def cmd_start(message: Message):
	await message.reply("Справка Openglypa\n\n"
						"h j g - генерация текста\n"
						"h j p - генерация опросов\n"
						"h j t - генерация Топор 1+ сообщения\n"
						"h j d - генерация демотиватора\n"
						"h j m - генрация мема из случайного шаблона\n"
						"h j s - настройки бота\n"
						"h j h - эта справка")

@dp.message(F.text.lower().startswith('h j g'))
async def force_generate(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[0] == 1:
		await bot.send_chat_action(chat_id=message.chat.id, action="typing")
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
			await message.reply(gen_message)
		except:
			await message.reply("База слов слишком мала для генерации")
	else:
		return

@dp.message(F.text.lower() == 'h j t')
async def generate_topor_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[1] == 1:
		await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		if message.reply_to_message:
			if message.reply_to_message.photo:
				if message.reply_to_message.caption:
					topor = await generate_topor(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id), message.reply_to_message.caption.capitalize())
				else:
					topor = await generate_topor(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id))
				await message.reply_photo(
					photo=BufferedInputFile(topor[1], filename="topor.jpg"),
					caption=topor[0])
		else:
			topor = await generate_topor(message.chat.id, await random_image(message.chat.id))
			await message.reply_photo(
				photo=BufferedInputFile(topor[1], filename="topor.jpg"),
				caption=topor[0])
	else:
		return

# TODO: обрабатывать текст при ответе
@dp.message(F.text.lower() == 'h j d')
async def generate_demotivator_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[2] == 1:
		await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		if message.reply_to_message:
			if message.reply_to_message.photo:
				demotivator = await generate_demotivator(message.chat.id, await bot.download(file=message.reply_to_message.photo[-1].file_id))
				await message.reply_photo(
					photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		else:
			demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id))
			await message.reply_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
	else:
		return

@dp.message(F.text.lower() == 'h j m')
async def generate_meme_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[3] == 1:
		await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		meme = await generate_meme(message.chat.id)
		await message.reply_photo(
			photo=BufferedInputFile(meme, filename="meme.jpg"))
	else:
		return

@dp.message(F.text.lower() == 'h j p')
async def generate_poll_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[4] == 1:
		await bot.send_chat_action(chat_id=message.chat.id, action="typing")
		await message.reply_poll(
			question=await generate_sentence(message.chat.id),
			options=await generate_sentences(message.chat.id, random.randint(3,6)),
			explanation=await generate_sentence(message.chat.id),
			is_anonymous=False,
		)
	else:
		return

@dp.message(F.text.lower() == 'h j s')
async def cmd_settings(message: Message):
	await check_group(message.chat.id)
	if await is_message_admin(message, message.from_user.id):
		await message.reply(
			"⚙️ Настройки Openglypa",
			reply_markup=kb_settings_main()
		)
	else:
		await message.reply(
			"У вас недостаточно прав в чате, чтобы вызывать эту команду"
		)

@dp.callback_query(F.data == 'generate')
async def process_callback_generate(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="⚙️ Настройки генерации",
			reply_markup=kb_settings_generate()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@dp.callback_query(F.data == 'generate_lazyness')
async def process_callback_generate_lazyness(callback: CallbackQuery, state: FSMContext):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="🥱 Управление ленью бота\n"
				f"На данный момент бот ленится писать в {(await get_automatic_generations(callback.message.chat.id))[0]}% случаев"
				"Ответьте значением от 0 до 100 чтобы изменить лень бота в процентах\n",
			reply_markup=kb_settings_generate_lazyness()
		)
		await state.set_state(Settings.waiting_for_lazyness.state)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@dp.message(Settings.waiting_for_lazyness)
async def lazyness_chosen(message: Message, state: FSMContext):
	if (message.text).isdigit and int(message.text) >= 0 and int(message.text) <= 100:
		await update_lazyness(int(message.text), message.chat.id)
		await message.reply(text="🥱 Лень бота изменена!",
							reply_markup=kb_settings_generate_lazyness())
		await state.clear()

@dp.callback_query(F.data.startswith('generate_types'))
async def process_callback_generate_types(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		if callback.data == "generate_types":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, отправляемых ботом",
				reply_markup=kb_settings_generate_types()
			)
		elif callback.data == "generate_types_commands":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, который присылает бот с помощью команд",
				reply_markup=kb_settings_generate_types_commands(await get_commands_settings(callback.message.chat.id))
			)
		elif callback.data == "generate_types_automatic":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, который присылает бот автоматически",
				reply_markup=kb_settings_generate_types_automatic(await get_automatic_settings(callback.message.chat.id))
			)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@dp.callback_query(F.data.startswith('type'))
async def process_callback_generate_types(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		setting = await get_commands_settings(callback.message.chat.id)
		if callback.data.startswith("type_commands"):
			setting = await get_commands_settings(callback.message.chat.id)
			if callback.data == "type_commands_text":
				await set_setting("commands", "text", not(setting[0]), callback.message.chat.id)
			elif callback.data == "type_commands_topor":
				await set_setting("commands", "topor", not(setting[1]), callback.message.chat.id)
			elif callback.data == "type_commands_demotivators":
				await set_setting("commands", "demotivators", not(setting[2]), callback.message.chat.id)
			elif callback.data == "type_commands_memes":
				await set_setting("commands", "memes", not(setting[3]), callback.message.chat.id)
			elif callback.data == "type_commands_polls":
				await set_setting("commands", "polls", not(setting[4]), callback.message.chat.id)
			await callback.message.edit_text(
					text="⚙️ Настройки типов контента, который присылает бот с помощью команд",
					reply_markup=kb_settings_generate_types_commands(await get_commands_settings(callback.message.chat.id))
				)	
		elif callback.data.startswith("type_automatic"):
			setting = await get_automatic_settings(callback.message.chat.id)
			if callback.data == "type_automatic_text":
				await set_setting("automatic", "text", not(setting[0]), callback.message.chat.id)
			elif callback.data == "type_automatic_topor":
				await set_setting("automatic", "topor", not(setting[1]), callback.message.chat.id)
			elif callback.data == "type_automatic_demotivators":
				await set_setting("automatic", "demotivators", not(setting[2]), callback.message.chat.id)
			elif callback.data == "type_automatic_memes":
				await set_setting("automatic", "memes", not(setting[3]), callback.message.chat.id)
			elif callback.data == "type_automatic_polls":
				await set_setting("automatic", "polls", not(setting[4]), callback.message.chat.id)
			await callback.message.edit_text(
					text="⚙️ Настройки типов контента, который присылает бот автоматически",
					reply_markup=kb_settings_generate_types_automatic(await get_automatic_settings(callback.message.chat.id))
				)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@dp.callback_query(F.data == 'settings')
async def process_callback_settings(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="⚙️ Настройки Openglypa",
			reply_markup=kb_settings_main()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@dp.message(F.text)
async def any_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if not os.path.exists("chats"):
			os.mkdir(f"chats")
		if not os.path.exists(f"chats/{message.chat.id}"):
			os.mkdir(f"chats/{message.chat.id}")
		generation = await get_automatic_generations(message.chat.id)
		if generation[0] != 100 and chance_hit(100 - generation[0]):
			try:
				set_generations = [i for i in range(1, 5) if generation[i] == 1]
				choice = random.choice(set_generations)
				if choice == 1:
					gen_message = await generate_sentence(message.chat.id)
					await message.answer(gen_message)
				elif choice == 2:
					topor = await generate_topor(message.chat.id, await random_image(message.chat.id))
					await message.answer_photo(
						photo=BufferedInputFile(topor[1], filename="topor.jpg"),
						caption=topor[0])
				elif choice == 3:
					demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id))
					await message.answer_photo(
						photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
				elif choice == 4:
					meme = await generate_meme(message.chat.id)
					await message.answer_photo(
						photo=BufferedInputFile(meme, filename="meme.jpg"))
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
			await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			demotivator = await generate_demotivator(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.reply_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		elif message.caption == "h j t":
			await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			topor = await generate_topor(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.reply_photo(
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
