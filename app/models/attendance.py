"""履约域模型，覆盖考勤、请假和薪资结果。"""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign}

if TYPE_CHECKING:
    from app.models.workforce import Worker


class AttendanceRecord(Base, IdentityMixin, TimestampMixin, DictMixin):
    """单日考勤记录。"""

    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("worker_id", "work_date"),
        Index("ix_attendance_records_worker_work_date", "worker_id", "work_date"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in_time: Mapped[time] = mapped_column(Time, nullable=False)
    check_out_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    work_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="attendance_records",
        primaryjoin="foreign(AttendanceRecord.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


class LeaveRequest(Base, IdentityMixin, TimestampMixin, DictMixin):
    """请假申请与审批结果。"""

    __tablename__ = "leave_requests"
    __table_args__ = (Index("ix_leave_requests_worker_status_dates", "worker_id", "status", "start_date", "end_date"),)

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    leave_type: Mapped[str] = mapped_column(String(30), nullable=False)
    leave_type_name: Mapped[str] = mapped_column(String(60), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    requested_days: Mapped[int] = mapped_column(nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    approver_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    approved_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="leave_requests",
        primaryjoin="foreign(LeaveRequest.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


class PayrollRecord(Base, IdentityMixin, TimestampMixin, DictMixin):
    """薪资结算结果。"""

    __tablename__ = "payroll_records"
    __table_args__ = (
        UniqueConstraint("worker_id", "pay_period"),
        Index("ix_payroll_records_worker_pay_period", "worker_id", "pay_period"),
    )

    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    pay_period: Mapped[str] = mapped_column(String(20), nullable=False)
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    bonuses: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    deductions: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    net_salary: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="payroll_records",
        primaryjoin="foreign(PayrollRecord.worker_id) == Worker.id",
        foreign_keys=[worker_id],
    )


__all__ = ["AttendanceRecord", "LeaveRequest", "PayrollRecord"]
