"""Agent runtime memory and conversation schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MemoryCreate(BaseModel):
    """Create payload for agent memory."""

    session_id: str
    user_tag: str | None = None
    memory_type: str
    category: str
    subject: str
    content: str
    source: str
    importance: int = 3
    expires_at: datetime | None = None


class MemoryResponse(BaseModel):
    """Agent memory response."""

    id: int
    session_id: str
    user_tag: str | None = None
    memory_type: str
    category: str
    subject: str
    content: str
    source: str
    importance: int
    expires_at: datetime | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    """Agent memory list response."""

    memories: list[MemoryResponse]
    total: int


class ReminderCreate(BaseModel):
    """Create payload for memory reminders."""

    reminder_type: str = "one_time"
    trigger_at: datetime
    recurrence_rule: str | None = None


class ReminderResponse(BaseModel):
    """Reminder response."""

    id: int
    memory_id: int
    reminder_type: str
    trigger_at: datetime
    recurrence_rule: str | None = None
    triggered: bool
    trigger_count: int
    created_at: datetime


class ReminderListResponse(BaseModel):
    """Reminder list response."""

    reminders: list[ReminderResponse]
    total: int


class ConversationMessageResponse(BaseModel):
    """Conversation history item response."""

    id: int
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: str | None = None
    reasoning_content: str | None = None
    user_tag: str
    created_at: datetime


class ConversationMessageListResponse(BaseModel):
    """Conversation history response."""

    messages: list[ConversationMessageResponse]
    total: int


__all__ = [
    "ConversationMessageListResponse",
    "ConversationMessageResponse",
    "MemoryCreate",
    "MemoryListResponse",
    "MemoryResponse",
    "ReminderCreate",
    "ReminderListResponse",
    "ReminderResponse",
]
