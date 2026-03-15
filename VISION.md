# My Note — Vision

<!-- USER_SECTION_START -->
## Goals
- Build a **Knowledge Agent**: a local-first, long-running agent that accumulates understanding of project materials over time
- Feed it documents, code, URLs, meeting notes — it reads, connects, and remembers
- Most valuable output: **gap detection** — identifying what's missing, what conflicts, and what changed
- Persistent, evolving understanding of specific projects — not a search engine or chatbot

## Scope

### In Scope
- **Ingestion pipeline**: PDF, Word, URL, code, plain text → text extraction → chunking → vector indexing (Qdrant)
- **Analysis loop** (OBSERVE → THINK → ACT → RECORD): Sonnet for observation, Opus with extended thinking for deep analysis
- **Structured memory** (SQLite): entities, relations, findings (risks, gaps, conflicts, insights)
- **Vector search** (Qdrant): semantic search over document chunks
- **Query handler**: combined Qdrant + SQLite retrieval, LLM synthesis with source citations
- **Skill system**: SKILL.md files (same format as PO Agent), crystallization every 5 documents, user-approved
- **Dashboard** (React): ingest panel, memory view, chat panel, skills panel
- **FastAPI backend** on port 8800: project CRUD, ingest, findings, entities, query, chat, skills
- **Docker Compose**: agent + Qdrant, local deployment
- **Reliability**: asyncio long-running process, watchdog, exponential backoff API retry

### Out of Scope
- Cloud deployment (local-first only)
- Real-time collaboration / multi-user
- Non-Anthropic LLM backends (initially)

### Execution Phases
1. **Phase 1 — Ingestion pipeline**: SQLite schema, text extraction, Qdrant setup, POST /ingest, analysis loop, basic query
2. **Phase 2 — Memory & retrieval**: structured extraction, combined query, gap detection, chat history + citations
3. **Phase 3 — Dashboard**: ingest panel, memory view tabs, chat panel, document list
4. **Phase 4 — Skills & evolution**: skill loading, crystallization, skills panel, multi-project UI
<!-- USER_SECTION_END -->
