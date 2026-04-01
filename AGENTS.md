# Project: TCM Herb Encyclopedia (herb-web)

## Build & Run

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
- Docker: `docker compose up --build`

## Verification

- Frontend build: `cd frontend && npm run build`
- Backend syntax check: `cd backend && python -m py_compile app/main.py`
- Backend tests: `cd backend && source .venv/bin/activate && python -m pytest tests/ -v`
- API docs: http://localhost:8000/docs

## Test Setup

- Virtual env: `backend/.venv/` (activate with `source backend/.venv/bin/activate`)
- Test database: `herbdb_test` on localhost PostgreSQL
- Test config: `backend/pyproject.toml` (pytest-asyncio in auto mode, session-scoped event loop)
- Tests use savepoint-based transaction rollback for isolation

## Key Conventions

- Backend: FastAPI + async SQLAlchemy, Pydantic v2 schemas
- Frontend: Vue 3 `<script setup>`, Element Plus, Pinia stores, Axios API layer
- All UI text is in Chinese
- Green theme (#2e7d32) throughout
- TCM categories are predefined constants (not free text)

## Git Commit Rules

- Follow Conventional Commits format (see `.gitmessage` template)
- Do NOT include "Generated with Devin" or Co-Authored-By Devin lines in commit messages
