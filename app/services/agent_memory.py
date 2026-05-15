from datetime import datetime, timezone

from fastapi import HTTPException

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
        raise HTTPException(
            status_code=400,
            detail=f"无效的记忆类型: {memory_type}，可选: {', '.join(VALID_MEMORY_TYPES)}",
        )


def _validate_category(category: str) -> None:
    if category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的业务分类: {category}，可选: {', '.join(VALID_CATEGORIES)}",
        )


def _validate_source(source: str) -> None:
    if source not in VALID_SOURCES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的来源: {source}，可选: {', '.join(VALID_SOURCES)}",
        )


def save_memory(memory_in: MemoryCreate) -> MemoryResponse:
    _validate_memory_type(memory_in.memory_type)
    _validate_category(memory_in.category)
    _validate_source(memory_in.source)

    now = datetime.now(timezone.utc)

    # preference 去重：同 user_tag + subject 已存在则更新
    if memory_in.memory_type == "preference" and memory_in.user_tag:
        existing = memory_repo.get_preference_by_user_tag_and_subject(
            memory_in.user_tag, memory_in.subject
        )
        if existing:
            updated = memory_repo.update_memory(
                existing["id"],
                {"content": memory_in.content, "importance": memory_in.importance, "updated_at": now},
            )
            return MemoryResponse(**updated)

    data = memory_in.model_dump()
    data["created_at"] = now
    data["updated_at"] = now
    result = memory_repo.create_memory(data)
    return MemoryResponse(**result)


def recall_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
) -> MemoryListResponse:
    if memory_type:
        _validate_memory_type(memory_type)
    if category:
        _validate_category(category)

    if subject:
        memories = memory_repo.get_memories_by_subject(subject)
    elif keyword:
        memories = memory_repo.search_memories_by_content(user_tag, keyword)
    else:
        memories = memory_repo.get_memories_by_user_tag(
            user_tag, memory_type=memory_type, category=category
        )

    memories = memories[:limit]
    return MemoryListResponse(
        memories=[MemoryResponse(**m) for m in memories],
        total=len(memories),
    )


def get_memory(memory_id: int) -> MemoryResponse:
    m = memory_repo.get_memory_by_id(memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail=f"记忆 {memory_id} 不存在")
    return MemoryResponse(**m)


def update_memory(memory_id: int, memory_in: MemoryUpdate) -> MemoryResponse:
    m = memory_repo.get_memory_by_id(memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail=f"记忆 {memory_id} 不存在")

    data = memory_in.model_dump(exclude_unset=True)
    data["updated_at"] = datetime.now(timezone.utc)
    result = memory_repo.update_memory(memory_id, data)
    return MemoryResponse(**result)


def delete_memory(memory_id: int) -> dict:
    if not memory_repo.delete_memory(memory_id):
        raise HTTPException(status_code=404, detail=f"记忆 {memory_id} 不存在")
    return {"message": f"记忆 {memory_id} 已删除"}


def create_reminder(memory_id: int, reminder_in: ReminderCreate) -> ReminderResponse:
    m = memory_repo.get_memory_by_id(memory_id)
    if m is None:
        raise HTTPException(status_code=404, detail=f"记忆 {memory_id} 不存在")

    if reminder_in.reminder_type not in VALID_REMINDER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"无效的提醒类型: {reminder_in.reminder_type}，可选: {', '.join(VALID_REMINDER_TYPES)}",
        )

    data = reminder_in.model_dump()
    data["memory_id"] = memory_id
    data["created_at"] = datetime.now(timezone.utc)
    result = memory_repo.create_reminder(data)
    return ReminderResponse(**result)


def check_pending_reminders(user_tag: str) -> ReminderListResponse:
    now = datetime.now(timezone.utc)
    pending = memory_repo.get_pending_reminders(user_tag, now)
    results = []
    for r in pending:
        triggered = memory_repo.mark_reminder_triggered(r["id"])
        if triggered:
            results.append(ReminderResponse(**triggered))
    return ReminderListResponse(reminders=results, total=len(results))


def dismiss_reminder(reminder_id: int) -> dict:
    if not memory_repo.delete_reminder(reminder_id):
        raise HTTPException(status_code=404, detail=f"提醒 {reminder_id} 不存在")
    return {"message": f"提醒 {reminder_id} 已删除"}


def get_session_messages(session_id: str) -> ConversationMessageListResponse:
    messages = memory_repo.get_messages_by_session(session_id)
    return ConversationMessageListResponse(
        messages=[ConversationMessageResponse(**m) for m in messages],
        total=len(messages),
    )


def cleanup_expired() -> dict:
    count = memory_repo.deactivate_expired_memories()
    return {"message": f"已清理 {count} 条过期记忆"}
