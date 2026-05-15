from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
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
def save_memory(memory_in: MemoryCreate, db: Session = Depends(get_db)):
    return memory_service.save_memory(memory_in, db)


@router.get("/", response_model=MemoryListResponse)
def recall_memories(
    user_tag: str,
    memory_type: str | None = None,
    category: str | None = None,
    subject: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    return memory_service.recall_memories(user_tag, memory_type, category, subject, keyword, limit, db)


@router.get("/reminders/pending", response_model=ReminderListResponse)
def check_pending_reminders(user_tag: str, db: Session = Depends(get_db)):
    return memory_service.check_pending_reminders(user_tag, db)


@router.delete("/reminders/{reminder_id}")
def dismiss_reminder(reminder_id: int, db: Session = Depends(get_db)):
    return memory_service.dismiss_reminder(reminder_id, db)


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: int, db: Session = Depends(get_db)):
    return memory_service.get_memory(memory_id, db)


@router.put("/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: int, memory_in: MemoryUpdate, db: Session = Depends(get_db)):
    return memory_service.update_memory(memory_id, memory_in, db)


@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db)):
    return memory_service.delete_memory(memory_id, db)


# ── MemoryReminder ───────────────────────────────────────────


@router.post("/{memory_id}/reminders", response_model=ReminderResponse, status_code=201)
def create_reminder(memory_id: int, reminder_in: ReminderCreate, db: Session = Depends(get_db)):
    return memory_service.create_reminder(memory_id, reminder_in, db)


@router.post("/cleanup")
def cleanup_expired(db: Session = Depends(get_db)):
    return memory_service.cleanup_expired(db)
