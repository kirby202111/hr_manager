"""业务服务层统一导出入口。"""

from app.services import attendance as attendance_services
from app.services import capability as capability_services
from app.services import collaboration as collaboration_services
from app.services import organization as organization_services
from app.services import qualification as qualification_services
from app.services import shopfloor as shopfloor_services
from app.services import staffing as staffing_services
from app.services import workforce as workforce_services

_MODULES = (
    attendance_services,
    capability_services,
    collaboration_services,
    organization_services,
    qualification_services,
    shopfloor_services,
    staffing_services,
    workforce_services,
)

for _module in _MODULES:
    for _name in dir(_module):
        if not _name.startswith(("create_", "delete_", "get_", "list_", "update_")):
            continue
        globals()[_name] = getattr(_module, _name)

__all__ = [
    name
    for module in _MODULES
    for name in dir(module)
    if name.startswith(("create_", "delete_", "get_", "list_", "update_"))
]
