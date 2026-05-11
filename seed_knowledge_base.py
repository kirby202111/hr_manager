"""知识库数据填充脚本 - 导入电子车间示例文档"""

import os

from app.services.knowledge_base import add_document_from_file

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "app", "knowledge_base", "sample_docs")


def main():
    if not os.path.isdir(SAMPLE_DIR):
        print(f"Sample docs directory not found: {SAMPLE_DIR}")
        return

    for filename in sorted(os.listdir(SAMPLE_DIR)):
        if filename.endswith(".txt"):
            filepath = os.path.join(SAMPLE_DIR, filename)
            print(f"Ingesting: {filename} ...")
            result = add_document_from_file(filepath)
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            else:
                print(f"  OK: {result['chunk_count']} chunks, doc_id={result['doc_id']}")

    from app.knowledge_base.vector_store import get_store

    store = get_store()
    print(f"\nTotal chunks in knowledge base: {store.get_chunk_count()}")


if __name__ == "__main__":
    main()
