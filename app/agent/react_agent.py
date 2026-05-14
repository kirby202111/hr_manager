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

SYSTEM_PROMPT = """你是一个专业的HR管理助手。你可以帮助用户查询员工信息、考勤记录、请假情况、薪资数据等。

你的职责：
1. 理解用户用自然语言提出的问题
2. 调用相应的工具获取数据
3. 用清晰、专业的中文回答用户的问题

你可以执行以下操作：
- 查询：员工、部门、考勤、请假、薪资等各类数据
- 操作：创建员工、提交/审批请假、签到签退、生成/支付薪资等
- 分析：薪资分布、考勤异常、请假趋势等
- 工作流：新员工入职等组合操作

注意事项：
- 回答时使用中文
- 如果数据量很大，只展示摘要和关键信息
- 如果工具返回错误信息，向用户解释错误原因
- 执行操作前请确认用户意图，避免误操作
- 对于多步骤操作，先查询数据再逐个操作
- 不要编造数据，只使用工具返回的真实数据

## 长期记忆使用指南

你拥有长期记忆能力，可以跨会话记住和回忆信息。请遵循以下规则：

1. **对话开始时**：如果用户提供了标识（user_tag），先调用recall_memories回忆相关记忆，了解用户偏好和历史上下文
2. **用户明确要求记住时**：当用户说"记住…"/"帮我记一下…"/"别忘了…"时，立即调用save_memory保存信息，source视为user_instructed
3. **重要业务观察后**：在执行关键操作后（如入职、分析、项目进度查询），主动判断是否值得保存为observation，如果是则调用save_memory
4. **设置跟进提醒**：当用户要求后续跟进时，先用save_memory保存事项，再用set_reminder设置提醒时间
5. **检查待办提醒**：每次对话开始时，调用check_reminders查看是否有到期提醒，并告知用户

记忆类型说明：
- fact: 稳定事实（员工信息、项目状态）
- observation: 时点观察（分析结果、进度快照）
- preference: 用户偏好（常用查询、角色信息）
- context: 对话上下文（本次对话的关键主题）
"""

MEMORY_EXTRACTION_PROMPT = """你是一个记忆提取器。请判断以下对话中是否有值得长期记住的信息。

值得记住的信息包括：
- 用户提到的个人信息、角色、偏好
- 重要的业务观察或决策
- 需要后续跟进的事项

不需要记住的信息：
- 日常查询的中间结果
- 已由系统自动保存的操作记录
- 无关紧要的闲聊
- 简单的事实确认

请以JSON格式返回一个列表，例如：
[{"memory_type": "preference", "category": "general", "subject": "user_preference", "content": "用户是HR经理张三", "importance": 3}]

如果没有值得记住的信息，返回：[]
只返回JSON，不要其他内容。"""


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


def _build_hook_memory(func_name: str, result: dict, context: dict) -> dict | None:
    """Build a memory record from tool hook results."""
    from app.schemas.agent_memory import MemoryCreate
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    user_tag = context.get("user_tag", "default")
    session_id = context.get("session_id", "agent")

    if func_name == "onboard_employee":
        if result.get("error"):
            return None
        emp_info = result.get("employee", result)
        name = emp_info.get("name", "未知")
        emp_id = emp_info.get("id", "")
        content = f"员工{name}(ID:{emp_id})入职流程已启动"
        return MemoryCreate(
            session_id=session_id, user_tag=user_tag,
            memory_type="fact", category="onboarding",
            subject=f"employee:{emp_id}", content=content,
            source="agent_observed", importance=4,
        ).model_dump()

    if func_name.startswith("analyze_"):
        if result.get("error"):
            return None
        content = json.dumps(result, ensure_ascii=False, default=str)
        if len(content) > 500:
            content = content[:500] + "..."
        category = "analytics"
        subject = f"analysis:{func_name}"
        return MemoryCreate(
            session_id=session_id, user_tag=user_tag,
            memory_type="observation", category=category,
            subject=subject, content=content,
            source="agent_observed", importance=2,
            expires_at=now.isoformat(),
        ).model_dump()

    if func_name == "query_project_progress":
        if result.get("error"):
            return None
        project_id = "unknown"
        content = json.dumps(result, ensure_ascii=False, default=str)
        if len(content) > 500:
            content = content[:500] + "..."
        return MemoryCreate(
            session_id=session_id, user_tag=user_tag,
            memory_type="observation", category="project",
            subject=f"project:{project_id}_progress", content=content,
            source="agent_observed", importance=2,
            expires_at=now.isoformat(),
        ).model_dump()

    return None


