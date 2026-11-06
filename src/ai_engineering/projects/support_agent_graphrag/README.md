# Customer Support Agent: RAG + GraphRAG (LangChain + LangGraph)

A support agent that answers customer questions from help docs, past tickets and product data. Vector RAG handles "what does the doc say" questions. GraphRAG handles relational questions ("which plans include feature X and which known issues affect it?"). A LangGraph state machine routes between them, grades answers, and escalates to a human when it cannot answer.

## Goal and success criteria

- Answers grounded in retrieved sources, each with a citation.
- Answers "I don't know" and escalates when evidence is weak.
- Measured on a fixed eval set, not by feel.

Targets (adjust after the baseline run): faithfulness >= 0.9, answer relevance >= 0.85, correct escalation on out-of-scope questions >= 0.9.

## Architecture

```
user question
   │
[classify_intent] ── chitchat ──► direct reply
   │
[route_retrieval] ── factual ──► vector retriever ──┐
   │                                                  ├─► [grade_context] ─► [generate] ─► [check_grounding]
   └── relational/multi-hop ──► graph retriever ─────┘         │ weak                          │ fail
                                                          [rewrite_query] (max 2 loops)    [escalate_to_human]
```

Folders:

- `src/support_agent/ingestion/` load, clean, chunk docs and tickets; extract entities and relations
- `src/support_agent/retrieval/` vector store and hybrid retrieval
- `src/support_agent/graph/` Neo4j schema, graph build, Cypher / graph retrieval
- `src/support_agent/agent/` LangGraph state, nodes, edges, compiled graph
- `data/raw` source files (git-ignored), `data/processed` indexes (git-ignored)
- `tests/` unit tests and eval runner
- `notebooks/` experiments
- `docs/` design notes and eval results

## Phases

1. **Foundations**: environment, sample dataset (help-center articles + resolved tickets), eval set of 30-50 questions with reference answers.
2. **Baseline vector RAG**: chunking, embeddings, Chroma, a simple LangChain retrieval chain. Record baseline eval scores.
3. **Knowledge graph**: define schema (Product, Feature, Plan, Issue, Resolution, Article). Extract entities and relations with an LLM, load into Neo4j, add graph retrieval (Cypher generation + neighbourhood expansion).
4. **LangGraph agent**: state, intent classifier, router, retrievers, context grader, generator, grounding check, query rewrite loop, human escalation with `interrupt`.
5. **Memory and personalization**: conversation memory via checkpointer, per-customer context (plan, open tickets).
6. **Evaluation and tracing**: LangSmith traces, RAG vs GraphRAG vs hybrid comparison on the eval set.
7. **Serving and guardrails**: FastAPI endpoint, PII redaction, prompt-injection checks, rate and cost limits.

Each phase ends with a measurable result in `docs/`.

## Key decisions to make early

- Graph store: Neo4j (default here) vs an in-memory NetworkX graph for a lighter start.
- Graph construction: LLM extraction with a fixed schema (more reliable) vs open extraction.
- Embedding model and chunk size, chosen by eval results rather than defaults.
- Which questions truly need the graph; if few do, keep it as a tool, not the main path.

## Setup

```
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys locally, never commit
docker compose up -d   # Neo4j
```

## Related notes

- `../../knowledge_graphs/graphrag-production-guide.md`
- `../../rag/agentic-rag-graphrag.md`
- `../../agent_architecture/agent-loops.md`
