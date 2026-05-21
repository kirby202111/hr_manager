"""Heuristic skill router for agent runtime."""

from __future__ import annotations

import re

from app.agent.protocol import AgentSkill, SkillMatch


class SkillRouter:
    """Resolve likely skills from user messages using structured heuristics."""

    def __init__(self, default_skill: str = "memory", max_selected_skills: int = 3) -> None:
        self._default_skill = default_skill
        self._max_selected_skills = max_selected_skills

    def route(
        self,
        message: str,
        skills: list[AgentSkill],
        *,
        forced_skill_names: list[str] | None = None,
    ) -> list[SkillMatch]:
        normalized = message.lower()
        forced = set(forced_skill_names or [])
        matches: list[SkillMatch] = []

        for skill in skills:
            if not skill.enabled:
                continue
            if skill.name in forced:
                matches.append(
                    SkillMatch(
                        skill_name=skill.name,
                        reason="runtime_override",
                        priority=self._priority_for(skill, forced=True),
                        match_type="forced",
                    )
                )
                continue

            reason = self._match_reason(normalized, skill)
            if reason is None:
                continue
            matches.append(
                SkillMatch(
                    skill_name=skill.name,
                    reason=reason,
                    priority=self._priority_for(skill),
                    match_type="strong",
                )
            )

        forced_matches = [match for match in matches if match.match_type == "forced"]
        strong_matches = [match for match in matches if match.match_type == "strong"]
        strong_matches.sort(key=lambda item: (-item.priority, item.skill_name))

        if forced_matches or strong_matches:
            ordered = forced_matches + strong_matches
            return ordered[: self._max_selected_skills]

        fallback_skill = next(
            (
                skill
                for skill in skills
                if skill.enabled and (skill.metadata.get("default", False) or skill.name == self._default_skill)
            ),
            None,
        )
        if fallback_skill is None:
            return []
        return [
            SkillMatch(
                skill_name=fallback_skill.name,
                reason="default_skill",
                priority=self._priority_for(fallback_skill),
                match_type="fallback",
            )
        ]

    @staticmethod
    def _priority_for(skill: AgentSkill, *, forced: bool = False) -> int:
        base_priority = int(skill.metadata.get("priority", 50))
        return base_priority + 1000 if forced else base_priority

    @staticmethod
    def _match_reason(message: str, skill: AgentSkill) -> str | None:
        routing_hints = skill.metadata.get("routing_hints", [])
        for hint in routing_hints:
            if isinstance(hint, str) and hint.lower() in message:
                return f"routing_hint:{hint}"
        for keyword in skill.keywords:
            if keyword.lower() in message:
                return f"keyword:{keyword}"
        name_tokens = [token for token in re.split(r"[_\-\s]+", skill.name.lower()) if token]
        matched_token = next((token for token in name_tokens if token in message), None)
        if matched_token:
            return f"name_token:{matched_token}"
        return None


__all__ = ["SkillRouter"]
