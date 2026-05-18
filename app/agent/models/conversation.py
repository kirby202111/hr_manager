"""Agent runtime conversation message model."""

from __future__ import annotations

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin


class ConversationMessage(Base, IdentityMixin, TimestampMixin, DictMixin):
    """Stored conversation message, tool trace, or reasoning fragment."""

    __tablename__ = "conversation_messages"
    __table_args__ = (
        Index("ix_conversation_messages_session_created", "session_id", "created_at"),
        Index("ix_conversation_messages_user_session", "user_tag", "session_id"),
    )

    session_id: Mapped[str] = mapped_column(String(80), nullable=False)
    user_tag: Mapped[str] = mapped_column(String(80), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tool_calls: Mapped[str | None] = mapped_column(Text, nullable=True)
    reasoning_content: Mapped[str | None] = mapped_column(Text, nullable=True)


__all__ = ["ConversationMessage"]
