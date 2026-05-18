"""Agent runtime skill registration."""

from app.agent.protocol import AgentSkill
from app.agent.skill_registry import SkillRegistry
from app.agent.skills.attendance import skill as attendance_skill
from app.agent.skills.capability import skill as capability_skill
from app.agent.skills.collaboration import skill as collaboration_skill
from app.agent.skills.knowledge_base import skill as knowledge_base_skill
from app.agent.skills.memory import skill as memory_skill
from app.agent.skills.workforce import skill as workforce_skill

ALL_SKILLS: list[AgentSkill] = [
    workforce_skill,
    attendance_skill,
    capability_skill,
    collaboration_skill,
    knowledge_base_skill,
    memory_skill,
]


def register_all_skills(registry: SkillRegistry) -> None:
    for skill in ALL_SKILLS:
        registry.register(skill)


__all__ = ["ALL_SKILLS", "register_all_skills"]
