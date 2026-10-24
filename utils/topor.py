import random
from io import BytesIO

from PIL import Image, ImageOps

from utils.chat_data import read_words


async def generate_topor(chat_id: int, image: bytes, text=None) -> tuple[str, bytes]:
	"""Генерация сообщения в стиле канала Топор 1+

	Args:
		chat_id (int): id группового чата
		image (bytes): изображение
		text (str, optional): текст, который необходимо обрезать, по умолчанию None, тогда берётся случайное выражение из базы данных чата

	Returns:
		tuple[str, bytes]: описание и обрезаная случайным образом картинка
	"""
	emojis = ['📣', '‼️', '❗️', '❓', '⚡️']

	img = Image.open(image)
	w, h = img.size
	border = (random.randint(0, int(w*0.25)), random.randint(0, int(h*0.25)), random.randint(0, int(w*0.25)), random.randint(0, int(h*0.25)))
	img = ImageOps.crop(img, border)
	
	byte_io = BytesIO()
	byte_io.name = 'image.jpg'

	img.save(byte_io, 'JPEG')
	byte_io.seek(0)

	if text is None:
		text_model = await read_words(chat_id=chat_id)
		text = random.choice(text_model)
	
	if len(text.split(' ', 1)) != 1:
		return str(random.choice(emojis) + ' ' + text.split(' ', 1)[0].capitalize() + ' ' + text.split(' ', 1)[1][:random.randrange(2,8)]), byte_io.read()
	else:
		return str(random.choice(emojis) + ' ' + text.capitalize()), byte_io.read()