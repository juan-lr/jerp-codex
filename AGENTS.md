# Repository Guidelines

This guide helps contributors work efficiently in this repo. Keep changes focused, small, and well‑described.

## Agent-Specific Instructions
- As an AI agent, respect these rules in this file for any file you touch within this repo tree.
- Keep edits minimal and in‑scope; do not reformat unrelated files.
- Use @agent_notes/cross_session_agent_notes.md to make any notes about this project that may
be helpful across sessions but do not rise to the level of clean documentation
- When faced with a big task, break it down into a until you have a list of small action items
- Be practical above all.
- Take a forward-thinking view.
- Tell it like it is; don't sugar-coat responses.
- Get right to the point.
- If you are not Claude, ignore the CLAUDE.md file - it has all the same info as this file
- Do not waste time reading .bu (backup) or raw data files such as .sql unless specifically told otherwise
- Always prioritize backend needs to fronend needs

## When In Doubt
- Prefer minimal, reversible changes
- Follow existing patterns and structure
- Keep types in sync across lerp/frontend
- Add or update tests alongside changes

## Project Structure & Module Organization
- lerp/ — the backend: Django 5.x, DRF, Postgres + PostGIS
- flerp/ — the frontend: React 19, TypeScript, Vite - set aside for MVP
- infra/ (optional) — Docker/Compose/Terraform
- `README.md` — quick start; update when behavior changes.

## Coding Style & Naming Conventions
- Indentation: 4 spaces. Keep lines ≤ 80 chars.
- Python: follow PEP 8; prefer type hints on public functions.
- Naming: modules `snake_case.py`; classes `PascalCase`; functions/vars `snake_case`.
- Lint/format: `ruff` (lint) and `black` (format). Run `make fmt && make lint` before pushing.

## Testing Guidelines
- Framework: `pytest` and `pytest-django` with coverage via `pytest-cov`.
- Mirror structure: `tests/` path mirrors `src/` (e.g., `src/foo/bar.py` → `tests/foo/test_bar.py`).
- Test names: files `test_*.py`; functions `test_*`; use descriptive docstrings.

## Commit & Pull Request Guidelines
- Commits: use conventional style when possible, e.g., `feat: add CLI init`, `fix: handle empty input`.
- Keep commits atomic; include rationale in the body when non‑obvious.
- PRs: include a clear summary, linked issues (`Closes #123`), and before/after notes or screenshots for user‑visible changes.
- Ensure CI is green and `make lint test` passes.
- Files with ending in `.bu*` are for local reference - not to be committed

## Security & Configuration Tips
- Do not commit secrets. Use environment variables and sample files like `.env.example`.
- Validate and sanitize all external inputs at boundaries.
- Prefer least‑privilege defaults in scripts and services.

## Repo Overview
- monorepo with two submodeuls:
  - lerp/ — Django 5.x, Postgres + PostGIS, DRF
  - flerp/ — React 19, TypeScript, Vite
- infra/ (if present) contains Docker, Compose, Terraform, or migrations for PostGIS

# Goals & Non-Goals
- Goal: High-quality, incremental changes with tests.
- Goal: Keep API contracts stable
- Non-goal: Adding new dependencies unless necessary and approved by codeowner

## Core Principles
- Small, incremental PRs with tests
- Maintain stable API contracts; use versioning and deprecation for breaking changes
- Prefer existing dependencies; add new ones only with clear justification and approval
- Minimal, in-scope edits; do not reformat unrelated files

## Security & Configuration
- Never commit secrets; use env vars and .env.example
- Validate/sanitize all external inputs
- Least-privilege defaults; do not log secrets/JWTs
- CORS: restrict to known origins outside dev

## Standards & Tooling
- Python: PEP 8, type hints on public functions, 4-space indent, ≤80 chars
- Naming: modules/functions/vars snake_case; classes PascalCase
- Backend lint/format: ruff, black; typing: mypy (if configured)
- Frontend lint/format: eslint, prettier; types: tsc
- Run before push: make fmt && make lint && make test
- CI must pass; don’t skip checks
- Pre-commit: pre-commit run -a (if configured)

## Quickstart

### Docker
- docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
- Backend: http://localhost:8000
- Frontend: http://localhost:5173

### Database
- Declared in jerp compose files - does not have its own submodule
- image: postgis/postgis:17-3.5

### Backend
- Env: lerp/.env.dev (DATABASE_URL, SECRET_KEY, DEBUG, etc.)
- Install: pip install -r requirements.dev.txt (or uv equivalent)
- Run: python manage.py runserver 0.0.0.0:8000
- Tests: pytest -q
- Lint/Type: ruff check ., black ., mypy backend (if mypy.ini)
- Common: makemigrations, collectstatic --noinput

### Frontend
- Env: flerp/.env.dev (VITE_API_URL=http://localhost:8000)
- Install: pnpm i (or npm ci/yarn)
- Dev: pnpm dev
- Build: pnpm build
- Lint/Test/Types: pnpm lint, pnpm test, pnpm typecheck

## Architecture

### Backend (Django + DRF + GeoDjango)
- Geo fields with SRID 4326; add GIST indexes for geometry
- Serializers return GeoJSON (RFC 7946) when applicable
- ViewSets + routers; default IsAuthenticated unless explicitly public
- Pagination: PageNumberPagination with count/next/previous/results
- Migrations: one per change; include data migrations when needed
- Performance: select_related/prefetch_related; GIST/GIN indexes

### Frontend (React + TS)
- None

## Data & Geo
- CRS: WGS84 (EPSG:4326) for API I/O
- GeoJSON: Feature/FeatureCollection compliant
- BBox: [minLon, minLat, maxLon, maxLat]
- Large datasets: require bbox/tiling; cap server-side results; simplify geometries if needed

## API Contracts
- JSON only; errors as {"detail": "..."} or DRF defaults
- Pagination: ?page=, ?page_size= (server max)
- Versioning: /api/v1; additive changes preferred; deprecate before removal
- Auth: Bearer tokens or JWT per existing impl; CSRF for session flows only

## Testing

### Backend
- pytest + pytest-django (+ pytest-cov)
- Cover: models/managers, API success/failure/permissions, geometry ser/de
- Use factories if available

### Frontend
- Unit tests for hooks/utils; component tests with Testing Library
- Snapshot tests only for stable presentational components

## Database & Migrations
- Don’t commit local creds
- Spatial index example:
  - migrations.RunSQL("CREATE INDEX CONCURRENTLY idx_table_geom ON table USING GIST (geom)")

## Git Workflow
- Branches: feature/<slug>, fix/<slug>, chore/<slug>, db/<slug> (schema)
- Commits: conventional style (feat:, fix:, chore:, refactor:, test:)
- PRs: small, scoped; include summary, linked issues (Closes #123), UI screenshots (if applicable), migration and testing notes
- Update docs and types with code changes

## Common Tasks
- New model:
  1) Add model (SRID 4326 if geometry)
  2) makemigrations && migrate
  3) Serializer → GeoJSON if geometry
  4) ViewSet + router; require bbox for large lists
  5) Ensure GIST index
  6) Tests: model, ser roundtrip, bbox filter, permissions

- New API endpoint:
  - Serializer, viewset/action, router entry, permissions, tests (200/400/403/404, pagination)

- New frontend page:
  - pages/NewPage.tsx with lazy route; data via typed React Query hook; tests for render/loading/error
