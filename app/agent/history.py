from __future__ import annotations

import json
import threading
from collections import defaultdict
from datetime import UTC, datetime

from app.config import settings


class InMemoryHistoryStore:
    def __init__(self) -> None:
        self._conversations: dict[str, list[dict]] = defaultdict(list)
        self._session_tags: dict[str, str] = {}
        self._lock = threading.Lock()

    def get_messages(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._conversations[session_id])

    def add_message(self, session_id: str, message: dict, user_tag: str = "default") -> None:
        with self._lock:
            self._session_tags[session_id] = user_tag
            self._conversations[session_id].append(message)
            msgs = self._conversations[session_id]
            if len(msgs) > settings.agent_max_history_messages:
                system = msgs[0] if msgs and msgs[0].get("role") == "system" else None
                rest = msgs[-(settings.agent_max_history_messages - 1) :]
                self._conversations[session_id] = ([system] + rest) if system else rest

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._conversations.pop(session_id, None)
            self._session_tags.pop(session_id, None)

    def list_sessions(self, user_tag: str | None = None) -> list[str]:
        with self._lock:
            if user_tag is None:
                return list(self._conversations.keys())
            return [sid for sid in self._conversations if self._session_tags.get(sid, "default") == user_tag]


class SQLiteHistoryStore:
    def __init__(self) -> None:
        from app.repositories import agent_memory as repo

        self._repo = repo

    def get_messages(self, session_id: str) -> list[dict]:
        rows = self._repo.get_messages_by_session(session_id)
        messages = []
        for row in rows:
            msg: dict = {"role": row["role"]}
            if row["content"] is not None:
                msg["content"] = row["content"]
            if row.get("tool_call_id"):
                msg["tool_call_id"] = row["tool_call_id"]
            if row.get("tool_calls"):
                msg["tool_calls"] = json.loads(row["tool_calls"])
            if row.get("reasoning_content"):
                msg["reasoning_content"] = row["reasoning_content"]
            messages.append(msg)
        return messages

    def add_message(self, session_id: str, message: dict, user_tag: str = "default") -> None:
        now = datetime.now(UTC)
        data = {
            "session_id": session_id,
            "user_tag": user_tag,
            "role": message.get("role", "user"),
            "content": message.get("content"),
            "tool_call_id": message.get("tool_call_id"),
            "tool_calls": json.dumps(message["tool_calls"], ensure_ascii=False) if message.get("tool_calls") else None,
            "reasoning_content": message.get("reasoning_content"),
            "created_at": now,
        }
        self._repo.create_message(data)

        count = self._repo.count_messages_by_session(session_id)
        if count > settings.agent_max_history_messages:
            self._repo.trim_session_messages(session_id, settings.agent_max_history_messages)

    def clear(self, session_id: str) -> None:
        self._repo.delete_messages_by_session(session_id)

    def list_sessions(self, user_tag: str | None = None) -> list[str]:
        if user_tag is None:
            return self._repo.list_sessions()
        return self._repo.list_sessions_by_user_tag(user_tag)
