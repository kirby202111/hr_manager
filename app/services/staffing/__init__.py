"""Service module."""

from app.services.staffing import shift_assignment, shift_plan, shift_template

_MODULES = (shift_assignment, shift_plan, shift_template)

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
