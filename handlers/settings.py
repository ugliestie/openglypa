from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.sqlite import *

from keyboards.settings import *

router = Router()

class Settings(StatesGroup):
	waiting_for_lazyness = State()

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
			await callback.message.edit_text(
					text="⚙️ Настройки типов контента, который присылает бот автоматически",
					reply_markup=kb_settings_generate_types_automatic(await get_automatic_settings(callback.message.chat.id))
				)
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