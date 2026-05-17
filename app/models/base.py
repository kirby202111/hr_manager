"""业务模型公共基础设施。"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "pk": "pk_%(table_name)s",
}

# 统一约束/索引命名，便于后续迁移和排查数据库对象。
Base.metadata.naming_convention = NAMING_CONVENTION
Base.metadata.info.setdefault("domain", "workforce_ops")


class DictMixin:
    """只序列化当前表列，不展开 relationship。"""

    def to_dict(self) -> dict:
        return {column.key: getattr(self, column.key) for column in sa_inspect(self).mapper.column_attrs}


class IdentityMixin:
    """整型自增主键。"""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimestampMixin:
    """统一的创建/更新时间戳。"""

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


__all__ = [
    "Base",
    "DictMixin",
    "IdentityMixin",
    "MetaData",
    "NAMING_CONVENTION",
    "TimestampMixin",
]
