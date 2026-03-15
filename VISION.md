# VISION.md

<!-- USER_SECTION_START — DO NOT MODIFY BELOW (PO READ ONLY) -->

## Goal

Build a local-first AI knowledge agent that accumulates understanding of project materials over time. You drop in documents, code files, URLs, or raw text — the agent reads, connects, and remembers. When you need context on a project, it has already done the analysis: identified risks, flagged missing information, found contradictions between documents, and mapped key entities and their relationships.

The core value is **persistent project understanding that grows with every document ingested**, not a search engine or a one-shot summarizer. The most valuable output is surfacing what is *absent* — "no rollback plan is mentioned across all 12 documents" is more useful than any summary of what is there.

## Scope and Constraints

- **Deployment**: Docker Compose only, runs entirely on the user's local machine. No cloud, no SaaS, no external data storage. Data never leaves the machine.
- **Target users**: Single user, no authentication needed, no multi-user support.
- **Input formats**: PDF, Word (.docx), URL/webpage, code files (.py, .sql, .js, .ts, etc.), plain text, Markdown. All formats are converted to plain text before any LLM processing.
- **Storage**: Qdrant (vector search, runs in Docker) + SQLite (structured memory, local file). Raw documents and extracted text stored on local filesystem.
- **Stack**:
  - Backend: Python 3.12+, FastAPI, asyncio
  - Vector DB: Qdrant (Docker)
  - Structured DB: SQLite
  - Frontend: React 19, TypeScript, Vite, Tailwind CSS
  - Package managers: uv (backend), pnpm (frontend)
  - Containerization: Docker Compose
- **LLM**: Anthropic API (claude-sonnet-4-6 for OBSERVE/summarization, claude-opus-4-6 for THINK/analysis with extended thinking). API key provided via environment variable.
- **Embedding**: Anthropic voyage-3 via API (configurable, can swap to local model).
- **Port**: 8800 (backend API + serves static frontend in production).
- **Out of scope**: Multi-user, real-time data streams, log/transaction processing, cloud deployment, authentication, sharing or collaboration features.
- **Must not**: Send any document content or user data to external services other than Anthropic API for LLM inference.

<!-- USER_SECTION_END -->

<!-- PO_SECTION_START — MAINTAINED BY PO AGENT -->

## PO Memory

### Current Phase
Project not started. First cycle: establish repository structure, Docker Compose, and basic ingestion pipeline.

### Active Decisions
None yet.

### Known Blockers and Risks
None yet.

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production, Vite dev server in development.

## Upcoming Plan
Phase 1 — core ingestion pipeline and basic query. See execution order below.

## Completed Work Log
No work completed yet.

<!-- PO_SECTION_END -->

---

## Technical Reference (for PO and implementation)

This section provides detailed technical context for the PO Agent and implementing agents. It is maintained by the user and should not be modified by PO.

---

### Repository Structure

```
my-note/
  backend/
    src/
      my_note/
        main.py              # FastAPI app entry, lifespan
        config.py            # Settings (MY_NOTE_ prefix env vars)
        routers/
          projects.py        # Project CRUD
          ingest.py          # Document ingestion
          query.py           # Query and chat
          findings.py        # Risks, gaps, conflicts CRUD
          skills.py          # Skill management
        services/
          agent.py           # KnowledgeAgent class (long-running asyncio)
          extractor.py       # Text extraction for all formats
          chunker.py         # Chunking + embedding
          qdrant_client.py   # Qdrant wrapper
          knowledge_db.py    # SQLite wrapper
          skill_manager.py   # Skill loading and crystallization
        models/
          project.py
          document.py
          finding.py
          skill.py
  frontend/
    src/
      App.tsx
      components/
        IngestPanel/
        MemoryView/
        ChatPanel/
        SkillsPanel/
  docker-compose.yml
  docker-compose.dev.yml
  Dockerfile
  .env.example
  VISION.md                  # This file (on main branch)
```

---

### Ingestion Pipeline (critical path)

Text extraction runs BEFORE any LLM call. All formats become plain UTF-8 text first.

```
Input file/URL
  → extractor.py
      PDF:    pdfplumber.open() → extract_text() per page
              fallback: pytesseract if pdfplumber returns empty (scanned PDF)
      DOCX:   python-docx Document() → paragraph text joined
      URL:    trafilatura.fetch_url() → trafilatura.extract()
      Code:   read as-is, detect language from file extension
      Text/MD: read as-is
  → plain text string
  → chunker.py
      split into 512-token chunks with ~50-token overlap
      each chunk: {text, document_id, chunk_index, source_path}
  → embed each chunk (voyage-3 via Anthropic API)
  → store in Qdrant (collection per project)
  → store chunk metadata in SQLite chunks table
  → trigger analysis pass (OBSERVE → THINK → ACT → RECORD)
```

