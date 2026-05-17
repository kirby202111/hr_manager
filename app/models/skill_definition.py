"""技能定义模型。"""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class SkillDefinition(Base):
    """技能标准项，用于统一员工技能、工位要求与项目要求。"""

    __tablename__ = "skill_catalogs"

    # 技能标识与基础属性。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    to_dict = _to_dict


# 兼容旧命名，避免影响现有 service/repository/schema 代码。
SkillCatalog = SkillDefinition
