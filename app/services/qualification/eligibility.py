"""Eligibility evaluation service."""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories.capability import skill as skill_repo
from app.repositories.capability import worker_skill as worker_skill_repo
from app.repositories.production import operation_qualification_requirement as operation_requirement_repo
from app.repositories.production import production_operation as production_operation_repo
from app.repositories.qualification import certification as certification_repo
from app.repositories.qualification import equipment_authorization as authorization_repo
from app.repositories.qualification import safety_training as training_repo
from app.repositories.qualification import worker_certification as worker_certification_repo
from app.repositories.qualification import worker_eligibility_snapshot as snapshot_repo
from app.repositories.qualification import worker_safety_training as worker_training_repo
from app.repositories.shopfloor import workstation as workstation_repo
from app.repositories.shopfloor import workstation_certification_requirement as workstation_cert_requirement_repo
from app.repositories.shopfloor import workstation_equipment_requirement as workstation_equipment_requirement_repo
from app.repositories.shopfloor import workstation_skill_requirement as workstation_skill_requirement_repo
from app.repositories.shopfloor import workstation_training_requirement as workstation_training_requirement_repo
from app.repositories.staffing import shift_plan as shift_plan_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.qualification import (
    EligibilityDetailResponse,
    WorkerEligibilityEvaluationResponse,
    WorkerEligibilitySnapshotListResponse,
    WorkerEligibilitySnapshotResponse,
)

VALID_LEVELS = {"L1": 1, "L2": 2, "L3": 3, "L4": 4, "L5": 5}
ACTIVE_OPERATION_STATUSES = {"planned", "released", "active"}
RULE_VERSION = "v1"


def _validate_level(level: str, field_name: str) -> None:
    if level not in VALID_LEVELS:
        raise ValidationError(f"{field_name} must be one of L1, L2, L3, L4, L5")


def _compare_levels(actual: str | None, expected: str, field_name: str) -> bool:
    _validate_level(expected, field_name)
    if actual is None or actual not in VALID_LEVELS:
        return False
    return VALID_LEVELS[actual] >= VALID_LEVELS[expected]


def _severity_rank(reason_code: str) -> int:
    if reason_code.startswith("WORKER_"):
        return 1
    if reason_code.startswith("CERTIFICATION_"):
        return 2
    if reason_code.startswith("TRAINING_"):
        return 3
    if reason_code.startswith("AUTH_"):
        return 4
    return 5


def _detail_to_dict(detail: EligibilityDetailResponse) -> dict:
    return detail.model_dump()


def _snapshot_to_response(row: dict) -> WorkerEligibilitySnapshotResponse:
    return WorkerEligibilitySnapshotResponse(**row)


def _build_evaluation_response(
    *,
    status: str,
    summary_reason: str,
    worker_id: int,
    workstation_id: int,
    work_date: date,
    details: list[EligibilityDetailResponse],
    checked_at: datetime,
    production_operation_id: int | None = None,
    shift_plan_id: int | None = None,
    shift_assignment_id: int | None = None,
    snapshot_id: int | None = None,
) -> WorkerEligibilityEvaluationResponse:
    return WorkerEligibilityEvaluationResponse(
        status=status,
        summary_reason=summary_reason,
        snapshot_id=snapshot_id,
        worker_id=worker_id,
        workstation_id=workstation_id,
        production_operation_id=production_operation_id,
        shift_plan_id=shift_plan_id,
        shift_assignment_id=shift_assignment_id,
        work_date=work_date,
        details=details,
        checked_at=checked_at,
    )


def _require_worker(worker_id: int, db: Session | None = None) -> dict:
    row = worker_repo.get_worker_by_id(worker_id, db)
    if row is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    return row


def _require_workstation(workstation_id: int, db: Session | None = None) -> dict:
    row = workstation_repo.get_workstation_by_id(workstation_id, db)
    if row is None:
        raise NotFoundError(f"Workstation {workstation_id} not found")
    return row


