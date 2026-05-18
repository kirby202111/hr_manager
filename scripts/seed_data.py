"""Seed the database with coherent sample data for the current schema."""

from __future__ import annotations

import os
import random
import sys
from datetime import date, time, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, SessionLocal
from app.models import (
    AttendanceRecord,
    Certification,
    EquipmentAuthorization,
    LeaveRequest,
    OperationalRiskReview,
    OperationalRiskSignal,
    OrganizationUnit,
    PayrollRecord,
    ProductionLine,
    ProductionOperation,
    ProductionOrder,
    ProductionTeam,
    Project,
    ProjectMember,
    ProjectSkillRequirement,
    ProjectTimesheetEntry,
    SafetyTraining,
    ShiftAssignment,
    ShiftPlan,
    ShiftTemplate,
    Skill,
    Worker,
    WorkerAssignment,
    WorkerCertification,
    WorkerSafetyTraining,
    WorkerSkill,
    Workstation,
    WorkstationCertificationRequirement,
    WorkstationEquipmentRequirement,
    WorkstationSkillRequirement,
)
from app.schema import initialize_database

TODAY = date(2026, 5, 18)


def reset_database(session) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


def seed_organization(session) -> dict[str, OrganizationUnit]:
    units = [
        OrganizationUnit(code="PLANT-SZ", name="Shenzhen Plant", unit_type="plant", status="active"),
        OrganizationUnit(code="MFG", name="Manufacturing", unit_type="department", status="active", parent_id=1),
        OrganizationUnit(code="QA", name="Quality", unit_type="department", status="active", parent_id=1),
        OrganizationUnit(code="ENG", name="Engineering", unit_type="department", status="active", parent_id=1),
        OrganizationUnit(code="WH", name="Warehouse", unit_type="department", status="active", parent_id=1),
    ]
    session.add_all(units)
    session.flush()
    return {unit.code: unit for unit in units}


def seed_skills(session) -> dict[str, Skill]:
    skills = [
        Skill(code="SMT", name="SMT Operation", category="manufacturing", status="active"),
        Skill(code="ASSY", name="Product Assembly", category="manufacturing", status="active"),
        Skill(code="TEST", name="Functional Testing", category="quality", status="active"),
        Skill(code="IPC610", name="IPC-A-610 Inspection", category="quality", status="active"),
        Skill(code="PLC", name="PLC Programming", category="engineering", status="active"),
        Skill(code="MES", name="MES Configuration", category="engineering", status="active"),
        Skill(code="FORK", name="Forklift Operation", category="warehouse", status="active"),
        Skill(code="WMS", name="Warehouse System", category="warehouse", status="active"),
    ]
    session.add_all(skills)
    session.flush()
    return {skill.code: skill for skill in skills}


def seed_certifications(session) -> dict[str, Certification]:
    certifications = [
        Certification(
            code="CERT-IPC",
            name="IPC Specialist",
            category="quality",
            validity_months=24,
            issuing_authority="IPC",
        ),
        Certification(
            code="CERT-EHS",
            name="EHS Operator",
            category="safety",
            validity_months=12,
            issuing_authority="Plant Safety Office",
        ),
        Certification(
            code="CERT-FLT",
            name="Forklift License",
            category="equipment",
            validity_months=36,
            issuing_authority="Logistics Authority",
        ),
    ]
    session.add_all(certifications)
    session.flush()
    return {cert.code: cert for cert in certifications}


def seed_safety_trainings(
    session, skills: dict[str, Skill], certifications: dict[str, Certification]
) -> dict[str, SafetyTraining]:
    trainings = [
        SafetyTraining(
            code="SAFE-LOCKOUT",
            title="Lockout Tagout",
            category="safety",
            required_hours=4.0,
            validity_months=12,
        ),
        SafetyTraining(
            code="SAFE-ESD",
            title="ESD Handling",
            category="quality",
            skill_id=skills["SMT"].id,
            required_hours=2.0,
            validity_months=12,
        ),
        SafetyTraining(
            code="SAFE-FLT",
            title="Forklift Refresher",
            category="equipment",
            required_certification_id=certifications["CERT-FLT"].id,
            required_hours=3.0,
            validity_months=12,
        ),
    ]
    session.add_all(trainings)
    session.flush()
    return {training.code: training for training in trainings}


