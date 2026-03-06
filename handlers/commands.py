from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
from aiogram.utils.chat_member import ADMINS
from aiogram.exceptions import TelegramBadRequest

from utils.sqlite import *
from utils.text import *
from utils.topor import *
from utils.images import *

from main import random_image

from keyboards.settings import kb_settings_main

from main import logger

router = Router()

async def is_message_admin(message: Message, user_id : int) -> bool:
	member = await message.bot.get_chat_member(message.chat.id, user_id)
	return isinstance(member, ADMINS)

@router.message(Command("start"))
async def cmd_start(message: Message):
	if message.chat.type == 'private':
		await message.reply("Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!")
	elif (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		await message.reply("Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nНастрой меня с помощью команды <code>h j s</code> и узнай мои команды с помощью команды <code>h j h</code>!")

@router.message(F.text.lower() == ('h j h'))
@router.message(Command("help"))
async def cmd_help(message: Message):
	await message.reply("""<b>Справка Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji></b>\n\n"""
						"""<code>h j g</code> - генерация текста\n"""
						"""<code>h j g l</code> - генерация длинного текста\n"""
						"""<code>h j g 100</code> - генерация текста размером около 100 символов\n"""
						"""<code>h j g привет</code> - генерация текста с началом "привет"\n"""
						"""<code>h j p</code> - генерация опросов\n"""
						"""<code>h j t</code> - генерация Топор 1+ сообщения\n"""
						"""<code>h j d</code> - генерация демотиватора\n"""
						"""<code>h j m</code> - генрация мема из случайного шаблона\n"""
						"""<code>h j s</code> - настройки бота\n"""
						"""<code>h j h</code> - эта справка""")

@router.message(F.text.lower().startswith('h j g'))
async def force_generate(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[0] == 1:
		if message.reply_to_message:
			if message.reply_to_message.caption:
				gen_message = await generate_sentence(chat_id=message.chat.id, start=message.reply_to_message.caption)
			elif message.reply_to_message.text:
				gen_message = await generate_sentence(chat_id=message.chat.id, start=message.reply_to_message.text)
			else:
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Бот не смог найти текст чтобы его продолжить...")
				return
		elif message.text.lower() != "h j g":
			arg = message.text[6:]
			if arg.isdigit() and int(arg) > 10:
				await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
				logger.warning(arg)
				gen_message = await generate_sentence(chat_id=message.chat.id, chars_count=int(arg))
			elif arg == 'l':
				await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
				gen_message = await generate_sentence(chat_id=message.chat.id, size=3)
			else:
				await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
				gen_message = await generate_sentence(chat_id=message.chat.id, start=arg.lower())
				if gen_message is None:
					await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji>  Бот не смог найти ничего подходящего с таким началом")
					return
		else:
			gen_message = await generate_sentence(chat_id=message.chat.id)
		if gen_message is None:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> База слов слишком мала для генерации")
		else:
			await message.reply(gen_message)
	else:
		return

@router.message(F.text.lower() == 'h j t')
async def generate_topor_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[1] == 1:
		try:
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
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу придумать из-за того, что мне нельзя отправлять изображе")
		except:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не придума")
	else:
		return

# TODO: обрабатывать текст при ответе
@router.message(F.text.lower() == 'h j d')
async def generate_demotivator_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[2] == 1:
		try:
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
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу надемотивировать из-за того, что мне нельзя отправлять изображения")
		except:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не смог надемотивировать")
	else:
		return

@router.message(F.text.lower() == 'h j m')
async def generate_meme_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[3] == 1:
		try:
			await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			meme = await generate_meme(message.chat.id)
			await message.reply_photo(
				photo=BufferedInputFile(meme, filename="meme.jpg"))
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу намемить из-за того, что мне нельзя отправлять изображения")
		except:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не смог намемить")
	else:
		return

@router.message(F.text.lower() == 'h j p')
async def generate_poll_message(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[4] == 1:
		try:
			await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
			type_poll = random.choice(["quiz", "regular"])
			count_options = random.randint(3,6)
			if type_poll == "quiz":
				await message.reply_poll(
					question=await generate_sentence(message.chat.id),
					options=await generate_sentences(message.chat.id, count_options),
					type=type_poll,
					explanation=await generate_sentence(message.chat.id),
					correct_option_id=random.randint(0, count_options-1),
					is_anonymous=random.choice([True, False]),
				)
			else:
				await message.reply_poll(
					question=await generate_sentence(message.chat.id),
					options=await generate_sentences(message.chat.id, count_options),
					type=type_poll,
					is_anonymous=random.choice([True, False]),
				)
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу намемить из-за того, что мне нельзя отправлять опросы")
			else:
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не смог придумать опрос")
		except:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не смог придумать опрос")
	else:
		return

@router.message(F.text.lower() == 'h j s')
async def cmd_settings(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False and (await get_commands_settings(message.chat.id))[4] == 1:
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
	else:
		return