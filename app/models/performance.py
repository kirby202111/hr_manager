from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class PerformanceCycle(Base):
    __tablename__ = "performance_cycles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    cycle_id: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    rating_level: Mapped[str] = mapped_column(String, nullable=False)
    reviewer: Mapped[str] = mapped_column(String, nullable=False)
    comments: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
