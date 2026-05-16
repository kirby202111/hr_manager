from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.manufacturing import (
    Certification,
    EmployeeCertification,
    EmployeeProductionProfile,
    EmployeeSafetyRecord,
    EmployeeShiftAssignment,
    EmployeeTeamAssignment,
    EquipmentAuthorization,
    ProductionLine,
    ProductionOrder,
    ProductionOrderOperation,
    ProductionRiskReview,
    ProductionRiskSignal,
    ProductionShiftPlan,
    ProductionTeam,
    SafetyTraining,
    ShiftDefinition,
    Workstation,
    WorkstationEquipmentRequirement,
    WorkstationRequiredCertification,
    WorkstationRequiredSkill,
)

Model = Any

MODEL_MAP: dict[str, Model] = {
    "production_line": ProductionLine,
    "production_team": ProductionTeam,
    "workstation": Workstation,
    "workstation_required_skill": WorkstationRequiredSkill,
    "workstation_required_certification": WorkstationRequiredCertification,
    "workstation_equipment_requirement": WorkstationEquipmentRequirement,
    "employee_team_assignment": EmployeeTeamAssignment,
    "employee_production_profile": EmployeeProductionProfile,
    "certification": Certification,
    "employee_certification": EmployeeCertification,
    "equipment_authorization": EquipmentAuthorization,
    "safety_training": SafetyTraining,
    "employee_safety_record": EmployeeSafetyRecord,
    "production_order": ProductionOrder,
    "production_order_operation": ProductionOrderOperation,
    "shift_definition": ShiftDefinition,
    "production_shift_plan": ProductionShiftPlan,
    "employee_shift_assignment": EmployeeShiftAssignment,
    "production_risk_signal": ProductionRiskSignal,
    "production_risk_review": ProductionRiskReview,
}


def list_records(kind: str, filters: dict[str, Any] | None = None, db: Session | None = None) -> list[dict]:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        query = session.query(model)
        for key, value in (filters or {}).items():
            if value is not None:
                query = query.filter(getattr(model, key) == value)
        return [row.to_dict() for row in query.all()]


def get_record(kind: str, record_id: int, db: Session | None = None) -> dict | None:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        row = session.get(model, record_id)
        return row.to_dict() if row else None


def get_one_by(kind: str, filters: dict[str, Any], db: Session | None = None) -> dict | None:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        query = session.query(model)
        for key, value in filters.items():
            query = query.filter(getattr(model, key) == value)
        row = query.first()
        return row.to_dict() if row else None


def create_record(kind: str, data: dict[str, Any], db: Session | None = None) -> dict:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        row = model(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def create_records(kind: str, rows: Iterable[dict[str, Any]], db: Session | None = None) -> list[dict]:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        instances = [model(**data) for data in rows]
        session.add_all(instances)
        session.flush()
        for row in instances:
            session.refresh(row)
        return [row.to_dict() for row in instances]


def update_record(kind: str, record_id: int, data: dict[str, Any], db: Session | None = None) -> dict | None:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        row = session.get(model, record_id)
        if row is None:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(row, key, value)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_record(kind: str, record_id: int, db: Session | None = None) -> bool:
    model = MODEL_MAP[kind]
    with db_session(db) as session:
        row = session.get(model, record_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_assignments_for_plan(plan_id: int, db: Session | None = None) -> list[dict]:
    return list_records("employee_shift_assignment", {"plan_id": plan_id}, db)


def list_employee_assignments_on_date(employee_id: int, work_date, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = (
            session.query(EmployeeShiftAssignment)
            .join(ProductionShiftPlan, EmployeeShiftAssignment.plan_id == ProductionShiftPlan.id)
            .filter(EmployeeShiftAssignment.employee_id == employee_id)
            .filter(ProductionShiftPlan.work_date == work_date)
            .filter(EmployeeShiftAssignment.status != "cancelled")
            .all()
        )
        return [row.to_dict() for row in rows]
