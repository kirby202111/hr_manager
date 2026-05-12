from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from openai import OpenAI, APIError, RateLimitError, APITimeoutError

from app.config import settings
from app.agent.protocol import AgentTool, BaseHistoryStore
from app.agent.skill_registry import SkillRegistry
from app.agent.skill_router import SkillRouter

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的HR管理助手。你可以帮助用户查询员工信息、考勤记录、请假情况、薪资数据和绩效评估等。

你的职责：
1. 理解用户用自然语言提出的问题
2. 调用相应的工具获取数据
3. 用清晰、专业的中文回答用户的问题

你可以执行以下操作：
- 查询：员工、部门、考勤、请假、薪资、绩效等各类数据
- 操作：创建员工、提交/审批请假、签到签退、生成/支付薪资、提交绩效评分等
- 分析：薪资分布、考勤异常、请假趋势、绩效分布等
- 工作流：新员工入职等组合操作

注意事项：
- 回答时使用中文
- 如果数据量很大，只展示摘要和关键信息
- 如果工具返回错误信息，向用户解释错误原因
- 执行操作前请确认用户意图，避免误操作
- 对于多步骤操作，先查询数据再逐个操作
- 不要编造数据，只使用工具返回的真实数据
"""


def _workflow_to_tool(wf_name: str, wf_fn) -> AgentTool:
    return AgentTool(
        name=wf_name,
        description=wf_fn.__doc__ or f"Execute {wf_name} workflow",
        parameters={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "员工姓名"},
                "salary": {"type": "number", "description": "月薪"},
                "department_id": {"type": "integer", "description": "部门ID（可选）"},
            },
            "required": ["name", "salary"],
        },
        fn=wf_fn,
    )


class ReActAgent:
    def __init__(
        self,
        history_store: BaseHistoryStore,
        skill_registry: SkillRegistry,
        use_routing: bool = True,
    ) -> None:
        self._history = history_store
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self._registry = skill_registry
        self._router = SkillRouter(self._client, settings.deepseek_model)
        self._use_routing = use_routing

    def _init_session(self, session_id: str) -> None:
        msgs = self._history.get_messages(session_id)
        if not msgs:
            self._history.add_message(session_id, {"role": "system", "content": SYSTEM_PROMPT})

    def _resolve_tools(self, message: str) -> tuple[list[dict], dict[str, AgentTool]]:
        if not self._use_routing:
            all_tools = self._registry.get_all_tools()
            tool_map = self._registry.get_tool_map()
            return [t.to_openai_tool() for t in all_tools], tool_map

        skill_names = self._router.route(
            message, self._registry.get_skill_summaries()
        )

        if not skill_names:
            skill_names = ["employee_management"]

        activated_tools = self._registry.get_tools_for_skills(skill_names)
        tool_map: dict[str, AgentTool] = {t.name: t for t in activated_tools}

        workflows_map = self._registry.get_workflows_for_skills(skill_names)
        for wf_name, skill in workflows_map.items():
            wf_fn = skill.workflows[wf_name]
            wf_tool = _workflow_to_tool(wf_name, wf_fn)
            activated_tools.append(wf_tool)
            tool_map[wf_name] = wf_tool

        logger.info("Activated skills: %s, tools: %s", skill_names, list(tool_map.keys()))
        return [t.to_openai_tool() for t in activated_tools], tool_map

    def chat(self, session_id: str, message: str) -> str:
        self._init_session(session_id)
        self._history.add_message(session_id, {"role": "user", "content": message})
        messages = self._history.get_messages(session_id)

        tools, tool_map = self._resolve_tools(message)

        for _ in range(settings.agent_max_iterations):
            try:
                response = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=messages,
                    tools=tools,
                    temperature=0.3,
                )
            except RateLimitError:
                return "API调用频率超限，请稍后重试"
            except APITimeoutError:
                return "AI服务响应超时，请稍后重试"
            except APIError as e:
                return f"AI服务错误: {e.message}"

            choice = response.choices[0]
            assistant_msg = choice.message.model_dump()
            if getattr(choice.message, "reasoning_content", None):
                assistant_msg["reasoning_content"] = choice.message.reasoning_content
            self._history.add_message(session_id, assistant_msg)
            messages = self._history.get_messages(session_id)

            if not assistant_msg.get("tool_calls"):
                return assistant_msg.get("content") or ""

            for tool_call in assistant_msg["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                tool = tool_map.get(func_name)
                if tool is None:
                    result = {"error": f"未知工具: {func_name}"}
                else:
                    try:
                        result = tool.fn(**func_args)
                    except Exception as e:
                        result = {"error": f"工具执行错误: {str(e)}"}

                self._history.add_message(session_id, {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
                messages = self._history.get_messages(session_id)

        return "抱歉，处理过程中超出了最大迭代次数，请简化您的问题后重试。"

    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[dict]:
        self._init_session(session_id)
        self._history.add_message(session_id, {"role": "user", "content": message})

        tools, tool_map = self._resolve_tools(message)

        for _ in range(settings.agent_max_iterations):
            messages = self._history.get_messages(session_id)
            try:
                stream = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=messages,
                    tools=tools,
                    temperature=0.3,
                    stream=True,
                )
            except RateLimitError:
                yield {"event": "error", "data": "API调用频率超限，请稍后重试"}
                return
            except APITimeoutError:
                yield {"event": "error", "data": "AI服务响应超时，请稍后重试"}
                return
            except APIError as e:
                yield {"event": "error", "data": f"AI服务错误: {e.message}"}
                return

            assistant_content = ""
            reasoning_content = ""
            tool_calls_accum: dict[int, dict] = {}

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                if delta.content:
                    yield {"event": "message", "data": delta.content}
                    assistant_content += delta.content

                if getattr(delta, "reasoning_content", None):
                    reasoning_content += delta.reasoning_content

                if delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        if idx not in tool_calls_accum:
                            tool_calls_accum[idx] = {"id": "", "name": "", "arguments": ""}
                        if tc_delta.id:
                            tool_calls_accum[idx]["id"] += tc_delta.id
                        if tc_delta.function:
                            if tc_delta.function.name:
                                tool_calls_accum[idx]["name"] += tc_delta.function.name
                            if tc_delta.function.arguments:
                                tool_calls_accum[idx]["arguments"] += tc_delta.function.arguments

            assistant_msg: dict = {"role": "assistant", "content": assistant_content or None}
            if reasoning_content:
                assistant_msg["reasoning_content"] = reasoning_content
            if tool_calls_accum:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": tc["arguments"]},
                    }
                    for _, tc in sorted(tool_calls_accum.items())
                ]
            self._history.add_message(session_id, assistant_msg)

            if not tool_calls_accum:
                yield {"event": "done", "data": ""}
                return

            tool_names = [tc["name"] for tc in tool_calls_accum.values()]
            yield {"event": "tool_call", "data": json.dumps(tool_names, ensure_ascii=False)}

            for idx in sorted(tool_calls_accum.keys()):
                tc = tool_calls_accum[idx]
                func_name = tc["name"]
                func_args = json.loads(tc["arguments"])
                tool = tool_map.get(func_name)
                if tool is None:
                    result = {"error": f"未知工具: {func_name}"}
                else:
                    try:
                        result = tool.fn(**func_args)
                    except Exception as e:
                        result = {"error": f"工具执行错误: {str(e)}"}

                self._history.add_message(session_id, {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })

            yield {"event": "tool_result", "data": json.dumps(
                [tc["name"] for tc in tool_calls_accum.values()],
                ensure_ascii=False,
            )}

        yield {"event": "error", "data": "超出最大迭代次数"}
