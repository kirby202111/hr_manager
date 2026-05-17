"""生产现场域仓储，覆盖产线、工位、工单与风险信号。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.shopfloor import (
    OperationalRiskReview,
    OperationalRiskSignal,
    ProductionLine,
    ProductionOperation,
    ProductionOrder,
    ProductionTeam,
    Workstation,
    WorkstationCertificationRequirement,
    WorkstationEquipmentRequirement,
    WorkstationSkillRequirement,
)


def _apply_updates(instance: object, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_production_lines(
    organization_unit_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionLine)
        if organization_unit_id is not None:
            query = query.filter(ProductionLine.organization_unit_id == organization_unit_id)
        if code is not None:
            query = query.filter(ProductionLine.code == code)
        if status is not None:
            query = query.filter(ProductionLine.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_line_by_id(production_line_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        return row.to_dict() if row else None


def get_production_line_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionLine).filter(ProductionLine.code == code).first()
        return row.to_dict() if row else None


def create_production_line(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionLine(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_line(production_line_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_line(production_line_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionLine, production_line_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_production_teams(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionTeam)
        if production_line_id is not None:
            query = query.filter(ProductionTeam.production_line_id == production_line_id)
        if code is not None:
            query = query.filter(ProductionTeam.code == code)
        if status is not None:
            query = query.filter(ProductionTeam.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_team_by_id(production_team_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        return row.to_dict() if row else None


def get_production_team_by_code(production_line_id: int, code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionTeam).filter(
            ProductionTeam.production_line_id == production_line_id,
            ProductionTeam.code == code,
        ).first()
        return row.to_dict() if row else None


def create_production_team(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionTeam(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_team(production_team_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_team(production_team_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionTeam, production_team_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_workstations(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(Workstation)
        if production_line_id is not None:
            query = query.filter(Workstation.production_line_id == production_line_id)
        if code is not None:
            query = query.filter(Workstation.code == code)
        if status is not None:
            query = query.filter(Workstation.status == status)
        return [row.to_dict() for row in query.all()]


def get_workstation_by_id(workstation_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        return row.to_dict() if row else None


def get_workstation_by_code(production_line_id: int, code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(Workstation).filter(
            Workstation.production_line_id == production_line_id,
            Workstation.code == code,
        ).first()
        return row.to_dict() if row else None


def create_workstation(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = Workstation(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation(workstation_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation(workstation_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(Workstation, workstation_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_workstation_skill_requirements(workstation_id: int | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationSkillRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationSkillRequirement.workstation_id == workstation_id)
        return [row.to_dict() for row in query.all()]


def get_workstation_skill_requirement_by_id(
    workstation_skill_requirement_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        return row.to_dict() if row else None


def create_workstation_skill_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationSkillRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_skill_requirement(
    workstation_skill_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_skill_requirement(
    workstation_skill_requirement_id: int,
    db: Session | None = None,
) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationSkillRequirement, workstation_skill_requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_workstation_certification_requirements(
    workstation_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationCertificationRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationCertificationRequirement.workstation_id == workstation_id)
        return [row.to_dict() for row in query.all()]


def get_workstation_certification_requirement_by_id(
    workstation_certification_requirement_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(
            WorkstationCertificationRequirement,
            workstation_certification_requirement_id,
        )
        return row.to_dict() if row else None


def create_workstation_certification_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationCertificationRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_certification_requirement(
    workstation_certification_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(
            WorkstationCertificationRequirement,
            workstation_certification_requirement_id,
        )
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_certification_requirement(
    workstation_certification_requirement_id: int,
    db: Session | None = None,
) -> bool:
    with db_session(db) as session:
        row = session.get(
            WorkstationCertificationRequirement,
            workstation_certification_requirement_id,
        )
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_workstation_equipment_requirements(
    workstation_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(WorkstationEquipmentRequirement)
        if workstation_id is not None:
            query = query.filter(WorkstationEquipmentRequirement.workstation_id == workstation_id)
        return [row.to_dict() for row in query.all()]


def get_workstation_equipment_requirement_by_id(
    workstation_equipment_requirement_id: int,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        return row.to_dict() if row else None


def create_workstation_equipment_requirement(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = WorkstationEquipmentRequirement(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_workstation_equipment_requirement(
    workstation_equipment_requirement_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_workstation_equipment_requirement(
    workstation_equipment_requirement_id: int,
    db: Session | None = None,
) -> bool:
    with db_session(db) as session:
        row = session.get(WorkstationEquipmentRequirement, workstation_equipment_requirement_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_production_orders(
    production_line_id: int | None = None,
    order_number: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionOrder)
        if production_line_id is not None:
            query = query.filter(ProductionOrder.production_line_id == production_line_id)
        if order_number is not None:
            query = query.filter(ProductionOrder.order_number == order_number)
        if status is not None:
            query = query.filter(ProductionOrder.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_order_by_id(production_order_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        return row.to_dict() if row else None


def get_production_order_by_order_number(order_number: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(ProductionOrder).filter(ProductionOrder.order_number == order_number).first()
        return row.to_dict() if row else None


def create_production_order(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionOrder(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_order(production_order_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_order(production_order_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionOrder, production_order_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_production_operations(
    production_order_id: int | None = None,
    workstation_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProductionOperation)
        if production_order_id is not None:
            query = query.filter(ProductionOperation.production_order_id == production_order_id)
        if workstation_id is not None:
            query = query.filter(ProductionOperation.workstation_id == workstation_id)
        if status is not None:
            query = query.filter(ProductionOperation.status == status)
        return [row.to_dict() for row in query.all()]


def get_production_operation_by_id(production_operation_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        return row.to_dict() if row else None


def create_production_operation(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = ProductionOperation(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_production_operation(
    production_operation_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_production_operation(production_operation_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(ProductionOperation, production_operation_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_operational_risk_signals(
    production_order_id: int | None = None,
    worker_id: int | None = None,
    production_line_id: int | None = None,
    workstation_id: int | None = None,
    shift_assignment_id: int | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OperationalRiskSignal)
        if production_order_id is not None:
            query = query.filter(OperationalRiskSignal.production_order_id == production_order_id)
        if worker_id is not None:
            query = query.filter(OperationalRiskSignal.worker_id == worker_id)
        if production_line_id is not None:
            query = query.filter(OperationalRiskSignal.production_line_id == production_line_id)
        if workstation_id is not None:
            query = query.filter(OperationalRiskSignal.workstation_id == workstation_id)
        if shift_assignment_id is not None:
            query = query.filter(OperationalRiskSignal.shift_assignment_id == shift_assignment_id)
        if status is not None:
            query = query.filter(OperationalRiskSignal.status == status)
        return [row.to_dict() for row in query.all()]


def get_operational_risk_signal_by_id(operational_risk_signal_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        return row.to_dict() if row else None


def create_operational_risk_signal(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OperationalRiskSignal(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_operational_risk_signal(
    operational_risk_signal_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_operational_risk_signal(operational_risk_signal_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OperationalRiskSignal, operational_risk_signal_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_operational_risk_reviews(
    risk_signal_id: int | None = None,
    review_status: str | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OperationalRiskReview)
        if risk_signal_id is not None:
            query = query.filter(OperationalRiskReview.risk_signal_id == risk_signal_id)
        if review_status is not None:
            query = query.filter(OperationalRiskReview.review_status == review_status)
        return [row.to_dict() for row in query.all()]


def get_operational_risk_review_by_id(operational_risk_review_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        return row.to_dict() if row else None


def create_operational_risk_review(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OperationalRiskReview(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_operational_risk_review(
    operational_risk_review_id: int,
    data: dict,
    db: Session | None = None,
) -> dict | None:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_operational_risk_review(operational_risk_review_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OperationalRiskReview, operational_risk_review_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True