def seed_workers(session, units: dict[str, OrganizationUnit]) -> dict[str, Worker]:
    workers = [
        Worker(
            worker_code="W001",
            full_name="Liu Mei",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=820),
            base_salary=7800,
        ),
        Worker(
            worker_code="W002",
            full_name="Chen Hao",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=640),
            base_salary=7200,
        ),
        Worker(
            worker_code="W003",
            full_name="Zhang Yu",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["QA"].id,
            hire_date=TODAY - timedelta(days=900),
            base_salary=8600,
        ),
        Worker(
            worker_code="W004",
            full_name="Lin Qiao",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["ENG"].id,
            hire_date=TODAY - timedelta(days=1100),
            base_salary=9800,
        ),
        Worker(
            worker_code="W005",
            full_name="Tang Wei",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["WH"].id,
            hire_date=TODAY - timedelta(days=500),
            base_salary=6800,
        ),
        Worker(
            worker_code="W006",
            full_name="Sun Jia",
            employment_type="contractor",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=230),
            base_salary=6500,
        ),
    ]
    session.add_all(workers)
    session.flush()

    units["PLANT-SZ"].manager_worker_id = workers[3].id
    units["MFG"].manager_worker_id = workers[0].id
    units["QA"].manager_worker_id = workers[2].id
    units["ENG"].manager_worker_id = workers[3].id
    units["WH"].manager_worker_id = workers[4].id
    session.flush()

    return {worker.worker_code: worker for worker in workers}


def seed_worker_profiles(
    session,
    workers: dict[str, Worker],
    skills: dict[str, Skill],
    certifications: dict[str, Certification],
    trainings: dict[str, SafetyTraining],
) -> None:
    worker_skills = [
        WorkerSkill(
            worker_id=workers["W001"].id,
            skill_id=skills["SMT"].id,
            proficiency_level="advanced",
            years_of_experience=4.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W001"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="advanced",
            years_of_experience=5.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W002"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="intermediate",
            years_of_experience=2.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W002"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="intermediate",
            years_of_experience=1.5,
            validated=False,
        ),
        WorkerSkill(
            worker_id=workers["W003"].id,
            skill_id=skills["IPC610"].id,
            proficiency_level="expert",
            years_of_experience=6.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W003"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="advanced",
            years_of_experience=4.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W004"].id,
            skill_id=skills["PLC"].id,
            proficiency_level="advanced",
            years_of_experience=7.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W004"].id,
            skill_id=skills["MES"].id,
            proficiency_level="advanced",
            years_of_experience=5.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W005"].id,
            skill_id=skills["FORK"].id,
            proficiency_level="advanced",
            years_of_experience=3.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W005"].id,
            skill_id=skills["WMS"].id,
            proficiency_level="intermediate",
            years_of_experience=3.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W006"].id,
            skill_id=skills["SMT"].id,
            proficiency_level="beginner",
            years_of_experience=0.8,
            validated=False,
        ),
    ]
    session.add_all(worker_skills)

    worker_certifications = [
        WorkerCertification(
            worker_id=workers["W003"].id,
            certification_id=certifications["CERT-IPC"].id,
            certification_number="IPC-2024-003",
            issued_at=TODAY - timedelta(days=280),
            expires_at=TODAY + timedelta(days=450),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W005"].id,
            certification_id=certifications["CERT-FLT"].id,
            certification_number="FLT-2025-014",
            issued_at=TODAY - timedelta(days=150),
            expires_at=TODAY + timedelta(days=900),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W001"].id,
            certification_id=certifications["CERT-EHS"].id,
            certification_number="EHS-2025-102",
            issued_at=TODAY - timedelta(days=120),
            expires_at=TODAY + timedelta(days=240),
            status="valid",
        ),
    ]
    session.add_all(worker_certifications)

    worker_training_records = [
        WorkerSafetyTraining(
            worker_id=workers["W001"].id,
            safety_training_id=trainings["SAFE-LOCKOUT"].id,
            completed_at=TODAY - timedelta(days=45),
            expires_at=TODAY + timedelta(days=320),
            score=92,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W003"].id,
            safety_training_id=trainings["SAFE-ESD"].id,
            completed_at=TODAY - timedelta(days=60),
            expires_at=TODAY + timedelta(days=300),
            score=96,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W005"].id,
            safety_training_id=trainings["SAFE-FLT"].id,
            completed_at=TODAY - timedelta(days=30),
            expires_at=TODAY + timedelta(days=330),
            score=88,
            status="valid",
        ),
    ]
    session.add_all(worker_training_records)

    equipment_authorizations = [
        EquipmentAuthorization(
            worker_id=workers["W001"].id,
            equipment_code="SMT-LINE-01",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=180),
            expires_at=TODAY + timedelta(days=365),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W005"].id,
            equipment_code="FORKLIFT-A",
            authorization_level="advanced",
            issued_at=TODAY - timedelta(days=150),
            expires_at=TODAY + timedelta(days=800),
            status="valid",
        ),
    ]
    session.add_all(equipment_authorizations)
    session.flush()


