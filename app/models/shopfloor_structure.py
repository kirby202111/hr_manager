"""生产现场结构模型。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class ProductionLine(Base):
    """产线主档，定义现场生产线及其所属部门。"""

    __tablename__ = "production_lines"
    __table_args__ = (Index("ix_production_lines_department_id", "department_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, nullable=False)
    supervisor_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class ProductionTeam(Base):
    """班组主档，描述产线下的人员组织单元。"""

    __tablename__ = "production_teams"
    __table_args__ = (Index("ix_production_teams_line_id", "line_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    leader_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shift_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class Workstation(Base):
    """工位主档，定义现场岗位、编码和风险等级。"""

    __tablename__ = "workstations"
    __table_args__ = (
        UniqueConstraint("line_id", "code", name="uq_workstations_line_code"),
        Index("ix_workstations_line_id", "line_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    line_id: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkstationRequiredSkill(Base):
    """工位技能要求，约束上岗人员的最低技能水平。"""

    __tablename__ = "workstation_required_skills"
    __table_args__ = (Index("ix_workstation_required_skills_workstation_id", "workstation_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_id: Mapped[int] = mapped_column(Integer, nullable=False)
    required_proficiency: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkstationRequiredCertification(Base):
    """工位资质要求，约束上岗人员必须持有的证书。"""

    __tablename__ = "workstation_required_certifications"
    __table_args__ = (Index("ix_workstation_required_certifications_workstation_id", "workstation_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    certification_id: Mapped[int] = mapped_column(Integer, nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


class WorkstationEquipmentRequirement(Base):
    """工位设备授权要求，约束操作相关设备所需等级。"""

    __tablename__ = "workstation_equipment_requirements"
    __table_args__ = (Index("ix_workstation_equipment_requirements_workstation_id", "workstation_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workstation_id: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_code: Mapped[str] = mapped_column(String(100), nullable=False)
    required_authorization_level: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
