"""Repository exports."""

from app.repositories import attendance as attendance_repositories
from app.repositories import capability as capability_repositories
from app.repositories import organization as organization_repositories
from app.repositories import production as production_repositories
from app.repositories import qualification as qualification_repositories
from app.repositories import risk as risk_repositories
from app.repositories import shopfloor as shopfloor_repositories
from app.repositories import staffing as staffing_repositories
from app.repositories import workforce as workforce_repositories

_MODULES = (
    attendance_repositories,
    capability_repositories,
    organization_repositories,
    production_repositories,
    qualification_repositories,
    risk_repositories,
    shopfloor_repositories,
    staffing_repositories,
    workforce_repositories,
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
