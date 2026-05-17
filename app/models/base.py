"""模型层通用辅助函数。"""

from sqlalchemy import inspect as sa_inspect


def _to_dict(self) -> dict:
    """将 SQLAlchemy 实体当前列值转换为普通字典。"""
    return {c.key: getattr(self, c.key) for c in sa_inspect(self).mapper.column_attrs}
