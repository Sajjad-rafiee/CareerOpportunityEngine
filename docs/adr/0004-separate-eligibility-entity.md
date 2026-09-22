# 4. Eligibility as its own entity

## Context

Visa sponsorship, language requirements, experience level, and remote
policy aren't in the raw posting data - they're inferred by an LLM from
free text, and could change if we improve the prompt or switch models.

## Decision

Store this as an `Eligibility` row (1:1 with `Opportunity`) instead of
extra columns on `Opportunity` itself.

## Consequences

Re-running extraction with a better prompt only touches `eligibilities`,
never the source-of-truth `Opportunity` row. It also makes the loader's
skip logic explicit: `ensure_eligibility` only calls the paid LLM API when
`opportunity.eligibility is None`, so re-running the loader after an
`Opportunity` update doesn't re-bill unchanged postings.
