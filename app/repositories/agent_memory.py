from datetime import datetime

from sqlalchemy import func

from app.database import SessionLocal
from app.models.agent_memory import (
    AgentMemory as MemoryORM,
    MemoryReminder as ReminderORM,
    ConversationMessage as MessageORM,
)


# ── AgentMemory ──────────────────────────────────────────────


def create_memory(data: dict) -> dict:
    with SessionLocal() as session:
        m = MemoryORM(**data)
        session.add(m)
        session.commit()
        session.refresh(m)
        return m.to_dict()


def get_memory_by_id(memory_id: int) -> dict | None:
    with SessionLocal() as session:
        m = session.get(MemoryORM, memory_id)
        return m.to_dict() if m else None


def get_memories_by_user_tag(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    active_only: bool = True,
) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(MemoryORM).filter_by(user_tag=user_tag)
        if memory_type:
            query = query.filter_by(memory_type=memory_type)
        if category:
            query = query.filter_by(category=category)
        if active_only:
            query = query.filter_by(is_active=True)
        query = query.order_by(MemoryORM.created_at.desc())
        return [m.to_dict() for m in query.all()]


def get_memories_by_subject(subject: str, active_only: bool = True) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(MemoryORM).filter_by(subject=subject)
        if active_only:
            query = query.filter_by(is_active=True)
        return [m.to_dict() for m in query.all()]


def search_memories_by_content(
    user_tag: str, keyword: str, active_only: bool = True
) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(MemoryORM).filter_by(user_tag=user_tag)
        if active_only:
            query = query.filter_by(is_active=True)
        query = query.filter(MemoryORM.content.ilike(f"%{keyword}%"))
        query = query.order_by(MemoryORM.created_at.desc())
        return [m.to_dict() for m in query.all()]


def get_recent_memories(
    user_tag: str, limit: int = 20, active_only: bool = True
) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(MemoryORM).filter_by(user_tag=user_tag)
        if active_only:
            query = query.filter_by(is_active=True)
        query = query.order_by(MemoryORM.created_at.desc()).limit(limit)
        return [m.to_dict() for m in query.all()]


def get_important_memories(
    user_tag: str, min_importance: int = 4, active_only: bool = True
) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(MemoryORM).filter_by(user_tag=user_tag)
        if active_only:
            query = query.filter_by(is_active=True)
        query = query.filter(MemoryORM.importance >= min_importance)
        query = query.order_by(MemoryORM.created_at.desc())
        return [m.to_dict() for m in query.all()]


def get_preference_by_user_tag_and_subject(
    user_tag: str, subject: str
) -> dict | None:
    with SessionLocal() as session:
        m = (
            session.query(MemoryORM)
            .filter_by(user_tag=user_tag, subject=subject, memory_type="preference", is_active=True)
            .first()
        )
        return m.to_dict() if m else None


def update_memory(memory_id: int, data: dict) -> dict | None:
    with SessionLocal() as session:
        m = session.get(MemoryORM, memory_id)
        if m is None:
            return None
        for k, v in data.items():
            setattr(m, k, v)
        session.commit()
        session.refresh(m)
        return m.to_dict()


def deactivate_memory(memory_id: int) -> bool:
    with SessionLocal() as session:
        m = session.get(MemoryORM, memory_id)
        if m is None:
            return False
        m.is_active = False
        session.commit()
        return True


def deactivate_expired_memories() -> int:
    with SessionLocal() as session:
        count = (
            session.query(MemoryORM)
            .filter(
                MemoryORM.expires_at.isnot(None),
                MemoryORM.expires_at <= datetime.now(),
                MemoryORM.is_active == True,
            )
            .update({MemoryORM.is_active: False})
        )
        session.commit()
        return count


def delete_memory(memory_id: int) -> bool:
    with SessionLocal() as session:
        m = session.get(MemoryORM, memory_id)
        if m is None:
            return False
        session.query(ReminderORM).filter_by(memory_id=memory_id).delete()
        session.delete(m)
        session.commit()
        return True


