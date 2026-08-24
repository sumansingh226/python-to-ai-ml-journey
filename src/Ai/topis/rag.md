RAG (Retrieval-Augmented Generation) — Complete Tutorial

A practical, from-scratch guide to understanding and building RAG systems, with examples geared toward a LangChain + Node.js + React + Postgres + ClickHouse stack.

1. What is RAG?

Retrieval-Augmented Generation is a technique where an LLM's answer is grounded in external data that is retrieved at query time, rather than relying only on what the model memorized during training.

Instead of this:

User question → LLM → Answer (from memory only)

RAG does this:

User question → Retrieve relevant documents → Stuff them into the prompt → LLM → Answer (grounded in retrieved data)

The LLM never "learns" your data — it just reads the retrieved chunks as context before answering, the same way you'd hand someone a few relevant pages from a book before asking them a question about it.


2. Why RAG instead of fine-tuning?
	RAG	Fine-tuning
Update data	Instant (just re-index)	Requires retraining
Cost	Low (embedding + storage)	High (GPU training time)
Source attribution	Easy (you know which chunk was used)	Hard (baked into weights)
Hallucination control	Better (model can cite/quote)	Doesn't inherently reduce hallucination
Best for	Knowledge that changes, private/proprietary data	Teaching a model a style, format, or skill



Most production systems that need "answer questions about our docs/tickets/codebase" use RAG. Fine-tuning is for changing how the model behaves, not what it knows.

3. The Core RAG Pipeline

RAG has two phases: Indexing (offline, done once/periodically) and Query time (online, happens per user question).

Phase A — Indexing (build the knowledge base)
Raw documents → Load → Chunk → Embed → Store in vector DB
Load — pull in PDFs, Notion pages, DB rows, web pages, transcripts, etc.
Chunk — split large documents into smaller pieces (see §4).
Embed — convert each chunk into a vector using an embedding model.
Store — save the vector + original text + metadata in a vector store (pgvector, Pinecone, etc.)