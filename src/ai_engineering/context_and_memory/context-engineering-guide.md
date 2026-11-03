# Context Engineering in Agentic AI — The Complete Detailed Guide
## What It Is, Why It Replaces Prompt Engineering, 7 Techniques, 12 Failures, Production Stack

> **Core Thesis:** Prompt Engineering (2022-24) shaped *how you ask*. Context Engineering (2024-26) shapes *what the model knows at inference time*. Coined by Andrej Karpathy / popularized by Anthropic, LangChain, OpenAI 2025: Context Engineering is the discipline of building the right context window for the next token prediction — assembling instructions, memory, knowledge, tools, state, history, examples, and constraints into a single, optimal prompt that maximizes probability of correct action. In agentic AI, context is not a static prompt — it is a living, managed, compacted, routed, compressed assembly line. Bad context = agent fails even with GPT-5. Good context = GPT-4o mini beats GPT-5. Context is the #1 performance lever: 60-80% of agent failures are context failures, not model failures.

### Table of Contents
1. What is Context Engineering? Definition vs Prompt vs RAG vs Memory
2. Why Context Engineering Became #1 Skill in 2025-26
3. The Context Window: Anatomy of What Goes Inside
4. The 7 Core Techniques of Context Engineering
5. 12 Context Failure Modes (Why Agents Hallucinate / Loop / Forget)
6. Context Engineering for Agentic Loops — ReAct, Planning, Tool Use
7. Context Compaction & Management — The Hardest Problem
8. Context Engineering for Long-Horizon Agents — Progress Files, Session Handoff
9. Context Routing, Progressive Disclosure, and Just-in-Time Context
10. Context Engineering Stack — OpenAI, Anthropic, LangChain, LlamaIndex Patterns
11. Measuring Context Quality — Evaluation Metrics
12. Production Checklist — Build Context That Scales to 2M Tokens

---

### 1. What is Context Engineering? Definition vs Prompt vs RAG vs Memory

**Definition (Anthropic / LangChain 2025):**

Context Engineering is the discipline of designing, assembling, retrieving, filtering, ranking, truncating, and injecting the optimal set of information into an LLM's context window at each step of an agentic workflow to maximize task success probability.

**Not same as:**

- **Prompt Engineering:** Crafting wording of instruction. "You are helpful assistant. Think step by step." Single-turn optimization.
- **RAG:** Retrieving documents from vector DB and injecting. Subset of context engineering.
- **Memory:** Storing conversation history / user preferences long-term. Subset.
- **Context Engineering:** Super-set that includes prompt + RAG + memory + tool definitions + tool outputs + state + examples + constraints + history + compressed summaries + system instructions — all orchestrated dynamically per step.

**Formula:**

```
Optimal Context = 
  System Instructions (who agent is, rules, safety) +
  Developer Instructions (task-specific constraints) +
  Memory (long-term user facts, episodic, semantic) +
  Knowledge (RAG, GraphRAG, File Search, Web Search) +
  Conversation History (compressed) +
  Tool Definitions (what tools available + when to use) +
  Tool Outputs (previous observations) +
  State (progress files, scratchpad, plan) +
  Few-Shot Examples (dynamic, relevant) +
  Current User Message
```

All must fit inside context window (128k-2M tokens) without losing signal. Art is what to include, what to exclude, what to compress, what to defer.

**Why context is everything for agents:**

LLM is next-token predictor with no knowledge beyond weights + context window. If fact not in context, model cannot know it. If instruction not in context, model cannot follow it. If tool not described in context, model cannot call it. If past error not in context, model repeats it. Agent's entire world = its context window. Context engineering = designing that world.

### 2. Why Context Engineering Became #1 Skill in 2025-26

**Era shift:**

- **2022-23: Prompt Engineering Era** — Single-turn ChatGPT tasks. Best prompt won. "Act as expert..."
- **2023-24: RAG Era** — Need external knowledge. Vector DB + embeddings. Chunking strategies.
- **2024-25: Tool Calling Era** — Agents call tools. Need tool definitions in context.
- **2025-26: Context Engineering Era** — Long-horizon agents running 6 hours, 500 tool calls, 2M tokens. Prompt + RAG + tools + memory + state all collide. Need systematic management.

**Data:**

- Anthropic: 70% of Claude Code failures traced to missing / stale / overloaded context, not model capability
- LangChain: Context compaction + offloading improved Terminal Bench from 48% to 66.5% same model
- OpenAI Codex: 1M lines shipped because progress files + AGENTS.md + docs/ gave agents correct context every session
- Google: File Search Tool replaces RAG because context assembly is hard — one API call assembles optimal context automatically

**Models got better, context got harder:**

