from datetime import date

from sqlalchemy.orm import Session

from app.errors import ValidationError
from app.repositories import employee_skill as employee_skill_repo
from app.repositories import leave as leave_repo
from app.repositories import manufacturing as repo
from app.schemas import manufacturing as schemas
from app.services.manufacturing_common import (
    employee_exists,
    exists,
    get_record,
    line_exists,
    require,
    stamp,
    workstation_exists,
)
from app.services.qualification import LEVEL_RANK


def create_shift(data: schemas.ShiftDefinitionCreate, db: Session | None = None) -> dict:
    require(data.shift_type, "shift_type", "shift_type")
    return repo.create_record("shift_definition", stamp(data.model_dump()), db)


def update_shift(shift_id: int, data: schemas.ShiftDefinitionUpdate, db: Session | None = None) -> dict:
    exists("shift_definition", shift_id, db)
    update = data.model_dump(exclude_unset=True)
    if "shift_type" in update:
        require(update["shift_type"], "shift_type", "shift_type")
    return repo.update_record("shift_definition", shift_id, stamp(update, update=True), db)


def create_shift_plan(data: schemas.ProductionShiftPlanCreate, db: Session | None = None) -> dict:
    line_exists(data.line_id, db)
    exists("shift_definition", data.shift_id, db)
    if data.order_id is not None:
        exists("production_order", data.order_id, db)
    require(data.status, "plan_status", "status")
    return repo.create_record("production_shift_plan", stamp(data.model_dump()), db)


def create_assignment(data: schemas.EmployeeShiftAssignmentCreate, db: Session | None = None) -> dict:
    exists("production_shift_plan", data.plan_id, db)
    employee_exists(data.employee_id, db)
    workstation_exists(data.workstation_id, db)
    require(data.assignment_type, "assignment_type", "assignment_type")
    require(data.status, "assignment_status", "status")
    return repo.create_record("employee_shift_assignment", stamp(data.model_dump()), db)


def _has_valid_certification(employee_id: int, certification_id: int, on_date: date, db: Session | None) -> bool:
    records = repo.list_records(
        "employee_certification",
        {"employee_id": employee_id, "certification_id": certification_id},
        db,
    )
    return any(
        record["status"] == "valid" and (record["expires_at"] is None or record["expires_at"] >= on_date)
        for record in records
    )


def _has_required_authorization(
    employee_id: int,
    equipment_code: str,
    required_level: str,
    on_date: date,
    db: Session | None,
) -> bool:
    records = repo.list_records(
        "equipment_authorization",
        {"employee_id": employee_id, "equipment_code": equipment_code},
        db,
    )
    required_rank = LEVEL_RANK[required_level]
    return any(
        record["status"] == "valid"
        and LEVEL_RANK.get(record["authorization_level"], 0) >= required_rank
        and (record["expires_at"] is None or record["expires_at"] >= on_date)
        for record in records
    )


def _has_skill(employee_id: int, skill_id: int, required_proficiency: str, db: Session | None) -> bool:
    records = employee_skill_repo.get_skills_by_employee(employee_id, db)
    required = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}[required_proficiency]
    ranks = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
    return any(
        record.get("skill_id") == skill_id and ranks.get(record["proficiency_level"], 0) >= required
        for record in records
    )


def _has_valid_safety(employee_id: int, on_date: date, db: Session | None) -> bool:
    records = repo.list_records("employee_safety_record", {"employee_id": employee_id, "status": "valid"}, db)
    return any(record["expires_at"] is None or record["expires_at"] >= on_date for record in records)


