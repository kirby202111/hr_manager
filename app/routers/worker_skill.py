from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.worker_skill import WorkerSkillCreate, WorkerSkillListResponse, WorkerSkillResponse, WorkerSkillUpdate
from app.services import worker_skill as skill_service

router = APIRouter(prefix="/worker-skills", tags=["员工技能管理"])


@router.get("/", response_model=WorkerSkillListResponse)
def list_skills(db: Session = Depends(get_db)):
    return skill_service.list_skills(db)


@router.get("/workers/{worker_id}/skills", response_model=WorkerSkillListResponse, tags=["员工管理"])
def list_skills_by_worker(worker_id: int, db: Session = Depends(get_db)):
    return skill_service.list_skills_by_worker(worker_id, db)


@router.get("/by-skill/{skill_name}", response_model=WorkerSkillListResponse)
def list_workers_by_skill(skill_name: str, db: Session = Depends(get_db)):
    return skill_service.list_workers_by_skill(skill_name, db)


@router.get("/{skill_id}", response_model=WorkerSkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    return skill_service.get_skill(skill_id, db)


@router.post("/", response_model=WorkerSkillResponse, status_code=201)
def create_skill(skill_in: WorkerSkillCreate, db: Session = Depends(get_db)):
    return skill_service.create_skill(skill_in, db)


@router.put("/{skill_id}", response_model=WorkerSkillResponse)
def update_skill(skill_id: int, skill_in: WorkerSkillUpdate, db: Session = Depends(get_db)):
    return skill_service.update_skill(skill_id, skill_in, db)


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    return skill_service.delete_skill(skill_id, db)
