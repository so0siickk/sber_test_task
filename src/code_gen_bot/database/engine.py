from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DB_URL = "sqlite+aiosqlite:///db.sqlite3"

engine = create_async_engine(DB_URL)

SessionMaker = async_sessionmaker(engine, expire_on_commit=False)