Chunk size (512) and overlap (50) are config values, not hardcoded.

---

### Analysis Pass (runs once per document at ingest time)

The analysis pass is the core intelligence. It runs once at ingest — never at query time. This makes queries fast and analysis thorough.

**OBSERVE** (claude-sonnet-4-6, cheap and fast):
- Input: full document text + existing project memory summary + relevant skills
- Output: structured JSON — what's new vs already known, which entities appear, which skills apply

**THINK** (claude-opus-4-6, extended thinking, budget 6000 tokens):
- Input: OBSERVE summary + full project memory
- Output: structured JSON with these fields:
  ```json
  {
    "entities": [{"name": str, "type": str, "description": str}],
    "relations": [{"from": str, "to": str, "relation": str, "confidence": float}],
    "risks": [{"content": str, "severity": "high|medium|low", "rationale": str}],
    "gaps": [{"content": str, "what_implies_it": str, "missing_artifact": str}],
    "conflicts": [{"content": str, "doc_a_says": str, "doc_b_says": str}],
    "insights": [{"content": str}]
  }
  ```

**Gap detection prompt (critical — must be explicit):**
The THINK prompt must explicitly ask:
```
"What important information is conspicuously absent from this project?
What would a senior engineer expect to find in a well-documented project
of this type that is missing here? Be specific: name the missing artifact,
explain why it should exist, and cite which existing documents imply it
should exist but don't provide it."
```
Without this explicit prompt, LLMs default to summarizing what IS there. Gap detection is the most valuable feature — do not let it be implicit.

**ACT** (deterministic, no LLM):
- Write all findings to SQLite
- Update entities and relations tables
- Record analysis in analysis_log

---

### SQLite Schema

```sql
CREATE TABLE projects (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    description TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE documents (
    id            TEXT PRIMARY KEY,
    project_id    TEXT NOT NULL REFERENCES projects(id),
    title         TEXT,
    source_type   TEXT NOT NULL,  -- pdf | url | code | text | docx
    source_path   TEXT,
    source_url    TEXT,
    ingested_at   TEXT NOT NULL,
    chunk_count   INTEGER DEFAULT 0,
    analysis_done INTEGER DEFAULT 0,  -- 0=pending, 1=done, 2=failed
    error_message TEXT
);

CREATE TABLE chunks (
    id          TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id),
    project_id  TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text        TEXT NOT NULL,
    token_count INTEGER
);

CREATE TABLE findings (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id),
    type        TEXT NOT NULL,   -- risk | gap | conflict | insight
    content     TEXT NOT NULL,
    severity    TEXT,            -- high | medium | low (risks only)
    source_docs TEXT NOT NULL,   -- JSON array of document_ids
    status      TEXT NOT NULL DEFAULT 'open',  -- open | acknowledged | resolved
    annotation  TEXT,            -- user note added via dashboard
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE entities (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL REFERENCES projects(id),
    name         TEXT NOT NULL,
    type         TEXT,           -- system | person | table | model | concept | process
    description  TEXT,
    first_seen   TEXT REFERENCES documents(id),
    last_updated TEXT NOT NULL
);

CREATE TABLE relations (
    id           TEXT PRIMARY KEY,
    project_id   TEXT NOT NULL,
    from_entity  TEXT REFERENCES entities(id),
    to_entity    TEXT REFERENCES entities(id),
    relation     TEXT NOT NULL,  -- depends_on | owned_by | feeds_into | calls | etc
    source_doc   TEXT REFERENCES documents(id),
    confidence   REAL DEFAULT 1.0
);

CREATE TABLE chat_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT NOT NULL,
    role       TEXT NOT NULL,    -- user | agent
    content    TEXT NOT NULL,
    timestamp  TEXT NOT NULL,
    sources    TEXT             -- JSON array of {document_id, chunk_index, excerpt}
);

CREATE TABLE analysis_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id     TEXT NOT NULL REFERENCES documents(id),
    observe_summary TEXT,
    think_output    TEXT,
    created_at      TEXT NOT NULL
);
```

---

### Qdrant Setup

One collection per project, named `project_{project_id}`.

Vector dimensions: 1024 (voyage-3 output dimension).
Distance: Cosine.

Each point payload:
```json
{
  "document_id": "...",
  "chunk_index": 0,
  "text": "...",
  "source_type": "pdf",
  "ingested_at": "2026-03-15T00:00:00Z"
}
```

---

### Skill System

Skills live at `~/.my-note/skills/` (or `/data/skills/` inside Docker).

Format follows the Anthropic Agent Skills standard:

