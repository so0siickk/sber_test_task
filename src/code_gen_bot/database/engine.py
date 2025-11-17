from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from code_gen_bot.config import settings

engine = create_async_engine(settings.db_url)

SessionMaker = async_sessionmaker(engine, expire_on_commit=False)
