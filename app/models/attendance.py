from datetime import date, time

from sqlalchemy import Date, Float, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    check_in: Mapped[time] = mapped_column(Time, nullable=False)
    check_out: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    work_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    to_dict = _to_dict
