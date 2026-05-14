from fastapi import APIRouter

from app.schemas.agent_memory import (
    MemoryCreate,
    MemoryListResponse,
    MemoryResponse,
    MemoryUpdate,
    ReminderCreate,
    ReminderListResponse,
    ReminderResponse,
)
from app.services import agent_memory as memory_service

router = APIRouter(prefix="/agent/memories", tags=["长期记忆"])


# ── AgentMemory ──────────────────────────────────────────────


@router.post("/", response_model=MemoryResponse, status_code=201)
def save_memory(memory_in: MemoryCreate):
    return memory_service.save_memory(memory_in)


@router.get("/", response_model=MemoryListResponse)
def recall_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
):
    return memory_service.recall_memories(
        user_tag, memory_type, category, subject, keyword, limit
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: int):
    return memory_service.get_memory(memory_id)


@router.put("/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: int, memory_in: MemoryUpdate):
    return memory_service.update_memory(memory_id, memory_in)


@router.delete("/{memory_id}")
def delete_memory(memory_id: int):
    return memory_service.delete_memory(memory_id)


# ── MemoryReminder ───────────────────────────────────────────


@router.post("/{memory_id}/reminders", response_model=ReminderResponse, status_code=201)
def create_reminder(memory_id: int, reminder_in: ReminderCreate):
    return memory_service.create_reminder(memory_id, reminder_in)


@router.get("/reminders/pending", response_model=ReminderListResponse)
def check_pending_reminders(user_tag: str):
    return memory_service.check_pending_reminders(user_tag)


@router.delete("/reminders/{reminder_id}")
def dismiss_reminder(reminder_id: int):
    return memory_service.dismiss_reminder(reminder_id)


@router.post("/cleanup")
def cleanup_expired():
    return memory_service.cleanup_expired()
