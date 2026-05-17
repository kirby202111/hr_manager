"""员工技能模型。"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class WorkerSkill(Base):
    """员工技能事实表，记录技能、熟练度和相关经验信息。"""

    __tablename__ = "worker_skills"
    __table_args__ = (
        UniqueConstraint("worker_id", "skill_name", name="uq_worker_skills_worker_skill_name"),
        Index("ix_worker_skills_worker_id", "worker_id"),
        Index("ix_worker_skills_skill_id", "skill_id"),
    )

    # 员工与技能标识。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[int] = mapped_column(Integer, nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # 技能评估信息。
    proficiency_level: Mapped[str] = mapped_column(String(20), nullable=False)
    years_of_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    certification: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict
