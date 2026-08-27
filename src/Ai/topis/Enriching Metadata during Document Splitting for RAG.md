#### Enriching Metadata during Document Splitting for RAG
When building a Retrieval-Augmented Generation (RAG) system, simply chunking text is not enough. To achieve high retrieval accuracy, you need to enrich each chunk with structural, semantic, and source-level metadata (similar to how a LangChain `Document` object separates `page_content` and `metadata`).

This guide covers how to architect the perfect metadata strategy: what to include, how to add it, and what to avoid.

## 1. Why is Metadata Critical for RAG Accuracy?

Vector similarity search (finding chunks that match the user's query embeddings) is flawed. It struggles with exact keyword matching, temporal filtering (e.g., "reports from 2023"), and domain-specific routing. Metadata solves this by enabling **hybrid search** (Vector Search + Metadata Filtering) and **Self-Querying** (where an LLM translates a user query into a metadata filter).
