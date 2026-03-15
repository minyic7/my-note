## ── Frontend build ──────────────────────────────────────────────
FROM node:22-alpine AS frontend

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY frontend/ .
RUN pnpm build

## ── Backend build ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY backend/pyproject.toml .
RUN uv pip install --system --no-cache -r pyproject.toml

## ── Runtime ────────────────────────────────────────────────────
FROM python:3.12-slim

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

WORKDIR /app
COPY backend/src ./src

# Copy frontend build output so FastAPI can serve it at /
COPY --from=frontend /app/dist ./frontend/dist

ENV PYTHONPATH=/app/src

EXPOSE 8800

CMD ["uvicorn", "my_note.main:app", "--host", "0.0.0.0", "--port", "8800"]
