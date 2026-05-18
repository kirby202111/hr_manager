"""FastAPI router for agent runtime."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.agent.history import SQLHistoryStore
from app.agent.protocol import BaseHistoryStore
from app.agent.react_agent import ReActAgent
from app.agent.schemas.chat import ChatRequest, ChatResponse, SessionListResponse
from app.agent.schemas.memory import ConversationMessageListResponse
from app.agent.schemas.skill import SkillListResponse
from app.agent.skill_registry import SkillRegistry
from app.agent.skills import register_all_skills
from app.config import settings

router = APIRouter(prefix="/agent", tags=["agent"])


def create_agent() -> tuple[ReActAgent, SkillRegistry, BaseHistoryStore]:
    history_store: BaseHistoryStore = SQLHistoryStore()
    skill_registry = SkillRegistry()
    register_all_skills(skill_registry)
    agent = ReActAgent(
        history_store=history_store,
        skill_registry=skill_registry,
        use_routing=settings.use_skill_routing,
    )
    return agent, skill_registry, history_store


def _format_sse_event(event: str, data: str) -> str:
    lines = str(data).splitlines() or [""]
    payload = "\n".join(f"data: {line}" for line in lines)
    return f"event: {event}\n{payload}\n\n"


def _get_agent(request: Request) -> ReActAgent:
    return request.app.state.agent


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, request: Request, agent: ReActAgent = Depends(_get_agent)) -> ChatResponse:
    session_id = req.session_id or str(uuid.uuid4())
    user_tag = req.user_tag or settings.default_user_tag
    try:
        reply = agent.chat(session_id, req.message, user_tag=user_tag)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent runtime error: {exc}") from exc
    return ChatResponse(session_id=session_id, reply=reply)


@router.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest, request: Request, agent: ReActAgent = Depends(_get_agent)):
    session_id = req.session_id or str(uuid.uuid4())
    user_tag = req.user_tag or settings.default_user_tag

    async def event_generator():
        async for event in agent.chat_stream(session_id, req.message, user_tag=user_tag):
            yield _format_sse_event(event["event"], event["data"])

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Session-ID": session_id},
    )


@router.get("/sessions", response_model=SessionListResponse)
def get_sessions(request: Request, user_tag: str | None = None) -> SessionListResponse:
    sessions = request.app.state.history_store.list_sessions(user_tag=user_tag)
    return SessionListResponse(sessions=sessions)


@router.get("/sessions/{session_id}/messages", response_model=ConversationMessageListResponse)
def get_session_messages(session_id: str) -> ConversationMessageListResponse:
    from app.agent.services.memory import get_session_messages as get_session_messages_service

    return get_session_messages_service(session_id)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request) -> dict[str, str]:
    request.app.state.history_store.clear(session_id)
    return {"message": f"Session {session_id} cleared"}


@router.get("/skills", response_model=SkillListResponse)
def list_skills(request: Request) -> SkillListResponse:
    from app.agent.schemas.skill import SkillResponse

    skills = [SkillResponse(**skill) for skill in request.app.state.skill_registry.list_skills()]
    return SkillListResponse(skills=skills)


@router.post("/skills/{skill_name}/enable")
def enable_skill(skill_name: str, request: Request) -> dict[str, str]:
    if request.app.state.skill_registry.enable(skill_name):
        return {"message": f"Skill '{skill_name}' enabled"}
    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")


@router.post("/skills/{skill_name}/disable")
def disable_skill(skill_name: str, request: Request) -> dict[str, str]:
    if request.app.state.skill_registry.disable(skill_name):
        return {"message": f"Skill '{skill_name}' disabled"}
    raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")


__all__ = ["create_agent", "router"]
