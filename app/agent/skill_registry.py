"""Agent skill registry."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool, SkillMatch


class SkillRegistry:
    """Register, discover, and toggle agent skills."""

    def __init__(self) -> None:
        self._skills: dict[str, AgentSkill] = {}
        self._tool_to_skill: dict[str, str] = {}

    def register(self, skill: AgentSkill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already registered")
        for tool in skill.tools:
            if tool.name in self._tool_to_skill:
                raise ValueError(f"Tool '{tool.name}' already registered by skill '{self._tool_to_skill[tool.name]}'")
        self._skills[skill.name] = skill
        for tool in skill.tools:
            self._tool_to_skill[tool.name] = skill.name

    def get_skill(self, name: str) -> AgentSkill | None:
        return self._skills.get(name)

    def get_enabled_skills(self) -> list[AgentSkill]:
        return [skill for skill in self._skills.values() if skill.enabled]

    def get_all_tools(self) -> list[AgentTool]:
        tools: list[AgentTool] = []
        for skill in self.get_enabled_skills():
            tools.extend(skill.tools)
        return tools

    def get_tool_map(self) -> dict[str, AgentTool]:
        return {tool.name: tool for tool in self.get_all_tools()}

    def get_tools_for_skills(self, skill_names: list[str]) -> list[AgentTool]:
        tools: list[AgentTool] = []
        seen: set[str] = set()
        for skill_name in skill_names:
            skill = self._skills.get(skill_name)
            if skill and skill.enabled:
                for tool in skill.tools:
                    if tool.name in seen:
                        continue
                    seen.add(tool.name)
                    tools.append(tool)
        return tools

    def get_tools_for_matches(self, matches: list[SkillMatch]) -> list[AgentTool]:
        return self.get_tools_for_skills([match.skill_name for match in matches])

    def list_skills(self) -> list[dict]:
        return [skill.to_summary() for skill in self._skills.values()]

    def enable(self, skill_name: str) -> bool:
        skill = self._skills.get(skill_name)
        if skill is None:
            return False
        skill.enabled = True
        return True

    def disable(self, skill_name: str) -> bool:
        skill = self._skills.get(skill_name)
        if skill is None:
            return False
        skill.enabled = False
        return True


__all__ = ["SkillRegistry"]
