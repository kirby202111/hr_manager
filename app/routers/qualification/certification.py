"""证书目录路由。"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.qualification import (
    CertificationCreate,
    CertificationListResponse,
    CertificationResponse,
    CertificationUpdate,
)
from app.services.qualification import certification as service

router = APIRouter(prefix="/certifications", tags=["certifications"])


@router.get("/", response_model=CertificationListResponse)
def list_certifications(category: str | None = None, db: Session = Depends(get_db)):
    return service.list_certifications(category, db)


@router.get("/{certification_id}", response_model=CertificationResponse)
def get_certification(certification_id: int, db: Session = Depends(get_db)):
    return service.get_certification(certification_id, db)


@router.post("/", response_model=CertificationResponse, status_code=201)
def create_certification(data: CertificationCreate, db: Session = Depends(get_db)):
    return service.create_certification(data, db)


@router.put("/{certification_id}", response_model=CertificationResponse)
def update_certification(
    certification_id: int,
    data: CertificationUpdate,
    db: Session = Depends(get_db),
):
    return service.update_certification(certification_id, data, db)


@router.delete("/{certification_id}")
def delete_certification(certification_id: int, db: Session = Depends(get_db)):
    return service.delete_certification(certification_id, db)