def check_workstation_eligibility(
    employee_id: int,
    workstation_id: int,
    db: Session | None = None,
    *,
    on_date: date | None = None,
    assignment_id: int | None = None,
) -> schemas.ValidationResult:
    employee_exists(employee_id, db)
    workstation = get_record("workstation", workstation_id, db)
    check_date = on_date or date.today()
    issues: list[schemas.ValidationIssue] = []
    profile = repo.get_one_by("employee_production_profile", {"employee_id": employee_id}, db)
    if profile is None or profile["production_status"] != "active":
        issues.append(
            schemas.ValidationIssue(
                signal_type="inactive_worker",
                severity="high",
                message="Employee production status is not active",
                employee_id=employee_id,
                workstation_id=workstation_id,
                shift_assignment_id=assignment_id,
            )
        )
    for requirement in repo.list_records("workstation_required_skill", {"workstation_id": workstation_id}, db):
        if not _has_skill(employee_id, requirement["skill_id"], requirement["required_proficiency"], db):
            issues.append(
                schemas.ValidationIssue(
                    signal_type="missing_skill",
                    severity="high",
                    message=f"Missing required skill {requirement['skill_id']}",
                    employee_id=employee_id,
                    workstation_id=workstation_id,
                    shift_assignment_id=assignment_id,
                )
            )
    requirements = repo.list_records(
        "workstation_required_certification",
        {"workstation_id": workstation_id, "required": True},
        db,
    )
    for requirement in requirements:
        if not _has_valid_certification(employee_id, requirement["certification_id"], check_date, db):
            issues.append(
                schemas.ValidationIssue(
                    signal_type="uncertified_worker_assigned",
                    severity="high",
                    message=f"Missing valid certification {requirement['certification_id']}",
                    employee_id=employee_id,
                    workstation_id=workstation_id,
                    shift_assignment_id=assignment_id,
                )
            )
    for requirement in repo.list_records("workstation_equipment_requirement", {"workstation_id": workstation_id}, db):
        has_auth = _has_required_authorization(
            employee_id,
            requirement["equipment_code"],
            requirement["required_authorization_level"],
            check_date,
            db,
        )
        if not has_auth:
            issues.append(
                schemas.ValidationIssue(
                    signal_type="missing_equipment_authorization",
                    severity="high",
                    message=f"Missing equipment authorization {requirement['equipment_code']}",
                    employee_id=employee_id,
                    workstation_id=workstation_id,
                    shift_assignment_id=assignment_id,
                )
            )
    if workstation["risk_level"] == "high" and not _has_valid_safety(employee_id, check_date, db):
        issues.append(
            schemas.ValidationIssue(
                signal_type="expired_safety_training",
                severity="high",
                message="High-risk workstation requires valid safety training",
                employee_id=employee_id,
                workstation_id=workstation_id,
                shift_assignment_id=assignment_id,
            )
        )
    return schemas.ValidationResult(valid=not issues, issues=issues)


def validate_shift_plan(plan_id: int, db: Session | None = None) -> schemas.ValidationResult:
    plan = get_record("production_shift_plan", plan_id, db)
    assignments = [row for row in repo.list_assignments_for_plan(plan_id, db) if row["status"] != "cancelled"]
    issues: list[schemas.ValidationIssue] = []
    if len(assignments) < plan["required_headcount"]:
        issues.append(
            schemas.ValidationIssue(
                signal_type="insufficient_headcount",
                severity="high",
                message="Assigned headcount is below required_headcount",
            )
        )
    for assignment in assignments:
        employee_id = assignment["employee_id"]
        leaves = leave_repo.get_approved_leaves_in_range(employee_id, plan["work_date"], plan["work_date"], db)
        if leaves:
            issues.append(
                schemas.ValidationIssue(
                    signal_type="leave_conflict",
                    severity="high",
                    message="Employee has approved leave on work date",
                    employee_id=employee_id,
                    shift_assignment_id=assignment["id"],
                )
            )
        same_day = repo.list_employee_assignments_on_date(employee_id, plan["work_date"], db)
        if len({row["id"] for row in same_day if row["id"] != assignment["id"]}) > 0:
            issues.append(
                schemas.ValidationIssue(
                    signal_type="shift_conflict",
                    severity="medium",
                    message="Employee has another shift assignment on the same date",
                    employee_id=employee_id,
                    shift_assignment_id=assignment["id"],
                )
            )
        eligibility = check_workstation_eligibility(
            employee_id,
            assignment["workstation_id"],
            db,
            on_date=plan["work_date"],
            assignment_id=assignment["id"],
        )
        issues.extend(eligibility.issues)
    return schemas.ValidationResult(valid=not issues, issues=issues)


def publish_shift_plan(plan_id: int, db: Session | None = None) -> dict:
    from app.services import production_risk

    validation = validate_shift_plan(plan_id, db)
    if not validation.valid:
        production_risk.generate_shift_plan_risks(plan_id, None)
        raise ValidationError("Shift plan has validation risks; review generated risk signals before publishing")
    return repo.update_record("production_shift_plan", plan_id, stamp({"status": "published"}, update=True), db)
