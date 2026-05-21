"""Agent-facing onboarding services and lightweight session state."""

from __future__ import annotations

import json
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from app.agent.repositories import runtime as runtime_repo
from app.agent.schemas.onboarding import OnboardingCasePatch, OnboardingCaseResponse, SessionStateResponse
from app.errors import NotFoundError
from app.repositories.capability import skill as skill_repo
from app.repositories.capability import worker_skill as worker_skill_repo
from app.repositories.organization import organization_unit as organization_unit_repo
from app.repositories.qualification import certification as certification_repo
from app.repositories.qualification import equipment_authorization as authorization_repo
from app.repositories.qualification import safety_training as training_repo
from app.repositories.qualification import worker_certification as worker_certification_repo
from app.repositories.qualification import worker_safety_training as worker_training_repo
from app.repositories.shopfloor import production_line as production_line_repo
from app.repositories.shopfloor import production_team as production_team_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.workforce import worker as worker_repo
from app.services.qualification import eligibility as eligibility_service

ONBOARDING_INTENT = "worker_onboarding"
REQUIRED_FIELDS = (
    "worker_code",
    "worker_name",
    "employment_type",
    "organization_unit_id",
    "production_line_id",
    "role_title",
    "hire_date",
    "target_workstation_id",
)


def _loads_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if item is not None]


