from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee_skill import (
    EmployeeSkillCreate,
    EmployeeSkillListResponse,
    EmployeeSkillResponse,
    EmployeeSkillUpdate,
)
from app.services import employee_skill as skill_service

router = APIRouter(prefix="/employee-skills", tags=["员工技能管理"])


@router.get("/", response_model=EmployeeSkillListResponse)
def list_skills(db: Session = Depends(get_db)):
    return skill_service.list_skills(db)


@router.get("/employees/{employee_id}/skills", response_model=EmployeeSkillListResponse, tags=["员工管理"])
def list_skills_by_employee(employee_id: int, db: Session = Depends(get_db)):
    return skill_service.list_skills_by_employee(employee_id, db)


@router.get("/by-skill/{skill_name}", response_model=EmployeeSkillListResponse)
def list_employees_by_skill(skill_name: str, db: Session = Depends(get_db)):
    return skill_service.list_employees_by_skill(skill_name, db)


@router.get("/{skill_id}", response_model=EmployeeSkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    return skill_service.get_skill(skill_id, db)


@router.post("/", response_model=EmployeeSkillResponse, status_code=201)
def create_skill(skill_in: EmployeeSkillCreate, db: Session = Depends(get_db)):
    return skill_service.create_skill(skill_in, db)


@router.put("/{skill_id}", response_model=EmployeeSkillResponse)
def update_skill(skill_id: int, skill_in: EmployeeSkillUpdate, db: Session = Depends(get_db)):
    return skill_service.update_skill(skill_id, skill_in, db)


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    return skill_service.delete_skill(skill_id, db)
