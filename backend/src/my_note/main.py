from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from my_note.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure data directory exists
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown: cleanup resources


app = FastAPI(title="my-note", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Mount static files for frontend (must be last)
static_dir = Path(__file__).parent.parent.parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
