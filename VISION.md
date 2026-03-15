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
Phase 1 — Core ingestion pipeline. Original 8 tickets created but ALL stuck for 13+ cycles. Fresh bootstrapping ticket created in cycle 14 with no dependencies as workaround.

### Active Decisions
- Created replacement scaffolding ticket (cycle 14) with zero dependencies to bypass stuck ticket #1
- Original tickets #2-#8 will need their dependency updated to point to new ticket once it completes
- Execution order follows VISION.md Phase 1

### Known Blockers and Risks
- **CRITICAL (since cycle 1):** No implementing agent has produced output in 14 cycles across 6 restarts
- **Mitigation attempted (cycle 14):** Fresh ticket with no dependencies, hoping it gets dispatched
- **If this fails:** The issue is definitively in agent dispatch/connection, not ticket state

### Deployment Decision
Docker Compose local deployment. Backend on port 8800. Qdrant on port 6333 (internal only). Frontend served as static files by FastAPI in production.

## Upcoming Plan
Phase 1 — core ingestion pipeline. If fresh scaffolding ticket succeeds, proceed with SQLite schema → text extraction → Qdrant integration → API endpoints → agent loop.

## Completed Work Log
No work completed yet. (Cycle 14)

<!-- PO_SECTION_END -->
