# Vector Embeddings — A Practical Tutorial

## 1. What is a Vector Embedding?

A vector embedding is a way of turning something — a word, sentence, paragraph, image, or even a user profile — into a list of numbers (a vector) that captures its **meaning** in a way a computer can work with.

```
"The cat sat on the mat"  →  [0.021, -0.183, 0.442, ..., 0.077]   (e.g. 1536 numbers)
```

The key property: **things that mean similar things end up close together in this numeric space**, and things that mean different things end up far apart.

```
"king" and "queen"        → close together
"king" and "banana"       → far apart
"How do I reset my password?" and "I forgot my login" → close together
```

Distance in this space is usually measured with:
- **Cosine similarity** — angle between two vectors (most common for text)
- **Euclidean distance** — straight-line distance
- **Dot product** — used when vectors are normalized

This is the entire foundation of semantic search, RAG, recommendation systems, and clustering.

---

## 2. Why Not Just Use Keywords?

Keyword search (like SQL `LIKE` or Postgres full-text search) matches exact words. It fails on:

| Query | Document | Keyword match? | Should match? |
|---|---|---|---|
| "car" | "automobile" | ❌ No | ✅ Yes |
| "cheap flights" | "affordable airfare" | ❌ No | ✅ Yes |
| "apple" (fruit) | "Apple" (company) | ✅ Yes | ❌ No |

Embeddings solve the first two problems by capturing meaning, not exact spelling — but note the third row: embeddings alone don't solve ambiguity, they just shift where the problem lives (context in the surrounding text helps disambiguate).

---

## 3. How Embeddings Are Actually Created

At a high level, every embedding model does the same job: it's a neural network trained so that semantically similar inputs produce numerically similar output vectors.

### 3.1 Classic approaches (good to know, mostly legacy now)

**One-Hot Encoding**
Each word gets a vector with a single `1` and the rest `0`s. No notion of similarity at all — "cat" and "dog" are just as different as "cat" and "car". Rarely used directly anymore, but it's the conceptual starting point.

**TF-IDF (Term Frequency–Inverse Document Frequency)**
Weighs words by how often they appear in a document vs. how rare they are across all documents. Still purely statistical — "car" and "automobile" are unrelated to it. Used today mostly for keyword/BM25 hybrid search, not semantic meaning.

**Word2Vec / GloVe (2013–2014)**
The first real breakthrough. Trained on the idea that *"a word is defined by the company it keeps."* Words that appear in similar contexts get similar vectors.
- Produces **one fixed vector per word**, regardless of context.
- Famous limitation: "bank" (river) and "bank" (money) get the *same* vector.

### 3.2 Modern approach: Transformer-based embeddings (what you should actually use)

Since ~2018 (BERT onward), embeddings are produced by transformer models that read the **entire sentence at once**, so the same word gets different vectors depending on context.

```
"I deposited money at the bank"   → "bank" vector leans toward finance
"I sat by the river bank"         → "bank" vector leans toward geography
```

Common families:

| Model type | Examples | Notes |
|---|---|---|
| Sentence-transformer models | `all-MiniLM-L6-v2`, `bge-large`, `gte-large` | Open source, run locally, good for RAG |
| OpenAI embeddings | `text-embedding-3-small/large` | Hosted API, strong quality, cheap |
| Cohere embeddings | `embed-v3` | Hosted API, strong multilingual support |
| Voyage AI | `voyage-3` | Hosted, tuned for retrieval/RAG specifically |
| Google | `gemini-embedding-001` | Hosted API |

**How you'd actually generate one (Node.js, matching your stack):**

```js
import { OpenAIEmbeddings } from "@langchain/openai";

const embeddings = new OpenAIEmbeddings({
  model: "text-embedding-3-small",
});

const vector = await embeddings.embedQuery("How do I reset my password?");
// vector is a number[] of length 1536
```

**Local/open-source alternative (no API cost, runs on your server):**

```js
import { HuggingFaceTransformersEmbeddings } from "@langchain/community/embeddings/hf_transformers";

const embeddings = new HuggingFaceTransformersEmbeddings({
  model: "Xenova/all-MiniLM-L6-v2",
});

const vector = await embeddings.embedQuery("How do I reset my password?");
// vector is a number[] of length 384
```

---

## 4. Different Levels / Granularities You Can Embed

This is where "different types of sentence embedding" comes in — you're not limited to embedding whole documents. What you choose to embed changes what kind of search you get.

