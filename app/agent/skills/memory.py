"""Memory-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.agent.schemas.memory import MemoryCreate, ReminderCreate
from app.agent.services import memory as memory_service


def _save_memory(
    session_id,
    memory_type,
    category,
    subject,
    content,
    source,
    user_tag=None,
    importance=3,
    expires_at=None,
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
    keywords=("memory", "remember", "reminder", "记住", "提醒", "记忆"),
    tools=[
        AgentTool(
            name="recall_memories",
            description="Recall saved memories for a user with optional filters.",
            parameters={
                "type": "object",
                "properties": {
                    "user_tag": {"type": "string"},
                    "memory_type": {"type": "string"},
                    "category": {"type": "string"},
                    "subject": {"type": "string"},
                    "keyword": {"type": "string"},
                    "limit": {"type": "integer"},
                },
                "required": ["user_tag"],
            },
            fn=lambda user_tag, memory_type=None, category=None, subject=None, keyword=None, limit=10: safe_call(
                memory_service.recall_memories,
                user_tag,
                memory_type,
                category,
                subject,
                keyword,
                limit,
            ),
        ),
        AgentTool(
            name="save_memory",
            description="Persist a long-term memory entry for a user.",
            parameters={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "user_tag": {"type": "string"},
                    "memory_type": {"type": "string"},
                    "category": {"type": "string"},
                    "subject": {"type": "string"},
                    "content": {"type": "string"},
                    "source": {"type": "string"},
                    "importance": {"type": "integer"},
                    "expires_at": {"type": "string"},
                },
                "required": ["session_id", "memory_type", "category", "subject", "content", "source"],
            },
            fn=_save_memory,
        ),
        AgentTool(
            name="check_reminders",
            description="Check due reminders for a user.",
            parameters={
                "type": "object",
                "properties": {"user_tag": {"type": "string"}},
                "required": ["user_tag"],
            },
            fn=lambda user_tag: safe_call(memory_service.check_pending_reminders, user_tag),
        ),
        AgentTool(
            name="set_reminder",
            description="Attach a reminder to a saved memory.",
            parameters={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "integer"},
                    "trigger_at": {"type": "string"},
                    "reminder_type": {"type": "string"},
                    "recurrence_rule": {"type": "string"},
                },
                "required": ["memory_id", "trigger_at"],
            },
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
