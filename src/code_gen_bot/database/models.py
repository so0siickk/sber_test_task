from sqlalchemy import BigInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CodeHistory(Base):
    __tablename__ = "code_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    line_number: Mapped[int]
    line_text: Mapped[str]


class ActivePoll(Base):
    __tablename__ = "active_polls"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger)
    poll_id: Mapped[str] = mapped_column(String, index=True)
