"""Heuristic skill router for agent runtime."""

from __future__ import annotations

import re

from app.agent.protocol import AgentSkill


class SkillRouter:
    """Resolve likely skills from user messages using local heuristics."""

    def __init__(self, default_skill: str = "memory") -> None:
        self._default_skill = default_skill

    def route(self, message: str, skills: list[AgentSkill]) -> list[str]:
        normalized = message.lower()
        matched: list[str] = []
        for skill in skills:
            if not skill.enabled:
                continue
            if self._matches_skill(normalized, skill):
                matched.append(skill.name)
        if not matched and any(skill.name == self._default_skill and skill.enabled for skill in skills):
            return [self._default_skill]
        return matched

    @staticmethod
    def _matches_skill(message: str, skill: AgentSkill) -> bool:
        if any(keyword.lower() in message for keyword in skill.keywords):
            return True
        name_tokens = [token for token in re.split(r"[_\-\s]+", skill.name.lower()) if token]
        return any(token in message for token in name_tokens)


__all__ = ["SkillRouter"]
