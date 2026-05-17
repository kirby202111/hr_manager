"""安全培训与合规模型。"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class SafetyTraining(Base):
    """安全培训课程主数据。"""

    __tablename__ = "safety_trainings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    required_for_certification_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validity_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkerSafetyRecord(Base):
    """员工安全培训完成记录，用于判断上岗安全状态。"""

    __tablename__ = "worker_safety_records"
    __table_args__ = (Index("ix_worker_safety_records_worker_id", "worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    training_id: Mapped[int] = mapped_column(Integer, nullable=False)
    completed_at: Mapped[date] = mapped_column(Date, nullable=False)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
