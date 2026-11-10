import logging
import random

from aiogram import F, Router, flags
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    BufferedInputFile,
    LinkPreviewOptions,
    Message,
    ReactionTypeEmoji,
)
from aiogram.utils.chat_member import ADMINS

from database.requests import get_commands_settings
from handlers.errors import handle_rights
from keyboards.settings import kb_settings_main
from keyboards.start import kb_add
from middlewares.inner import ThrottlingMiddleware
from utils.chat_data import NoSamples, RandomImageNotFound
from utils.text import FailedByTries, PossibleStartsNotFound

logger = logging.getLogger(__name__)

router = Router()
router.message.middleware(ThrottlingMiddleware())


class NoBot(BaseException):
    pass


class CantDownloadFileException(Exception):
    pass


async def is_message_admin(message: Message, user_id: int) -> bool:
    if message.bot is None:
        raise NoBot
    member = await message.bot.get_chat_member(message.chat.id, user_id)
    return isinstance(member, ADMINS)


@router.message(Command("start"))
async def cmd_start(message: Message):
    if message.bot:
        if message.chat.type == "private":
            await message.reply(
                text="Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nДобавь меня в групповой чат и я начну учиться вашей группе!",
                reply_markup=kb_add((await message.bot.get_me()).username),
            )
        elif (message.chat.type == "group" or message.chat.type == "supergroup") and (
            message.from_user is None or message.from_user.is_bot is False
        ):
            await message.reply(
                "Привет, я Openglypa! <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \nЯ анализирую сообщения в групповом чате и генерирую на его основе контент. \nНастрой меня с помощью команды <code>h j s</code> и узнай мои команды с помощью команды <code>h j h</code>!"
            )


@router.message(F.text.lower() == ("h j h"))
@router.message(Command("help"))
async def cmd_help(message: Message):
    from main import state

    await message.reply(
        """<b>Справка Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji></b>\n\n"""
        """<blockquote expandable><code>h j g</code> - генерация текста\n"""
        """<code>h j g l</code> - генерация длинного текста\n"""
        """<code>h j g 100</code> - генерация текста размером около 100 символов\n"""
        """<code>h j g привет</code> - генерация текста с началом "привет"\n"""
        """<code>h j hm я кружка?</code> - генерация ответа на да/нет вопрос\n"""
        """<code>h j p</code> - генерация опросов\n"""
        """<code>h j t</code> - генерация Топор 1+ сообщения\n"""
        """<code>h j d</code> - генерация демотиватора\n"""
        """<code>h j m</code> - генерация мема из случайного шаблона\n"""
        """<code>h j booru [теги через пробел]</code> - рандомная картинка из Safebooru по тегам\n"""
        """<code>h j s</code> - настройки бота\n"""
        """<code>h j del</code> - удалить изображение/стикер из базы данных бота\n"""
        """<code>h j stats</code> - статистика базы данных чата\n"""
        """<code>h j h</code> - эта справка</blockquote>\n\n""" + state,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )


@router.message(F.text.lower().startswith("h j g"))
async def force_generate(message: Message):
    from utils.text import generate_sentence

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[0] == 1
    ):
        chars_count = None
        start = None
        size = 0

        if message.reply_to_message:
            start = message.reply_to_message.caption or message.reply_to_message.text
            if start is None:
                await message.reply(
                    "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу найти текст, чтобы его продолжить..."
                )
                return
        elif message.text:
            if message.text.lower() != "h j g":
                arg = message.text[6:]
                if arg.isdigit() and int(arg) > 10:
                    chars_count = int(arg)
                elif arg == "l":
                    size = 4
                else:
                    start = arg.lower()
        else:
            size = 2

        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        try:
            await message.reply(
                await generate_sentence(
                    chat_id=message.chat.id,
                    size=size,
                    chars_count=chars_count,
                    start=start,
                )
            )
        except NoSamples as e:
            logger.warning(str(e))
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!"
            )
            return
        except PossibleStartsNotFound:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти ничего подходящего с таким началом"
            )
            return
        except FailedByTries:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз"
            )
            return
        except Exception:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не придума"
            )
    else:
        return


