from __future__ import annotations

from datetime import UTC, date, datetime, time

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base


def _make_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


_TEST_ENGINE = _make_engine()
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)

# Modules that do `from app.database import SessionLocal` — each holds its own ref
_REPO_MODULES = [
    "app.repositories.employee",
    "app.repositories.department",
    "app.repositories.attendance",
    "app.repositories.leave",
    "app.repositories.payroll",
    "app.repositories.project",
    "app.repositories.employee_skill",
    "app.repositories.skill_catalog",
    "app.repositories.agent_memory",
]


@pytest.fixture(autouse=True)
def _setup_db(monkeypatch):
    """Create all tables for each test and patch SessionLocal everywhere."""
    import app.database as db_mod

    monkeypatch.setattr(db_mod, "engine", _TEST_ENGINE)
    monkeypatch.setattr(db_mod, "SessionLocal", _TestSessionLocal)

    # Patch SessionLocal in every repo module that imported it at module level
    import importlib

    for mod_path in _REPO_MODULES:
        mod = importlib.import_module(mod_path)
        if hasattr(mod, "SessionLocal"):
            monkeypatch.setattr(mod, "SessionLocal", _TestSessionLocal)

    # Patch engine in main module so lifespan creates tables on test DB
    import main as main_mod

    monkeypatch.setattr(main_mod, "engine", _TEST_ENGINE)

    # Patch engine in database_migration module
    import app.database_migration as mig_mod

    monkeypatch.setattr(mig_mod, "engine", _TEST_ENGINE)

    Base.metadata.create_all(bind=_TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=_TEST_ENGINE)


@pytest.fixture()
def db_session():
    """Provide a transactional test database session."""
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    """FastAPI test client with test database, bypassing lifespan."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.routers import (
        agent_memory,
        attendance,
        department,
        employee,
        employee_skill,
        leave,
        payroll,
        project,
        skill_catalog,
    )

    app = FastAPI()
    app.include_router(employee.router)
    app.include_router(department.router)
    app.include_router(attendance.router)
    app.include_router(leave.router)
    app.include_router(payroll.router)
    app.include_router(employee_skill.router)
    app.include_router(skill_catalog.router)
    app.include_router(project.router)
    app.include_router(agent_memory.router)

    with TestClient(app) as c:
        yield c


async def _async_iter(items):
    for item in items:
        yield item


# ── Sample data fixtures ──────────────────────────────────────


@pytest.fixture()
def sample_department():
    from app.repositories import department as dept_repo

    dept = dept_repo.create_department(
        {
            "name": "工程部",
            "description": "研发部门",
            "manager": "张经理",
        }
    )
    return dept


@pytest.fixture()
def sample_employee(sample_department):
    from app.repositories import employee as emp_repo

    emp = emp_repo.create_employee(
        {
            "name": "张三",
            "department_id": sample_department["id"],
            "salary": 15000.0,
        }
    )
    return emp


@pytest.fixture()
def sample_attendance(sample_employee):
    from app.repositories import attendance as att_repo

    record = att_repo.create_attendance(
        {
            "employee_id": sample_employee["id"],
            "date": date(2026, 5, 1),
            "check_in": time(8, 30),
            "status": "normal",
        }
    )
    return record


@pytest.fixture()
def sample_leave(sample_employee):
    from app.repositories import leave as leave_repo

    record = leave_repo.create_leave(
        {
            "employee_id": sample_employee["id"],
            "leave_type": "annual",
            "leave_type_name": "年假",
            "start_date": date(2026, 5, 10),
            "end_date": date(2026, 5, 12),
            "days": 3,
            "status": "pending",
            "created_at": datetime.now(UTC),
        }
    )
    return record


@pytest.fixture()
def sample_payroll(sample_employee):
    from app.repositories import payroll as payroll_repo

    record = payroll_repo.create_payroll(
        {
            "employee_id": sample_employee["id"],
            "month": "2026-05",
            "base_salary": 15000.0,
            "bonuses": 0.0,
            "deductions": 0.0,
            "net_salary": 15000.0,
            "status": "draft",
            "created_at": datetime.now(UTC),
        }
    )
    return record


@pytest.fixture()
def sample_skill_catalog():
    from app.repositories import skill_catalog as catalog_repo

    skill = catalog_repo.create_skill(
        {
            "name": "Python",
            "category": "编程",
            "description": "Python编程语言",
            "created_at": datetime.now(UTC),
        }
    )
    return skill


@pytest.fixture()
def sample_employee_skill(sample_employee, sample_skill_catalog):
    from app.repositories import employee_skill as skill_repo

    skill = skill_repo.create_skill(
        {
            "employee_id": sample_employee["id"],
            "skill_name": "Python",
            "skill_id": sample_skill_catalog["id"],
            "proficiency_level": "advanced",
            "years_of_experience": 5.0,
            "certification": "PCEP",
            "created_at": datetime.now(UTC),
        }
    )
    return skill


@pytest.fixture()
def sample_project(sample_skill_catalog):
    from app.repositories import project as project_repo

    project = project_repo.create_project(
        {
            "name": "HR系统V2",
            "description": "HR管理系统升级",
            "status": "planning",
            "start_date": date(2026, 1, 1),
            "end_date": date(2026, 12, 31),
            "created_at": datetime.now(UTC),
        }
    )
    return project
