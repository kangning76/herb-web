# TCM Herb Encyclopedia (中药百科)

A web-based system for managing, browsing, searching, and visualizing Traditional Chinese Medicine (TCM) herbs.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL
- **Frontend**: Vue 3 (Composition API), Vite, Element Plus, ECharts, Pinia, Axios

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

### Option 1: Docker Compose (recommended)

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`.

Default admin credentials: `admin` / `admin123`

### Option 2: Local Development

**1. Start PostgreSQL** (e.g. via Docker):

```bash
docker run -d --name herbdb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=herbdb -p 5432:5432 postgres:15-alpine
```

**2. Backend**:

```bash
cd backend
cp .env.example .env   # edit as needed
pip install -r requirements.txt
# Enable pg_trgm extension
python -c "
import asyncio, asyncpg
async def main():
    conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/herbdb')
    await conn.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    await conn.close()
asyncio.run(main())
"
# Run migrations or create tables + seed data
python -m app.seed_admin
python -m app.seed_herbs
# Start server
uvicorn app.main:app --reload --port 8000
```

**3. Frontend**:

```bash
cd frontend
npm install
npm run dev
```

Frontend at `http://localhost:5173`, proxies `/api` to backend.

## Project Structure

```
herb-web/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry
│   │   ├── config.py        # Settings
│   │   ├── database.py      # Async SQLAlchemy setup
│   │   ├── models/          # SQLAlchemy models (Herb, User)
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # Route handlers
│   │   ├── services/        # Business logic
│   │   ├── seed_admin.py    # Create admin user
│   │   └── seed_herbs.py    # Seed sample herbs
│   ├── alembic/             # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API layer
│   │   ├── components/      # Reusable Vue components
│   │   ├── views/           # Page views
│   │   ├── stores/          # Pinia stores
│   │   └── router/          # Vue Router
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml
└── SPEC.md                  # Full specification
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive Swagger UI.

## Features

- **Browse**: Card grid with herb images, properties, and pagination
- **Search**: Keyword search across name, pinyin, category, and efficacy
- **Filter**: Filter by category and thermal nature
- **Visualize**: Pie chart (categories), bar chart (nature), radar chart (flavors)
- **Admin**: CRUD management, image upload, CSV batch import
- **Auth**: JWT-based login for admin operations
