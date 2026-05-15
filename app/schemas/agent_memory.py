from datetime import datetime

from pydantic import BaseModel


# ── AgentMemory ──────────────────────────────────────────────


VALID_MEMORY_TYPES = {"fact", "observation", "preference", "reminder", "context"}
VALID_CATEGORIES = {"onboarding", "project", "employee", "analytics", "general"}
VALID_SOURCES = {"agent_observed", "user_instructed", "system_detected"}


class MemoryCreate(BaseModel):
    session_id: str
    user_tag: str | None = None
    memory_type: str
    category: str
    subject: str
    content: str
    source: str = "agent_observed"
    importance: int = 3
    expires_at: datetime | None = None


class MemoryUpdate(BaseModel):
    content: str | None = None
    importance: int | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None


class MemoryResponse(BaseModel):
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
    memories: list[MemoryResponse]
    total: int


# ── MemoryReminder ───────────────────────────────────────────


VALID_REMINDER_TYPES = {"one_time", "recurring"}


class ReminderCreate(BaseModel):
    reminder_type: str = "one_time"
    trigger_at: datetime
    recurrence_rule: str | None = None


class ReminderResponse(BaseModel):
    id: int
    memory_id: int
    reminder_type: str
    trigger_at: datetime
    recurrence_rule: str | None = None
    triggered: bool
    trigger_count: int
    created_at: datetime


class ReminderListResponse(BaseModel):
    reminders: list[ReminderResponse]
    total: int


class ConversationMessageResponse(BaseModel):
    id: int
    role: str
    content: str | None = None
    tool_call_id: str | None = None
    tool_calls: str | None = None
    reasoning_content: str | None = None
    user_tag: str
    created_at: datetime


class ConversationMessageListResponse(BaseModel):
    messages: list[ConversationMessageResponse]
    total: int
