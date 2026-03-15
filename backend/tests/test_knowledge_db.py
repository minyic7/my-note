"""Tests for KnowledgeDB CRUD operations."""

import pytest
import pytest_asyncio

from my_note.services.knowledge_db import KnowledgeDB


@pytest_asyncio.fixture
async def db(tmp_path):
    """Create a fresh in-memory-like database for each test."""
    db_path = str(tmp_path / "test.db")
    kdb = await KnowledgeDB.init_db(db_path)
    yield kdb
    await kdb.close()


# ------------------------------------------------------------------
# Projects
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_project(db: KnowledgeDB):
    proj = await db.create_project("Test Project", "A description")
    assert proj["name"] == "Test Project"
    assert proj["description"] == "A description"
    assert proj["id"]

    fetched = await db.get_project(proj["id"])
    assert fetched is not None
    assert fetched["name"] == "Test Project"


@pytest.mark.asyncio
async def test_list_projects(db: KnowledgeDB):
    await db.create_project("P1")
    await db.create_project("P2")
    projects = await db.list_projects()
    assert len(projects) == 2


@pytest.mark.asyncio
async def test_delete_project(db: KnowledgeDB):
    proj = await db.create_project("To Delete")
    assert await db.delete_project(proj["id"]) is True
    assert await db.get_project(proj["id"]) is None


@pytest.mark.asyncio
async def test_get_nonexistent_project(db: KnowledgeDB):
    assert await db.get_project("nonexistent") is None


# ------------------------------------------------------------------
# Documents
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_and_get_document(db: KnowledgeDB):
    proj = await db.create_project("DocProject")
    doc = await db.create_document(proj["id"], "My Doc", "pdf", source_path="/tmp/test.pdf")
    assert doc["source_type"] == "pdf"
    assert doc["chunk_count"] == 0
    assert doc["analysis_done"] == 0

    fetched = await db.get_document(doc["id"])
    assert fetched is not None
    assert fetched["title"] == "My Doc"


@pytest.mark.asyncio
async def test_list_documents(db: KnowledgeDB):
    proj = await db.create_project("DocProject")
    await db.create_document(proj["id"], "D1", "text")
    await db.create_document(proj["id"], "D2", "url", source_url="https://example.com")
    docs = await db.list_documents(proj["id"])
    assert len(docs) == 2


