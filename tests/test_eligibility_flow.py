from datetime import date, time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.errors import ValidationError
from app.models.capability import Skill, WorkerSkill
from app.models.organization import OrganizationUnit
from app.models.production import ProductionOperation, ProductionOrder
from app.models.qualification import (
    Certification,
    EquipmentAuthorization,
    SafetyTraining,
    WorkerCertification,
    WorkerEligibilitySnapshot,
    WorkerSafetyTraining,
)
from app.models.shopfloor import ProductionLine, Workstation
from app.models.staffing import ShiftAssignment, ShiftPlan, ShiftTemplate
from app.models.workforce import Worker
from app.schemas.production import (
    OperationQualificationRequirementCreate,
    OperationQualificationRequirementUpdate,
)
from app.schemas.qualification import EligibilityCheckRequest
from app.schemas.shopfloor import (
    WorkstationSkillRequirementCreate,
    WorkstationSkillRequirementUpdate,
)
from app.schemas.staffing import ShiftAssignmentCreate
from app.services.production import operation_qualification_requirement as operation_requirement_service
from app.services.qualification import eligibility as eligibility_service
from app.services.shopfloor import workstation_skill_requirement as workstation_skill_requirement_service
from app.services.staffing import shift_assignment as shift_assignment_service


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


def seed_context(session: Session) -> dict[str, int]:
    unit = OrganizationUnit(name="Plant A", code="PLANT-A", unit_type="plant", status="active")
    worker = Worker(
        worker_code="W-001",
        full_name="Ada Worker",
        employment_type="full_time",
        status="active",
        organization_unit=unit,
        hire_date=date(2024, 1, 1),
    )
    line = ProductionLine(
        organization_unit=unit,
        code="LINE-1",
        name="Line 1",
        status="active",
    )
    workstation = Workstation(
        production_line=line,
        code="WS-01",
        name="Station 1",
        workstation_type="assembly",
        risk_level="medium",
        status="active",
    )
    shift_template = ShiftTemplate(
        code="DAY",
        name="Day Shift",
        shift_type="day",
        start_time=time(8, 0),
        end_time=time(16, 0),
        allowance_rate=1.0,
        status="active",
    )
    production_order = ProductionOrder(
        order_number="PO-100",
        production_line=line,
        product_code="SKU-1",
        product_name="Widget",
        planned_quantity=100,
        priority="high",
        status="released",
    )
    shift_plan = ShiftPlan(
        production_order=production_order,
        production_line=line,
        shift_template=shift_template,
        work_date=date(2026, 5, 20),
        required_headcount=2,
        status="planned",
    )
    operation = ProductionOperation(
        production_order=production_order,
        workstation=workstation,
        operation_code="OP-10",
        operation_name="Assemble",
        sequence_number=10,
        required_headcount=1,
        status="released",
    )
    skill = Skill(name="Soldering", code="SKILL-SOLDER", category="technical", status="active")
    certification = Certification(name="IPC", code="CERT-IPC", category="quality", validity_months=24)
    training = SafetyTraining(title="ESD", code="TRN-ESD", category="safety", validity_months=12)

    session.add_all(
        [
            unit,
            worker,
            line,
            workstation,
            shift_template,
            production_order,
            shift_plan,
            operation,
            skill,
            certification,
            training,
        ]
    )
    session.flush()
    return {
        "worker_id": worker.id,
        "workstation_id": workstation.id,
        "shift_plan_id": shift_plan.id,
        "operation_id": operation.id,
        "skill_id": skill.id,
        "certification_id": certification.id,
        "training_id": training.id,
    }


def add_worker_qualifications(session: Session, context: dict[str, int], *, cert_expires_at: date) -> None:
    session.add_all(
        [
            WorkerSkill(
                worker_id=context["worker_id"],
                skill_id=context["skill_id"],
                proficiency_level="L3",
                validated=True,
            ),
            WorkerCertification(
                worker_id=context["worker_id"],
                certification_id=context["certification_id"],
                issued_at=date(2025, 1, 1),
                expires_at=cert_expires_at,
                status="valid",
            ),
            WorkerSafetyTraining(
                worker_id=context["worker_id"],
                safety_training_id=context["training_id"],
                completed_at=date(2026, 1, 1),
                expires_at=date(2026, 12, 31),
                score=95,
                status="valid",
            ),
            EquipmentAuthorization(
                worker_id=context["worker_id"],
                equipment_code="EQ-1",
                authorization_level="L3",
                issued_at=date(2025, 1, 1),
                expires_at=date(2026, 12, 31),
                status="valid",
            ),
        ]
    )
    session.flush()


