"""Agent runtime repositories for memories, reminders, conversations, and onboarding state."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.agent.models import AgentMemory, ConversationMessage, MemoryReminder, OnboardingCase
from app.database import db_session


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 10,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(AgentMemory).filter(AgentMemory.user_tag == user_tag, AgentMemory.is_active.is_(True))
        if memory_type is not None:
            query = query.filter(AgentMemory.memory_type == memory_type)
        if category is not None:
            query = query.filter(AgentMemory.category == category)
        if subject is not None:
            query = query.filter(AgentMemory.subject == subject)
        if keyword is not None:
            query = query.filter(
                or_(
                    AgentMemory.subject.ilike(f"%{keyword}%"),
                    AgentMemory.content.ilike(f"%{keyword}%"),
                )
            )
        now = datetime.now(UTC)
        query = query.filter(or_(AgentMemory.expires_at.is_(None), AgentMemory.expires_at > now))
        rows = query.order_by(AgentMemory.importance.desc(), AgentMemory.updated_at.desc()).limit(limit).all()
        return [row.to_dict() for row in rows]


def get_memory_by_id(memory_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(AgentMemory, memory_id)
        return row.to_dict() if row else None


def create_memory(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = AgentMemory(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_memory(memory_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(AgentMemory, memory_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_memory(memory_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(AgentMemory, memory_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def create_reminder(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = MemoryReminder(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def get_reminders_by_memory(memory_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(MemoryReminder).filter(MemoryReminder.memory_id == memory_id).all()
        return [row.to_dict() for row in rows]


def list_triggered_reminders(user_tag: str, before: datetime | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        cutoff = before or datetime.now(UTC)
        rows = (
            session.query(MemoryReminder)
            .join(AgentMemory, MemoryReminder.memory_id == AgentMemory.id)
            .filter(
                AgentMemory.user_tag == user_tag,
                AgentMemory.is_active.is_(True),
                MemoryReminder.trigger_at <= cutoff,
                MemoryReminder.triggered.is_(False),
            )
            .order_by(MemoryReminder.trigger_at.asc())
            .all()
        )
        results: list[dict] = []
        for row in rows:
            row.triggered = True
            row.trigger_count += 1
            results.append(row.to_dict())
        session.flush()
        return results


def create_message(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ConversationMessage(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def get_messages_by_session(session_id: str, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = (
            session.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.asc())
            .all()
        )
        return [row.to_dict() for row in rows]


def count_messages_by_session(session_id: str, db: Session | None = None) -> int:
    with db_session(db) as session:
        return int(
            session.query(func.count(ConversationMessage.id))
            .filter(ConversationMessage.session_id == session_id)
            .scalar()
            or 0
        )


def trim_session_messages(session_id: str, max_messages: int, db: Session | None = None) -> int:
    with db_session(db) as session:
        keep_rows = (
            session.query(ConversationMessage.id)
            .filter(ConversationMessage.session_id == session_id)
            .order_by(ConversationMessage.created_at.desc())
            .limit(max_messages)
            .all()
        )
        keep_id_set = {row.id for row in keep_rows}
        deleted = (
            session.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .filter(~ConversationMessage.id.in_(keep_id_set) if keep_id_set else True)
            .delete(synchronize_session=False)
        )
        session.flush()
        return int(deleted)


def delete_messages_by_session(session_id: str, db: Session | None = None) -> int:
    with db_session(db) as session:
        deleted = (
            session.query(ConversationMessage)
            .filter(ConversationMessage.session_id == session_id)
            .delete(synchronize_session=False)
        )
        session.flush()
        return int(deleted)


def get_active_onboarding_case(
    session_id: str,
    user_tag: str,
    intent: str = "worker_onboarding",
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = (
            session.query(OnboardingCase)
            .filter(
                OnboardingCase.session_id == session_id,
                OnboardingCase.user_tag == user_tag,
                OnboardingCase.intent == intent,
                OnboardingCase.is_active.is_(True),
            )
            .first()
        )
        return row.to_dict() if row else None


def get_latest_onboarding_case(
    session_id: str,
    user_tag: str,
    intent: str = "worker_onboarding",
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = (
            session.query(OnboardingCase)
            .filter(
                OnboardingCase.session_id == session_id,
                OnboardingCase.user_tag == user_tag,
                OnboardingCase.intent == intent,
            )
            .order_by(OnboardingCase.updated_at.desc(), OnboardingCase.id.desc())
            .first()
        )
        return row.to_dict() if row else None


def create_onboarding_case(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OnboardingCase(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_onboarding_case(
    session_id: str,
    user_tag: str,
    data: dict,
    intent: str = "worker_onboarding",
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = (
            session.query(OnboardingCase)
            .filter(
                OnboardingCase.session_id == session_id,
                OnboardingCase.user_tag == user_tag,
                OnboardingCase.intent == intent,
            )
            .first()
        )
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def upsert_onboarding_case(
    session_id: str,
    user_tag: str,
    data: dict,
    intent: str = "worker_onboarding",
    db: Session | None = None,
) -> dict:
    row = update_onboarding_case(session_id, user_tag, data, intent=intent, db=db)
    if row is not None:
        return row
    payload = {"session_id": session_id, "user_tag": user_tag, "intent": intent, **data}
    return create_onboarding_case(payload, db)


def reset_onboarding_case(
    session_id: str,
    user_tag: str,
    intent: str = "worker_onboarding",
    db: Session | None = None,
) -> int:
    with db_session(db) as session:
        deleted = (
            session.query(OnboardingCase)
            .filter(
                OnboardingCase.session_id == session_id,
                OnboardingCase.user_tag == user_tag,
                OnboardingCase.intent == intent,
            )
            .delete(synchronize_session=False)
        )
        session.flush()
        return int(deleted)


def list_sessions(db: Session | None = None) -> list[str]:
    with db_session(db) as session:
        rows = (
            session.query(ConversationMessage.session_id)
            .distinct()
            .order_by(ConversationMessage.session_id.asc())
            .all()
        )
        return [row[0] for row in rows]


def list_sessions_by_user_tag(user_tag: str, db: Session | None = None) -> list[str]:
    with db_session(db) as session:
        rows = (
            session.query(ConversationMessage.session_id)
            .filter(ConversationMessage.user_tag == user_tag)
            .distinct()
            .order_by(ConversationMessage.created_at.desc())
            .all()
        )
        return [row[0] for row in rows]


__all__ = [
    "count_messages_by_session",
    "create_memory",
    "create_message",
    "create_onboarding_case",
    "create_reminder",
    "delete_memory",
    "delete_messages_by_session",
    "get_active_onboarding_case",
    "get_latest_onboarding_case",
    "get_memory_by_id",
    "get_messages_by_session",
    "get_reminders_by_memory",
    "list_memories",
    "list_sessions",
    "list_sessions_by_user_tag",
    "list_triggered_reminders",
    "reset_onboarding_case",
    "trim_session_messages",
    "update_onboarding_case",
    "update_memory",
    "upsert_onboarding_case",
]
