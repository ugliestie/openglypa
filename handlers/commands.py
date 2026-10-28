import logging
import random
from functools import lru_cache
from pathlib import Path

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message, ReactionTypeEmoji
from aiogram.utils.chat_member import ADMINS

from database.requests import get_commands_settings
from keyboards.settings import kb_settings_main
from keyboards.start import kb_add
from utils.chat_data import NoSamples, RandomImageNotFound
from utils.text import FailedByTries, PossibleStartsNotFound

logger = logging.getLogger(__name__)

router = Router()

class NoBot(BaseException):
	pass

class CantDownloadFileException(Exception):
	pass

async def is_message_admin(message: Message, user_id : int) -> bool:
	if message.bot is None:
		raise NoBot
	member = await message.bot.get_chat_member(message.chat.id, user_id)
	return isinstance(member, ADMINS)

@router.message(Command("start"))
async def cmd_start(message: Message):
	if message.bot:
		if message.chat.type == 'private':
			await message.reply(text="Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!",
								reply_markup=kb_add((await message.bot.get_me()).username))
		elif (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is None or message.from_user.is_bot is False):
			await message.reply("Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nНастрой меня с помощью команды <code>h j s</code> и узнай мои команды с помощью команды <code>h j h</code>!")

@lru_cache
def get_commit():
	try:
		head_name = Path("./.git", 'HEAD').read_text().split('\n')[0].split(' ')[-1]
		head_ref = Path("./.git",head_name)
		return head_ref.read_text().replace('\n','')
	except FileNotFoundError:
		return 'Бот выполняется не из репозитория'

@router.message(F.text.lower() == ('h j h'))
@router.message(Command("help"))
async def cmd_help(message: Message):
	await message.reply("""<b>Справка Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji></b>\n\n"""
						"""<code>h j g</code> - генерация текста\n"""
						"""<code>h j g l</code> - генерация длинного текста\n"""
						"""<code>h j g 100</code> - генерация текста размером около 100 символов\n"""
						"""<code>h j g привет</code> - генерация текста с началом "привет"\n"""
						"""<code>h j hm я кружка?</code> - генерация ответа на да/нет вопрос\n"""
						"""<code>h j p</code> - генерация опросов\n"""
						"""<code>h j t</code> - генерация Топор 1+ сообщения\n"""
						"""<code>h j d</code> - генерация демотиватора\n"""
						"""<code>h j m</code> - генерация мема из случайного шаблона\n"""
						"""<code>h j s</code> - настройки бота\n"""
						"""<code>h j del</code> - удалить изображение/стикер из базы данных бота\n"""
						"""<code>h j stats</code> - статистика базы данных чата\n"""
						"""<code>h j h</code> - эта справка\n\n"""
	  					+ get_commit())

@router.message(F.text.lower().startswith('h j g'))
async def force_generate(message: Message):
	from utils.text import generate_sentence
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') \
		and (message.from_user is None or message.from_user.is_bot is False) \
		and (await get_commands_settings(message.chat.id))[0] == 1:
			
		chars_count = None
		start = None
		size = 0

		if message.reply_to_message:
			start = (message.reply_to_message.caption or message.reply_to_message.text)
			if start is None:
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу найти текст, чтобы его продолжить...")
				return
		elif message.text:
			if message.text.lower() != "h j g":
				arg = message.text[6:]
				if arg.isdigit() and int(arg) > 10:
					chars_count = int(arg)
				elif arg == 'l':
					size = 4
				else:
					start = arg.lower()
		else:
			size = 2
		
		await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
		try:
			await message.reply(await generate_sentence(chat_id=message.chat.id, size=size, chars_count=chars_count, start=start))
		except NoSamples as e:
			logger.warning(str(e))
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!")
			return
		except PossibleStartsNotFound:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти ничего подходящего с таким началом")
			return
		except FailedByTries:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз")
			return
		except Exception:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не придума")
	else:
		return

@router.message(F.text.lower() == 'h j t')
async def generate_topor_message(message: Message):
	from utils.chat_data import random_image
	from utils.topor import generate_topor
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') \
		and (message.from_user is None or message.from_user.is_bot is False) \
		and (await get_commands_settings(message.chat.id))[1] == 1:
		try:
			text = None
   
			if message.reply_to_message and message.reply_to_message.photo and message.reply_to_message.caption:
					image = await message.bot.download(file=message.reply_to_message.photo[-1].file_id)
					text = message.reply_to_message.caption.capitalize()
			else:
				image = await random_image(message.chat.id, message.bot)
	 
			if image == None:
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу найти изображение, чтобы сгенерировать Топо")
			else:
				await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
				topor = await generate_topor(message.chat.id, image=image, text=text)
				await message.reply_photo(
					photo=BufferedInputFile(topor[1], filename="topor.jpg"),
					caption=topor[0])
	
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу придумать из-за того, что мне нельзя отправлять изображе")
		except NoSamples as e:
			logger.warning(str(e))
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!")
			return
		except RandomImageNotFound:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз")
			return
		except Exception as e:
			logger.error(f"Ошибка при вызове h j t: {e!s}")
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не придума")
	else:
		return

