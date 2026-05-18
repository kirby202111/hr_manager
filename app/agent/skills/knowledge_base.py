"""Knowledge-base-related agent tools."""

from __future__ import annotations

from app.agent.protocol import AgentSkill, AgentTool
from app.knowledge_base.vector_store import get_store


def _search_knowledge(query: str, top_k: int | None = None) -> dict:
    results = get_store().search(query, top_k)
    return {
        "results": [
            {
                "text": result.text,
                "score": result.score,
                "metadata": result.metadata,
            }
            for result in results
        ],
        "total": len(results),
    }


def _list_knowledge_documents() -> dict:
    documents = get_store().list_documents()
    return {"documents": documents, "total": len(documents)}


skill = AgentSkill(
    name="knowledge_base",
    description="Search manufacturing knowledge base documents.",
    applicability="Use for SOP lookup, safety rules, equipment guides, and contextual reference material.",
    keywords=("knowledge", "sop", "safety", "guide", "知识库", "规范", "安全", "设备"),
    tools=[
        AgentTool(
            name="search_knowledge_base",
            description="Search the knowledge base for relevant document chunks.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer"},
                },
                "required": ["query"],
            },
            fn=_search_knowledge,
        ),
        AgentTool(
            name="list_knowledge_documents",
            description="List indexed knowledge-base documents.",
            parameters={"type": "object", "properties": {}},
            fn=_list_knowledge_documents,
        ),
    ],
)

__all__ = ["skill"]
