"""Unit tests for the Knowledge Base system: chunking, vector_store,
and embeddings modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from app.knowledge_base.chunking import Chunk, chunk_text
from app.knowledge_base.embeddings import embed_query, embed_texts
from app.knowledge_base.vector_store import KnowledgeStore, SearchResult

# ── chunking.py ────────────────────────────────────────────────


class TestChunkText:
    def test_empty_text_returns_empty(self):
        assert chunk_text("") == []

    def test_short_text_single_chunk(self):
        text = "Hello world"
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"
        assert chunks[0].index == 0
        assert chunks[0].start_char == 0
        assert chunks[0].end_char == len(text)

    def test_long_text_multiple_chunks(self):
        text = "A" * 1200
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        assert len(chunks) >= 2

    def test_overlap_between_consecutive_chunks(self):
        text = "Word " * 300  # 1500 chars
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        if len(chunks) >= 2:
            # The end of chunk i should overlap with the start of chunk i+1
            # i.e., chunk[i].end_char > chunk[i+1].start_char
            # Only when the first chunk was a full chunk_size
            for i in range(len(chunks) - 1):
                # Overlap means chunk i's end region and chunk i+1's start region share text
                # Verify by checking that start of next chunk is before end of previous chunk
                # when the previous chunk had full size (stride = cs - ov = 400)
                assert chunks[i + 1].start_char < chunks[i].end_char

    def test_prefers_newline_boundary(self):
        # Create text where a newline falls inside the overlap zone
        text = "A" * 400 + "\n" + "B" * 400
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        # The first chunk should split at the newline rather than mid-word
        assert len(chunks) >= 2
        # The first chunk should end at or near the newline
        assert "\n" not in chunks[0].text or chunks[0].text.endswith("\n")

    def test_chunk_size_less_equal_overlap_raises(self):
        with pytest.raises(ValueError, match="chunk_size must be greater than chunk_overlap"):
            chunk_text("some text", chunk_size=100, overlap=100)

    def test_chunk_size_smaller_than_overlap_raises(self):
        with pytest.raises(ValueError, match="chunk_size must be greater than chunk_overlap"):
            chunk_text("some text", chunk_size=50, overlap=100)

    def test_chunk_indices_are_sequential(self):
        text = "X" * 2000
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_start_and_end_char_monotonically_increase(self):
        text = "Y" * 2000
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        for i in range(len(chunks) - 1):
            assert chunks[i].start_char < chunks[i + 1].start_char


# ── vector_store.py ────────────────────────────────────────────


class TestKnowledgeStore:
    def _make_store(self, mock_collection=None):
        """Create a KnowledgeStore with a mocked chromadb collection."""
        store = KnowledgeStore.__new__(KnowledgeStore)
        store._client = MagicMock()
        store._collection = mock_collection or MagicMock()
        return store

    def test_add_document_calls_upsert(self):
        collection = MagicMock()
        store = self._make_store(collection)

        chunks = [
            Chunk(text="hello world", index=0, start_char=0, end_char=11),
            Chunk(text="foo bar", index=1, start_char=12, end_char=19),
        ]

        with patch(
            "app.knowledge_base.vector_store.embed_texts",
            return_value=[
                [0.1, 0.2],
                [0.3, 0.4],
            ],
        ):
            count = store.add_document("doc1", "source.txt", chunks)

        assert count == 2
        collection.upsert.assert_called_once()
        call_kwargs = collection.upsert.call_args
        ids = (
            call_kwargs.kwargs.get("ids")
            or call_kwargs[1].get("ids")
            or (call_kwargs[0][0] if call_kwargs[0] else call_kwargs.kwargs["ids"])
        )
        # Verify ids format
        assert "doc1_chunk_0" in ids
        assert "doc1_chunk_1" in ids

    def test_add_document_empty_chunks_returns_zero(self):
        store = self._make_store()
        count = store.add_document("doc1", "source.txt", [])
        assert count == 0

    def test_search_returns_search_results(self):
        collection = MagicMock()
        collection.query.return_value = {
            "documents": [["doc text 1", "doc text 2"]],
            "distances": [[0.1, 0.4]],
            "metadatas": [[{"doc_id": "d1"}, {"doc_id": "d2"}]],
        }
        store = self._make_store(collection)

        with patch("app.knowledge_base.vector_store.embed_query", return_value=[0.5, 0.6]):
            results = store.search("test query")

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)
        # score = 1.0 - dist/2.0
        assert results[0].score == round(1.0 - 0.1 / 2.0, 4)
        assert results[0].text == "doc text 1"
        assert results[0].metadata == {"doc_id": "d1"}

    def test_search_empty_results(self):
        collection = MagicMock()
        collection.query.return_value = {
            "documents": [[]],
            "distances": [[]],
            "metadatas": [[]],
        }
        store = self._make_store(collection)

        with patch("app.knowledge_base.vector_store.embed_query", return_value=[0.5, 0.6]):
            results = store.search("no results query")

        assert results == []

    def test_list_documents_aggregates_by_doc_id(self):
        collection = MagicMock()
        collection.get.return_value = {
            "metadatas": [
                {"doc_id": "doc1", "source": "a.txt"},
                {"doc_id": "doc1", "source": "a.txt"},
                {"doc_id": "doc2", "source": "b.txt"},
            ],
        }
        store = self._make_store(collection)
        docs = store.list_documents()
        assert len(docs) == 2
        doc1 = next(d for d in docs if d["doc_id"] == "doc1")
        assert doc1["chunk_count"] == 2
        doc2 = next(d for d in docs if d["doc_id"] == "doc2")
        assert doc2["chunk_count"] == 1

    def test_delete_document(self):
        collection = MagicMock()
        collection.get.return_value = {"ids": ["doc1_chunk_0", "doc1_chunk_1"]}
        store = self._make_store(collection)

        deleted_count = store.delete_document("doc1")
        assert deleted_count == 2
        collection.delete.assert_called_once_with(ids=["doc1_chunk_0", "doc1_chunk_1"])

    def test_delete_document_no_ids(self):
        collection = MagicMock()
        collection.get.return_value = {"ids": []}
        store = self._make_store(collection)

        deleted_count = store.delete_document("nonexistent")
        assert deleted_count == 0

    def test_get_chunk_count(self):
        collection = MagicMock()
        collection.count.return_value = 42
        store = self._make_store(collection)

        assert store.get_chunk_count() == 42


# ── embeddings.py ──────────────────────────────────────────────


class TestEmbeddings:
    @patch("app.knowledge_base.embeddings._client")
    def test_embed_texts_returns_embeddings_in_order(self, mock_client):
        # Mock the OpenAI client's embeddings.create response
        emb1 = MagicMock()
        emb1.index = 1
        emb1.embedding = [0.1, 0.2, 0.3]
        emb0 = MagicMock()
        emb0.index = 0
        emb0.embedding = [0.4, 0.5, 0.6]

        mock_response = MagicMock()
        mock_response.data = [emb1, emb0]  # deliberately out of order
        mock_client.embeddings.create.return_value = mock_response

        result = embed_texts(["hello", "world"])
        mock_client.embeddings.create.assert_called_once()
        # Should be sorted by index
        assert result == [[0.4, 0.5, 0.6], [0.1, 0.2, 0.3]]

    @patch("app.knowledge_base.embeddings._client")
    def test_embed_query_returns_single_embedding(self, mock_client):
        emb = MagicMock()
        emb.index = 0
        emb.embedding = [0.7, 0.8, 0.9]

        mock_response = MagicMock()
        mock_response.data = [emb]
        mock_client.embeddings.create.return_value = mock_response

        result = embed_query("test query")
        assert result == [0.7, 0.8, 0.9]