def seed_shopfloor(
    session,
    units: dict[str, OrganizationUnit],
    workers: dict[str, Worker],
    skills: dict[str, Skill],
    certifications: dict[str, Certification],
):
    line = ProductionLine(
        organization_unit_id=units["MFG"].id,
        code="LINE-1",
        name="SMT Line 1",
        supervisor_worker_id=workers["W001"].id,
        status="active",
    )
    session.add(line)
    session.flush()

    team = ProductionTeam(
        production_line_id=line.id,
        code="TEAM-A",
        name="Team A",
        leader_worker_id=workers["W002"].id,
        shift_pattern="2_shift",
        status="active",
    )
    session.add(team)
    session.flush()

    workstations = [
        Workstation(
            production_line_id=line.id,
            code="WS-SMT-01",
            name="SMT Loader",
            workstation_type="smt",
            risk_level="medium",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-ASSY-01",
            name="Assembly Bench",
            workstation_type="assembly",
            risk_level="low",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-QA-01",
            name="QA Inspection",
            workstation_type="inspection",
            risk_level="medium",
            status="active",
        ),
    ]
    session.add_all(workstations)
    session.flush()

    session.add_all(
        [
            WorkstationSkillRequirement(
                workstation_id=workstations[0].id, skill_id=skills["SMT"].id, required_proficiency="intermediate"
            ),
            WorkstationSkillRequirement(
                workstation_id=workstations[1].id, skill_id=skills["ASSY"].id, required_proficiency="intermediate"
            ),
            WorkstationSkillRequirement(
                workstation_id=workstations[2].id, skill_id=skills["IPC610"].id, required_proficiency="advanced"
            ),
            WorkstationCertificationRequirement(
                workstation_id=workstations[2].id, certification_id=certifications["CERT-IPC"].id
            ),
            WorkstationEquipmentRequirement(
                workstation_id=workstations[0].id, equipment_code="SMT-LINE-01", required_authorization_level="operator"
            ),
        ]
    )

    assignments = [
        WorkerAssignment(
            worker_id=workers["W001"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="Line Supervisor",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=120),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W002"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="Assembler",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=100),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W003"].id,
            organization_unit_id=units["QA"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="QA Inspector",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=90),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W006"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="SMT Operator",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=45),
            is_primary=True,
        ),
    ]
    session.add_all(assignments)
    session.flush()

    return line, team, workstations


