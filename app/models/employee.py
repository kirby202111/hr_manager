from sqlalchemy import Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import _to_dict


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (Index("ix_employees_department_id", "department_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary: Mapped[float] = mapped_column(Float, nullable=False)

    to_dict = _to_dict
