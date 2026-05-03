# Как создавать мемы для данного бота?

В [utils/images.py](utils/images.py) содержится логика создания мемов, которыми пользуется бот, в utils/resources/templates - шаблоны, используемые в нём, а в utils/resources/fonts - шрифты.

## Обязательное условие!

```python
async def generate_meme(chat_id):
	select = random.randint(1, 22)
```

`select` отвечает за выбор случаного мема (в примере от 1 до 22 мема). При добавлении не забудьте изменить это, чтобы ваш мем включился!

## Мемы со вставкой случайной картинки

```python
if select == 17:
	img = Image.open("./utils/resources/templates/17.jpg")
	img_paste = Image.open(await random_image(chat_id=chat_id)).convert("RGBA").resize((355, 355))

	img.paste(img_paste, (-81, 201))

	byte_io = BytesIO()
	byte_io.name = 'image.jpg'

	img.save(byte_io, 'JPEG')
	byte_io.seek(0)

	return byte_io.read()
```

Здесь представлен пример мема со вставкой картинки, далее я его разберу на части.

В `Image.open("./utils/resources/templates/17.jpg")` мы открываем файл шаблона

Дальше открывается случайная картинка из чата (`await random_image(chat_id=chat_id)`) и изменяется по ширине и длине как вам нужно (`resize((355, 355))`)

Дальше с помощью `img.paste` происходит вставка картинки на шаблон. `(-81, 201)` являются координатами по x и y верхнего левого края картинки, которую вы хотите вставить. Для удобства просчитывания x, y картинки используйте Asperite/Libresprite.

В следующих строчках файл сохраняется и возвращается функции, которая вызвала этот мем.

## Мемы со вставкой текста

```python
if select == 18:
	img = Image.open("./utils/resources/templates/18.png")

	drawer = ImageDraw.Draw(img)
	font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 50, encoding='UTF-8')
	image_width = img.size[0]
	text = await generate_sentence(chat_id=chat_id, size=2)

	y_text = 320
	lines = textwrap.wrap(text, width=20)
	for line in lines:
		line_width = font.getbbox(line)[2]
		line_height = font.getbbox(line)[3]
		drawer.text((((image_width - line_width) / 2)-25, y_text), 
				line, fill='black', font=font)
		y_text += line_height

	byte_io = BytesIO()
	byte_io.name = 'image.png'

	img.save(byte_io, 'PNG')
	byte_io.seek(0)

	return byte_io.read()
```

Здесь представлен пример мема со вставкой текста. Сначала открывается шаблон мема и создаётся `drawer` чтобы бот мог рисовать на ней текстом.

`font = ImageFont.truetype("./utils/resources/fonts/impact.ttf", 50, encoding='UTF-8')` задаёт шрифт мема, который в нём используется. `50` - его размер.

`text = await generate_sentence(chat_id=chat_id, size=2)` получения текста из генератора среднего размера. Для получения маленького выбирайте `size=1`.

`y_text` задаёт верхнюю границу по y текста, который рисует бот.

`lines = textwrap.wrap(text, width=20)` разделяет текст на строчки шириной по 20 символов, это также можно изменить.

Далее происходит цикл по строчкам и конкретную строчку надо разобрать подробно.

```python
drawer.text((((image_width - line_width) / 2)-25, y_text),
				line, fill='black', font=font)
```

`image_width - line_width) / 2` - середина изображания, соответственно текст можно сдигвть слево с помощью минуса и вправо с помощью плюса.

`fill='black'` - чёрный текст, также можно добавить обводку добавив после `fill` аргументы `stroke_width=2, stroke_fill='black'`, где `stroke_width` отвечает за ширину обводки, а `stroke_fill` за цвет обводки.

Далее y увеличивается для новой строчки и цикл продолжается. Файл сохраняется и возвращается функции, которая вызвала этот мем.

## Помогите в разработке!

Так как проект абсолютно открытый, вы можете создавать мемы конкретно для себя, а можете сделать pull request чтобы их можно было использовать всем, кто будет создавать свои инстансы для себя. Пожалуйста, рассмотрите эту возможность <3
