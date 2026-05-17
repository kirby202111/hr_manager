"""资质域仓储，覆盖证书、安全培训与设备授权。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.qualification import (
    Certification,
    EquipmentAuthorization,
    SafetyTraining,
    WorkerCertification,
    WorkerSafetyTraining,
)


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_certifications(category: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Certification)
        if category is not None:
            query = query.filter(Certification.category == category)
        return [row.to_dict() for row in query.all()]


def get_certification_by_id(certification_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        return row.to_dict() if row else None


def get_certification_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Certification).filter(Certification.code == code).first()
        return row.to_dict() if row else None


def create_certification(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Certification(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_certification(certification_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_certification(certification_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Certification, certification_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_worker_certifications(
    worker_id: int | None = None,
    certification_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerCertification)
        if worker_id is not None:
            query = query.filter(WorkerCertification.worker_id == worker_id)
        if certification_id is not None:
            query = query.filter(WorkerCertification.certification_id == certification_id)
        if status is not None:
            query = query.filter(WorkerCertification.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_certification_by_id(worker_certification_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        return row.to_dict() if row else None


def get_worker_certification_by_worker_and_certification(
    worker_id: int,
    certification_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkerCertification).filter(
            WorkerCertification.worker_id == worker_id,
            WorkerCertification.certification_id == certification_id,
        ).first()
        return row.to_dict() if row else None


def create_worker_certification(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerCertification(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_certification(worker_certification_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_certification(worker_certification_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerCertification, worker_certification_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_safety_trainings(category: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(SafetyTraining)
        if category is not None:
            query = query.filter(SafetyTraining.category == category)
        return [row.to_dict() for row in query.all()]


def get_safety_training_by_id(safety_training_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        return row.to_dict() if row else None


def get_safety_training_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(SafetyTraining).filter(SafetyTraining.code == code).first()
        return row.to_dict() if row else None


def create_safety_training(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = SafetyTraining(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_safety_training(safety_training_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_safety_training(safety_training_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(SafetyTraining, safety_training_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_worker_safety_trainings(
    worker_id: int | None = None,
    safety_training_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkerSafetyTraining)
        if worker_id is not None:
            query = query.filter(WorkerSafetyTraining.worker_id == worker_id)
        if safety_training_id is not None:
            query = query.filter(WorkerSafetyTraining.safety_training_id == safety_training_id)
        if status is not None:
            query = query.filter(WorkerSafetyTraining.status == status)
        return [row.to_dict() for row in query.all()]


def get_worker_safety_training_by_id(worker_safety_training_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        return row.to_dict() if row else None


def get_worker_safety_training_by_worker_and_training(
    worker_id: int,
    safety_training_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(WorkerSafetyTraining).filter(
            WorkerSafetyTraining.worker_id == worker_id,
            WorkerSafetyTraining.safety_training_id == safety_training_id,
        ).first()
        return row.to_dict() if row else None


def create_worker_safety_training(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkerSafetyTraining(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_worker_safety_training(
    worker_safety_training_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_worker_safety_training(worker_safety_training_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(WorkerSafetyTraining, worker_safety_training_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_equipment_authorizations(
    worker_id: int | None = None,
    equipment_code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(EquipmentAuthorization)
        if worker_id is not None:
            query = query.filter(EquipmentAuthorization.worker_id == worker_id)
        if equipment_code is not None:
            query = query.filter(EquipmentAuthorization.equipment_code == equipment_code)
        if status is not None:
            query = query.filter(EquipmentAuthorization.status == status)
        return [row.to_dict() for row in query.all()]


def get_equipment_authorization_by_id(equipment_authorization_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        return row.to_dict() if row else None


def get_equipment_authorization_by_worker_and_equipment(
    worker_id: int,
    equipment_code: str,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.query(EquipmentAuthorization).filter(
            EquipmentAuthorization.worker_id == worker_id,
            EquipmentAuthorization.equipment_code == equipment_code,
        ).first()
        return row.to_dict() if row else None


def create_equipment_authorization(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = EquipmentAuthorization(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_equipment_authorization(
    equipment_authorization_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_equipment_authorization(equipment_authorization_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(EquipmentAuthorization, equipment_authorization_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
