#### Enriching Metadata during Document Splitting for RAG
When building a Retrieval-Augmented Generation (RAG) system, simply chunking text is not enough. To achieve high retrieval accuracy, you need to enrich each chunk with structural, semantic, and source-level metadata (similar to how a LangChain `Document` object separates `page_content` and `metadata`).

This guide covers how to architect the perfect metadata strategy: what to include, how to add it, and what to avoid.
