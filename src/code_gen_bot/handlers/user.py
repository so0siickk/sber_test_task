from aiogram import Router, types
from aiogram.filters import Command

from code_gen_bot.database.repository import Repo

user_router = Router()


@user_router.message(Command("code"))
async def cmd_code(message: types.Message, repo: Repo):
    full_code = await repo.get_full_code(chat_id=message.chat.id)

    if not full_code:
        await message.answer("Код пока пуст. Начните генерацию командой /start (только для админов).")
        return

    await message.answer(f"<pre>{full_code}</pre>")