@router.message(F.text.lower() == 'h j d')
async def generate_demotivator_message(message: Message):
	from utils.chat_data import random_image
	from utils.images import generate_demotivator
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is None or message.from_user.is_bot is False) and (await get_commands_settings(message.chat.id))[2] == 1:
		try:
			await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			if message.reply_to_message:
				if message.reply_to_message.photo:
					image = await message.bot.download(file=message.reply_to_message.photo[-1].file_id)
					if image is None:
						raise Exception('Изображение не найдено')
					demotivator = await generate_demotivator(message.chat.id, image)
					await message.reply_photo(
						photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
				else:
					demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id, message.bot))
					await message.reply_photo(
						photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
			else:
				demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id, message.bot))
				await message.reply_photo(
					photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу надемотивировать из-за того, что мне нельзя отправлять изображения")
		except NoSamples:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!")
			return
		except RandomImageNotFound:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз")
			return
		except FailedByTries:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз")
			return
		except Exception as e:
			logger.error(f"Ошибка при вызове h j d: {e!s}")
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и ничего не вышло надемотивировать")
	else:
		return

@router.message(F.text.lower() == 'h j m')
async def generate_meme_message(message: Message):
	from utils.images import generate_meme
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is None or message.from_user.is_bot is False) and (await get_commands_settings(message.chat.id))[3] == 1:
		try:
			await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			meme = await generate_meme(message.chat.id, message.bot)
			await message.reply_photo(
				photo=BufferedInputFile(meme, filename="meme.jpg"))
		except TelegramBadRequest as e:
			if "not enough rights" in str(e):
				await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу намемить из-за того, что мне нельзя отправлять изображения")
		except NoSamples:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!")
			return
		except RandomImageNotFound:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз")
			return
		except FailedByTries:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз")
			return
		except Exception as e:
			logger.error(f"Ошибка при вызове h j m: {e!s}")
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и ничего не вышло намемить")
	else:
		return

@router.message(F.text.lower() == 'h j p')
async def generate_poll_message(message: Message):
	from utils.text import generate_sentence, generate_sentences
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is None or message.from_user.is_bot is False) and (await get_commands_settings(message.chat.id))[4] == 1:
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
		except NoSamples:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!")
			return
		except FailedByTries:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз")
			return
		except Exception as e:
			logger.error(f"Ошибка при вызове h j p: {e!s}")
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не смог придумать опрос")
	else:
		return

@router.message(F.text.lower() == 'h j s')
async def cmd_settings(message: Message):
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is not None and message.from_user.is_bot is False):
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

# TODO: добавить банлист для стикеров
@router.message(F.text.lower() == 'h j del')
async def cmd_delete(message: Message):
	from utils.chat_data import delete_image, delete_sticker
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is not None and message.from_user.is_bot is False):
		if await is_message_admin(message, message.from_user.id):
			if message.photo:
				await delete_image(message.photo[-1].file_id, message.chat.id)
				await message.reply(
					"Изображение удалено из базы данных бота"
				)
			elif message.sticker:
				await delete_sticker(message.sticker.file_id, message.chat.id)
				await message.reply(
					"Стикер удалён из базы данных бота"
				)
		else:
			await message.reply(
				"У вас недостаточно прав в чате, чтобы вызывать эту команду"
			)
	else:
		return

@router.message(F.text.lower() == 'h j stats')
async def cmd_stats(message: Message):
	from utils.chat_data import read_images, read_stickers, read_words
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') and (message.from_user is None or message.from_user.is_bot is False):
		chat_id = message.chat.id
  
		try:
			samples = len(await read_words(chat_id))
		except FileNotFoundError:
			samples = 0
		except NoSamples:
			samples = 0
   
		try:
			images = len(await read_images(chat_id))
		except FileNotFoundError:
			images = 0
		except NoSamples:
			samples = 0
   
		try:
			stickers = len(await read_stickers(chat_id))
		except FileNotFoundError:
			stickers = 0
		except NoSamples:
			samples = 0
   
		await message.reply("""<b>Статистика Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji></b>\n\n"""
						f"""Количество сообщений в базе данных: {samples}\n"""
						f"""Количество изображений в базе данных: {images}\n"""
						f"""Количество стикеров в базе данных: {stickers}""")
	else:
		return
	
@router.message(F.text.lower().contains('h j hm'))
async def generate_reply(message: Message):
	if message.bot and (message.chat.type == 'group' or message.chat.type == 'supergroup') \
	and (message.from_user is None or message.from_user.is_bot is False) \
	and (await get_commands_settings(message.chat.id))[5] == 1:
		yn = random.randint(1, 10)
		if yn == 1:
			await message.reply('Неее...')
		if yn == 2:
			await message.reply('Возможно в будущем! 🤔')
		if yn == 3:
			await message.reply('Да, у меня есть уверенность 🙂')
		if yn == 4:
			await message.reply('Это странный вопрос. Я не хочу отвечать')
		if yn == 5:
			await message.reply('Это имеет шестидесятисемипроцентный шанс. не скажу, в какую сторону')
		if yn == 6:
			await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не могу сложить 2+2") 
		if yn == 7:
			await message.reply('Спокойным волнам на реке понравилось. Всё сбудется')
		if yn == 8:
			set_reactions = ["🤔", "🤯", "😢", "🎉", "🤩", "🕊", "🤷‍♂", "🤷", "🤷‍♀", "😡"]
			react = ReactionTypeEmoji(emoji=random.choice(set_reactions))
			await message.react([react])
		if yn == 9:
			await message.answer_sticker(sticker="CAACAgIAAxkBAAEpAsFp--224lYB9gthIp4I36sDAAHjH5cAAiWPAAKHTklKtLyM8h5_QgE7BA")
		if yn == 10:
			await message.reply('да давай ура даааааа')
	else:
		return