Context windows grew 4k → 32k → 128k → 1M → 2M (Gemini). Bigger window != better agent. Larger window = more noise, more distraction, higher cost, attention dilution (Lost in Middle problem). Need engineering to curate, not just dump.

**Context is performance lever:**

Same model, different context = 3x performance difference. Example: GPT-4o mini with excellent context (precise docs, relevant RAG, compressed history, clear tool descriptions) beats GPT-4o with bad context (200 tool definitions, 50k irrelevant history, no memory). Model matters less than context after certain capability threshold.

### 3. The Context Window: Anatomy of What Goes Inside

**Typical agentic context window (200k tokens example):**

| Component | % Tokens | Example | Purpose |
|-----------|----------|---------|---------|
| System Prompt | 2-5% | "You are refund specialist. Follow policy v2.3. Never auto-refund bundles." | Identity, safety, high-level rules |
| Developer Prompt / AGENTS.md | 5-10% | "Repo structure: docs/policies/, src/refund/. Rules: never comment tests..." | Project-specific constraints from failures |
| Memory | 5-15% | "User: Summi, prefers Hindi + English, Delhi timezone, builds AI curriculum" | Long-term personalization |
| RAG / Knowledge | 15-30% | Retrieved policy chunks, API docs, relevant files | External facts needed for task |
| Conversation History (compressed) | 10-20% | Summarized last 50 turns | Continuity |
| Tool Definitions | 5-10% | 10 tools with descriptions, parameters | What agent can do |
| Tool Outputs / Observations | 20-30% | Previous ReAct steps, file reads, search results | Short-term working memory |
| Scratchpad / State / Plan | 5-10% | "Plan: Step1 done, Step2 in progress, error in Step2 retrying" | Execution state |
| Few-Shot Examples | 2-5% | 2-3 relevant tool call examples | In-context learning |
| Current User Query | 1-2% | "Refund order #12345 bundle?" | Immediate intent |

**Key insight:** System + Developer + Memory + Knowledge are relatively static across session. Tool outputs + State + History are dynamic and grow fast — need compaction.

**Context Token Budgeting:**

Production agents enforce token budgets per component:

```python
CONTEXT_BUDGET = {
  "system": 2000,
  "agents_md": 4000,
  "memory": 6000,
  "rag": 20000,
  "history_compressed": 15000,
  "tool_definitions": 8000,
  "tool_outputs_recent": 30000,
  "scratchpad": 4000,
  "examples": 2000,
  "user_query": 1000,
  "reserve": 10000  # for next tool output
}
Total ~ 94k / 128k window, leaving 34k headroom
```

Exceed budget → trigger compaction, offloading, summarization.

### 4. The 7 Core Techniques of Context Engineering

**Technique 1: Context Assembly / Composition**

Dynamically building context per step based on intent.

- **Static assembly:** Same context every turn (simple chatbot)
- **Dynamic assembly:** Different context per agent step. Example: Planning agent needs architecture docs, implementation agent needs API specs, QA agent needs test cases.
- **Intent-based routing:** Classify user intent → assemble relevant context only. Refund query → refund policies. Coding query → code files.

Implementation:

```python
def assemble_context(intent, stage):
  context = [SYSTEM_PROMPT, AGENTS_MD]
  if intent == "refund_bundle":
    context += [memory.get_user(), rag.search("bundle promotion policy", top_k=5), docs["refund_policy_v2.3"]]
  elif stage == "planning":
    context += [architecture_docs, progress_file]
  elif stage == "tool_retry":
    context += [previous_error, relevant_docs_for_error]
  return compress(context)
```

**Technique 2: Retrieval & Ranking (RAG, GraphRAG, File Search)**

Getting right knowledge into context.

- **Naive RAG:** Chunk 500 tokens, embed, top_k=5, inject. Fails: retrieval 30% failure, ranking 15%.
- **Advanced RAG:** Hybrid search (dense + BM25) + reranker (Cohere, bge-reranker) + query rewriting + HyDE + contextual retrieval (Anthropic). Reduces retrieval failure 30% → 8%.
- **GraphRAG:** Knowledge graph + Leiden communities for multi-hop reasoning. Improves multi-hop 60% → 85%.
- **File Search Tool (Google replacement):** No vector DB, no chunking. Upload files, one API call assembles optimal context. Agent doesn't manage retrieval — tool does.
- **Contextual Compression:** Retrieve 10 chunks, compress to essential sentences only relevant to query. Saves 70% tokens.

**Technique 3: Memory Management (Long-Term Context)**

Three types:

- **Semantic Memory:** Facts about user, preferences, past decisions. "Summi builds curriculum from Python to Agentic AI, prefers .md files not slides, Delhi timezone." Stored in vector DB / SQLite, retrieved per query.
- **Episodic Memory:** Past conversations, tool traces, what worked/failed. "Last time refund for bundle failed because policy check missing, added rule." Enables learning across sessions.
- **Procedural Memory:** Skills, workflows, how to do tasks. "To refund, always: check order → check policy → check bundle rule → ask approval → execute."

Google's Always-On Memory Agent: No vector DB, SQLite with 3 subagents — Ingest (extract facts from conversation), Consolidate (merge/deduplicate), Query (retrieve relevant facts). Replaces RAG for memory.

**Technique 4: Context Compaction & Summarization**

Hardest problem. Context grows every tool call. After 50 tool calls, 80k tokens tool outputs. Model degrades, cost explodes, attention dilutes.

Solutions:

- **Summarization:** Summarize old tool outputs into compressed narrative. "Agent read 5 files, found policy v2.3 says bundle needs approval."
- **Tool-call offloading:** Store massive tool outputs (2000-line logs) in filesystem, keep only essential headers/footers in context. Anthropic: progress files in JSON not Markdown — agents less likely overwrite structured data.
- **Compaction with LLM:** Use cheaper model (Claude Haiku / GPT-4o mini) to summarize old context into 10% size, preserving key facts, decisions, errors.
- **Hierarchical compaction:** Summarize turn-level → session-level → project-level. L0 raw tool outputs, L1 turn summary, L2 session summary, L3 project summary.
- **Lossy vs Lossless:** Lossy (summarization) saves tokens but loses detail. Lossless (offloading to file) keeps detail but requires file read. Hybrid: keep critical facts lossless, compress rest lossy.

Anthropic pattern:

```
Session 1: [Tool outputs] → Write progress.json → Session ends
Session 2: init script reads progress.json + AGENTS.md → Agent oriented instantly without replaying 80k tokens history
```

**Technique 5: Progressive Disclosure & Just-in-Time Context**

Don't load everything upfront. Reveal instructions and tools only when task explicitly requires them.

- **Tool progressive disclosure:** Start with 5 core tools. If agent needs more, it can request tool list. Instead of 50 tool definitions (15k tokens) upfront, load 5 (1.5k tokens) + dynamic discovery.
- **Documentation progressive disclosure:** Don't load entire docs/ (50k tokens). Load AGENTS.md table of contents, then load specific docs based on task. "Task is refund → load docs/policies/refund.md only."
- **Skill routing:** 85 skills available, but only inject 3 relevant skills per task based on intent classification.

Example:

```
Step 1: System: "You have access to skill discovery. Call list_skills(intent) to see relevant skills."
Step 2: Agent: list_skills("refund_bundle")
Step 3: System: Returns 3 skills: refund_policy_check, bundle_validation, approval_flow (not all 85)
```

Saves 80% tokens, reduces distraction.

**Technique 6: Scratchpad, State Management & Structured Context**

Where agent tracks its own progress.

- **Scratchpad:** Chain-of-thought working memory. "I need to check order, then policy, then bundle rule..."
- **Plan file:** Structured plan with steps, status (todo, in-progress, done, failed). Persists across sessions.
- **Progress file:** progress.json / progress.md with what done, what pending, errors encountered, decisions made. Critical for long-horizon agents.
- **Context as files:** Instead of keeping everything in LLM context, write to files that agent can read via tools. Enables 2M context virtually — files act as external memory.

OpenAI Codex pattern:

```
docs/
  architecture.md
  policies/
AGENTS.md (table of contents)
progress.json (structured: {"features": [{"name": "refund", "status": "done", "pr": "#123"}]})
session_handoff.md (for next agent)
```

Agent reads progress.json via read_file tool — not injected permanently, but available on demand.

**Technique 7: Few-Shot Examples & In-Context Learning (Dynamic)**

Examples teach agent how to use tools correctly.

- **Static few-shot:** 2-3 fixed examples in system prompt. "To refund: call check_order, then check_policy..."
- **Dynamic few-shot:** Retrieve examples relevant to current task from example bank using embeddings. Refund task → retrieve 2 refund examples. Coding task → retrieve coding examples.
- **Negative examples:** Show what NOT to do. "Don't auto-refund bundles — see failed example where agent refunded bundle without approval and got penalized."
- **Self-generated examples:** Agent's own successful past traces become examples for future (episodic memory → few-shot).

**Golden rule:** Examples > Instructions. Showing 1 correct tool call trace beats 10 paragraphs describing how to call tool.

### 5. 12 Context Failure Modes (Why Agents Hallucinate / Loop / Forget)

