from aiogram import Router
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, IS_NOT_MEMBER, MEMBER, ADMINISTRATOR
from aiogram.types import ChatMemberUpdated

router = Router()

@router.my_chat_member(
    ChatMemberUpdatedFilter(
        member_status_changed=IS_NOT_MEMBER >> (MEMBER | ADMINISTRATOR)
    )
)
async def bot_added_as_admin(event: ChatMemberUpdated):
    await event.answer(
        text='''Привет, я Openglypa <tg-emoji emoji-id='5197442707751996058'>🆗</tg-emoji> \n'''
            f'''Спасибо, что добавили меня в "{event.chat.title}"! Я анализирую сообщения в групповом чате и генерирую на его основе контент. \n'''
            '''Настрой меня с помощью команды <code>h j s</code> и узнай мои команды с помощью команды <code>h j h</code>!'''
    )