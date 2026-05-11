from app.database import SessionLocal
from app.models.performance import PerformanceCycle as CycleORM
from app.models.performance import PerformanceReview as ReviewORM


# ---- 考核周期 ----

def get_all_cycles() -> list[dict]:
    with SessionLocal() as session:
        cycles = session.query(CycleORM).all()
        return [c.to_dict() for c in cycles]


def get_cycle_by_id(cycle_id: int) -> dict | None:
    with SessionLocal() as session:
        cycle = session.get(CycleORM, cycle_id)
        return cycle.to_dict() if cycle else None


def create_cycle(cycle_data: dict) -> dict:
    with SessionLocal() as session:
        cycle = CycleORM(**cycle_data)
        session.add(cycle)
        session.commit()
        session.refresh(cycle)
        return cycle.to_dict()


def update_cycle(cycle_id: int, cycle_data: dict) -> dict | None:
    with SessionLocal() as session:
        cycle = session.get(CycleORM, cycle_id)
        if cycle is None:
            return None
        for k, v in cycle_data.items():
            if v is not None:
                setattr(cycle, k, v)
        session.commit()
        session.refresh(cycle)
        return cycle.to_dict()


# ---- 绩效评分 ----

def rating_to_level(rating: float) -> str:
    if rating >= 4.5:
        return "excellent"
    if rating >= 3.5:
        return "good"
    if rating >= 2.5:
        return "average"
    return "poor"


def get_all_reviews(employee_id: int | None = None, cycle_id: int | None = None) -> list[dict]:
    with SessionLocal() as session:
        query = session.query(ReviewORM)
        if employee_id is not None:
            query = query.filter_by(employee_id=employee_id)
        if cycle_id is not None:
            query = query.filter_by(cycle_id=cycle_id)
        records = query.all()
        return [r.to_dict() for r in records]


def get_review_by_id(review_id: int) -> dict | None:
    with SessionLocal() as session:
        record = session.get(ReviewORM, review_id)
        return record.to_dict() if record else None


def get_review_by_employee_cycle(employee_id: int, cycle_id: int) -> dict | None:
    with SessionLocal() as session:
        record = session.query(ReviewORM).filter_by(employee_id=employee_id, cycle_id=cycle_id).first()
        return record.to_dict() if record else None


def get_reviews_by_employee(employee_id: int) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(ReviewORM).filter_by(employee_id=employee_id).all()
        return [r.to_dict() for r in records]


def get_reviews_by_cycle(cycle_id: int) -> list[dict]:
    with SessionLocal() as session:
        records = session.query(ReviewORM).filter_by(cycle_id=cycle_id).all()
        return [r.to_dict() for r in records]


def create_review(review_data: dict) -> dict:
    with SessionLocal() as session:
        record = ReviewORM(**review_data)
        session.add(record)
        session.commit()
        session.refresh(record)
        return record.to_dict()


def update_review(review_id: int, review_data: dict) -> dict | None:
    with SessionLocal() as session:
        record = session.get(ReviewORM, review_id)
        if record is None:
            return None
        for k, v in review_data.items():
            if v is not None:
                setattr(record, k, v)
        session.commit()
        session.refresh(record)
        return record.to_dict()
