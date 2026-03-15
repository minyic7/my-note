"""Text chunking and embedding service."""

from __future__ import annotations

import logging
import time
from typing import Any

import voyageai

from my_note.config import settings

logger = logging.getLogger(__name__)


def _whitespace_token_count(text: str) -> int:
    return len(text.split())


def _whitespace_tokenize(text: str) -> list[str]:
    return text.split()


def _whitespace_detokenize(tokens: list[str]) -> str:
    return " ".join(tokens)


def chunk_text(
    text: str,
    document_id: str,
    source_path: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[dict[str, Any]]:
    """Split plain text into overlapping chunks.

    Uses whitespace tokenization for v1.  Each chunk is returned as a dict
    with keys: text, document_id, chunk_index, source_path.
    """
    if chunk_size is None:
        chunk_size = settings.chunk_size
    if chunk_overlap is None:
        chunk_overlap = settings.chunk_overlap

    tokens = _whitespace_tokenize(text)
    if not tokens:
        return []

    chunks: list[dict[str, Any]] = []
    start = 0
    chunk_index = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(
            {
                "text": _whitespace_detokenize(chunk_tokens),
                "document_id": document_id,
                "chunk_index": chunk_index,
                "source_path": source_path,
            }
        )
        chunk_index += 1
        # Advance by (chunk_size - overlap), but at least 1 token
        step = max(chunk_size - chunk_overlap, 1)
        start += step
    return chunks


def embed_chunks(
    chunks: list[dict[str, Any]],
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Add embeddings to chunks using the Voyage AI API (batch).

    Returns a new list of chunk dicts, each augmented with an ``embedding`` key.
    """
    if not chunks:
        return []

    if model is None:
        model = settings.embedding_model

    texts = [c["text"] for c in chunks]

    client = voyageai.Client()
    result = client.embed(texts, model=model)

    enriched: list[dict[str, Any]] = []
    for chunk, embedding in zip(chunks, result.embeddings):
        enriched.append({**chunk, "embedding": embedding})
    return enriched


def chunk_and_embed(
    text: str,
    document_id: str,
    source_path: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
    model: str | None = None,
) -> list[dict[str, Any]]:
    """Convenience: chunk text then embed all chunks."""
    chunks = chunk_text(
        text,
        document_id=document_id,
        source_path=source_path,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return embed_chunks(chunks, model=model)