def _require_shift_plan(shift_plan_id: int, db: Session | None = None) -> dict:
    row = shift_plan_repo.get_shift_plan_by_id(shift_plan_id, db)
    if row is None:
        raise NotFoundError(f"Shift plan {shift_plan_id} not found")
    return row


def _require_operation(production_operation_id: int, db: Session | None = None) -> dict:
    row = production_operation_repo.get_production_operation_by_id(production_operation_id, db)
    if row is None:
        raise NotFoundError(f"Production operation {production_operation_id} not found")
    return row


def _require_operation_for_workstation(
    production_operation_id: int,
    workstation_id: int,
    db: Session | None = None,
) -> dict:
    row = _require_operation(production_operation_id, db)
    if row["workstation_id"] != workstation_id:
        raise ValidationError(
            "Production operation does not belong to workstation",
            error_code="operation_workstation_mismatch",
        )
    return row


def _build_detail(
    *,
    dimension: str,
    requirement_type: str,
    reason_code: str,
    message: str,
    status: str,
    severity: str,
    reference_id: int | None = None,
    reference_code: str | None = None,
    reference_name: str | None = None,
    actual_value: str | None = None,
    expected_value: str | None = None,
) -> EligibilityDetailResponse:
    return EligibilityDetailResponse(
        dimension=dimension,
        requirement_type=requirement_type,
        reference_id=reference_id,
        reference_code=reference_code,
        reference_name=reference_name,
        status=status,
        reason_code=reason_code,
        message=message,
        actual_value=actual_value,
        expected_value=expected_value,
        severity=severity,
    )


def _merge_requirement_map(requirements: list[dict], key_fn, reducer) -> list[dict]:
    merged: dict[tuple | str | int, dict] = {}
    for requirement in requirements:
        key = key_fn(requirement)
        if key in merged:
            merged[key] = reducer(merged[key], requirement)
        else:
            merged[key] = dict(requirement)
    return list(merged.values())


