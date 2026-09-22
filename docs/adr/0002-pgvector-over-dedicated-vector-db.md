# 2. pgvector instead of a dedicated vector database

## Context

Semantic search needs nearest-neighbor lookup over embeddings. Options
considered: a dedicated vector store (Pinecone, Weaviate, Qdrant) or a
Postgres extension.

## Decision

Use `pgvector` inside the existing Postgres instance.

## Consequences

One database, one connection, one backup story - opportunities and their
embeddings stay in the same transaction. A dedicated vector store would
scale further and offer more index types (HNSW tuning, hybrid search
built in), but at this data size (tens of thousands of rows, not
billions) that scaling headroom isn't needed, and it would mean running
and syncing a second system. Revisit if the row count or query volume
grows by orders of magnitude.
