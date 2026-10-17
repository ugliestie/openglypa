from sqlalchemy import select

from database.models import AutomaticSettings, CommandsSettings, async_session


class GroupNotFound(BaseException):
    pass

async def check_group(group_id):
    async with async_session() as session:
        group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == group_id))
        
        if not group:
            session.add(CommandsSettings(group_id=group_id))
            session.add(AutomaticSettings(group_id=group_id))
            await session.commit()

async def get_commands_settings(group_id):
    async with async_session() as session:
        group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == group_id))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.text, group.topor, group.demotivators, group.memes, group.polls)
        
async def get_automatic_settings(group_id):
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == group_id))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.text, group.topor, group.demotivators, group.memes, group.polls, group.reactions, group.stickers)       

async def get_automatic_generations(group_id):
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == group_id))
        
        if group is None:
            raise GroupNotFound
        else:
            return (group.text, group.topor, group.demotivators, group.memes, group.polls, group.reactions, group.stickers) 

async def set_setting(type_setting, kind_setting, setting, group_id):
    async with async_session() as session:   
        if type_setting == "commands":
            group = await session.scalar(select(CommandsSettings).where(CommandsSettings.group_id == group_id))
        elif type_setting == "automatic":
            group = await session.scalar(select(AutomaticSettings).where(AutomaticSettings.group_id == group_id))
        
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

async def update_lazyness(lazyness, group_id):
    async with async_session() as session:
        group = await session.scalar(select(AutomaticSettings).where(CommandsSettings.group_id == group_id))
                
        if group is None:
            raise GroupNotFound
        else:
            group.lazyness = lazyness
            await session.commit()