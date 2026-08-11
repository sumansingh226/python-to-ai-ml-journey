# Knowledge Graphs for AI

## 1. What is a Knowledge Graph?

A **Knowledge Graph (KG)** is a structured way of representing knowledge as **entities and relationships**.

Instead of storing information only as text or rows in a database, a knowledge graph connects related pieces of information.

For example:

```text
Alice ── works_at ──> OpenAI
Alice ── knows ──> Bob
OpenAI ── develops ──> AI Models
AI Model ── used_for ──> Natural Language Processing
```

The basic structure is:

```text
Entity → Relationship → Entity
```

This is commonly called a **triple**:

```text
Subject → Predicate → Object
```

Example:

```text
Alice → works_at → OpenAI
```
