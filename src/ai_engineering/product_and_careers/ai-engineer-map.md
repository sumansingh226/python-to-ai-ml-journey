# The AI Engineer's Map: Everything You Need to Build Agentic Systems

Most "AI engineering" reading lists are just a pile of buzzwords in a row. This one is organized by what actually depends on what — so you can see why context engineering comes before agent orchestration, and why observability isn't optional once you have more than one agent talking to more than one tool.

Stack references throughout assume **LangChain (Node.js) + React + PostgreSQL + ClickHouse**, since that's the environment most of these decisions get made in practice.

---

## Layer 1 — Foundations: How the AI Talks to Your System

Everything else in this document sits on top of these four things. Get them wrong and no amount of clever orchestration saves you.

### 1. Prompt Engineering
The discipline of writing instructions that reliably produce the output you want, across edge cases, not just the happy path.

**What it actually involves:**
- Few-shot examples (showing 2-3 input/output pairs beats a paragraph of description)
- Explicit output format instructions ("respond only in JSON, no preamble")
- Chain-of-thought scaffolding for reasoning-heavy tasks ("think step by step before answering")
- Negative examples ("do NOT include X") — often more effective than positive instructions alone
- System prompt vs. user prompt separation — stable instructions vs. per-request content

**Where it breaks:** prompts that work in isolated testing fail once real context (RAG results, conversation history, tool outputs) gets injected around them. Always test prompts *inside* the full pipeline, not standalone.

### 2. Context Engineering
The layer above prompt engineering — deciding *what information the model receives at all*, and how it's structured, before you even think about wording.

**Core questions this discipline answers:**
- What goes in the system prompt vs. what's retrieved per-request?
- How much conversation history do you include, and how do you summarize/truncate the rest?
- What order do you place things in? (Models attend more reliably to the start and end of context — the "lost in the middle" problem is real)
- Do you inject RAG results as raw text, structured JSON, or a formatted table?

**Rule of thumb:** every token you add to context is a token that dilutes attention on every other token. More context isn't automatically better context.

### 3. JSON Schema / Structured Outputs
Defining exactly what shape a model's response must take, so your application code can parse it without regex gymnastics or hoping the model "behaves."

```typescript
// Example: forcing a structured decision from an LLM call
const schema = {
  type: "object",
  properties: {
    decision: { type: "string", enum: ["approve", "deny", "escalate"] },
    confidence: { type: "number", minimum: 0, maximum: 1 },
    reasoning: { type: "string" }
  },
  required: ["decision", "confidence", "reasoning"]
};
```

