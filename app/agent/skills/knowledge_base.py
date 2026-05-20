"""Knowledge base agent tools."""

from __future__ import annotations

from pydantic import BaseModel

from app.agent.protocol import AgentSkill, AgentTool, safe_call
from app.agent.services import knowledge_base as knowledge_base_service


class SearchKnowledgeBaseInput(BaseModel):
    query: str
    top_k: int | None = None


class DeleteKnowledgeDocumentInput(BaseModel):
    doc_id: str


skill = AgentSkill(
    name="knowledge_base",
    description="Search and manage the local manufacturing knowledge base.",
    applicability="Use for SOPs, safety rules, equipment guides, and operating references.",
    keywords=("knowledge", "sop", "guide", "manual", "document", "知识库", "规范", "作业指导书", "安全"),
    tools=[
        AgentTool(
            name="search_knowledge_base",
            description="Search the local knowledge base for relevant passages.",
            parameters=SearchKnowledgeBaseInput.model_json_schema(),
            fn=lambda query, top_k=None: safe_call(knowledge_base_service.search_knowledge_base, query, top_k),
        ),
        AgentTool(
            name="list_knowledge_documents",
            description="List indexed knowledge base documents.",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: safe_call(knowledge_base_service.list_knowledge_documents),
        ),
        AgentTool(
            name="delete_knowledge_document",
            description="Delete one indexed knowledge base document by document ID.",
            parameters=DeleteKnowledgeDocumentInput.model_json_schema(),
            fn=lambda doc_id: safe_call(knowledge_base_service.delete_knowledge_document, doc_id),
        ),
    ],
)

__all__ = ["skill"]
