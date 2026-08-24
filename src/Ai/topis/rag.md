# RAG (Retrieval-Augmented Generation) — Complete Tutorial

A practical, from-scratch guide to understanding and building RAG systems, with examples geared toward a **LangChain + Node.js + React + Postgres + ClickHouse** stack.

---

## 1. What is RAG?

**Retrieval-Augmented Generation** is a technique where an LLM's answer is grounded in external data that is *retrieved at query time*, rather than relying only on what the model memorized during training.

Instead of this:

```
User question → LLM → Answer (from memory only)
```

RAG does this:

```
User question → Retrieve relevant documents → Stuff them into the prompt → LLM → Answer (grounded in retrieved data)
```

The LLM never "learns" your data — it just reads the retrieved chunks as context before answering, the same way you'd hand someone a few relevant pages from a book before asking them a question about it.

---

## 2. Why RAG instead of fine-tuning?

| | RAG | Fine-tuning |
|---|---|---|
| Update data | Instant (just re-index) | Requires retraining |
| Cost | Low (embedding + storage) | High (GPU training time) |
| Source attribution | Easy (you know which chunk was used) | Hard (baked into weights) |
| Hallucination control | Better (model can cite/quote) | Doesn't inherently reduce hallucination |
| Best for | Knowledge that changes, private/proprietary data | Teaching a model a *style*, *format*, or *skill* |

Most production systems that need "answer questions about our docs/tickets/codebase" use RAG. Fine-tuning is for changing *how* the model behaves, not *what* it knows.

---

## 3. The Core RAG Pipeline

RAG has two phases: **Indexing** (offline, done once/periodically) and **Query time** (online, happens per user question).

### Phase A — Indexing (build the knowledge base)

```
Raw documents → Load → Chunk → Embed → Store in vector DB
```

1. **Load** — pull in PDFs, Notion pages, DB rows, web pages, transcripts, etc.
2. **Chunk** — split large documents into smaller pieces (see §4).
3. **Embed** — convert each chunk into a vector using an embedding model.
4. **Store** — save the vector + original text + metadata in a vector store (pgvector, Pinecone, etc.)

### Phase B — Query time (answer a question)

```
User query → Embed query → Similarity search → (Optional: rerank) → Build prompt → LLM → Answer
```

1. **Embed the query** with the *same* embedding model used for indexing.
2. **Similarity search** — find the top-k chunks whose vectors are closest to the query vector.
3. **Rerank (optional but recommended)** — re-score the top-k results with a more precise (usually cross-encoder) model.
4. **Assemble the prompt** — inject retrieved chunks + the user's question into a prompt template.
5. **Generate** — send to the LLM, get an answer grounded in the retrieved text.

---

## 4. Chunking Strategies

How you split documents has a bigger impact on RAG quality than most people expect. Bad chunking = irrelevant retrieval = bad answers, no matter how good your model is.

