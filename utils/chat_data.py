from aiofile import AIOFile
from pyutil import filereplace
import os

# Запись слов и выражений в файл, созданный под чат
async def write_words(text, chat_id):
	async with AIOFile(f"chats/{chat_id}/text.txt", "a", encoding="utf-8") as f:
		text = text.replace("\n", ". ").replace("\n\n", ". ")
		await f.write(text + ",")

# Запись file_id изображений в файл, созданный под чат (сами изображения обрабатываются только при использовании команд и не используют лишнее место на диске)
async def write_images(*args):
	chat_id, file_id = args
	if not os.path.exists(f"chats/{chat_id}"):
		os.mkdir(f"chats/{chat_id}")
	async with AIOFile(f"chats/{chat_id}/images.txt", "a", encoding="utf-8") as f:
		await f.write(file_id + ",")

# Получение слов и выражений из файла, созданного под чат
async def read_words(chat_id, topor=False):
	# Получение для Топора 1+ именно такое, чтобы гарантировано не получить пустые сообщения
	if topor:
		async with AIOFile(f"chats/{chat_id}/text.txt", encoding="utf-8") as f:
			text = await f.read()
			return [sample.strip() for sample in text.split(",") if len(sample)>3]
	# Получение модели слов для работы цепи Маркова
	else:
		async with AIOFile(f"chats/{chat_id}/text.txt", encoding="utf-8") as f:
			text = await f.read()
			return [sample.strip() for sample in text.split(",")]

# Получение изображений из файла, созданного под чат	
async def read_images(chat_id):
	async with AIOFile(f"chats/{chat_id}/images.txt", encoding="utf-8") as f:
		images = await f.read()
		return [sample for sample in images.split(",") if sample != ""]

# Удаление из файла изображения, к которому невозможно получить доступ
async def delete_image(file_id, chat_id):
	filereplace(f"chats/{chat_id}/images.txt",f"{file_id},","")