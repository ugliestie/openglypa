from sqlalchemy import select

from database.models import AutomaticSettings, CommandsSettings, async_session


class GroupNotFound(BaseException):
    pass

async def check_group(group_id: int) -> None:
    """Проверка, есть ли группа в базе данных

    Args:
        group_id (int): id группового чата
    """
    async with async_session() as session:
        group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == str(group_id)))
        
        if not group:
            session.add(CommandsSettings(group_id=group_id))
            session.add(AutomaticSettings(group_id=group_id))
            await session.commit()

async def get_commands_settings(group_id: int) -> tuple[bool, bool, bool, bool, bool]:
    """Получение списка включенных/выключенных и выключенных команд

    Args:
        group_id (int): id группового чата

    Raises:
        GroupNotFound: группы нет в базе данных

    Returns:
        tuple[bool, bool, bool, bool, bool]: список включенных/выключенных команд по типам text, topor, demotivators, memes, polls
    """
    async with async_session() as session:
        group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == str(group_id)))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.text, group.topor, group.demotivators, group.memes, group.polls)
        
async def get_automatic_settings(group_id: int) -> tuple[bool, bool, bool, bool, bool, bool, bool]:
    """Получение списка включенных/выключенных автоматических генераций

    Args:
        group_id (int): id группового чата

    Raises:
        GroupNotFound: группы нет в базе данных

    Returns:
        tuple[bool, bool, bool, bool, bool, bool, bool]: список включенных/выключенных генераций по типам text, topor, demotivators, memes, polls, reactions, stickers
    """
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == str(group_id)))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.text, group.topor, group.demotivators, group.memes, group.polls, group.reactions, group.stickers)       

async def get_automatic_generations(group_id: int) -> tuple[int, bool, bool, bool, bool, bool, bool, bool]:
    """Получение списка из значения лени и включенных/выключенных автоматических генераций

    Args:
        group_id (int): id группового чата

    Raises:
        GroupNotFound: группы нет в базе данных

    Returns:
        tuple[int, bool, bool, bool, bool, bool, bool, bool]: список из лени в процентах и включенных/выключенных генераций по типам text, topor, demotivators, memes, polls, reactions, stickers
    """
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == str(group_id)))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.lazyness, group.text, group.topor, group.demotivators, group.memes, group.polls, group.reactions, group.stickers) 

async def set_setting(type_setting: str, kind_setting: str, setting: bool, group_id: int) -> None:
    """Сменить значение настройки

    Args:
        type_setting (str): commands, automatic
        kind_setting (str): тип контента (text, topor, demotivators, memes, polls, reactions, stickers)
        setting (bool): True, если включить и False, если выключить
        group_id (int): id группового чата

    Raises:
        GroupNotFound: группы нет в базе данных
    """
    async with async_session() as session:   
        if type_setting == "commands":
            group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == str(group_id)))
        elif type_setting == "automatic":
            group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == str(group_id)))
        
        if group is None:
            raise GroupNotFound
        else:
            if kind_setting == "text":
                group.text = setting
            elif kind_setting == "topor":
                group.topor = setting
            elif kind_setting == "demotivators":
                group.demotivators = setting
            elif kind_setting == "memes":
                group.memes = setting
            elif kind_setting == "polls":
                group.polls = setting
            elif type(group) is AutomaticSettings and kind_setting == "reactions":
                group.reactions = setting
            elif type(group) is AutomaticSettings and kind_setting == "stickers":
                group.stickers = setting
            await session.commit()

async def update_lazyness(lazyness: int, group_id: int) -> None:
    """Сменить значение лени

    Args:
        lazyness (int): значение лени в процентах
        group_id (int): id группового чата

    Raises:
        GroupNotFound: группы нет в базе данных
    """
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == str(group_id)))
                
        if group is None:
            raise GroupNotFound
        else:
            group.lazyness = lazyness
            await session.commit()