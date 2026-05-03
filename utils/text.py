from utils.chat_data import read_words
from random import choice

# Спасибо Witless за реализацию алгоритма Маркова! 
# https://github.com/jieggii/witless/blob/master/api/generator/generator.pyx
def generate(samples, tries_count, size=None, chars_count=None, start=None):
	_start = "___start___"
	_end = "___end___"
	frames = []
	start_frames = []
	frame_map = {}
 
	if not samples:
		return None

	for sample in samples:
		words = sample.split(" ")
		frames.append(_start)
		for word in words:
			frames.append(word.lower())
		frames.append(_end)

	for i in range(len(frames)):
		if frames[i] != _end:
			try:
				frame_map[frames[i]].append(frames[i + 1])

			except KeyError:
				frame_map[frames[i]] = [frames[i + 1]]

			if frames[i] == _start:
				start_frames.append(frames[i + 1])

	if start is None:
		for i in range(tries_count):
			result = [choice(start_frames)]

			for frame in result:
				next_frame = choice(frame_map[frame])
				if next_frame == _end:
					break
				else:
					result.append(next_frame)

			str_result = " ".join(result)

			if str_result not in samples:
				if size is not None:
					if size == 0: # any
						if len(result) <= 100:
							return str_result

					if size == 1:  # small
						if 2 <= len(result) <= 3:
							return str_result

					elif size == 2:  # medium
						if 4 <= len(result) <= 7:
							return str_result
	
					elif size == 3:  # small + medium для демотиваторов
							if 2 <= len(result) <= 7:
								return str_result

					elif size == 4:  # large
						if len(result) >= 30:
							return str_result
				elif chars_count is not None:
					if chars_count-10 <= len(str_result) <= chars_count+10:
						return str_result
				elif start is not None:
					if str_result.startswith(start):
						return str_result
	else: 
		start_word = start.split(" ")[-1] ## Генерация продолжается с последнего слова в стартовой строке, остальное пока можно отбросить
		try: 
			validated = choice(frame_map[start_word]) ## Происходит попытка получить следующий фрейм к слову, если получается, то идёт дальше генерация как обычно, иначе упадёт в except
			for i in range(tries_count):
				result = [validated] ## Берём следующий фрейм и от него продолжаем

				for frame in result:
					next_frame = choice(frame_map[frame])
					if next_frame == _end:
						break
					else:
						result.append(next_frame)

				result[:0] = [start] ## Добавление всей стратовой строки к массиву результата
				print(start_word)

				str_result = " ".join(result)

				if str_result not in samples and str_result != start:
					if size is not None:
						if size == 0: # any
							if len(result) <= 100:
								return str_result

						if size == 1:  # small
							if 2 <= len(result) <= 3:
								return str_result

						elif size == 2:  # medium
							if 4 <= len(result) <= 7:
								return str_result
		
						elif size == 3:  # small + medium для демотиваторов
								if 2 <= len(result) <= 7:
									return str_result

						elif size == 4:  # large
							if len(result) >= 30:
								return str_result
					elif chars_count is not None:
						if chars_count-10 <= len(str_result) <= chars_count+10:
							return str_result
		except: ## Если получить следующий фрейм к слову не получилось, если получается
			start_before_last = start.split(" ")[:-1] ## Получение всех слов до последнего
			possible = [] ## Массив возможных слов для продолжения

			for i in range(len(frames)-1): ## Перебор всех фреймов
				if frames[i].startswith(start_word) and frames[i] != _start and frames[i+1] != _end: ## Если фрейм начинается также, как и стартовое слово
					possible.append(frames[i]) ## Добавление в массив возможных стартов

			for possible_start in possible: ## Перебор всех возможных слов, похожих на данное в start для продолжения
				for i in range(tries_count):
					result = [possible_start]

					for frame in result:
						next_frame = choice(frame_map[frame])
						if next_frame == _end:
							break
						else:
							result.append(next_frame)

					if start_before_last: 
						result[:0] = start_before_last

					str_result = " ".join(result)

					if str_result not in samples and str_result != start:
						if size is not None:
							if size == 0: # any
								if len(result) <= 100:
									return str_result

							if size == 1:  # small
								if 2 <= len(result) <= 3:
									return str_result

							elif size == 2:  # medium
								if 4 <= len(result) <= 7:
									return str_result
			
							elif size == 3:  # small + medium для демотиваторов
									if 2 <= len(result) <= 7:
										return str_result

							elif size == 4:  # large
								if len(result) >= 30:
									return str_result
						elif chars_count is not None:
							if chars_count-10 <= len(str_result) <= chars_count+10:
								return str_result

	return None

async def generate_sentence(chat_id, size=None, chars_count=None, start=None):
	text_model = await read_words(chat_id=chat_id)
	if size is not None:
		message = generate(samples=text_model, tries_count=5000, size=size)
	elif chars_count is not None:
		message = generate(samples=text_model, tries_count=10000, chars_count=chars_count)
	elif start is not None:
		message = generate(samples=text_model, tries_count=10000, start=start)
	else:
		message = generate(samples=text_model, tries_count=5000, size=0)
	return message

async def generate_sentences(chat_id, count, size=0):
	text_model = await read_words(chat_id=chat_id)
	messages = [generate(samples=text_model, tries_count=5000, size=size) for x in range(count)]
	return messages