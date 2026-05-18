"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.organization import organization_unit as organization_unit_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.organization import (
    OrganizationUnitCreate,
    OrganizationUnitListResponse,
    OrganizationUnitResponse,
    OrganizationUnitUpdate,
)


# 将仓储层返回的原始数据转换为对外响应模型。
def _to_response(row: dict) -> OrganizationUnitResponse:
    return OrganizationUnitResponse(**row)


# 读取组织单元；不存在时统一抛出未找到异常。
def _require_organization_unit(organization_unit_id: int, db: Session | None = None) -> dict:
    row = organization_unit_repo.get_organization_unit_by_id(organization_unit_id, db)
    if row is None:
        raise NotFoundError(f"Organization unit {organization_unit_id} not found")
    return row


def list_organization_units(
    unit_type: str | None = None,
    status: str | None = None,
    parent_id: int | None = None,
    db: Session | None = None,
) -> OrganizationUnitListResponse:
    rows = organization_unit_repo.list_organization_units(unit_type, status, parent_id, db)
    return OrganizationUnitListResponse(organization_units=[_to_response(row) for row in rows], total=len(rows))


def get_organization_unit(organization_unit_id: int, db: Session | None = None) -> OrganizationUnitResponse:
    return _to_response(_require_organization_unit(organization_unit_id, db))


def create_organization_unit(data: OrganizationUnitCreate, db: Session | None = None) -> OrganizationUnitResponse:
    if organization_unit_repo.get_organization_unit_by_code(data.code, db) is not None:
        raise ConflictError(f"Organization unit code '{data.code}' already exists")
    if organization_unit_repo.get_organization_unit_by_name(data.name, db) is not None:
        raise ConflictError(f"Organization unit name '{data.name}' already exists")
    if data.parent_id is not None:
        _require_organization_unit(data.parent_id, db)
    if data.manager_worker_id is not None and worker_repo.get_worker_by_id(data.manager_worker_id, db) is None:
        raise NotFoundError(f"Worker {data.manager_worker_id} not found")
    row = organization_unit_repo.create_organization_unit(data.model_dump(), db)
    return _to_response(row)


def update_organization_unit(
    organization_unit_id: int,
    data: OrganizationUnitUpdate,
    db: Session | None = None,
) -> OrganizationUnitResponse:
    current = _require_organization_unit(organization_unit_id, db)
    payload = data.model_dump(exclude_unset=True)
    if "code" in payload and payload["code"] != current["code"]:
        if organization_unit_repo.get_organization_unit_by_code(payload["code"], db) is not None:
            raise ConflictError(f"Organization unit code '{payload['code']}' already exists")
    if "name" in payload and payload["name"] != current["name"]:
        if organization_unit_repo.get_organization_unit_by_name(payload["name"], db) is not None:
            raise ConflictError(f"Organization unit name '{payload['name']}' already exists")
    if payload.get("parent_id") is not None:
        _require_organization_unit(payload["parent_id"], db)
    if (
        payload.get("manager_worker_id") is not None
        and worker_repo.get_worker_by_id(payload["manager_worker_id"], db) is None
    ):
        raise NotFoundError(f"Worker {payload['manager_worker_id']} not found")
    row = organization_unit_repo.update_organization_unit(organization_unit_id, payload, db)
    if row is None:
        raise NotFoundError(f"Organization unit {organization_unit_id} not found")
    return _to_response(row)


def delete_organization_unit(organization_unit_id: int, db: Session | None = None) -> dict[str, str]:
    _require_organization_unit(organization_unit_id, db)
    organization_unit_repo.delete_organization_unit(organization_unit_id, db)
    return {"message": f"Organization unit {organization_unit_id} deleted"}


def list_child_organization_units(parent_id: int, db: Session | None = None) -> OrganizationUnitListResponse:
    _require_organization_unit(parent_id, db)
    rows = organization_unit_repo.list_child_organization_units(parent_id, db)
    return OrganizationUnitListResponse(organization_units=[_to_response(row) for row in rows], total=len(rows))


def list_organization_units_by_manager(
    manager_worker_id: int,
    db: Session | None = None,
) -> OrganizationUnitListResponse:
    if worker_repo.get_worker_by_id(manager_worker_id, db) is None:
        raise NotFoundError(f"Worker {manager_worker_id} not found")
    rows = organization_unit_repo.list_organization_units_by_manager(manager_worker_id, db)
    return OrganizationUnitListResponse(organization_units=[_to_response(row) for row in rows], total=len(rows))