| # | Failure Mode | Symptom | Root Cause | Fix |
|---|---|---|---|---|
| 1 | **Context Overflow** | Agent forgets early instructions, ignores system prompt | Tool outputs + history fill window, push out system prompt | Token budgeting, compaction, offloading, reserve 10k |
| 2 | **Lost in Middle** | Agent ignores info in middle of long context, only uses start/end | Attention dilution in long contexts | Put critical info at start and end, not middle; reranking; compression |
| 3 | **Stale Context** | Agent uses old policy v1.0 not v2.3, hallucinates outdated facts | Memory / RAG not updated, no versioning | Versioned docs, freshness timestamp, always-on memory consolidation, file search with latest |
| 4 | **Retrieval Failure** | Relevant doc not retrieved, agent says "I don't know" | Bad chunking, embedding mismatch, top_k too low | Hybrid search + reranker + query rewriting + GraphRAG |
| 5 | **Ranking Failure** | Irrelevant docs ranked higher than relevant | Similarity search != relevance | Reranker, contextual retrieval, RRF fusion |
| 6 | **Tool Definition Overload** | Agent calls wrong tool, confused by 50 similar tools | Too many tools in context, overlapping descriptions | Progressive disclosure, 5 core tools, dynamic discovery, better naming |
| 7 | **History Poisoning** | Agent repeats past mistake because history contains mistake | Previous failed trace kept in context, model imitates | Filter history, keep only successful traces, summarize errors as learnings not raw logs |
| 8 | **Context Leakage** | PII, secrets, other user's data appears in context | Memory retrieval without permission check, cross-user contamination | PII masking (Presidio), permission-scoped memory, isolation |
| 9 | **Instruction Conflicts** | System says "never auto-refund bundles" but RAG doc says "auto-refund bundles allowed" | Contradictory sources in context | Hierarchy: System > Developer > Memory > RAG. Conflict resolver: prioritize higher authority, flag conflict |
| 10 | **Distraction / Attention Hacking** | Agent follows instructions injected in RAG doc / tool output | Prompt injection via retrieved docs | Sandboxing, tool output sanitization, instruction hierarchy, security hooks |
| 11 | **No Progress Tracking** | Agent loops same action 10 times, doesn't know what done | No scratchpad, no progress file, no state | progress.json, scratchpad, loop detection middleware |
| 12 | **Compaction Loss** | After summarization, agent forgets critical detail (order ID) | Lossy summarization removed key entity | Lossless offloading for entities (order IDs, file paths), structured JSON not markdown, keep critical facts verbatim |

**Most common production failure:** #1 + #5 + #11 = Overflow + Ranking failure + No progress tracking = agent loops, forgets, hallucinates.

### 6. Context Engineering for Agentic Loops — ReAct, Planning, Tool Use

**ReAct Loop Context Needs:**

```
Thought: Need to reason about next action — requires plan + previous observations + policy
Action: Need tool definition + parameters from previous thought + relevant docs
Observation: Tool output becomes part of context for next Thought — but must be compressed if large
```

**Challenge:** Each ReAct iteration adds Thought + Action + Observation (~500-2000 tokens). After 20 iterations, 40k tokens just ReAct traces. Need compaction: keep last 3 iterations full, summarize older 17 into 2k tokens.

**Planning Loop Context Needs:**

```
Planner agent: Needs architecture docs, requirements, progress file — but NOT tool outputs
Generator agent: Needs plan + specific API docs + scratchpad — but NOT entire architecture
Evaluator agent: Needs implementation + test cases + acceptance criteria — but NOT plan generation traces
```

**Solution:** Different context per stage (see Technique 1). Don't give planner tool outputs, don't give evaluator planner's internal reasoning.

**Tool Use Loop Context Needs:**

- Before tool call: Need tool definition + relevant examples + current state
- After tool call: Need tool output + error handling context if failed
- On retry: Need previous error + relevant docs to fix error, NOT same context that failed

**Tool Retry Context Pattern:**

```
Attempt 1 context: [policy doc] + [tool def] → fails: "bundle refund requires approval"
Attempt 2 context: [policy doc] + [previous error] + [approval flow doc] + [tool def] → succeeds
```

If retry with same context, will fail same way. Need to augment context with error-specific knowledge.

### 7. Context Compaction & Management — The Hardest Problem

**Why hardest:**

- Context grows unbounded: 1 tool call = 500-2000 tokens, 100 tool calls = 100k tokens
- Models degrade: Attention diluted, reasoning worse, more hallucinations as context fills
- Cost explodes: 2M tokens = $20-40 per session
- No automatic GC: Unlike RAM, LLM context doesn't auto-free old tokens

**Three strategies:**

**Strategy A: Summarization Compaction (Lossy but cheap)**