Most modern model APIs (including Claude's tool-use and structured output modes) support this natively now — you shouldn't be regex-parsing free text out of an LLM response in 2026. If you are, that's a sign to move this up your priority list.

### 4. Function / Tool Calling
Letting the model invoke real code — APIs, databases, calculators, search — instead of just generating text about what it *would* do.

**The mechanic, simplified:**
1. You describe available tools to the model (name, description, parameter schema)
2. The model decides whether/which tool to call, and generates the arguments
3. Your code executes the actual function
4. The result goes back into the model's context
5. The model continues (maybe calls another tool, maybe responds to the user)

This is the single mechanism underneath RAG, agents, and orchestration — they're all built from tool calling plus a loop.

---

## Layer 2 — Data & Knowledge

Once the model can call tools, the next question is: what does it call them *on*? This layer is about representing your domain's knowledge so it's retrievable and reasoned over correctly.

### 5. Data Modeling
Designing the entities, relationships, and structures your AI application runs on — conversations, messages, memory, agent runs. (Full worked example in the schema-design doc from earlier in this conversation — Postgres for live state, ClickHouse for event logs.)

### 6. Ontology Design
Before you build a knowledge graph, you decide what *kinds* of things and relationships are even allowed to exist in your domain — Person, Company, Project; `works_at`, `uses`, `documents`. This is schema design for meaning, not just for storage. Skip it and two engineers will model the same fact two different ways, and your graph silently fragments.

### 7. Knowledge Graphs
Representing relationships between people, concepts, documents, and entities as traversable connections rather than flat rows. (Covered in full depth in the knowledge-graphs doc earlier — the short version: use one when the answer to a question depends on a *chain* of connected facts, not just similar-sounding text.)

### 8. Vector Databases & Embeddings
Turning text (or images, or code) into numeric vectors positioned so that semantically similar content sits close together in vector space — which is what makes "find me documents about this topic" work without exact keyword matches.

**Practical decisions you'll actually face:**
- **Embedding dimension** — matches your model (e.g., 1536 for `text-embedding-3-small`); this is fixed once you pick a model, changing it means re-embedding everything
- **Chunking strategy** — how you split documents before embedding matters more than which vector DB you pick. Too small and you lose context; too large and retrieval gets fuzzy
- **`pgvector` vs. a dedicated vector DB** (Pinecone, Qdrant, Weaviate) — `pgvector` is fine up to a few million vectors and keeps your data in one place; dedicated vector DBs win at massive scale or when you need advanced filtering/hybrid search
- **Similarity metric** — cosine similarity is the default; dot product and Euclidean distance exist for specific embedding models

### 9. RAG Architecture
Connecting an LLM to external documents/databases so it can answer using information it wasn't trained on, and that changes after training.

**The pipeline, and where it usually breaks:**
```
Query → Embed query → Vector search → Retrieve top-k chunks → Inject into prompt → LLM generates answer
```
- **Retrieval quality is almost always the bottleneck**, not the LLM. If your RAG answers are bad, check what got retrieved before you touch the prompt.
- **Hybrid search** (keyword + vector) usually beats pure vector search for anything with proper nouns, IDs, or exact terms.
- **Re-ranking** — retrieve more candidates than you need (e.g., top 20), then use a cheaper model or cross-encoder to re-rank down to the top 3-5 you actually inject.
- **Graph RAG** — when the answer depends on connected facts rather than one similar-sounding chunk, layer a knowledge graph lookup before the vector search.

---

## Layer 3 — Interfaces & Integration

How your AI system connects to the outside world in a way that's maintainable, not a pile of one-off API calls.

### 10. API Design
Designing clean interfaces between AI models and applications — the same discipline as any backend API design, with a few AI-specific wrinkles: streaming responses (SSE/WebSockets for token-by-token output), idempotency for retries (LLM calls fail and get retried more than typical API calls), and versioning your prompts/models the same way you version an API contract.

### 11. MCP / Tool Integration
The **Model Context Protocol** is becoming the standard way to expose tools and data sources to AI models in a consistent, discoverable format — instead of every team writing a bespoke tool-calling wrapper per integration.

**Why it matters practically:** without a standard, every new tool integration (Gmail, a CRM, an internal API) needs custom glue code in every agent that wants to use it. MCP servers expose a standard interface once, and any MCP-compatible agent can use it — this is exactly the pattern behind the "connected tools" you've seen show up automatically in agent platforms like Antigravity or Claude.

---

## Layer 4 — Reasoning & Execution

This is where single tool calls become multi-step, autonomous behavior.

### 12. Agent Architecture
How a *single* agent reasons, decides which tools to use, and completes a multi-step task — the loop underneath everything.

**The core loop (ReAct-style, which is what most agent frameworks implement):**
```
Thought  → what should I do next, given the goal and what I know so far?
Action   → call a tool
Observation → read the tool's result
   ↓ (repeat until done)
Final Answer
```

**Key design decisions:**
- **Max iteration limits** — always cap the loop, or a confused agent will burn tokens indefinitely
- **Memory within the loop** — does each step see the full history, or a summarized version?
- **Error handling** — what happens when a tool call fails? Does the agent retry, ask a human, or give up gracefully?

### 13. Agent Orchestration / Multi-Agent Systems
Coordinating *multiple* agents or subagents — sequential, parallel, or hierarchical — so complex work gets decomposed instead of one agent trying to do everything in one long context.

**Common patterns:**
- **Sequential** — agent A's output feeds agent B (e.g., research agent → writer agent → editor agent)
- **Parallel** — independent subagents work concurrently on different pieces (this is the pattern in the Antigravity subagent setup from earlier: coder + tester + validator + reviewer running at once)
- **Hierarchical / supervisor** — one "manager" agent plans and delegates to specialist subagents, then merges results (Antigravity's "Technical Director" model, or LangChain's supervisor-agent pattern)
- **Debate/critique** — one agent generates, another critiques, iterating until quality bar is met

**The real cost to plan for:** parallel multi-agent systems multiply token usage — a 3-agent team can burn roughly 5-7x the tokens of a single agent doing the same task sequentially. Orchestration buys you speed and specialization, not efficiency.

### 14. AI Workflow / Orchestration (Broader)
The layer above multi-agent coordination — connecting models, tools, APIs, databases, and deterministic business logic into one coherent pipeline. Not everything in a workflow needs to be an "agent" — a lot of production AI workflows are: deterministic step → deterministic step → one LLM call for the judgment-requiring part → deterministic step. Resist the urge to make everything agentic just because you can; deterministic code is cheaper, faster, and more predictable than an LLM call wherever a fixed rule would do the same job.

Common orchestration tools: LangGraph (stateful graphs of steps, good fit with your LangChain.js stack), Temporal (durable execution for long-running workflows), or plain queue-based orchestration (BullMQ + Node.js) for simpler pipelines.

---

## Layer 5 — Quality & Safety

The layer that separates a demo from something you'd trust in production.

### 15. Guardrails & Validation
Enforcing schemas, policies, and constraints on what an AI is allowed to output or do — the safety net between "the model generated something" and "the model's output reaches a user or takes an action."

**Practical layers of guardrails:**
- **Input validation** — sanitize/screen what goes into the model (prompt injection defense)
- **Output schema validation** — reject/retry if structured output doesn't match your JSON Schema
- **Policy checks** — does the response violate content rules, mention competitors, leak PII?
- **Action guardrails** — for agents that *do* things (send emails, make payments), require human approval above a risk/dollar threshold, or restrict tool permissions per agent role (this is exactly what Antigravity's `commandExecutionPolicy: sandbox` setting does)

### 16. Evaluation Design
Creating tests and metrics to measure AI quality — the thing that tells you whether a prompt change made things better or worse, instead of guessing from vibes.

**Types of evals you'll need, roughly in order of how early to build them:**
- **Golden dataset evals** — a fixed set of input/expected-output pairs you run every time you change a prompt or model. Start with 20-50 examples; this alone catches most regressions.
- **LLM-as-judge** — using a second model to score outputs against a rubric when there's no single "correct" answer (tone, helpfulness, accuracy of a summary)
- **Task success rate** — for agents specifically: did it actually complete the multi-step task, not just "did it respond plausibly"
- **Regression testing** — running your eval suite in CI before deploying any prompt/model change, the same way you'd run unit tests before deploying code
- **Human eval sampling** — periodically spot-check a sample of real production outputs; automated evals drift from what users actually care about over time

### 17. Observability & Tracing *(the one most teams add too late)*
Logging every LLM call, tool call, and agent step so you can answer "why did the agent do that" after the fact — not a nice-to-have, the actual mechanism by which you debug non-deterministic systems.

**What to actually capture, mapped to the schema pattern from earlier in this conversation:**

| What | Where it lives (this stack) | Why |
|---|---|---|
| Every agent run (start/end, status, cost) | ClickHouse `agent_runs` | Aggregate cost/latency dashboards |
| Every reasoning step (thought → action → observation) | ClickHouse `agent_steps` | Reconstruct *why* an agent made a decision |
| Every raw LLM API call (tokens, latency, model version) | ClickHouse `llm_events` | Cost attribution, regression detection when a model version changes |
| Conversation state, feedback | Postgres `messages`, `message_feedback` | Live app state + product quality loop |

**Monitoring specifics that matter for agentic systems (beyond generic APM):**
- **Token usage & cost per org/user/agent** — LLM calls are metered differently than normal API calls; track cost as a first-class metric, not an afterthought
- **Latency percentiles per step type**, not just end-to-end — a slow tool call looks different from a slow LLM call, and you fix them differently
- **Tool call failure rates**, broken down by tool — tells you which integrations are flaky before users complain
- **Model version tagging on every trace** — when a provider silently updates a model, you need to be able to correlate a quality dip with the version change
- **Drift detection** — track eval scores over time in production, not just at deploy time; model providers update models under the hood, and prompts that worked last month can silently degrade
- **Alerting thresholds** — cost spikes (a runaway agent loop is the AI-era equivalent of an infinite loop bug, except it costs real money per iteration), error rate spikes, and latency SLA breaches

Tools in this space: LangSmith (built for LangChain specifically), Langfuse (open source, model-agnostic), Helicone, or a custom ClickHouse setup like the one above if you want full control and already run ClickHouse for other analytics.

---

## Layer 6 — The Parts People Forget

These didn't make most "AI engineer" reading lists two years ago, but they're now table stakes for anything running in production.

### 18. Memory Systems
Short-term memory (the current conversation buffer), long-term memory (facts persisted across sessions, usually vector- or graph-backed), and episodic memory (what happened in past sessions, summarized). Getting this wrong means your agent either forgets everything between sessions or drowns in irrelevant history within one.

### 19. Fine-Tuning & Model Selection
Knowing when to reach for prompting vs. RAG vs. fine-tuning (in that order of preference, usually — fine-tuning is the most expensive and least flexible lever, reach for it last), and routing tasks to the right model size: a cheap/fast model for classification-style subtasks, a frontier model reserved for the genuinely hard reasoning step.

### 20. Cost & Latency Optimization
Caching repeated prompts/responses, prompt compression, batching where the API supports it, and model routing (send easy requests to a cheap model, escalate to an expensive one only when needed). At scale, this is often the difference between a product that's profitable and one that isn't.

### 21. Human-in-the-Loop Design
Deciding *where* a human needs to review, approve, or correct AI output before it takes effect — critical for anything high-stakes (the healthcare/fintech examples from earlier both required this by design, not as an afterthought). This includes designing the actual review UI, not just the backend gate.

### 22. Security for AI Systems
Prompt injection defense (untrusted content — web pages, documents, emails — can contain instructions that hijack your agent if you don't treat it as data, not commands), tool permission scoping (an agent should only have access to the specific tools/data it needs for its role, not everything), and sandboxing code execution or browser-agent actions.

### 23. Version Control for Prompts & Agents
Treating prompts, agent configs, and eval suites as versioned artifacts with the same rigor as application code — diffable, reviewable, rollback-able. A prompt change is a deploy; it should go through the same discipline as one.

---

## Layer 7 — Model-Level Engineering

Everything so far treats the model as a black box you call through an API. Once you have real production volume and a narrow enough task, it stops being just a black box.

### 24. Training & Fine-Tuning Small Models
Using a small, focused model (1B-8B parameters) for a specific job instead of a frontier model for everything — cheaper, faster, and sometimes runnable on-device or at the edge.

**The techniques that make this practical:**
- **Distillation** — a frontier model generates outputs (or full training examples) that a small model is then fine-tuned to reproduce. This is the single most common way small models get built now: have Claude or GPT generate 5-10k high-quality examples, fine-tune a small open model on them.
- **LoRA / QLoRA** — parameter-efficient fine-tuning that trains small "adapter" layers instead of the whole model, cutting training cost and time by orders of magnitude while keeping most of the base model's general ability.
- **RLHF / DPO (Direct Preference Optimization)** — aligning a model's outputs to human preferences using pairs of "better vs. worse" responses, rather than single correct-answer labels.
- **Synthetic data generation** — using a large model to manufacture the training set itself, especially useful when real labeled data is scarce.

**When it's actually worth doing:** only once you have (a) a narrow, well-defined, high-volume task, (b) real production data or a reliable way to synthesize it, and (c) you've confirmed prompting/RAG on a bigger model genuinely can't hit the cost or latency target. Fine-tuning is the most expensive, least flexible lever — reach for it last, not first.

### 25. Model Serving & Inference Optimization
Once you're running your own models (fine-tuned or open-weight), how you serve them matters as much as how you trained them.

- **Quantization** — running a model at lower numerical precision (e.g., 8-bit or 4-bit instead of 16/32-bit) to cut memory and cost, usually with a small, acceptable accuracy trade-off.
- **Batching & KV-cache reuse** — serving multiple requests together and reusing computed attention state, which is where most self-hosted inference cost savings actually come from.
- **Hosted API vs. self-hosted** — API providers (Anthropic, OpenAI) win on simplicity and staying current with the frontier; self-hosting (via vLLM, TGI) wins when you need data residency, extreme cost control at scale, or a fine-tuned model no provider hosts for you.

---

## Layer 8 — Infrastructure & MLOps

The plumbing that makes everything above reliable at scale — mostly invisible until it's missing.

### 26. AI Gateway / Model Routing Infrastructure
A layer between your application and model providers (tools like LiteLLM, or a custom gateway) that lets you swap models/providers without touching application code, handle automatic fallback when a provider has an outage, and centralize rate limiting and cost tracking across every team using AI in your org.

### 27. CI/CD for AI Systems
Treating prompt changes, model version bumps, and agent config changes as deploys — run your eval suite in CI before merging, gate deploys on eval score thresholds, and keep the ability to roll back a prompt exactly like you'd roll back a code change. Most teams build this *after* their first bad prompt change reaches production; build it before instead.

---

## Layer 9 — Data Engineering & Training Pipelines

Distinct from the "data modeling" in Layer 2 — that was about *application* data (conversations, agent runs). This is about the data that feeds RAG ingestion and model training.

### 28. Data Engineering for AI
The pipelines that clean, transform, and curate raw data before it becomes RAG-ready documents or fine-tuning examples — deduplication, format normalization, chunking strategy (revisited here from a pipeline-throughput angle, not just a retrieval-quality angle), and keeping ingestion pipelines idempotent so re-running them doesn't create duplicate vectors or documents.

### 29. Dataset Curation & Labeling
Building the human (or model-assisted) labeling workflows that produce eval sets and fine-tuning data — including measuring inter-annotator agreement (do two labelers agree on the same example?) and active learning (prioritizing which unlabeled examples are most valuable to label next, instead of labeling everything uniformly).

---

## Layer 10 — Trust, Safety & Compliance

Guardrails (Layer 5) stop bad outputs from reaching users. This layer is about proving your system is trustworthy *before* it ships, and staying compliant as it runs.

### 30. Red-Teaming & Adversarial Testing
Deliberately trying to break your own system — prompt injection attempts, jailbreaks, edge-case inputs designed to make an agent misuse a tool — before an attacker or a confused user finds the same hole in production.

### 31. AI Governance & Compliance
Model documentation (what model version, what training/eval data, what known limitations), audit trails for regulated industries, and change-management processes for anything AI touches in a regulated workflow. This is where the `model_version` column from the fintech schema example earlier stops being "nice to have" and becomes a regulatory requirement.

### 32. Privacy & Data Governance
PII detection and redaction before data ever reaches an LLM prompt (especially relevant if you're calling a third-party API), data residency requirements (does data need to stay in-region?), and handling right-to-deletion requests against conversation history, embeddings, and any fine-tuning data derived from user content.

---

## Layer 11 — Emerging & Often-Overlooked

### 33. Multi-Modal AI
Vision, audio, and multi-modal embeddings — increasingly a baseline requirement rather than an extra, since agents now routinely need to read screenshots, scanned PDFs, diagrams, or listen to audio as part of a task (the Antigravity browser agent from earlier is a concrete example: it needs vision to do visual QA on a UI).

### 34. Semantic Caching
Caching LLM responses by *meaning* rather than exact string match — if two differently-worded queries are semantically equivalent, you can serve a cached response to the second one instead of paying for another LLM call. A genuinely different technique from standard API response caching, usually implemented via embedding similarity on the incoming query.

### 35. Licensing & Model Selection Trade-offs
Open-weight vs. closed-model licensing terms (can you fine-tune it? can you deploy it commercially? does the license require attribution?), and the broader self-host vs. API decision beyond just raw cost — including who owns the model weights, how quickly a provider updates their frontier model out from under you, and vendor lock-in risk.

---

## How It All Fits Together

```
                          ┌─────────────────────┐
                          │   Evaluation &       │
                          │   Observability       │◄── watches everything below
                          └──────────┬────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │  Guardrails &          │
                          │  Validation            │◄── gates everything below
                          └──────────┬────────────┘
                                     │
        ┌────────────────────────────▼───────────────────────────┐
        │        Agent Orchestration / Multi-Agent Workflows       │
        └────────────────────────────┬───────────────────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │   Agent Architecture   │  (single agent's reasoning loop)
                          └──────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
     ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
     │  Tool Calling /   │  │   RAG / Vector    │  │   Knowledge Graph /  │
     │  MCP Integration  │  │   Retrieval       │  │   Structured Data    │
     └────────┬─────────┘  └────────┬──────────┘  └──────────┬──────────┘
              │                     │                        │
              └─────────────────────┴────────────────────────┘
                                     │
                          ┌──────────▼────────────┐
                          │  Prompt & Context      │  (the foundation everything
                          │  Engineering + Schemas │   above is built from)
                          └────────────────────────┘
```

Read it bottom-up: nothing above a layer works reliably if the layer beneath it is weak. A brilliant multi-agent orchestration setup running on sloppy context engineering just fails in more expensive, harder-to-debug ways.

Layers 7-11 (model training, infra/MLOps, data pipelines, and governance) sit *alongside* this stack rather than strictly above or below it — they become relevant once you outgrow "call a hosted API and prompt it well," which for most teams is well after the core loop above is working.

---

## A Practical Build Order

If you're building an agentic system from scratch with this stack, this is roughly the order that avoids rework:

1. **Data model first** (Postgres schema — conversations, messages, agent runs)
2. **Prompt + structured output** for the single core task, no tools yet
3. **Add tool calling** for 1-2 essential tools
4. **Add RAG** if the task needs external knowledge
5. **Build your eval set** — even 20 examples — before adding more complexity
6. **Add observability** (ClickHouse traces) — do this *before* you add multi-agent orchestration, not after, or you'll be debugging blind
7. **Add guardrails** appropriate to the risk level of the task
8. **Only then** consider multi-agent orchestration, if a single agent genuinely can't handle the task's breadth
9. **Add memory systems** once you need cross-session continuity
10. **Optimize cost/latency** once you know real usage patterns — premature optimization here wastes effort on the wrong bottleneck
11. **Add CI/CD for prompts/evals** once you have more than one person changing prompts, so changes can't silently regress
12. **Consider small-model fine-tuning** only once a specific, high-volume task has stable production data and prompting a big model is confirmed too slow/expensive for it
13. **Formalize governance/compliance** (model versioning, audit trails, PII handling) as soon as the system touches regulated data — earlier than feels necessary, because retrofitting audit trails onto an existing system is much harder than building them in from the start

Steps 5 and 6 are the two most commonly skipped, and the two that make everything after them dramatically easier to build. Step 13 is the one teams regret skipping the longest once a regulator or a security review asks for it.