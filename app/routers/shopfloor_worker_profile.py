from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import shopfloor as repo
from app.schemas import shopfloor as s
from app.services import shopfloor_worker_profile as svc
from app.services.shopfloor_support import decode_record, line_exists, list_response

router = APIRouter(tags=["employee production profiles"])


@router.get("/production-lines/{line_id}/available-employees", response_model=s.ListResponse)
def line_available_employees(line_id: int, db: Session = Depends(get_db)):
    line_exists(line_id, db)
    profiles = [decode_record(profile) for profile in repo.list_records("employee_production_profile", db=db)]
    available = [
        profile
        for profile in profiles
        if line_id in profile.get("can_support_lines", []) or profile["production_status"] == "active"
    ]
    return s.ListResponse(items=available, total=len(available))


@router.post("/employee-team-assignments", status_code=201)
def create_team_assignment(data: s.EmployeeTeamAssignmentCreate, db: Session = Depends(get_db)):
    return svc.create_team_assignment(data, db)


@router.get("/employee-team-assignments", response_model=s.ListResponse)
def list_team_assignments(db: Session = Depends(get_db)):
    return list_response("employee_team_assignment", db=db)


@router.post("/employee-production-profiles", status_code=201)
def create_profile(data: s.EmployeeProductionProfileCreate, db: Session = Depends(get_db)):
    return svc.create_profile(data, db)


@router.get("/employees/{employee_id}/production-profile")
def get_profile(employee_id: int, db: Session = Depends(get_db)):
    return svc.get_profile(employee_id, db)


@router.patch("/employees/{employee_id}/production-profile")
def update_profile(
    employee_id: int,
    data: s.EmployeeProductionProfileUpdate,
    db: Session = Depends(get_db),
):
    return svc.update_profile(employee_id, data, db)
