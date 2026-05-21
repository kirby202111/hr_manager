"""Coordinator for runtime orchestrators."""

from __future__ import annotations

from dataclasses import dataclass

from app.agent.protocol import BaseOrchestrator, ToolResultEnvelope


@dataclass(slots=True)
class ResolvedOrchestrator:
    """Resolved orchestrator metadata for a turn."""

    orchestrator: BaseOrchestrator
    forced_skills: list[str]


class OrchestratorManager:
    """Resolve and fan out runtime hooks for active workflows."""

    def __init__(self, orchestrators: list[BaseOrchestrator] | None = None) -> None:
        self._orchestrators = sorted(orchestrators or [], key=lambda item: item.priority, reverse=True)

    def resolve(self, session_id: str, user_tag: str, message: str) -> list[ResolvedOrchestrator]:
        resolved: list[ResolvedOrchestrator] = []
        for orchestrator in self._orchestrators:
            if not orchestrator.should_handle(message, session_id, user_tag):
                continue
            resolved.append(
                ResolvedOrchestrator(
                    orchestrator=orchestrator,
                    forced_skills=orchestrator.forced_skills(session_id, user_tag, message),
                )
            )
        return resolved

    @staticmethod
    def collect_forced_skills(orchestrators: list[ResolvedOrchestrator]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for resolved in orchestrators:
            for skill_name in resolved.forced_skills:
                if skill_name in seen:
                    continue
                seen.add(skill_name)
                ordered.append(skill_name)
        return ordered

    @staticmethod
    def prepare_turn(orchestrators: list[ResolvedOrchestrator], session_id: str, user_tag: str, message: str) -> None:
        for resolved in orchestrators:
            resolved.orchestrator.prepare_turn(session_id, user_tag, message)

    @staticmethod
    def build_runtime_messages(
        orchestrators: list[ResolvedOrchestrator],
        session_id: str,
        user_tag: str,
    ) -> list[dict[str, str]]:
        runtime_messages: list[dict[str, str]] = []
        for resolved in orchestrators:
            summary = resolved.orchestrator.build_runtime_summary(session_id, user_tag)
            if summary:
                runtime_messages.append({"role": "system", "content": summary})
        return runtime_messages

    @staticmethod
    def handle_tool_result(
        orchestrators: list[ResolvedOrchestrator],
        session_id: str,
        user_tag: str,
        tool_name: str,
        arguments: dict,
        result: ToolResultEnvelope,
    ) -> None:
        for resolved in orchestrators:
            resolved.orchestrator.handle_tool_result(session_id, user_tag, tool_name, arguments, result)


__all__ = ["OrchestratorManager", "ResolvedOrchestrator"]