```markdown
---
name: skill-name-kebab-case
description: One line, max 15 words, describes when this skill applies
confidence: 0.85
usage_count: 0
created_at: 2026-03-15T00:00:00Z
last_used_at: null
---

# Skill Title

## When this applies
[Describe the document type or situation that triggers this skill]

## What to look for
[Specific things the agent should check for — be concrete]

## Learned from
[Which documents or analysis cycles produced this insight]
```

`index.md` — loaded every analysis cycle (tiny, ~50 tokens total):
```markdown
# Skills Index

001_data_lineage.md: When analyzing ETL or data pipeline documents, look for undocumented transformations
002_risk_gap.md: For compliance or audit documents, check for missing approval processes
```

**Loading:** OBSERVE step loads index.md, selects 1-3 relevant skills, THINK step receives full skill content.

**Crystallization:** triggers every 5 documents analyzed. Max 1 skill proposal per batch. User approves via Skills panel in dashboard. Max 20 skills total — consolidate when approaching limit.

---

### API Endpoints

```
# Projects
POST   /api/projects                    → create project
GET    /api/projects                    → list all projects
GET    /api/projects/{id}               → get project details
DELETE /api/projects/{id}               → delete project and all its data

# Ingestion
POST   /api/projects/{id}/ingest        → ingest file (multipart) or {url} or {text}
GET    /api/projects/{id}/documents     → list documents with status
DELETE /api/documents/{id}              → delete document and its findings
POST   /api/documents/{id}/retry        → retry failed analysis

# Memory / Findings
GET    /api/projects/{id}/findings      → list findings (filter: type, severity, status)
PATCH  /api/findings/{id}              → update status or annotation
GET    /api/projects/{id}/entities      → list entities
GET    /api/projects/{id}/relations     → list relations (for graph view)

# Query / Chat
POST   /api/projects/{id}/query        → {question: str} → {answer, sources, findings}
GET    /api/projects/{id}/chat         → get chat history
DELETE /api/projects/{id}/chat         → clear chat history

# Skills
GET    /api/skills                     → list all skills
POST   /api/skills                     → create skill manually {content: markdown}
PUT    /api/skills/{id}                → update skill content
DELETE /api/skills/{id}               → delete skill
POST   /api/skills/{id}/approve        → approve pending crystallization proposal
POST   /api/skills/{id}/reject         → reject proposal

# System
GET    /api/health                     → {status, qdrant, sqlite, agent_running}
```

---

### Environment Variables (.env.example)

```
ANTHROPIC_API_KEY=sk-ant-...
MY_NOTE_PORT=8800
MY_NOTE_DATA_DIR=/data          # inside Docker
MY_NOTE_QDRANT_URL=http://qdrant:6333
MY_NOTE_CHUNK_SIZE=512
MY_NOTE_CHUNK_OVERLAP=50
MY_NOTE_EMBEDDING_MODEL=voyage-3
MY_NOTE_OBSERVE_MODEL=claude-sonnet-4-6
MY_NOTE_THINK_MODEL=claude-opus-4-6
MY_NOTE_THINK_BUDGET=6000
```

---

### Docker Compose

```yaml
# docker-compose.yml (base)
services:
  app:
    build: .
    ports:
      - "8800:8800"
    volumes:
      - my_note_data:/data
    env_file: .env
    depends_on:
      qdrant:
        condition: service_healthy
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  my_note_data:
  qdrant_data:
```

---

### Execution Order for PO Agent

```
Phase 1 — Core ingestion pipeline:
  - Project structure + Docker Compose + Dockerfile
  - SQLite schema + KnowledgeDB wrapper (knowledge_db.py)
  - Text extraction for all formats (extractor.py)
  - Qdrant setup + chunking + embedding (chunker.py, qdrant_client.py)
  - POST /api/projects/{id}/ingest endpoint
  - OBSERVE → THINK → ACT analysis loop (agent.py)
  - POST /api/projects/{id}/query endpoint (basic version)
  - GET /api/health endpoint

Phase 2 — Memory quality and retrieval:
  - Entity / risk / gap / conflict structured extraction in THINK
  - Gap detection with explicit absence prompt
  - Combined Qdrant + SQLite query synthesis
  - Chat history with source citations
  - GET /api/projects/{id}/findings, /entities, /relations

Phase 3 — Dashboard:
  - Ingest panel (drag-drop, URL, paste text)
  - Memory view tabs (risks, gaps, conflicts, entities)
  - Chat panel with source excerpt display
  - Document list with status, error message, retry button

Phase 4 — Skills and evolution:
  - Skill loading + injection into analysis
  - Crystallization trigger (every 5 documents)
  - Skills panel (list, approve, reject, edit, add manually)
  - Multi-project switching in UI
```
