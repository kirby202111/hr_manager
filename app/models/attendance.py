"""考勤模型。"""

from datetime import date, time

from sqlalchemy import Date, Float, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Attendance(Base):
    """按员工与日期记录签到、签退和工时结果。"""

    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint("worker_id", "date", name="uq_attendance_worker_date"),
        Index("ix_attendance_worker_date", "worker_id", "date"),
    )

    # 一天只能有一条考勤主记录。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    # 上下班时间与考勤结论。
    check_in: Mapped[time] = mapped_column(Time, nullable=False)
    check_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    work_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    to_dict = _to_dict
