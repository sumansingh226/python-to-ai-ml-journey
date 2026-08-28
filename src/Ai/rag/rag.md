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

## 7. Building a Minimal RAG Pipeline — Python + LangChain + pgvector

```bash
pip install langchain langchain-openai langchain-postgres psycopg
```

```python
# 1. Setup: Postgres + pgvector
# Run once in your DB: CREATE EXTENSION IF NOT EXISTS vector;

import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

connection_string = os.environ["DATABASE_URL"]  # e.g. postgresql+psycopg://user:pass@localhost:5432/db

vector_store = PGVector(
    embeddings=embeddings,
    collection_name="documents",
    connection=connection_string,
)

# 2. Indexing
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

docs = splitter.create_documents([raw_text])  # raw_text = your loaded document
vector_store.add_documents(docs)

# 3. Query time
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

query = "What is our refund policy?"
relevant_docs = retriever.invoke(query)

context = "\n\n".join(doc.page_content for doc in relevant_docs)

prompt = f"""Answer the question using ONLY the context below.
If the answer isn't in the context, say you don't know.

Context:
{context}

Question: {query}"""

# 4. Generation
llm = ChatOpenAI(model="gpt-4o-mini")
answer = llm.invoke(prompt)
print(answer.content)
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

## 11. Types of RAG — A Field Guide

RAG isn't one fixed architecture — it's a family. Here's how the major variants differ:

| Type | How it works | When to use |
|---|---|---|
| **Naive RAG** | The basic pipeline from §3: embed → retrieve top-k → stuff into prompt → generate. No re-ranking, no query rewriting. | Prototypes, simple Q&A over a small, clean document set. |
| **Advanced RAG** | Naive RAG + optimizations: query rewriting, hybrid search, re-ranking, better chunking (see §4–5). | Most real production systems land here. |
| **Modular RAG** | Treats retrieval, routing, re-ranking, and generation as swappable modules/pipeline stages you can mix, reorder, or run conditionally (e.g. route to different retrievers based on query type). | Systems with multiple data sources or query types (e.g. "search tickets" vs. "search docs"). |
| **Agentic RAG** | An LLM agent decides when/whether to retrieve, chooses which tool or index to query, and can loop (retrieve → check → retrieve again) until satisfied. | Complex, multi-step, or ambiguous questions; when you have multiple retrievers/tools to choose from. |
| **Self-RAG** | The model is trained/prompted to critique its own retrieval and output — deciding if retrieval was even necessary, and grading whether the generated answer is actually supported by the retrieved chunks. | High-stakes answers where hallucination control matters more than latency. |
| **Corrective RAG (CRAG)** | After retrieval, a lightweight evaluator scores the retrieved chunks' relevance. If they're weak, the system falls back to a broader search (e.g. web search) or discards them before generating. | Cases where your index might not have the answer, and you want a fallback instead of a confidently wrong answer. |
| **GraphRAG** | Retrieval happens over a knowledge graph (entities + relationships) instead of, or in addition to, flat vector chunks. | Multi-hop, relationship-heavy questions ("who approved the vendor that missed the SLA?"). |
| **Multi-hop / Iterative RAG** | Multiple retrieve→reason cycles, where each step's output informs the next retrieval query. | Questions that need facts stitched together from several different documents. |
| **CAG (Cache-Augmented Generation)** | Skips runtime retrieval entirely — instead, the relevant knowledge is *preloaded* into the model's context window (or KV-cache) ahead of time, since modern long-context models can hold entire document sets. No vector search at query time. | Small-to-medium, fairly static knowledge bases where long-context models fit the whole corpus, and you want to cut retrieval latency/complexity. Not a fit for large or frequently-changing datasets. |
| **Hybrid RAG + CAG** | Frequently-used or "core" knowledge is cached in-context (CAG-style) for instant access; RAG kicks in only for the long tail of less common queries or larger corpora that don't fit in context. | Systems wanting the speed of CAG for common queries and the scalability of RAG for everything else. |

**Quick mental model:**
- **Naive → Advanced → Modular** is a spectrum of *how sophisticated your retrieve-then-generate pipeline is*.
- **Agentic / Self-RAG / CRAG** are about giving the system *judgment* — deciding whether/how to retrieve, and checking its own work.
- **GraphRAG / Multi-hop** are about *retrieval structure* — graph traversal or chained retrieval instead of flat top-k similarity.
- **CAG** is a different bet entirely — skip retrieval, lean on context length instead. Best thought of as a RAG *alternative* for smaller, static corpora rather than a RAG *variant*.
