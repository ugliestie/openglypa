from utils.db import read_words
import mc
from mc.builtin import validators

async def generate_sentence(chat_id, chars=None, words=None):
	text_model = await read_words(chat_id=chat_id)
	generator = mc.PhraseGenerator(samples=text_model)
	if chars is not None:
		message = generator.generate_phrase(
		attempts=1999,
		validators=[
			validators.chars_count(minimal=chars),
		],
		)
	elif words is not None:
		message = generator.generate_phrase(
		attempts=1999,
		validators=[
			validators.words_count(minimal=words)
		],
		)
	else:
		message = generator.generate_phrase(
		validators=[
			validators.words_count(minimal=4, maximal=10),
			validators.chars_count(minimal=10, maximal=100),
		],
		)
	return message

async def generate_sentences(chat_id, count):
	text_model = await read_words(chat_id=chat_id)
	generator = mc.PhraseGenerator(samples=text_model)
	messages = generator.generate_phrases(
		count=count,
		validators=[
			validators.words_count(minimal=4, maximal=10),
			validators.chars_count(minimal=10, maximal=100),
		],
		)
	return messages