"""协同域服务导出。"""

from app.services.collaboration import (
    project,
    project_member,
    project_skill_requirement,
    project_timesheet_entry,
)

_MODULES = (project, project_member, project_skill_requirement, project_timesheet_entry)

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
