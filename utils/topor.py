from utils.chat_data import read_words
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
		text = random.choice(text_model)
	
	if len(text.split(' ', 1)) != 1:
		return str(random.choice(emojis) + ' ' + text.split(' ', 1)[0].capitalize() + text.split(' ', 1)[1][:random.randrange(2,8)]), byte_io.read()
	else:
		return str(random.choice(emojis) + ' ' + text.capitalize()), byte_io.read()