def _loads_dict(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _dump_json(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False)


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _case_to_response(row: dict, db: Session | None = None) -> OnboardingCaseResponse:
    organization_unit = (
        organization_unit_repo.get_organization_unit_by_id(row["organization_unit_id"], db)
        if row.get("organization_unit_id") is not None
        else None
    )
    production_line = (
        production_line_repo.get_production_line_by_id(row["production_line_id"], db)
        if row.get("production_line_id") is not None
        else None
    )
    production_team = (
        production_team_repo.get_production_team_by_id(row["production_team_id"], db)
        if row.get("production_team_id") is not None
        else None
    )
    workstation = (
        workstation_repo.get_workstation_by_id(row["target_workstation_id"], db)
        if row.get("target_workstation_id") is not None
        else None
    )
    payload = {
        **row,
        "organization_unit_name": organization_unit["name"] if organization_unit else None,
        "production_line_name": production_line["name"] if production_line else None,
        "production_team_name": production_team["name"] if production_team else None,
        "target_workstation_name": workstation["name"] if workstation else None,
        "collected_fields": _loads_list(row.get("collected_fields_json")),
        "missing_fields": _loads_list(row.get("missing_fields_json")),
        "pending_actions": _loads_list(row.get("pending_actions_json")),
        "completed_actions": _loads_list(row.get("completed_actions_json")),
        "risk_flags": _loads_list(row.get("risk_flags_json")),
        "latest_eligibility": _loads_dict(row.get("latest_eligibility_json")),
    }
    return OnboardingCaseResponse(**payload)


def _infer_collected_fields(payload: dict[str, Any], current: OnboardingCaseResponse | None = None) -> list[str]:
    existing = current.collected_fields if current else []
    inferred = list(existing)
    for field in REQUIRED_FIELDS:
        value = payload.get(field)
        if value not in (None, "", []):
            inferred.append(field)
    if payload.get("worker_id") is not None:
        inferred.append("worker_id")
    return _dedupe(inferred)


def _infer_missing_fields(payload: dict[str, Any], current: OnboardingCaseResponse | None = None) -> list[str]:
    if current and payload.get("missing_fields") is not None:
        return payload["missing_fields"]
    merged = {}
    if current:
        merged.update(current.model_dump())
    merged.update(payload)
    return [field for field in REQUIRED_FIELDS if merged.get(field) in (None, "", [])]


def get_active_case(
    session_id: str,
    user_tag: str,
    db: Session | None = None,
) -> OnboardingCaseResponse | None:
    row = runtime_repo.get_active_onboarding_case(session_id, user_tag, ONBOARDING_INTENT, db)
    return _case_to_response(row, db) if row else None


def get_latest_case(
    session_id: str,
    user_tag: str,
    db: Session | None = None,
) -> OnboardingCaseResponse | None:
    row = runtime_repo.get_latest_onboarding_case(session_id, user_tag, ONBOARDING_INTENT, db)
    return _case_to_response(row, db) if row else None


def upsert_case(
    session_id: str,
    user_tag: str,
    patch: OnboardingCasePatch,
    db: Session | None = None,
) -> OnboardingCaseResponse:
    current = get_active_case(session_id, user_tag, db)
    payload = patch.model_dump(exclude_unset=True)
    collected_fields = payload.pop("collected_fields", None)
    missing_fields = payload.pop("missing_fields", None)
    pending_actions = payload.pop("pending_actions", None)
    completed_actions = payload.pop("completed_actions", None)
    risk_flags = payload.pop("risk_flags", None)
    latest_eligibility = payload.pop("latest_eligibility", None)

    payload["collected_fields_json"] = _dump_json(
        _dedupe(collected_fields if collected_fields is not None else _infer_collected_fields(payload, current))
    )
    payload["missing_fields_json"] = _dump_json(
        missing_fields if missing_fields is not None else _infer_missing_fields(payload, current)
    )
    if pending_actions is not None:
        payload["pending_actions_json"] = _dump_json(_dedupe(pending_actions))
    if completed_actions is not None:
        baseline = current.completed_actions if current else []
        payload["completed_actions_json"] = _dump_json(_dedupe([*baseline, *completed_actions]))
    if risk_flags is not None:
        baseline = current.risk_flags if current else []
        payload["risk_flags_json"] = _dump_json(_dedupe([*baseline, *risk_flags]))
    if latest_eligibility is not None:
        payload["latest_eligibility_json"] = _dump_json(latest_eligibility)

    row = runtime_repo.upsert_onboarding_case(session_id, user_tag, payload, ONBOARDING_INTENT, db)
    return _case_to_response(row, db)


def mark_case_inactive(session_id: str, user_tag: str, db: Session | None = None) -> OnboardingCaseResponse | None:
    row = runtime_repo.update_onboarding_case(
        session_id,
        user_tag,
        {"is_active": False},
        intent=ONBOARDING_INTENT,
        db=db,
    )
    return _case_to_response(row, db) if row else None


def reset_case(session_id: str, user_tag: str, db: Session | None = None) -> dict[str, str]:
    runtime_repo.reset_onboarding_case(session_id, user_tag, ONBOARDING_INTENT, db)
    return {"message": f"Onboarding case for session '{session_id}' cleared"}


def get_session_state(session_id: str, user_tag: str, db: Session | None = None) -> SessionStateResponse:
    return SessionStateResponse(
        session_id=session_id,
        onboarding_case=get_latest_case(session_id, user_tag, db),
    )


def find_worker_candidates(
    worker_code: str | None = None,
    full_name: str | None = None,
    phone_number: str | None = None,
    limit: int = 5,
    db: Session | None = None,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    code_key = worker_code.strip().lower() if worker_code else None
    name_key = full_name.strip().lower() if full_name else None
    phone_key = phone_number.strip() if phone_number else None
    rows = worker_repo.list_workers(db=db)
    for row in rows:
        score = 0
        if code_key:
            current = str(row.get("worker_code", "")).lower()
            if current == code_key:
                score += 100
            elif code_key in current:
                score += 70
        if name_key:
            current = str(row.get("full_name", "")).lower()
            if current == name_key:
                score += 90
            elif name_key in current:
                score += 60
        if phone_key:
            current = str(row.get("phone_number", ""))
            if current == phone_key:
                score += 80
            elif phone_key in current:
                score += 50
        if score == 0 and any([code_key, name_key, phone_key]):
            continue
        if row.get("status") == "active":
            score += 5
        candidates.append({"score": score, **row})
    candidates.sort(key=lambda row: (-row["score"], row["id"]))
    return {"candidates": candidates[:limit], "total": len(candidates)}


def _keyword_match(row: dict[str, Any], keyword: str | None) -> bool:
    if not keyword:
        return True
    normalized = keyword.lower()
    return normalized in str(row.get("code", "")).lower() or normalized in str(row.get("name", "")).lower()


def list_shopfloor_targets(
    keyword: str | None = None,
    organization_unit_id: int | None = None,
    production_line_id: int | None = None,
    production_team_id: int | None = None,
    workstation_id: int | None = None,
    db: Session | None = None,
) -> dict[str, Any]:
    organization_units = [
        row
        for row in organization_unit_repo.list_organization_units(status="active", db=db)
        if (organization_unit_id is None or row["id"] == organization_unit_id) and _keyword_match(row, keyword)
    ]
    production_lines = [
        row
        for row in production_line_repo.list_production_lines(
            organization_unit_id=organization_unit_id,
            status="active",
            db=db,
        )
        if (production_line_id is None or row["id"] == production_line_id) and _keyword_match(row, keyword)
    ]
    production_teams = [
        row
        for row in production_team_repo.list_production_teams(
            production_line_id=production_line_id,
            status="active",
            db=db,
        )
        if (production_team_id is None or row["id"] == production_team_id) and _keyword_match(row, keyword)
    ]
    workstations = [
        row
        for row in workstation_repo.list_workstations(production_line_id=production_line_id, status="active", db=db)
        if (workstation_id is None or row["id"] == workstation_id) and _keyword_match(row, keyword)
    ]
    return {
        "organization_units": organization_units,
        "production_lines": production_lines,
        "production_teams": production_teams,
        "workstations": workstations,
    }


def get_workstation_requirements(
    workstation_id: int,
    production_operation_id: int | None = None,
    db: Session | None = None,
) -> dict[str, Any]:
    workstation = workstation_repo.get_workstation_by_id(workstation_id, db)
    if workstation is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    merged = eligibility_service._merge_workstation_and_operation_requirements(  # noqa: SLF001
        workstation_id,
        production_operation_id,
        db,
    )
    skill_map = {row["id"]: row for row in skill_repo.list_skills(db=db)}
    certification_map = {row["id"]: row for row in certification_repo.list_certifications(db=db)}
    training_map = {row["id"]: row for row in training_repo.list_safety_trainings(db=db)}
    return {
        "workstation": workstation,
        "requirements": {
            "skills": [
                {
                    **row,
                    "reference_id": row["skill_id"],
                    "reference_code": skill_map.get(row["skill_id"], {}).get("code"),
                    "reference_name": skill_map.get(row["skill_id"], {}).get("name"),
                }
                for row in merged["skills"]
            ],
            "certifications": [
                {
                    **row,
                    "reference_id": row["certification_id"],
                    "reference_code": certification_map.get(row["certification_id"], {}).get("code"),
                    "reference_name": certification_map.get(row["certification_id"], {}).get("name"),
                }
                for row in merged["certifications"]
            ],
            "trainings": [
                {
                    **row,
                    "reference_id": row["safety_training_id"],
                    "reference_code": training_map.get(row["safety_training_id"], {}).get("code"),
                    "reference_name": training_map.get(row["safety_training_id"], {}).get("title"),
                }
                for row in merged["trainings"]
            ],
            "equipment": [
                {
                    **row,
                    "reference_id": None,
                    "reference_code": row["equipment_code"],
                    "reference_name": row["equipment_code"],
                }
                for row in merged["equipment"]
            ],
        },
    }


def get_worker_qualification_summary(worker_id: int, db: Session | None = None) -> dict[str, Any]:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    skill_map = {row["id"]: row for row in skill_repo.list_skills(db=db)}
    certification_map = {row["id"]: row for row in certification_repo.list_certifications(db=db)}
    training_map = {row["id"]: row for row in training_repo.list_safety_trainings(db=db)}
    return {
        "worker": worker,
        "skills": [
            {
                **row,
                "skill_code": skill_map.get(row["skill_id"], {}).get("code"),
                "skill_name": skill_map.get(row["skill_id"], {}).get("name"),
            }
            for row in worker_skill_repo.list_worker_skills(worker_id=worker_id, db=db)
        ],
        "certifications": [
            {
                **row,
                "certification_code": certification_map.get(row["certification_id"], {}).get("code"),
                "certification_name": certification_map.get(row["certification_id"], {}).get("name"),
            }
            for row in worker_certification_repo.list_worker_certifications(worker_id=worker_id, db=db)
        ],
        "trainings": [
            {
                **row,
                "training_code": training_map.get(row["safety_training_id"], {}).get("code"),
                "training_name": training_map.get(row["safety_training_id"], {}).get("title"),
            }
            for row in worker_training_repo.list_worker_safety_trainings(worker_id=worker_id, db=db)
        ],
        "equipment_authorizations": authorization_repo.list_equipment_authorizations(worker_id=worker_id, db=db),
    }


__all__ = [
    "ONBOARDING_INTENT",
    "REQUIRED_FIELDS",
    "find_worker_candidates",
    "get_active_case",
    "get_latest_case",
    "get_session_state",
    "get_worker_qualification_summary",
    "get_workstation_requirements",
    "list_shopfloor_targets",
    "mark_case_inactive",
    "reset_case",
    "upsert_case",
]
