from utils.text import generate_sentences
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO


async def generate_demotivator(chat_id, image):
	img = Image.new('RGB', (1280, 1124), color='#000000')
	img_border = Image.new('RGB', (1060, 720), color='#000000')
	border = ImageOps.expand(img_border, border=2, fill='#ffffff')

	user_img = Image.open(image).convert("RGBA").resize((1050, 710))

	img.paste(border, (111, 96))
	img.paste(user_img, (118, 103))

	fontsize = 1

	drawer = ImageDraw.Draw(img)
	font = ImageFont.truetype("./utils/resources/fonts/timesnewroman.ttf", fontsize, encoding='UTF-8')
	
	text = await generate_sentences(chat_id=chat_id, count=2)

	if len(text[0]) <= 25:
		img_fraction = 0.40
	if len(text[0]) > 25:
		img_fraction = 0.75

	while font.getbbox(text[0])[2] < img_fraction * img.size[0]:
		fontsize += 1
		font = ImageFont.truetype("./utils/resources/fonts/timesnewroman.ttf", fontsize, encoding='UTF-8')
	fontsize -= 1
	font = ImageFont.truetype("./utils/resources/fonts/timesnewroman.ttf", fontsize, encoding='UTF-8')

	size_1 = drawer.textlength(f'{text[0]}', font=font)
	drawer.text(((1280 - size_1) / 2, 880), f'{text[0]}', fill=(240, 230, 210), font=font)

	size_2 = drawer.textlength(f'{text[1]}', font=font)
	drawer.text(((1280 - size_2) / 2, 1010), f'{text[1]}', fill=(240, 230, 210), font=font)

	byte_io = BytesIO()
	byte_io.name = 'image.jpg'
	
	img.save(byte_io, 'JPEG')
	byte_io.seek(0)

	return byte_io.read()