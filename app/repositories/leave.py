from app.database import SessionLocal
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


def get_all_leaves(employee_id: int | None = None, status: str | None = None) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(LeaveORM)
        if employee_id is not None:
            query = query.filter_by(employee_id=employee_id)
        if status is not None:
            query = query.filter_by(status=status)
        records = query.all()
        return [r.to_dict() for r in records]


def get_leave_by_id(leave_id: int) -> dict | None:
    with SessionLocal() as session:
        record = session.get(LeaveORM, leave_id)
        return record.to_dict() if record else None


def get_leaves_by_employee(employee_id: int) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(LeaveORM).filter_by(employee_id=employee_id).all()
        return [r.to_dict() for r in records]


def get_approved_leaves_by_type(employee_id: int, leave_type: str) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(LeaveORM).filter_by(
            employee_id=employee_id, leave_type=leave_type, status="approved"
        ).all()
        return [r.to_dict() for r in records]


def get_approved_leaves_in_range(employee_id: int, start_date, end_date) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(LeaveORM).filter_by(
            employee_id=employee_id, status="approved"
        ).filter(
            LeaveORM.start_date <= end_date,
            LeaveORM.end_date >= start_date,
        ).all()
        return [r.to_dict() for r in records]


def create_leave(leave_data: dict) -> dict:
    with SessionLocal() as session:
        record = LeaveORM(**leave_data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.to_dict()


def update_leave(leave_id: int, leave_data: dict) -> dict | None:
    with SessionLocal() as session:
        record = session.get(LeaveORM, leave_id)
        if record is None:
            return None
        for k, v in leave_data.items():
            setattr(record, k, v)
        session.commit()
        session.refresh(record)
        return record.to_dict()