def _merge_workstation_and_operation_requirements(
    workstation_id: int,
    production_operation_id: int | None,
    db: Session | None = None,
) -> dict[str, list[dict]]:
    skill_requirements = workstation_skill_requirement_repo.list_workstation_skill_requirements(
        workstation_id=workstation_id,
        status="active",
        db=db,
    )
    certification_requirements = workstation_cert_requirement_repo.list_workstation_certification_requirements(
        workstation_id=workstation_id,
        status="active",
        db=db,
    )
    training_requirements = workstation_training_requirement_repo.list_workstation_training_requirements(
        workstation_id=workstation_id,
        status="active",
        db=db,
    )
    equipment_requirements = workstation_equipment_requirement_repo.list_workstation_equipment_requirements(
        workstation_id=workstation_id,
        status="active",
        db=db,
    )

    if production_operation_id is not None:
        operation_requirements = operation_requirement_repo.list_operation_qualification_requirements(
            production_operation_id=production_operation_id,
            status="active",
            db=db,
        )
        for requirement in operation_requirements:
            if requirement["requirement_type"] == "skill":
                skill_requirements.append(
                    {
                        "workstation_id": workstation_id,
                        "skill_id": requirement["reference_id"],
                        "min_proficiency_level": requirement["min_proficiency_level"] or "L1",
                        "must_be_validated": requirement["must_be_validated"],
                        "is_mandatory": requirement["is_mandatory"],
                        "status": requirement["status"],
                        "description": requirement["description"],
                    }
                )
            elif requirement["requirement_type"] == "certification":
                certification_requirements.append(
                    {
                        "workstation_id": workstation_id,
                        "certification_id": requirement["reference_id"],
                        "is_mandatory": requirement["is_mandatory"],
                        "grace_days": 0,
                        "status": requirement["status"],
                        "description": requirement["description"],
                    }
                )
            elif requirement["requirement_type"] == "training":
                training_requirements.append(
                    {
                        "workstation_id": workstation_id,
                        "safety_training_id": requirement["reference_id"],
                        "is_mandatory": requirement["is_mandatory"],
                        "min_score": requirement["min_score"],
                        "status": requirement["status"],
                        "description": requirement["description"],
                    }
                )
            else:
                equipment_requirements.append(
                    {
                        "workstation_id": workstation_id,
                        "equipment_code": requirement["equipment_code"],
                        "min_authorization_level": requirement["min_authorization_level"] or "L1",
                        "is_mandatory": requirement["is_mandatory"],
                        "status": requirement["status"],
                        "description": requirement["description"],
                    }
                )

    merged_skills = _merge_requirement_map(
        skill_requirements,
        key_fn=lambda row: row["skill_id"],
        reducer=lambda left, right: {
            **left,
            "min_proficiency_level": (
                left["min_proficiency_level"]
                if VALID_LEVELS[left["min_proficiency_level"]] >= VALID_LEVELS[right["min_proficiency_level"]]
                else right["min_proficiency_level"]
            ),
            "must_be_validated": left["must_be_validated"] or right["must_be_validated"],
            "is_mandatory": left["is_mandatory"] or right["is_mandatory"],
        },
    )
    merged_certs = _merge_requirement_map(
        certification_requirements,
        key_fn=lambda row: row["certification_id"],
        reducer=lambda left, right: {
            **left,
            "is_mandatory": left["is_mandatory"] or right["is_mandatory"],
            "grace_days": max(left.get("grace_days", 0), right.get("grace_days", 0)),
        },
    )
    merged_trainings = _merge_requirement_map(
        training_requirements,
        key_fn=lambda row: row["safety_training_id"],
        reducer=lambda left, right: {
            **left,
            "is_mandatory": left["is_mandatory"] or right["is_mandatory"],
            "min_score": max(value for value in [left.get("min_score"), right.get("min_score")] if value is not None)
            if left.get("min_score") is not None or right.get("min_score") is not None
            else None,
        },
    )
    merged_equipment = _merge_requirement_map(
        equipment_requirements,
        key_fn=lambda row: row["equipment_code"],
        reducer=lambda left, right: {
            **left,
            "min_authorization_level": (
                left["min_authorization_level"]
                if VALID_LEVELS[left["min_authorization_level"]] >= VALID_LEVELS[right["min_authorization_level"]]
                else right["min_authorization_level"]
            ),
            "is_mandatory": left["is_mandatory"] or right["is_mandatory"],
        },
    )
    return {
        "skills": merged_skills,
        "certifications": merged_certs,
        "trainings": merged_trainings,
        "equipment": merged_equipment,
    }


def _evaluate_worker_status(worker: dict, work_date: date) -> list[EligibilityDetailResponse]:
    details: list[EligibilityDetailResponse] = []
    if worker["status"] != "active":
        details.append(
            _build_detail(
                dimension="worker_status",
                requirement_type="worker_status",
                reason_code="WORKER_INACTIVE",
                message="Worker is not active",
                status="blocked",
                severity="error",
                actual_value=worker["status"],
                expected_value="active",
            )
        )
    if worker.get("hire_date") is not None and work_date < worker["hire_date"]:
        details.append(
            _build_detail(
                dimension="worker_status",
                requirement_type="worker_status",
                reason_code="WORKER_NOT_YET_HIRED",
                message="Worker has not reached hire date",
                status="blocked",
                severity="error",
                actual_value=str(work_date),
                expected_value=str(worker["hire_date"]),
            )
        )
    if worker.get("exit_date") is not None and work_date > worker["exit_date"]:
        details.append(
            _build_detail(
                dimension="worker_status",
                requirement_type="worker_status",
                reason_code="WORKER_EXITED",
                message="Worker exit date has passed",
                status="blocked",
                severity="error",
                actual_value=str(work_date),
                expected_value=str(worker["exit_date"]),
            )
        )
    return details


