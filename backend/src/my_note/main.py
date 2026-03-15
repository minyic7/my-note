from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from my_note.config import settings
from my_note.routers.health import router as health_router

# Holds a reference to the KnowledgeAgent background task (if started).
_agent_task: asyncio.Task | None = None  # noqa: FA100


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure data directory exists
    data_dir = Path(settings.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize SQLite knowledge database
    from my_note.services.knowledge_db import KnowledgeDB

    db_path = str(data_dir / "knowledge.db")
    app.state.knowledge_db = await KnowledgeDB.init_db(db_path)

    yield

    # Shutdown: close database
    await app.state.knowledge_db.close()

    # Shutdown: cancel agent task if running
    global _agent_task  # noqa: PLW0603
    if _agent_task is not None and not _agent_task.done():
        _agent_task.cancel()
        _agent_task = None


app = FastAPI(title="my-note", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)

# Mount static files for frontend (must be last)
static_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
