"""Tests for the Qdrant client wrapper (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from my_note.services import qdrant_client as qc


@pytest.fixture
def mock_client():
    with patch.object(qc, "_get_client") as factory:
        client = MagicMock()
        factory.return_value = client
        yield client


class TestEnsureCollection:
    def test_creates_when_missing(self, mock_client):
        mock_client.get_collections.return_value.collections = []
        qc.ensure_collection("abc")
        mock_client.create_collection.assert_called_once()
        args = mock_client.create_collection.call_args
        assert args.kwargs["collection_name"] == "project_abc"

    def test_skips_when_exists(self, mock_client):
        col = MagicMock()
        col.name = "project_abc"
        mock_client.get_collections.return_value.collections = [col]
        qc.ensure_collection("abc")
        mock_client.create_collection.assert_not_called()


class TestUpsertChunks:
    def test_upsert_empty_list(self, mock_client):
        qc.upsert_chunks("p1", [])
        mock_client.upsert.assert_not_called()

    def test_upsert_sends_points(self, mock_client):
        chunks = [
            {
                "embedding": [0.0] * 1024,
                "document_id": "doc1",
                "chunk_index": 0,
                "text": "hello",
                "source_path": "file.txt",
            }
        ]
        qc.upsert_chunks("p1", chunks)
        mock_client.upsert.assert_called_once()
        call_args = mock_client.upsert.call_args
        assert call_args.kwargs["collection_name"] == "project_p1"
        points = call_args.kwargs["points"]
        assert len(points) == 1
        assert points[0].payload["document_id"] == "doc1"
        assert points[0].payload["text"] == "hello"
        assert "ingested_at" in points[0].payload


class TestSearch:
    def test_returns_results(self, mock_client):
        hit = MagicMock()
        hit.id = "id1"
        hit.score = 0.95
        hit.payload = {"text": "found", "document_id": "doc1", "chunk_index": 0}
        mock_client.query_points.return_value.points = [hit]

        results = qc.search("p1", [0.0] * 1024, limit=5)
        assert len(results) == 1
        assert results[0]["score"] == 0.95
        assert results[0]["text"] == "found"
        mock_client.query_points.assert_called_once()


class TestDeleteByDocument:
    def test_calls_delete_with_filter(self, mock_client):
        qc.delete_by_document("p1", "doc1")
        mock_client.delete.assert_called_once()
        call_args = mock_client.delete.call_args
        assert call_args.kwargs["collection_name"] == "project_p1"


class TestDeleteCollection:
    def test_calls_delete_collection(self, mock_client):
        qc.delete_collection("p1")
        mock_client.delete_collection.assert_called_once_with(collection_name="project_p1")
