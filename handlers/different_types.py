from aiogram import Router, F
from aiogram.types import Message, BufferedInputFile, ContentType as CT
from aiogram.filters import StateFilter

from aiogram_media_group import media_group_handler

import os
import re
import random

from utils.chat_data import *
from utils.sqlite import *
from utils.text import *
from utils.topor import *
from utils.images import *

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

@router.message(StateFilter(None), F.text)
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
					topor = await generate_topor(message.chat.id, await random_image(message, message.chat.id))
					await message.answer_photo(
						photo=BufferedInputFile(topor[1], filename="topor.jpg"),
						caption=topor[0])
				elif choice == 3:
					demotivator = await generate_demotivator(message.chat.id, await random_image(message, message.chat.id))
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

@router.message(F.media_group_id, F.content_type.in_([CT.PHOTO, CT.VIDEO, CT.AUDIO, CT.DOCUMENT]))
@media_group_handler
async def handle_albums(group: list[Message]):
	if (group[0].chat.type == 'group' or group[0].chat.type == 'supergroup') and group[0].from_user.is_bot is False:
		for msg in group:
			if msg.photo:
				await write_images(group[0].chat.id, msg.photo[-1].file_id)
			if msg.caption is not None:
				await write_words(group[0].caption, group[0].chat.id)
	else:
		return
	
@router.message(F.content_type.in_([CT.PHOTO, CT.VIDEO, CT.AUDIO, CT.DOCUMENT]))
async def handle_single_media(message: Message):
	if (message.chat.type == 'group' or message.chat.type == 'supergroup') and message.from_user.is_bot is False:
		await write_images(message.chat.id, message.photo[-1].file_id)
		if message.caption == "h j d":
			await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			demotivator = await generate_demotivator(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.reply_photo(
				photo=BufferedInputFile(demotivator, filename="demotivator.jpg"))
		elif message.caption == "h j t":
			await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
			topor = await generate_topor(message.chat.id, await bot.download(file=message.photo[-1].file_id))
			await message.reply_photo(
				photo=BufferedInputFile(topor[1], filename="topor.jpg"),
				caption=topor[0])
		elif message.caption is not None:
			await write_words(message.caption, message.chat.id)
	else:
		return