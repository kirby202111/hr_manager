"""Agent knowledge base schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class KnowledgeSearchResult(BaseModel):
    """One retrieved knowledge-base passage."""

    text: str
    score: float
    metadata: dict[str, Any]


class KnowledgeSearchResponse(BaseModel):
    """Knowledge-base search response."""

    query: str
    results: list[KnowledgeSearchResult]
    total: int


class KnowledgeDocumentResponse(BaseModel):
    """Indexed knowledge document summary."""

    doc_id: str
    source: str
    chunk_count: int


class KnowledgeDocumentListResponse(BaseModel):
    """List of indexed knowledge documents."""

    documents: list[KnowledgeDocumentResponse]
    total: int


class KnowledgeDocumentIngestResponse(BaseModel):
    """Document ingestion response."""

    doc_id: str
    source: str
    chunk_count: int


class KnowledgeDocumentDeleteResponse(BaseModel):
    """Document deletion response."""

    doc_id: str
    deleted_chunks: int


__all__ = [
    "KnowledgeDocumentDeleteResponse",
    "KnowledgeDocumentIngestResponse",
    "KnowledgeDocumentListResponse",
    "KnowledgeDocumentResponse",
    "KnowledgeSearchResponse",
    "KnowledgeSearchResult",
]