def _resolve_operation_for_assignment(
    shift_plan: dict,
    workstation_id: int,
    db: Session | None = None,
) -> tuple[int | None, list[EligibilityDetailResponse]]:
    if shift_plan.get("production_order_id") is None:
        return None, []
    rows = production_operation_repo.list_production_operations(
        production_order_id=shift_plan["production_order_id"],
        workstation_id=workstation_id,
        status=None,
        db=db,
    )
    if not rows:
        return None, [
            _build_detail(
                dimension="operation_context",
                requirement_type="operation_context",
                reason_code="MISSING_OPERATION_CONTEXT",
                message="Production order does not define an operation for the workstation",
                status="blocked",
                severity="error",
                expected_value="1",
                actual_value="0",
            )
        ]
    active_rows = [row for row in rows if row["status"] in ACTIVE_OPERATION_STATUSES]
    if not active_rows:
        return None, [
            _build_detail(
                dimension="operation_context",
                requirement_type="operation_context",
                reason_code="MISSING_OPERATION_CONTEXT",
                message="Production order does not define an active operation for the workstation",
                status="blocked",
                severity="error",
                expected_value="1",
                actual_value="0",
            )
        ]
    candidates = active_rows
    candidates.sort(key=lambda row: (row["sequence_number"], row["id"]))
    if len(candidates) > 1:
        return None, [
            _build_detail(
                dimension="operation_context",
                requirement_type="operation_context",
                reason_code="AMBIGUOUS_OPERATION_CONTEXT",
                message="Multiple operations matched the workstation for the production order",
                status="blocked",
                severity="error",
                actual_value=str(len(candidates)),
                expected_value="1",
            )
        ]
    return candidates[0]["id"], []


def _evaluate_skills(
    requirements: list[dict],
    worker_id: int,
    db: Session | None = None,
) -> list[EligibilityDetailResponse]:
    details: list[EligibilityDetailResponse] = []
    worker_skills = {row["skill_id"]: row for row in worker_skill_repo.list_worker_skills(worker_id=worker_id, db=db)}
    skill_map = {row["id"]: row for row in skill_repo.list_skills(db=db)}
    for requirement in requirements:
        skill = skill_map.get(requirement["skill_id"])
        skill_name = skill["name"] if skill else None
        skill_code = skill["code"] if skill else None
        worker_skill = worker_skills.get(requirement["skill_id"])
        if worker_skill is None:
            details.append(
                _build_detail(
                    dimension="skill",
                    requirement_type="skill",
                    reference_id=requirement["skill_id"],
                    reference_code=skill_code,
                    reference_name=skill_name,
                    reason_code="SKILL_MISSING",
                    message="Worker is missing required skill",
                    status="blocked",
                    severity="error",
                    expected_value=requirement["min_proficiency_level"],
                )
            )
            continue
        if not _compare_levels(
            worker_skill.get("proficiency_level"),
            requirement["min_proficiency_level"],
            "min_proficiency_level",
        ):
            details.append(
                _build_detail(
                    dimension="skill",
                    requirement_type="skill",
                    reference_id=requirement["skill_id"],
                    reference_code=skill_code,
                    reference_name=skill_name,
                    reason_code="SKILL_LEVEL_INSUFFICIENT",
                    message="Worker skill level is below requirement",
                    status="blocked",
                    severity="error",
                    actual_value=worker_skill.get("proficiency_level"),
                    expected_value=requirement["min_proficiency_level"],
                )
            )
            continue
        if requirement["must_be_validated"] and not worker_skill.get("validated", False):
            status = "blocked" if requirement["is_mandatory"] else "warning"
            details.append(
                _build_detail(
                    dimension="skill",
                    requirement_type="skill",
                    reference_id=requirement["skill_id"],
                    reference_code=skill_code,
                    reference_name=skill_name,
                    reason_code="SKILL_NOT_VALIDATED",
                    message="Worker skill is not validated",
                    status=status,
                    severity="error" if status == "blocked" else "warning",
                    actual_value="false",
                    expected_value="true",
                )
            )
    return details