@router.message(F.text.lower() == "h j t")
@flags.rate_limit()
async def generate_topor_message(message: Message):
    from utils.chat_data import random_image
    from utils.topor import generate_topor

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[1] == 1
    ):
        try:
            text = None

            if (
                message.reply_to_message
                and message.reply_to_message.photo
                and message.reply_to_message.caption
            ):
                image = await message.bot.download(
                    file=message.reply_to_message.photo[-1].file_id
                )
                text = message.reply_to_message.caption.capitalize()
            else:
                image = await random_image(message.chat.id, message.bot)

            if image == None:
                await message.reply(
                    "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу найти изображение, чтобы сгенерировать Топо"
                )
            else:
                await message.bot.send_chat_action(
                    chat_id=message.chat.id, action="upload_photo"
                )
                topor = await generate_topor(message.chat.id, image=image, text=text)
                await message.reply_photo(
                    photo=BufferedInputFile(topor[1], filename="topor.jpg"),
                    caption=topor[0],
                )

        except TelegramBadRequest as e:
            if "not enough rights" in str(e):
                await handle_rights(message, "commands", "topor")
            logger.warning(str(e))
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!"
            )
            return
        except RandomImageNotFound:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз"
            )
            return
        except Exception as e:
            logger.error(f"Ошибка при вызове h j t: {e!s}")
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я ничего не придума"
            )
    else:
        return


@router.message(F.text.lower() == "h j d")
@flags.rate_limit()
async def generate_demotivator_message(message: Message):
    from utils.chat_data import random_image
    from utils.images import generate_demotivator

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[2] == 1
    ):
        try:
            await message.bot.send_chat_action(
                chat_id=message.chat.id, action="upload_photo"
            )
            if message.reply_to_message:
                if message.reply_to_message.photo:
                    image = await message.bot.download(
                        file=message.reply_to_message.photo[-1].file_id
                    )
                    if image is None:
                        raise Exception("Изображение не найдено")
                    demotivator = await generate_demotivator(message.chat.id, image)
                    await message.reply_photo(
                        photo=BufferedInputFile(demotivator, filename="demotivator.jpg")
                    )
                else:
                    demotivator = await generate_demotivator(
                        message.chat.id,
                        await random_image(message.chat.id, message.bot),
                    )
                    await message.reply_photo(
                        photo=BufferedInputFile(demotivator, filename="demotivator.jpg")
                    )
            else:
                demotivator = await generate_demotivator(
                    message.chat.id, await random_image(message.chat.id, message.bot)
                )
                await message.reply_photo(
                    photo=BufferedInputFile(demotivator, filename="demotivator.jpg")
                )
        except TelegramBadRequest as e:
            if "not enough rights" in str(e):
                await handle_rights(message, "automatic", "demotivators")
        except NoSamples:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!"
            )
            return
        except RandomImageNotFound:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз"
            )
            return
        except FailedByTries:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз"
            )
            return
        except Exception as e:
            logger.error(f"Ошибка при вызове h j d: {e!s}")
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и ничего не вышло надемотивировать"
            )
    else:
        return


@router.message(F.text.lower() == "h j m")
@flags.rate_limit()
async def generate_meme_message(message: Message):
    from utils.images import generate_meme

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[3] == 1
    ):
        try:
            await message.bot.send_chat_action(
                chat_id=message.chat.id, action="upload_photo"
            )
            meme = await generate_meme(message.chat.id, message.bot)
            await message.reply_photo(
                photo=BufferedInputFile(meme, filename="meme.jpg")
            )
        except TelegramBadRequest as e:
            if "not enough rights" in str(e):
                await handle_rights(message, "commands", "memes")
        except NoSamples:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!"
            )
            return
        except RandomImageNotFound:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Не могу скачать случайную картинку... Либо я знаю мало картинок, или надо попробовать ещё раз"
            )
            return
        except FailedByTries:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз"
            )
            return
        except Exception as e:
            logger.error(f"Ошибка при вызове h j m: {e!s}")
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и ничего не вышло намемить"
            )
    else:
        return


