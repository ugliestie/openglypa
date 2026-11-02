"""
Скрипт для оптимизации базы данных, которая была до коммита ba34c110a495429a1c0cec800a48602d85766b20
"""
import asyncio
import os

from utils.chat_data import read_words, write_words

chats = [int(n) for n in os.listdir("chats") if os.path.isdir(os.path.join("chats", n))]
print("привет! процесс оптимизации может занять до 30 секунд! \033[93mКруто погнали\033[0m") # ОЧЕНЬ важно что этот текст ЖЁЛТЕНЬКОГО ЦВЕТА!!!!!!!!!!
async def main():
	for chat in chats:
		samples = await read_words(chat)
		os.remove(f"chats/{chat}/text.txt")
		for sample in samples:
			await write_words(sample, chat)

if __name__ == "__main__":
	asyncio.run(main())
print("круто! готово! можешь запускать main.py")
