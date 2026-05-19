"""Agent runtime skill registration."""

from app.agent.protocol import AgentSkill
from app.agent.skill_registry import SkillRegistry
from app.agent.skills.memory import skill as memory_skill

ALL_SKILLS: list[AgentSkill] = [
    memory_skill,
]


def register_all_skills(registry: SkillRegistry) -> None:
    for skill in ALL_SKILLS:
        registry.register(skill)


__all__ = ["ALL_SKILLS", "register_all_skills"]