@router.message(F.text.lower().startswith("h j booru"))
async def generate_booru_message(message: Message):
    from json import JSONDecodeError
    from urllib.error import HTTPError

    from utils.booru import random_booru

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[3] == 1
        and type(message.text) is str
    ):
        try:
            arg = message.text[10:]
            await message.bot.send_chat_action(
                chat_id=message.chat.id, action="upload_photo"
            )
            response = random_booru(arg)

            if "gay" in arg:
                title = "🐘 gaaaaayyyyyyyyy\n"
            elif "furry" in arg:
                title = "🚨🚨🚨🚨 furry detected 🚨🚨🚨🚨\n"
            elif "yaoi" in arg:
                title = "🚨🚨🚨🚨 yaoi detected 🚨🚨🚨🚨\n"
            elif "yuri" in arg:
                title = "🚨🚨🚨🚨 yuri detected 🚨🚨🚨🚨\n"
            else:
                title = ""

            if response[1] != "":
                credit = f"""<a href="{response[1]}">Источник</a>"""
            else:
                credit = "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Нет информации об источнике"

            await message.reply(
                f"""{title}<a href="https://safebooru.org/index.php?page=post&s=view&id={response[2]}">Safebooru</a> • {credit}""",
                link_preview_options=LinkPreviewOptions(
                    url=str(response[0]), show_above_text=True
                ),
            )

        except JSONDecodeError:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Ай! По тегу ничего не найдено :("
            )
        except IndexError:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Ай! По тегу ничего не найдено :("
            )
        except HTTPError:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Ай! Не могу получить ничего с Safebooru, может упал :("
            )
    else:
        return


# I'm so fucking good at this job ... (Kira optimized everything and I wrote funny names for variables and bruteforced shitty code. This is how coding should be)


@router.message(F.text.lower() == "h j p")
async def generate_poll_message(message: Message):
    from utils.text import generate_sentence, generate_sentences

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[4] == 1
    ):
        try:
            await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
            type_poll = random.choice(["quiz", "regular"])
            count_options = random.randint(3, 6)
            if type_poll == "quiz":
                await message.reply_poll(
                    question=await generate_sentence(message.chat.id),
                    options=await generate_sentences(message.chat.id, count_options),
                    type=type_poll,
                    explanation=await generate_sentence(message.chat.id),
                    correct_option_id=random.randint(0, count_options - 1),
                    is_anonymous=random.choice([True, False]),
                )
            else:
                await message.reply_poll(
                    question=await generate_sentence(message.chat.id),
                    options=await generate_sentences(message.chat.id, count_options),
                    type=type_poll,
                    is_anonymous=random.choice([True, False]),
                )
        except TelegramBadRequest as e:
            if "not enough rights" in str(e):
                await handle_rights(message, "commands", "polls")
            else:
                await message.reply(
                    "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не смог придумать опрос"
                )
        except NoSamples:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу найти выражения, из которых можно что-то сгенерировать. Наверное, я не знаю слов, пообщайтесь, чтобы это исправить!"
            )
            return
        except FailedByTries:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Я не могу ничего придумать... Либо я знаю мало слов, или надо попробовать ещё раз"
            )
            return
        except Exception as e:
            logger.error(f"Ошибка при вызове h j p: {e!s}")
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не смог придумать опрос"
            )
    else:
        return


@router.message(F.text.lower() == "h j s")
async def cmd_settings(message: Message):
    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is not None and message.from_user.is_bot is False)
    ):
        if await is_message_admin(message, message.from_user.id):
            await message.reply(
                "⚙️ Настройки Openglypa", reply_markup=kb_settings_main()
            )
        else:
            await message.reply(
                "У вас недостаточно прав в чате, чтобы вызывать эту команду"
            )
    else:
        return


