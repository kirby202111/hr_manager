"""生产工单模型。"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class ProductionOrder(Base):
    """生产工单主表，描述生产目标、时间窗口和优先级。"""

    __tablename__ = "production_orders"
    __table_args__ = (UniqueConstraint("order_no", name="uq_production_orders_order_no"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(100), nullable=False)
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    line_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class ProductionOrderOperation(Base):
    """工单工序表，将工单拆解到具体工位与人力需求。"""

    __tablename__ = "production_order_operations"
    __table_args__ = (Index("ix_production_order_operations_order_id", "order_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(Integer, nullable=False)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    process_code: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_headcount: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
