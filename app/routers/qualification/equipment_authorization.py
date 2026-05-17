"""设备授权路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    EquipmentAuthorizationCreate,
    EquipmentAuthorizationListResponse,
    EquipmentAuthorizationResponse,
    EquipmentAuthorizationUpdate,
)
from app.services.qualification import equipment_authorization as service

router = APIRouter(prefix="/equipment-authorizations", tags=["equipment authorizations"])


@router.get("/", response_model=EquipmentAuthorizationListResponse)
def list_equipment_authorizations(
    worker_id: int | None = None,
    equipment_code: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    return service.list_equipment_authorizations(worker_id, equipment_code, status, db)


@router.get("/{equipment_authorization_id}", response_model=EquipmentAuthorizationResponse)
def get_equipment_authorization(equipment_authorization_id: int, db: Session = Depends(get_db)):
    return service.get_equipment_authorization(equipment_authorization_id, db)


@router.post("/", response_model=EquipmentAuthorizationResponse, status_code=201)
def create_equipment_authorization(data: EquipmentAuthorizationCreate, db: Session = Depends(get_db)):
    return service.create_equipment_authorization(data, db)


@router.put("/{equipment_authorization_id}", response_model=EquipmentAuthorizationResponse)
def update_equipment_authorization(
    equipment_authorization_id: int,
    data: EquipmentAuthorizationUpdate,
    db: Session = Depends(get_db),
):
    return service.update_equipment_authorization(equipment_authorization_id, data, db)


@router.delete("/{equipment_authorization_id}")
def delete_equipment_authorization(equipment_authorization_id: int, db: Session = Depends(get_db)):
    return service.delete_equipment_authorization(equipment_authorization_id, db)