# TODO: добавить банлист для стикеров
@router.message(F.text.lower() == "h j del")
async def cmd_delete(message: Message):
    from utils.chat_data import delete_animation, delete_image, delete_sticker

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is not None and message.from_user.is_bot is False)
        and type(message.reply_to_message) is Message
    ):
        if await is_message_admin(message, message.from_user.id):
            if message.reply_to_message.photo:
                await delete_image(
                    message.reply_to_message.photo[-1].file_id, message.chat.id
                )
                await message.reply("Изображение удалено из базы данных бота")
            elif message.reply_to_message.sticker:
                await delete_sticker(
                    message.reply_to_message.sticker.file_id, message.chat.id
                )
                await message.reply("Стикер удалён из базы данных бота")
            elif message.reply_to_message.animation:
                await delete_animation(
                    message.reply_to_message.animation.file_id, message.chat.id
                )
                await message.reply("Гифка удалена из базы данных бота")
        else:
            await message.reply(
                "У вас недостаточно прав в чате, чтобы вызывать эту команду"
            )
    else:
        return


@router.message(F.text.lower() == "h j stats")
async def cmd_stats(message: Message):
    from utils.chat_data import read_images, read_stickers, read_words

    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
    ):
        chat_id = message.chat.id

        try:
            samples = len(await read_words(chat_id))
        except FileNotFoundError:
            samples = 0
        except NoSamples:
            samples = 0

        try:
            images = len(await read_images(chat_id))
        except FileNotFoundError:
            images = 0
        except NoSamples:
            samples = 0

        try:
            stickers = len(await read_stickers(chat_id))
        except FileNotFoundError:
            stickers = 0
        except NoSamples:
            samples = 0

        await message.reply(
            """<b>Статистика Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji></b>\n\n"""
            f"""Количество сообщений в базе данных: {samples}\n"""
            f"""Количество изображений в базе данных: {images}\n"""
            f"""Количество стикеров в базе данных: {stickers}"""
        )
    else:
        return


@router.message(F.text.lower().contains("h j hm"))
async def generate_reply(message: Message):
    if (
        message.bot
        and (message.chat.type == "group" or message.chat.type == "supergroup")
        and (message.from_user is None or message.from_user.is_bot is False)
        and (await get_commands_settings(message.chat.id))[5] == 1
    ):
        yn = random.randint(1, 10)
        if yn == 1:
            await message.reply("Неее...")
        if yn == 2:
            await message.reply("Возможно в будущем! 🤔")
        if yn == 3:
            await message.reply("Да, у меня есть уверенность 🙂")
        if yn == 4:
            await message.reply("Это странный вопрос. Я не хочу отвечать")
        if yn == 5:
            await message.reply(
                "Это имеет шестидесятисемипроцентный шанс. не скажу, в какую сторону"
            )
        if yn == 6:
            await message.reply(
                "<tg-emoji emoji-id='5197389312718575425'>😪</tg-emoji> Что-то пошло не так и я не могу сложить 2+2"
            )
        if yn == 7:
            await message.reply("Спокойным волнам на реке понравилось. Всё сбудется")
        if yn == 8:
            set_reactions = [
                "🤔",
                "🤯",
                "😢",
                "🎉",
                "🤩",
                "🕊",
                "🤷‍♂",
                "🤷",
                "🤷‍♀",
                "😡",
            ]
            react = ReactionTypeEmoji(emoji=random.choice(set_reactions))
            await message.react([react])
        if yn == 9:
            await message.answer_sticker(
                sticker="CAACAgIAAxkBAAEpAsFp--224lYB9gthIp4I36sDAAHjH5cAAiWPAAKHTklKtLyM8h5_QgE7BA"
            )
        if yn == 10:
            await message.reply("да давай ура даааааа")
    else:
        return