```
Old context (80k tokens):
  Turn 1-20: Agent read files, checked policies, tried refund, failed, retried, succeeded

Compacted (8k tokens):
  "Session summary: Agent completed refund for order #12345. Steps: checked order valid, checked policy v2.3, identified bundle requires approval, requested approval, executed refund. Key decisions: used v2.3 not v1.0, asked approval per page 25. Errors: first attempt failed missing approval, fixed in second attempt."
```

Use cheap model (Haiku, GPT-4o mini) to summarize. Keep entities (order IDs, file paths) verbatim, compress reasoning.

**Strategy B: Offloading to Files (Lossless but requires tool call)**

```
Old context: 2000-line log file

Instead of injecting 2000 lines into context:
  Save to /tmp/logs/tool_output_123.txt
  Inject only: "Log saved to /tmp/logs/tool_output_123.txt (2000 lines, errors at line 450, 890). Summary: 2 errors, 98% tests passed. Read file if need details."

Agent can read file via tool if needed, but not forced to carry 2000 lines every turn.
```

Anthropic: Tool-call offloading saved 60% context, improved performance 15%.

**Strategy C: Hierarchical Memory + Progress Files (Production Pattern)**

```
L0: Raw tool outputs (ephemeral, offloaded to files after 3 turns)
L1: Turn summaries (kept 3 recent full, older summarized)
L2: Session summary (progress.json updated each turn)
L3: Project memory (AGENTS.md + docs/ + semantic memory)
```

Session 2 doesn't replay Session 1 raw outputs. It reads L2 + L3 only: progress.json + AGENTS.md + memory.

**OpenAI Codex Pattern:**

```json
// progress.json — structured, not markdown (agents less likely overwrite structured data)
{
  "project": "refund-service",
  "completed": [
    {"task": "refund-policy-check", "status": "done", "pr": "#123", "files": ["src/policy.js"]},
    {"task": "bundle-validation", "status": "done", "pr": "#124"}
  ],
  "in_progress": {"task": "approval-flow", "attempt": 2, "last_error": "missing approver email"},
  "decisions": [{"decision": "Use policy v2.3", "reason": "v1.0 outdated per docs/policies/changelog.md"}]
}
```

Next agent reads progress.json via init script — oriented instantly.

**Compaction Triggers:**

- Token count > 80% window → trigger compaction
- Tool outputs > 30k tokens → offload oldest
- History > 15k tokens → summarize oldest 70%
- Before session end → write progress file + session handoff

### 8. Context Engineering for Long-Horizon Agents — Progress Files, Session Handoff

**Problem:** Long-horizon agents run 6 hours, 500 tool calls, multiple sessions. Context window resets each session (or after compaction). Agent starts fresh with no memory prior work → repeats work, loses decisions, fails.

**Solution: Progress Files + Session Handoff**

**Progress File (progress.json / progress.md):**

Persistent file tracking what done, what pending, decisions, errors. Written each turn, read at session start.

**Session Handoff Document (session_handoff.md):**

Written at end of session for next agent/session.

```
# Session Handoff — 2026-10-24 18:30 IST

## What Done This Session
- Implemented refund policy check v2.3
- Fixed bundle validation bug #456
- PR #123 merged

## What's Pending
- Approval flow (attempt 2 failed missing approver email, need to fetch from contacts)
- Tests for bundle edge case

## Key Decisions Made
- Use policy v2.3 not v1.0 (v1.0 deprecated per changelog)
- Bundle refunds need approval per page 25 — never auto-refund

## Errors Encountered & How Fixed
- Error: "approval required" — Fixed by adding approval_flow tool call
- Error: "policy not found" — Fixed by loading docs/policies/refund.md

## Next Steps for Next Agent
1. Fetch approver email from contacts_search
2. Call approval_flow tool
3. Run tests: npm test src/refund/
4. Update progress.json

## Files Modified
- src/refund/policy.js
- docs/policies/refund.md

## Context Needed for Next Session
- Order #12345 details in /tmp/order_12345.json
- Policy v2.3 at docs/policies/refund_v2.3.md
```

Next agent reads handoff + progress.json via init script — knows exactly where to continue.

**Anthropic Pattern:**

- Structured progress logs, feature tracking files in JSON not Markdown — agents less likely overwrite structured data
- init script so fresh agent can orient itself instantly
- Knowledge base inside repository itself, not Slack or someone's head

### 9. Context Routing, Progressive Disclosure, and Just-in-Time Context

**Context Routing:**

Route different context to different agents / stages.

```
User Query → Intent Classifier → Router

If refund: → Refund Agent gets refund policies + order tools + approval flow
If coding: → Coding Agent gets architecture docs + code files + test tools
If research: → Research Agent gets web search + GraphRAG + summarization tools

Each agent gets minimal, relevant context — not everything.
```

