"""班次、排班计划与排班分配模型。"""

from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class ShiftDefinition(Base):
    """班次模板，描述时间窗口和班次津贴系数。"""

    __tablename__ = "shift_definitions"
    __table_args__ = (UniqueConstraint("code", name="uq_shift_definitions_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False)
    allowance_rate: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class ProductionShiftPlan(Base):
    """排班计划主表，描述某产线某日期某班次的人力需求。"""

    __tablename__ = "production_shift_plans"
    __table_args__ = (Index("ix_production_shift_plans_line_date_shift", "line_id", "work_date", "shift_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    shift_id: Mapped[int] = mapped_column(Integer, nullable=False)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkerShiftAssignment(Base):
    """排班明细，记录员工被分配到哪个计划和工位。"""

    __tablename__ = "worker_shift_assignments"
    __table_args__ = (Index("ix_worker_shift_assignments_plan_worker", "plan_id", "worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assignment_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
