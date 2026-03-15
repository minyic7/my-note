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
Phase 1 — Core ingestion pipeline. 8 tickets created and correctly sequenced. ZERO executed after 15+ cycles.

### Active Decisions
- Ticket #1 Dockerfile fix: use `uv sync --system` (not `uv pip install -r pyproject.toml`)
- Execution order: scaffolding → SQLite schema → text extraction → Qdrant → API endpoints → agent loop
- Raised critical escalation to user (cycle 15) requesting dev agent verification

### Known Blockers and Risks
- **CRITICAL (since cycle 1):** No implementing agent has produced any output in 15 cycles across 6+ restarts
- **Ticket #1 blocked:** Dockerfile syntax error — answer ready (`uv sync --system`), need UUID to unblock
- **Root cause:** Either no dev agent is connected, or dispatch mechanism is broken — PO cannot diagnose further
- **Need from user:** Confirm dev agent is running; provide ticket UUIDs so PO can issue start_ticket/answer_ticket

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production.

## Upcoming Plan
Once dev agent is confirmed running:
1. Unblock Ticket #1 (answer Dockerfile question)
2. Start Ticket #1 (scaffolding)
3. Start Ticket #2 (SQLite schema) once #1 completes
4. Continue Phase 1 sequence through tickets #3-#8

## Completed Work Log
No work completed yet. (Cycle 15)

<!-- PO_SECTION_END -->