**Progressive Disclosure:**

Don't load everything upfront. Load on demand.

**Level 0: Always loaded (2-5k tokens)**
- System prompt, AGENTS.md table of contents, 5 core tools

**Level 1: On intent detection (5-10k tokens)**
- Relevant policies, relevant tool definitions, memory

**Level 2: On demand via tool calls (variable)**
- Full file contents via read_file, full logs via read_log, full docs via fetch_docs

Example:

```
Agent starts: System + AGENTS.md (TOC) + 5 core tools (5k tokens)
Agent: "Task is refund bundle" → Intent = refund_bundle
System injects: refund_policy_v2.3 chunk + bundle rule + 3 refund tools (10k tokens)
Agent needs order details: calls read_file(/tmp/order_12345.json) → gets order (2k tokens) only when needed
Agent needs approver: calls contacts_search → gets email (500 tokens) only when needed
Total: 17.5k tokens vs 100k if loaded everything upfront
```

Saves 80% tokens, reduces distraction, improves accuracy 20%+.

**Just-in-Time Context:**

Inject context exactly when needed, not before.

- Before tool call that needs policy → inject policy
- After tool failure → inject error-specific docs
- Before planning → inject architecture docs
- Before evaluation → inject acceptance criteria

**Skill Routing (51-agent system):**

85 skills available, but only 3 relevant injected per task based on intent classification. Agent calls list_skills(intent) to discover relevant skills, not all 85 upfront.

### 10. Context Engineering Stack — OpenAI, Anthropic, LangChain, LlamaIndex Patterns

**OpenAI Pattern (Codex, Agents SDK):**

- AGENTS.md as table of contents at repo root
- docs/ directory versioned, indexed, single source truth
- Custom linters enforce architectural rules — no agent can violate
- Garbage-collection agents scan for documentation drift
- Observability data + browser navigation so agents can debug themselves
- Progress files in JSON, init script for orientation
- Context budget: System 2k + AGENTS.md 4k + docs dynamic 20k + tools 8k + outputs 30k

**Anthropic Pattern (Claude Code):**

- CLAUDE.md similar to AGENTS.md, short, pilot checklist
- Structured progress logs, feature tracking JSON not Markdown
- Tool-call offloading: massive tool outputs stored in filesystem, only headers/footers kept in context
- Context compaction: summarize older context intelligently preserving key info
- Progressive disclosure: reveal instructions and tools only when task requires
- Playwright MCP for UI testing — evaluator uses browser to verify work
- Hooks: pre-tool-call, post-file-edit, pre-commit — block destructive commands, enforce formatting

**LangChain Pattern:**

- Context engineering via LangGraph state: StateGraph with channels for messages, docs, tool outputs
- Compaction node: Summarize old messages when token count > threshold
- Offloading node: Store tool outputs in file system, keep summary in state
- Routing: Conditional edges route to different agents based on intent, each gets different context
- Memory: Semantic (vector store), episodic (conversation history), procedural (skills)
- Improved harness without changing model: 52.8% → 66.5% Terminal Bench 2.0

**LlamaIndex / Google Pattern (File Search Tool, Always-On Memory):**

- File Search Tool: No vector DB, no chunking. Upload files, one API call assembles optimal context. Agent doesn't manage retrieval — tool does. Replaces RAG.
- Always-On Memory Agent: No vector DB, SQLite with 3 subagents — Ingest (extract facts), Consolidate (merge/dedup), Query (retrieve). Replaces RAG for memory.
- Agentic RAG with Sufficient Context: Agent checks if retrieved context sufficient to answer, if not, rewrites query and retrieves more. Self-verifying RAG.
- 2M context window (Gemini): Enables entire codebase in context, but still needs engineering — progressive disclosure + compaction still needed even with 2M.

**Production Stack Example:**

```python
# Context Engineering Stack for Refund Agent

# 1. System + AGENTS.md (static)
system_prompt = "You are refund specialist. Follow policy v2.3. Never auto-refund bundles."
agents_md = load_file("AGENTS.md")  # 4k tokens, TOC + rules from failures

# 2. Memory (dynamic, per user)
memory = memory_agent.query(user_id, intent)  # SQLite, 3 subagents, returns relevant facts

# 3. Knowledge (dynamic, per intent)
if intent == "refund_bundle":
  knowledge = file_search_tool.search("bundle promotion policy v2.3", top_k=5)
  # OR hybrid search + reranker + contextual compression

# 4. History (compressed)
history = compact_history(conversation_history, budget=15000)

# 5. Tools (progressive disclosure)
tools = tool_router.get_relevant_tools(intent)  # 5 core + 3 intent-specific, not 50

# 6. State (progress file)
state = load_file("progress.json")  # structured, JSON

# 7. Few-shot (dynamic)
examples = example_bank.search(intent, top_k=2)

# 8. Assembly with token budgeting
context = assemble(
  system_prompt, agents_md, memory, knowledge, history, tools, state, examples, user_query,
  budget=CONTEXT_BUDGET
)

# 9. Compaction trigger
if token_count(context) > 0.8 * WINDOW:
  context = compact(context, preserve_entities=["order_id", "policy_version"])

# 10. Injection
response = llm.generate(context)
```

