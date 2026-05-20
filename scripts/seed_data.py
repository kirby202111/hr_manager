"""写入贴近电子产品生产车间场景的中文种子数据。"""

from __future__ import annotations

import os
import random
import sys
from datetime import date, datetime, time, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, SessionLocal, engine
from app.models import (
    AttendanceRecord,
    Certification,
    EquipmentAuthorization,
    LeaveRequest,
    OperationalRiskReview,
    OperationalRiskSignal,
    OperationQualificationRequirement,
    OrganizationUnit,
    PayrollRecord,
    ProductionLine,
    ProductionOperation,
    ProductionOrder,
    ProductionTeam,
    SafetyTraining,
    ShiftAssignment,
    ShiftPlan,
    ShiftTemplate,
    Skill,
    Worker,
    WorkerAssignment,
    WorkerCertification,
    WorkerEligibilitySnapshot,
    WorkerSafetyTraining,
    WorkerSkill,
    Workstation,
    WorkstationCertificationRequirement,
    WorkstationEquipmentRequirement,
    WorkstationSkillRequirement,
    WorkstationTrainingRequirement,
)
from app.schema import initialize_database

TODAY = date(2026, 5, 18)


def reset_database(session) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()


def recreate_database() -> None:
    Base.metadata.drop_all(bind=engine)
    initialize_database()


def seed_organization(session) -> dict[str, OrganizationUnit]:
    units = [
        OrganizationUnit(
            code="PLANT-SZ",
            name="深圳电子工厂",
            unit_type="plant",
            status="active",
            description="以智能控制板和整机装配为主的电子产品制造工厂。",
        ),
        OrganizationUnit(
            code="MFG",
            name="制造部",
            unit_type="department",
            status="active",
            description="负责 SMT、THT、装配、测试配合和包装作业。",
        ),
        OrganizationUnit(
            code="QA",
            name="质量部",
            unit_type="department",
            status="active",
            description="负责来料检验、过程质量控制和出货质量管控。",
        ),
        OrganizationUnit(
            code="ENG",
            name="工艺工程部",
            unit_type="department",
            status="active",
            description="负责导入、治具、测试系统和制程优化。",
        ),
        OrganizationUnit(
            code="WH",
            name="仓储物流部",
            unit_type="department",
            status="active",
            description="负责备料、线边配送、成品入库和内部物流。",
        ),
    ]
    session.add_all(units)
    session.flush()

    unit_map = {unit.code: unit for unit in units}
    plant_id = unit_map["PLANT-SZ"].id
    for code in ("MFG", "QA", "ENG", "WH"):
        unit_map[code].parent_id = plant_id
    session.flush()
    return unit_map


def seed_skills(session) -> dict[str, Skill]:
    skills = [
        Skill(code="SMT_SETUP", name="SMT换线与调机", category="manufacturing", status="active"),
        Skill(code="SMT_OP", name="SMT产线操作", category="manufacturing", status="active"),
        Skill(code="AOI", name="AOI检验", category="quality", status="active"),
        Skill(code="THT", name="THT插件作业", category="manufacturing", status="active"),
        Skill(code="SOLDER", name="手工焊接与返修", category="manufacturing", status="active"),
        Skill(code="ASSY", name="整机装配", category="manufacturing", status="active"),
        Skill(code="TEST", name="功能测试", category="quality", status="active"),
        Skill(code="PACK", name="包装作业", category="manufacturing", status="active"),
        Skill(code="IPC610", name="IPC-A-610外观判定", category="quality", status="active"),
        Skill(code="MES", name="MES报工", category="systems", status="active"),
        Skill(code="FIXTURE", name="测试治具维护", category="engineering", status="active"),
        Skill(code="FORK", name="叉车操作", category="warehouse", status="active"),
    ]
    session.add_all(skills)
    session.flush()
    return {skill.code: skill for skill in skills}


def seed_certifications(session) -> dict[str, Certification]:
    certifications = [
        Certification(
            code="CERT-IPC-A610",
            name="IPC-A-610检验员",
            category="quality",
            validity_months=24,
            issuing_authority="IPC协会",
            description="电子组件外观接收标准判定资格。",
        ),
        Certification(
            code="CERT-ESD",
            name="ESD防护操作员",
            category="safety",
            validity_months=12,
            issuing_authority="工厂EHS办公室",
            description="静电防护与敏感器件操作资格。",
        ),
        Certification(
            code="CERT-WAVE",
            name="波峰焊设备操作员",
            category="equipment",
            validity_months=18,
            issuing_authority="工艺工程部",
            description="选择焊与波峰焊设备操作资格。",
        ),
        Certification(
            code="CERT-FLT",
            name="叉车操作证",
            category="equipment",
            validity_months=36,
            issuing_authority="当地物流监管机构",
            description="厂内物流与叉车驾驶资格证书。",
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
            code="SAFE-ESD",
            title="电子产品生产ESD防护培训",
            category="quality",
            skill_id=skills["SMT_OP"].id,
            validity_months=12,
            required_hours=2.0,
            description="包括接地、腕带点检和湿敏器件操作要求。",
        ),
        SafetyTraining(
            code="SAFE-REWORK",
            title="烙铁与热风返修安全培训",
            category="safety",
            skill_id=skills["SOLDER"].id,
            validity_months=12,
            required_hours=3.0,
            description="包括烙铁安全、烟雾排放和热工具使用规范。",
        ),
        SafetyTraining(
            code="SAFE-WAVE",
            title="波峰焊设备安全培训",
            category="equipment",
            required_certification_id=certifications["CERT-WAVE"].id,
            validity_months=12,
            required_hours=4.0,
            description="包括助焊剂使用、传送机构风险和急停流程。",
        ),
        SafetyTraining(
            code="SAFE-FCT",
            title="电性能测试工位安全培训",
            category="safety",
            skill_id=skills["TEST"].id,
            validity_months=12,
            required_hours=2.0,
            description="包括带电测试注意事项、治具锁定和异常板隔离。",
        ),
        SafetyTraining(
            code="SAFE-FLT",
            title="叉车复训",
            category="equipment",
            required_certification_id=certifications["CERT-FLT"].id,
            validity_months=12,
            required_hours=3.0,
            description="包括人车分流和电池充电安全要求。",
        ),
    ]
    session.add_all(trainings)
    session.flush()
    return {training.code: training for training in trainings}


