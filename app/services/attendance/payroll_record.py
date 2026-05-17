"""Service module."""

from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.repositories.attendance import payroll_record as payroll_record_repo
from app.repositories.workforce import worker as worker_repo
from app.schemas.attendance import (
    PayrollRecordCreate,
    PayrollRecordListResponse,
    PayrollRecordResponse,
    PayrollRecordUpdate,
)


def _to_response(row: dict) -> PayrollRecordResponse:
    return PayrollRecordResponse(**row)


def _require_row(payroll_record_id: int, db: Session | None = None) -> dict:
    row = payroll_record_repo.get_payroll_record_by_id(payroll_record_id, db)
    if row is None:
        raise NotFoundError(f"Payroll record {payroll_record_id} not found")
    return row


def _validate_payload(payload: dict, db: Session | None = None) -> None:
    if worker_repo.get_worker_by_id(payload["worker_id"], db) is None:
        raise NotFoundError(f"Worker {payload['worker_id']} not found")


def list_payroll_records(
    worker_id: int | None = None,
    pay_period: str | None = None,
    status: str | None = None,
    db: Session | None = None,
) -> PayrollRecordListResponse:
    rows = payroll_record_repo.list_payroll_records(worker_id, pay_period, status, db)
    return PayrollRecordListResponse(payroll_records=[_to_response(row) for row in rows], total=len(rows))


def get_payroll_record(payroll_record_id: int, db: Session | None = None) -> PayrollRecordResponse:
    return _to_response(_require_row(payroll_record_id, db))


def create_payroll_record(data: PayrollRecordCreate, db: Session | None = None) -> PayrollRecordResponse:
    payload = data.model_dump()
    _validate_payload(payload, db)
    if (
        payroll_record_repo.get_payroll_record_by_worker_and_pay_period(payload["worker_id"], payload["pay_period"], db)
        is not None
    ):
        raise ConflictError("Payroll record already exists")
    row = payroll_record_repo.create_payroll_record(payload, db)
    return _to_response(row)


def update_payroll_record(
    payroll_record_id: int,
    data: PayrollRecordUpdate,
    db: Session | None = None,
) -> PayrollRecordResponse:
    current = _require_row(payroll_record_id, db)
    payload = {**current, **data.model_dump(exclude_unset=True)}
    _validate_payload(payload, db)
    existing = payroll_record_repo.get_payroll_record_by_worker_and_pay_period(
        payload["worker_id"], payload["pay_period"], db
    )
    if existing is not None and existing["id"] != payroll_record_id:
        raise ConflictError("Payroll record already exists")
    row = payroll_record_repo.update_payroll_record(payroll_record_id, data.model_dump(exclude_unset=True), db)
    if row is None:
        raise NotFoundError(f"Payroll record {payroll_record_id} not found")
    return _to_response(row)


def delete_payroll_record(payroll_record_id: int, db: Session | None = None) -> dict[str, str]:
    _require_row(payroll_record_id, db)
    payroll_record_repo.delete_payroll_record(payroll_record_id, db)
    return {"message": f"Payroll record {payroll_record_id} deleted"}