| Granularity | Example | Best for |
|---|---|---|
| **Word-level** | "bank" | Rare today; used inside older NLP pipelines |
| **Sentence-level** | "The refund was processed on Monday." | FAQ matching, short Q&A |
| **Chunk-level (paragraph)** | 200–500 token chunks of a document | RAG systems — the most common choice |
| **Document-level** | Entire PDF/article as one vector | Coarse topic clustering, not good for precise retrieval |
| **Multi-vector / hierarchical** | Summary vector + child chunk vectors | Advanced RAG — search summaries first, then drill into chunks |
| **Query vs. passage (asymmetric)** | Short question embedded differently than long passage | Some models (e.g. `bge`, `e5`) require prefixes like `"query: ..."` vs `"passage: ..."` |

### Why chunk size matters
- **Too small** (single sentence) → loses surrounding context, embedding becomes ambiguous.
- **Too large** (whole document) → embedding becomes an "average" of many topics, retrieval gets vague.
- **Sweet spot for RAG**: 200–500 tokens per chunk, with ~10–20% overlap between chunks so you don't cut a fact in half.

```js
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 75,
});

const chunks = await splitter.splitText(longDocumentText);
```

---

## 5. Different Embedding *Strategies* for Retrieval

Once you know what to embed, there are several strategies for *how* to embed and search it:

**1. Dense embeddings (standard)**
One vector per chunk, similarity search via cosine distance. What most people mean by "embeddings."

**2. Sparse embeddings (keyword-aware, e.g. BM25 / SPLADE)**
Vector is mostly zeros, weighted heavily on exact important terms. Great for exact matches (product SKUs, error codes, names) that dense embeddings sometimes blur.

**3. Hybrid search (dense + sparse combined)**
Run both, merge/re-rank results. This is the industry-standard approach for production RAG — dense catches meaning, sparse catches exact terms.

**4. Multi-vector / late interaction (e.g. ColBERT)**
Instead of one vector per chunk, keep a vector *per token*, and compare all pairs at query time. More accurate, more expensive to store/query.

**5. HyDE (Hypothetical Document Embeddings)**
Instead of embedding the user's short question directly, first ask an LLM to write a hypothetical answer, then embed *that*. Answers tend to be more similar to real documents than short questions are.

**6. Query rewriting / multi-query**
Generate 3–5 paraphrases of the user's question, embed and search with each, merge results. Reduces the risk that one phrasing misses relevant chunks.

---

## 6. Storing and Searching Embeddings (Your Stack: Postgres)

Postgres with the **pgvector** extension is a solid production choice — you avoid running a separate vector database.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1536),   -- match your model's dimension
    metadata JSONB
);

-- Approximate nearest neighbor index for fast search at scale
CREATE INDEX ON document_chunks
USING hnsw (embedding vector_cosine_ops);
```

Querying for the nearest matches:

```sql
SELECT content, 1 - (embedding <=> $1) AS similarity
FROM document_chunks
ORDER BY embedding <=> $1   -- <=> is cosine distance in pgvector
LIMIT 5;
```

With LangChain.js:

```js
import { PGVectorStore } from "@langchain/community/vectorstores/pgvector";
import { OpenAIEmbeddings } from "@langchain/openai";

const vectorStore = await PGVectorStore.initialize(
  new OpenAIEmbeddings({ model: "text-embedding-3-small" }),
  {
    postgresConnectionOptions: { connectionString: process.env.DATABASE_URL },
    tableName: "document_chunks",
  }
);

await vectorStore.addDocuments(chunks);

const results = await vectorStore.similaritySearch("How do I reset my password?", 5);
```

**Where ClickHouse fits in:** not for the vector search itself (Postgres/pgvector handles that fine at moderate scale) — but great for logging retrieval events, tracking which chunks get retrieved most often, latency metrics, and A/B testing different chunking/embedding strategies at analytics scale.

---

## 7. Common Mistakes to Avoid

- **Mixing embeddings from different models in the same index.** Vectors from `text-embedding-3-small` and `all-MiniLM-L6-v2` are not comparable — distances become meaningless.
- **Forgetting to re-embed if you switch models.** Every chunk needs to be re-embedded with the new model.
- **Not normalizing vectors** when your similarity metric assumes it (check your model's docs).
- **Chunking without overlap**, which can split a key fact across two chunks so neither one fully answers the question.
- **Embedding raw HTML/markdown syntax** instead of cleaned text — the noise dilutes the meaning captured in the vector.

---

## 8. Quick Mental Model Summary

```
Text → Embedding Model → Vector (list of numbers)
                            │
                            ▼
              Stored in a vector index (pgvector)
                            │
        Query text → same embedding model → query vector
                            │
                            ▼
         Find nearest vectors (cosine similarity) → return matching chunks
                            │
                            ▼
              Feed chunks + question into an LLM → final answer (RAG)
```

That last step — feeding retrieved chunks into an LLM — is what turns "vector search" into "RAG."