### 11. Measuring Context Quality — Evaluation Metrics

**How to know if context engineering good?**

| Metric | What Measures | Good Value | Tool |
|--------|---------------|------------|------|
| **Retrieval Precision** | % retrieved docs relevant to query | >80% | RAG evaluation, human label |
| **Retrieval Recall** | % relevant docs retrieved / total relevant | >75% | RAG evaluation |
| **Context Relevance** | % context tokens actually used in final answer | >60% | Attention analysis, LLM judge |
| **Context Utilization** | Does agent use injected context or ignore it? | >70% | Check if agent cites / uses RAG docs |
| **Token Efficiency** | Tokens used / task success | <100k per task | Cost tracking |
| **Compaction Loss** | % critical entities lost after compaction | <2% | Entity preservation test |
| **History Poisoning Rate** | % times agent repeats past mistake due to history | <5% | Failure mode tracking |
| **Progress Tracking Accuracy** | Does progress file match actual progress? | >95% | Manual audit |
| **Tool Definition Clarity** | % tool calls correct first try | >85% | BFCL, Tool calling eval |
| **Context Overflow Rate** | % sessions hitting overflow | <5% | Token counting |
| **Lost in Middle Rate** | % times agent ignores middle context | <10% | Needle-in-haystack test |
| **Stale Context Rate** | % times agent uses outdated info | <3% | Freshness audit |

**Needle-in-Haystack Test:**

Inject critical fact (order ID, policy rule) in middle of 100k context, ask agent to use it. If agent fails, Lost in Middle failure — need reranking, positioning at start/end, compression.

**Context Engineering Evaluation Loop:**

1. Run agent on benchmark (GAIA, SWE-bench, BFCL, WebArena)
2. Analyze failures: which failure mode? (12 modes above)
3. Fix context: add missing doc, improve retrieval, add progress file, compact better
4. Re-run, measure improvement
5. Ratchet: Every failure → new rule in AGENTS.md, new hook, new retrieval pattern

Every component in harness encodes assumption about what model cannot do on own. When model improves, outdated scaffolding should be removed, new scaffolding built to reach next horizon.

### 12. Production Checklist — Build Context That Scales to 2M Tokens

**Checklist for building production context engineering:**

1. **Token Budgeting:** Define budget per component (system, agents_md, memory, rag, history, tools, outputs, state, examples). Enforce budget, trigger compaction at 80%.

2. **Progress Files:** progress.json structured, not markdown. Update each turn. Init script reads it at session start. Enables long-horizon agents across sessions.

3. **AGENTS.md as TOC:** Short (5-10 rules), each from real failure. Table of contents pointing to docs/. Not style guide, pilot checklist.

4. **Memory Agent:** Semantic, episodic, procedural. SQLite + 3 subagents (Ingest, Consolidate, Query) — Google pattern. No cross-user contamination, PII masking.

5. **Hybrid Search + Reranker:** Dense + BM25 + reranker (Cohere / bge-reranker) + query rewriting + contextual retrieval. Reduces retrieval failure 30% → 8%.

6. **Tool Progressive Disclosure:** Start 5 core tools, dynamic discovery via list_skills(intent). Not 50 tools upfront. Better naming, clear descriptions.

7. **Tool-Call Offloading:** Massive tool outputs (2000-line logs) stored in filesystem, only headers/footers + summary kept in context. Saves 60% tokens.

8. **Compaction Strategy:** Summarization with cheap model + hierarchical (L0 raw → L1 turn summary → L2 session summary → L3 project memory). Preserve entities verbatim (order IDs, file paths). Lossless for critical, lossy for rest.

9. **Progressive Disclosure + JIT Context:** Don't load everything upfront. Load on demand via tools. Intent-based routing, skill routing.

10. **State Management:** Scratchpad for working memory, plan file with status, progress.json for persistence, session_handoff.md for next agent.

11. **Few-Shot Examples:** Dynamic retrieval of relevant examples, negative examples showing what NOT to do, self-generated examples from past successful traces.

12. **Security:** PII masking (Presidio), permission-scoped memory, tool output sanitization, instruction hierarchy (System > Developer > Memory > RAG), security hooks blocking prompt injection via RAG.

