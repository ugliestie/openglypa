from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, ContentType as CT, ReactionTypeEmoji
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest

from aiogram_media_group import media_group_handler

import os
import re
import random

router = Router()

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

@router.message(StateFilter(None), F.media_group_id)
@media_group_handler
async def handle_albums(group: list[Message]):
	from utils.chat_data import write_words, write_images
	if (group[0].chat.type == 'group' or group[0].chat.type == 'supergroup') and group[0].from_user.is_bot is False:
		for msg in group:
			if msg.photo:
				await write_images(group[0].chat.id, msg.photo[-1].file_id)
			if msg.caption is not None and not re.findall(link_pattern, msg.caption) and not re.findall(commands_pattern, msg.caption):
				await write_words(group[0].caption, group[0].chat.id)
	else:
		return
	
@router.message(StateFilter(None))
async def handle_single(message: Message):
	from utils.sqlite import get_automatic_generations
	from utils.images import generate_meme, generate_demotivator
	from utils.topor import generate_topor
	from utils.text import generate_sentence, generate_sentences
	from utils.chat_data import read_stickers, write_words, write_images, write_stickers, delete_sticker
	from main import random_image, logger
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		if not os.path.exists("chats"):
			os.mkdir(f"chats")
		if not os.path.exists(f"chats/{message.chat.id}"):
			os.mkdir(f"chats/{message.chat.id}")
		
		generation = await get_automatic_generations(message.chat.id)
		if generation[0] != 100 and chance_hit(100 - generation[0]):
			try:
				set_generations = [i for i in range(1, 8) if generation[i] == 1]
				choice = random.choice(set_generations)
				if choice == 1:
					gen_message = await generate_sentence(message.chat.id)
					await message.answer(gen_message)
				elif choice == 2:
					try:
						topor = await generate_topor(message.chat.id, await random_image(message.chat.id))
						await message.answer_photo(
							photo=BufferedInputFile(topor[1], filename="topor.jpg"),
							caption=topor[0])
					except Exception as e:
						logger.warning(f"Ошибка при автоматической генерации Топор 1+: {str(e)}")
				elif choice == 3:
					try:
						demotivator = await generate_demotivator(message.chat.id, await random_image(message.chat.id))
						await message.answer_photo(
							photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
					except Exception as e:
						logger.warning(f"Ошибка при автоматической генерации демотиватора: {str(e)}")
				elif choice == 4:
					try:
						meme = await generate_meme(message.chat.id)
						await message.answer_photo(
							photo=BufferedInputFile(meme, filename="meme.jpg"))
					except Exception as e:
						logger.warning(f"Ошибка при автоматической генерации мема: {str(e)}")
				elif choice == 5:
					try:
						await message.answer_poll(
						question=await generate_sentence(message.chat.id),
						options=await generate_sentences(message.chat.id, random.randint(3,6)),
						explanation=await generate_sentence(message.chat.id),
						is_anonymous=False,
						)
					except Exception as e:
						logger.warning(f"Ошибка при автоматической генерации опроса: {str(e)}")
				elif choice == 6:
					set_reactions = ["❤", "👍", "👎", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳", "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨", "😐", "🍓", "🍾", "💋", "🖕", "😈", "😴", "😭", "🤓", "👻", "👨‍💻", "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅", "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘", "💊", "🙊", "😎", "👾", "🤷‍♂", "🤷", "🤷‍♀", "😡"]
					react = ReactionTypeEmoji(emoji=random.choice(set_reactions))
					await message.react([react])
				elif choice == 7:
					try:
						sticker = random.choice(await read_stickers(message.chat.id))
						await message.answer_sticker(
							sticker=sticker
						)
					except TelegramBadRequest as e:
						if "not enough rights" in str(e):
							await message.reply("<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> <b>Я не могу прислать стикер из-за того, что мне нельзя их отправлять.</b><br><br>Я больше не буду пытаться. Чтобы исправить это, разрешите боту присылать стикеры и в настройках бота включите их автоматическое присылание.")
						else:
							await delete_sticker(sticker, message.chat.id)
			except:
				pass
		
		if message.text is not None and not re.findall(link_pattern, message.text) and not re.findall(commands_pattern, message.text):
			await write_words(message.text, message.chat.id)
		elif message.photo:
			await write_images(message.chat.id, message.photo[-1].file_id)
			if message.caption == "h j d":
				await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
				demotivator = await generate_demotivator(message.chat.id, await message.bot.download(file=message.photo[-1].file_id))
				await message.reply_photo(
					photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
			elif message.caption == "h j t":
				await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
				topor = await generate_topor(message.chat.id, await message.bot.download(file=message.photo[-1].file_id))
				await message.reply_photo(
					photo=BufferedInputFile(topor[1], filename="topor.jpg"),
					caption=topor[0])
		
		if message.caption is not None and not re.findall(link_pattern, message.caption) and not re.findall(commands_pattern, message.caption):
			await write_words(message.caption, message.chat.id)
		elif message.sticker is not None:
			await write_stickers(message.chat.id, message.sticker.file_id)
	else:
		return