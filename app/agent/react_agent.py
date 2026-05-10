from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator

from openai import OpenAI, APIError, RateLimitError, APITimeoutError

from app.config import settings
from app.agent.protocol import BaseAgent, BaseHistoryStore
from app.agent.tools import TOOL_MAP, ALL_TOOLS, SYSTEM_PROMPT


class ReActAgent:
    def __init__(self, history_store: BaseHistoryStore) -> None:
        self._history = history_store
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
        self._tools = [t.to_openai_tool() for t in ALL_TOOLS]

    def _init_session(self, session_id: str) -> None:
        msgs = self._history.get_messages(session_id)
        if not msgs:
            self._history.add_message(session_id, {"role": "system", "content": SYSTEM_PROMPT})

    def chat(self, session_id: str, message: str) -> str:
        self._init_session(session_id)
        self._history.add_message(session_id, {"role": "user", "content": message})
        messages = self._history.get_messages(session_id)

        for _ in range(settings.agent_max_iterations):
            try:
                response = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=messages,
                    tools=self._tools,
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
            self._history.add_message(session_id, assistant_msg)
            messages = self._history.get_messages(session_id)

            if not assistant_msg.get("tool_calls"):
                return assistant_msg.get("content") or ""

            for tool_call in assistant_msg["tool_calls"]:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                tool = TOOL_MAP.get(func_name)
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

        for _ in range(settings.agent_max_iterations):
            messages = self._history.get_messages(session_id)
            try:
                stream = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=messages,
                    tools=self._tools,
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
            tool_calls_accum: dict[int, dict] = {}

            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta

                if delta.content:
                    yield {"event": "message", "data": delta.content}
                    assistant_content += delta.content

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
                tool = TOOL_MAP.get(func_name)
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
