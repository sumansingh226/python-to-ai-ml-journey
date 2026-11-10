# Building a Vector Database with PostgreSQL + pgvector

A practical guide to storing embeddings in Postgres, choosing the right vector **dimension**, indexing, and running similarity search.

---

## 1. What is pgvector?

`pgvector` is a PostgreSQL extension that adds:

- A `vector(n)` column type for storing embeddings (arrays of floats)
- Distance operators for similarity search
- Approximate nearest-neighbour (ANN) indexes: **HNSW** and **IVFFlat**
- Extra types: `halfvec` (16-bit floats), `bit` (binary vectors), `sparsevec` (sparse vectors)

You keep your vectors next to your regular relational data, so you can filter, join and transact on them with normal SQL.

---

## 2. Installation

### Option A: Docker (quickest)

```bash
docker run -d --name pgvector \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg17
```

### Option B: Linux (Debian/Ubuntu)

```bash
# Replace 17 with your Postgres major version
sudo apt install postgresql-17-pgvector
```

### Option C: macOS (Homebrew)

```bash
brew install pgvector
```

### Option D: Build from source

```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Option E: Managed Postgres

Most managed providers ship pgvector already: AWS RDS / Aurora, Google Cloud SQL / AlloyDB, Azure Database for PostgreSQL, Supabase, Neon, Timescale, etc. You only need to enable it (next step).

### Enable the extension (once per database)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Check the installed version
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

---

## 3. Understanding Vector Dimensions

The **dimension** is the number of floats in each embedding. It is fixed by the embedding model you use — **the column dimension must match the model's output exactly**, or inserts will fail.

### Common embedding models and their dimensions

| Model | Provider | Dimensions |
|---|---|---|
| `text-embedding-3-small` | OpenAI | 1536 (can be shortened) |
| `text-embedding-3-large` | OpenAI | 3072 (can be shortened) |
| `text-embedding-ada-002` | OpenAI (legacy) | 1536 |
| `embed-english-v3.0` / `embed-multilingual-v3.0` | Cohere | 1024 |
| `all-MiniLM-L6-v2` | Sentence-Transformers | 384 |
| `all-mpnet-base-v2` | Sentence-Transformers | 768 |
| `bge-small-en-v1.5` | BAAI | 384 |
| `bge-base-en-v1.5` | BAAI | 768 |
| `bge-large-en-v1.5` | BAAI | 1024 |
| `nomic-embed-text` | Nomic | 768 |
| CLIP ViT-B/32 (images + text) | OpenAI | 512 |

> Always confirm the dimension in your model's docs, or just embed one test string and check `len(embedding)`.

### pgvector dimension limits

| Type | Max dimensions stored | Max dimensions indexable (HNSW / IVFFlat) |
|---|---|---|
| `vector` | 16,000 | 2,000 |
| `halfvec` | 16,000 | 4,000 |
| `bit` | 64,000 | 64,000 |
| `sparsevec` | 16,000 non-zero elements | 1,000 non-zero elements |

**Key consequence:** a 3072-dim model (e.g. `text-embedding-3-large`) **cannot be indexed as `vector`**. Your options:

1. Store/index it as `halfvec(3072)` (fits under 4,000)
2. Ask the model for fewer dimensions (OpenAI v3 models accept a `dimensions` parameter, e.g. 1024 or 1536)
3. Use an expression index that casts to `halfvec` (see §6)

### Choosing a dimension — trade-offs

| Smaller (384–768) | Larger (1536–3072) |
|---|---|
| Less storage & RAM | More storage & RAM |
| Faster index build & search | Slower |
| Slightly lower retrieval quality | Usually better quality |

**Storage rule of thumb:** `vector(n)` ≈ `4 × n + 8` bytes per row.
- 1M rows × 1536 dims ≈ **6 GB** of raw vectors (plus index, often similar size again)
- Same with `halfvec` ≈ **3 GB**

---

## 4. Create the Table

```sql
CREATE TABLE documents (
    id          BIGSERIAL PRIMARY KEY,
    content     TEXT NOT NULL,
    metadata    JSONB DEFAULT '{}',
    category    TEXT,
    created_at  TIMESTAMPTZ DEFAULT now(),
    embedding   vector(1536)          -- must match your model's output size
);
```

Other type variants:

```sql
embedding  halfvec(3072)     -- half-precision, half the storage
embedding  bit(1024)         -- binary quantized
embedding  sparsevec(30000)  -- sparse (e.g. SPLADE)
```

### Chunked documents (typical RAG layout)

```sql
CREATE TABLE sources (
    id     BIGSERIAL PRIMARY KEY,
    title  TEXT,
    url    TEXT
);

