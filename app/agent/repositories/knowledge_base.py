"""Agent knowledge base repository backed by ChromaDB."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import chromadb
from openai import OpenAI

from app.config import settings

_EMBED_BATCH_SIZE = 20


@dataclass(slots=True)
class KnowledgeChunk:
    text: str
    index: int
    start_char: int
    end_char: int


@dataclass(slots=True)
class KnowledgeSearchRow:
    text: str
    score: float
    metadata: dict[str, Any]


@dataclass(slots=True)
class KnowledgeDocumentRow:
    doc_id: str
    source: str
    chunk_count: int


class KnowledgeBaseRepository:
    """Persistence and retrieval adapter for agent knowledge documents."""

    def __init__(self) -> None:
        self._vector_client = chromadb.PersistentClient(path=settings.knowledge_base_dir)
        self._collection = self._vector_client.get_or_create_collection(
            name="hr_knowledge",
            metadata={"hnsw:space": "cosine"},
        )
        self._embedding_client: OpenAI | None = None

    def add_document(self, doc_id: str, source: str, text: str) -> int:
        chunks = self._chunk_text(text)
        if not chunks:
            return 0

        texts = [chunk.text for chunk in chunks]
        embeddings: list[list[float]] = []
        for index in range(0, len(texts), _EMBED_BATCH_SIZE):
            embeddings.extend(self._embed_texts(texts[index : index + _EMBED_BATCH_SIZE]))

        self._collection.upsert(
            ids=[f"{doc_id}_chunk_{chunk.index}" for chunk in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {
                    "doc_id": doc_id,
                    "source": source,
                    "chunk_index": chunk.index,
                    "start_char": chunk.start_char,
                    "end_char": chunk.end_char,
                }
                for chunk in chunks
            ],
        )
        return len(chunks)

    def search(self, query: str, top_k: int | None = None) -> list[KnowledgeSearchRow]:
        result = self._collection.query(
            query_embeddings=[self._embed_query(query)],
            n_results=top_k or settings.knowledge_base_search_top_k,
            include=["documents", "distances", "metadatas"],
        )

        rows: list[KnowledgeSearchRow] = []
        if not result["documents"] or not result["documents"][0]:
            return rows

        for text, distance, metadata in zip(
            result["documents"][0],
            result["distances"][0],
            result["metadatas"][0],
        ):
            rows.append(
                KnowledgeSearchRow(
                    text=text,
                    score=round(1.0 - distance / 2.0, 4),
                    metadata=metadata,
                )
            )
        return rows

    def list_documents(self) -> list[KnowledgeDocumentRow]:
        result = self._collection.get(include=["metadatas"])
        documents: dict[str, KnowledgeDocumentRow] = {}
        if not result["metadatas"]:
            return []

        for metadata in result["metadatas"]:
            doc_id = str(metadata.get("doc_id", "unknown"))
            existing = documents.get(doc_id)
            if existing is None:
                existing = KnowledgeDocumentRow(
                    doc_id=doc_id,
                    source=str(metadata.get("source", "")),
                    chunk_count=0,
                )
                documents[doc_id] = existing
            existing.chunk_count += 1
        return list(documents.values())

    def delete_document(self, doc_id: str) -> int:
        result = self._collection.get(where={"doc_id": doc_id}, include=[])
        ids_to_delete = result["ids"]
        if ids_to_delete:
            self._collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def get_chunk_count(self) -> int:
        return self._collection.count()

    def _embed_query(self, text: str) -> list[float]:
        return self._embed_texts([text])[0]

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        response = self._get_embedding_client().embeddings.create(
            model=settings.dashscope_embedding_model,
            input=texts,
        )
        ordered = sorted(response.data, key=lambda row: row.index)
        return [row.embedding for row in ordered]

    def _get_embedding_client(self) -> OpenAI:
        if self._embedding_client is None:
            self._embedding_client = OpenAI(
                api_key=settings.dashscope_api_key,
                base_url=settings.dashscope_base_url,
            )
        return self._embedding_client

    @staticmethod
    def _chunk_text(
        text: str,
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[KnowledgeChunk]:
        effective_chunk_size = chunk_size or settings.knowledge_base_chunk_size
        effective_overlap = overlap or settings.knowledge_base_chunk_overlap
        stride = effective_chunk_size - effective_overlap

        if stride <= 0:
            raise ValueError("chunk_size must be greater than chunk_overlap")

        chunks: list[KnowledgeChunk] = []
        start = 0
        index = 0
        while start < len(text):
            end = min(start + effective_chunk_size, len(text))

            if end < len(text):
                search_start = max(end - effective_overlap, start)
                last_newline = text.rfind("\n", search_start, end)
                if last_newline > start:
                    end = last_newline

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    KnowledgeChunk(
                        text=chunk_text,
                        index=index,
                        start_char=start,
                        end_char=end,
                    )
                )
                index += 1

            start = start + stride if end - start == effective_chunk_size else end

        return chunks


_repository: KnowledgeBaseRepository | None = None


def get_repository() -> KnowledgeBaseRepository:
    global _repository
    if _repository is None:
        _repository = KnowledgeBaseRepository()
    return _repository


__all__ = [
    "KnowledgeBaseRepository",
    "KnowledgeDocumentRow",
    "KnowledgeSearchRow",
    "get_repository",
]
