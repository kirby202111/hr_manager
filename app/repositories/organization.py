"""组织域仓储，负责组织单元的持久化与查询。"""

from sqlalchemy.orm import Session

from app.database import db_session
from app.models.organization import OrganizationUnit


def _apply_updates(instance: OrganizationUnit, data: dict) -> None:
    for key, value in data.items():
        if value is not None:
            setattr(instance, key, value)


def list_organization_units(
    unit_type: str | None = None,
    status: str | None = None,
    parent_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(OrganizationUnit)
        if unit_type is not None:
            query = query.filter(OrganizationUnit.unit_type == unit_type)
        if status is not None:
            query = query.filter(OrganizationUnit.status == status)
        if parent_id is not None:
            query = query.filter(OrganizationUnit.parent_id == parent_id)
        return [row.to_dict() for row in query.all()]


def get_organization_unit_by_id(organization_unit_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OrganizationUnit, organization_unit_id)
        return row.to_dict() if row else None


def get_organization_unit_by_code(code: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(OrganizationUnit).filter(OrganizationUnit.code == code).first()
        return row.to_dict() if row else None


def get_organization_unit_by_name(name: str, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.query(OrganizationUnit).filter(OrganizationUnit.name == name).first()
        return row.to_dict() if row else None


def create_organization_unit(data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        row = OrganizationUnit(**data)
        session.add(row)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def update_organization_unit(organization_unit_id: int, data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        row = session.get(OrganizationUnit, organization_unit_id)
        if row is None:
            return None
        _apply_updates(row, data)
        session.flush()
        session.refresh(row)
        return row.to_dict()


def delete_organization_unit(organization_unit_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        row = session.get(OrganizationUnit, organization_unit_id)
        if row is None:
            return False
        session.delete(row)
        session.flush()
        return True


def list_child_organization_units(parent_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(OrganizationUnit).filter(OrganizationUnit.parent_id == parent_id).all()
        return [row.to_dict() for row in rows]


def list_organization_units_by_manager(manager_worker_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        rows = session.query(OrganizationUnit).filter(OrganizationUnit.manager_worker_id == manager_worker_id).all()
        return [row.to_dict() for row in rows]