CREATE TABLE chunks (
    id          BIGSERIAL PRIMARY KEY,
    source_id   BIGINT REFERENCES sources(id) ON DELETE CASCADE,
    chunk_index INT,
    content     TEXT NOT NULL,
    embedding   vector(1536)
);
```

### Changing the dimension later

You can't mix dimensions in one column. If you switch models:

```sql
ALTER TABLE documents ADD COLUMN embedding_v2 vector(768);
-- re-embed all rows into embedding_v2, build its index, then:
ALTER TABLE documents DROP COLUMN embedding;
ALTER TABLE documents RENAME COLUMN embedding_v2 TO embedding;
```

---

## 5. Insert Data

Vectors are written as a bracketed list string:

```sql
INSERT INTO documents (content, category, embedding)
VALUES ('Postgres is a relational database', 'db', '[0.012, -0.044, 0.981, ...]');
```

Bulk loading is much faster with `COPY`:

```sql
COPY documents (content, embedding) FROM STDIN WITH (FORMAT csv);
```

> Tip: for large loads, **insert data first, then build the index**. It's far faster than indexing row by row.

---

## 6. Indexing

Without an index, pgvector does an exact (brute-force) scan — perfectly fine up to tens of thousands of rows. Beyond that, add an ANN index.

### Pick the operator class that matches your distance metric

| Distance | Operator | `vector` op class | `halfvec` op class |
|---|---|---|---|
| L2 (Euclidean) | `<->` | `vector_l2_ops` | `halfvec_l2_ops` |
| Cosine distance | `<=>` | `vector_cosine_ops` | `halfvec_cosine_ops` |
| Negative inner product | `<#>` | `vector_ip_ops` | `halfvec_ip_ops` |
| L1 (Manhattan) | `<+>` | `vector_l1_ops` | `halfvec_l1_ops` |
| Hamming (bit) | `<~>` | `bit_hamming_ops` | — |
| Jaccard (bit) | `<%>` | `bit_jaccard_ops` | — |

> **Your query must use the same operator as the index**, otherwise the index won't be used.
> For normalized embeddings (OpenAI, most sentence-transformers), cosine and inner product give the same ranking; inner product is slightly faster.

### HNSW (recommended default)

Better speed/recall trade-off, no training step, can be built on an empty table.

```sql
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

| Parameter | Default | Meaning |
|---|---|---|
| `m` | 16 | Connections per node. Higher = better recall, more memory |
| `ef_construction` | 64 | Candidate list size at build. Higher = better index, slower build |

Query-time tuning:

```sql
SET hnsw.ef_search = 100;   -- default 40; higher = better recall, slower
```

### IVFFlat

Faster to build and smaller, but lower recall; **build after loading data** (it clusters existing rows).

```sql
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 1000);
```

- `lists`: ≈ `rows / 1000` up to 1M rows, ≈ `sqrt(rows)` above 1M
- Query-time: `SET ivfflat.probes = 10;` (start ≈ `sqrt(lists)`)

### HNSW vs IVFFlat at a glance

| | HNSW | IVFFlat |
|---|---|---|
| Recall / speed | Better | Good |
| Build time | Slower | Faster |
| Memory | Higher | Lower |
| Needs data before build | No | Yes |
| Good default? | ✅ | For huge, mostly static data |

### Indexing > 2,000 dimensions (half-precision expression index)

```sql
CREATE TABLE docs_large (
    id        BIGSERIAL PRIMARY KEY,
    content   TEXT,
    embedding vector(3072)
);

CREATE INDEX ON docs_large
USING hnsw ((embedding::halfvec(3072)) halfvec_cosine_ops);

