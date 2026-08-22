# Text Splitting for Vector Embeddings — A Practical Guide

Text splitting is the process of breaking large documents into smaller, meaningful chunks before creating vector embeddings. It helps the embedding model understand the text better and improves search accuracy. Proper chunk size and overlap ensure that important context is not lost.

## Why Splitting Matters

Embedding models turn text into a fixed-size vector, and that vector is
meant to represent *one coherent idea*. Feed it a whole document and the
vector becomes a blurry average of everything in it — good at nothing.
Feed it a single, well-bounded chunk and the vector actually captures what
that chunk is about, which is what makes retrieval work.

Two failure modes to keep in mind while reading the rest of this doc:

- **Chunks too big** → the embedding is diluted across multiple topics;
  retrieval returns chunks that are "sort of" relevant to everything and
  precisely relevant to nothing.
- **Chunks too small** → each chunk loses surrounding context; retrieval
  finds the right sentence but the answer synthesis step can't tell what
  it's actually about.

Every strategy below is a different answer to "where's the right boundary,
for this kind of content?"

---
