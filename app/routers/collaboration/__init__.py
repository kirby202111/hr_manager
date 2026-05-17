"""协同域路由聚合。"""

from fastapi import APIRouter

from app.routers.collaboration import project, project_member, project_skill_requirement, project_timesheet_entry

router = APIRouter()
router.include_router(project.router)
router.include_router(project_member.router)
router.include_router(project_skill_requirement.router)
router.include_router(project_timesheet_entry.router)

__all__ = ["router"]
