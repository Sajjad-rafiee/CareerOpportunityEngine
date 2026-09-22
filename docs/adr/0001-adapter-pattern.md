# 1. Adapter pattern for external sources

## Context

Job/opportunity data comes from different APIs (Greenhouse, Lever, university
sites), each with its own response shape and quirks.

## Decision

Every source gets one file under `app/adapters/` whose only job is to fetch
raw data and normalize it into `OpportunityIngest`. No business logic, no
persistence, no embedding - just fetch and shape.

## Consequences

Adding a second source means adding one file that returns the same shape;
nothing else in the codebase needs to change. The cost is an extra
translation step even for sources whose data already looks similar.
