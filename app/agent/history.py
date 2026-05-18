"""Agent history store implementations."""

from __future__ import annotations

import json
import threading
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from app.agent.repositories import runtime as runtime_repo
from app.config import settings


class InMemoryHistoryStore:
    """In-memory history store used for tests or ephemeral sessions."""

    def __init__(self) -> None:
        self._messages: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._session_tags: dict[str, str] = {}
        self._lock = threading.Lock()

    def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._messages[session_id])

    def add_message(self, session_id: str, message: dict[str, Any], user_tag: str = "default") -> None:
        with self._lock:
            self._session_tags[session_id] = user_tag
            self._messages[session_id].append(message)
            self._messages[session_id] = self._trim_messages(self._messages[session_id])

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._messages.pop(session_id, None)
            self._session_tags.pop(session_id, None)

    def list_sessions(self, user_tag: str | None = None) -> list[str]:
        with self._lock:
            if user_tag is None:
                return list(self._messages.keys())
            return [sid for sid, tag in self._session_tags.items() if tag == user_tag]

    @staticmethod
    def _trim_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        max_messages = settings.agent_max_history_messages
        if len(messages) <= max_messages:
            return messages
        system_message = messages[0] if messages and messages[0].get("role") == "system" else None
        recent = messages[-(max_messages - 1) :] if system_message else messages[-max_messages:]
        return [system_message, *recent] if system_message else recent


class SQLHistoryStore:
    """Database-backed history store built on agent runtime repositories."""

    def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        rows = runtime_repo.get_messages_by_session(session_id)
        messages: list[dict[str, Any]] = []
        for row in rows:
            message: dict[str, Any] = {"role": row["role"]}
            if row["content"] is not None:
                message["content"] = row["content"]
            if row.get("tool_call_id") is not None:
                message["tool_call_id"] = row["tool_call_id"]
            if row.get("tool_calls"):
                message["tool_calls"] = json.loads(row["tool_calls"])
            if row.get("reasoning_content") is not None:
                message["reasoning_content"] = row["reasoning_content"]
            messages.append(message)
        return messages

    def add_message(self, session_id: str, message: dict[str, Any], user_tag: str = "default") -> None:
        payload = {
            "session_id": session_id,
            "user_tag": user_tag,
            "role": message.get("role", "user"),
            "content": message.get("content"),
            "tool_call_id": message.get("tool_call_id"),
            "tool_calls": json.dumps(message["tool_calls"], ensure_ascii=False) if message.get("tool_calls") else None,
            "reasoning_content": message.get("reasoning_content"),
            "created_at": message.get("created_at", datetime.now(UTC)),
            "updated_at": message.get("updated_at", datetime.now(UTC)),
        }
        runtime_repo.create_message(payload)
        if runtime_repo.count_messages_by_session(session_id) > settings.agent_max_history_messages:
            runtime_repo.trim_session_messages(session_id, settings.agent_max_history_messages)

    def clear(self, session_id: str) -> None:
        runtime_repo.delete_messages_by_session(session_id)

    def list_sessions(self, user_tag: str | None = None) -> list[str]:
        if user_tag is None:
            return runtime_repo.list_sessions()
        return runtime_repo.list_sessions_by_user_tag(user_tag)


__all__ = ["InMemoryHistoryStore", "SQLHistoryStore"]
