"""资质与设备授权模型。"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Certification(Base):
    """证书主数据，定义培训学时、有效期和适用类别。"""

    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    required_training_hours: Mapped[float] = mapped_column(Float, nullable=False)
    validity_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkerCertification(Base):
    """员工持证记录，用于校验证书有效性和到期时间。"""

    __tablename__ = "worker_certifications"
    __table_args__ = (Index("ix_worker_certifications_worker_id", "worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    certification_id: Mapped[int] = mapped_column(Integer, nullable=False)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    evidence: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class EquipmentAuthorization(Base):
    """设备操作授权记录，用于校验特定设备的操作等级。"""

    __tablename__ = "equipment_authorizations"
    __table_args__ = (Index("ix_equipment_authorizations_worker_id", "worker_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_code: Mapped[str] = mapped_column(String(100), nullable=False)
    authorization_level: Mapped[str] = mapped_column(String(20), nullable=False)
    issued_at: Mapped[date] = mapped_column(Date, nullable=False)
    expires_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
