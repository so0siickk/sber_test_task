import asyncio
import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from loguru import logger

from code_gen_bot.config import settings
from code_gen_bot.database.engine import SessionMaker, engine
from code_gen_bot.database.models import Base
from code_gen_bot.handlers import register_all_routers
from code_gen_bot.middleware.repo import RepoMiddleware
from code_gen_bot.services.llm_client import MockLLMClient


async def main():
    logger.add("logs/bot.log", rotation="500 MB", level="INFO")
    logger.info("Starting bot...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # --- используем заглушку ---

    # Чтобы переключиться на реальный API, нужно заменить MockLLMClient на OpenAIClient.
    llm_client = MockLLMClient()
    # llm_client = OpenAIClient(
    #     api_key=settings.llm_api_key,
    #     api_base=settings.llm_api_base
    # )

    bot_start_time = datetime.datetime.now()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp["bot_start_time"] = bot_start_time
    dp["bot"] = bot
    dp["llm_client"] = llm_client
    dp.update.middleware(RepoMiddleware(session_pool=SessionMaker))
    register_all_routers(dp)

    logger.info("Bot started!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
