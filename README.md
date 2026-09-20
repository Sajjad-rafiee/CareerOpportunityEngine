# CareerGraphAI

![CI](https://github.com/Sajjad-rafiee/CareerGraphAI/actions/workflows/ci.yml/badge.svg)

An AI-powered platform that aggregates job and academic opportunities from multiple external sources, normalizes them into a single internal model, and (in later iterations) uses embeddings and LLMs to match them against a user's profile and determine eligibility.

## Features

- FastAPI backend with a health-check endpoint, backed by Postgres via `docker-compose`.
- A `Greenhouse` job board adapter that fetches real postings and normalizes them into an internal schema, with automatic retry on transient network/server errors.
- Centralized, configurable logging (`LOG_LEVEL` env var) instead of ad-hoc `print` calls.
- Unit tests for business logic, a separate opt-in integration suite for live external calls, linting (`ruff`) and static type checking (`mypy`), all enforced in CI.

## Roadmap

- [ ] Persist opportunities in Postgres via SQLAlchemy models and Alembic migrations.
- [ ] Serve stored opportunities through a paginated REST endpoint.
- [ ] Semantic search over opportunities using `pgvector` embeddings.
- [ ] Structured extraction of eligibility criteria from raw postings using an LLM.
- [ ] A second data source behind a shared adapter contract.

## Architecture

Each folder under `app/` answers one specific question:

| Folder | Question it answers |
|---|---|
| `app/adapters/` | Where does raw data come from? (one file per external source, no business logic) |
| `app/schemas/` | What shape is the data? (Pydantic models, source-independent) |
| `app/models/` | How is the data stored? (SQLAlchemy ORM models, once the database layer exists) |
| `app/services/` | What logic runs on this data? (matching, eligibility — the core of the project) |
| `app/api/` | How does the outside world reach the system? (thin FastAPI routers) |
| `app/core/` | Shared configuration, logging, error handling |
| `app/jobs/` | Scheduled/recurring tasks |
| `scripts/` | One-off scripts (not part of the running app) |

## Running locally

```bash
uv sync
cp .env.example .env   # fill in Postgres credentials
docker compose up -d   # starts Postgres
uv run uvicorn app.main:app --reload
```

## Fetching real data

```bash
uv run python -m scripts.fetch_greenhouse
```

Writes normalized opportunities from N26's public Greenhouse job board to `data/opportunities_greenhouse.json`.

## Testing

```bash
uv run pytest                 # fast unit tests only
uv run pytest -m integration  # also hits real external APIs
uv run ruff check .           # lint
uv run mypy app                # static type checking
```
