"""组织单元模型。"""

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class OrgUnit(Base):
    """组织单元主档，当前主要用于表达部门信息。"""

    __tablename__ = "departments"
    __table_args__ = (UniqueConstraint("name", name="uq_departments_name"),)

    # 主键与唯一名称。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # 说明性信息。
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    manager: Mapped[str | None] = mapped_column(String, nullable=True)

    to_dict = _to_dict


# 兼容旧命名，避免影响现有 service/repository/schema 代码。
Department = OrgUnit
