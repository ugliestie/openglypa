from sqlalchemy import TEXT, Boolean, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column

from utils.config import DB_URL

engine = create_async_engine(url=DB_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class CommandsSettings(Base):
    __tablename__ = "group_commands_settings"
    __table_args__ = {'extend_existing': True} 

    group_id = mapped_column(TEXT, primary_key=True)
    text = mapped_column(Boolean, default=True)
    topor = mapped_column(Boolean, default=True)
    demotivators = mapped_column(Boolean, default=True)
    memes = mapped_column(Boolean, default=True)
    polls = mapped_column(Boolean, default=True)


class AutomaticSettings(Base):
    __tablename__ = "group_automatic_settings"
    __table_args__ = {'extend_existing': True} 

    group_id = mapped_column(TEXT, primary_key=True)
    lazyness = mapped_column(Integer, default=95)
    text = mapped_column(Boolean, default=True)
    topor = mapped_column(Boolean, default=True)
    demotivators = mapped_column(Boolean, default=True)
    memes = mapped_column(Boolean, default=True)
    polls = mapped_column(Boolean, default=True)
    reactions = mapped_column(Boolean, default=True)
    stickers = mapped_column(Boolean, default=True)
    


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
