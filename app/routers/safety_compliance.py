from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import shopfloor as s
from app.services import safety_compliance as svc
from app.services.shopfloor_support import list_response

router = APIRouter(tags=["production safety"])


@router.post("/safety-trainings", status_code=201)
def create_safety_training(data: s.SafetyTrainingCreate, db: Session = Depends(get_db)):
    return svc.create_safety_training(data, db)


@router.get("/safety-trainings", response_model=s.ListResponse)
def list_safety_trainings(db: Session = Depends(get_db)):
    return list_response("safety_training", db=db)


@router.post("/employee-safety-records", status_code=201)
def create_safety_record(data: s.EmployeeSafetyRecordCreate, db: Session = Depends(get_db)):
    return svc.create_safety_record(data, db)


@router.get("/employees/{employee_id}/safety-records", response_model=s.ListResponse)
def employee_safety_records(employee_id: int, db: Session = Depends(get_db)):
    return list_response("employee_safety_record", {"employee_id": employee_id}, db)


@router.get("/employees/{employee_id}/safety-status")
def employee_safety_status(employee_id: int, db: Session = Depends(get_db)):
    return svc.safety_status(employee_id, db)


@router.get("/safety-records/expiring", response_model=s.ListResponse)
def expiring_safety_records(days: int = 30, db: Session = Depends(get_db)):
    return svc.expiring_safety_records(days, db)
