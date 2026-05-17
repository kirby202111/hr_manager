from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import org_unit as department_repo
from app.repositories import worker as worker_repo
from app.schemas.worker import WorkerCreate, WorkerListResponse, WorkerResponse, WorkerUpdate


def _fill_department_name(worker: dict, db: Session | None = None) -> dict:
    dept_id = worker.get("department_id")
    if dept_id is not None:
        dept = department_repo.get_department_by_id(dept_id, db)
        worker["department_name"] = dept["name"] if dept else None
    return worker


def list_workers(db: Session | None = None) -> WorkerListResponse:
    workers = worker_repo.get_all_workers(db)
    return WorkerListResponse(
        workers=[WorkerResponse(**_fill_department_name(worker, db)) for worker in workers],
        total=len(workers),
    )


def get_worker(worker_id: int, db: Session | None = None) -> WorkerResponse:
    worker = worker_repo.get_worker_by_id(worker_id, db)
    if worker is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    return WorkerResponse(**_fill_department_name(worker, db))


def create_worker(worker_in: WorkerCreate, db: Session | None = None) -> WorkerResponse:
    if worker_in.department_id is not None:
        dept = department_repo.get_department_by_id(worker_in.department_id, db)
        if dept is None:
            raise ValidationError(f"Department {worker_in.department_id} not found")
    worker = worker_repo.create_worker(worker_in.model_dump(), db)
    return WorkerResponse(**_fill_department_name(worker, db))


def update_worker(worker_id: int, worker_in: WorkerUpdate, db: Session | None = None) -> WorkerResponse:
    existing = worker_repo.get_worker_by_id(worker_id, db)
    if existing is None:
        raise NotFoundError(f"Worker {worker_id} not found")
    if worker_in.department_id is not None:
        dept = department_repo.get_department_by_id(worker_in.department_id, db)
        if dept is None:
            raise ValidationError(f"Department {worker_in.department_id} not found")
    worker = worker_repo.update_worker(worker_id, worker_in.model_dump(exclude_unset=True), db)
    return WorkerResponse(**_fill_department_name(worker, db))


def delete_worker(worker_id: int, db: Session | None = None) -> dict:
    success = worker_repo.delete_worker(worker_id, db)
    if not success:
        raise NotFoundError(f"Worker {worker_id} not found")
    return {"message": f"Worker {worker_id} deleted"}