def seed_orders_and_shifts(session, line: ProductionLine, workstations: list[Workstation], workers: dict[str, Worker]):
    order = ProductionOrder(
        order_number="MO-20260518-001",
        production_line_id=line.id,
        product_code="PCB-CTRL-01",
        product_name="Controller Board",
        planned_quantity=1200,
        planned_start_date=TODAY,
        planned_end_date=TODAY + timedelta(days=3),
        priority="high",
        status="released",
    )
    session.add(order)

    templates = [
        ShiftTemplate(
            code="DAY",
            name="Day Shift",
            shift_type="day",
            start_time=time(8, 0),
            end_time=time(16, 0),
            allowance_rate=0.0,
            status="active",
        ),
        ShiftTemplate(
            code="NIGHT",
            name="Night Shift",
            shift_type="night",
            start_time=time(20, 0),
            end_time=time(4, 0),
            allowance_rate=0.2,
            status="active",
        ),
    ]
    session.add_all(templates)
    session.flush()

    operations = [
        ProductionOperation(
            production_order_id=order.id,
            workstation_id=workstations[0].id,
            operation_code="OP-SMT",
            operation_name="SMT Placement",
            sequence_number=10,
            planned_hours=16.0,
            required_headcount=2,
            status="ready",
        ),
        ProductionOperation(
            production_order_id=order.id,
            workstation_id=workstations[1].id,
            operation_code="OP-ASSY",
            operation_name="Final Assembly",
            sequence_number=20,
            planned_hours=12.0,
            required_headcount=2,
            status="planned",
        ),
        ProductionOperation(
            production_order_id=order.id,
            workstation_id=workstations[2].id,
            operation_code="OP-QA",
            operation_name="Final Inspection",
            sequence_number=30,
            planned_hours=8.0,
            required_headcount=1,
            status="planned",
        ),
    ]
    session.add_all(operations)

    day_template = next(template for template in templates if template.code == "DAY")
    plan = ShiftPlan(
        production_order_id=order.id,
        production_line_id=line.id,
        shift_template_id=day_template.id,
        work_date=TODAY,
        required_headcount=4,
        status="published",
        created_by="scheduler.bot",
    )
    session.add(plan)
    session.flush()

    shift_assignments = [
        ShiftAssignment(
            shift_plan_id=plan.id,
            worker_id=workers["W001"].id,
            workstation_id=workstations[0].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="Supervisor",
        ),
        ShiftAssignment(
            shift_plan_id=plan.id,
            worker_id=workers["W002"].id,
            workstation_id=workstations[1].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="Assembler",
        ),
        ShiftAssignment(
            shift_plan_id=plan.id,
            worker_id=workers["W003"].id,
            workstation_id=workstations[2].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="Inspector",
        ),
        ShiftAssignment(
            shift_plan_id=plan.id,
            worker_id=workers["W006"].id,
            workstation_id=workstations[0].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="Operator",
        ),
    ]
    session.add_all(shift_assignments)
    session.flush()

    return order, plan, shift_assignments


def seed_attendance(session, workers: dict[str, Worker]) -> None:
    records = []
    for offset in range(5):
        work_day = TODAY - timedelta(days=offset)
        for worker_code in ["W001", "W002", "W003", "W004", "W005", "W006"]:
            records.append(
                AttendanceRecord(
                    worker_id=workers[worker_code].id,
                    work_date=work_day,
                    check_in_time=time(8, random.randint(0, 12)),
                    check_out_time=time(17, random.randint(0, 25)),
                    status="present",
                    work_hours=8.0,
                )
            )
    session.add_all(records)

    leave = LeaveRequest(
        worker_id=workers["W005"].id,
        leave_type="annual",
        leave_type_name="Annual Leave",
        start_date=TODAY + timedelta(days=7),
        end_date=TODAY + timedelta(days=8),
        requested_days=2,
        reason="Family trip",
        status="approved",
        approver_name="Lin Qiao",
        approved_at=TODAY,
    )
    session.add(leave)

    payrolls = []
    for worker in workers.values():
        bonuses = 300 if worker.worker_code in {"W001", "W003", "W004"} else 120
        deductions = 80 if worker.worker_code == "W006" else 0
        base_salary = float(worker.base_salary or 0)
        payrolls.append(
            PayrollRecord(
                worker_id=worker.id,
                pay_period="2026-05",
                base_salary=base_salary,
                bonuses=float(bonuses),
                deductions=float(deductions),
                net_salary=base_salary + bonuses - deductions,
                status="processed",
                payment_date=TODAY + timedelta(days=12),
            )
        )
    session.add_all(payrolls)
    session.flush()


