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
Phase 1 — Core ingestion pipeline + frontend scaffolding in parallel.

### Progress (Cycle 30)
- **Ticket #1 (Scaffolding v2)**: MERGED ✅
- **Ticket #7 (Health endpoint)**: MERGED ✅
- **Tickets #2 (SQLite), #3 (Extraction), #4 (Qdrant)**: `review` — awaiting auto-merge
- **Ticket #11 (Frontend query UI)**: `review` — anomaly: reached review before dependency #9
- **Ticket #9 (Frontend scaffolding)**: STARTED this cycle (again — was started cycle 27 but reverted to todo after restarts)
- **Tickets #5, #6, #8, #10**: `todo`, correctly waiting on upstream

### Active Decisions
- Ticket #1-v2 Dockerfile fix: use `uv sync --system` (not `uv pip install -r pyproject.toml`)
- Execution order: scaffolding → SQLite schema → text extraction → Qdrant → API endpoints → agent loop
- Frontend scaffolding runs in parallel with backend — no dependency
- Frontend feature tickets (dashboard, query) can start once scaffolding merges; they'll use stub APIs until backend endpoints land

### Known Blockers and Risks
- **RESOLVED:** Original Ticket #1 scaffolding blocker (Cycle 25)
- **RESOLVED:** Ticket #7 health endpoint (Cycle 27)
- **ANOMALY:** Ticket #11 in review despite #9 (dependency) still being todo — monitor merge outcome
- **ACTIVE RISK:** 6+ PO process restarts detected — elevated system instability
- **WATCH:** 3 backend tickets in review simultaneously (#2, #3, #4) — monitor for integration conflicts at merge
- **WATCH:** Frontend tickets created without explicit dependency on backend endpoints — will need integration testing

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production. Multi-stage Docker build for frontend assets.

## Upcoming Plan
1. **This cycle:** Started #9 (frontend scaffolding); 4 tickets in review awaiting merge
2. **When #2/#3/#4 merge:** Start Ticket #5 (ingest endpoint), then #8 (query endpoint)
3. **When #5/#8 merge:** Start Ticket #6 (agent loop)
4. **When #9 merges:** Start #10 (dashboard UI); reconcile #11 status

## Completed Work Log
- Cycle 19: Original Ticket #1 reached review status
- Cycles 20-24: Ticket #1 stuck in review — merge queue failing silently
- Cycle 25: ESCALATION — Stopped Ticket #1, created replacement scaffolding ticket (v2)
- Cycle 26: Scaffolding v2 merged; 4 backend tickets started; 3 frontend tickets created
- Cycle 27: Ticket #7 merged; started Ticket #9 (frontend scaffolding)
- Cycle 30: #2, #3, #4, #11 all in review; restarted #9

<!-- PO_SECTION_END -->
