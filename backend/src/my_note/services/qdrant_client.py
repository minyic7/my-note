"""Wrapper around the Qdrant vector-database client."""

from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from my_note.config import settings

logger = logging.getLogger(__name__)

VECTOR_SIZE = 1024


def _collection_name(project_id: str) -> str:
    return f"project_{project_id}"


def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(project_id: str) -> None:
    """Create collection ``project_{project_id}`` if it does not already exist."""
    client = _get_client()
    name = _collection_name(project_id)

    existing = [c.name for c in client.get_collections().collections]
    if name in existing:
        logger.debug("Collection %s already exists", name)
        return

    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    logger.info("Created collection %s", name)


def upsert_chunks(
    project_id: str,
    chunks_with_embeddings: list[dict[str, Any]],
) -> None:
    """Upsert embedded chunks as points into the project collection.

    Each chunk dict must contain at minimum:
    ``embedding``, ``document_id``, ``chunk_index``, ``text``.
    Optional: ``source_path`` (stored as ``source_type``).
    """
    if not chunks_with_embeddings:
        return

    client = _get_client()
    name = _collection_name(project_id)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    points = []
    for chunk in chunks_with_embeddings:
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{chunk['document_id']}:{chunk['chunk_index']}"))
        points.append(
            PointStruct(
                id=point_id,
                vector=chunk["embedding"],
                payload={
                    "document_id": chunk["document_id"],
                    "chunk_index": chunk["chunk_index"],
                    "text": chunk["text"],
                    "source_type": chunk.get("source_path", ""),
                    "ingested_at": now,
                },
            )
        )

    client.upsert(collection_name=name, points=points)
    logger.info("Upserted %d points into %s", len(points), name)


def search(
    project_id: str,
    query_embedding: list[float],
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Return ranked search results from the project collection."""
    client = _get_client()
    name = _collection_name(project_id)

    hits = client.query_points(
        collection_name=name,
        query=query_embedding,
        limit=limit,
    )

    results: list[dict[str, Any]] = []
    for hit in hits.points:
        results.append(
            {
                "id": hit.id,
                "score": hit.score,
                **hit.payload,
            }
        )
    return results


def delete_by_document(project_id: str, document_id: str) -> None:
    """Remove all points belonging to *document_id* from the project collection."""
    client = _get_client()
    name = _collection_name(project_id)

    client.delete(
        collection_name=name,
        points_selector=Filter(
            must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
        ),
    )
    logger.info("Deleted points for document %s from %s", document_id, name)


def delete_collection(project_id: str) -> None:
    """Delete the entire project collection."""
    client = _get_client()
    name = _collection_name(project_id)
    client.delete_collection(collection_name=name)
    logger.info("Deleted collection %s", name)
