from app.agent.protocol import Skill
from app.agent.skill_registry import SkillRegistry
from app.agent.skills.core import skill as core_skill
from app.agent.skills.onboarding import skill as onboarding_skill
from app.agent.skills.leave import skill as leave_skill
from app.agent.skills.attendance import skill as attendance_skill
from app.agent.skills.payroll import skill as payroll_skill
from app.agent.skills.performance import skill as performance_skill
from app.agent.skills.analytics import skill as analytics_skill


_ALL_SKILLS: list[Skill] = [
    core_skill,
    onboarding_skill,
    leave_skill,
    attendance_skill,
    payroll_skill,
    performance_skill,
    analytics_skill,
]


def register_all_skills(registry: SkillRegistry) -> None:
    for skill in _ALL_SKILLS:
        registry.register(skill)
