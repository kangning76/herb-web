# TCM Herb Encyclopedia Web System — Specification

## 1. Overview

A web-based system for managing, browsing, searching, and visualizing Traditional
Chinese Medicine (TCM) herbs. The system provides a public-facing herb catalog with
keyword search and visual analytics, and an authenticated management interface for
data entry and editing.

### Tech Stack

| Layer         | Technology                                          |
| ------------- | --------------------------------------------------- |
| Backend       | Python 3.11+, FastAPI, SQLAlchemy (async), Alembic  |
| Frontend      | Vue 3 (Composition API), Vite, Vue Router, Pinia, Axios |
| UI Library    | Element Plus                                        |
| Visualization | ECharts (via vue-echarts)                           |
| Database      | PostgreSQL 15+ with pg_trgm extension               |
| Auth          | JWT (localStorage), access + refresh tokens         |
| Image Storage | Local filesystem (served via FastAPI static files)  |

---

## 2. Data Model

### 2.1 `herbs` Table

| Column       | Type                        | Description                            |
| ------------ | --------------------------- | -------------------------------------- |
| `id`         | SERIAL PK                   | Auto-increment primary key             |
| `name_cn`    | VARCHAR(100), NOT NULL, UQ  | Chinese name (e.g. 黄芪)              |
| `name_pinyin`| VARCHAR(200)                | Pinyin romanization (e.g. Huang Qi)    |
| `category`   | VARCHAR(50), NOT NULL       | TCM category (e.g. 补气药)            |
| `nature`     | VARCHAR(20)                 | Thermal nature (寒/热/温/凉/平)        |
| `flavor`     | TEXT[]                      | Flavor(s) as PG array (甘/苦/辛/酸/咸) |
| `efficacy`   | TEXT                        | Therapeutic effects description        |
| `image_url`  | VARCHAR(500)                | Relative path to uploaded image        |
| `created_at` | TIMESTAMP                   | Auto-set on creation                   |
| `updated_at` | TIMESTAMP                   | Auto-set on update                     |

### 2.2 `users` Table

| Column           | Type                        | Description              |
| ---------------- | --------------------------- | ------------------------ |
| `id`             | SERIAL PK                   | Auto-increment primary key |
| `username`       | VARCHAR(50), UNIQUE, NOT NULL | Login username           |
| `hashed_password`| VARCHAR(255), NOT NULL      | bcrypt-hashed password   |
| `created_at`     | TIMESTAMP                   | Auto-set on creation     |

### 2.3 Search Index

- PostgreSQL `pg_trgm` extension with GIN index on `name_cn`, `name_pinyin`,
  `category`, and `efficacy` columns.
- Search uses `ILIKE` with trigram similarity for Chinese + pinyin matching.

---

## 3. API Design (FastAPI REST)

Base URL: `/api/v1`

### 3.1 Public Endpoints (No Auth Required)

| Method | Path                          | Description                             |
| ------ | ----------------------------- | --------------------------------------- |
| GET    | `/herbs`                      | List herbs (paginated, filterable, searchable) |
| GET    | `/herbs/{id}`                 | Get single herb detail                  |
| GET    | `/herbs/categories`           | List all distinct categories            |
| GET    | `/stats/overview`             | Total herbs, total categories, latest date |
| GET    | `/stats/category-distribution`| Herb count grouped by category          |
| GET    | `/stats/nature-distribution`  | Herb count grouped by thermal nature    |
| GET    | `/stats/flavor-distribution`  | Herb count grouped by flavor            |

**Query parameters for `GET /herbs`:**
- `page` (int, default 1)
- `page_size` (int, default 20, max 100)
- `category` (string, filter by category)
- `nature` (string, filter by nature)
- `q` (string, keyword search across text fields)
- `sort_by` (string: `name_cn` | `created_at`, default `created_at`)
- `order` (string: `asc` | `desc`, default `desc`)

### 3.2 Auth Endpoints

| Method | Path             | Description                          |
| ------ | ---------------- | ------------------------------------ |
| POST   | `/auth/login`    | Login, returns JWT access + refresh  |
| POST   | `/auth/refresh`  | Refresh access token                 |
| POST   | `/auth/logout`   | Logout (client-side token removal)   |
| GET    | `/auth/me`       | Get current user info                |

### 3.3 Protected Endpoints (Login Required)

