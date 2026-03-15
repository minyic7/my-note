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
Post-compaction — cycle 34

## Completed Work Log

**Infrastructure & Configuration**
- Scaffolded full repo structure with FastAPI, Pydantic Settings (MY_NOTE_ prefix), Docker Compose (app + Qdrant), and multi-stage Dockerfile; Qdrant intentionally has no external port exposure
- Health endpoint returns `degraded` (never 500) when dependencies are down — deliberate UX decision for Docker healthcheck compatibility
- Reviewer flagged missing config defaults; Pydantic would fail silently on incomplete `.env` without them

**Embeddings & Vector Storage**
- Chose `voyageai` SDK for batch embedding (voyage-3, 1024-dim cosine collections per project); batch size hardcoded at 128 — noted as tech debt
- Token counting uses whitespace splitting, not tiktoken — accepted as v1 tradeoff
- Two review rounds needed; second round surfaced bare `except Exception` masking API errors and missing `QDRANT_URL` validation at startup

**Frontend Scaffolding**
- React 19 + Vite + Tailwind CSS 4 + pnpm; Tailwind 4 dropped `tailwind.config.ts` — reviewer flagged this as potentially misconfigured but defaults proved sufficient
- Router setup was minimal in PR; reviewer noted `BrowserRouter`/`Routes` absent from `App.tsx` despite ticket requiring them — approved as minor
- FastAPI serves production build as static files; Vite proxies to `:8800` in dev

**Project Dashboard UI**
- Built project list, detail, and document upload UI (file, URL, raw text ingestion paths)
- No file size validation on upload — could cause silent timeouts with large files; flagged but not blocking
- Document list has no pagination — potential performance issue at scale, deferred


<!-- PO_SECTION_END -->
