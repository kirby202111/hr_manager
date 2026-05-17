"""员工生产现场画像模型。"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class WorkerTeamAssignment(Base):
    """员工班组归属历史，支持主归属与临时支援记录。"""

    __tablename__ = "worker_team_assignments"
    __table_args__ = (Index("ix_worker_team_assignments_worker_id", "worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False)
    line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkerProductionProfile(Base):
    """员工生产画像，保存现场角色、状态和可支援产线。"""

    __tablename__ = "worker_production_profiles"
    __table_args__ = (UniqueConstraint("worker_id", name="uq_worker_production_profiles_worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_type: Mapped[str] = mapped_column(String(30), nullable=False)
    production_status: Mapped[str] = mapped_column(String(20), nullable=False)
    can_support_lines: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