def seed_projects(session, workers: dict[str, Worker], skills: dict[str, Skill]) -> None:
    projects = [
        Project(
            code="PRJ-MES-01",
            name="MES Rollout",
            status="active",
            start_date=TODAY - timedelta(days=40),
            end_date=TODAY + timedelta(days=60),
            description="Connect staffing and shopfloor execution data.",
        ),
        Project(
            code="PRJ-QA-02",
            name="Inspection Upgrade",
            status="planning",
            start_date=TODAY - timedelta(days=10),
            end_date=TODAY + timedelta(days=45),
            description="Raise outbound quality coverage.",
        ),
    ]
    session.add_all(projects)
    session.flush()

    members = [
        ProjectMember(
            project_id=projects[0].id,
            worker_id=workers["W004"].id,
            role_name="Tech Lead",
            assigned_date=TODAY - timedelta(days=35),
            allocation_percent=60,
        ),
        ProjectMember(
            project_id=projects[0].id,
            worker_id=workers["W003"].id,
            role_name="QA Lead",
            assigned_date=TODAY - timedelta(days=35),
            allocation_percent=40,
        ),
        ProjectMember(
            project_id=projects[1].id,
            worker_id=workers["W001"].id,
            role_name="Manufacturing SME",
            assigned_date=TODAY - timedelta(days=8),
            allocation_percent=30,
        ),
    ]
    session.add_all(members)

    requirements = [
        ProjectSkillRequirement(
            project_id=projects[0].id,
            skill_id=skills["MES"].id,
            required_proficiency="advanced",
            person_days=25.0,
            headcount=1,
        ),
        ProjectSkillRequirement(
            project_id=projects[0].id,
            skill_id=skills["PLC"].id,
            required_proficiency="intermediate",
            person_days=18.0,
            headcount=1,
        ),
        ProjectSkillRequirement(
            project_id=projects[1].id,
            skill_id=skills["IPC610"].id,
            required_proficiency="advanced",
            person_days=12.0,
            headcount=1,
        ),
    ]
    session.add_all(requirements)
    session.flush()

    timesheets = [
        ProjectTimesheetEntry(
            project_id=projects[0].id,
            project_skill_requirement_id=requirements[0].id,
            worker_id=workers["W004"].id,
            work_date=TODAY - timedelta(days=2),
            hours=6.0,
            description="MES configuration workshop",
        ),
        ProjectTimesheetEntry(
            project_id=projects[0].id,
            project_skill_requirement_id=requirements[1].id,
            worker_id=workers["W004"].id,
            work_date=TODAY - timedelta(days=1),
            hours=4.0,
            description="PLC interface review",
        ),
        ProjectTimesheetEntry(
            project_id=projects[1].id,
            project_skill_requirement_id=requirements[2].id,
            worker_id=workers["W003"].id,
            work_date=TODAY - timedelta(days=1),
            hours=3.5,
            description="Inspection coverage analysis",
        ),
    ]
    session.add_all(timesheets)
    session.flush()


def seed_risks(
    session,
    order: ProductionOrder,
    line: ProductionLine,
    workstations: list[Workstation],
    shift_assignments: list[ShiftAssignment],
    workers: dict[str, Worker],
) -> None:
    signal = OperationalRiskSignal(
        production_order_id=order.id,
        worker_id=workers["W006"].id,
        production_line_id=line.id,
        workstation_id=workstations[0].id,
        shift_assignment_id=shift_assignments[3].id,
        signal_type="training_gap",
        severity="medium",
        status="open",
        detected_by="system",
        evidence="Operator assigned to SMT station with beginner proficiency and pending validation.",
    )
    session.add(signal)
    session.flush()

    review = OperationalRiskReview(
        risk_signal_id=signal.id,
        reviewer_name="Liu Mei",
        conclusion="Keep worker paired with supervisor until validation is complete.",
        action_suggestion="Schedule skills validation this week and keep dual coverage for the SMT station.",
        review_status="completed",
    )
    session.add(review)
    session.flush()


def main() -> None:
    random.seed(42)
    initialize_database()

    with SessionLocal() as session:
        reset_database(session)

        units = seed_organization(session)
        skills = seed_skills(session)
        certifications = seed_certifications(session)
        trainings = seed_safety_trainings(session, skills, certifications)
        workers = seed_workers(session, units)
        seed_worker_profiles(session, workers, skills, certifications, trainings)
        line, _team, workstations = seed_shopfloor(session, units, workers, skills, certifications)
        order, _plan, shift_assignments = seed_orders_and_shifts(session, line, workstations, workers)
        seed_attendance(session, workers)
        seed_projects(session, workers, skills)
        seed_risks(session, order, line, workstations, shift_assignments, workers)
        session.commit()

        counts = {
            "organization_units": session.query(OrganizationUnit).count(),
            "workers": session.query(Worker).count(),
            "skills": session.query(Skill).count(),
            "certifications": session.query(Certification).count(),
            "workstations": session.query(Workstation).count(),
            "shift_assignments": session.query(ShiftAssignment).count(),
            "attendance_records": session.query(AttendanceRecord).count(),
            "projects": session.query(Project).count(),
            "risk_signals": session.query(OperationalRiskSignal).count(),
        }

    print("Sample data seeded into workforce_ops database:")
    for name, count in counts.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
