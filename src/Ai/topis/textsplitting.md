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

## 1. Fixed-Size / Character-Based Splitting

Split every N characters (or tokens), usually with some overlap between
consecutive chunks.

**When to use:** unstructured plain text with no reliable structure to
split on — logs, raw scraped text, transcripts with no formatting.

**Why:** it's the simplest possible strategy and works on literally
anything, since it doesn't need to understand the content at all.

**Pros**
- Trivial to implement, zero dependencies.
- Predictable chunk sizes — easy to reason about embedding cost and
  retrieval latency.
- Works on any language, any format.

**Cons**
- Cuts sentences, functions, and ideas in half arbitrarily.
- No awareness of meaning — a chunk boundary might fall mid-sentence.
- Consistently the worst-performing strategy on structured content (code,
  docs, tables) where better options exist.

---

## 2. Recursive Character Splitting

A refinement of #1: instead of cutting at a hard character count, it tries
a list of separators in priority order (paragraph break → line break →
sentence → word → character) and only falls back to a harder cut when a
chunk is still too big.

**When to use:** as a *fallback* layer underneath a structure-aware
splitter (see #4 and #6 below) for any section that's still too long after
a smarter split — this is the standard "safety net," not usually the
primary strategy on its own.

**Why:** it respects natural text boundaries (paragraphs, sentences) far
more often than a blind character cut, while still guaranteeing every
chunk stays under a size limit.

**Pros**
- Much less likely to cut mid-sentence than plain fixed-size splitting.
- Still simple, deterministic, and dependency-light.
- Pairs well as a second-stage fallback under almost any other strategy.

**Cons**
- Still has no understanding of *meaning* — just structural punctuation.
- Overlap (commonly 10–15% of chunk size) adds some redundant storage and
  embedding cost in exchange for not losing context at boundaries.

---

## 3. Sentence-Based Splitting

Split at sentence boundaries (using a real sentence tokenizer, not just
`.` matching — abbreviations, decimals, and initials break naive regex
approaches), then group sentences into chunks up to a target size.

**When to use:** dense prose where individual sentences carry complete
thoughts — legal text, policy documents, narrative content.

**Why:** guarantees no sentence is ever split in half, which matters when
a single sentence is often the actual unit of meaning you want retrieved.

**Pros**
- Never breaks a sentence mid-way.
- Good middle ground between fixed-size and full semantic splitting.

**Cons**
- Doesn't account for structure above the sentence level (a chunk can
  still straddle two unrelated paragraphs or sections).
- Needs a real sentence tokenizer for good results — naive punctuation
  splitting fails on abbreviations, numbers, and code-like text.

---

## 4. Structure-Aware Splitting (Markdown / HTML Headers)

Split at structural boundaries the format already gives you — Markdown
headers (`#`, `##`, `###`), HTML tags, or similar — so each chunk is one
logical section, then apply recursive character splitting *within* a
section if it's still too long.

**When to use:** any structured document format — Markdown docs, HTML
pages, wikis, README files, `.mdx`. This was the strategy used for the docs
and meeting-notes sources in the Org Brain project.

**Why:** a header almost always marks a genuine topic boundary that a
human author already decided on — piggybacking on that structure is far
more reliable than guessing where topics change from raw text alone.

**Pros**
- Chunks align with how the author actually organized the content.
- Cheap to implement (just parse the markup), no ML model needed.
- Each chunk can be enriched with its header/title as context prefix,
  which meaningfully improves retrieval (see "Context Enrichment" below).

**Cons**
- Only as good as the document's actual structure — a wall-of-text
  document with no headers gets no benefit.
- A single header's section can still be too large or contain multiple
  sub-topics, requiring a second-stage split.

---

## 5. Semantic Splitting

Embed individual sentences (or small groups of sentences), then measure
the similarity between consecutive sentences. Where similarity drops
sharply, that's a topic shift — cut the chunk there instead of at a fixed
size or structural marker.

**When to use:** long-form unstructured prose where topic shifts happen
mid-document with no formatting cues — think a long email thread, a
transcript, or a book chapter with no subheadings.

**Why:** it's the only strategy on this list that actually looks at
*meaning* to decide where to cut, rather than structure or character
count.

**Pros**
- Chunk boundaries genuinely track topic changes, not just formatting.
- Works even when the source has zero usable structure.

**Cons**
- Requires embedding every sentence just to decide how to chunk — real
  compute and latency cost before you've even built the index.
- More moving parts (similarity threshold tuning) than any other strategy
  here; harder to debug when it chunks "wrong."
