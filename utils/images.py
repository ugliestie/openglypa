from utils.text import generate_sentence, generate_sentences
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import random
import textwrap
from main import random_image

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

async def generate_meme(chat_id):
	select = random.randint(9, 9)

	if select == 1:
		img = Image.open("./utils/resources/templates/1.jpg")
		text = await generate_sentence(chat_id=chat_id)

		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 25, encoding='UTF-8')
		image_width, image_height = img.size
		y_text = 750
		lines = textwrap.wrap(text, width=11)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)-35, y_text), 
					line, fill='white', font=font,
       				stroke_width=2, stroke_fill='black')
			y_text += line_height
		
		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()
	
	if select == 2:
		img = Image.open("./utils/resources/templates/2.jpg")
		img_paste = Image.open(await random_image(chat_id=chat_id)).convert("RGBA").resize((639, 348))

		img.paste(img_paste)
		
		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 3:
		img = Image.open("./utils/resources/templates/3.jpg")
		text = await generate_sentences(chat_id=chat_id, count=3)

		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 35, encoding='UTF-8')
		image_width = 595

		y_text = 205
		lines = textwrap.wrap(text[0], width=33)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2), y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		y_text = 430
		lines = textwrap.wrap(text[1], width=20)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)-125, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		y_text = 650
		lines = textwrap.wrap(text[2], width=28)
		if len(lines) != 1: y_text = 685
		else: y_text = 713
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2), y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()
	
	if select == 4:
		img = Image.open("./utils/resources/templates/4.jpg")
		img_paste = Image.open(await random_image(chat_id=chat_id)).convert("RGBA").resize((1000, 538))

		img.paste(img_paste, (0, 460))

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 5:
		img = Image.open("./utils/resources/templates/5.jpg")
		img_paste = Image.open(await random_image(chat_id=chat_id)).convert("RGBA").resize((426, 299))

		img.paste(img_paste, (520, 105))

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 6:
		img = Image.open("./utils/resources/templates/6.jpg")
	
		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 15, encoding='UTF-8')
		image_width, image_height = img.size
		text = await generate_sentence(chat_id=chat_id)
		
		y_text = 340
		lines = textwrap.wrap(text, width=20)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)+5, y_text), 
					line, fill='black', font=font)
			y_text += line_height

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 7:
		img = Image.open("./utils/resources/templates/7.jpg")
	
		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 35, encoding='UTF-8')
		image_width, image_height = img.size
		text = await generate_sentence(chat_id=chat_id)
		
		y_text = 10
		lines = textwrap.wrap(text, width=20)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2), y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 8:
		img = Image.open("./utils/resources/templates/8.jpg")
	
		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 32, encoding='UTF-8')
		image_width, image_height = img.size
		text = await generate_sentences(chat_id=chat_id, count=3)
		
		y_text = 305
		lines = textwrap.wrap(text[0], width=13)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)-190, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		y_text = 170
		lines = textwrap.wrap(text[1], width=19)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)+90, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		y_text = 520
		lines = textwrap.wrap(text[2], width=13)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)+190, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()

	if select == 9:
		img = Image.open("./utils/resources/templates/9.jpg")
	
		drawer = ImageDraw.Draw(img)
		font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 20, encoding='UTF-8')
		image_width, image_height = img.size
		text = await generate_sentences(chat_id=chat_id, count=2)
		
		y_text = 32
		lines = textwrap.wrap(text[0], width=10)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)-165, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		y_text = 49
		lines = textwrap.wrap(text[1], width=10)
		for line in lines:
			line_width = font.getbbox(line)[2]
			line_height = font.getbbox(line)[3]
			drawer.text((((image_width - line_width) / 2)+190, y_text), 
					line, fill='white', font=font,
					stroke_width=2, stroke_fill='black')
			y_text += line_height

		byte_io = BytesIO()
		byte_io.name = 'image.jpg'
		
		img.save(byte_io, 'JPEG')
		byte_io.seek(0)

		return byte_io.read()