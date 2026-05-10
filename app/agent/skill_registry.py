from __future__ import annotations

from app.agent.protocol import AgentTool, Skill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._tool_to_skill: dict[str, str] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill '{skill.name}' already registered")
        for tool in skill.tools:
            if tool.name in self._tool_to_skill:
                raise ValueError(
                    f"Tool '{tool.name}' already belongs to skill "
                    f"'{self._tool_to_skill[tool.name]}'"
                )
        for wf_name in skill.workflows:
            if wf_name in self._tool_to_skill:
                raise ValueError(
                    f"Workflow '{wf_name}' conflicts with existing tool/skill name "
                    f"in '{self._tool_to_skill[wf_name]}'"
                )
        self._skills[skill.name] = skill
        for tool in skill.tools:
            self._tool_to_skill[tool.name] = skill.name
        for wf_name in skill.workflows:
            self._tool_to_skill[wf_name] = skill.name

    def unregister(self, skill_name: str) -> None:
        skill = self._skills.pop(skill_name, None)
        if skill:
            for tool in skill.tools:
                self._tool_to_skill.pop(tool.name, None)
            for wf_name in skill.workflows:
                self._tool_to_skill.pop(wf_name, None)

    def get_skill(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def get_skill_for_tool(self, tool_name: str) -> Skill | None:
        skill_name = self._tool_to_skill.get(tool_name)
        return self._skills.get(skill_name) if skill_name else None

    def get_all_tools(self) -> list[AgentTool]:
        tools: list[AgentTool] = []
        for skill in self._skills.values():
            if skill.enabled:
                tools.extend(skill.tools)
        return tools

    def get_tool_map(self) -> dict[str, AgentTool]:
        result: dict[str, AgentTool] = {}
        for skill in self._skills.values():
            if skill.enabled:
                for tool in skill.tools:
                    result[tool.name] = tool
        return result

    def get_skill_summaries(self) -> list[dict]:
        return [
            s.to_openai_skill_summary()
            for s in self._skills.values()
            if s.enabled
        ]

    def get_tools_for_skills(self, skill_names: list[str]) -> list[AgentTool]:
        tools: list[AgentTool] = []
        for name in skill_names:
            skill = self._skills.get(name)
            if skill and skill.enabled:
                tools.extend(skill.tools)
        return tools

    def get_workflows_for_skills(self, skill_names: list[str]) -> dict[str, Skill]:
        result: dict[str, Skill] = {}
        for name in skill_names:
            skill = self._skills.get(name)
            if skill and skill.enabled and skill.workflows:
                for wf_name in skill.workflows:
                    result[wf_name] = skill
        return result

    def enable(self, skill_name: str) -> bool:
        skill = self._skills.get(skill_name)
        if skill:
            skill.enabled = True
            return True
        return False

    def disable(self, skill_name: str) -> bool:
        skill = self._skills.get(skill_name)
        if skill:
            skill.enabled = False
            return True
        return False

    def list_skills(self) -> list[dict]:
        return [
            {
                "name": s.name,
                "description": s.description,
                "enabled": s.enabled,
                "tool_count": len(s.tools),
                "workflow_count": len(s.workflows),
            }
            for s in self._skills.values()
        ]
