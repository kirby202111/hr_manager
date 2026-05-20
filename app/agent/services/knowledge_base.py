"""Agent runtime services for knowledge base access."""

from __future__ import annotations

from pathlib import Path

from app.agent.repositories import knowledge_base as knowledge_base_repo
from app.agent.schemas.knowledge_base import (
    KnowledgeDocumentDeleteResponse,
    KnowledgeDocumentIngestResponse,
    KnowledgeDocumentListResponse,
    KnowledgeDocumentResponse,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
)
from app.config import settings
from app.errors import NotFoundError, ValidationError


def _require_embedding_configured() -> None:
    if not settings.dashscope_api_key:
        raise ValidationError("DASHSCOPE_API_KEY is not configured")


def search_knowledge_base(query: str, top_k: int | None = None) -> KnowledgeSearchResponse:
    _require_embedding_configured()
    rows = knowledge_base_repo.get_repository().search(query, top_k)
    results = [KnowledgeSearchResult(text=row.text, score=row.score, metadata=row.metadata) for row in rows]
    return KnowledgeSearchResponse(query=query, results=results, total=len(results))


def list_knowledge_documents() -> KnowledgeDocumentListResponse:
    rows = knowledge_base_repo.get_repository().list_documents()
    documents = [
        KnowledgeDocumentResponse(
            doc_id=row.doc_id,
            source=row.source,
            chunk_count=row.chunk_count,
        )
        for row in rows
    ]
    return KnowledgeDocumentListResponse(documents=documents, total=len(documents))


def add_document_from_file(
    file_path: str,
    doc_id: str | None = None,
    source: str | None = None,
) -> KnowledgeDocumentIngestResponse:
    _require_embedding_configured()

    path = Path(file_path)
    if not path.is_file():
        raise NotFoundError(f"Knowledge base source file not found: {file_path}")

    text = path.read_text(encoding="utf-8")
    effective_doc_id = doc_id or path.stem
    effective_source = source or str(path)
    chunk_count = knowledge_base_repo.get_repository().add_document(
        effective_doc_id,
        effective_source,
        text,
    )
    return KnowledgeDocumentIngestResponse(
        doc_id=effective_doc_id,
        source=effective_source,
        chunk_count=chunk_count,
    )


def delete_knowledge_document(doc_id: str) -> KnowledgeDocumentDeleteResponse:
    deleted_chunks = knowledge_base_repo.get_repository().delete_document(doc_id)
    if deleted_chunks == 0:
        raise NotFoundError(f"Knowledge base document '{doc_id}' not found")
    return KnowledgeDocumentDeleteResponse(doc_id=doc_id, deleted_chunks=deleted_chunks)


__all__ = [
    "add_document_from_file",
    "delete_knowledge_document",
    "list_knowledge_documents",
    "search_knowledge_base",
]
