from app.schemas import attendance as attendance_schemas
from app.schemas import capability as capability_schemas
from app.schemas import organization as organization_schemas
from app.schemas import production as production_schemas
from app.schemas import qualification as qualification_schemas
from app.schemas import risk as risk_schemas
from app.schemas import shopfloor as shopfloor_schemas
from app.schemas import staffing as staffing_schemas
from app.schemas import workforce as workforce_schemas

_MODULES = (
    attendance_schemas,
    capability_schemas,
    organization_schemas,
    production_schemas,
    qualification_schemas,
    risk_schemas,
    shopfloor_schemas,
    staffing_schemas,
    workforce_schemas,
)

_SCHEMA_SUFFIXES = ("Create", "Update", "Response", "ListResponse")

for _module in _MODULES:
    for _name in dir(_module):
        if not _name.endswith(_SCHEMA_SUFFIXES):
            continue
        globals()[_name] = getattr(_module, _name)

__all__ = [
    name
    for module in _MODULES
    for name in dir(module)
    if name.endswith(_SCHEMA_SUFFIXES)
]
