from sqlalchemy.orm import Session

from app.database import db_session
from app.models.leave import Leave as LeaveORM

LEAVE_TYPE_NAMES = {
    "sick": "病假",
    "annual": "年假",
    "personal": "事假",
    "other": "其他",
}

LEAVE_BALANCE_DEFAULTS = {
    "annual": 10,
    "sick": 15,
    "personal": 5,
}


def get_all_leaves(worker_id: int | None = None, status: str | None = None, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(LeaveORM)
        if worker_id is not None:
            query = query.filter_by(worker_id=worker_id)
        if status is not None:
            query = query.filter_by(status=status)
        return [record.to_dict() for record in query.all()]


def get_leave_by_id(leave_id: int, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(LeaveORM, leave_id)
        return record.to_dict() if record else None


def get_leaves_by_worker(worker_id: int, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        return [record.to_dict() for record in session.query(LeaveORM).filter_by(worker_id=worker_id).all()]


def get_approved_leaves_by_type(worker_id: int, leave_type: str, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = session.query(LeaveORM).filter_by(worker_id=worker_id, leave_type=leave_type, status="approved")
        return [record.to_dict() for record in query.all()]


def get_approved_leaves_in_range(worker_id: int, start_date, end_date, db: Session | None = None) -> list[dict]:
    with db_session(db) as session:
        query = (
            session.query(LeaveORM)
            .filter_by(worker_id=worker_id, status="approved")
            .filter(LeaveORM.start_date <= end_date, LeaveORM.end_date >= start_date)
        )
        return [record.to_dict() for record in query.all()]


def create_leave(leave_data: dict, db: Session | None = None) -> dict:
    with db_session(db) as session:
        record = LeaveORM(**leave_data)
        session.add(record)
        session.flush()
        session.refresh(record)
        return record.to_dict()


def update_leave(leave_id: int, leave_data: dict, db: Session | None = None) -> dict | None:
    with db_session(db) as session:
        record = session.get(LeaveORM, leave_id)
        if record is None:
            return None
        for key, value in leave_data.items():
            setattr(record, key, value)
        session.flush()
        session.refresh(record)
        return record.to_dict()
