from __future__ import annotations

import hashlib
import os

from app.knowledge_base.chunking import chunk_text
from app.knowledge_base.vector_store import get_store


def _make_doc_id(source: str) -> str:
    return hashlib.md5(source.encode()).hexdigest()[:12]


def add_document_from_text(title: str, content: str, source: str = "") -> dict:
    doc_id = _make_doc_id(source or title)
    src = source or title

    chunks = chunk_text(content)
    store = get_store()
    count = store.add_document(doc_id=doc_id, source=src, chunks=chunks)

    return {
        "doc_id": doc_id,
        "source": src,
        "title": title,
        "chunk_count": count,
        "total_chars": len(content),
    }


def add_document_from_file(filepath: str) -> dict:
    if not os.path.isfile(filepath):
        return {"error": f"File not found: {filepath}"}
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    source = os.path.basename(filepath)
    title = os.path.splitext(source)[0]
    return add_document_from_text(title=title, content=content, source=source)


def search_documents(query: str, top_k: int = 5) -> dict:
    store = get_store()
    results = store.search(query, top_k=top_k)
    return {
        "query": query,
        "total_results": len(results),
        "results": [
            {
                "text": r.text,
                "score": r.score,
                "source": r.metadata.get("source", ""),
                "doc_id": r.metadata.get("doc_id", ""),
                "chunk_index": r.metadata.get("chunk_index", 0),
            }
            for r in results
        ],
    }


def list_documents() -> dict:
    store = get_store()
    docs = store.list_documents()
    return {
        "total_documents": len(docs),
        "total_chunks": store.get_chunk_count(),
        "documents": docs,
    }


def delete_document(doc_id: str) -> dict:
    store = get_store()
    count = store.delete_document(doc_id)
    if count == 0:
        return {"error": f"Document '{doc_id}' not found"}
    return {"doc_id": doc_id, "chunks_deleted": count}