| Method | Path                   | Description                          |
| ------ | ---------------------- | ------------------------------------ |
| POST   | `/herbs`               | Create new herb record               |
| PUT    | `/herbs/{id}`          | Update existing herb                 |
| DELETE | `/herbs/{id}`          | Delete herb                          |
| POST   | `/herbs/{id}/image`    | Upload herb image (multipart)        |
| POST   | `/herbs/import`        | Batch import herbs from CSV          |

---

## 4. Frontend Architecture (Vue 3 SPA)

### 4.1 Pages / Routes

| Route                    | Page          | Auth? | Description                              |
| ------------------------ | ------------- | ----- | ---------------------------------------- |
| `/`                      | Home          | No    | Search bar, featured herbs, quick stats  |
| `/herbs`                 | Herb List     | No    | Card grid with filters + keyword search  |
| `/herbs/:id`             | Herb Detail   | No    | Full herb info with image + tags         |
| `/visualization`         | Dashboard     | No    | 3 charts + overview stat cards           |
| `/login`                 | Login         | No    | Login form                               |
| `/admin/herbs`           | Herb Mgmt     | Yes   | Table with create/edit/delete actions    |
| `/admin/herbs/new`       | Add Herb      | Yes   | Form with image upload                   |
| `/admin/herbs/:id/edit`  | Edit Herb     | Yes   | Pre-filled edit form                     |
| `/admin/herbs/import`    | CSV Import    | Yes   | CSV upload with preview + validation     |

### 4.2 Visualization Dashboard

3 charts on the `/visualization` page:

1. **Category Distribution** — Pie chart (herb count per TCM category)
2. **Thermal Nature Distribution** — Bar chart (寒/热/温/凉/平)
3. **Flavor Profile** — Radar chart (甘/苦/辛/酸/咸)

Plus overview stat cards: total herbs, total categories, latest added date.

### 4.3 Category Dropdown

Admin herb form uses a **dropdown with predefined TCM categories** to ensure
consistent data. Standard categories include:

解表药, 清热药, 泻下药, 祛风湿药, 化湿药, 利水渗湿药, 温里药, 理气药,
消食药, 驱虫药, 止血药, 活血化瘀药, 化痰止咳平喘药, 安神药, 平肝息风药,
开窍药, 补气药, 补血药, 补阴药, 补阳药, 收涩药, 涌吐药, 外用药

---

## 5. Authentication Flow

1. User navigates to `/login` and enters username + password.
2. Frontend POSTs to `/api/v1/auth/login`; backend returns JWT access token
   (30 min expiry) + refresh token (7 day expiry).
3. Frontend stores tokens in `localStorage`; Axios interceptor attaches
   `Authorization: Bearer <token>` on protected requests.
4. On 401 response, interceptor attempts refresh; if refresh fails, redirects
   to login.
5. Vue Router navigation guards check for valid token on admin routes.
6. A seed command (`python -m app.seed_admin`) creates the initial admin user.

---

## 6. Image Handling

- Upload endpoint accepts `multipart/form-data`, single image file.
- Accepted formats: JPEG, PNG, WebP. Max size: 5 MB.
- Saved to `./uploads/herbs/{herb_id}_{timestamp}.{ext}`.
- `image_url` stores relative path (e.g. `/uploads/herbs/42_1711900000.jpg`).
- FastAPI serves `/uploads` as static files.
- Frontend shows placeholder if no image uploaded.

---

## 7. Batch Import (CSV)

- CSV format with columns: `name_cn, name_pinyin, category, nature, flavor, efficacy`
- `flavor` column uses `|` separator for multiple values (e.g. `甘|苦`)
- Admin uploads CSV via `/admin/herbs/import` page.
- Frontend previews parsed data in a table before confirming import.
- Backend validates each row; returns success count + error details.

---

## 8. Non-Functional Requirements

- **Performance**: API responses < 200ms; max 100 items per page.
- **Security**: bcrypt passwords; short-lived JWT; CORS restricted; parameterized
  queries; file upload validated by MIME type + size.
- **Responsive**: Desktop (1280px+), tablet (768px+), mobile (375px+).
- **API Docs**: Auto-generated Swagger UI at `/docs`.

---

## 9. Deployment

### Docker Compose (2 services)

- **db**: PostgreSQL 15 with pg_trgm, persistent volume.
- **backend**: Python 3.11 slim, FastAPI + uvicorn, serves Vue `dist/` as
  static files.

### Environment Variables

