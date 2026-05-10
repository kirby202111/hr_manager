from __future__ import annotations

import json
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

ROUTING_SYSTEM_PROMPT = """你是一个技能路由器。根据用户的问题，判断需要激活哪些技能。

可用技能:
{skill_summaries}

请只返回需要激活的技能名称列表。如果用户的问题只需要闲聊或一般性问题，返回空数组。

示例：
- 用户问"帮我办理新员工入职" -> ["employee_onboarding"]
- 用户问"张三这个月考勤怎么样" -> ["attendance_management"]
- 用户问"帮我生成本月工资并查看考勤异常" -> ["payroll_processing", "attendance_management"]
- 用户问"你好" -> []
"""

ROUTING_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "skills": {
            "type": "array",
            "items": {"type": "string"},
            "description": "需要激活的技能名称列表",
        }
    },
    "required": ["skills"],
}


class SkillRouter:
    def __init__(self, client: OpenAI, model: str) -> None:
        self._client = client
        self._model = model

    def route(self, message: str, skill_summaries: list[dict]) -> list[str]:
        if not skill_summaries:
            return []

        summaries_text = "\n".join(
            f"- {s['name']}: {s['description']}。适用场景: {s['applicability']}"
            for s in skill_summaries
        )

        system_prompt = ROUTING_SYSTEM_PROMPT.format(
            skill_summaries=summaries_text
        )

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "select_skills",
                        "description": "选择需要激活的技能",
                        "parameters": ROUTING_OUTPUT_SCHEMA,
                    },
                }],
                tool_choice={"type": "function", "function": {"name": "select_skills"}},
                temperature=0.0,
            )

            tool_call = response.choices[0].message.tool_calls[0]
            result = json.loads(tool_call.function.arguments)
            return result.get("skills", [])

        except Exception:
            logger.warning("Skill routing failed, falling back to all skills", exc_info=True)
            return [s["name"] for s in skill_summaries]
