from app.agent.protocol import Skill
from app.agent.skill_registry import SkillRegistry
from app.agent.skills.core import skill as core_skill
from app.agent.skills.employee_skill import skill as employee_skill_skill
from app.agent.skills.onboarding import skill as onboarding_skill
from app.agent.skills.leave import skill as leave_skill
from app.agent.skills.attendance import skill as attendance_skill
from app.agent.skills.payroll import skill as payroll_skill
from app.agent.skills.analytics import skill as analytics_skill
from app.agent.skills.knowledge_base import skill as knowledge_base_skill
from app.agent.skills.project import skill as project_skill


_ALL_SKILLS: list[Skill] = [
    core_skill,
    employee_skill_skill,
    onboarding_skill,
    leave_skill,
    attendance_skill,
    payroll_skill,
    analytics_skill,
    knowledge_base_skill,
    project_skill,
]


def register_all_skills(registry: SkillRegistry) -> None:
    for skill in _ALL_SKILLS:
        registry.register(skill)
