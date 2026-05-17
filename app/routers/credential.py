from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import shopfloor as s
from app.services import credential as svc
from app.services.shopfloor_support import get_record, list_response

router = APIRouter(tags=["qualifications"])


@router.post("/certifications", status_code=201)
def create_certification(data: s.CertificationCreate, db: Session = Depends(get_db)):
    return svc.create_certification(data, db)


@router.get("/certifications", response_model=s.ListResponse)
def list_certifications(db: Session = Depends(get_db)):
    return list_response("certification", db=db)


@router.get("/certifications/expiring", response_model=s.ListResponse)
def expiring_certifications(days: int = 30, db: Session = Depends(get_db)):
    return svc.expiring_certifications(days, db)


@router.get("/certifications/{certification_id}")
def get_certification(certification_id: int, db: Session = Depends(get_db)):
    return get_record("certification", certification_id, db)


@router.patch("/certifications/{certification_id}")
def update_certification(certification_id: int, data: s.CertificationUpdate, db: Session = Depends(get_db)):
    return svc.update_certification(certification_id, data, db)


@router.post("/employee-certifications", status_code=201)
def create_employee_certification(data: s.EmployeeCertificationCreate, db: Session = Depends(get_db)):
    return svc.create_employee_certification(data, db)


@router.get("/employees/{employee_id}/certifications", response_model=s.ListResponse)
def employee_certifications(employee_id: int, db: Session = Depends(get_db)):
    return list_response("employee_certification", {"employee_id": employee_id}, db)


@router.patch("/employee-certifications/{record_id}")
def update_employee_certification(
    record_id: int,
    data: s.EmployeeCertificationUpdate,
    db: Session = Depends(get_db),
):
    return svc.update_employee_certification(record_id, data, db)


@router.post("/equipment-authorizations", status_code=201)
def create_equipment_authorization(data: s.EquipmentAuthorizationCreate, db: Session = Depends(get_db)):
    return svc.create_equipment_authorization(data, db)


@router.get("/employees/{employee_id}/equipment-authorizations", response_model=s.ListResponse)
def employee_equipment_authorizations(employee_id: int, db: Session = Depends(get_db)):
    return list_response("equipment_authorization", {"employee_id": employee_id}, db)


@router.get("/equipment-authorizations/expiring", response_model=s.ListResponse)
def expiring_authorizations(days: int = 30, db: Session = Depends(get_db)):
    return svc.expiring_authorizations(days, db)


@router.patch("/equipment-authorizations/{record_id}")
def update_equipment_authorization(
    record_id: int,
    data: s.EquipmentAuthorizationUpdate,
    db: Session = Depends(get_db),
):
    return svc.update_equipment_authorization(record_id, data, db)
