"""Memory-related agent tools."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.agent.schemas.memory import MemoryCreate, ReminderCreate
from app.agent.services import memory as memory_service


class RecallMemoriesInput(BaseModel):
    user_tag: str | None = None
    memory_type: str | None = None
    category: str | None = None
    subject: str | None = None
    keyword: str | None = None
    limit: int = 10


class SaveMemoryInput(BaseModel):
    memory_type: str
    category: str
    subject: str
    content: str
    source: str
    importance: int = 3
    expires_at: datetime | None = None


class CheckRemindersInput(BaseModel):
    user_tag: str | None = None


class SetReminderInput(BaseModel):
    memory_id: int
    trigger_at: datetime
    reminder_type: str = "one_time"
    recurrence_rule: str | None = None


def _save_memory(
    session_id: str,
    memory_type: str,
    category: str,
    subject: str,
    content: str,
    source: str,
    user_tag: str | None = None,
    importance: int = 3,
    expires_at: datetime | None = None,
):
    return safe_call(
        memory_service.save_memory,
        MemoryCreate(
            session_id=session_id,
            user_tag=user_tag,
            memory_type=memory_type,
            category=category,
            subject=subject,
            content=content,
            source=source,
            importance=importance,
            expires_at=expires_at,
        ),
    )


skill = AgentSkill(
    name="memory",
    description="Store and recall long-term user memories and reminders.",
    applicability="Use for cross-session context, preferences, reminders, and durable observations.",
    keywords=("memory", "remember", "reminder", "记住", "提醒", "记忆", "preference", "偏好"),
    tools=[
        AgentTool(
            name="recall_memories",
            description="Recall saved memories for the current user with optional filters.",
            parameters=RecallMemoriesInput.model_json_schema(),
            fn=lambda user_tag=None, memory_type=None, category=None, subject=None, keyword=None, limit=10: safe_call(
                memory_service.recall_memories,
                user_tag,
                memory_type,
                category,
                subject,
                keyword,
                limit,
            ),
            context_defaults={"user_tag": "user_tag"},
        ),
        AgentTool(
            name="save_memory",
            description="Persist a long-term memory entry for the current user.",
            parameters=SaveMemoryInput.model_json_schema(),
            fn=_save_memory,
            context_defaults={"session_id": "session_id", "user_tag": "user_tag"},
        ),
        AgentTool(
            name="check_reminders",
            description="Check due reminders for the current user.",
            parameters=CheckRemindersInput.model_json_schema(),
            fn=lambda user_tag=None: safe_call(memory_service.check_pending_reminders, user_tag),
            context_defaults={"user_tag": "user_tag"},
        ),
        AgentTool(
            name="set_reminder",
            description="Attach a reminder to a saved memory.",
            parameters=SetReminderInput.model_json_schema(),
            fn=lambda memory_id, trigger_at, reminder_type="one_time", recurrence_rule=None: safe_call(
                memory_service.create_reminder,
                memory_id,
                ReminderCreate(
                    reminder_type=reminder_type,
                    trigger_at=trigger_at,
                    recurrence_rule=recurrence_rule,
                ),
            ),
        ),
    ],
)

__all__ = ["skill"]
