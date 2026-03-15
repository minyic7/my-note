from __future__ import annotations

import aiosqlite
import httpx
from fastapi import APIRouter

from my_note.config import settings

router = APIRouter(prefix="/api")


async def _check_qdrant() -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{settings.qdrant_url}/healthz")
            return resp.status_code == 200
    except Exception:
        return False


async def _check_sqlite() -> bool:
    db_path = f"{settings.data_dir}/my_note.db"
    try:
        async with aiosqlite.connect(db_path) as db:
            await db.execute("SELECT 1")
        return True
    except Exception:
        return False


def _check_agent_running() -> bool:
    """Check if the KnowledgeAgent background task is alive."""
    from my_note.main import _agent_task

    if _agent_task is None:
        return False
    return not _agent_task.done()


@router.get("/health")
async def health():
    qdrant = await _check_qdrant()
    sqlite = await _check_sqlite()
    agent_running = _check_agent_running()

    all_ok = qdrant and sqlite
    status = "ok" if all_ok else "degraded"

    return {
        "status": status,
        "qdrant": qdrant,
        "sqlite": sqlite,
        "agent_running": agent_running,
    }