| Variable         | Example                                          |
| ---------------- | ------------------------------------------------ |
| `DATABASE_URL`   | `postgresql+asyncpg://user:pass@db:5432/herbdb`  |
| `JWT_SECRET`     | (random 64-char string)                          |
| `UPLOAD_DIR`     | `./uploads`                                      |
| `ADMIN_USERNAME` | `admin`                                          |
| `ADMIN_PASSWORD` | (strong password)                                |

---

## 10. Versioning

The project follows [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

### Single Source of Truth

The root `VERSION` file contains the plain version string (e.g. `0.1.0`).
All other locations read from or must stay in sync with this file:

| Location                       | How it uses the version                          |
| ------------------------------ | ------------------------------------------------ |
| `VERSION`                      | **Source of truth** — plain text, one line        |
| `backend/app/main.py`          | Reads `VERSION` at import time → FastAPI & `/docs` |
| `frontend/package.json`        | `"version"` field — update manually on release   |

### Release Workflow

1. Update `VERSION` to the new version string
2. Update `frontend/package.json` `"version"` to match
3. Add a section to `CHANGELOG.md` under the new version
4. Commit: `chore: release v<version>`
5. Tag: `git tag v<version>`

### Version Bumping Rules

| Change type                        | Bump    | Example            |
| ---------------------------------- | ------- | ------------------ |
| Breaking API / DB schema changes   | MAJOR   | 0.x → 1.0.0       |
| New features, non-breaking         | MINOR   | 0.1.0 → 0.2.0     |
| Bug fixes, minor improvements      | PATCH   | 0.1.0 → 0.1.1     |

---

## 11. Smart Herb Recommendation (智能推荐)

### 11.1 Overview

A recommendation engine that suggests similar herbs based on four dimensions:
category, thermal nature, flavor profile, and efficacy keywords. The system
provides two entry points: an automatic "similar herbs" section on the detail
page, and a standalone exploration page accessible from the navbar.

### 11.2 Similarity Algorithm

Python-side weighted scoring. For a given target herb (or user-selected
criteria), compute a 0–100 similarity score against every other herb:

| Dimension          | Weight | Scoring Method                                      |
| ------------------ | ------ | --------------------------------------------------- |
| Category (分类)    | 35%    | Exact match → 1.0, else 0.0                        |
| Efficacy (功效)    | 25%    | Jaccard similarity on keyword set (split on punctuation) |
| Nature (药性)      | 20%    | Exact match → 1.0, else 0.0                        |
| Flavor (药味)      | 20%    | Jaccard similarity on flavor arrays                 |

Only herbs with score > 0 are returned. Results sorted by score descending.

### 11.3 Match Reason Tags

Each recommendation includes human-readable labels explaining why it matched:

- `"同分类：补气药"` — same category
- `"同药性：温"` — same thermal nature
- `"共同药味：甘、苦"` — shared flavors
- `"相似功效：补气、升阳"` — overlapping efficacy keywords

### 11.4 API Endpoints

| Method | Path                                    | Auth? | Description                              |
| ------ | --------------------------------------- | ----- | ---------------------------------------- |
| GET    | `/herbs/{id}/recommendations`           | No    | Similar herbs for a given herb           |
| GET    | `/herbs/recommendations/explore`        | No    | Explore herbs by user-selected criteria  |

**Query parameters for `GET /herbs/{id}/recommendations`:**
- `limit` (int, default 6, max 20)

**Query parameters for `GET /herbs/recommendations/explore`:**
- `category` (string, optional)
- `nature` (string, optional)
- `flavor` (list[string], optional, repeated param)
- `efficacy_keywords` (string, optional, space-separated)
- `limit` (int, default 12, max 50)

### 11.5 Response Schema

```json
{
  "items": [
    {
      "herb": { /* HerbResponse */ },
      "similarity_score": 85.0,
      "match_reasons": [
        { "dimension": "category", "label": "同分类：补气药" },
        { "dimension": "nature", "label": "同药性：温" }
      ]
    }
  ],
  "total": 5
}
```

### 11.6 Frontend Pages

| Route               | Page             | Description                                          |
| -------------------- | ---------------- | ---------------------------------------------------- |
| `/herbs/:id`         | Herb Detail      | "相似药材推荐" section at bottom (4–6 cards)         |
| `/recommendations`   | Smart Recommend  | Filter panel + result grid with match reason tags    |

---

## 12. Deferred to v2

- Meridians (归经) field
- English name (name_en) field
- Usage/dosage (用法用量) field
- Aliases (别名) field
- Source/origin (来源) field
- Contraindications (禁忌) field
- Image thumbnails
- nginx reverse proxy
- Excel import support