| Strategy | How it works | Good for |
|---|---|---|
| **Fixed-size chunking** | Split every N characters/tokens, with some overlap (e.g. 500 tokens, 50 overlap) | Quick baseline, unstructured text |
| **Recursive character splitting** | Try splitting on paragraphs → sentences → words, in order, until chunks fit the size limit | General-purpose default (LangChain's `RecursiveCharacterTextSplitter`) |
| **Semantic chunking** | Split based on embedding similarity shifts between sentences — a new chunk starts where meaning changes | Long-form articles, blog posts |
| **Document-structure-aware** | Split on markdown headers, HTML tags, code function boundaries | Docs, wikis, source code |
| **Parent-child / small-to-big** | Embed small chunks for precise matching, but return the larger parent chunk to the LLM for full context | High-precision retrieval + full context generation |

**Rule of thumb:** start with recursive splitting at ~500–1000 tokens with ~10–15% overlap. Only get fancier once you've measured that retrieval quality is actually the bottleneck.

---

## 5. Retrieval Strategies

"Retrieval" isn't just "cosine similarity search." There's a spectrum of techniques:

- **Dense retrieval** — embed everything, do vector similarity search. Good at semantic/paraphrase matches, weaker on exact keywords, acronyms, IDs.
- **Sparse retrieval (BM25/keyword)** — classic keyword search. Great for exact terms, product codes, names — things embeddings can blur.
- **Hybrid search** — combine dense + sparse scores (e.g. weighted sum or reciprocal rank fusion). Usually outperforms either alone.
- **Multi-query retrieval** — the LLM rewrites the user's question into 3–5 variations, retrieves for each, and merges results. Helps when the user's phrasing doesn't match the document's phrasing.
- **HyDE (Hypothetical Document Embeddings)** — ask the LLM to *generate* a hypothetical answer first, embed *that*, and search with it instead of the raw question. Often retrieves better because the hypothetical answer "sounds like" the real documents.
- **Re-ranking** — after initial retrieval (e.g. top 20), pass candidates through a cross-encoder reranker (e.g. Cohere Rerank, BGE-reranker) to reorder by true relevance, then keep the top 3–5.
- **Parent-document retrieval** — search on small chunks, but return their parent (larger) chunk to preserve context.

---

## 6. Vector Stores — and where your stack fits

| Store | Notes |
|---|---|
| **pgvector (Postgres)** | Add vector similarity search directly to Postgres. Great if you already run Postgres — no new infra, transactional consistency with your other tables. Solid default for small-to-mid scale. |
| **ClickHouse** | Not a typical vector store, but excellent for **logging and analytics on your RAG pipeline** — query latency, retrieval hit rates, which chunks get retrieved most, user feedback over time. ClickHouse also now supports vector search functions, so it can double as a high-throughput retrieval layer at large scale. |
| **Pinecone / Weaviate / Qdrant** | Managed, purpose-built vector DBs. Easier to scale to millions of vectors, but adds another service to operate. |
| **In-memory (FAISS, etc.)** | Fine for prototyping, not for production with growing data. |

**For your stack (Node.js + Postgres + ClickHouse):** use **pgvector** as the primary retrieval store, and pipe retrieval events/logs into **ClickHouse** for analytics — e.g. tracking which queries get poor retrieval scores, latency percentiles, and usage patterns over time. This is a very natural split: Postgres for the "live" retrieval path, ClickHouse for the "how is this system performing" path.

---

## 7. Building a Minimal RAG Pipeline — LangChain.js + Node + pgvector

```bash
npm install @langchain/openai @langchain/community langchain pg
```

```js
// 1. Setup: Postgres + pgvector
// Run once in your DB: CREATE EXTENSION IF NOT EXISTS vector;

import { PGVectorStore } from "@langchain/community/vectorstores/pgvector";
import { OpenAIEmbeddings } from "@langchain/openai";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });

const config = {
  postgresConnectionOptions: {
    connectionString: process.env.DATABASE_URL,
  },
  tableName: "documents",
  columns: {
    idColumnName: "id",
    vectorColumnName: "embedding",
    contentColumnName: "content",
    metadataColumnName: "metadata",
  },
};

const vectorStore = await PGVectorStore.initialize(embeddings, config);

// 2. Indexing
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 800,
  chunkOverlap: 100,
});

const docs = await splitter.createDocuments([rawText]); // rawText = your loaded document
await vectorStore.addDocuments(docs);

// 3. Query time
const retriever = vectorStore.asRetriever({ k: 5 });

const relevantDocs = await retriever.invoke("What is our refund policy?");

const context = relevantDocs.map((d) => d.pageContent).join("\n\n");

const prompt = `Answer the question using ONLY the context below. 
If the answer isn't in the context, say you don't know.

Context:
${context}

Question: What is our refund policy?`;

// 4. Generation
import { ChatOpenAI } from "@langchain/openai";
const llm = new ChatOpenAI({ model: "gpt-4o-mini" });
const answer = await llm.invoke(prompt);
console.log(answer.content);
```

---

## 8. Evaluating a RAG System

RAG failures fall into two buckets — **retrieval failures** (wrong/no chunks found) and **generation failures** (right chunks, but bad answer). Measure both:

- **Retrieval metrics:** hit rate (was the right chunk in the top-k?), MRR (mean reciprocal rank), precision@k
- **Generation metrics:** faithfulness (is the answer supported by the retrieved context?), answer relevance, groundedness
- **Tools:** RAGAS, LangSmith (pairs naturally with LangChain), TruLens

Log every query → retrieved chunks → final answer → (optional) user feedback into ClickHouse. This turns "does our RAG system work?" from a guess into a queryable dataset.

---

## 9. Common Pitfalls

- **Chunking too large** → irrelevant text dilutes the prompt, retrieval gets fuzzy.
- **Chunking too small** → loses context, answers feel disjointed.
- **No metadata filtering** → e.g. searching all documents when the user is clearly asking about "the 2024 report" wastes retrieval budget. Filter by metadata (date, source, user) before or alongside vector search.
- **Skipping re-ranking** → top-k vector search alone often isn't precise enough for production quality.
- **Same embedding model mismatch** → indexing with one embedding model and querying with another silently breaks retrieval (vectors aren't in the same space).
- **No evaluation loop** → shipping RAG and never measuring retrieval quality means you're flying blind on why answers are bad.

---

## 10. Beyond Basic RAG

- **Agentic RAG** — instead of a fixed retrieve-then-generate pipeline, the LLM (as an agent) decides *when* and *what* to retrieve, can issue multiple retrieval calls, and can re-query if the first result isn't good enough.
- **GraphRAG** — build a knowledge graph from your documents (entities + relationships) and retrieve via graph traversal instead of (or alongside) vector similarity — better for multi-hop questions ("who reports to the person who approved X?").
- **Multi-hop RAG** — chain multiple retrieval steps together to answer questions that require combining facts from different documents.

---

*Next step: pair this with a vector embeddings deep-dive doc (what embeddings are, different embedding approaches, sentence vs. word vs. document embeddings) if you want the retrieval half of this pipeline explained from first principles.*