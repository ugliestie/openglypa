from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import os

from utils.sqlite import *

from keyboards.settings import *

router = Router()

class Settings(StatesGroup):
	waiting_for_lazyness = State()
	waiting_for_ignore_words = State()

@router.callback_query(F.data == 'generate')
async def process_callback_generate(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="⚙️ Настройки генерации",
			reply_markup=kb_settings_generate()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@router.callback_query(F.data == 'generate_lazyness')
async def process_callback_generate_lazyness(callback: CallbackQuery, state: FSMContext):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="🥱 Управление ленью бота\n"
				f"На данный момент бот ленится писать в {(await get_automatic_generations(callback.message.chat.id))[0]}% случаев\n"
				"Ответьте значением от 0 до 100 чтобы изменить лень бота в процентах\n",
			reply_markup=kb_settings_generate_lazyness()
		)
		await state.set_state(Settings.waiting_for_lazyness.state)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@router.message(Settings.waiting_for_lazyness)
async def lazyness_chosen(message: Message, state: FSMContext):
	if (message.text).isdigit and int(message.text) >= 0 and int(message.text) <= 100:
		await update_lazyness(int(message.text), message.chat.id)
		await message.reply(text="🥱 Лень бота изменена!",
							reply_markup=kb_settings_generate_lazyness())
		await state.clear()

@router.callback_query(F.data.startswith('generate_types'))
async def process_callback_generate_types(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		if callback.data == "generate_types":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, отправляемых ботом",
				reply_markup=kb_settings_generate_types()
			)
		elif callback.data == "generate_types_commands":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, который присылает бот с помощью команд",
				reply_markup=kb_settings_generate_types_commands(await get_commands_settings(callback.message.chat.id))
			)
		elif callback.data == "generate_types_automatic":
			await callback.message.edit_text(
				text="⚙️ Настройки типов контента, который присылает бот автоматически",
				reply_markup=kb_settings_generate_types_automatic(await get_automatic_settings(callback.message.chat.id))
			)
	else:
		await callback.answer("Вы не вызывали данные настройки")

@router.callback_query(F.data.startswith('type'))
async def process_callback_generate_types(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		setting = await get_commands_settings(callback.message.chat.id)
		if callback.data.startswith("type_commands"):
			setting = await get_commands_settings(callback.message.chat.id)
			if callback.data == "type_commands_text":
				await set_setting("commands", "text", not(setting[0]), callback.message.chat.id)
			elif callback.data == "type_commands_topor":
				await set_setting("commands", "topor", not(setting[1]), callback.message.chat.id)
			elif callback.data == "type_commands_demotivators":
				await set_setting("commands", "demotivators", not(setting[2]), callback.message.chat.id)
			elif callback.data == "type_commands_memes":
				await set_setting("commands", "memes", not(setting[3]), callback.message.chat.id)
			elif callback.data == "type_commands_polls":
				await set_setting("commands", "polls", not(setting[4]), callback.message.chat.id)
			await callback.message.edit_text(
					text="⚙️ Настройки типов контента, который присылает бот с помощью команд",
					reply_markup=kb_settings_generate_types_commands(await get_commands_settings(callback.message.chat.id))
				)	
		elif callback.data.startswith("type_automatic"):
			setting = await get_automatic_settings(callback.message.chat.id)
			if callback.data == "type_automatic_text":
				await set_setting("automatic", "text", not(setting[0]), callback.message.chat.id)
			elif callback.data == "type_automatic_topor":
				await set_setting("automatic", "topor", not(setting[1]), callback.message.chat.id)
			elif callback.data == "type_automatic_demotivators":
				await set_setting("automatic", "demotivators", not(setting[2]), callback.message.chat.id)
			elif callback.data == "type_automatic_memes":
				await set_setting("automatic", "memes", not(setting[3]), callback.message.chat.id)
			elif callback.data == "type_automatic_polls":
				await set_setting("automatic", "polls", not(setting[4]), callback.message.chat.id)
			elif callback.data == "type_automatic_reactions":
				await set_setting("automatic", "reactions", not(setting[5]), callback.message.chat.id)
			elif callback.data == "type_automatic_stickers":
				await set_setting("automatic", "stickers", not(setting[6]), callback.message.chat.id)
			await callback.message.edit_text(
					text="⚙️ Настройки типов контента, который присылает бот автоматически",
					reply_markup=kb_settings_generate_types_automatic(await get_automatic_settings(callback.message.chat.id))
				)
	else:
		await callback.answer("Вы не вызывали данные настройки")
  
@router.callback_query(F.data == 'ignore_words')
async def process_callback_ignore_words(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="🚫 Управление игнорируемыми словами",
			reply_markup=kb_settings_ignore_words()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")
  
@router.callback_query(F.data == 'ignore_words_add')
async def process_callback_ignore_words_update(callback: CallbackQuery, state: FSMContext):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="🚫 Управление игнорируемыми словами\n"
				f"Ответьте игнорируемыми строчками через запятую",
			reply_markup=kb_settings_ignore_words_back()
		)
		await state.set_state(Settings.waiting_for_ignore_words.state)
	else:
		await callback.answer("Вы не вызывали данные настройки")
  
@router.message(Settings.waiting_for_ignore_words)
async def state_update_ignore_words(message: Message, state: FSMContext):
	from utils.chat_data import write_ban_words
	if message.text:
		await write_ban_words(message.text, message.chat.id)
		await message.reply(text="Игнорируемые слова обновлены!",
							reply_markup=kb_settings_ignore_words_back())
		await state.clear()
  
@router.callback_query(F.data == 'ignore_words_delete')
async def process_callback_ignore_words_update(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		try:
			os.remove(f"chats/{callback.message.chat.id}/ban.txt")
			await callback.message.edit_text(text="Игнорируемые слова удалены!",
								reply_markup=kb_settings_ignore_words_back())
		except FileNotFoundError:
			await callback.message.edit_text(text="Файла с игнориуемыми словами нет, удалять было нечего",
								reply_markup=kb_settings_ignore_words_back())
	else:
		await callback.answer("Вы не вызывали данные настройки")
   
@router.callback_query(F.data == 'chat_data')
async def process_callback_chat_data(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="🗄️ Управление базами данных чата",
			reply_markup=kb_settings_chat_data()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")
  
@router.callback_query(F.data.startswith('chat_data_'))
async def process_callback_ignore_words_update(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		if callback.data == 'chat_data_text':
			path = f"chats/{callback.message.chat.id}/text.txt"
			message = "текста"
		if callback.data == 'chat_data_images':
			path = f"chats/{callback.message.chat.id}/images.txt"
			message = "изображений"
		if callback.data == 'chat_data_stickers':
			path = f"chats/{callback.message.chat.id}/stickers.txt"
			message = "стикеров"
		try:
			os.remove(path)
			await callback.message.edit_text(text=f"База данных {message} удалена!",
								reply_markup=kb_settings_chat_data_back())
		except FileNotFoundError:
			await callback.message.edit_text(text=f"Базы данных {message} нет, удалять было нечего",
								reply_markup=kb_settings_chat_data_back())
	else:
		await callback.answer("Вы не вызывали данные настройки")

@router.callback_query(F.data == 'settings')
async def process_callback_settings(callback: CallbackQuery):
	if callback.from_user.id == callback.message.reply_to_message.from_user.id:
		await callback.message.edit_text(
			text="⚙️ Настройки Openglypa",
			reply_markup=kb_settings_main()
		)
	else:
		await callback.answer("Вы не вызывали данные настройки")