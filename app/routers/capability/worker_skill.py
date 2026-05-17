"""人员技能路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.capability import WorkerSkillCreate, WorkerSkillListResponse, WorkerSkillResponse, WorkerSkillUpdate
from app.services.capability import worker_skill as service

router = APIRouter(prefix="/worker-skills", tags=["worker skills"])


@router.get("/", response_model=WorkerSkillListResponse)
def list_worker_skills(
    worker_id: int | None = None,
    skill_id: int | None = None,
    proficiency_level: str | None = None,
    validated: bool | None = None,
    db: Session = Depends(get_db),
):
    return service.list_worker_skills(worker_id, skill_id, proficiency_level, validated, db)


@router.get("/{worker_skill_id}", response_model=WorkerSkillResponse)
def get_worker_skill(worker_skill_id: int, db: Session = Depends(get_db)):
    return service.get_worker_skill(worker_skill_id, db)


@router.post("/", response_model=WorkerSkillResponse, status_code=201)
def create_worker_skill(data: WorkerSkillCreate, db: Session = Depends(get_db)):
    return service.create_worker_skill(data, db)


@router.put("/{worker_skill_id}", response_model=WorkerSkillResponse)
def update_worker_skill(worker_skill_id: int, data: WorkerSkillUpdate, db: Session = Depends(get_db)):
    return service.update_worker_skill(worker_skill_id, data, db)


@router.delete("/{worker_skill_id}")
def delete_worker_skill(worker_skill_id: int, db: Session = Depends(get_db)):
    return service.delete_worker_skill(worker_skill_id, db)
