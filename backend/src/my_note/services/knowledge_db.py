"""Async SQLite wrapper for the my-note knowledge database."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4

import aiosqlite

_SCHEMA_SQL = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS documents (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL REFERENCES projects(id),
    title         TEXT,
    source_type   TEXT NOT NULL,
    source_path   TEXT,
    source_url    TEXT,
    ingested_at   TEXT NOT NULL,
    chunk_count   INTEGER DEFAULT 0,
    analysis_done INTEGER DEFAULT 0,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS chunks (
    id          TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    project_id  TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text        TEXT NOT NULL,
    token_count INTEGER
);

CREATE TABLE IF NOT EXISTS findings (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    type        TEXT NOT NULL,
    content     TEXT NOT NULL,
    severity    TEXT,
    source_docs TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'open',
    annotation  TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS entities (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL REFERENCES projects(id),
    name         TEXT NOT NULL,
    type         TEXT,
    description  TEXT,
    first_seen   TEXT REFERENCES documents(id),
    last_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS relations (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    from_entity  TEXT REFERENCES entities(id),
    to_entity    TEXT REFERENCES entities(id),
    relation     TEXT NOT NULL,
    source_doc   TEXT REFERENCES documents(id),
    confidence   REAL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS chat_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    role       TEXT NOT NULL,
    content    TEXT NOT NULL,
    timestamp  TEXT NOT NULL,
    sources    TEXT
);

CREATE TABLE IF NOT EXISTS analysis_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id     TEXT NOT NULL REFERENCES documents(id),
    observe_summary TEXT,
    think_output    TEXT,
    created_at      TEXT NOT NULL
);
"""


