from datetime import datetime

from fastapi import HTTPException

from app.repositories import employee as employee_repo
from app.repositories import performance as performance_repo
from app.schemas.performance import (
    ReviewCycleCreate, ReviewCycleUpdate, ReviewCycleResponse, ReviewCycleListResponse,
    PerformanceReviewCreate, PerformanceReviewUpdate,
    PerformanceReviewResponse, PerformanceReviewListResponse,
    EmployeePerformanceSummary, rating_to_level,
)


# ---- 考核周期 ----

def create_cycle(data: ReviewCycleCreate) -> ReviewCycleResponse:
    if data.end_date < data.start_date:
        raise HTTPException(status_code=400, detail="end_date must be >= start_date")
    cycle_data = data.model_dump()
    cycle_data["status"] = "open"
    cycle_data["created_at"] = datetime.now()
    cycle = performance_repo.create_cycle(cycle_data)
    return ReviewCycleResponse(review_count=0, **cycle)


def list_cycles() -> ReviewCycleListResponse:
    cycles = performance_repo.get_all_cycles()
    result = []
    for c in cycles:
        reviews = performance_repo.get_reviews_by_cycle(c["id"])
        result.append(ReviewCycleResponse(review_count=len(reviews), **c))
    return ReviewCycleListResponse(cycles=result, total=len(result))


def get_cycle(cycle_id: int) -> ReviewCycleResponse:
    cycle = performance_repo.get_cycle_by_id(cycle_id)
    if cycle is None:
        raise HTTPException(status_code=404, detail=f"Review cycle {cycle_id} not found")
    reviews = performance_repo.get_reviews_by_cycle(cycle_id)
    return ReviewCycleResponse(review_count=len(reviews), **cycle)


def update_cycle(cycle_id: int, data: ReviewCycleUpdate) -> ReviewCycleResponse:
    cycle = performance_repo.get_cycle_by_id(cycle_id)
    if cycle is None:
        raise HTTPException(status_code=404, detail=f"Review cycle {cycle_id} not found")
    if cycle["status"] == "closed":
        raise HTTPException(status_code=400, detail="Closed cycles cannot be updated")
    update_data = data.model_dump(exclude_unset=True)
    updated = performance_repo.update_cycle(cycle_id, update_data)
    reviews = performance_repo.get_reviews_by_cycle(cycle_id)
    return ReviewCycleResponse(review_count=len(reviews), **updated)


# ---- 绩效评分 ----

def _fill_names(record: dict) -> dict:
    emp = employee_repo.get_employee_by_id(record["employee_id"])
    record["employee_name"] = emp["name"] if emp else "Unknown"
    cycle = performance_repo.get_cycle_by_id(record["cycle_id"])
    record["cycle_name"] = cycle["name"] if cycle else "Unknown"
    return record


def create_review(data: PerformanceReviewCreate) -> PerformanceReviewResponse:
    emp = employee_repo.get_employee_by_id(data.employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {data.employee_id} not found")
    cycle = performance_repo.get_cycle_by_id(data.cycle_id)
    if cycle is None:
        raise HTTPException(status_code=404, detail=f"Review cycle {data.cycle_id} not found")
    if cycle["status"] != "open":
        raise HTTPException(status_code=400, detail="Cannot add reviews to a closed cycle")
    existing = performance_repo.get_review_by_employee_cycle(data.employee_id, data.cycle_id)
    if existing is not None:
        raise HTTPException(status_code=400, detail="Employee already has a review in this cycle")
    if not (1.0 <= data.rating <= 5.0):
        raise HTTPException(status_code=422, detail="Rating must be between 1.0 and 5.0")
    review_data = data.model_dump()
    review_data["rating_level"] = rating_to_level(data.rating)
    review_data["created_at"] = datetime.now()
    record = performance_repo.create_review(review_data)
    return PerformanceReviewResponse(**_fill_names(record))


def list_reviews(employee_id: int | None = None, cycle_id: int | None = None) -> PerformanceReviewListResponse:
    records = performance_repo.get_all_reviews(employee_id, cycle_id)
    return PerformanceReviewListResponse(
        reviews=[PerformanceReviewResponse(**_fill_names(r)) for r in records],
        total=len(records),
    )


def get_review(review_id: int) -> PerformanceReviewResponse:
    record = performance_repo.get_review_by_id(review_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
    return PerformanceReviewResponse(**_fill_names(record))


def update_review(review_id: int, data: PerformanceReviewUpdate) -> PerformanceReviewResponse:
    record = performance_repo.get_review_by_id(review_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
    cycle = performance_repo.get_cycle_by_id(record["cycle_id"])
    if cycle["status"] != "open":
        raise HTTPException(status_code=400, detail="Cannot update reviews in a closed cycle")
    update_data = data.model_dump(exclude_unset=True)
    if "rating" in update_data:
        if not (1.0 <= update_data["rating"] <= 5.0):
            raise HTTPException(status_code=422, detail="Rating must be between 1.0 and 5.0")
        update_data["rating_level"] = rating_to_level(update_data["rating"])
    updated = performance_repo.update_review(review_id, update_data)
    return PerformanceReviewResponse(**_fill_names(updated))


def get_employee_summary(employee_id: int) -> EmployeePerformanceSummary:
    emp = employee_repo.get_employee_by_id(employee_id)
    if emp is None:
        raise HTTPException(status_code=404, detail=f"Employee {employee_id} not found")
    reviews = performance_repo.get_reviews_by_employee(employee_id)
    if not reviews:
        return EmployeePerformanceSummary(
            employee_id=employee_id,
            employee_name=emp["name"],
            average_rating=0.0,
            review_count=0,
            latest_rating=None,
            rating_distribution={},
        )
    ratings = [r["rating"] for r in reviews]
    distribution = {}
    for r in reviews:
        level = r["rating_level"]
        distribution[level] = distribution.get(level, 0) + 1
    return EmployeePerformanceSummary(
        employee_id=employee_id,
        employee_name=emp["name"],
        average_rating=round(sum(ratings) / len(ratings), 2),
        review_count=len(reviews),
        latest_rating=reviews[-1]["rating"],
        rating_distribution=distribution,
    )