def add_requirements(session: Session, context: dict[str, int], *, include_certification: bool = True) -> None:
    workstation_skill_requirement_service.create_workstation_skill_requirement(
        context["workstation_id"],
        WorkstationSkillRequirementCreate(
            skill_id=context["skill_id"],
            min_proficiency_level="L2",
            must_be_validated=True,
        ),
        session,
    )
    operation_requirement_service.create_operation_qualification_requirement(
        context["operation_id"],
        OperationQualificationRequirementCreate(
            requirement_type="training",
            reference_id=context["training_id"],
            min_score=90,
        ),
        session,
    )
    operation_requirement_service.create_operation_qualification_requirement(
        context["operation_id"],
        OperationQualificationRequirementCreate(
            requirement_type="equipment_authorization",
            equipment_code="EQ-1",
            min_authorization_level="L2",
        ),
        session,
    )
    if include_certification:
        operation_requirement_service.create_operation_qualification_requirement(
            context["operation_id"],
            OperationQualificationRequirementCreate(
                requirement_type="certification",
                reference_id=context["certification_id"],
            ),
            session,
        )


def test_requirement_crud_services() -> None:
    session = make_session()
    context = seed_context(session)

    created = workstation_skill_requirement_service.create_workstation_skill_requirement(
        context["workstation_id"],
        WorkstationSkillRequirementCreate(
            skill_id=context["skill_id"],
            min_proficiency_level="L2",
            must_be_validated=True,
        ),
        session,
    )
    listed = workstation_skill_requirement_service.list_workstation_skill_requirements(
        context["workstation_id"],
        db=session,
    )
    updated = workstation_skill_requirement_service.update_workstation_skill_requirement(
        created.id,
        WorkstationSkillRequirementUpdate(min_proficiency_level="L4"),
        session,
    )

    op_requirement = operation_requirement_service.create_operation_qualification_requirement(
        context["operation_id"],
        OperationQualificationRequirementCreate(
            requirement_type="equipment_authorization",
            equipment_code="EQ-1",
            min_authorization_level="L2",
        ),
        session,
    )
    updated_op_requirement = operation_requirement_service.update_operation_qualification_requirement(
        op_requirement.id,
        OperationQualificationRequirementUpdate(min_authorization_level="L4"),
        session,
    )
    operation_requirement_service.delete_operation_qualification_requirement(op_requirement.id, session)

    assert created.min_proficiency_level == "L2"
    assert listed.total == 1
    assert updated.min_proficiency_level == "L4"
    assert updated_op_requirement.min_authorization_level == "L4"
    assert (
        operation_requirement_service.list_operation_qualification_requirements(
            context["operation_id"],
            db=session,
        ).total
        == 0
    )


def test_evaluate_worker_eligibility_persists_warning_snapshot() -> None:
    session = make_session()
    context = seed_context(session)
    add_worker_qualifications(session, context, cert_expires_at=date(2026, 5, 22))
    add_requirements(session, context)

    request = EligibilityCheckRequest(
        worker_id=context["worker_id"],
        workstation_id=context["workstation_id"],
        production_operation_id=context["operation_id"],
        work_date=date(2026, 5, 20),
        persist_snapshot=True,
    )
    evaluation = eligibility_service.evaluate_worker_eligibility(
        worker_id=request.worker_id,
        workstation_id=request.workstation_id,
        production_operation_id=request.production_operation_id,
        work_date=request.work_date,
        persist_snapshot=request.persist_snapshot,
        source_context="manual_check",
        db=session,
    )
    snapshots = eligibility_service.list_worker_eligibility_snapshots(context["worker_id"], db=session)

    assert evaluation.status == "warning"
    assert evaluation.snapshot_id is not None
    assert any(detail.reason_code == "CERTIFICATION_EXPIRING_SOON" for detail in evaluation.details)
    assert snapshots.total == 1
    assert snapshots.snapshots[0].summary_reason == evaluation.summary_reason


def test_shift_assignment_rejects_blocked_worker() -> None:
    session = make_session()
    context = seed_context(session)
    add_worker_qualifications(session, context, cert_expires_at=date(2026, 12, 31))
    add_requirements(session, context, include_certification=True)

    session.query(WorkerCertification).delete()
    session.flush()

    try:
        shift_assignment_service.create_shift_assignment(
            ShiftAssignmentCreate(
                shift_plan_id=context["shift_plan_id"],
                worker_id=context["worker_id"],
                workstation_id=context["workstation_id"],
                assignment_type="primary",
                status="scheduled",
            ),
            session,
        )
    except ValidationError as exc:
        assert "certification" in exc.message.lower()
    else:
        raise AssertionError("Expected blocked assignment to raise ValidationError")

    assert session.query(ShiftAssignment).count() == 0
    assert session.query(WorkerEligibilitySnapshot).count() == 1
