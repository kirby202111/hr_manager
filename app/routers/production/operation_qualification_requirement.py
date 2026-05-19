"""Operation qualification requirement router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.production import (
    OperationQualificationRequirementCreate,
    OperationQualificationRequirementListResponse,
    OperationQualificationRequirementResponse,
    OperationQualificationRequirementUpdate,
)
from app.services.production import operation_qualification_requirement as service

router = APIRouter(
    prefix="/production-operations/{production_operation_id}/qualification-requirements",
    tags=["operation qualification requirements"],
)


@router.get("/", response_model=OperationQualificationRequirementListResponse)
def list_operation_qualification_requirements(
    production_operation_id: int,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_operation_qualification_requirements(production_operation_id, status, db)


@router.get("/{requirement_id}", response_model=OperationQualificationRequirementResponse)
def get_operation_qualification_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.get_operation_qualification_requirement(requirement_id, db)


@router.post("/", response_model=OperationQualificationRequirementResponse, status_code=201)
def create_operation_qualification_requirement(
    production_operation_id: int,
    data: OperationQualificationRequirementCreate,
    db: Session = Depends(get_db),
):
    return service.create_operation_qualification_requirement(production_operation_id, data, db)


@router.put("/{requirement_id}", response_model=OperationQualificationRequirementResponse)
def update_operation_qualification_requirement(
    requirement_id: int,
    data: OperationQualificationRequirementUpdate,
    db: Session = Depends(get_db),
):
    return service.update_operation_qualification_requirement(requirement_id, data, db)


@router.delete("/{requirement_id}")
def delete_operation_qualification_requirement(requirement_id: int, db: Session = Depends(get_db)):
    return service.delete_operation_qualification_requirement(requirement_id, db)