- Usually overkill for content that already has good structure — don't
  reach for this if header-based splitting (#4) already works well.

---

## 6. Code-Aware / AST-Based Splitting

Parse the code into an Abstract Syntax Tree and split at function/class/
method boundaries, so a chunk is always one complete, syntactically valid
unit — never half a function.

**When to use:** source code, always. This is the non-negotiable choice
for codebases — used for the codebase source in the Org Brain project via
Graphify's AST parsing.

**Why:** a function or class is the actual unit of meaning in code. A
fixed-size or line-count split will cut a function in half at an arbitrary
line, destroying the one thing that made it embeddable as a coherent idea
in the first place.

**Pros**
- Every chunk is a complete, valid unit — never truncated mid-logic.
- Can carry real structural metadata for free: symbol name, file path,
  line range, and (with a tool like Graphify) call-graph relationships
  (what this function calls, what calls it).
- Dramatically better retrieval precision for "what does function X do"
  style questions than any text-based splitter.

**Cons**
- Needs a real parser per language (tree-sitter, `ast`, or a tool like
  Graphify) — not a drop-in text operation.
- Doesn't handle non-code content in the same repo (READMEs, configs) —
  those still need a text-based strategy alongside it.
- Very large functions/classes can still exceed a reasonable chunk size
  and may need a secondary split — rare, but worth handling.

---

## 7. Sliding Window (High-Overlap) Splitting

Like fixed-size splitting, but with much higher overlap (30–50%+) between
consecutive chunks, so nearly every piece of context appears in at least
two chunks.

**When to use:** when losing information at a chunk boundary is
especially costly and you can afford the extra storage/embedding cost —
e.g. legal or compliance text where missing a clause due to an unlucky
boundary is a real problem.

**Why:** heavy overlap means a fact sitting right at a boundary is very
unlikely to be "orphaned" in a way that hurts retrieval.

**Pros**
- Strong protection against boundary-related information loss.
- Simple to implement — just a parameter change on fixed-size splitting.

**Cons**
- Meaningfully more chunks for the same source text → higher embedding
  cost and a larger index.
- Increases duplicate/near-duplicate content in retrieval results, which
  can crowd out genuinely distinct chunks in a top-k search.

---

## 8. Agentic / LLM-Based Chunking

Give an LLM the document and ask it to propose chunk boundaries directly —
optionally also asking it to generate a summary or title for each chunk.

**When to use:** high-value, relatively small corpora where retrieval
quality matters more than cost — e.g. a curated policy handbook, not a
firehose of raw logs.

**Why:** an LLM can use genuine judgment about what constitutes "one
idea," including cases that trip up every rule-based approach above
(irregular formatting, mixed content types, ambiguous topic shifts).

**Pros**
- Can outperform every rule-based strategy on messy or irregular content.
- Can simultaneously generate useful chunk-level metadata (a summary,
  title, or keywords) as part of the same pass.

**Cons**
- Real cost and latency per document — this doesn't scale cheaply to a
  large or frequently-changing corpus.
- Non-deterministic — the same document can chunk differently on a rerun
  unless you pin the model and prompt carefully.
- Overkill for anything that already has good structure (code, Markdown)
  — reach for a rule-based strategy first.

---

## Context Enrichment (applies on top of any strategy)

Regardless of which splitter you use, prepending context to the chunk
*before* embedding it consistently improves retrieval:

```
Title: Caption Service Overview | Category: middleware | Section: Retry behavior

<actual chunk text>
```

This matters because an isolated chunk can lose its surrounding context —
a chunk that's just a retry-limit number, with no prefix, embeds as "a
number," not "the caption service's retry limit." The prefix keeps the
domain context inside the vector itself, not just in a metadata column
that similarity search never actually looks at.

---

## Quick Reference: Content Type → Strategy

| Content type | Best strategy | Why |
|---|---|---|
| Source code | AST-based (#6) | Function/class is the real unit of meaning |
| Markdown / HTML docs | Header-based (#4) + recursive fallback (#2) | Structure already marks topic boundaries |
| Meeting notes / structured notes | Header/section-based (#4), enrich with date + attendees | Same as docs, plus recency matters |
| Long-form prose, no structure | Semantic (#5) or sentence-based (#3) | No formatting cues to lean on |
| Legal / compliance text | Sentence-based (#3) with high overlap (#7) | Losing a clause at a boundary is costly |
| Raw logs / scraped text | Fixed-size or recursive character (#1/#2) | No usable structure at all |
| Small, high-value curated corpus | Agentic/LLM-based (#8) | Quality matters more than cost at small scale |

---

## Chunk Size & Overlap — General Guidance

- **500 characters (~125–150 tokens) with 10–15% overlap** is a common,
  reasonable default for prose/docs — small enough to stay topically
  focused, large enough to retain context.
- **Code chunks should be sized by the language construct, not a target
  character count** — a function is as long as it needs to be.
- **Bigger isn't automatically better retrieval** — an oversized chunk
  dilutes the embedding even if it technically "contains" the answer
  somewhere inside it.
- **Always test chunk size empirically against real queries** — the right
  size depends on your actual content and questions, not a rule of thumb
  alone.

---

## Common Pitfalls

- Using one splitting strategy for every content type in a mixed corpus
  (code + docs + notes) — each type has a genuinely different "unit of
  meaning" and deserves its own strategy, as in the table above.
- Skipping context enrichment — an isolated chunk with no title/section/
  file prefix underperforms an enriched one on the exact same content.
- Chasing a fancy strategy (semantic or agentic chunking) on content that
  already has good structure — header-based splitting on well-formatted
  Markdown will usually beat semantic splitting on the same document, for
  a fraction of the cost.
- Ignoring overlap entirely on prose content — zero overlap means facts
  sitting exactly at a boundary can become unretrievable from either
  side of the cut.