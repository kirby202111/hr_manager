from __future__ import annotations

import logging
from dataclasses import dataclass

import chromadb

from app.config import settings
from app.knowledge_base.chunking import Chunk
from app.knowledge_base.embeddings import embed_query, embed_texts

logger = logging.getLogger(__name__)

_EMBED_BATCH_SIZE = 20


@dataclass
class SearchResult:
    text: str
    score: float
    metadata: dict


class KnowledgeStore:
    def __init__(self) -> None:
        self._client = chromadb.PersistentClient(path=settings.knowledge_base_dir)
        self._collection = self._client.get_or_create_collection(
            name="hr_knowledge",
            metadata={"hnsw:space": "cosine"},
        )

    def add_document(self, doc_id: str, source: str, chunks: list[Chunk]) -> int:
        if not chunks:
            return 0

        texts = [c.text for c in chunks]

        # 分批嵌入，避免 API 限制
        embeddings: list[list[float]] = []
        for i in range(0, len(texts), _EMBED_BATCH_SIZE):
            batch = texts[i : i + _EMBED_BATCH_SIZE]
            embeddings.extend(embed_texts(batch))

        ids = [f"{doc_id}_chunk_{c.index}" for c in chunks]
        metadatas = [
            {
                "doc_id": doc_id,
                "source": source,
                "chunk_index": c.index,
                "start_char": c.start_char,
                "end_char": c.end_char,
            }
            for c in chunks
        ]

        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )
        return len(chunks)

    def search(self, query: str, top_k: int | None = None) -> list[SearchResult]:
        k = top_k or settings.knowledge_base_search_top_k
        query_embedding = embed_query(query)

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "distances", "metadatas"],
        )

        search_results: list[SearchResult] = []
        if results["documents"] and results["documents"][0]:
            for doc, dist, meta in zip(
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0],
            ):
                score = round(1.0 - dist / 2.0, 4)
                search_results.append(SearchResult(text=doc, score=score, metadata=meta))
        return search_results

    def list_documents(self) -> list[dict]:
        all_meta = self._collection.get(include=["metadatas"])
        doc_map: dict[str, dict] = {}
        if all_meta["metadatas"]:
            for meta in all_meta["metadatas"]:
                did = meta.get("doc_id", "unknown")
                if did not in doc_map:
                    doc_map[did] = {
                        "doc_id": did,
                        "source": meta.get("source", ""),
                        "chunk_count": 0,
                    }
                doc_map[did]["chunk_count"] += 1
        return list(doc_map.values())

    def delete_document(self, doc_id: str) -> int:
        all_ids = self._collection.get(where={"doc_id": doc_id}, include=[])
        ids_to_delete = all_ids["ids"]
        if ids_to_delete:
            self._collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def get_chunk_count(self) -> int:
        return self._collection.count()


_store: KnowledgeStore | None = None


def get_store() -> KnowledgeStore:
    global _store
    if _store is None:
        _store = KnowledgeStore()
    return _store
