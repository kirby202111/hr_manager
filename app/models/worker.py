"""员工主数据模型。"""

from sqlalchemy import Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Worker(Base):
    """员工主档，承载人员基础信息与部门归属。"""

    __tablename__ = "employees"
    __table_args__ = (Index("ix_employees_department_id", "department_id"),)

    # 主键与基础身份信息。
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # 组织归属与薪资基线。
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    to_dict = _to_dict
