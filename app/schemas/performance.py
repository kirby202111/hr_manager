from datetime import date, datetime

from pydantic import BaseModel


def rating_to_level(rating: float) -> str:
    if rating >= 4.5:
        return "excellent"
    if rating >= 3.5:
        return "good"
    if rating >= 2.5:
        return "average"
    return "poor"


# ---- 考核周期 ----

class ReviewCycleCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    description: str | None = None


class ReviewCycleUpdate(BaseModel):
    name: str | None = None
    end_date: date | None = None
    description: str | None = None
    status: str | None = None


class ReviewCycleResponse(BaseModel):
    id: int
    name: str
    start_date: date
    end_date: date
    description: str | None = None
    status: str
    review_count: int = 0
    created_at: datetime


class ReviewCycleListResponse(BaseModel):
    cycles: list[ReviewCycleResponse]
    total: int


# ---- 绩效评分 ----

class PerformanceReviewCreate(BaseModel):
    employee_id: int
    cycle_id: int
    rating: float
    reviewer: str
    comments: str | None = None


class PerformanceReviewUpdate(BaseModel):
    rating: float | None = None
    reviewer: str | None = None
    comments: str | None = None


class PerformanceReviewResponse(BaseModel):
    id: int
    employee_id: int
    employee_name: str
    cycle_id: int
    cycle_name: str
    rating: float
    rating_level: str
    reviewer: str
    comments: str | None = None
    created_at: datetime


class PerformanceReviewListResponse(BaseModel):
    reviews: list[PerformanceReviewResponse]
    total: int


class EmployeePerformanceSummary(BaseModel):
    employee_id: int
    employee_name: str
    average_rating: float
    review_count: int
    latest_rating: float | None = None
    rating_distribution: dict
