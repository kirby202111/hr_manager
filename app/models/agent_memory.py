"""Agent 记忆与会话消息模型。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class AgentMemory(Base):
    """长期记忆实体，保存偏好、事实和可过期上下文。"""

    __tablename__ = "agent_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False)
    user_tag: Mapped[str | None] = mapped_column(String(100), nullable=True)
    memory_type: Mapped[str] = mapped_column(String(30), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    importance: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class MemoryReminder(Base):
    """记忆提醒实体，用于对指定记忆进行定时触发。"""

    __tablename__ = "memory_reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    memory_id: Mapped[int] = mapped_column(Integer, nullable=False)
    reminder_type: Mapped[str] = mapped_column(String(20), nullable=False)
    trigger_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recurrence_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    triggered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    trigger_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class ConversationMessage(Base):
    """会话消息审计实体，保存用户、助手和工具调用消息。"""

    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_tag: Mapped[str] = mapped_column(String(100), nullable=False, default="default", index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(String, nullable=True)
    tool_call_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tool_calls: Mapped[str | None] = mapped_column(String, nullable=True)
    reasoning_content: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def to_dict(self) -> dict:
        """默认用户标签不回传给前端，减少冗余字段。"""
        data = _to_dict(self)
        if self.user_tag == "default":
            data.pop("user_tag", None)
        return data
