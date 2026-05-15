from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agent.protocol import BaseHistoryStore
from app.agent.react_agent import ReActAgent
from app.agent.history import SQLiteHistoryStore
from app.agent.skill_registry import SkillRegistry
from app.agent.skills import register_all_skills
from app.config import settings
from app.schemas.agent_memory import ConversationMessageListResponse


def create_agent() -> tuple[ReActAgent, SkillRegistry, BaseHistoryStore]:
    history_store: BaseHistoryStore = SQLiteHistoryStore()
    skill_registry = SkillRegistry()
    register_all_skills(skill_registry)
    agent = ReActAgent(
        history_store,
        skill_registry,
        use_routing=settings.use_skill_routing,
    )
    return agent, skill_registry, history_store


_agent, _skill_registry, _history_store = create_agent()

router = APIRouter(prefix="/agent", tags=["AI助手"])


def _format_sse_event(event: str, data: str) -> str:
    lines = str(data).splitlines()
    if not lines:
        lines = [""]
    data_lines = "\n".join(f"data: {line}" for line in lines)
    return f"event: {event}\n{data_lines}\n\n"


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_tag: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    user_tag = req.user_tag or settings.default_user_tag
    try:
        reply = _agent.chat(session_id, req.message, user_tag=user_tag)
        return ChatResponse(session_id=session_id, reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI助手错误: {str(e)}")


@router.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    user_tag = req.user_tag or settings.default_user_tag

    async def event_generator():
        async for event in _agent.chat_stream(session_id, req.message, user_tag=user_tag):
            yield _format_sse_event(event["event"], event["data"])

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Session-ID": session_id},
    )


@router.get("/sessions")
def get_sessions(user_tag: str | None = None):
    return {"sessions": _history_store.list_sessions(user_tag=user_tag)}


@router.get("/sessions/{session_id}/messages", response_model=ConversationMessageListResponse)
def get_session_messages(session_id: str):
    from app.services.agent_memory import get_session_messages as _get_session_messages

    return _get_session_messages(session_id)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    _history_store.clear(session_id)
    return {"message": f"Session {session_id} cleared"}


# ---- Skill Management ----

@router.get("/skills")
def list_skills():
    return {"skills": _skill_registry.list_skills()}


@router.post("/skills/{skill_name}/enable")
def enable_skill(skill_name: str):
    if _skill_registry.enable(skill_name):
        return {"message": f"Skill '{skill_name}' enabled"}
    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")


@router.post("/skills/{skill_name}/disable")
def disable_skill(skill_name: str):
    if _skill_registry.disable(skill_name):
        return {"message": f"Skill '{skill_name}' disabled"}
    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")
