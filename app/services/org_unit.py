from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.repositories import org_unit as department_repo
from app.repositories import worker as worker_repo
from app.schemas.org_unit import DepartmentCreate, DepartmentListResponse, DepartmentResponse, DepartmentUpdate
from app.schemas.worker import WorkerResponse


def list_departments(db: Session | None = None) -> DepartmentListResponse:
    departments = department_repo.get_all_departments(db)
    worker_counts = department_repo.count_employees_by_department(db)
    dept_responses = [
        DepartmentResponse(worker_count=worker_counts.get(dept["id"], 0), **dept)
        for dept in departments
    ]
    return DepartmentListResponse(departments=dept_responses, total=len(dept_responses))


def get_department(department_id: int, db: Session | None = None) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    workers = worker_repo.get_workers_by_department(department_id, db)
    return DepartmentResponse(worker_count=len(workers), **dept)


def create_department(dept_in: DepartmentCreate, db: Session | None = None) -> DepartmentResponse:
    existing = department_repo.get_department_by_name(dept_in.name, db)
    if existing is not None:
        raise ValidationError(f"Department '{dept_in.name}' already exists")
    dept = department_repo.create_department(dept_in.model_dump(), db)
    return DepartmentResponse(**dept)


def update_department(department_id: int, dept_in: DepartmentUpdate, db: Session | None = None) -> DepartmentResponse:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    if dept_in.name is not None:
        existing = department_repo.get_department_by_name(dept_in.name, db)
        if existing is not None and existing["id"] != department_id:
            raise ValidationError(f"Department '{dept_in.name}' already exists")
    updated = department_repo.update_department(department_id, dept_in.model_dump(exclude_unset=True), db)
    workers = worker_repo.get_workers_by_department(department_id, db)
    return DepartmentResponse(worker_count=len(workers), **updated)


def delete_department(department_id: int, db: Session | None = None) -> dict:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    workers = worker_repo.get_workers_by_department(department_id, db)
    if workers:
        raise ValidationError("Cannot delete department with existing workers")
    department_repo.delete_department(department_id, db)
    return {"message": f"Department {department_id} deleted"}


def get_department_workers(department_id: int, db: Session | None = None) -> list[WorkerResponse]:
    dept = department_repo.get_department_by_id(department_id, db)
    if dept is None:
        raise NotFoundError(f"Department {department_id} not found")
    workers = worker_repo.get_workers_by_department(department_id, db)
    return [WorkerResponse(**worker) for worker in workers]