# ── MemoryReminder ───────────────────────────────────────────


def create_reminder(data: dict) -> dict:
    with SessionLocal() as session:
        r = ReminderORM(**data)
        session.add(r)
        session.commit()
        session.refresh(r)
        return r.to_dict()


def get_reminders_by_memory(memory_id: int) -> list[dict]:
    with SessionLocal() as session:
        reminders = session.query(ReminderORM).filter_by(memory_id=memory_id).all()
        return [r.to_dict() for r in reminders]


def get_pending_reminders(user_tag: str, before: datetime) -> list[dict]:
    with SessionLocal() as session:
        reminder_ids = (
            session.query(ReminderORM.id)
            .join(MemoryORM, ReminderORM.memory_id == MemoryORM.id)
            .filter(
                MemoryORM.user_tag == user_tag,
                MemoryORM.is_active == True,
                ReminderORM.trigger_at <= before,
                ReminderORM.triggered == False,
            )
            .all()
        )
        ids = [r[0] for r in reminder_ids]
        if not ids:
            return []
        reminders = session.query(ReminderORM).filter(ReminderORM.id.in_(ids)).all()
        return [r.to_dict() for r in reminders]


def mark_reminder_triggered(reminder_id: int) -> dict | None:
    with SessionLocal() as session:
        r = session.get(ReminderORM, reminder_id)
        if r is None:
            return None
        r.triggered = True
        r.trigger_count += 1
        session.commit()
        session.refresh(r)
        return r.to_dict()


def delete_reminder(reminder_id: int) -> bool:
    with SessionLocal() as session:
        r = session.get(ReminderORM, reminder_id)
        if r is None:
            return False
        session.delete(r)
        session.commit()
        return True


# ── ConversationMessage ──────────────────────────────────────


def create_message(data: dict) -> dict:
    with SessionLocal() as session:
        msg = MessageORM(**data)
        session.add(msg)
        session.commit()
        session.refresh(msg)
        return msg.to_dict()


def get_messages_by_session(session_id: str) -> list[dict]:
    with SessionLocal() as session:
        msgs = (
            session.query(MessageORM)
            .filter_by(session_id=session_id)
            .order_by(MessageORM.created_at.asc())
            .all()
        )
        return [m.to_dict() for m in msgs]


def count_messages_by_session(session_id: str) -> int:
    with SessionLocal() as session:
        return session.query(MessageORM).filter_by(session_id=session_id).count()


def delete_messages_by_session(session_id: str) -> bool:
    with SessionLocal() as session:
        count = session.query(MessageORM).filter_by(session_id=session_id).delete()
        session.commit()
        return count > 0


def list_sessions() -> list[str]:
    with SessionLocal() as session:
        results = (
            session.query(MessageORM.session_id)
            .distinct()
            .order_by(MessageORM.session_id)
            .all()
        )
        return [r[0] for r in results]


def list_sessions_by_user_tag(user_tag: str) -> list[str]:
    with SessionLocal() as session:
        results = (
            session.query(MessageORM.session_id)
            .filter_by(user_tag=user_tag)
            .distinct()
            .order_by(MessageORM.session_id)
            .all()
        )
        return [r[0] for r in results]


def trim_session_messages(session_id: str, max_messages: int) -> None:
    with SessionLocal() as session:
        count = session.query(MessageORM).filter_by(session_id=session_id).count()
        if count <= max_messages:
            return
        keep_ids = (
            session.query(MessageORM.id)
            .filter_by(session_id=session_id)
            .order_by(MessageORM.created_at.desc())
            .limit(max_messages)
            .all()
        )
        keep_id_set = {r[0] for r in keep_ids}
        session.query(MessageORM).filter(
            MessageORM.session_id == session_id,
            MessageORM.id.notin_(keep_id_set),
        ).delete(synchronize_session=False)
        session.commit()
