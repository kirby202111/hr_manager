"""班次模板路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.staffing import (
    ShiftTemplateCreate,
    ShiftTemplateListResponse,
    ShiftTemplateResponse,
    ShiftTemplateUpdate,
)
from app.services.staffing import shift_template as service

router = APIRouter(prefix="/shift-templates", tags=["shift templates"])


@router.get("/", response_model=ShiftTemplateListResponse)
def list_shift_templates(
    code: str | None = None,
    shift_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_shift_templates(code, shift_type, status, db)


@router.get("/{shift_template_id}", response_model=ShiftTemplateResponse)
def get_shift_template(shift_template_id: int, db: Session = Depends(get_db)):
    return service.get_shift_template(shift_template_id, db)


@router.post("/", response_model=ShiftTemplateResponse, status_code=201)
def create_shift_template(data: ShiftTemplateCreate, db: Session = Depends(get_db)):
    return service.create_shift_template(data, db)


@router.put("/{shift_template_id}", response_model=ShiftTemplateResponse)
def update_shift_template(
    shift_template_id: int,
    data: ShiftTemplateUpdate,
    db: Session = Depends(get_db),
):
    return service.update_shift_template(shift_template_id, data, db)


@router.delete("/{shift_template_id}")
def delete_shift_template(shift_template_id: int, db: Session = Depends(get_db)):
    return service.delete_shift_template(shift_template_id, db)
