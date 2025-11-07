import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from code_gen_bot.database.repository import Repo

pytestmark = pytest.mark.asyncio


async def test_add_and_get_code(db_session: AsyncSession):
    """
    Тестируем добавление строк кода и их последующее получение.
    """
    repo = Repo(session=db_session)
    chat_id = 12345
    lines_to_add = [
        "import asyncio",
        "async def main():",
        "    print('Hello, test!')",
    ]

    for line in lines_to_add:
        await repo.add_code_line(chat_id=chat_id, line_text=line)

    result_code = await repo.get_full_code(chat_id=chat_id)

    expected_code = "\n".join(lines_to_add)

    assert result_code == expected_code


async def test_clear_history_is_specific_to_chat(db_session: AsyncSession):
    """
    Проверяем, что clear_chat_history удаляет историю только для одного чата.
    """
    repo = Repo(session=db_session)
    chat_id_1 = 111
    chat_id_2 = 222
    line_for_chat_1 = "code for chat 1"
    line_for_chat_2 = "code for chat 2"

    await repo.add_code_line(chat_id_1, line_for_chat_1)
    await repo.add_code_line(chat_id_2, line_for_chat_2)

    await repo.clear_chat_history(chat_id=chat_id_1)

    code_1 = await repo.get_full_code(chat_id_1)
    code_2 = await repo.get_full_code(chat_id_2)

    assert code_1 == ""
    assert code_2 == line_for_chat_2


async def test_set_get_and_update_active_poll(db_session: AsyncSession):
    """
    Проверяем полный цикл работы с активным опросом: создание, получение и обновление.
    """
    repo = Repo(session=db_session)
    chat_id = 123

    await repo.set_active_poll(chat_id=chat_id, message_id=1001, poll_id="poll_one")

    active_poll = await repo.get_active_poll(chat_id)
    assert active_poll is not None
    assert active_poll.message_id == 1001
    assert active_poll.poll_id == "poll_one"

    await repo.set_active_poll(chat_id=chat_id, message_id=2002, poll_id="poll_two")

    updated_poll = await repo.get_active_poll(chat_id)
    assert updated_poll is not None
    assert updated_poll.message_id == 2002


async def test_get_returns_none_for_nonexistent_items(db_session: AsyncSession):
    """
    Проверяем, что методы get_* возвращают None или пустые значения для несуществующих чатов.
    """
    repo = Repo(session=db_session)
    nonexistent_chat_id = 999

    code = await repo.get_full_code(nonexistent_chat_id)
    poll = await repo.get_active_poll(nonexistent_chat_id)

    assert code == ""
    assert poll is None
