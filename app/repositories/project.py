from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import db_session
from app.models.project import (
    Project as ProjectORM,
)
from app.models.project import (
    ProjectMember as MemberORM,
)
from app.models.project import (
    ProjectSkillRequirement as ReqORM,
)
from app.models.project import (
    ProjectTimesheet as TimesheetORM,
)

# ── Project ──────────────────────────────────────────────────


def get_all_projects(status: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(ProjectORM)
        if status:
            query = query.filter_by(status=status)
        projects = query.all()
        return [p.to_dict() for p in projects]


def get_project_by_id(project_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        project = session.get(ProjectORM, project_id)
        return project.to_dict() if project else None


def create_project(project_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        project = ProjectORM(**project_data)
        session.add(project)
        session.flush()
        session.refresh(project)
        return project.to_dict()


def update_project(project_id: int, project_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        project = session.get(ProjectORM, project_id)
        if project is None:
            return None
        for k, v in project_data.items():
            if v is not None:
                setattr(project, k, v)
        session.flush()
        session.refresh(project)
        return project.to_dict()


def delete_project(project_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        project = session.get(ProjectORM, project_id)
        if project is None:
            return False
        session.query(TimesheetORM).filter_by(project_id=project_id).delete()
        session.query(MemberORM).filter_by(project_id=project_id).delete()
        session.query(ReqORM).filter_by(project_id=project_id).delete()
        session.delete(project)
        session.flush()
        return True


def count_requirements(project_id: int, db: Session | None = None) -> int:
    with db_session(db) as session:
        return session.query(ReqORM).filter_by(project_id=project_id).count()


def count_members(project_id: int, db: Session | None = None) -> int:
    with db_session(db) as session:
        return session.query(MemberORM).filter_by(project_id=project_id).count()


# ── ProjectSkillRequirement ──────────────────────────────────


def get_requirements_by_project(project_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        reqs = session.query(ReqORM).filter_by(project_id=project_id).all()
        return [r.to_dict() for r in reqs]


def get_requirement_by_id(req_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        req = session.get(ReqORM, req_id)
        return req.to_dict() if req else None


def get_requirement_by_project_and_skill(project_id: int, skill_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        req = session.query(ReqORM).filter_by(project_id=project_id, skill_id=skill_id).first()
        return req.to_dict() if req else None


def create_requirement(req_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        req = ReqORM(**req_data)
        session.add(req)
        session.flush()
        session.refresh(req)
        return req.to_dict()


def update_requirement(req_id: int, req_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        req = session.get(ReqORM, req_id)
        if req is None:
            return None
        for k, v in req_data.items():
            if v is not None:
                setattr(req, k, v)
        session.flush()
        session.refresh(req)
        return req.to_dict()


def delete_requirement(req_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        req = session.get(ReqORM, req_id)
        if req is None:
            return False
        session.query(TimesheetORM).filter_by(requirement_id=req_id).delete()
        session.delete(req)
        session.flush()
        return True


# ── ProjectMember ────────────────────────────────────────────


def get_members_by_project(project_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        members = session.query(MemberORM).filter_by(project_id=project_id).all()
        return [m.to_dict() for m in members]


def get_member_by_id(member_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        member = session.get(MemberORM, member_id)
        return member.to_dict() if member else None


def get_member_by_employee_project(employee_id: int, project_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        member = session.query(MemberORM).filter_by(employee_id=employee_id, project_id=project_id).first()
        return member.to_dict() if member else None


def create_member(member_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        member = MemberORM(**member_data)
        session.add(member)
        session.flush()
        session.refresh(member)
        return member.to_dict()


def update_member(member_id: int, member_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        member = session.get(MemberORM, member_id)
        if member is None:
            return None
        for k, v in member_data.items():
            if v is not None:
                setattr(member, k, v)
        session.flush()
        session.refresh(member)
        return member.to_dict()


def delete_member(member_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        member = session.get(MemberORM, member_id)
        if member is None:
            return False
        session.delete(member)
        session.flush()
        return True


# ── ProjectTimesheet ─────────────────────────────────────────


def get_timesheets_by_project(
    project_id: int,
    employee_id: int | None = None,
    requirement_id: int | None = None,
    db: Session | None = None,
) -> list[dict]:
    with db_session(db) as session:
        query = session.query(TimesheetORM).filter_by(project_id=project_id)
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        if requirement_id:
            query = query.filter_by(requirement_id=requirement_id)
        timesheets = query.all()
        return [t.to_dict() for t in timesheets]


def get_timesheet_by_id(timesheet_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        ts = session.get(TimesheetORM, timesheet_id)
        return ts.to_dict() if ts else None


def create_timesheet(ts_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        ts = TimesheetORM(**ts_data)
        session.add(ts)
        session.flush()
        session.refresh(ts)
        return ts.to_dict()


def update_timesheet(timesheet_id: int, ts_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        ts = session.get(TimesheetORM, timesheet_id)
        if ts is None:
            return None
        for k, v in ts_data.items():
            if v is not None:
                setattr(ts, k, v)
        session.flush()
        session.refresh(ts)
        return ts.to_dict()


def delete_timesheet(timesheet_id: int, db: Session | None = None) -> bool:
    with db_session(db) as session:
        ts = session.get(TimesheetORM, timesheet_id)
        if ts is None:
            return False
        session.delete(ts)
        session.flush()
        return True


# ── Progress aggregation ─────────────────────────────────────


def get_progress_by_project(project_id: int, db: Session | None = None) -> dict:
    with db_session(db) as session:
        requirements = session.query(ReqORM).filter_by(project_id=project_id).all()
        by_requirement = []
        total_budget = 0.0
        total_used = 0.0

        for req in requirements:
            used_hours = (
                session.query(func.coalesce(func.sum(TimesheetORM.hours), 0)).filter_by(requirement_id=req.id).scalar()
            )
            used_days = round(used_hours / 8.0, 2)
            budget = req.person_days
            progress = round(used_days / budget * 100, 1) if budget > 0 else 0.0
            total_budget += budget
            total_used += used_days
            by_requirement.append(
                {
                    "requirement_id": req.id,
                    "skill_id": req.skill_id,
                    "budget_person_days": budget,
                    "used_person_days": used_days,
                    "progress": min(progress, 100.0),
                }
            )

        members = session.query(MemberORM).filter_by(project_id=project_id).all()
        by_member = []
        for m in members:
            used_hours = (
                session.query(func.coalesce(func.sum(TimesheetORM.hours), 0))
                .filter_by(employee_id=m.employee_id, project_id=project_id)
                .scalar()
            )
            by_member.append(
                {
                    "employee_id": m.employee_id,
                    "total_person_days": round(used_hours / 8.0, 2),
                }
            )

        overall = round(total_used / total_budget * 100, 1) if total_budget > 0 else 0.0

        return {
            "total_budget_person_days": total_budget,
            "total_used_person_days": total_used,
            "overall_progress": min(overall, 100.0),
            "by_requirement": by_requirement,
            "by_member": by_member,
        }