def _uid() -> str:
    return uuid4().hex


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeDB:
    """Async wrapper around the SQLite knowledge store."""

    def __init__(self, db: aiosqlite.Connection) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    async def init_db(cls, db_path: str) -> "KnowledgeDB":
        """Open (or create) the database and ensure all tables exist."""
        db = await aiosqlite.connect(db_path)
        db.row_factory = aiosqlite.Row
        await db.executescript(_SCHEMA_SQL)
        await db.execute("PRAGMA foreign_keys = ON")
        await db.commit()
        return cls(db)

    async def close(self) -> None:
        await self._db.close()

    # ------------------------------------------------------------------
    # Projects
    # ------------------------------------------------------------------

    async def create_project(self, name: str, description: str | None = None) -> dict:
        uid = _uid()
        now = _now()
        await self._db.execute(
            "INSERT INTO projects (id, name, description, created_at) VALUES (?, ?, ?, ?)",
            (uid, name, description, now),
        )
        await self._db.commit()
        return {"id": uid, "name": name, "description": description, "created_at": now}

    async def get_project(self, project_id: str) -> dict | None:
        cur = await self._db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def list_projects(self) -> list[dict]:
        cur = await self._db.execute("SELECT * FROM projects ORDER BY created_at DESC")
        return [dict(r) for r in await cur.fetchall()]

    async def delete_project(self, project_id: str) -> bool:
        """Cascade-delete a project and all related data."""
        # Delete in dependency order to satisfy foreign keys.
        await self._db.execute(
            "DELETE FROM analysis_log WHERE document_id IN (SELECT id FROM documents WHERE project_id = ?)",
            (project_id,),
        )
        await self._db.execute("DELETE FROM chunks WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM relations WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM entities WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM findings WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM chat_history WHERE project_id = ?", (project_id,))
        await self._db.execute("DELETE FROM documents WHERE project_id = ?", (project_id,))
        cur = await self._db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await self._db.commit()
        return cur.rowcount > 0

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    async def create_document(
        self,
        project_id: str,
        title: str | None,
        source_type: str,
        source_path: str | None = None,
        source_url: str | None = None,
    ) -> dict:
        uid = _uid()
        now = _now()
        await self._db.execute(
            """INSERT INTO documents
               (id, project_id, title, source_type, source_path, source_url, ingested_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (uid, project_id, title, source_type, source_path, source_url, now),
        )
        await self._db.commit()
        return {
            "id": uid,
            "project_id": project_id,
            "title": title,
            "source_type": source_type,
            "source_path": source_path,
            "source_url": source_url,
            "ingested_at": now,
            "chunk_count": 0,
            "analysis_done": 0,
            "error_message": None,
        }

    async def get_document(self, doc_id: str) -> dict | None:
        cur = await self._db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def list_documents(self, project_id: str) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM documents WHERE project_id = ? ORDER BY ingested_at DESC",
            (project_id,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def update_document_status(
        self,
        doc_id: str,
        analysis_done: int,
        error_message: str | None = None,
        chunk_count: int | None = None,
    ) -> bool:
        parts: list[str] = ["analysis_done = ?"]
        params: list = [analysis_done]
        if error_message is not None:
            parts.append("error_message = ?")
            params.append(error_message)
        if chunk_count is not None:
            parts.append("chunk_count = ?")
            params.append(chunk_count)
        params.append(doc_id)
        cur = await self._db.execute(
            f"UPDATE documents SET {', '.join(parts)} WHERE id = ?",
            params,
        )
        await self._db.commit()
        return cur.rowcount > 0

    async def delete_document(self, doc_id: str) -> bool:
        await self._db.execute(
            "DELETE FROM analysis_log WHERE document_id = ?", (doc_id,)
        )
        await self._db.execute(
            "DELETE FROM chunks WHERE document_id = ?", (doc_id,)
        )
        cur = await self._db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        await self._db.commit()
        return cur.rowcount > 0

    # ------------------------------------------------------------------
    # Chunks
    # ------------------------------------------------------------------

    async def insert_chunks(self, chunks: list[dict]) -> list[str]:
        """Insert a batch of chunks. Each dict needs document_id, project_id, chunk_index, text, and optionally token_count."""
        ids: list[str] = []
        for c in chunks:
            uid = _uid()
            ids.append(uid)
            await self._db.execute(
                """INSERT INTO chunks (id, document_id, project_id, chunk_index, text, token_count)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (uid, c["document_id"], c["project_id"], c["chunk_index"], c["text"], c.get("token_count")),
            )
        await self._db.commit()
        return ids

    async def get_chunks_by_document(self, doc_id: str) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index",
            (doc_id,),
        )
        return [dict(r) for r in await cur.fetchall()]

    # ------------------------------------------------------------------
    # Findings
    # ------------------------------------------------------------------

    async def insert_findings(self, findings: list[dict]) -> list[str]:
        """Insert findings. Each dict needs project_id, type, content, source_docs (list), and optionally severity."""
        ids: list[str] = []
        now = _now()
        for f in findings:
            uid = _uid()
            ids.append(uid)
            source_docs = f["source_docs"]
            if isinstance(source_docs, list):
                source_docs = json.dumps(source_docs)
            await self._db.execute(
                """INSERT INTO findings
                   (id, project_id, type, content, severity, source_docs, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?)""",
                (uid, f["project_id"], f["type"], f["content"], f.get("severity"), source_docs, now, now),
            )
        await self._db.commit()
        return ids

    async def list_findings(
        self,
        project_id: str,
        type_filter: str | None = None,
        severity_filter: str | None = None,
        status_filter: str | None = None,
    ) -> list[dict]:
        sql = "SELECT * FROM findings WHERE project_id = ?"
        params: list = [project_id]
        if type_filter:
            sql += " AND type = ?"
            params.append(type_filter)
        if severity_filter:
            sql += " AND severity = ?"
            params.append(severity_filter)
        if status_filter:
            sql += " AND status = ?"
            params.append(status_filter)
        sql += " ORDER BY created_at DESC"
        cur = await self._db.execute(sql, params)
        return [dict(r) for r in await cur.fetchall()]

    async def update_finding(
        self, finding_id: str, status: str | None = None, annotation: str | None = None
    ) -> bool:
        parts: list[str] = ["updated_at = ?"]
        params: list = [_now()]
        if status is not None:
            parts.append("status = ?")
            params.append(status)
        if annotation is not None:
            parts.append("annotation = ?")
            params.append(annotation)
        params.append(finding_id)
        cur = await self._db.execute(
            f"UPDATE findings SET {', '.join(parts)} WHERE id = ?",
            params,
        )
        await self._db.commit()
        return cur.rowcount > 0

    # ------------------------------------------------------------------
    # Entities / Relations
    # ------------------------------------------------------------------

    async def upsert_entity(
        self,
        project_id: str,
        name: str,
        entity_type: str | None = None,
        description: str | None = None,
        first_seen: str | None = None,
    ) -> dict:
        now = _now()
        # Try update first (match on project_id + name)
        cur = await self._db.execute(
            "SELECT id FROM entities WHERE project_id = ? AND name = ?",
            (project_id, name),
        )
        existing = await cur.fetchone()
        if existing:
            eid = existing["id"]
            parts = ["last_updated = ?"]
            params: list = [now]
            if entity_type is not None:
                parts.append("type = ?")
                params.append(entity_type)
            if description is not None:
                parts.append("description = ?")
                params.append(description)
            params.append(eid)
            await self._db.execute(
                f"UPDATE entities SET {', '.join(parts)} WHERE id = ?", params
            )
            await self._db.commit()
            return {"id": eid, "project_id": project_id, "name": name, "upserted": "updated"}

        eid = _uid()
        await self._db.execute(
            """INSERT INTO entities (id, project_id, name, type, description, first_seen, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (eid, project_id, name, entity_type, description, first_seen, now),
        )
        await self._db.commit()
        return {"id": eid, "project_id": project_id, "name": name, "upserted": "created"}

    async def insert_relation(
        self,
        project_id: str,
        from_entity: str,
        to_entity: str,
        relation: str,
        source_doc: str | None = None,
        confidence: float = 1.0,
    ) -> str:
        uid = _uid()
        await self._db.execute(
            """INSERT INTO relations (id, project_id, from_entity, to_entity, relation, source_doc, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (uid, project_id, from_entity, to_entity, relation, source_doc, confidence),
        )
        await self._db.commit()
        return uid

    async def list_entities(self, project_id: str) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM entities WHERE project_id = ? ORDER BY name", (project_id,)
        )
        return [dict(r) for r in await cur.fetchall()]

    async def list_relations(self, project_id: str) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM relations WHERE project_id = ?", (project_id,)
        )
        return [dict(r) for r in await cur.fetchall()]

    # ------------------------------------------------------------------
    # Chat history
    # ------------------------------------------------------------------

    async def add_chat_message(
        self,
        project_id: str,
        role: str,
        content: str,
        sources: list | None = None,
    ) -> int:
        now = _now()
        sources_json = json.dumps(sources) if sources else None
        cur = await self._db.execute(
            """INSERT INTO chat_history (project_id, role, content, timestamp, sources)
               VALUES (?, ?, ?, ?, ?)""",
            (project_id, role, content, now, sources_json),
        )
        await self._db.commit()
        return cur.lastrowid  # type: ignore[return-value]

    async def get_chat_history(self, project_id: str) -> list[dict]:
        cur = await self._db.execute(
            "SELECT * FROM chat_history WHERE project_id = ? ORDER BY id", (project_id,)
        )
        return [dict(r) for r in await cur.fetchall()]

    async def clear_chat_history(self, project_id: str) -> int:
        cur = await self._db.execute(
            "DELETE FROM chat_history WHERE project_id = ?", (project_id,)
        )
        await self._db.commit()
        return cur.rowcount

    # ------------------------------------------------------------------
    # Analysis log
    # ------------------------------------------------------------------

    async def log_analysis(
        self,
        document_id: str,
        observe_summary: str | None = None,
        think_output: str | None = None,
    ) -> int:
        now = _now()
        cur = await self._db.execute(
            """INSERT INTO analysis_log (document_id, observe_summary, think_output, created_at)
               VALUES (?, ?, ?, ?)""",
            (document_id, observe_summary, think_output, now),
        )
        await self._db.commit()
        return cur.lastrowid  # type: ignore[return-value]
