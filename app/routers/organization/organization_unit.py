"""组织单元路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.organization import (
    OrganizationUnitCreate,
    OrganizationUnitListResponse,
    OrganizationUnitResponse,
    OrganizationUnitUpdate,
)
from app.services.organization import organization_unit as service

router = APIRouter(prefix="/organization-units", tags=["organization units"])


@router.get("/manager/{manager_worker_id}", response_model=OrganizationUnitListResponse)
def list_by_manager(manager_worker_id: int, db: Session = Depends(get_db)):
    return service.list_organization_units_by_manager(manager_worker_id, db)


@router.get("/", response_model=OrganizationUnitListResponse)
def list_organization_units(
    unit_type: str | None = None,
    status: str | None = None,
    parent_id: int | None = None,
    db: Session = Depends(get_db),
):
    return service.list_organization_units(unit_type, status, parent_id, db)


@router.get("/{organization_unit_id}", response_model=OrganizationUnitResponse)
def get_organization_unit(organization_unit_id: int, db: Session = Depends(get_db)):
    return service.get_organization_unit(organization_unit_id, db)


@router.get("/{organization_unit_id}/children", response_model=OrganizationUnitListResponse)
def list_children(organization_unit_id: int, db: Session = Depends(get_db)):
    return service.list_child_organization_units(organization_unit_id, db)


@router.post("/", response_model=OrganizationUnitResponse, status_code=201)
def create_organization_unit(data: OrganizationUnitCreate, db: Session = Depends(get_db)):
    return service.create_organization_unit(data, db)


@router.put("/{organization_unit_id}", response_model=OrganizationUnitResponse)
def update_organization_unit(
    organization_unit_id: int,
    data: OrganizationUnitUpdate,
    db: Session = Depends(get_db),
):
    return service.update_organization_unit(organization_unit_id, data, db)


@router.delete("/{organization_unit_id}")
def delete_organization_unit(organization_unit_id: int, db: Session = Depends(get_db)):
    return service.delete_organization_unit(organization_unit_id, db)
