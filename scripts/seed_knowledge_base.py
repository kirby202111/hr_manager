"""Seed the local knowledge base with bundled sample documents."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

SAMPLE_DIR = PROJECT_ROOT / "app" / "knowledge_base" / "sample_docs"


def main() -> None:
    from app.agent.repositories.knowledge_base import get_repository
    from app.agent.services.knowledge_base import add_document_from_file

    if not SAMPLE_DIR.is_dir():
        print(f"Sample docs directory not found: {SAMPLE_DIR}")
        return

    for filepath in sorted(SAMPLE_DIR.glob("*.txt")):
        print(f"Ingesting: {filepath.name} ...")
        try:
            result = add_document_from_file(str(filepath))
        except Exception as exc:
            print(f"  ERROR: {exc}")
            continue
        print(f"  OK: {result.chunk_count} chunks, doc_id={result.doc_id}")

    print(f"\nTotal chunks in knowledge base: {get_repository().get_chunk_count()}")


if __name__ == "__main__":
    main()
