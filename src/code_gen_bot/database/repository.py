from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import ActivePoll, CodeHistory


class Repo:
    """Класс-репозиторий для всех запросов к БД."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def clear_chat_history(self, chat_id: int) -> None:
        """
        Удаляет все строки кода для указанного чата.
        """
        stmt = delete(CodeHistory).where(CodeHistory.chat_id == chat_id)

        await self.session.execute(stmt)

        await self.session.commit()

    async def get_full_code(self, chat_id: int) -> str:
        """Получает весь код для чата в виде одной строки."""
        stmt = select(CodeHistory.line_text).where(CodeHistory.chat_id == chat_id).order_by(CodeHistory.line_number)
        result = await self.session.execute(stmt)
        lines = result.scalars().all()
        return "\n".join(lines)

    async def add_code_line(self, chat_id: int, line_text: str) -> None:
        """Добавляет новую строку кода, вычисляя ее порядковый номер."""
        max_line_stmt = select(func.max(CodeHistory.line_number)).where(CodeHistory.chat_id == chat_id)
        max_line_res = await self.session.execute(max_line_stmt)
        max_line = max_line_res.scalar_one_or_none() or 0

        new_line = CodeHistory(
            chat_id=chat_id,
            line_number=max_line + 1,
            line_text=line_text,
        )
        self.session.add(new_line)
        await self.session.commit()

    async def set_active_poll(self, chat_id: int, message_id: int, poll_id: str) -> None:
        """Сохраняет или обновляет информацию об активном опросе."""
        await self.session.execute(delete(ActivePoll).where(ActivePoll.chat_id == chat_id))

        new_poll = ActivePoll(chat_id=chat_id, message_id=message_id, poll_id=poll_id)
        self.session.add(new_poll)
        await self.session.commit()

    async def get_active_poll(self, chat_id: int) -> ActivePoll | None:
        """Получает информацию об активном опросе в чате."""
        stmt = select(ActivePoll).where(ActivePoll.chat_id == chat_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
