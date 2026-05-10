from __future__ import annotations

import threading
from collections import defaultdict

from app.config import settings
from app.agent.protocol import BaseHistoryStore


class InMemoryHistoryStore:
    def __init__(self) -> None:
        self._conversations: dict[str, list[dict]] = defaultdict(list)
        self._lock = threading.Lock()

    def get_messages(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._conversations[session_id])

    def add_message(self, session_id: str, message: dict) -> None:
        with self._lock:
            self._conversations[session_id].append(message)
            msgs = self._conversations[session_id]
            if len(msgs) > settings.agent_max_history_messages:
                system = msgs[0] if msgs and msgs[0].get("role") == "system" else None
                rest = msgs[-(settings.agent_max_history_messages - 1):]
                self._conversations[session_id] = ([system] + rest) if system else rest

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._conversations.pop(session_id, None)

    def list_sessions(self) -> list[str]:
        with self._lock:
            return list(self._conversations.keys())
