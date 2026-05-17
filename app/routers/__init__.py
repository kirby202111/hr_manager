"""业务路由层统一导出入口。"""

from app.routers import (
    attendance,
    capability,
    collaboration,
    organization,
    qualification,
    shopfloor,
    staffing,
    workforce,
)

__all__ = [
    "attendance",
    "capability",
    "collaboration",
    "organization",
    "qualification",
    "shopfloor",
    "staffing",
    "workforce",
]
