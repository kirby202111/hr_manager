"""Agent runtime skill registration."""

from app.agent.protocol import AgentSkill
from app.agent.skill_registry import SkillRegistry
from app.agent.skills.attendance import skill as attendance_skill
from app.agent.skills.capability import skill as capability_skill
from app.agent.skills.knowledge_base import skill as knowledge_base_skill
from app.agent.skills.memory import skill as memory_skill
from app.agent.skills.operations import skill as operations_skill
from app.agent.skills.qualification import skill as qualification_skill
from app.agent.skills.workforce import skill as workforce_skill
from app.agent.skills.onboarding import skill as onboarding_skill

ALL_SKILLS: list[AgentSkill] = [
    onboarding_skill,
    workforce_skill,
    capability_skill,
    attendance_skill,
    qualification_skill,
    operations_skill,
    knowledge_base_skill,
    memory_skill,
]


def register_all_skills(registry: SkillRegistry) -> None:
    for skill in ALL_SKILLS:
        registry.register(skill)


__all__ = ["ALL_SKILLS", "register_all_skills"]
