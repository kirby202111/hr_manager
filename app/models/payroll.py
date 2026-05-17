"""薪资模型。"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Payroll(Base):
    """员工月度薪资单，保存基础工资、奖扣项和发薪状态。"""

    __tablename__ = "payrolls"
    __table_args__ = (
        UniqueConstraint("worker_id", "month", name="uq_payrolls_worker_month"),
        Index("ix_payrolls_worker_month", "worker_id", "month"),
    )

    # 一名员工每月一张薪资单。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[str] = mapped_column(String, nullable=False)

    # 薪资金额字段。
    base_salary: Mapped[float] = mapped_column(Float, nullable=False)
    bonuses: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    deductions: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    net_salary: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