def seed_workers(session, units: dict[str, OrganizationUnit]) -> dict[str, Worker]:
    workers = [
        Worker(
            worker_code="W001",
            full_name="刘梅",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=1320),
            base_salary=9800,
            phone_number="13800010001",
            notes="SMT产线主管，现场执行力强，熟悉换线和首件确认。",
        ),
        Worker(
            worker_code="W002",
            full_name="陈浩",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=880),
            base_salary=8200,
            phone_number="13800010002",
            notes="资深SMT操作员，负责钢网更换和换线调机。",
        ),
        Worker(
            worker_code="W003",
            full_name="张宇",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["QA"].id,
            hire_date=TODAY - timedelta(days=1460),
            base_salary=9300,
            phone_number="13800010003",
            notes="质量组长，擅长AOI复判和外观工艺判定。",
        ),
        Worker(
            worker_code="W004",
            full_name="林乔",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["ENG"].id,
            hire_date=TODAY - timedelta(days=1680),
            base_salary=11800,
            phone_number="13800010004",
            notes="工艺工程师，负责治具维护和线平衡优化。",
        ),
        Worker(
            worker_code="W005",
            full_name="唐伟",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["WH"].id,
            hire_date=TODAY - timedelta(days=760),
            base_salary=7200,
            phone_number="13800010005",
            notes="仓库与线边配送人员，负责补料和成品流转。",
        ),
        Worker(
            worker_code="W006",
            full_name="孙佳",
            employment_type="contractor",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=210),
            base_salary=6300,
            phone_number="13800010006",
            notes="新入岗插件与装配作业员，当前处于上岗验证期。",
        ),
        Worker(
            worker_code="W007",
            full_name="何敏",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=540),
            base_salary=7600,
            phone_number="13800010007",
            notes="插件与波峰焊作业员，可独立处理焊接段。",
        ),
        Worker(
            worker_code="W008",
            full_name="高宁",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=620),
            base_salary=7500,
            phone_number="13800010008",
            notes="装配包装组长，负责末段产能与人员协调。",
        ),
        Worker(
            worker_code="W009",
            full_name="徐帆",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["QA"].id,
            hire_date=TODAY - timedelta(days=450),
            base_salary=7900,
            phone_number="13800010009",
            notes="功能测试与出货检验员，负责终检判定。",
        ),
        Worker(
            worker_code="W010",
            full_name="彭睿",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=300),
            base_salary=7000,
            phone_number="13800010010",
            notes="包装与物料核对作业员，负责标签与装箱确认。",
        ),
        Worker(
            worker_code="W011",
            full_name="邓凯",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=410),
            base_salary=7100,
            phone_number="13800010011",
            notes="夜班SMT操作员，负责飞达恢复和首件确认。",
        ),
        Worker(
            worker_code="W012",
            full_name="姚莉",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=520),
            base_salary=7350,
            phone_number="13800010012",
            notes="装配与维修作业员，支持ECO变更机种。",
        ),
        Worker(
            worker_code="W013",
            full_name="秦越",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["QA"].id,
            hire_date=TODAY - timedelta(days=680),
            base_salary=8050,
            phone_number="13800010013",
            notes="IPQC巡检员，负责SMT和THT过程巡检。",
        ),
        Worker(
            worker_code="W014",
            full_name="方磊",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["ENG"].id,
            hire_date=TODAY - timedelta(days=960),
            base_salary=10200,
            phone_number="13800010014",
            notes="测试工程师，负责ICT与FCT治具维护。",
        ),
        Worker(
            worker_code="W015",
            full_name="马鑫",
            employment_type="contractor",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=130),
            base_salary=6100,
            phone_number="13800010015",
            notes="旺季临时包装工，支援高峰期出货。",
        ),
        Worker(
            worker_code="W016",
            full_name="吴晨",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["WH"].id,
            hire_date=TODAY - timedelta(days=390),
            base_salary=6900,
            phone_number="13800010016",
            notes="物料员，负责线边备料和成品转运。",
        ),
        Worker(
            worker_code="W017",
            full_name="沈璐",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=245),
            base_salary=6800,
            phone_number="13800010017",
            notes="老化与功能测试助理，支持混线工单。",
        ),
        Worker(
            worker_code="W018",
            full_name="田默",
            employment_type="full_time",
            status="active",
            organization_unit_id=units["MFG"].id,
            hire_date=TODAY - timedelta(days=860),
            base_salary=7850,
            phone_number="13800010018",
            notes="资深维修返修技术员，可支援插件段异常处理。",
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
            skill_id=skills["SMT_SETUP"].id,
            proficiency_level="advanced",
            years_of_experience=7.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W001"].id,
            skill_id=skills["SMT_OP"].id,
            proficiency_level="expert",
            years_of_experience=8.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W001"].id,
            skill_id=skills["MES"].id,
            proficiency_level="advanced",
            years_of_experience=5.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W002"].id,
            skill_id=skills["SMT_SETUP"].id,
            proficiency_level="advanced",
            years_of_experience=4.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W002"].id,
            skill_id=skills["SMT_OP"].id,
            proficiency_level="advanced",
            years_of_experience=5.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W002"].id,
            skill_id=skills["AOI"].id,
            proficiency_level="intermediate",
            years_of_experience=2.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W003"].id,
            skill_id=skills["AOI"].id,
            proficiency_level="expert",
            years_of_experience=6.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W003"].id,
            skill_id=skills["IPC610"].id,
            proficiency_level="expert",
            years_of_experience=7.0,
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
            skill_id=skills["FIXTURE"].id,
            proficiency_level="expert",
            years_of_experience=8.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W004"].id,
            skill_id=skills["MES"].id,
            proficiency_level="advanced",
            years_of_experience=6.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W004"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="intermediate",
            years_of_experience=2.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W005"].id,
            skill_id=skills["FORK"].id,
            proficiency_level="advanced",
            years_of_experience=4.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W005"].id,
            skill_id=skills["PACK"].id,
            proficiency_level="intermediate",
            years_of_experience=2.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W006"].id,
            skill_id=skills["THT"].id,
            proficiency_level="beginner",
            years_of_experience=0.6,
            validated=False,
        ),
        WorkerSkill(
            worker_id=workers["W006"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="intermediate",
            years_of_experience=1.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W007"].id,
            skill_id=skills["THT"].id,
            proficiency_level="advanced",
            years_of_experience=4.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W007"].id,
            skill_id=skills["SOLDER"].id,
            proficiency_level="advanced",
            years_of_experience=4.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W008"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="advanced",
            years_of_experience=4.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W008"].id,
            skill_id=skills["PACK"].id,
            proficiency_level="advanced",
            years_of_experience=3.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W009"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="advanced",
            years_of_experience=3.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W009"].id,
            skill_id=skills["IPC610"].id,
            proficiency_level="advanced",
            years_of_experience=3.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W010"].id,
            skill_id=skills["PACK"].id,
            proficiency_level="intermediate",
            years_of_experience=1.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W010"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="beginner",
            years_of_experience=0.8,
            validated=False,
        ),
        WorkerSkill(
            worker_id=workers["W011"].id,
            skill_id=skills["SMT_OP"].id,
            proficiency_level="intermediate",
            years_of_experience=2.2,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W011"].id,
            skill_id=skills["SMT_SETUP"].id,
            proficiency_level="intermediate",
            years_of_experience=1.8,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W012"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="advanced",
            years_of_experience=3.1,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W012"].id,
            skill_id=skills["SOLDER"].id,
            proficiency_level="intermediate",
            years_of_experience=2.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W013"].id,
            skill_id=skills["AOI"].id,
            proficiency_level="advanced",
            years_of_experience=4.1,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W013"].id,
            skill_id=skills["IPC610"].id,
            proficiency_level="advanced",
            years_of_experience=4.0,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W014"].id,
            skill_id=skills["FIXTURE"].id,
            proficiency_level="advanced",
            years_of_experience=5.2,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W014"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="advanced",
            years_of_experience=4.8,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W015"].id,
            skill_id=skills["PACK"].id,
            proficiency_level="beginner",
            years_of_experience=0.5,
            validated=False,
        ),
        WorkerSkill(
            worker_id=workers["W016"].id,
            skill_id=skills["FORK"].id,
            proficiency_level="intermediate",
            years_of_experience=1.6,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W016"].id,
            skill_id=skills["PACK"].id,
            proficiency_level="beginner",
            years_of_experience=0.9,
            validated=False,
        ),
        WorkerSkill(
            worker_id=workers["W017"].id,
            skill_id=skills["TEST"].id,
            proficiency_level="intermediate",
            years_of_experience=1.7,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W017"].id,
            skill_id=skills["ASSY"].id,
            proficiency_level="intermediate",
            years_of_experience=1.4,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W018"].id,
            skill_id=skills["SOLDER"].id,
            proficiency_level="expert",
            years_of_experience=6.5,
            validated=True,
        ),
        WorkerSkill(
            worker_id=workers["W018"].id,
            skill_id=skills["THT"].id,
            proficiency_level="advanced",
            years_of_experience=5.3,
            validated=True,
        ),
    ]
    session.add_all(worker_skills)

    worker_certifications = [
        WorkerCertification(
            worker_id=workers["W001"].id,
            certification_id=certifications["CERT-ESD"].id,
            certification_number="ESD-2026-001",
            issued_at=TODAY - timedelta(days=90),
            expires_at=TODAY + timedelta(days=275),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W002"].id,
            certification_id=certifications["CERT-ESD"].id,
            certification_number="ESD-2026-014",
            issued_at=TODAY - timedelta(days=120),
            expires_at=TODAY + timedelta(days=245),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W003"].id,
            certification_id=certifications["CERT-IPC-A610"].id,
            certification_number="IPC-2025-023",
            issued_at=TODAY - timedelta(days=250),
            expires_at=TODAY + timedelta(days=470),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W007"].id,
            certification_id=certifications["CERT-WAVE"].id,
            certification_number="WAVE-2025-008",
            issued_at=TODAY - timedelta(days=180),
            expires_at=TODAY + timedelta(days=330),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W009"].id,
            certification_id=certifications["CERT-IPC-A610"].id,
            certification_number="IPC-2026-041",
            issued_at=TODAY - timedelta(days=100),
            expires_at=TODAY + timedelta(days=620),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W005"].id,
            certification_id=certifications["CERT-FLT"].id,
            certification_number="FLT-2024-112",
            issued_at=TODAY - timedelta(days=420),
            expires_at=TODAY + timedelta(days=640),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W011"].id,
            certification_id=certifications["CERT-ESD"].id,
            certification_number="ESD-2026-026",
            issued_at=TODAY - timedelta(days=60),
            expires_at=TODAY + timedelta(days=305),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W013"].id,
            certification_id=certifications["CERT-IPC-A610"].id,
            certification_number="IPC-2025-067",
            issued_at=TODAY - timedelta(days=220),
            expires_at=TODAY + timedelta(days=500),
            status="valid",
        ),
        WorkerCertification(
            worker_id=workers["W016"].id,
            certification_id=certifications["CERT-FLT"].id,
            certification_number="FLT-2026-008",
            issued_at=TODAY - timedelta(days=95),
            expires_at=TODAY + timedelta(days=980),
            status="valid",
        ),
    ]
    session.add_all(worker_certifications)

    worker_training_records = [
        WorkerSafetyTraining(
            worker_id=workers["W001"].id,
            safety_training_id=trainings["SAFE-ESD"].id,
            completed_at=TODAY - timedelta(days=30),
            expires_at=TODAY + timedelta(days=335),
            score=98,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W002"].id,
            safety_training_id=trainings["SAFE-ESD"].id,
            completed_at=TODAY - timedelta(days=40),
            expires_at=TODAY + timedelta(days=325),
            score=95,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W003"].id,
            safety_training_id=trainings["SAFE-FCT"].id,
            completed_at=TODAY - timedelta(days=75),
            expires_at=TODAY + timedelta(days=290),
            score=93,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W007"].id,
            safety_training_id=trainings["SAFE-WAVE"].id,
            completed_at=TODAY - timedelta(days=60),
            expires_at=TODAY + timedelta(days=305),
            score=90,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W007"].id,
            safety_training_id=trainings["SAFE-REWORK"].id,
            completed_at=TODAY - timedelta(days=65),
            expires_at=TODAY + timedelta(days=300),
            score=92,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W005"].id,
            safety_training_id=trainings["SAFE-FLT"].id,
            completed_at=TODAY - timedelta(days=50),
            expires_at=TODAY + timedelta(days=315),
            score=88,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W008"].id,
            safety_training_id=trainings["SAFE-REWORK"].id,
            completed_at=TODAY - timedelta(days=80),
            expires_at=TODAY + timedelta(days=285),
            score=85,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W009"].id,
            safety_training_id=trainings["SAFE-FCT"].id,
            completed_at=TODAY - timedelta(days=45),
            expires_at=TODAY + timedelta(days=320),
            score=96,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W011"].id,
            safety_training_id=trainings["SAFE-ESD"].id,
            completed_at=TODAY - timedelta(days=25),
            expires_at=TODAY + timedelta(days=340),
            score=91,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W012"].id,
            safety_training_id=trainings["SAFE-REWORK"].id,
            completed_at=TODAY - timedelta(days=55),
            expires_at=TODAY + timedelta(days=310),
            score=87,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W014"].id,
            safety_training_id=trainings["SAFE-FCT"].id,
            completed_at=TODAY - timedelta(days=38),
            expires_at=TODAY + timedelta(days=327),
            score=94,
            status="valid",
        ),
        WorkerSafetyTraining(
            worker_id=workers["W017"].id,
            safety_training_id=trainings["SAFE-FCT"].id,
            completed_at=TODAY - timedelta(days=82),
            expires_at=TODAY + timedelta(days=283),
            score=89,
            status="valid",
        ),
    ]
    session.add_all(worker_training_records)

    equipment_authorizations = [
        EquipmentAuthorization(
            worker_id=workers["W001"].id,
            equipment_code="SMT-LINE-01",
            authorization_level="supervisor",
            issued_at=TODAY - timedelta(days=320),
            expires_at=TODAY + timedelta(days=410),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W002"].id,
            equipment_code="SMT-LINE-01",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=260),
            expires_at=TODAY + timedelta(days=390),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W007"].id,
            equipment_code="WAVE-SOLDER-01",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=180),
            expires_at=TODAY + timedelta(days=300),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W009"].id,
            equipment_code="FCT-BENCH-02",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=120),
            expires_at=TODAY + timedelta(days=365),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W005"].id,
            equipment_code="FORKLIFT-A",
            authorization_level="advanced",
            issued_at=TODAY - timedelta(days=210),
            expires_at=TODAY + timedelta(days=720),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W011"].id,
            equipment_code="SMT-LINE-01",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=115),
            expires_at=TODAY + timedelta(days=365),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W014"].id,
            equipment_code="FCT-BENCH-02",
            authorization_level="engineer",
            issued_at=TODAY - timedelta(days=160),
            expires_at=TODAY + timedelta(days=480),
            status="valid",
        ),
        EquipmentAuthorization(
            worker_id=workers["W016"].id,
            equipment_code="FORKLIFT-B",
            authorization_level="operator",
            issued_at=TODAY - timedelta(days=75),
            expires_at=TODAY + timedelta(days=1000),
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
    trainings: dict[str, SafetyTraining],
) -> tuple[ProductionLine, ProductionTeam, list[Workstation]]:
    line = ProductionLine(
        organization_unit_id=units["MFG"].id,
        code="LINE-EC01",
        name="智能控制板混合产线",
        supervisor_worker_id=workers["W001"].id,
        status="active",
        description="覆盖SMT、THT、装配、测试和包装的电子产品混合产线。",
    )
    session.add(line)
    session.flush()

    team = ProductionTeam(
        production_line_id=line.id,
        code="TEAM-D1",
        name="白班A组",
        leader_worker_id=workers["W008"].id,
        shift_pattern="2_shift",
        status="active",
        description="负责控制板与整机白班生产的核心班组。",
    )
    session.add(team)
    session.flush()

    workstations = [
        Workstation(
            production_line_id=line.id,
            code="WS-SMT-PRINT",
            name="锡膏印刷",
            workstation_type="smt",
            risk_level="medium",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-SMT-MOUNT",
            name="SMT贴片",
            workstation_type="smt",
            risk_level="medium",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-AOI-01",
            name="AOI检测",
            workstation_type="inspection",
            risk_level="low",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-THT-01",
            name="THT插件与波峰焊",
            workstation_type="tht",
            risk_level="high",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-ASSY-01",
            name="总装装配",
            workstation_type="assembly",
            risk_level="medium",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-FCT-01",
            name="功能测试",
            workstation_type="test",
            risk_level="medium",
            status="active",
        ),
        Workstation(
            production_line_id=line.id,
            code="WS-PACK-01",
            name="包装",
            workstation_type="packaging",
            risk_level="low",
            status="active",
        ),
    ]
    session.add_all(workstations)
    session.flush()

    station_map = {station.code: station for station in workstations}

    session.add_all(
        [
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-SMT-PRINT"].id,
                skill_id=skills["SMT_SETUP"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
                description="负责钢网安装、参数切换和锡膏确认。",
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-SMT-MOUNT"].id,
                skill_id=skills["SMT_OP"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
                description="负责飞达上料和贴片机操作。",
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-AOI-01"].id,
                skill_id=skills["AOI"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-THT-01"].id,
                skill_id=skills["THT"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-THT-01"].id,
                skill_id=skills["SOLDER"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-ASSY-01"].id,
                skill_id=skills["ASSY"].id,
                min_proficiency_level="intermediate",
                must_be_validated=False,
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-FCT-01"].id,
                skill_id=skills["TEST"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            WorkstationSkillRequirement(
                workstation_id=station_map["WS-PACK-01"].id,
                skill_id=skills["PACK"].id,
                min_proficiency_level="beginner",
                must_be_validated=False,
            ),
            WorkstationCertificationRequirement(
                workstation_id=station_map["WS-AOI-01"].id,
                certification_id=certifications["CERT-IPC-A610"].id,
                description="AOI异常复判需要具备IPC外观判定能力。",
            ),
            WorkstationCertificationRequirement(
                workstation_id=station_map["WS-THT-01"].id,
                certification_id=certifications["CERT-WAVE"].id,
                description="波峰焊设备操作需具备设备上岗资格。",
            ),
            WorkstationCertificationRequirement(
                workstation_id=station_map["WS-SMT-MOUNT"].id,
                certification_id=certifications["CERT-ESD"].id,
                description="操作员需持有有效的ESD防护资格。",
            ),
            WorkstationTrainingRequirement(
                workstation_id=station_map["WS-SMT-MOUNT"].id,
                safety_training_id=trainings["SAFE-ESD"].id,
                min_score=85,
                description="设备上岗前必须完成ESD培训。",
            ),
            WorkstationTrainingRequirement(
                workstation_id=station_map["WS-THT-01"].id, safety_training_id=trainings["SAFE-WAVE"].id, min_score=85
            ),
            WorkstationTrainingRequirement(
                workstation_id=station_map["WS-THT-01"].id, safety_training_id=trainings["SAFE-REWORK"].id, min_score=80
            ),
            WorkstationTrainingRequirement(
                workstation_id=station_map["WS-FCT-01"].id, safety_training_id=trainings["SAFE-FCT"].id, min_score=85
            ),
            WorkstationEquipmentRequirement(
                workstation_id=station_map["WS-SMT-MOUNT"].id,
                equipment_code="SMT-LINE-01",
                min_authorization_level="operator",
                description="贴片设备上机权限要求。",
            ),
            WorkstationEquipmentRequirement(
                workstation_id=station_map["WS-THT-01"].id,
                equipment_code="WAVE-SOLDER-01",
                min_authorization_level="operator",
            ),
            WorkstationEquipmentRequirement(
                workstation_id=station_map["WS-FCT-01"].id,
                equipment_code="FCT-BENCH-02",
                min_authorization_level="operator",
            ),
        ]
    )

    assignments = [
        WorkerAssignment(
            worker_id=workers["W001"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="产线主管",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=180),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W002"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="SMT作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=160),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W003"].id,
            organization_unit_id=units["QA"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="质量组长",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=150),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W006"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="THT作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=90),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W007"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="波峰焊作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=135),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W008"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="装配组长",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=140),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W009"].id,
            organization_unit_id=units["QA"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="测试检验员",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=120),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W010"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="包装作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=80),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W011"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="夜班SMT作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=105),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W012"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="装配作业员",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=110),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W013"].id,
            organization_unit_id=units["QA"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="IPQC巡检员",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=100),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W014"].id,
            organization_unit_id=units["ENG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="测试工程师",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=95),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W015"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="季节性包装作业员",
            assignment_type="temporary",
            status="active",
            start_date=TODAY - timedelta(days=60),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W016"].id,
            organization_unit_id=units["WH"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="物料员",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=75),
            is_primary=False,
        ),
        WorkerAssignment(
            worker_id=workers["W017"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="测试助理",
            assignment_type="primary",
            status="active",
            start_date=TODAY - timedelta(days=70),
            is_primary=True,
        ),
        WorkerAssignment(
            worker_id=workers["W018"].id,
            organization_unit_id=units["MFG"].id,
            production_line_id=line.id,
            production_team_id=team.id,
            role_title="返修技术员",
            assignment_type="shared",
            status="active",
            start_date=TODAY - timedelta(days=150),
            is_primary=False,
        ),
    ]
    session.add_all(assignments)
    session.flush()

    return line, team, workstations


def seed_orders_and_shifts(
    session,
    line: ProductionLine,
    workstations: list[Workstation],
    workers: dict[str, Worker],
    skills: dict[str, Skill],
    certifications: dict[str, Certification],
    trainings: dict[str, SafetyTraining],
) -> tuple[ProductionOrder, list[ShiftPlan], list[ShiftAssignment], list[ProductionOperation]]:
    orders = [
        ProductionOrder(
            order_number="MO-20260518-EC1001",
            production_line_id=line.id,
            product_code="EC-SPK-CTRL-02",
            product_name="智能音箱控制模块",
            planned_quantity=2400,
            planned_start_date=TODAY,
            planned_end_date=TODAY + timedelta(days=4),
            priority="high",
            status="released",
            description="智能音箱控制板及整机包装主生产工单。",
        ),
        ProductionOrder(
            order_number="MO-20260519-EC1002",
            production_line_id=line.id,
            product_code="EC-HUB-MAIN-03",
            product_name="智能家居网关主板",
            planned_quantity=1600,
            planned_start_date=TODAY + timedelta(days=1),
            planned_end_date=TODAY + timedelta(days=3),
            priority="medium",
            status="released",
            description="与主线共享贴片和终测产能的混线追加工单。",
        ),
        ProductionOrder(
            order_number="MO-20260520-EC1003",
            production_line_id=line.id,
            product_code="EC-AMP-DRV-01",
            product_name="便携音频驱动板",
            planned_quantity=900,
            planned_start_date=TODAY + timedelta(days=2),
            planned_end_date=TODAY + timedelta(days=3),
            priority="rush",
            status="planned",
            description="需要返修能力支撑的短单加急补产工单。",
        ),
    ]
    session.add_all(orders)

    templates = [
        ShiftTemplate(
            code="DAY",
            name="白班",
            shift_type="day",
            start_time=time(8, 0),
            end_time=time(16, 30),
            allowance_rate=0.0,
            status="active",
        ),
        ShiftTemplate(
            code="NIGHT",
            name="夜班",
            shift_type="night",
            start_time=time(20, 0),
            end_time=time(4, 30),
            allowance_rate=0.2,
            status="active",
        ),
    ]
    session.add_all(templates)
    session.flush()
    template_map = {template.code: template for template in templates}
    station_map = {station.code: station for station in workstations}

    operation_specs = [
        ("OP-010", "锡膏印刷", "WS-SMT-PRINT", 10, 9.5, 1, "ready"),
        ("OP-020", "SMT贴片", "WS-SMT-MOUNT", 20, 18.0, 2, "ready"),
        ("OP-030", "AOI检测", "WS-AOI-01", 30, 8.0, 1, "ready"),
        ("OP-040", "THT插件与波峰焊", "WS-THT-01", 40, 12.0, 2, "planned"),
        ("OP-050", "总装装配", "WS-ASSY-01", 50, 14.0, 2, "planned"),
        ("OP-060", "功能测试", "WS-FCT-01", 60, 10.0, 1, "planned"),
        ("OP-070", "包装", "WS-PACK-01", 70, 7.5, 2, "planned"),
    ]

    operations: list[ProductionOperation] = []
    order_offsets = {orders[0].id: 0, orders[1].id: 100, orders[2].id: 200}
    order_hour_scale = {orders[0].id: 1.0, orders[1].id: 0.82, orders[2].id: 0.58}
    order_status_overrides = {
        orders[0].id: {"OP-040": "in_progress"},
        orders[1].id: {"OP-010": "ready", "OP-020": "ready"},
        orders[2].id: {"OP-010": "planned", "OP-020": "planned", "OP-030": "planned"},
    }
    for order in orders:
        seq_offset = order_offsets[order.id]
        hour_scale = order_hour_scale[order.id]
        status_map = order_status_overrides[order.id]
        for op_code, op_name, station_code, seq, hours, headcount, default_status in operation_specs:
            operations.append(
                ProductionOperation(
                    production_order_id=order.id,
                    workstation_id=station_map[station_code].id,
                    operation_code=f"{op_code}-{order.order_number[-4:]}",
                    operation_name=op_name,
                    sequence_number=seq + seq_offset,
                    planned_hours=round(hours * hour_scale, 1),
                    required_headcount=headcount,
                    status=status_map.get(op_code, default_status),
                )
            )
    session.add_all(operations)
    session.flush()

    primary_ops = [op for op in operations if op.production_order_id == orders[0].id]

    session.add_all(
        [
            OperationQualificationRequirement(
                production_operation_id=primary_ops[1].id,
                requirement_type="skill",
                reference_id=skills["SMT_OP"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
                description="贴片设备操作必须具备已验证的SMT技能。",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[1].id,
                requirement_type="certification",
                reference_id=certifications["CERT-ESD"].id,
                description="贴片工序要求具备有效ESD资格。",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[1].id,
                requirement_type="training",
                reference_id=trainings["SAFE-ESD"].id,
                min_score=85,
                description="需要具备近期有效的ESD培训记录。",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[3].id,
                requirement_type="skill",
                reference_id=skills["THT"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[3].id,
                requirement_type="equipment",
                equipment_code="WAVE-SOLDER-01",
                min_authorization_level="operator",
                description="波峰焊设备授权要求。",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[5].id,
                requirement_type="skill",
                reference_id=skills["TEST"].id,
                min_proficiency_level="intermediate",
                must_be_validated=True,
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[5].id,
                requirement_type="equipment",
                equipment_code="FCT-BENCH-02",
                min_authorization_level="operator",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[6].id,
                requirement_type="skill",
                reference_id=skills["PACK"].id,
                min_proficiency_level="beginner",
            ),
            OperationQualificationRequirement(
                production_operation_id=primary_ops[4].id,
                requirement_type="skill",
                reference_id=skills["ASSY"].id,
                min_proficiency_level="intermediate",
            ),
        ]
    )

    plans = [
        ShiftPlan(
            production_order_id=orders[0].id,
            production_line_id=line.id,
            shift_template_id=template_map["DAY"].id,
            work_date=TODAY,
            required_headcount=10,
            status="published",
            created_by="排班机器人",
        ),
        ShiftPlan(
            production_order_id=orders[0].id,
            production_line_id=line.id,
            shift_template_id=template_map["NIGHT"].id,
            work_date=TODAY,
            required_headcount=6,
            status="published",
            created_by="排班机器人",
        ),
        ShiftPlan(
            production_order_id=orders[1].id,
            production_line_id=line.id,
            shift_template_id=template_map["DAY"].id,
            work_date=TODAY + timedelta(days=1),
            required_headcount=10,
            status="published",
            created_by="排班机器人",
        ),
        ShiftPlan(
            production_order_id=orders[1].id,
            production_line_id=line.id,
            shift_template_id=template_map["NIGHT"].id,
            work_date=TODAY + timedelta(days=1),
            required_headcount=6,
            status="draft",
            created_by="排班机器人",
        ),
        ShiftPlan(
            production_order_id=orders[2].id,
            production_line_id=line.id,
            shift_template_id=template_map["DAY"].id,
            work_date=TODAY + timedelta(days=2),
            required_headcount=8,
            status="planned",
            created_by="排班机器人",
        ),
    ]
    session.add_all(plans)
    session.flush()

    shift_assignments = [
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W001"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="主管",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W002"].id,
            workstation_id=station_map["WS-SMT-PRINT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="SMT调机",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W003"].id,
            workstation_id=station_map["WS-AOI-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="AOI检验",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W006"].id,
            workstation_id=station_map["WS-THT-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="THT作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W007"].id,
            workstation_id=station_map["WS-THT-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="波峰焊作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W008"].id,
            workstation_id=station_map["WS-ASSY-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="装配组长",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W009"].id,
            workstation_id=station_map["WS-FCT-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="终测检验",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W010"].id,
            workstation_id=station_map["WS-PACK-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="包装作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W013"].id,
            workstation_id=station_map["WS-AOI-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="IPQC巡检",
        ),
        ShiftAssignment(
            shift_plan_id=plans[0].id,
            worker_id=workers["W016"].id,
            workstation_id=station_map["WS-PACK-01"].id,
            assignment_type="support",
            status="scheduled",
            assigned_role="线边补料",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W001"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="夜班支援",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W002"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="SMT作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W007"].id,
            workstation_id=station_map["WS-THT-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="波峰焊作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W008"].id,
            workstation_id=station_map["WS-ASSY-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="装配作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W010"].id,
            workstation_id=station_map["WS-PACK-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="包装作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W011"].id,
            workstation_id=station_map["WS-SMT-PRINT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="夜班SMT调机",
        ),
        ShiftAssignment(
            shift_plan_id=plans[1].id,
            worker_id=workers["W017"].id,
            workstation_id=station_map["WS-FCT-01"].id,
            assignment_type="support",
            status="scheduled",
            assigned_role="测试助理",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W001"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="产线主管",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W002"].id,
            workstation_id=station_map["WS-SMT-PRINT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="SMT调机",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W011"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="SMT作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W013"].id,
            workstation_id=station_map["WS-AOI-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="IPQC检验",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W007"].id,
            workstation_id=station_map["WS-THT-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="波峰焊作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W012"].id,
            workstation_id=station_map["WS-ASSY-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="装配作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W009"].id,
            workstation_id=station_map["WS-FCT-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="终测检验",
        ),
        ShiftAssignment(
            shift_plan_id=plans[2].id,
            worker_id=workers["W015"].id,
            workstation_id=station_map["WS-PACK-01"].id,
            assignment_type="temporary",
            status="scheduled",
            assigned_role="临时包装",
        ),
        ShiftAssignment(
            shift_plan_id=plans[3].id,
            worker_id=workers["W011"].id,
            workstation_id=station_map["WS-SMT-MOUNT"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="夜班SMT作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[3].id,
            worker_id=workers["W017"].id,
            workstation_id=station_map["WS-FCT-01"].id,
            assignment_type="primary",
            status="scheduled",
            assigned_role="夜班测试作业",
        ),
        ShiftAssignment(
            shift_plan_id=plans[4].id,
            worker_id=workers["W018"].id,
            workstation_id=station_map["WS-THT-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="返修支援",
        ),
        ShiftAssignment(
            shift_plan_id=plans[4].id,
            worker_id=workers["W014"].id,
            workstation_id=station_map["WS-FCT-01"].id,
            assignment_type="shared",
            status="scheduled",
            assigned_role="治具工程支援",
        ),
    ]
    session.add_all(shift_assignments)
    session.flush()

    return orders[0], plans, shift_assignments, operations


def seed_eligibility_snapshots(
    session,
    workstations: list[Workstation],
    operations: list[ProductionOperation],
    plans: list[ShiftPlan],
    shift_assignments: list[ShiftAssignment],
    workers: dict[str, Worker],
) -> None:
    station_map = {station.code: station for station in workstations}
    operation_map = {(operation.production_order_id, operation.operation_name): operation for operation in operations}
    assignment_map = {
        (assignment.shift_plan_id, assignment.worker_id, assignment.workstation_id): assignment
        for assignment in shift_assignments
    }

    eligible_assignment = assignment_map[(plans[0].id, workers["W007"].id, station_map["WS-THT-01"].id)]
    risk_assignment = assignment_map[(plans[0].id, workers["W006"].id, station_map["WS-THT-01"].id)]
    smt_night_assignment = assignment_map[(plans[1].id, workers["W011"].id, station_map["WS-SMT-PRINT"].id)]
    pack_temp_assignment = assignment_map[(plans[2].id, workers["W015"].id, station_map["WS-PACK-01"].id)]
    primary_order_id = plans[0].production_order_id
    second_order_id = plans[2].production_order_id

    snapshots = [
        WorkerEligibilitySnapshot(
            worker_id=workers["W007"].id,
            workstation_id=station_map["WS-THT-01"].id,
            production_operation_id=operation_map[(primary_order_id, "THT插件与波峰焊")].id,
            shift_plan_id=plans[0].id,
            shift_assignment_id=eligible_assignment.id,
            work_date=TODAY,
            status="eligible",
            summary_reason="THT作业员技能已验证，且波峰焊设备授权有效。",
            detail_json=[
                {
                    "type": "skill",
                    "status": "pass",
                    "message": "插件与焊接技能满足当前工位要求。",
                },
                {"type": "equipment", "status": "pass", "message": "波峰焊设备授权在有效期内。"},
            ],
            checked_at=datetime(2026, 5, 18, 7, 20),
            checked_by="排班机器人",
            rule_version="v1",
            source_context="shift_assignment",
        ),
        WorkerEligibilitySnapshot(
            worker_id=workers["W006"].id,
            workstation_id=station_map["WS-THT-01"].id,
            production_operation_id=operation_map[(primary_order_id, "THT插件与波峰焊")].id,
            shift_plan_id=plans[0].id,
            shift_assignment_id=risk_assignment.id,
            work_date=TODAY,
            status="restricted",
            summary_reason="因THT技能尚未完成验证，当前仅允许在带教覆盖下上岗。",
            detail_json=[
                {"type": "skill", "status": "warning", "message": "已具备THT技能记录，但尚未完成技能验证。"},
                {"type": "training", "status": "fail", "message": "缺少波峰焊安全培训记录。"},
            ],
            checked_at=datetime(2026, 5, 18, 7, 22),
            checked_by="排班机器人",
            rule_version="v1",
            source_context="shift_assignment",
        ),
        WorkerEligibilitySnapshot(
            worker_id=workers["W011"].id,
            workstation_id=station_map["WS-SMT-PRINT"].id,
            production_operation_id=operation_map[(primary_order_id, "锡膏印刷")].id,
            shift_plan_id=plans[1].id,
            shift_assignment_id=smt_night_assignment.id,
            work_date=TODAY,
            status="eligible",
            summary_reason="夜班SMT调机人员资格完整，可执行产线支援。",
            detail_json=[
                {"type": "skill", "status": "pass", "message": "SMT调机技能已完成验证。"},
                {"type": "training", "status": "pass", "message": "ESD培训成绩满足门槛要求。"},
            ],
            checked_at=datetime(2026, 5, 18, 19, 30),
            checked_by="排班机器人",
            rule_version="v1",
            source_context="shift_assignment",
        ),
        WorkerEligibilitySnapshot(
            worker_id=workers["W015"].id,
            workstation_id=station_map["WS-PACK-01"].id,
            production_operation_id=operation_map[(second_order_id, "包装")].id,
            shift_plan_id=plans[2].id,
            shift_assignment_id=pack_temp_assignment.id,
            work_date=TODAY + timedelta(days=1),
            status="restricted",
            summary_reason="临时包装工仅允许在监督条件下参与包装批次。",
            detail_json=[
                {"type": "skill", "status": "warning", "message": "已有包装技能记录，但验证仍待完成。"},
                {
                    "type": "assignment",
                    "status": "pass",
                    "message": "旺季临时上岗安排已获批准。",
                },
            ],
            checked_at=datetime(2026, 5, 19, 7, 35),
            checked_by="排班机器人",
            rule_version="v1",
            source_context="shift_assignment",
        ),
    ]
    session.add_all(snapshots)
    session.flush()


def seed_attendance(session, workers: dict[str, Worker]) -> None:
    records = []
    worker_codes = list(workers.keys())
    for offset in range(7):
        work_day = TODAY - timedelta(days=offset)
        for code in worker_codes:
            if code == "W015" and offset in (1, 2):
                records.append(
                    AttendanceRecord(
                        worker_id=workers[code].id,
                        work_date=work_day,
                        check_in_time=time(0, 0),
                        check_out_time=None,
                        status="off",
                        work_hours=0.0,
                    )
                )
                continue
            if code == "W010" and offset == 4:
                records.append(
                    AttendanceRecord(
                        worker_id=workers[code].id,
                        work_date=work_day,
                        check_in_time=time(0, 0),
                        check_out_time=None,
                        status="leave",
                        work_hours=0.0,
                    )
                )
                continue
            if code == "W004" and offset in (1, 3):
                check_in = time(9, random.randint(0, 20))
                check_out = time(18, random.randint(0, 25))
                work_hours = 8.0
                status = "present"
            elif code == "W005" and offset == 2:
                check_in = time(7, 30)
                check_out = time(16, 0)
                work_hours = 8.5
                status = "present"
            elif code in {"W007", "W011", "W017"} and offset in (0, 2, 5):
                check_in = time(20, random.randint(0, 10))
                check_out = time(4, random.randint(20, 40))
                work_hours = 8.5
                status = "present"
            elif code in {"W006", "W015"} and offset == 0:
                check_in = time(8, random.randint(18, 35))
                check_out = time(17, random.randint(10, 35))
                work_hours = 7.7
                status = "late"
            elif code in {"W001", "W002", "W008", "W009"} and offset in (0, 1):
                check_in = time(7, random.randint(45, 58))
                check_out = time(18, random.randint(20, 55))
                work_hours = 9.5
                status = "overtime"
            else:
                check_in = time(8, random.randint(0, 18))
                check_out = time(17, random.randint(0, 35))
                work_hours = 8.0
                status = "present"
            records.append(
                AttendanceRecord(
                    worker_id=workers[code].id,
                    work_date=work_day,
                    check_in_time=check_in,
                    check_out_time=check_out,
                    status=status,
                    work_hours=work_hours,
                )
            )
    session.add_all(records)

    session.add_all(
        [
            LeaveRequest(
                worker_id=workers["W010"].id,
                leave_type="personal",
                leave_type_name="事假",
                start_date=TODAY + timedelta(days=5),
                end_date=TODAY + timedelta(days=5),
                requested_days=1,
                reason="家中有事需请假处理",
                status="approved",
                approver_name="刘梅",
                approved_at=TODAY,
            ),
            LeaveRequest(
                worker_id=workers["W003"].id,
                leave_type="annual",
                leave_type_name="年假",
                start_date=TODAY + timedelta(days=12),
                end_date=TODAY + timedelta(days=13),
                requested_days=2,
                reason="已安排短途出行",
                status="approved",
                approver_name="林乔",
                approved_at=TODAY - timedelta(days=1),
            ),
            LeaveRequest(
                worker_id=workers["W015"].id,
                leave_type="sick",
                leave_type_name="病假",
                start_date=TODAY - timedelta(days=2),
                end_date=TODAY - timedelta(days=1),
                requested_days=2,
                reason="发热就诊，需要休息",
                status="approved",
                approver_name="高宁",
                approved_at=TODAY - timedelta(days=2),
            ),
        ]
    )

    payroll_settings = {
        "W001": (900, 0),
        "W002": (650, 0),
        "W003": (700, 0),
        "W004": (1200, 0),
        "W005": (320, 0),
        "W006": (180, 60),
        "W007": (420, 0),
        "W008": (360, 0),
        "W009": (450, 0),
        "W010": (220, 0),
        "W011": (380, 0),
        "W012": (340, 0),
        "W013": (410, 0),
        "W014": (860, 0),
        "W015": (150, 80),
        "W016": (260, 0),
        "W017": (240, 0),
        "W018": (520, 0),
    }
    payrolls = []
    for code, worker in workers.items():
        bonuses, deductions = payroll_settings[code]
        base_salary = float(worker.base_salary or 0)
        payrolls.append(
            PayrollRecord(
                worker_id=worker.id,
                pay_period="2026-05",
                base_salary=base_salary,
                bonuses=float(bonuses),
                deductions=float(deductions),
                net_salary=base_salary + float(bonuses) - float(deductions),
                status="processed",
                payment_date=TODAY + timedelta(days=12),
            )
        )
    session.add_all(payrolls)
    session.flush()


def seed_risks(
    session,
    order: ProductionOrder,
    line: ProductionLine,
    workstations: list[Workstation],
    shift_assignments: list[ShiftAssignment],
    workers: dict[str, Worker],
) -> None:
    station_map = {station.code: station for station in workstations}
    risk_assignment = next(
        assignment
        for assignment in shift_assignments
        if assignment.worker_id == workers["W006"].id and assignment.workstation_id == station_map["WS-THT-01"].id
    )
    temp_pack_assignment = next(
        assignment
        for assignment in shift_assignments
        if assignment.worker_id == workers["W015"].id and assignment.workstation_id == station_map["WS-PACK-01"].id
    )
    material_support_assignment = next(
        assignment
        for assignment in shift_assignments
        if assignment.worker_id == workers["W016"].id and assignment.workstation_id == station_map["WS-PACK-01"].id
    )

    signals = [
        OperationalRiskSignal(
            production_order_id=order.id,
            worker_id=workers["W006"].id,
            production_line_id=line.id,
            workstation_id=station_map["WS-THT-01"].id,
            shift_assignment_id=risk_assignment.id,
            signal_type="qualification_gap",
            severity="medium",
            status="open",
            detected_by="资格校验引擎",
            evidence=(
                "人员被排到THT与波峰焊区域，但技能验证未完成，且缺少波峰焊安全培训记录。"
            ),
        ),
        OperationalRiskSignal(
            production_order_id=order.id,
            worker_id=workers["W015"].id,
            production_line_id=line.id,
            workstation_id=station_map["WS-PACK-01"].id,
            shift_assignment_id=temp_pack_assignment.id,
            signal_type="temporary_staffing",
            severity="low",
            status="monitoring",
            detected_by="排班机器人",
            evidence="旺季临时包装工被安排到高出货批次，但包装技能验证尚未完成。",
        ),
        OperationalRiskSignal(
            production_order_id=order.id,
            worker_id=workers["W016"].id,
            production_line_id=line.id,
            workstation_id=station_map["WS-PACK-01"].id,
            shift_assignment_id=material_support_assignment.id,
            signal_type="material_flow",
            severity="medium",
            status="open",
            detected_by="仓储同步服务",
            evidence="包装标签线边补料余量不足两小时，存在断料风险。",
        ),
    ]
    session.add_all(signals)
    session.flush()

    session.add_all(
        [
            OperationalRiskReview(
                risk_signal_id=signals[0].id,
                reviewer_name="刘梅",
                conclusion="该员工仅可在持证波峰焊作业员带教覆盖下继续留在线上作业。",
                action_suggestion=(
                    "将最终焊接触发工步转由W007执行，本周内补齐SAFE-WAVE培训，"
                    "随后为W006安排技能验证。"
                ),
                review_status="completed",
            ),
            OperationalRiskReview(
                risk_signal_id=signals[1].id,
                reviewer_name="高宁",
                conclusion="临时工可继续执行外箱装配和贴标作业。",
                action_suggestion="在技能验证完成前，不允许W015执行最终装箱数量确认。",
                review_status="completed",
            ),
            OperationalRiskReview(
                risk_signal_id=signals[2].id,
                reviewer_name="唐伟",
                conclusion="通过一次紧急补料可以消除当前断料风险。",
                action_suggestion="在14:00前从仓库B区释放备用标签库存到线边。",
                review_status="completed",
            ),
        ]
    )
    session.flush()


def main() -> None:
    random.seed(42)
    recreate_database()

    with SessionLocal() as session:
        units = seed_organization(session)
        skills = seed_skills(session)
        certifications = seed_certifications(session)
        trainings = seed_safety_trainings(session, skills, certifications)
        workers = seed_workers(session, units)
        seed_worker_profiles(session, workers, skills, certifications, trainings)
        line, _team, workstations = seed_shopfloor(session, units, workers, skills, certifications, trainings)
        order, plans, shift_assignments, operations = seed_orders_and_shifts(
            session, line, workstations, workers, skills, certifications, trainings
        )
        seed_eligibility_snapshots(session, workstations, operations, plans, shift_assignments, workers)
        seed_attendance(session, workers)
        seed_risks(session, order, line, workstations, shift_assignments, workers)
        session.commit()

        counts = {
            "organization_units": session.query(OrganizationUnit).count(),
            "workers": session.query(Worker).count(),
            "skills": session.query(Skill).count(),
            "certifications": session.query(Certification).count(),
            "trainings": session.query(SafetyTraining).count(),
            "workstations": session.query(Workstation).count(),
            "operations": session.query(ProductionOperation).count(),
            "shift_plans": session.query(ShiftPlan).count(),
            "shift_assignments": session.query(ShiftAssignment).count(),
            "eligibility_snapshots": session.query(WorkerEligibilitySnapshot).count(),
            "attendance_records": session.query(AttendanceRecord).count(),
            "risk_signals": session.query(OperationalRiskSignal).count(),
        }

    print("Sample data seeded into workforce_ops database:")
    for name, count in counts.items():
        print(f"  {name}: {count}")


if __name__ == "__main__":
    main()
