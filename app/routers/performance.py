from fastapi import APIRouter, Query

from app.schemas.performance import (
    ReviewCycleCreate, ReviewCycleUpdate, ReviewCycleResponse, ReviewCycleListResponse,
    PerformanceReviewCreate, PerformanceReviewUpdate,
    PerformanceReviewResponse, PerformanceReviewListResponse,
    EmployeePerformanceSummary,
)
from app.services import performance as performance_service

router = APIRouter(prefix="/performance", tags=["绩效管理"])


# ---- 考核周期 ----

@router.post("/cycles/", response_model=ReviewCycleResponse, status_code=201)
def create_cycle(data: ReviewCycleCreate):
    return performance_service.create_cycle(data)


@router.get("/cycles/", response_model=ReviewCycleListResponse)
def list_cycles():
    return performance_service.list_cycles()


@router.get("/cycles/{cycle_id}", response_model=ReviewCycleResponse)
def get_cycle(cycle_id: int):
    return performance_service.get_cycle(cycle_id)


@router.put("/cycles/{cycle_id}", response_model=ReviewCycleResponse)
def update_cycle(cycle_id: int, data: ReviewCycleUpdate):
    return performance_service.update_cycle(cycle_id, data)


# ---- 绩效评分 ----

@router.post("/reviews/", response_model=PerformanceReviewResponse, status_code=201)
def create_review(data: PerformanceReviewCreate):
    return performance_service.create_review(data)


@router.get("/reviews/", response_model=PerformanceReviewListResponse)
def list_reviews(
    employee_id: int | None = None,
    cycle_id: int | None = None,
):
    return performance_service.list_reviews(employee_id, cycle_id)


@router.get("/reviews/{review_id}", response_model=PerformanceReviewResponse)
def get_review(review_id: int):
    return performance_service.get_review(review_id)


@router.put("/reviews/{review_id}", response_model=PerformanceReviewResponse)
def update_review(review_id: int, data: PerformanceReviewUpdate):
    return performance_service.update_review(review_id, data)


@router.get("/employee/{employee_id}/summary", response_model=EmployeePerformanceSummary)
def get_employee_summary(employee_id: int):
    return performance_service.get_employee_summary(employee_id)
