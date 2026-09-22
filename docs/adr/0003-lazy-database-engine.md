# 3. Lazy database engine initialization

## Context

An early version built the SQLAlchemy engine at module import time. This
meant importing `app.db.session` - even from a test that never touches a
real database - required valid Postgres settings. In CI, where `.env`
doesn't exist, this broke unit tests that only use an in-memory SQLite
database.

## Decision

Build the engine inside a `@lru_cache`-wrapped `get_engine()`, called only
when a session is actually created.

## Consequences

Importing the module has no side effects and no environment requirements;
the connection is only attempted when code actually needs the database.
The cache means the engine is still built once per process, not once per
request.