-- Query must use the same cast
SELECT id, content
FROM docs_large
ORDER BY embedding::halfvec(3072) <=> '[...]'::halfvec(3072)
LIMIT 5;
```

### Speeding up index builds

```sql
SET maintenance_work_mem = '4GB';            -- graph should fit in memory
SET max_parallel_maintenance_workers = 7;    -- plus the leader process
```

---

## 7. Querying

### Nearest neighbours

```sql
SELECT id, content, embedding <=> '[0.01, -0.02, ...]' AS distance
FROM documents
ORDER BY embedding <=> '[0.01, -0.02, ...]'
LIMIT 5;
```

### Cosine similarity score (0–1 for normalized vectors)

```sql
SELECT id, content, 1 - (embedding <=> $1) AS similarity
FROM documents
ORDER BY embedding <=> $1
LIMIT 5;
```

### With a metadata filter

```sql
SELECT id, content
FROM documents
WHERE category = 'db'
ORDER BY embedding <=> $1
LIMIT 5;
```

Filtering + ANN can return fewer rows than `LIMIT`, because the index fetches candidates before the filter is applied. Fixes:

```sql
-- pgvector 0.8+: keep scanning until enough rows match
SET hnsw.iterative_scan = relaxed_order;     -- or strict_order
SET ivfflat.iterative_scan = relaxed_order;

-- Or index the filter column / use a partial index
CREATE INDEX ON documents (category);
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
    WHERE category = 'db';
```

### Similarity threshold

```sql
SELECT id, content
FROM documents
WHERE embedding <=> $1 < 0.3          -- cosine distance under 0.3
ORDER BY embedding <=> $1
LIMIT 10;
```

### Hybrid search (vector + full-text, using Reciprocal Rank Fusion)

```sql
ALTER TABLE documents
  ADD COLUMN tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
CREATE INDEX ON documents USING gin (tsv);

WITH semantic AS (
    SELECT id, RANK() OVER (ORDER BY embedding <=> $1) AS rank
    FROM documents
    ORDER BY embedding <=> $1
    LIMIT 20
),
keyword AS (
    SELECT id, RANK() OVER (ORDER BY ts_rank_cd(tsv, q) DESC) AS rank
    FROM documents, plainto_tsquery('english', $2) q
    WHERE tsv @@ q
    ORDER BY ts_rank_cd(tsv, q) DESC
    LIMIT 20
)
SELECT d.id, d.content,
       COALESCE(1.0 / (60 + s.rank), 0) + COALESCE(1.0 / (60 + k.rank), 0) AS score
FROM semantic s
FULL OUTER JOIN keyword k USING (id)
JOIN documents d USING (id)
ORDER BY score DESC
LIMIT 5;
```

### Useful vector functions

```sql
SELECT vector_dims(embedding)  FROM documents LIMIT 1;  -- dimension check
SELECT vector_norm(embedding)  FROM documents LIMIT 1;  -- L2 norm
SELECT AVG(embedding)          FROM documents;          -- centroid
SELECT l2_normalize(embedding) FROM documents LIMIT 1;  -- normalize
SELECT subvector(embedding, 1, 256) FROM documents;     -- first 256 dims
```

---

## 8. End-to-End Python Example

```bash
pip install psycopg[binary] pgvector openai numpy
```

```python
import os
import numpy as np
import psycopg
from pgvector.psycopg import register_vector
from openai import OpenAI

MODEL = "text-embedding-3-small"
DIM = 1536

client = OpenAI()  # uses OPENAI_API_KEY

def embed(texts: list[str]) -> list[np.ndarray]:
    resp = client.embeddings.create(model=MODEL, input=texts)
    return [np.array(d.embedding, dtype=np.float32) for d in resp.data]

conn = psycopg.connect(
    "postgresql://postgres:postgres@localhost:5432/postgres",
    autocommit=True,
)
conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
register_vector(conn)

conn.execute(f"""
    CREATE TABLE IF NOT EXISTS documents (
        id        BIGSERIAL PRIMARY KEY,
        content   TEXT NOT NULL,
        embedding vector({DIM})
    )
""")

