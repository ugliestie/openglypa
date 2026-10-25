from random import choice

from utils.chat_data import read_words


class PossibleStartsNotFound(BaseException):
    pass

class FailedByTries(BaseException):
    pass

# Спасибо Witless за реализацию алгоритма Маркова! 
# https://github.com/jieggii/witless/blob/master/api/generator/generator.pyx
def generate(samples: list[str], tries_count: int, size: int = 0, chars_count: int | None =None, start: str | None = None) -> str:
	"""Генерация выражения на основе массива исходных с помощью цепи Маркова

	Args:
		samples (list[str]): лист выражений
		tries_count (int): число попыток
		size (int, optional): размер сообщения, задаваемое при наличии, по умолчанию 0, если 0 - до 100 слов, 1 - от двух до трёх, 2 - от четырёх до семи, 3 - от двух до семи, 4 - сообщение больше десяти слов.
		chars_count (int | None, optional): количество символов, задаваемое при наличии, около которого нужно создать выражение, по умолчанию None
		start (str | None, optional): начало выражения, задаваемое при наличии, которое надо продолжить, по умолчанию None

	Raises:
		NoSamples: не приведено никаких семплов для генерации
		PossibleStartsNotFound: при генерации с заданным стартом не удалось найти любые возможные старты с началом из этого выражения, если frame_map для заданного выражения не было найдено
		FailedByTries: не удалось собрать выражение за заданное число попыток

	Returns:
		str: готовое выражение
	"""
	_start = "___start___"
	_end = "___end___"
	frames = []
	start_frames = []
	frame_map = {}
 
	for sample in samples:
		words = sample.split(" ")
		frames.append(_start)
		frames.extend(words)
		frames.append(_end)

	for i in range(len(frames)):
		if frames[i] != _end:
			try:
				frame_map[frames[i]].append(frames[i + 1])

			except KeyError:
				frame_map[frames[i]] = [frames[i + 1]]

			if frames[i] == _start and frames[i + 1] not in start_frames:
				start_frames.append(frames[i + 1])

	if start is None:
		start_before_last = None
	else:
		start_before_last = start.split(" ")[:-1]
		start_word = start.split(" ")[-1]
		try:
			if frame_map[start_word]:
				found_start_frame = True
		except KeyError:
			found_start_frame = False
			possible = [] # Массив возможных слов для продолжения
		
			for i in range(len(frames)-1): # Перебор всех фреймов
				if frames[i].startswith(start_word) and frames[i] != start_word and frames[i+1] != _end: # Если фрейм начинается также, как и стартовое слово
					possible.append(frames[i]) # Добавление в массив возможных стартов
			if not possible:
				raise PossibleStartsNotFound

	for _ in range(tries_count):
		if start is None:
			result = [choice(start_frames)]
		else:
			if found_start_frame is False:
				result = [choice(possible)]
			else:
				result = [start_word]
    
		for frame in result:
			next_frame = choice(frame_map[frame])
			if next_frame == _end:
				break
			else:
				result.append(next_frame)

		if start_before_last: 
			result[:0] = start_before_last
     
		str_result = " ".join(result)
  
		if chars_count is not None:
			if len(str_result) >= chars_count - 10 and len(str_result) <= chars_count + 10:
				return str_result

		elif size == 0:
			if 2 <= len(result) <= 100:
				return str_result

		elif size == 1:
			if 2 <= len(result) <= 3:
				return str_result

		elif size == 2:
			if 4 <= len(result) <= 7:
				return str_result

		elif size == 3:
			if 2 <= len(result) <= 7:
				return str_result

		elif size == 4:
			if len(result) >= 30:
				return str_result

		elif len(result) != 1:
			return str_result

	raise FailedByTries

async def generate_sentence(chat_id: int, size=0, chars_count=None, start=None) -> str:
	"""Функция, помогающая задавать условия для генерации выражения 

	Args:
		chat_id (_type_): id группового чата
		size (int, optional): размер сообщения, задаваемое при наличии, по умолчанию 0, если 0 - до 100 слов, 1 - от двух до трёх, 2 - от четырёх до семи, 3 - от двух до семи, 4 - сообщение больше десяти слов.
		chars_count (int, optional): количество символов, задаваемое при наличии, около которого нужно создать выражение, по умолчанию None
		start (str, optional): начало выражения, задаваемое при наличии, которое надо продолжить, по умолчанию None

	Returns:
		str: выражение
	"""
	text_model = await read_words(chat_id=chat_id)
	if start is not None:
		message = generate(samples=text_model, tries_count=10000, start=start)
	elif chars_count is not None:
		message = generate(samples=text_model, tries_count=10000, chars_count=chars_count)
	else:
		message = generate(samples=text_model, tries_count=10000, size=size)
	return message

async def generate_sentences(chat_id, count, size=0) -> list[str]:
	"""Функция, помогающая задавать условия для генерации нескольких выражений сразу

	Args:
		chat_id (_type_): id группового чата
		count (_type_): количество выражений
		size (int, optional): размер сообщения, задаваемое при наличии, по умолчанию 0, если 0 - до 100 слов, 1 - от двух до трёх, 2 - от четырёх до семи, 3 - от двух до семи, 4 - сообщение больше десяти слов.

	Returns:
		list[str]: лист выражений
	"""
	return [generate(samples=await read_words(chat_id=chat_id), tries_count=10000, size=size) for _ in range(count)]