"""技能目录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.capability import SkillCreate, SkillListResponse, SkillResponse, SkillUpdate
from app.services.capability import skill as service

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("/", response_model=SkillListResponse)
def list_skills(category: str | None = None, status: str | None = None, db: Session = Depends(get_db)):
    return service.list_skills(category, status, db)


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    return service.get_skill(skill_id, db)


@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(data: SkillCreate, db: Session = Depends(get_db)):
    return service.create_skill(data, db)


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(skill_id: int, data: SkillUpdate, db: Session = Depends(get_db)):
    return service.update_skill(skill_id, data, db)


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    return service.delete_skill(skill_id, db)