_TOOL_MEMORY_HOOKS = {
    "onboard_employee",
    "analyze_department_salary_distribution",
    "analyze_attendance_anomalies",
    "analyze_leave_trends",
    "query_project_progress",
}


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
        self._context: dict = {}

    def _init_session(self, session_id: str, user_tag: str | None = None) -> None:
        msgs = self._history.get_messages(session_id)
        if not msgs:
            self._history.add_message(session_id, {"role": "system", "content": SYSTEM_PROMPT})
            if user_tag:
                self._inject_memory_context(session_id, user_tag)

    def _inject_memory_context(self, session_id: str, user_tag: str) -> None:
        from app.services import agent_memory as memory_service
        try:
            # 告知 LLM 当前用户的 user_tag，使其能正确调用记忆工具
            self._history.add_message(session_id, {
                "role": "system",
                "content": f"当前用户的标识(user_tag)为：{user_tag}。在调用recall_memories、save_memory、check_reminders等记忆工具时，请使用此user_tag。",
            })

            # 自动注入最近的重要记忆，避免完全依赖 Agent 主动查询
            recent = memory_service.recall_memories(user_tag, limit=5)
            if recent.memories:
                lines = ["以下是该用户的近期记忆："]
                for m in recent.memories:
                    lines.append(f"- [{m.memory_type}/{m.category}] {m.content}")
                self._history.add_message(session_id, {
                    "role": "system",
                    "content": "\n".join(lines),
                })

            reminders = memory_service.check_pending_reminders(user_tag)
            if reminders.reminders:
                lines = ["你有以下待办提醒："]
                for r in reminders.reminders:
                    mem = memory_service.get_memory(r.memory_id)
                    lines.append(f"- {mem.content}（提醒时间：{r.trigger_at}）")
                self._history.add_message(session_id, {
                    "role": "system",
                    "content": "\n".join(lines),
                })
        except Exception as e:
            logger.warning("Failed to inject memory context: %s", e)

    # memory 技能始终激活，不参与路由筛选
    _ALWAYS_ON_SKILLS = {"memory"}

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

        skill_names = list(set(skill_names) | self._ALWAYS_ON_SKILLS)

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

    def _run_tool_hook(self, func_name: str, result: dict) -> None:
        if func_name not in _TOOL_MEMORY_HOOKS:
            return
        try:
            memory_data = _build_hook_memory(func_name, result, self._context)
            if memory_data is None:
                return
            from app.services import agent_memory as memory_service
            from app.schemas.agent_memory import MemoryCreate
            memory_service.save_memory(MemoryCreate(**memory_data))
        except Exception as e:
            logger.warning("Tool memory hook failed for %s: %s", func_name, e)

    def _post_process_memory(self, session_id: str, user_tag: str, messages: list[dict]) -> None:
        conversation_parts = []
        for msg in messages:
            role = msg.get("role", "")
            if role in ("user", "assistant") and msg.get("content"):
                conversation_parts.append(f"[{role}]: {msg['content']}")
        if not conversation_parts:
            return

        conversation_text = "\n".join(conversation_parts[-10:])
        try:
            response = self._client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": MEMORY_EXTRACTION_PROMPT},
                    {"role": "user", "content": conversation_text},
                ],
                temperature=0.1,
            )
            raw = response.choices[0].message.content or "[]"
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            items = json.loads(raw)
            if not isinstance(items, list):
                return
            from app.services import agent_memory as memory_service
            from app.schemas.agent_memory import MemoryCreate
            for item in items:
                if not isinstance(item, dict):
                    continue
                item.setdefault("session_id", session_id)
                item.setdefault("user_tag", user_tag)
                item.setdefault("source", "agent_observed")
                try:
                    memory_service.save_memory(MemoryCreate(**item))
                except Exception:
                    pass
        except Exception as e:
            logger.warning("Memory post-processing failed: %s", e)

    def chat(self, session_id: str, message: str, user_tag: str | None = None) -> str:
        effective_tag = user_tag or settings.default_user_tag
        self._context = {"session_id": session_id, "user_tag": effective_tag}
        self._init_session(session_id, effective_tag)
        self._history.add_message(session_id, {"role": "user", "content": message})
        messages = self._history.get_messages(session_id)

        tools, tool_map = self._resolve_tools(message)

        final_reply = ""
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
                final_reply = assistant_msg.get("content") or ""
                break

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

                self._run_tool_hook(func_name, result)

                self._history.add_message(session_id, {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })
                messages = self._history.get_messages(session_id)
        else:
            final_reply = "抱歉，处理过程中超出了最大迭代次数，请简化您的问题后重试。"

        self._post_process_memory(session_id, effective_tag, messages)
        return final_reply

    async def chat_stream(self, session_id: str, message: str, user_tag: str | None = None) -> AsyncIterator[dict]:
        effective_tag = user_tag or settings.default_user_tag
        self._context = {"session_id": session_id, "user_tag": effective_tag}
        self._init_session(session_id, effective_tag)
        self._history.add_message(session_id, {"role": "user", "content": message})

        tools, tool_map = self._resolve_tools(message)

        final_messages = []
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
                final_messages = self._history.get_messages(session_id)
                yield {"event": "done", "data": ""}
                self._post_process_memory(session_id, effective_tag, final_messages)
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

                self._run_tool_hook(func_name, result)

                self._history.add_message(session_id, {
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                })

            yield {"event": "tool_result", "data": json.dumps(
                [tc["name"] for tc in tool_calls_accum.values()],
                ensure_ascii=False,
            )}

        final_messages = self._history.get_messages(session_id)
        yield {"event": "error", "data": "超出最大迭代次数"}
        self._post_process_memory(session_id, effective_tag, final_messages)
