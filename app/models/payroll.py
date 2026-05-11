from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Payroll(Base):
    __tablename__ = "payrolls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[str] = mapped_column(String, nullable=False)
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    bonuses: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    deductions: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    net_salary: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