def _evaluate_certifications(
    requirements: list[dict],
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> list[EligibilityDetailResponse]:
    details: list[EligibilityDetailResponse] = []
    worker_certifications = {
        row["certification_id"]: row
        for row in worker_certification_repo.list_worker_certifications(worker_id=worker_id, db=db)
    }
    cert_map = {row["id"]: row for row in certification_repo.list_certifications(db=db)}
    for requirement in requirements:
        certification = cert_map.get(requirement["certification_id"])
        cert_name = certification["name"] if certification else None
        cert_code = certification["code"] if certification else None
        worker_certification = worker_certifications.get(requirement["certification_id"])
        if worker_certification is None:
            details.append(
                _build_detail(
                    dimension="certification",
                    requirement_type="certification",
                    reference_id=requirement["certification_id"],
                    reference_code=cert_code,
                    reference_name=cert_name,
                    reason_code="CERTIFICATION_MISSING",
                    message="Worker is missing required certification",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        if worker_certification["status"] != "valid":
            details.append(
                _build_detail(
                    dimension="certification",
                    requirement_type="certification",
                    reference_id=requirement["certification_id"],
                    reference_code=cert_code,
                    reference_name=cert_name,
                    reason_code="CERTIFICATION_INVALID_STATUS",
                    message="Worker certification status is not valid",
                    status="blocked",
                    severity="error",
                    actual_value=worker_certification["status"],
                    expected_value="valid",
                )
            )
            continue
        if worker_certification["issued_at"] > work_date:
            details.append(
                _build_detail(
                    dimension="certification",
                    requirement_type="certification",
                    reference_id=requirement["certification_id"],
                    reference_code=cert_code,
                    reference_name=cert_name,
                    reason_code="CERTIFICATION_INVALID_STATUS",
                    message="Worker certification issue date is after work date",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        expires_at = worker_certification.get("expires_at")
        if expires_at is not None and work_date > expires_at:
            details.append(
                _build_detail(
                    dimension="certification",
                    requirement_type="certification",
                    reference_id=requirement["certification_id"],
                    reference_code=cert_code,
                    reference_name=cert_name,
                    reason_code="CERTIFICATION_EXPIRED",
                    message="Worker certification is expired",
                    status="blocked",
                    severity="error",
                    actual_value=str(expires_at),
                    expected_value=str(work_date),
                )
            )
            continue
        if expires_at is not None:
            days_to_expiry = (expires_at - work_date).days
            if days_to_expiry <= requirement.get("grace_days", 0):
                details.append(
                    _build_detail(
                        dimension="certification",
                        requirement_type="certification",
                        reference_id=requirement["certification_id"],
                        reference_code=cert_code,
                        reference_name=cert_name,
                        reason_code="CERTIFICATION_EXPIRING_SOON",
                        message="Worker certification is approaching expiration",
                        status="warning",
                        severity="warning",
                        actual_value=str(days_to_expiry),
                        expected_value=str(requirement.get("grace_days", 0)),
                    )
                )
    return details


def _evaluate_trainings(
    requirements: list[dict],
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> list[EligibilityDetailResponse]:
    details: list[EligibilityDetailResponse] = []
    worker_trainings = {
        row["safety_training_id"]: row
        for row in worker_training_repo.list_worker_safety_trainings(worker_id=worker_id, db=db)
    }
    training_map = {row["id"]: row for row in training_repo.list_safety_trainings(db=db)}
    for requirement in requirements:
        training = training_map.get(requirement["safety_training_id"])
        training_name = training["title"] if training else None
        training_code = training["code"] if training else None
        worker_training = worker_trainings.get(requirement["safety_training_id"])
        if worker_training is None:
            details.append(
                _build_detail(
                    dimension="training",
                    requirement_type="training",
                    reference_id=requirement["safety_training_id"],
                    reference_code=training_code,
                    reference_name=training_name,
                    reason_code="TRAINING_MISSING",
                    message="Worker is missing required training",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        if worker_training["status"] != "valid":
            details.append(
                _build_detail(
                    dimension="training",
                    requirement_type="training",
                    reference_id=requirement["safety_training_id"],
                    reference_code=training_code,
                    reference_name=training_name,
                    reason_code="TRAINING_INVALID_STATUS",
                    message="Worker training status is not valid",
                    status="blocked",
                    severity="error",
                    actual_value=worker_training["status"],
                    expected_value="valid",
                )
            )
            continue
        if worker_training["completed_at"] > work_date:
            details.append(
                _build_detail(
                    dimension="training",
                    requirement_type="training",
                    reference_id=requirement["safety_training_id"],
                    reference_code=training_code,
                    reference_name=training_name,
                    reason_code="TRAINING_INVALID_STATUS",
                    message="Worker training completion date is after work date",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        expires_at = worker_training.get("expires_at")
        if expires_at is not None and work_date > expires_at:
            details.append(
                _build_detail(
                    dimension="training",
                    requirement_type="training",
                    reference_id=requirement["safety_training_id"],
                    reference_code=training_code,
                    reference_name=training_name,
                    reason_code="TRAINING_EXPIRED",
                    message="Worker training is expired",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        if requirement.get("min_score") is not None and (
            worker_training.get("score") is None or worker_training["score"] < requirement["min_score"]
        ):
            details.append(
                _build_detail(
                    dimension="training",
                    requirement_type="training",
                    reference_id=requirement["safety_training_id"],
                    reference_code=training_code,
                    reference_name=training_name,
                    reason_code="TRAINING_SCORE_INSUFFICIENT",
                    message="Worker training score is below requirement",
                    status="blocked",
                    severity="error",
                    actual_value=str(worker_training.get("score")),
                    expected_value=str(requirement["min_score"]),
                )
            )
    return details


def _evaluate_equipment(
    requirements: list[dict],
    worker_id: int,
    work_date: date,
    db: Session | None = None,
) -> list[EligibilityDetailResponse]:
    details: list[EligibilityDetailResponse] = []
    authorizations = {
        row["equipment_code"]: row
        for row in authorization_repo.list_equipment_authorizations(worker_id=worker_id, db=db)
    }
    for requirement in requirements:
        authorization = authorizations.get(requirement["equipment_code"])
        if authorization is None:
            details.append(
                _build_detail(
                    dimension="equipment_authorization",
                    requirement_type="equipment_authorization",
                    reference_code=requirement["equipment_code"],
                    reason_code="AUTH_MISSING",
                    message="Worker is missing required equipment authorization",
                    status="blocked",
                    severity="error",
                    expected_value=requirement["min_authorization_level"],
                )
            )
            continue
        if authorization["status"] != "valid":
            details.append(
                _build_detail(
                    dimension="equipment_authorization",
                    requirement_type="equipment_authorization",
                    reference_code=requirement["equipment_code"],
                    reason_code="AUTH_INVALID_STATUS",
                    message="Equipment authorization status is not valid",
                    status="blocked",
                    severity="error",
                    actual_value=authorization["status"],
                    expected_value="valid",
                )
            )
            continue
        if authorization["issued_at"] > work_date:
            details.append(
                _build_detail(
                    dimension="equipment_authorization",
                    requirement_type="equipment_authorization",
                    reference_code=requirement["equipment_code"],
                    reason_code="AUTH_INVALID_STATUS",
                    message="Equipment authorization issue date is after work date",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        expires_at = authorization.get("expires_at")
        if expires_at is not None and work_date > expires_at:
            details.append(
                _build_detail(
                    dimension="equipment_authorization",
                    requirement_type="equipment_authorization",
                    reference_code=requirement["equipment_code"],
                    reason_code="AUTH_EXPIRED",
                    message="Equipment authorization is expired",
                    status="blocked",
                    severity="error",
                )
            )
            continue
        if not _compare_levels(
            authorization.get("authorization_level"),
            requirement["min_authorization_level"],
            "min_authorization_level",
        ):
            details.append(
                _build_detail(
                    dimension="equipment_authorization",
                    requirement_type="equipment_authorization",
                    reference_code=requirement["equipment_code"],
                    reason_code="AUTH_LEVEL_INSUFFICIENT",
                    message="Equipment authorization level is below requirement",
                    status="blocked",
                    severity="error",
                    actual_value=authorization.get("authorization_level"),
                    expected_value=requirement["min_authorization_level"],
                )
            )
    return details


def save_eligibility_snapshot(
    *,
    worker_id: int,
    workstation_id: int,
    production_operation_id: int | None,
    shift_plan_id: int | None,
    shift_assignment_id: int | None,
    work_date: date,
    status: str,
    summary_reason: str,
    details: list[EligibilityDetailResponse],
    checked_at: datetime,
    source_context: str,
    checked_by: str = "system",
    rule_version: str = RULE_VERSION,
    db: Session | None = None,
) -> dict:
    payload = {
        "worker_id": worker_id,
        "workstation_id": workstation_id,
        "production_operation_id": production_operation_id,
        "shift_plan_id": shift_plan_id,
        "shift_assignment_id": shift_assignment_id,
        "work_date": work_date,
        "status": status,
        "summary_reason": summary_reason,
        "detail_json": [_detail_to_dict(detail) for detail in details],
        "checked_at": checked_at,
        "checked_by": checked_by,
        "rule_version": rule_version,
        "source_context": source_context,
    }
    return snapshot_repo.create_worker_eligibility_snapshot(payload, db)


def evaluate_worker_eligibility(
    *,
    worker_id: int,
    workstation_id: int,
    work_date: date,
    production_operation_id: int | None = None,
    shift_plan_id: int | None = None,
    shift_assignment_id: int | None = None,
    source_context: str,
    persist_snapshot: bool = True,
    db: Session | None = None,
) -> WorkerEligibilityEvaluationResponse:
    worker = _require_worker(worker_id, db)
    _require_workstation(workstation_id, db)
    if production_operation_id is not None:
        _require_operation_for_workstation(production_operation_id, workstation_id, db)

    requirements = _merge_workstation_and_operation_requirements(workstation_id, production_operation_id, db)
    details = _evaluate_worker_status(worker, work_date)
    details.extend(_evaluate_skills(requirements["skills"], worker_id, db))
    details.extend(_evaluate_certifications(requirements["certifications"], worker_id, work_date, db))
    details.extend(_evaluate_trainings(requirements["trainings"], worker_id, work_date, db))
    details.extend(_evaluate_equipment(requirements["equipment"], worker_id, work_date, db))

    blocked = [detail for detail in details if detail.status == "blocked"]
    warnings = [detail for detail in details if detail.status == "warning"]
    if blocked:
        blocked.sort(key=lambda detail: _severity_rank(detail.reason_code))
        status = "blocked"
        summary_detail = blocked[0]
        summary_reason = summary_detail.message
    elif warnings:
        warnings.sort(key=lambda detail: _severity_rank(detail.reason_code))
        status = "warning"
        summary_detail = warnings[0]
        summary_reason = summary_detail.message
    else:
        status = "eligible"
        summary_reason = "All qualification checks passed"

    checked_at = datetime.now(UTC).replace(tzinfo=None)
    snapshot_id: int | None = None
    if persist_snapshot:
        snapshot = save_eligibility_snapshot(
            worker_id=worker_id,
            workstation_id=workstation_id,
            production_operation_id=production_operation_id,
            shift_plan_id=shift_plan_id,
            shift_assignment_id=shift_assignment_id,
            work_date=work_date,
            status=status,
            summary_reason=summary_reason,
            details=details,
            checked_at=checked_at,
            source_context=source_context,
            db=db,
        )
        snapshot_id = snapshot["id"]

    return _build_evaluation_response(
        status=status,
        summary_reason=summary_reason,
        snapshot_id=snapshot_id,
        worker_id=worker_id,
        workstation_id=workstation_id,
        production_operation_id=production_operation_id,
        shift_plan_id=shift_plan_id,
        shift_assignment_id=shift_assignment_id,
        work_date=work_date,
        details=details,
        checked_at=checked_at,
    )


def evaluate_shift_assignment_payload(
    *,
    shift_plan_id: int,
    worker_id: int,
    workstation_id: int,
    assignment_type: str,
    assigned_role: str | None = None,
    existing_shift_assignment_id: int | None = None,
    persist_snapshot: bool = True,
    db: Session | None = None,
) -> WorkerEligibilityEvaluationResponse:
    del assignment_type, assigned_role
    shift_plan = _require_shift_plan(shift_plan_id, db)
    production_operation_id, operation_details = _resolve_operation_for_assignment(shift_plan, workstation_id, db)
    if operation_details:
        checked_at = datetime.now(UTC).replace(tzinfo=None)
        summary_reason = operation_details[0].message
        snapshot_id: int | None = None
        if persist_snapshot:
            snapshot = save_eligibility_snapshot(
                worker_id=worker_id,
                workstation_id=workstation_id,
                production_operation_id=None,
                shift_plan_id=shift_plan_id,
                shift_assignment_id=existing_shift_assignment_id,
                work_date=shift_plan["work_date"],
                status="blocked",
                summary_reason=summary_reason,
                details=operation_details,
                checked_at=checked_at,
                source_context="assignment_update" if existing_shift_assignment_id is not None else "assignment_create",
                db=db,
            )
            snapshot_id = snapshot["id"]
        return _build_evaluation_response(
            status="blocked",
            summary_reason=summary_reason,
            snapshot_id=snapshot_id,
            worker_id=worker_id,
            workstation_id=workstation_id,
            production_operation_id=None,
            shift_plan_id=shift_plan_id,
            shift_assignment_id=existing_shift_assignment_id,
            work_date=shift_plan["work_date"],
            details=operation_details,
            checked_at=checked_at,
        )
    evaluation = evaluate_worker_eligibility(
        worker_id=worker_id,
        workstation_id=workstation_id,
        work_date=shift_plan["work_date"],
        production_operation_id=production_operation_id,
        shift_plan_id=shift_plan_id,
        shift_assignment_id=existing_shift_assignment_id,
        source_context="assignment_update" if existing_shift_assignment_id is not None else "assignment_create",
        persist_snapshot=persist_snapshot,
        db=db,
    )
    return _build_evaluation_response(
        status=evaluation.status,
        summary_reason=evaluation.summary_reason,
        snapshot_id=evaluation.snapshot_id,
        worker_id=evaluation.worker_id,
        workstation_id=evaluation.workstation_id,
        production_operation_id=evaluation.production_operation_id,
        shift_plan_id=evaluation.shift_plan_id,
        shift_assignment_id=evaluation.shift_assignment_id,
        work_date=evaluation.work_date,
        details=list(evaluation.details),
        checked_at=evaluation.checked_at,
    )


def link_snapshot_to_shift_assignment(
    snapshot_id: int,
    shift_assignment_id: int,
    db: Session | None = None,
) -> dict | None:
    return snapshot_repo.update_worker_eligibility_snapshot(
        snapshot_id,
        {"shift_assignment_id": shift_assignment_id},
        db,
    )


def list_worker_eligibility_snapshots(
    worker_id: int,
    workstation_id: int | None = None,
    shift_plan_id: int | None = None,
    status: str | None = None,
    work_date_from: date | None = None,
    work_date_to: date | None = None,
    db: Session | None = None,
) -> WorkerEligibilitySnapshotListResponse:
    _require_worker(worker_id, db)
    rows = snapshot_repo.list_worker_eligibility_snapshots(
        worker_id=worker_id,
        workstation_id=workstation_id,
        shift_plan_id=shift_plan_id,
        status=status,
        work_date_from=work_date_from,
        work_date_to=work_date_to,
        db=db,
    )
    return WorkerEligibilitySnapshotListResponse(
        snapshots=[_snapshot_to_response(row) for row in rows],
        total=len(rows),
    )


def get_worker_eligibility_snapshot(
    worker_id: int,
    snapshot_id: int,
    db: Session | None = None,
) -> WorkerEligibilitySnapshotResponse:
    _require_worker(worker_id, db)
    row = snapshot_repo.get_worker_eligibility_snapshot_by_id(snapshot_id, db)
    if row is None or row["worker_id"] != worker_id:
        raise NotFoundError(f"Worker eligibility snapshot {snapshot_id} not found")
    return _snapshot_to_response(row)
