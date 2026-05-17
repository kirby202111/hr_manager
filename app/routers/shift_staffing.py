from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import shopfloor as s
from app.services import operational_risk as production_risk
from app.services import shift_staffing as svc
from app.services.shopfloor_support import get_record, list_response

router = APIRouter(tags=["production scheduling"])


@router.post("/shifts", status_code=201)
def create_shift(data: s.ShiftDefinitionCreate, db: Session = Depends(get_db)):
    return svc.create_shift(data, db)


@router.get("/shifts", response_model=s.ListResponse)
def list_shifts(db: Session = Depends(get_db)):
    return list_response("shift_definition", db=db)


@router.patch("/shifts/{shift_id}")
def update_shift(shift_id: int, data: s.ShiftDefinitionUpdate, db: Session = Depends(get_db)):
    return svc.update_shift(shift_id, data, db)


@router.post("/production-shift-plans", status_code=201)
def create_shift_plan(data: s.ProductionShiftPlanCreate, db: Session = Depends(get_db)):
    return svc.create_shift_plan(data, db)


@router.get("/production-shift-plans", response_model=s.ListResponse)
def list_shift_plans(db: Session = Depends(get_db)):
    return list_response("production_shift_plan", db=db)


@router.get("/production-shift-plans/{plan_id}")
def get_shift_plan(plan_id: int, db: Session = Depends(get_db)):
    return get_record("production_shift_plan", plan_id, db)


@router.post("/production-shift-plans/{plan_id}/validate", response_model=s.ValidationResult)
def validate_shift_plan(plan_id: int, db: Session = Depends(get_db)):
    return svc.validate_shift_plan(plan_id, db)


@router.post("/production-shift-plans/{plan_id}/publish")
def publish_shift_plan(plan_id: int, db: Session = Depends(get_db)):
    return svc.publish_shift_plan(plan_id, db)


@router.post("/shift-assignments", status_code=201)
def create_assignment(data: s.EmployeeShiftAssignmentCreate, db: Session = Depends(get_db)):
    return svc.create_assignment(data, db)


@router.get("/shift-assignments", response_model=s.ListResponse)
def list_assignments(db: Session = Depends(get_db)):
    return list_response("employee_shift_assignment", db=db)


@router.post("/employees/{employee_id}/workstation-eligibility-check", response_model=s.ValidationResult)
def workstation_eligibility(employee_id: int, data: s.EligibilityCheckRequest, db: Session = Depends(get_db)):
    result = svc.check_workstation_eligibility(employee_id, data.workstation_id, db)
    if data.create_risk_signal:
        for issue in result.issues:
            production_risk.create_risk_signal(
                s.ProductionRiskSignalCreate(
                    employee_id=employee_id,
                    workstation_id=data.workstation_id,
                    signal_type=issue.signal_type,
                    severity=issue.severity,
                    evidence={"message": issue.message},
                    detected_by="system",
                ),
                db,
            )
    return result
