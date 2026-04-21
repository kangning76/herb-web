# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-04-21

First release of the TCM Herb Encyclopedia.

### Added

- **Backend**: FastAPI REST API with async SQLAlchemy, JWT authentication, image upload, CSV import
- **Frontend**: Vue 3 SPA with Element Plus — herb browsing, search, filtering, detail pages
- **Data Visualization**: category pie chart, nature bar chart, flavor radar chart (ECharts)
- **Admin Panel**: CRUD management, image upload, CSV batch import with preview
- **Auth**: JWT access/refresh tokens, login guard on admin routes
- **Smart Recommendation**: similarity-based herb recommendations by category, nature, flavor, and efficacy
  - Detail page "相似药材推荐" section
  - Standalone `/recommendations` exploration page with multi-criteria filters
  - Python-side weighted scoring algorithm with match reason tags
- **Seed Data**: 100 herbs covering all 23 standard TCM categories
- **Testing**: 64 backend test cases (auth, CRUD, search, import, image, stats, recommendations)
- **Deployment**: Docker Compose setup (PostgreSQL + FastAPI serving Vue dist)
- **Versioning**: `VERSION` file as single source of truth, read by backend and synced to frontend
