from utils.db import read_words
from PIL import Image, ImageOps
import random
from io import BytesIO

async def generate_topor(chat_id, image, text=None):
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
		return str(random.choice(emojis) + ' ' + random.choice(text_model)[:random.randrange(2,8)].capitalize()), byte_io.read()
	else:
		return str(random.choice(emojis) + ' ' + text[:random.randrange(2,8)].capitalize()), byte_io.read()