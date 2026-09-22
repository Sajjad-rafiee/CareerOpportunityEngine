# CareerGraphAI

![CI](https://github.com/Sajjad-rafiee/CareerGraphAI/actions/workflows/ci.yml/badge.svg)

An AI-powered platform that aggregates job and academic opportunities from multiple external sources, normalizes them into a single internal model, and (in later iterations) uses embeddings and LLMs to match them against a user's profile and determine eligibility.

## Features

- FastAPI backend with a health-check endpoint, backed by Postgres via `docker-compose`.
- A `Greenhouse` job board adapter that fetches real postings and normalizes them into an internal schema, with automatic retry on transient network/server errors.
- SQLAlchemy models and Alembic migrations for persisting opportunities, with an idempotent loader that finds-or-creates the parent organization before inserting or updating each record.
- `GET /opportunities` (paginated) and `GET /opportunities/search` for semantic search: query text is embedded locally (`sentence-transformers/all-MiniLM-L6-v2`, no API key or network call needed at query time) and matched against stored embeddings with pgvector cosine distance, so a search finds relevant postings even with no shared words.
- Structured eligibility extraction with an LLM (Gemini): visa sponsorship, German language requirement, experience level, and remote-friendliness are inferred from each posting's raw text into their own `Eligibility` record, constrained to a Pydantic schema so the model can't return malformed output.
- Centralized, configurable logging (`LOG_LEVEL` env var) instead of ad-hoc `print` calls.
- Unit tests for business logic, a separate opt-in integration suite for live external calls, linting (`ruff`) and static type checking (`mypy`), all enforced in CI.

## Architecture

Each folder under `app/` answers one specific question:

| Folder | Question it answers |
|---|---|
| `app/adapters/` | Where does raw data come from? (one file per external source, no business logic) |
| `app/schemas/` | What shape is the data? (Pydantic models, source-independent) |
| `app/models/` | How is the data stored? (SQLAlchemy ORM models) |
| `app/db/` | Where and how is it persisted? (engine/session setup, Alembic migrations) |
| `app/services/` | What logic runs on this data? (querying, embeddings, matching, eligibility — the core of the project) |
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

## Persisting to Postgres

```bash
uv run alembic upgrade head              # create/update tables
uv run python -m scripts.load_greenhouse_to_db
```

Reads `data/opportunities_greenhouse.json` and upserts it into Postgres, creating each organization on first sight and updating existing opportunities on repeat runs instead of duplicating them. Each record's `title + description` is also embedded and stored alongside it, ready for semantic search. Eligibility is extracted with an LLM once per opportunity (skipped on repeat runs if it already exists, since unlike embeddings this calls a paid API) — requires `GEMINI_API_KEY` in `.env` (free key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)).

## Semantic search

```bash
curl "http://127.0.0.1:8000/opportunities/search?q=money+laundering+compliance&limit=5"
```

Returns the closest opportunities by meaning, each with a `score` (cosine similarity, higher is closer) — including postings that share no words at all with the query.

## Testing

```bash
uv run pytest                 # fast unit tests only
uv run pytest -m integration  # also hits real external APIs
uv run ruff check .           # lint
uv run mypy app                # static type checking
```
