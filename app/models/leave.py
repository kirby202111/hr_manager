"""请假模型。"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Leave(Base):
    """员工请假申请与审批流转记录。"""

    __tablename__ = "leaves"
    __table_args__ = (Index("ix_leaves_worker_status_dates", "worker_id", "status", "start_date", "end_date"),)

    # 请假主体与假别信息。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    leave_type: Mapped[str] = mapped_column(String, nullable=False)
    leave_type_name: Mapped[str] = mapped_column(String, nullable=False)

    # 日期区间与审批结果。
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    approver: Mapped[str | None] = mapped_column(String, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