13. **Evaluation:** Measure retrieval precision/recall, context relevance, token efficiency, compaction loss, overflow rate, Lost in Middle rate, stale rate. Needle-in-haystack test. Failure mode tracking.

14. **Ratchet Principle:** Every context failure → new rule, new hook, new retrieval pattern, new doc in knowledge base. Harness only tightens unless model upgrade makes constraint redundant.

15. **File Search Tool Future:** Consider Google's File Search Tool (one API call assembles optimal context, no vector DB) and Always-On Memory Agent (SQLite) to replace manual RAG + memory management.

---

**Bottom Line:** Context Engineering is discipline of building right context window for next token prediction — assembling instructions, memory, knowledge, tools, state, history, examples, constraints into single optimal prompt that maximizes probability correct action. In agentic AI, context is not static prompt — it is living, managed, compacted, routed, compressed assembly line. Bad context = agent fails even with GPT-5. Good context = GPT-4o mini beats GPT-5. Context is #1 performance lever: 60-80% of agent failures are context failures not model failures. Prompt engineering shapes how you ask, Context engineering shapes what model knows at inference time, Harness engineering shapes what agent can and cannot do. Anatomy: System 2-5%, Developer/AGENTS.md 5-10%, Memory 5-15%, RAG 15-30%, History compressed 10-20%, Tool Definitions 5-10%, Tool Outputs 20-30%, Scratchpad/State 5-10%, Few-Shot 2-5%, User Query 1-2%. Token budgeting essential: define budget per component, trigger compaction at 80% window. 7 Techniques: 1 Context Assembly dynamic per intent and stage, intent-based routing, 2 Retrieval & Ranking hybrid search + reranker + GraphRAG + File Search Tool + contextual compression, 3 Memory Management semantic episodic procedural Google Always-On Memory Agent SQLite 3 subagents Ingest Consolidate Query, 4 Context Compaction summarization with cheap model + tool-call offloading to files + hierarchical compaction L0 raw L1 turn summary L2 session summary L3 project memory, 5 Progressive Disclosure just-in-time context don't load everything upfront skill routing, 6 Scratchpad State Management structured progress.json not markdown init script, 7 Few-Shot dynamic retrieval negative examples self-generated. 12 Failures: Overflow, Lost in Middle, Stale, Retrieval, Ranking, Tool Overload, History Poisoning, Leakage, Instruction Conflicts, Distraction/Prompt Injection, No Progress Tracking, Compaction Loss. Most common: Overflow + Ranking + No Progress Tracking. Agentic Loops: ReAct needs compaction last 3 full older summarized, Planning needs different context per stage planner architecture not tool outputs generator plan + API docs evaluator implementation + test cases, Tool Retry needs error-specific docs not same context that failed. Compaction hardest problem: grows unbounded, models degrade, cost explodes, no auto GC. Strategies: Summarization lossy but cheap, Offloading lossless but requires tool call, Hierarchical memory + progress files production pattern. Long-Horizon: progress.json structured + session_handoff.md with what done pending decisions errors next steps enables agents across sessions. OpenAI Codex pattern docs/ + AGENTS.md TOC + progress.json JSON + custom linters + garbage-collection agents. Anthropic CLAUDE.md pilot checklist + tool-call offloading + compaction + progressive disclosure + Playwright MCP + hooks. LangChain LangGraph StateGraph channels compaction node offloading node routing conditional edges memory semantic episodic procedural 52.8%→66.5%. LlamaIndex Google File Search Tool one API call + Always-On Memory Agent SQLite + Agentic RAG sufficient context self-verifying + 2M context but still needs engineering. Measuring: Retrieval Precision >80%, Recall >75%, Relevance >60%, Utilization >70%, Token Efficiency <100k/task, Compaction Loss <2%, Poisoning <5%, Tracking >95%, Tool Clarity >85%, Overflow <5%, Lost Middle <10%, Stale <3%. Needle-in-Haystack test critical fact middle 100k context. Production checklist: token budgeting, progress files JSON, AGENTS.md TOC 5-10 rules from failures, memory agent, hybrid search + reranker, tool progressive disclosure 5 core dynamic discovery, tool-call offloading saves 60%, compaction cheap model hierarchical preserve entities verbatim, progressive disclosure JIT skill routing, state management scratchpad plan progress session_handoff, few-shot dynamic negative self-generated, security PII masking Presidio permission-scoped memory sanitization hierarchy System>Developer>Memory>RAG hooks, evaluation precision recall relevance efficiency loss overflow Lost Middle stale, ratchet every failure → new rule hook retrieval pattern, consider File Search Tool future one API call replaces manual RAG.

