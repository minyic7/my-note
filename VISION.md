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
Phase 1 — Core ingestion pipeline. Escalation executed at Cycle 25.

### Progress (Cycle 25)
- **Ticket #1 (Original scaffolding)**: STOPPED — was stuck in `review` for 6 cycles (19→25). Merge queue never resolved.
- **Ticket #1-v2 (Replacement scaffolding)**: CREATED this cycle. Identical scope + Dockerfile fix (`uv sync --system`).
- Tickets #2–#8: `todo / po_proposed`, blocked on scaffolding completion.

### Active Decisions
- Ticket #1-v2 Dockerfile fix: use `uv sync --system` (not `uv pip install -r pyproject.toml`)
- Execution order: scaffolding → SQLite schema → text extraction → Qdrant → API endpoints → agent loop
- Once scaffolding-v2 merges, immediately start Ticket #2 (SQLite schema) and Ticket #3 (text extraction) in parallel

### Known Blockers and Risks
- **RESOLVED (Cycle 25):** Original Ticket #1 stopped, replacement created
- **ACTIVE RISK:** 5+ PO process restarts detected — elevated system instability
- **WATCH:** If replacement scaffolding ticket also stalls in review for 3+ cycles, consider fundamental approach change

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production.

## Upcoming Plan
1. **This cycle:** Start replacement scaffolding ticket immediately
2. **Post-merge:** Start Ticket #2 (SQLite schema) + Ticket #3 (text extraction) in parallel
3. Continue Phase 1 sequence through tickets #4-#8

## Completed Work Log
- Cycle 19: Original Ticket #1 reached review status (first code output)
- Cycles 20-24: Ticket #1 stuck in review — merge queue failing silently
- Cycle 25: ESCALATION — Stopped Ticket #1, created replacement scaffolding ticket (v2)

<!-- PO_SECTION_END -->
