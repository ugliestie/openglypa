import os
import random
import string
from typing import BinaryIO

import aiofiles
from aiogram import Bot
from pyutil import fileoverwrite, filereplace


class NoSamples(Exception):
	def __init__(self, type: str):
		self.type = type
		
	def __str__(self):
		if self.type == "words":
			return "Нет текстовых выражений в файле чата"
		elif self.type == "images":
			return "Нет file_id изображений в файле чата"
		elif self.type == "stickers":
			return "Нет file_id стикеров в файле чата"

class RandomImageNotFound(BaseException):
	pass

# Корпус данных чата устроен на основе логики NeuronBot
# https://github.com/kesha1225/NeuronBot

async def write_words(text: str, chat_id: int) -> None:
	"""Запись слов и выражений в файл, созданный под чат

	Args:
		text (str): текст сообщения
		chat_id (int): id группового чата
	"""
	if not os.path.exists(f"chats/{chat_id}"):
		os.mkdir(f"chats/{chat_id}")
	if not await check_ban_words(text, chat_id):
		async with aiofiles.open(f"chats/{chat_id}/text.txt", "a", encoding="utf-8") as f:
			while '  ' in text.strip():
				text = text.replace("  ", " ")
			text = " ".join([word for word in text.split() if word not in string.punctuation])
			if len(text.split()) > 2:
				text = text.casefold()
				text = text.replace("\n", ". ").replace("\n\n", ". ")
				await f.write(text + ",")
	else:
		pass
  
async def write_ban_words(text: str, chat_id: int) -> None:
	"""Добавление слов и выражений в файл, созданный под чат, сообщения с которыми не будут добавляться в базу данных чата

	Args:
		text (str): слово или выражение
		chat_id (int): id группового чата
	"""
	update_ban = [sample for sample in text.lower().split(",") if sample != ""]
	if not os.path.exists(f"chats/{chat_id}"):
		os.mkdir(f"chats/{chat_id}")
	if os.path.isfile(f"chats/{chat_id}/ban.txt"):
		async with aiofiles.open(f"chats/{chat_id}/ban.txt", "w+", encoding="utf-8") as f:
			ban_words = str(await f.read())
			ban_words_read = [sample.strip() for sample in ban_words.split(",") if sample != ""]
			for string in update_ban:
				if string in ban_words_read:
					update_ban.remove(string)
				else:
					await f.write(string + ",")
	else:
		async with aiofiles.open(f"chats/{chat_id}/ban.txt", "a", encoding="utf-8") as f:
			for string in update_ban:
				await f.write(string + ",")
	async with aiofiles.open(f"chats/{chat_id}/text.txt", encoding="utf-8") as f:
		text_data = str(await f.read())
		chat_words = [sample.strip() for sample in text_data.split(",")]
		for string in chat_words:
			if await check_ban_words(string.lower(), chat_id):
				chat_words.remove(string)
		fileoverwrite(f"chats/{chat_id}/text.txt", ','.join(chat_words))

async def check_ban_words(text, chat_id) -> bool:
	"""Проверка текста на наличие запретных слов и выражений, если они добавлены для этого чата

	Args:
		text (str): текст сообщения
		chat_id (int): id группового чата

	Returns:
		bool: True, если сообщение содержит запретное выражение, False, если содержит
	"""
	if os.path.isfile(f"chats/{chat_id}/ban.txt"):
		async with aiofiles.open(f"chats/{chat_id}/ban.txt", encoding="utf-8") as f:
			ban_words = str(await f.read())
			ban_words_read = [sample.strip() for sample in ban_words.split(",") if sample != ""]
		if not ban_words_read:
			return False
		for string in ban_words_read:
			if string in text.lower():
				return True
	return False

async def write_images(chat_id: int, file_id: str) -> None:
	"""Запись file_id изображений в файл, созданный под чат (сами изображения обрабатываются только при использовании команд и не используют лишнее место на диске)

	Args:
		chat_id (int): id группового чата
		file_id (str): id файла, лежащего на сервере Telegram
	"""
	if not os.path.exists(f"chats/{chat_id}"):
		os.mkdir(f"chats/{chat_id}")
	async with aiofiles.open(f"chats/{chat_id}/images.txt", "a", encoding="utf-8") as f:
		await f.write(file_id + ",")

async def write_stickers(chat_id: int, file_id: str):
	"""Запись file_id стикеров в файл, созданный под чат

	Args:
		chat_id (int): id группового чата
		file_id (str): id файла, лежащего на сервере Telegram
	"""
	if not os.path.exists(f"chats/{chat_id}"):
		os.mkdir(f"chats/{chat_id}")
	async with aiofiles.open(f"chats/{chat_id}/stickers.txt", "a", encoding="utf-8") as f:
		await f.write(file_id + ",")

async def read_words(chat_id: int) -> list[str]:
	"""Получение слов и выражений из файла, созданного под чат

	Args:
		chat_id (int): id группового чата

	Returns:
		list[str]: лист выражений
	"""
	async with aiofiles.open(f"chats/{chat_id}/text.txt", encoding="utf-8") as f:
		text = str(await f.read())
		samples = [sample.strip() for sample in text.split(",") if sample != '']
		if not samples:
			raise NoSamples('words')
		else:
			return samples
	
async def read_images(chat_id) -> list[str]:
	"""Получение изображений из файла, созданного под чат

	Args:
		chat_id (_type_): id группового чата

	Returns:
		list[str]: лист id файлов, лежащих на сервере Telegram
	"""
	async with aiofiles.open(f"chats/{chat_id}/images.txt", encoding="utf-8") as f:
		images = str(await f.read())
		samples = [sample for sample in images.split(",") if sample != ""]
		if not samples:
			raise NoSamples('images')
		else:
			return samples

async def random_image(chat_id: int, bot: Bot) -> BinaryIO:
	"""Скачивание случайного изображения в BinaryIO

	Args:
		chat_id (int): id группового чата

	Returns:
		bytes | None: изображение, или None, если его не получилось скачать
	"""
	photos_model = await read_images(chat_id)
	for _ in range(3):
		file_id = random.choice(photos_model)
		try:
			image = await bot.download(file=file_id)
			if image is None:
				raise RandomImageNotFound
			else:
				return image
		except RandomImageNotFound:
			await delete_image(file_id, chat_id)
	raise RandomImageNotFound
	
async def read_stickers(chat_id) -> list[str]:
	"""Получение стикеров из файла, созданного под чат

	Args:
		chat_id (_type_): id группового чата

	Returns:
		list[str]: лист id файлов, лежащих на сервере Telegram
	"""
	async with aiofiles.open(f"chats/{chat_id}/stickers.txt", encoding="utf-8") as f:
		stickers = str(await f.read())
		samples = [sample for sample in stickers.split(",") if sample != ""]
		if not samples:
			raise NoSamples('stickers')
		else:
			return samples
	
async def delete_image(file_id, chat_id) -> None:
	"""Удаление из файла изображения, к которому невозможно получить доступ

	Args:
		file_id (_type_): id файла, лежащего на сервере Telegram
		chat_id (_type_): id группового чата
	"""
	filereplace(f"chats/{chat_id}/images.txt",f"{file_id},","")

async def delete_sticker(file_id, chat_id) -> None:
	"""Удаление из файла стикеров, к которому невозможно получить доступ

	Args:
		file_id (_type_): id файла, лежащего на сервере Telegram
		chat_id (_type_): id группового чата
	"""
	filereplace(f"chats/{chat_id}/stickers.txt",f"{file_id},","")