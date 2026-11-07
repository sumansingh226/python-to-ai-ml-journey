# Customer Support Agent: RAG + GraphRAG (LangChain + LangGraph)

A support agent that answers customer questions from help docs, past tickets and product data. Vector RAG handles "what does the doc say" questions. GraphRAG handles relational questions ("which plans include feature X and which known issues affect it?"). A LangGraph state machine routes between them, grades answers, and escalates to a human when it cannot answer.

## Goal and success criteria

- Answers grounded in retrieved sources, each with a citation.
- Answers "I don't know" and escalates when evidence is weak.
- Measured on a fixed eval set, not by feel.

Targets (adjust after the baseline run): faithfulness >= 0.9, answer relevance >= 0.85, correct escalation on out-of-scope questions >= 0.9.

## Requirements

Functional:

1. **Understand the query**: classify it as how-to, feature/plan question, bug report, feature request, billing, or out of scope.
2. **Search product knowledge**: look through product docs, feature descriptions, changelogs and past tickets (stored as chunks with metadata: product, feature, doc type, version, updated date).
3. **Answer with sources**: reply in plain language and list the doc chunks used (title, section, link). If the docs do not cover it, say so.
4. **Relational answers**: use the feature graph for questions like "which plan has X", "does issue Y affect feature Z", "what is the workaround".
5. **Detect when a ticket is needed**: bug reports, unresolved questions, missing docs, feature requests, or low-confidence answers.
6. **Create a ticket** with: customer query, summary, type (bug / question / feature request / docs gap), product and feature, severity, steps to reproduce if given, retrieved evidence, the draft answer, and customer identifier.
7. **Assign the ticket to a developer or team** using rules:
   - by feature or component owner (from a feature-to-owner map)
   - by type (bug → engineering, billing → finance/support, docs gap → docs team, feature request → product)
   - by severity (critical → on-call dev, notify immediately)
   - fall back to the support lead if no owner matches
8. **Avoid duplicates**: search open tickets first; link or comment on a matching ticket instead of creating a new one.
9. **Tell the customer** the ticket number, what happens next, and the expected response time.
10. **Human-in-the-loop**: for high severity or low confidence, a support agent reviews the ticket and draft answer before it is sent or assigned.
11. **Track status**: look up an existing ticket by id and report its state when the customer asks.

Non-functional:

1. Every answer cites its sources; no uncited claims.
2. Ticket creation is idempotent (same conversation does not create two tickets).
3. PII is redacted in logs and traces; only the ticket carries customer details.
4. Full trace per conversation (LangSmith) for audit.
5. Target latency: answer under 8 seconds, ticket creation under 3 seconds.
6. Ticketing and owner lookup sit behind an interface, so Jira, GitHub Issues, Linear or Zendesk can be swapped in.

Inputs and outputs:

| Input | Output |
|---|---|
| Customer query + customer id | Answer with doc-chunk citations |
| Low-confidence or bug query | Ticket id, assignee, severity, customer message |
| Ticket id | Current status |

Example flow:

```
Customer: "Export to CSV fails for my Pro plan since yesterday."
1. intent = bug report; product = Reports; feature = CSV export
2. docs: export is supported on Pro (cited chunk); graph: no known issue linked
3. answer: "CSV export is included in Pro. I could not find a known issue, so I've raised a ticket."
4. dedupe: no open ticket matches
5. ticket created: type bug, severity high, owner = Reports team (from feature owner map)
6. customer told: ticket #1234, assigned to Reports team, reply expected within 1 business day
```

Agent additions in the graph: `detect_ticket_need`, `check_duplicate_ticket`, `create_ticket`, `assign_ticket`, `notify_customer`, `get_ticket_status`. Ticketing is exposed to the agent as tools with a human approval step before `create_ticket` and `assign_ticket` on high severity.

Extra graph schema for assignment: `Team`, `Developer`, with `Feature -OWNED_BY-> Team` and `Team -HAS_MEMBER-> Developer`.

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
