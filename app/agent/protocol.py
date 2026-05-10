from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Callable, Protocol, runtime_checkable


@runtime_checkable
class BaseAgent(Protocol):
    def chat(self, session_id: str, message: str) -> str: ...
    async def chat_stream(self, session_id: str, message: str) -> AsyncIterator[dict]: ...


@runtime_checkable
class BaseHistoryStore(Protocol):
    def get_messages(self, session_id: str) -> list[dict]: ...
    def add_message(self, session_id: str, message: dict) -> None: ...
    def clear(self, session_id: str) -> None: ...
    def list_sessions(self) -> list[str]: ...


@dataclass
class AgentTool:
    name: str
    description: str
    parameters: dict
    fn: Callable[..., dict]

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_langchain_tool(self) -> Any:
        from langchain_core.tools import StructuredTool

        return StructuredTool.from_function(
            name=self.name,
            description=self.description,
            args_schema=self.parameters,
            func=self.fn,
        )
