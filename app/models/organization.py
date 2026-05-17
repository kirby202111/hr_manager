"""组织域模型。"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship, remote

from app.models.base import Base, DictMixin, IdentityMixin, TimestampMixin

ORM_EVAL_HELPERS = {"foreign": foreign, "remote": remote}

if TYPE_CHECKING:
    from app.models.shopfloor import ProductionLine
    from app.models.workforce import Worker, WorkerAssignment


class OrganizationUnit(Base, IdentityMixin, TimestampMixin, DictMixin):
    """制造现场中的组织单元，如工厂、部门、车间等。"""

    __tablename__ = "organization_units"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    unit_type: Mapped[str] = mapped_column(String(30), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manager_worker_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 组织层级和负责人都在 ORM 层表达，不依赖数据库外键。
    parent: Mapped[OrganizationUnit | None] = relationship(
        "OrganizationUnit",
        remote_side="OrganizationUnit.id",
        back_populates="children",
        primaryjoin="remote(OrganizationUnit.id) == foreign(OrganizationUnit.parent_id)",
        foreign_keys="OrganizationUnit.parent_id",
    )
    children: Mapped[list[OrganizationUnit]] = relationship(
        "OrganizationUnit",
        back_populates="parent",
        primaryjoin="OrganizationUnit.id == foreign(OrganizationUnit.parent_id)",
        foreign_keys="OrganizationUnit.parent_id",
    )
    manager: Mapped[Worker | None] = relationship(
        "Worker",
        back_populates="managed_units",
        primaryjoin="foreign(OrganizationUnit.manager_worker_id) == Worker.id",
        foreign_keys=[manager_worker_id],
    )
    # 下挂业务实体：人员、任职记录、产线。
    workers: Mapped[list[Worker]] = relationship("Worker", back_populates="organization_unit")
    worker_assignments: Mapped[list[WorkerAssignment]] = relationship(
        "WorkerAssignment",
        back_populates="organization_unit",
    )
    production_lines: Mapped[list[ProductionLine]] = relationship(
        "ProductionLine",
        back_populates="organization_unit",
    )


__all__ = ["OrganizationUnit"]
