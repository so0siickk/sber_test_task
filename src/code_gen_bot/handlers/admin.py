import datetime
import html
from pathlib import Path

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from loguru import logger

from code_gen_bot.config import settings
from code_gen_bot.database.repository import Repo
from code_gen_bot.services.llm_client import LLMClient, LLMError

admin_router = Router()
admin_router.message.filter(lambda message: message.from_user.id in settings.admin_ids)


async def process_and_send_new_poll(message: types.Message, repo: Repo, llm_client: LLMClient):
    """Общая логика: получить контекст, сгенерировать варианты, отправить опрос."""
    try:
        code_context = await repo.get_full_code(message.chat.id)
        options = await llm_client.generate_code_options(context=code_context)

        options_to_send = options[:4]

        poll_message = await message.bot.send_poll(
            chat_id=message.chat.id,
            question="Выберите следующую строку кода",
            options=options_to_send,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        await repo.set_active_poll(
            chat_id=message.chat.id, message_id=poll_message.message_id, poll_id=poll_message.poll.id
        )
    except LLMError as e:
        logger.error(f"LLM error for chat {message.chat.id}: {e}")
        await message.answer(
            "Не удалось сгенерировать варианты после нескольких попыток.\n"
            "Пожалуйста, попробуйте выполнить команду еще раз."
        )


@admin_router.message(Command("start"))
async def cmd_start(message: types.Message, repo: Repo, llm_client: LLMClient):
    await message.answer(
        f"Привет, админ {message.from_user.full_name}!\nИстория этого чата очищена. Генерирую первый опрос..."
    )
    await repo.clear_chat_history(chat_id=message.chat.id)
    await process_and_send_new_poll(message, repo, llm_client)


@admin_router.message(Command("next"))
async def cmd_next(message: types.Message, repo: Repo, llm_client: LLMClient):
    active_poll = await repo.get_active_poll(chat_id=message.chat.id)
    if not active_poll:
        await message.answer("Нет активных опросов. Начните с команды /start")
        return

    try:
        final_poll = await message.bot.stop_poll(chat_id=active_poll.chat_id, message_id=active_poll.message_id)
    except Exception as e:
        logger.warning(f"Could not stop poll (it might be already closed): {e}")
        await process_and_send_new_poll(message, repo, llm_client)
        return

    winner = max(final_poll.options, key=lambda opt: opt.voter_count, default=None)

    if winner and winner.voter_count > 0:
        await message.answer(f"Принято! Победившая строка:\n<pre>{html.escape(winner.text)}</pre>")
        await repo.add_code_line(chat_id=message.chat.id, line_text=winner.text)
    else:
        await message.answer("Никто не проголосовал. Пропускаем строку.")

    await process_and_send_new_poll(message, repo, llm_client)


@admin_router.message(Command("code_completed"))
async def cmd_code_completed(message: types.Message, repo: Repo, llm_client: LLMClient):
    await message.answer("Получаю текущий код из базы данных...")
    current_code = await repo.get_full_code(chat_id=message.chat.id)

    if not current_code:
        await message.answer("Код пуст, финализировать нечего.")
        return

    await message.answer("Отправляю код в LLM для финализации...")
    try:
        final_code = await llm_client.finalize_code(context=current_code)

        await message.answer("Готово! Финальный код:")
        await message.answer(f"<pre>{final_code}</pre>")

        await message.answer_document(
            document=BufferedInputFile(final_code.encode("utf-8"), filename="code.py"), caption="Код в виде файла"
        )

    except LLMError as e:
        await message.answer(f"Не удалось финализировать код: {e}")


@admin_router.message(Command("logs"))
async def cmd_logs(message: types.Message):
    log_file = Path("logs/bot.log")
    if not log_file.exists():
        await message.answer("Файл логов еще не создан.")
        return

    try:
        log_data = log_file.read_bytes()

        if not log_data:
            await message.answer("Логи пока пусты.")
            return

        await message.answer_document(
            document=BufferedInputFile(log_data, filename="bot_logs.txt"), caption="Последние логи бота."
        )

    except Exception as e:
        logger.error(f"Error reading or sending log file: {e}")
        await message.answer(f"Не удалось отправить файл логов: {e}")


@admin_router.message(Command("health"))
async def cmd_health(message: types.Message, repo: Repo, bot_start_time: datetime.datetime):
    uptime = datetime.datetime.now() - bot_start_time

    active_poll = await repo.get_active_poll(chat_id=message.chat.id)

    status_text = (
        "<b>Bot Health Status:</b>\n\n"
        f"<b>Uptime:</b> {str(uptime).split('.')[0]}\n"
        f"<b>Scheduler Status:</b> Not used (manual poll trigger via /next)\n"
        f"<b>Active Poll in this chat:</b> {'✅ Yes' if active_poll else '❌ No'}"
    )

    await message.answer(status_text)
