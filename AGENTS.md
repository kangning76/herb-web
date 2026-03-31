# Project: TCM Herb Encyclopedia (herb-web)

## Build & Run

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
- Docker: `docker compose up --build`

## Verification

- Frontend build: `cd frontend && npm run build`
- Backend syntax check: `cd backend && python -m py_compile app/main.py`
- API docs: http://localhost:8000/docs

## Key Conventions

- Backend: FastAPI + async SQLAlchemy, Pydantic v2 schemas
- Frontend: Vue 3 `<script setup>`, Element Plus, Pinia stores, Axios API layer
- All UI text is in Chinese
- Green theme (#2e7d32) throughout
- TCM categories are predefined constants (not free text)

## Git Commit Rules

- Follow Conventional Commits format (see `.gitmessage` template)
- Do NOT include "Generated with Devin" or Co-Authored-By Devin lines in commit messages
