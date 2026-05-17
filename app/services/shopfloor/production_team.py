"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.shopfloor import production_line as production_line_repo
from app.repositories.shopfloor import production_team as production_team_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.shopfloor import (
    ProductionTeamCreate,
    ProductionTeamListResponse,
    ProductionTeamResponse,
    ProductionTeamUpdate,
)


def _to_response(row: dict) -> ProductionTeamResponse:
    return ProductionTeamResponse(**row)


def _require_row(production_team_id: int, db: Session | None = None) -> dict:
    row = production_team_repo.get_production_team_by_id(production_team_id, db)
    if row is None:
        raise NotFoundError(f"Production team {production_team_id} not found")
    return row


def list_production_teams(
    production_line_id: int | None = None,
    code: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> ProductionTeamListResponse:
    rows = production_team_repo.list_production_teams(production_line_id, code, status, db)
    return ProductionTeamListResponse(production_teams=[_to_response(row) for row in rows], total=len(rows))


def get_production_team(production_team_id: int, db: Session | None = None) -> ProductionTeamResponse:
    return _to_response(_require_row(production_team_id, db))


def create_production_team(data: ProductionTeamCreate, db: Session | None = None) -> ProductionTeamResponse:
    if production_line_repo.get_production_line_by_id(data.production_line_id, db) is None:
        raise NotFoundError(f"Production line {data.production_line_id} not found")
    if data.leader_worker_id is not None and worker_repo.get_worker_by_id(data.leader_worker_id, db) is None:
        raise NotFoundError(f"Worker {data.leader_worker_id} not found")
    existing = production_team_repo.get_production_team_by_code(data.production_line_id, data.code, db)
    if existing is not None:
        raise ConflictError("Production team code already exists on production line")
    row = production_team_repo.create_production_team(data.model_dump(), db)
    return _to_response(row)


def update_production_team(
    production_team_id: int,
    data: ProductionTeamUpdate,
    db: Session | None = None,
) -> ProductionTeamResponse:
    current = _require_row(production_team_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    if production_line_repo.get_production_line_by_id(payload["production_line_id"], db) is None:
        raise NotFoundError(f"Production line {payload['production_line_id']} not found")
    if (
        payload.get("leader_worker_id") is not None
        and worker_repo.get_worker_by_id(payload["leader_worker_id"], db) is None
    ):
        raise NotFoundError(f"Worker {payload['leader_worker_id']} not found")
    existing = production_team_repo.get_production_team_by_code(payload["production_line_id"], payload["code"], db)
    if existing is not None and existing["id"] != production_team_id:
        raise ConflictError("Production team code already exists on production line")
    row = production_team_repo.update_production_team(production_team_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Production team {production_team_id} not found")
    return _to_response(row)


def delete_production_team(production_team_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(production_team_id, db)
    production_team_repo.delete_production_team(production_team_id, db)
    return {"message": f"Production team {production_team_id} deleted"}
