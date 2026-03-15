"""Tests for the chunking and embedding service."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from my_note.services.chunker import chunk_text, embed_chunks


class TestChunkText:
    def test_empty_text_returns_no_chunks(self):
        assert chunk_text("", document_id="d1", source_path="/a.txt") == []

    def test_short_text_single_chunk(self):
        text = "hello world"
        chunks = chunk_text(text, document_id="d1", source_path="/a.txt", chunk_size=512)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "hello world"
        assert chunks[0]["document_id"] == "d1"
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["source_path"] == "/a.txt"

    def test_correct_chunk_count_and_overlap(self):
        # 100 words, chunk_size=30, overlap=10 → step=20
        # chunks start at 0,20,40,60,80 → 5 chunks
        words = [f"word{i}" for i in range(100)]
        text = " ".join(words)
        chunks = chunk_text(text, document_id="d1", source_path="/b.txt", chunk_size=30, chunk_overlap=10)

        assert len(chunks) == 5

        # Verify overlap: last 10 tokens of chunk 0 == first 10 tokens of chunk 1
        c0_tokens = chunks[0]["text"].split()
        c1_tokens = chunks[1]["text"].split()
        assert c0_tokens[-10:] == c1_tokens[:10]

    def test_chunk_indices_are_sequential(self):
        words = " ".join(f"w{i}" for i in range(200))
        chunks = chunk_text(words, document_id="d1", source_path="/c.txt", chunk_size=50, chunk_overlap=10)
        indices = [c["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_no_text_lost(self):
        """Every word in the original text appears in at least one chunk."""
        words = [f"w{i}" for i in range(150)]
        text = " ".join(words)
        chunks = chunk_text(text, document_id="d1", source_path="/d.txt", chunk_size=40, chunk_overlap=5)
        all_chunk_words = set()
        for c in chunks:
            all_chunk_words.update(c["text"].split())
        assert all_chunk_words == set(words)


class TestEmbedChunks:
    def test_empty_list(self):
        assert embed_chunks([]) == []

    @patch("my_note.services.chunker.voyageai")
    def test_embed_adds_embedding_key(self, mock_voyageai):
        mock_client = MagicMock()
        mock_voyageai.Client.return_value = mock_client
        mock_result = MagicMock()
        mock_result.embeddings = [[0.1] * 1024, [0.2] * 1024]
        mock_client.embed.return_value = mock_result

        chunks = [
            {"text": "hello", "document_id": "d1", "chunk_index": 0, "source_path": "/a.txt"},
            {"text": "world", "document_id": "d1", "chunk_index": 1, "source_path": "/a.txt"},
        ]
        result = embed_chunks(chunks, model="voyage-3")

        assert len(result) == 2
        assert "embedding" in result[0]
        assert result[0]["embedding"] == [0.1] * 1024
        assert result[1]["text"] == "world"
        mock_client.embed.assert_called_once_with(["hello", "world"], model="voyage-3")
