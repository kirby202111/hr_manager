"""Agent runtime services for memories and conversations."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.agent.repositories import runtime as runtime_repo
from app.agent.schemas.memory import (
    ConversationMessageListResponse,
    ConversationMessageResponse,
    MemoryCreate,
    MemoryListResponse,
    MemoryResponse,
    ReminderCreate,
    ReminderListResponse,
    ReminderResponse,
)
from app.errors import NotFoundError


def _to_memory_response(row: dict) -> MemoryResponse:
    return MemoryResponse(**row)


def _to_reminder_response(row: dict) -> ReminderResponse:
    return ReminderResponse(**row)


def _to_message_response(row: dict) -> ConversationMessageResponse:
    return ConversationMessageResponse(**row)


def get_memory(memory_id: int, db: Session | None = None) -> MemoryResponse:
    row = runtime_repo.get_memory_by_id(memory_id, db)
    if row is None:
        raise NotFoundError(f"Memory {memory_id} not found")
    return _to_memory_response(row)


def recall_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 10,
    db: Session | None = None,
) -> MemoryListResponse:
    rows = runtime_repo.list_memories(user_tag, memory_type, category, subject, keyword, limit, db)
    return MemoryListResponse(memories=[_to_memory_response(row) for row in rows], total=len(rows))


def save_memory(data: MemoryCreate, db: Session | None = None) -> MemoryResponse:
    if data.memory_type == "preference" and data.user_tag:
        existing = runtime_repo.list_memories(
            data.user_tag,
            memory_type="preference",
            subject=data.subject,
            limit=1,
            db=db,
        )
        if existing:
            row = runtime_repo.update_memory(
                existing[0]["id"],
                {
                    "content": data.content,
                    "importance": data.importance,
                    "source": data.source,
                    "expires_at": data.expires_at,
                },
                db,
            )
            if row is not None:
                return _to_memory_response(row)
    row = runtime_repo.create_memory(data.model_dump(), db)
    return _to_memory_response(row)


def delete_memory(memory_id: int, db: Session | None = None) -> dict[str, str]:
    if not runtime_repo.delete_memory(memory_id, db):
        raise NotFoundError(f"Memory {memory_id} not found")
    return {"message": f"Memory {memory_id} deleted"}


def create_reminder(memory_id: int, data: ReminderCreate, db: Session | None = None) -> ReminderResponse:
    if runtime_repo.get_memory_by_id(memory_id, db) is None:
        raise NotFoundError(f"Memory {memory_id} not found")
    payload = data.model_dump()
    payload["memory_id"] = memory_id
    row = runtime_repo.create_reminder(payload, db)
    return _to_reminder_response(row)


def check_pending_reminders(
    user_tag: str,
    before: datetime | None = None,
    db: Session | None = None,
) -> ReminderListResponse:
    effective_before = before or datetime.now(UTC)
    rows = runtime_repo.list_triggered_reminders(user_tag, effective_before, db)
    return ReminderListResponse(reminders=[_to_reminder_response(row) for row in rows], total=len(rows))


def get_session_messages(session_id: str, db: Session | None = None) -> ConversationMessageListResponse:
    rows = runtime_repo.get_messages_by_session(session_id, db)
    return ConversationMessageListResponse(messages=[_to_message_response(row) for row in rows], total=len(rows))


__all__ = [
    "check_pending_reminders",
    "create_reminder",
    "delete_memory",
    "get_memory",
    "get_session_messages",
    "recall_memories",
    "save_memory",
]
