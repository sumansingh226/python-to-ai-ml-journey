# Projects

Hands-on builds that apply the concepts from the notes in `src/ai_engineering/`. Each project is self-contained with its own README, dependencies, `.gitignore` and `.env.example`.

| Project | What it builds | Stack | Related notes |
|---|---|---|---|
| [support_agent_graphrag](support_agent_graphrag/) | Customer support agent using vector RAG and GraphRAG, routed by a state machine | LangChain, LangGraph, Chroma, Neo4j | `../rag/`, `../knowledge_graphs/`, `../agent_architecture/` |

## Conventions

- One folder per project, named in `snake_case`.
- Each project has its own `README.md` with goal, success criteria, phases and setup.
- Secrets live in a local `.env`, never committed. Commit only `.env.example`.
- Data and generated indexes are git-ignored; keep folders with `.gitkeep`.
- Each phase ends with a measurable result recorded in the project's `docs/`.

---

## Project 1: support_agent_graphrag

### Problem

- Support teams answer the same questions repeatedly from scattered docs and old tickets.
- Plain vector search finds similar text but misses relationships (plan → feature → known issue → fix).
- Wrong answers are costly, so the agent must cite sources and hand off when unsure.

### Scope

In scope:
- Answer product, billing, how-to and troubleshooting questions.
- Cite the article or ticket behind every answer.
- Escalate to a human with a summary when confidence is low.
- Remember the conversation within a session.

Out of scope (for now):
- Taking actions (refunds, account changes).
- Voice or multi-language support.
- Live ticketing-system integration.

### Data sources

1. Help-center articles (how-to, FAQs, policies).
2. Resolved tickets (question, resolution, product, tags), anonymized.
3. Product catalog (products, features, plans, limits).
4. Known-issues list (issue, affected features, workaround, status).

### Vector RAG track

1. Load and clean documents; strip boilerplate and PII.
2. Split into chunks; attach metadata (source, product, doc type, updated date).
3. Embed and store in Chroma.
4. Retrieve top-k with metadata filters (for example, by product).
5. Optionally rerank before generation.
6. Best for: "how do I...", "what does the policy say...".

### GraphRAG track

1. Schema: `Product`, `Feature`, `Plan`, `Issue`, `Resolution`, `Article`.
2. Relations: `Plan -INCLUDES-> Feature`, `Issue -AFFECTS-> Feature`, `Issue -FIXED_BY-> Resolution`, `Article -DOCUMENTS-> Feature`.
3. Extract entities and relations with an LLM against the fixed schema.
4. Deduplicate entities (same feature, different spelling) before loading into Neo4j.
5. Retrieve by entity linking, then expand 1-2 hops, or by generated Cypher.
6. Best for: "does the Pro plan support X and is anything broken?", multi-hop and comparison questions.

### LangGraph agent

State fields:
- `messages`, `question`, `rewritten_question`
- `intent`, `route`
- `documents`, `graph_context`
- `answer`, `citations`
- `retry_count`, `needs_human`

Nodes:
1. `classify_intent`: support question, chitchat, or out of scope.
2. `route_retrieval`: vector, graph, or both.
3. `retrieve_vector` and `retrieve_graph`: fetch evidence.
4. `grade_context`: is the evidence relevant and sufficient?
5. `rewrite_query`: reformulate and retry (max 2 loops).
6. `generate`: answer using only the evidence, with citations.
7. `check_grounding`: every claim must be backed by a source.
8. `escalate_to_human`: pause with `interrupt`, pass a summary of the conversation and evidence found.

Edges:
- Out of scope or chitchat → direct reply, no retrieval.
- Weak context and retries left → `rewrite_query`.
- Weak context and no retries left → `escalate_to_human`.
- Grounding fails → `escalate_to_human`.

### Evaluation

1. Build an eval set of 30-50 questions: factual, multi-hop, ambiguous, out of scope, adversarial.
2. Store reference answers and the source each should cite.
3. Metrics: faithfulness, answer relevance, citation accuracy, correct escalation rate, latency, cost per question.
4. Compare three setups on the same set: vector only, graph only, hybrid.
5. Keep the numbers in `docs/` and re-run after every major change.

### Guardrails

1. Redact PII in inputs, logs and traces.
2. Treat retrieved text as untrusted; block instructions hidden in documents (prompt injection).
3. Answer only from retrieved evidence; refuse otherwise.
4. Per-request token and tool-call limits.

### Milestones

| # | Milestone | Done when |
|---|---|---|
| 1 | Dataset and eval set | Sample data loaded, 30+ questions with references |
| 2 | Vector RAG baseline | Baseline scores recorded |
| 3 | Knowledge graph | Graph loaded, graph retrieval answers multi-hop questions |
| 4 | LangGraph agent | Full routing, grading, retry and escalation path works |
| 5 | Memory | Follow-up questions resolve using earlier turns |
| 6 | Evaluation | Vector vs graph vs hybrid comparison written up |
| 7 | Serving and guardrails | API endpoint up, guardrail tests passing |

### Risks

1. Poor entity extraction produces a noisy graph; use a fixed schema and spot-check samples.
2. Duplicate entities fragment the graph; deduplicate before loading.
3. Graph adds cost and complexity; keep it only if the eval shows a gain on relational questions.
4. Stale docs give outdated answers; store `updated` metadata and prefer recent sources.
5. Eval set too small or too easy; include hard and adversarial cases.
