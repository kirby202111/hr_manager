"""Agent chat request and response schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request payload."""

    message: str
    session_id: str | None = None
    user_tag: str | None = None


class ChatResponse(BaseModel):
    """Synchronous chat response."""

    session_id: str
    reply: str


class SessionListResponse(BaseModel):
    """Session list response."""

    sessions: list[str]


__all__ = ["ChatRequest", "ChatResponse", "SessionListResponse"]
