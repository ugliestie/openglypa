from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.utils.chat_member import ADMINS

from utils.sqlite import *
from utils.text import *
from utils.topor import *
from utils.images import *

from main import random_image

from keyboards.settings import kb_settings_main

router = Router()

async def is_message_admin(message: Message, user_id : int) -> bool:
	member = await message.bot.get_chat_member(message.chat.id, user_id)
	return isinstance(member, ADMINS)

# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: Message):
	await message.reply("Привет, я Openglypa! Я анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!")

# Хэндлер на команду /start
@router.message(Command("help"))
async def cmd_help(message: Message):
	await message.reply("Справка Openglypa\n\n"
						"h j g - генерация текста\n"
						"h j p - генерация опросов\n"
						"h j t - генерация Топор 1+ сообщения\n"
						"h j d - генерация демотиватора\n"
						"h j m - генрация мема из случайного шаблона\n"
						"h j s - настройки бота\n"
						"h j h - эта справка")

@router.message(F.text.lower().startswith('h j g'))
async def force_generate(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[0] == 1:
		await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
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

@router.message(F.text.lower() == 'h j t')
async def generate_topor_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[1] == 1:
		await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		if message.reply_to_message:
			if message.reply_to_message.photo:
				if message.reply_to_message.caption:
					topor = await generate_topor(message.chat.id, await message.bot.download(file=message.reply_to_message.photo[-1].file_id), message.reply_to_message.caption.capitalize())
				else:
					topor = await generate_topor(message.chat.id, await message.bot.download(file=message.reply_to_message.photo[-1].file_id))
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
@router.message(F.text.lower() == 'h j d')
async def generate_demotivator_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[2] == 1:
		await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		if message.reply_to_message:
			if message.reply_to_message.photo:
				demotivator = await generate_demotivator(message.chat.id, await message.bot.download(file=message.reply_to_message.photo[-1].file_id))
				await message.reply_photo(
					photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		else:
			demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id))
			await message.reply_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
	else:
		return

@router.message(F.text.lower() == 'h j m')
async def generate_meme_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[3] == 1:
		await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
		meme = await generate_meme(message.chat.id)
		await message.reply_photo(
			photo=BufferedInputFile(meme, filename="meme.jpg"))
	else:
		return

@router.message(F.text.lower() == 'h j p')
async def generate_poll_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[4] == 1:
		await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
		await message.reply_poll(
			question=await generate_sentence(message.chat.id),
			options=await generate_sentences(message.chat.id, random.randint(3,6)),
			explanation=await generate_sentence(message.chat.id),
			is_anonymous=False,
		)
	else:
		return

@router.message(F.text.lower() == 'h j s')
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