# Insert
docs = [
    "PostgreSQL is an open-source relational database.",
    "pgvector adds vector similarity search to Postgres.",
    "Bananas are a good source of potassium.",
]
with conn.cursor() as cur:
    for text, emb in zip(docs, embed(docs)):
        cur.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (text, emb),
        )

# Index (after loading)
conn.execute("""
    CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING hnsw (embedding vector_cosine_ops)
""")

# Search
query_vec = embed(["How do I do semantic search in Postgres?"])[0]
rows = conn.execute(
    """
    SELECT content, 1 - (embedding <=> %s) AS similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 3
    """,
    (query_vec, query_vec),
).fetchall()

for content, sim in rows:
    print(f"{sim:.3f}  {content}")
```

### Local (free) embeddings instead of OpenAI

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")   # 384 dims → use vector(384)
embeddings = model.encode(docs, normalize_embeddings=True)
```

### Node.js equivalent (short)

```bash
npm install pg pgvector
```

```js
import pg from 'pg';
import pgvector from 'pgvector/pg';

const client = new pg.Client({ connectionString: process.env.DATABASE_URL });
await client.connect();
await pgvector.registerTypes(client);

const embedding = [/* ...1536 floats... */];
await client.query(
  'INSERT INTO documents (content, embedding) VALUES ($1, $2)',
  ['hello', pgvector.toSql(embedding)]
);

const { rows } = await client.query(
  'SELECT content FROM documents ORDER BY embedding <=> $1 LIMIT 5',
  [pgvector.toSql(embedding)]
);
```

---

## 9. Performance & Production Checklist

- [ ] **Column dimension matches the model** exactly
- [ ] **Same distance operator** in index and query (`<=>` ↔ `*_cosine_ops`)
- [ ] Load data **before** building IVFFlat; prefer bulk load then index for HNSW too
- [ ] `maintenance_work_mem` large enough for index builds
- [ ] Tune `hnsw.ef_search` / `ivfflat.probes` for your recall target
- [ ] Use `halfvec` to halve storage, or for models > 2,000 dims
- [ ] Enable `iterative_scan` (0.8+) when combining filters with ANN
- [ ] Verify the index is used:
  ```sql
  EXPLAIN ANALYZE
  SELECT id FROM documents ORDER BY embedding <=> '[...]' LIMIT 5;
  -- look for "Index Scan using ... hnsw"
  ```
- [ ] Measure recall: compare ANN results vs exact results on a sample
  ```sql
  BEGIN;
  SET LOCAL enable_indexscan = off;   -- forces exact search
  SELECT id FROM documents ORDER BY embedding <=> '[...]' LIMIT 10;
  COMMIT;
  ```
- [ ] `VACUUM` regularly; after heavy deletes/updates consider `REINDEX INDEX CONCURRENTLY`
- [ ] Keep the HNSW index in RAM (`shared_buffers` / instance memory) for best latency

---

## 10. Troubleshooting

| Error / symptom | Cause | Fix |
|---|---|---|
| `expected 1536 dimensions, not 768` | Embedding size ≠ column size | Match the column to the model |
| `column cannot have more than 2000 dimensions for hnsw index` | `vector` > 2,000 dims | Use `halfvec` or reduce dimensions |
| Query is slow, index ignored | Operator mismatch, or no `ORDER BY ... LIMIT` | Use matching operator; always `ORDER BY dist LIMIT k` |
| Fewer rows than `LIMIT` with `WHERE` | Filter applied after ANN candidates | `SET hnsw.iterative_scan = relaxed_order` or raise `ef_search` |
| Index build very slow | Low `maintenance_work_mem` | Increase it; add parallel workers |
| `type "vector" does not exist` | Extension not enabled in this DB | `CREATE EXTENSION vector;` |

---

## 11. Quick Reference

```sql
-- Setup
CREATE EXTENSION IF NOT EXISTS vector;

-- Table
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(1536));

-- Index
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- Search
SELECT id FROM items ORDER BY embedding <=> '[...]' LIMIT 5;

-- Operators
--  <->  L2      <=>  cosine      <#>  -inner product
--  <+>  L1      <~>  hamming     <%>  jaccard
```

