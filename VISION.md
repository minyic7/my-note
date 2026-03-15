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

### Progress (Cycle 33)
- **Ticket #1 (Scaffolding v2)**: MERGED ✅
- **Ticket #7 (Health endpoint)**: MERGED ✅
- **Ticket #4 (Qdrant/chunking/embedding)**: MERGED ✅
- **Ticket #10 (Frontend dashboard UI)**: MERGED ✅
- **Ticket #2 (SQLite)**: Was BLOCKED — answered blocker this cycle, should resume
- **Ticket #3 (Text extraction)**: `review` — 2nd review cycle, watching for regression
- **Ticket #9 (Frontend scaffolding)**: `in_progress` — 3rd attempt; #10 already merged ahead of it
- **Ticket #11 (Frontend query UI)**: `in_progress` — ahead of #9 scaffolding
- **Tickets #5, #8, #6**: `todo`, waiting on upstream (#2, #3)

### Active Decisions
- Ticket #1-v2 Dockerfile fix: use `uv sync --system` (not `uv pip install -r pyproject.toml`)
- Execution order: scaffolding → SQLite schema → text extraction → Qdrant → API endpoints → agent loop
- Frontend scaffolding runs in parallel with backend — no dependency
- Frontend feature tickets (dashboard, query) can start once scaffolding merges; they'll use stub APIs until backend endpoints land
- **SQLite schema confirmed**: 8 tables (projects, documents, chunks, findings, entities, relations, chat_history, analysis_log) — decision given to unblock #2

### Known Blockers and Risks
- **RESOLVED:** Ticket #2 blocker — answered schema question (Cycle 33)
- **ANOMALY:** Ticket #10 merged and #11 in-flight despite #9 (dependency) still not merged — will need reconciliation
- **WATCH:** #3 in 2nd review — if regresses again, stop and recreate
- **WATCH:** #9 on 3rd attempt — if fails again, stop and recreate
- **ACTIVE RISK:** 6+ PO process restarts detected — elevated system instability

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production. Multi-stage Docker build for frontend assets.

## Upcoming Plan
1. **This cycle:** Unblocked #2; #3 in review; #9 and #11 in progress
2. **When #2/#3 merge:** Start Ticket #5 (ingest endpoint), then #8 (query endpoint)
3. **When #5/#8 merge:** Start Ticket #6 (agent loop)
4. **When #9 merges:** Reconcile #10/#11, ensure they build correctly on scaffolding
5. **If board clears:** Consider creating remaining tickets (integration tests, agent analysis features)

## Completed Work Log
- Cycle 19: Original Ticket #1 reached review status
- Cycles 20-24: Ticket #1 stuck in review — merge queue failing silently
- Cycle 25: ESCALATION — Stopped Ticket #1, created replacement scaffolding ticket (v2)
- Cycle 26: Scaffolding v2 merged; 4 backend tickets started; 3 frontend tickets created
- Cycle 27: Ticket #7 merged; started Ticket #9 (frontend scaffolding)
- Cycle 30: #2, #3, #4, #11 all in review; restarted #9
- Cycle 31: #4 merged; started #9 again (3rd attempt)
- Cycle 32: Started #9 again; board saturated at 8 active
- Cycle 33: #10 merged; unblocked #2 (schema question answered)

<!-- PO_SECTION_END -->
