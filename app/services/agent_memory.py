from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import agent_memory as memory_repo
from app.schemas.agent_memory import (
    VALID_CATEGORIES,
    VALID_MEMORY_TYPES,
    VALID_REMINDER_TYPES,
    VALID_SOURCES,
    ConversationMessageListResponse,
    ConversationMessageResponse,
    MemoryCreate,
    MemoryListResponse,
    MemoryResponse,
    MemoryUpdate,
    ReminderCreate,
    ReminderListResponse,
    ReminderResponse,
)


def _validate_memory_type(memory_type: str) -> None:
    if memory_type not in VALID_MEMORY_TYPES:
        raise ValidationError(f"无效的记忆类型: {memory_type}，可选值: {', '.join(VALID_MEMORY_TYPES)}")


def _validate_category(category: str) -> None:
    if category not in VALID_CATEGORIES:
        raise ValidationError(f"无效的业务分类: {category}，可选值: {', '.join(VALID_CATEGORIES)}")


def _validate_source(source: str) -> None:
    if source not in VALID_SOURCES:
        raise ValidationError(f"无效的来源: {source}，可选值: {', '.join(VALID_SOURCES)}")


def save_memory(memory_in: MemoryCreate, db: Session | None = None) -> MemoryResponse:
    _validate_memory_type(memory_in.memory_type)
    _validate_category(memory_in.category)
    _validate_source(memory_in.source)

    now = datetime.now(UTC)
    if memory_in.memory_type == "preference" and memory_in.user_tag:
        existing = memory_repo.get_preference_by_user_tag_and_subject(memory_in.user_tag, memory_in.subject, db)
        if existing:
            updated = memory_repo.update_memory(
                existing["id"],
                {"content": memory_in.content, "importance": memory_in.importance, "updated_at": now},
                db,
            )
            return MemoryResponse(**updated)

    data = memory_in.model_dump()
    data["created_at"] = now
    data["updated_at"] = now
    result = memory_repo.create_memory(data, db)
    return MemoryResponse(**result)


def recall_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
    db: Session | None = None,
) -> MemoryListResponse:
    if memory_type:
        _validate_memory_type(memory_type)
    if category:
        _validate_category(category)

    if subject:
        memories = memory_repo.get_memories_by_subject(subject, db=db)
    elif keyword:
        memories = memory_repo.search_memories_by_content(user_tag, keyword, db=db)
    else:
        memories = memory_repo.get_memories_by_user_tag(user_tag, memory_type=memory_type, category=category, db=db)

    memories = memories[:limit]
    return MemoryListResponse(memories=[MemoryResponse(**m) for m in memories], total=len(memories))


def get_memory(memory_id: int, db: Session | None = None) -> MemoryResponse:
    memory = memory_repo.get_memory_by_id(memory_id, db)
    if memory is None:
        raise NotFoundError(f"记忆 {memory_id} 不存在")
    return MemoryResponse(**memory)


def update_memory(memory_id: int, memory_in: MemoryUpdate, db: Session | None = None) -> MemoryResponse:
    if memory_repo.get_memory_by_id(memory_id, db) is None:
        raise NotFoundError(f"记忆 {memory_id} 不存在")
    data = memory_in.model_dump(exclude_unset=True)
    data["updated_at"] = datetime.now(UTC)
    result = memory_repo.update_memory(memory_id, data, db)
    return MemoryResponse(**result)


def delete_memory(memory_id: int, db: Session | None = None) -> dict:
    if not memory_repo.delete_memory(memory_id, db):
        raise NotFoundError(f"记忆 {memory_id} 不存在")
    return {"message": f"记忆 {memory_id} 已删除"}


def create_reminder(memory_id: int, reminder_in: ReminderCreate, db: Session | None = None) -> ReminderResponse:
    if memory_repo.get_memory_by_id(memory_id, db) is None:
        raise NotFoundError(f"记忆 {memory_id} 不存在")
    if reminder_in.reminder_type not in VALID_REMINDER_TYPES:
        raise ValidationError(f"无效的提醒类型: {reminder_in.reminder_type}，可选值: {', '.join(VALID_REMINDER_TYPES)}")
    data = reminder_in.model_dump()
    data["memory_id"] = memory_id
    data["created_at"] = datetime.now(UTC)
    result = memory_repo.create_reminder(data, db)
    return ReminderResponse(**result)


def check_pending_reminders(user_tag: str, db: Session | None = None) -> ReminderListResponse:
    now = datetime.now(UTC)
    pending = memory_repo.get_pending_reminders(user_tag, now, db)
    results = []
    for reminder in pending:
        triggered = memory_repo.mark_reminder_triggered(reminder["id"], db)
        if triggered:
            results.append(ReminderResponse(**triggered))
    return ReminderListResponse(reminders=results, total=len(results))


def dismiss_reminder(reminder_id: int, db: Session | None = None) -> dict:
    if not memory_repo.delete_reminder(reminder_id, db):
        raise NotFoundError(f"提醒 {reminder_id} 不存在")
    return {"message": f"提醒 {reminder_id} 已删除"}


def get_session_messages(session_id: str, db: Session | None = None) -> ConversationMessageListResponse:
    messages = memory_repo.get_messages_by_session(session_id, db)
    return ConversationMessageListResponse(
        messages=[ConversationMessageResponse(**m) for m in messages],
        total=len(messages),
    )


def cleanup_expired(db: Session | None = None) -> dict:
    count = memory_repo.deactivate_expired_memories(db)
    return {"message": f"已清理 {count} 条过期记忆"}
