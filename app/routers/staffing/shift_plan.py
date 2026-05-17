"""排班计划路由。"""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.staffing import ShiftPlanCreate, ShiftPlanListResponse, ShiftPlanResponse, ShiftPlanUpdate
from app.services.staffing import shift_plan as service

router = APIRouter(prefix="/shift-plans", tags=["shift plans"])


@router.get("/", response_model=ShiftPlanListResponse)
def list_shift_plans(
    production_line_id: int | None = None,
    shift_template_id: int | None = None,
    work_date: date | None = None,
    status: str | None = None,
    production_order_id: int | None = None,
    db: Session = Depends(get_db),
):
    return service.list_shift_plans(
        production_line_id,
        shift_template_id,
        work_date,
        status,
        production_order_id,
        db,
    )


@router.get("/{shift_plan_id}", response_model=ShiftPlanResponse)
def get_shift_plan(shift_plan_id: int, db: Session = Depends(get_db)):
    return service.get_shift_plan(shift_plan_id, db)


@router.post("/", response_model=ShiftPlanResponse, status_code=201)
def create_shift_plan(data: ShiftPlanCreate, db: Session = Depends(get_db)):
    return service.create_shift_plan(data, db)


@router.put("/{shift_plan_id}", response_model=ShiftPlanResponse)
def update_shift_plan(shift_plan_id: int, data: ShiftPlanUpdate, db: Session = Depends(get_db)):
    return service.update_shift_plan(shift_plan_id, data, db)


@router.delete("/{shift_plan_id}")
def delete_shift_plan(shift_plan_id: int, db: Session = Depends(get_db)):
    return service.delete_shift_plan(shift_plan_id, db)