@pytest.mark.asyncio
async def test_update_document_status(db: KnowledgeDB):
    proj = await db.create_project("DocProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    await db.update_document_status(doc["id"], analysis_done=1, chunk_count=10)
    fetched = await db.get_document(doc["id"])
    assert fetched["analysis_done"] == 1
    assert fetched["chunk_count"] == 10


@pytest.mark.asyncio
async def test_delete_document(db: KnowledgeDB):
    proj = await db.create_project("DocProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    assert await db.delete_document(doc["id"]) is True
    assert await db.get_document(doc["id"]) is None


# ------------------------------------------------------------------
# Chunks
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_and_get_chunks(db: KnowledgeDB):
    proj = await db.create_project("ChunkProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    chunks = [
        {"document_id": doc["id"], "project_id": proj["id"], "chunk_index": 0, "text": "Hello world", "token_count": 2},
        {"document_id": doc["id"], "project_id": proj["id"], "chunk_index": 1, "text": "Second chunk"},
    ]
    ids = await db.insert_chunks(chunks)
    assert len(ids) == 2

    fetched = await db.get_chunks_by_document(doc["id"])
    assert len(fetched) == 2
    assert fetched[0]["chunk_index"] == 0
    assert fetched[1]["chunk_index"] == 1


# ------------------------------------------------------------------
# Findings
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_insert_and_list_findings(db: KnowledgeDB):
    proj = await db.create_project("FindProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    findings = [
        {"project_id": proj["id"], "type": "risk", "content": "Something risky", "severity": "high", "source_docs": [doc["id"]]},
        {"project_id": proj["id"], "type": "insight", "content": "An insight", "source_docs": [doc["id"]]},
    ]
    ids = await db.insert_findings(findings)
    assert len(ids) == 2

    all_findings = await db.list_findings(proj["id"])
    assert len(all_findings) == 2

    risks = await db.list_findings(proj["id"], type_filter="risk")
    assert len(risks) == 1
    assert risks[0]["severity"] == "high"

    high = await db.list_findings(proj["id"], severity_filter="high")
    assert len(high) == 1


@pytest.mark.asyncio
async def test_update_finding(db: KnowledgeDB):
    proj = await db.create_project("FindProject")
    ids = await db.insert_findings([
        {"project_id": proj["id"], "type": "risk", "content": "A risk", "severity": "medium", "source_docs": []},
    ])
    await db.update_finding(ids[0], status="acknowledged", annotation="Noted")
    findings = await db.list_findings(proj["id"])
    assert findings[0]["status"] == "acknowledged"
    assert findings[0]["annotation"] == "Noted"


@pytest.mark.asyncio
async def test_list_findings_status_filter(db: KnowledgeDB):
    proj = await db.create_project("FindProject")
    ids = await db.insert_findings([
        {"project_id": proj["id"], "type": "risk", "content": "R1", "source_docs": []},
        {"project_id": proj["id"], "type": "gap", "content": "G1", "source_docs": []},
    ])
    await db.update_finding(ids[0], status="resolved")
    open_findings = await db.list_findings(proj["id"], status_filter="open")
    assert len(open_findings) == 1
    assert open_findings[0]["type"] == "gap"


# ------------------------------------------------------------------
# Entities & Relations
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_entity(db: KnowledgeDB):
    proj = await db.create_project("EntityProject")
    result = await db.upsert_entity(proj["id"], "AuthService", entity_type="system")
    assert result["upserted"] == "created"

    result2 = await db.upsert_entity(proj["id"], "AuthService", description="Handles auth")
    assert result2["upserted"] == "updated"
    assert result2["id"] == result["id"]

    entities = await db.list_entities(proj["id"])
    assert len(entities) == 1


@pytest.mark.asyncio
async def test_insert_relation(db: KnowledgeDB):
    proj = await db.create_project("RelProject")
    e1 = await db.upsert_entity(proj["id"], "A", entity_type="system")
    e2 = await db.upsert_entity(proj["id"], "B", entity_type="system")
    rid = await db.insert_relation(proj["id"], e1["id"], e2["id"], "depends_on")
    assert rid

    rels = await db.list_relations(proj["id"])
    assert len(rels) == 1
    assert rels[0]["relation"] == "depends_on"


# ------------------------------------------------------------------
# Chat history
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_history(db: KnowledgeDB):
    proj = await db.create_project("ChatProject")
    msg_id = await db.add_chat_message(proj["id"], "user", "Hello")
    assert msg_id > 0

    await db.add_chat_message(proj["id"], "agent", "Hi!", sources=[{"doc": "123"}])

    history = await db.get_chat_history(proj["id"])
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["sources"] is not None

    count = await db.clear_chat_history(proj["id"])
    assert count == 2
    assert await db.get_chat_history(proj["id"]) == []


# ------------------------------------------------------------------
# Analysis log
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_analysis(db: KnowledgeDB):
    proj = await db.create_project("LogProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    log_id = await db.log_analysis(doc["id"], observe_summary="Observed X", think_output="Thought Y")
    assert log_id > 0


# ------------------------------------------------------------------
# Cascade delete
# ------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cascade_delete_project(db: KnowledgeDB):
    proj = await db.create_project("CascadeProject")
    doc = await db.create_document(proj["id"], "D1", "text")
    await db.insert_chunks([
        {"document_id": doc["id"], "project_id": proj["id"], "chunk_index": 0, "text": "chunk"},
    ])
    await db.insert_findings([
        {"project_id": proj["id"], "type": "risk", "content": "R", "source_docs": [doc["id"]]},
    ])
    e = await db.upsert_entity(proj["id"], "E1", entity_type="system")
    e2 = await db.upsert_entity(proj["id"], "E2", entity_type="system")
    await db.insert_relation(proj["id"], e["id"], e2["id"], "calls")
    await db.add_chat_message(proj["id"], "user", "Hi")
    await db.log_analysis(doc["id"], observe_summary="obs")

    # Delete project and verify everything is gone
    assert await db.delete_project(proj["id"]) is True
    assert await db.get_project(proj["id"]) is None
    assert await db.get_document(doc["id"]) is None
    assert await db.list_findings(proj["id"]) == []
    assert await db.list_entities(proj["id"]) == []
    assert await db.list_relations(proj["id"]) == []
    assert await db.get_chat_history(proj["id"]) == []
    assert await db.get_chunks_by_document(doc["id"]) == []
