# Context Engineering in Agentic AI 
## The #1 Skill for Building Production Agents: W-S-C-I Framework, Failure Modes, Token Budgeting, Compaction, Memory, OKF, MCP/A2A

> **Core Thesis:** In 2026 prompt engineering is no longer sufficient. Pure prompt engineering is 2-3x improvement, context engineering is 5-10x. Context engineering is curating what fills LLM's context window at every step — now the key skill for building agents. Defined by Andrej Karpathy: "the delicate art and science of filling the context window with just the right information for the next step." Anthropic, LangChain, Cognition all published frameworks for it. By 2026 excellent agent developers are also excellent context architects. Best context does not contain everything; contains just right critical clues. Treat context window as Agent's working memory (RAM) and manage it strictly — not bottomless trash can to dump everything into. Treat like OS managing RAM, loading only high-signal data needed for current execution frame. Well-engineered context window can raise agent task-completion rates from ~30% to ~90% on same underlying model. 60-80% agent failures are context failures, not model failures. Context Engineering = system-level architecture that turns simple LLMs into reliable production-grade AI agents. Focused context beats bloated context.

### Table of Contents
1. What is Context Engineering? Definition vs Prompt Engineering
2. Why Context Engineering is #1 Skill 2025-26 — The Shift
3. Anatomy of Context Window — What Enters LLM Every Step
4. The 4 Context Failure Modes That Break Agents
5. The W-S-C-I Framework — 4 Core Operations (Write, Select, Compress, Isolate)
6. Write — Persist Outside Context, Free RAM
7. Select — Precise Retrieval, Load on Demand, Progressive Disclosure
8. Compress — Dynamic Compression, Evict Redundancy, Compaction Hardest Problem
9. Isolate — Split Work Across Separate Contexts, Sub-Agent Pattern
10. Token Budgeting — 128K and 32K Frameworks
11. Memory Systems — Semantic, Episodic, Procedural, Always-On Memory
12. Context Engineering Stack — OKF, MCP, A2A, File Search Tool, Knowledge Catalog
13. Production Patterns — Anthropic, OpenAI, LangChain, Google
14. Anti-Patterns & Failure Mode Fixes
15. Measuring Context Quality — 10 Metrics
16. Full Production Checklist & Implementation

---

### 1. What is Context Engineering? Definition vs Prompt Engineering

**Every time you call LLM, you send context window — full set of tokens model sees.** That includes system prompts, tool definitions, conversation history, retrieved documents, agent state (memory, scratchpads, goals), OKF bundles, MCP tool definitions.

Prompt engineering focuses on instruction text. Context engineering focuses on all of it — continuously deciding what enters context, what stays, what gets removed or compressed.

**Definition:** Context engineering is the discipline of designing, assembling, retrieving, filtering, ranking, truncating, injecting optimal information into LLM context window at each step. Super-set of prompt + RAG + memory + tools + state. LLM's entire world = its context window. System-level architecture that turns simple LLMs into reliable production-grade AI agents.

**Analogy:** LLM is CPU, context window is RAM, context engineering is OS — managing what fits in working memory so processor can do best work.

**Context Engineering vs Prompt Engineering:**

| Prompt Engineering (Old) | Context Engineering (2026 Approach) |
|---|---|
| Focus: instruction text | Focus: everything model sees |
| When: before deployment | When: continuously at runtime every step |
| Static/Dynamic: mostly static | Always dynamic |
| Scale: single interaction | Multi-turn, multi-tool, multi-source, multi-agent |
| Key skill: writing clearly | Key skill: systems design, information architecture |
| Optimise words in prompt | Optimise what context window contains and how ordered |
| Works for isolated single-step tasks | Required for agentic multi-step production workflows |
| Token budget: 100% discipline | Token budget: 3% of budget, not 100% |

Prompt engineering doesn't disappear — becomes 3% of token budget, not 100% of discipline.

**3 critical components (Glean framework):**
1. Data curation — ensures AI agents receive high-quality relevant information free from noise contradictions
2. Information architecture — structures data in ways agents can efficiently parse and understand — using semantic tagging, hierarchical organization, relationship mapping
3. Dynamic context management — orchestrates end-to-end information lifecycle across persistence, selective retrieval, rolling compression, sub-agent isolation

### 2. Why Context Engineering is #1 Skill 2025-26 — The Shift

**Timeline:**

- 2022: Prompt Era — single-turn, instruction optimization
- 2023: RAG Era — external knowledge, vector DB, retrieval
- 2024: Tool Era — function calling, agents with tools
- 2025-26: Context Era — long-horizon 6 hours, 500 tool calls, 2M tokens, multi-agent orchestration

**Why needed now:**

1. **Plummeting Signal-to-Noise Ratio:** Cost for model to find key information in hundreds pages documents increases sharply. Attention scattered by irrelevant content (Context Distraction). Modern models support 128K-1M+ tokens temptation throw everything in and let model sort out — fails.

2. **Contradictions and Context Poisoning:** Failed early attempts or discarded reasoning processes if left in context heavily interfere with model's subsequent judgments. Google DeepMind documented this with Gemini Pokémon agent — one hallucinated game state propagated into goals and summaries causing nonsensical strategies persisted entire session.

3. **Runaway Costs and Latency:** Every 1K tokens added not only multiplies API costs but significantly increases Time To First Token (TTFT). n² pairwise relationships — at 100K tokens that's 10B relationships each gets proportionally less attention.

4. **Production reality:** LangChain 2026 State of Agent Engineering: 57% teams have agents in production. Anthropic: 70% Claude Code failures = missing/stale/overloaded context. LangChain: compaction improved 48%→66.5% same model. Good context: GPT-4o mini beats GPT-5 with bad context.

5. **Gartner predictions:** 40% enterprise applications will feature task-specific AI agents by late 2026 up from <5% 2025, one-third agentic implementations will combine agents with different skills by 2027 reinforcing context engineering as critical infrastructure. Gartner Top Strategic Trends 2026: Agentic AI officially displaced generative chat as primary driver digital transformation. 60% agentic analytics projects relying solely on MCP will fail by 2028 for want of consistent semantic layer underneath — MCP moves context, does not create it.

**Impact numbers:**

- Context engineering delivers 5-10x improvement vs prompt engineering 2-3x
- Well-engineered context window can raise task completion 30%→90% same model
- Databricks study: accuracy drops around 32K tokens for Llama 3.1 405B — earlier for smaller models. Gemini agent started repeating past actions beyond ~100K tokens literally forgetting how to play because history louder than training
- Chroma Research: every LLM degrades as context grows often hitting cliff around 32K-64K tokens. Focused 20K context outperforms bloated 200K context virtually every task
- Berkeley Function-Calling Leaderboard: every model performs worse with more tools. Quantized Llama 3.1 8B given 46 tools failed task it solved easily with 19 even though everything fit in context — model must attend to everything you put in
- Microsoft/Salesforce team: splitting same benchmark across multiple turns caused 39% accuracy drop. OpenAI o3 dropped from 98.1 to 64.1. Early preliminary answers remain in context act as strong priors for final answer — When LLMs take wrong turn they get lost and do not recover

### 3. Anatomy of Context Window — What Enters LLM Every Step

**Typical 200K context window breakdown (agentic loop):**

| Component | Budget | % | Description |
|---|---|---|---|
| System instructions | 2-5% | Identity, safety, AGENTS.md / CLAUDE.md rules, pilot checklist |
| AGENTS.md / OKF index | 5-10% | Project rules from failures, knowledge bundle entry points |
| Memory (long-term) | 5-15% | Semantic (facts), Episodic (experiences), Procedural (how-to), user facts |
| RAG / File Search | 15-30% | External knowledge, OKF concepts, retrieved docs, hybrid dense+BM25+reranker |
| History compressed | 10-20% | Conversation history after compaction, anchors, summaries |
| Tool Definitions | 5-10% | MCP servers, function schemas — grows fastest, need progressive disclosure |
| Tool Outputs | 20-30% | Observations, API responses, file contents — grows fastest, need offloading |
| Scratchpad / State | 5-10% | progress.json, session_handoff.md, current goals, decisions, blockers |
| Few-Shot | 2-5% | Dynamic examples retrieved relevant to intent, negative examples |
| User Query | 1-2% | Current intent |

**Token Budget Practical Frameworks:**

**128K context window:**

| Component | Budget | % |
|---|---|---|
| System prompt + rules | 3,000-4,000 | 3% |
| Tool definitions (5-8) | 2,000-3,000 | 2% |
| Few-shot examples | 3,000-5,000 | 3% |
| Retrieved context (RAG/OKF) | 15,000-20,000 | 15% |
| Conversation history (compacted) | 25,000-35,000 | 25% |
| Working memory / scratchpad | 30,000-40,000 | 28% |
| Safety buffer | 25,000-30,000 | 22% |

Buffer isn't wasted — insurance against unexpected tool outputs.

**32K local model (Ollama Qwen 3 14B etc):**

| Component | Budget | % |
|---|---|---|
| System prompt | 1,500 | 5% |
| Tools (3-5) | 1,000 | 3% |
| Retrieved context | 5,000 | 16% |
| History (compacted) | 8,000 | 25% |
| Working memory | 10,000 | 31% |
| Buffer | 6,500 | 20% |

**Core rule:** Budget per component, trigger compaction at 80% usage.

### 4. The 4 Context Failure Modes That Break Agents

Identified by Drew Breunig, validated by DeepMind, Databricks, Berkeley, Microsoft:

**1. Context Poisoning — hallucination enters context treated as ground truth**

A hallucination enters context and gets treated as ground truth. Google DeepMind documented with Gemini Pokémon agent — one hallucinated game state propagated into goals and summaries causing nonsensical strategies persisted entire session.

Especially dangerous for local LLMs which hallucinate more often. Without validation errors cascade every turn.

Fix: Write, Select with validation, Compress with verification, Isolate with quarantine.

**2. Context Distraction — accumulated info overwhelms training-time knowledge**

Accumulated information overwhelms training-time knowledge. Databricks study found accuracy drops around 32K tokens for Llama 3.1 405B — earlier for smaller models. Gemini agent started repeating past actions from history beyond ~100K tokens literally forgetting how to play because its history was louder than its training.

For local models (32K-128K windows) distraction hits after 15-20 complex tool interactions.

Fix: Write + Select — tiered retrieval, progressive disclosure, offload large outputs.

**3. Context Confusion — irrelevant info influences decisions**

Irrelevant information influences decisions. Berkeley Function-Calling Leaderboard proved every model performs worse with more tools. Quantized Llama 3.1 8B given 46 tools failed task it solved easily with 19 even though everything fit in context. Model must attend to everything you put in.

Fix: Isolate + Select — curate 5-8 tools max, load others dynamically via MCP, intent-level tools with strong validation.

**4. Context Clash — different parts disagree**

Different parts of context disagree. Microsoft/Salesforce team showed splitting same benchmark across multiple turns caused 39% accuracy drop. OpenAI o3 dropped 98.1→64.1. Early preliminary answers remain in context act as strong priors for final answer — When LLMs take wrong turn they get lost and do not recover.

Fix: Isolate + Compress — sub-agent pattern with clean context, squashing failed attempts, quarantining conflicting external data.

### 5. The W-S-C-I Framework — 4 Core Operations

Industry converged on four core strategies, each maps to failure modes. Treat context window like RAM, OS managing what fits in working memory so processor can do best work.

**W-S-C-I:**

1. **Write — Externalize, Persist Outside Context, Free RAM**
2. **Select — Precise Retrieval, Load on Demand, Progressive Disclosure**
3. **Compress — Dynamic Compression, Evict Redundancy, Rolling Window**
4. **Isolate — Context Isolation, Firewall Mechanism, Sub-Agent Pattern**

Mental model: Do not treat context window as bottomless trash can to dump everything into; treat as Agent's working memory (RAM) and manage strictly. OS loading only high-signal data needed for current execution frame.

**Mapping to failure modes:**

- Write → fixes Poisoning, Distraction, Clash (by persisting clean state outside, synthesizing)
- Select → fixes Distraction, Confusion, Poisoning (by retrieving only relevant, validated)
- Compress → fixes Distraction, Poisoning, Clash (by evicting redundancy, squashing failures)
- Isolate → fixes all four (by splitting work across separate contexts, firewall)

### 6. Write — Persist Information Outside Context, Free RAM

In long-running tasks agents generate massive intermediate data (e.g., contents of downloaded temp files, 100MB JSON response from API call, lengthy drafts).

**Best Practices:**

- Never inject raw big data directly into conversation history
- Have agent use tools to write data to external storage (databases, file systems, specialized Long-term Memory services) and only retain reference ID or brief summary in current context
- Act of writing forces agent to synthesize — itself improves quality

**Patterns:**

**Pattern 1: MEMORY.md scratchpads / progress.json**

Agent maintains structured file — goals, observations, decisions, blockers — and reads at start of each session. Claude Code does this extensively tracking progress and recording decisions across complex tasks. OpenClaw agents same pattern where each agent maintains own accumulated knowledge base.

Even 7B model can maintain useful memory files — key is keeping them short and structured.

Example progress.json (structured not markdown — JSON better for agents):

```json
{
  "goal": "Handle refund for order #12345 bundle promotion",
  "done": ["Checked order has bundle_id BND-789", "Read policy v2.3 page 25"],
  "pending": ["Validate approval required", "Run Playwright test"],
  "decisions": ["Bundle promotion refunds need approval per policy page 25 - never auto-refund"],
  "errors": ["Tool call fetch_policy failed once due to timeout"],
  "next_steps": "Call bundle_validation tool via MCP"
}
```

**Pattern 2: Structured task logs / log.md**

For multi-step tasks write each completed step and result to log file. Agent reads only log summary instead of keeping full tool output history in context.

OKF convention: log.md records chronological change history.

**Pattern 3: Memory databases — Mem0, Letta, Redis, SQLite**

For semantic memory queries at scale more powerful than flat files when agent accumulates hundreds of facts. Example Google Always-On Memory Agent SQLite 3 subagents Ingest/Consolidate/Query replaces RAG for memory.

**Pattern 4: Offloading tool outputs**

When agent calls fetch_user_activity_logs(user_id) and returns 10k logs, tool should save logs to /tmp/logs_user_X.json and return {"status":"success","file_path":"/tmp/logs_user_X.json","summary":"Found 10k logs covers Jan to Jun"} to agent. If agent later needs specific data can invoke another tool like query_json_file(file_path, jsonpath).

This saves 60% tokens — store 2000-line log to file keep header/footer.

**Pattern 5: Session handoff**

session_handoff.md for next agent: what done, pending, decisions, errors, next steps — enables 6-hour agents across sessions.

### 7. Select — Precise Retrieval, Load on Demand, Progressive Disclosure

Extension of traditional RAG concepts in agent runtimes. Select strategy requires agent actively fetch necessary information to execute current step.

Don't pre-load everything. Pull data just-in-time so you pay token cost only when information actually needed.

**Best Practices:**

- Tiered Retrieval: Grade knowledge base. Tier 1 core rules hardcoded in System Prompt; Tier 2 task guidelines obtained via fast vector retrieval; Tier 3 deep search tools actively invoked by Agent
- Ensure fetched content highly structured (e.g., Markdown format with clear H2 headings) to help model allocate Attention more effectively
- Use pointers not full data: Pointer-Based Retrieval — instead of loading full data use pointers LLM can follow when necessary just like humans recall where to find info rather than memorizing everything

**Patterns:**

**1. Tool-based retrieval / File Search Tool:**

Give agent grep, file-read, search tools. It decides what to load based on current task. Claude Code uses this — writing targeted queries using head/tail to extract specific sections rather than loading entire files. Google File Search Tool one API call replaces RAG.

**2. RAG + Hybrid retrieval + Reranker + GraphRAG:**

Embed knowledge base into ChromaDB or Qdrant and retrieve relevant chunks at query time. ChromaDB runs entirely on-device with zero API cost pairing well with Ollama for fully local setups. Hybrid dense+BM25+reranker reduces retrieval failure 30%→8%. GraphRAG for relationships. OKF bundle for curated stable knowledge.

**3. Progressive disclosure:**

Let agent explore incrementally. File names suggest relevance. Directory structure hints at organization. Agent builds understanding layer by layer. Start with 5 core tools, dynamic discovery list_skills(intent) returns 3 relevant not 85 — saves 80% tokens. OKF index.md entry points offer progressive disclosure root carries okf_version.

**4. Hybrid retrieval:**

Drop small always-relevant context file (like CLAUDE.md or AGENTS.md) into system prompt for speed, and use RAG for everything else. This is approach Claude Code and OpenClaw both take. Level 0 always loaded 5k, Level 1 on intent 10k, Level 2 on demand via tool calls.

**5. Intent router:**

Intent classifier → router → different agent gets minimal relevant context. Refund query → refund policies, coding → code files.

**6. Contextual compression:**

Use LLM to compress retrieved chunks to keep only relevant sentences — reduces token usage 70% while preserving relevance.

**7. Few-Shot Dynamic:**

Retrieve relevant examples + negative examples + self-generated from past successes — examples > instructions.

### 8. Compress — Dynamic Compression, Evict Redundancy, Compaction Hardest Problem

Just like OS garbage collection agent's context needs regular cleanup. Lengthy interactions generate traces of small talk, intermediate confirmations, error retries.

When context grows too large compress without losing critical information. Without compression every agent eventually hits limit or degrades below useful accuracy.

**Compaction is hardest problem in context engineering:**

Grows unbounded, models degrade, cost explodes, no auto GC. 60-80% failures are context failures. Models degrade after 32K-64K. Cost explodes. No automatic garbage collection.

**3 Strategies:**

**Strategy 1: Summarization with cheap model + offloading:**

Rolling Window & Summarization: When conversation turns exceed set threshold trigger background task to pass earlier turns to smaller model (like Gemini 3.5 Flash or Claude Haiku). Have it generate Current State & Goals Summary and replace thousands tokens raw logs with brief summary.

Tool-call offloading (store 2000-line log to file keep header/footer) saves 60%.

Example: OpenAI Codex: progress.json structured JSON not markdown + init script. Claude Code preserves architectural decisions and unresolved bugs while discarding redundant tool outputs. After compaction continues with summary plus five most recently accessed files.

**Strategy 2: Squashing Tool Calls:**

If agent calls terminal command 10 times with errors trying to fix bug and finally succeeds on 11th try, details of first 10 failures should be squashed into single line for future context: "Failed 10 times due to syntax errors ultimately resolved by doing X."

Replace old tool outputs with brief summaries or remove entirely. Anthropic launched this as platform feature — one of safest forms compression because old results rarely re-referenced.

**Strategy 3: Hierarchical memory — L0 raw → L1 turn → L2 session → L3 project:**

Production pattern:

- L0 raw logs
- L1 turn summaries
- L2 session summaries
- L3 project knowledge (AGENTS.md, OKF)

Sliding window with anchors: Keep system prompt + last N turns; summarize everything between. Anchors are turns with critical decisions or state changes that survive even aggressive compression.

Incremental summarization: Instead of compressing everything at once maintain running summary updated every K turns. Avoids quality loss compressing very long conversation in one shot.

**For 32K local models:** Set compaction threshold at 75% usage (~24K tokens). Summarize into structured brief (goals, progress, blockers, key findings), reinitiate with brief + system prompt + last 3 turns, write full detailed state to MEMORY.md for reference. Lets 32K model handle tasks that would otherwise require 200K+ tokens history.

**Anthropic approach for long-horizon tasks:**

Context engineering for long-horizon tasks: rolling compaction + tool result clearing + anchors. Conversation compaction: summarize history and reinitiate with compressed summary.

**LangChain approach:**

LangGraph StateGraph + compaction node + routing — compaction improved 48%→66.5% same model.

### 9. Isolate — Split Work Across Separate Contexts, Sub-Agent Pattern

In complex tasks agents often need to wear multiple hats (e.g., planning task, writing code, reviewing code). Mixing contexts of different roles easily leads to Context Clash.

Use multiple agents with clean focused context windows instead of one agent trying to hold everything. Nuclear option against all four failure modes.

**Best Practices:**

- Sub-Agent Pattern: When need to execute subtask likely to generate lot of noise spin up new Sub-Agent instance (with clean context or even different System Prompt). Main agent only passes explicit instructions and limited context to sub-agent. Once finished sub-agent only returns final report discarding its messy thought process. Architecture not only reduces costs but drastically improves reliability
- Three Qwen 3 14B agents with 8K focused context each will outperform single 70B model drowning in 100K tokens. OpenClaw makes practical — run coordinator on smarter model delegate subtasks to faster smaller models via Ollama

**Patterns:**

**1. Sub-agent delegation:**

Coordinator agent delegates focused tasks to specialized sub-agents each with own clean context. Sub-agent processes returns summary and its full context discarded. Parent's context stays lean.

Main agent assigns tasks and receives results keeping its context clean and focused.

**2. Fan-out/fan-in:**

For research tasks spin up multiple agents in parallel to investigate different aspects. Each works independently then coordinator synthesizes. This is how Devin (Cognition) handles complex coding.

**3. Tool-scoped isolation:**

When using complex tools that return large outputs (web search, code analysis) make tool call in isolated inference. Return only compressed result to main agent.

**4. Context quarantines:**

Process potentially conflicting external data in isolated call first. Quarantine agent evaluates reconciles returns clean synthesis — keeping contradictions out of main context.

**5. Role isolation:**

Planning agent gets architecture not tool outputs, executor gets tool outputs not full history, validator gets test results not planning docs.

### 10. Token Budgeting — 128K and 32K Frameworks

Already detailed in Section 3. Add practical enforcement:

**Enforcement code (pseudo):**

```python
def check_budget(context):
  total = sum(len(c.tokens) for c in context.components)
  if total > 0.8 * MAX_TOKENS:
    trigger_compaction()
  if len(context.tools) > 8:
    trigger_tool_pruning() # keep 5-8 core, dynamic load rest via MCP
  if len(context.tool_outputs) > 10:
    trigger_offloading() # write to file, keep summary
```

**Key metrics:**

- Buffer 20-22% insurance
- Tools 5-8 max curated non-overlapping
- Retrieved context 15% budget
- History 25% compacted
- Working memory 28-31%

**Local LLM changes:**

- Smaller windows demand better engineering — 32K-128K usable but can't be lazy, techniques requirements not nice-to-haves
- Smaller context = faster inference — focused 8K context generates noticeably faster than 30K same hardware. Prompt caching amplifies further
- Write aggressively — MEMORY.md, task logs, structured notes keep window free
- Local RAG cheap — ChromaDB + Ollama embeddings negligible overhead for dramatically better context management
- Compaction non-negotiable at 32K — hit wall after 10-15 complex tool interactions

### 11. Memory Systems — Semantic, Episodic, Procedural, Always-On Memory

**Types:**

- **Semantic memory:** Facts about world, user, organization — e.g., "Revenue = net excluding refunds"
- **Episodic memory:** Experiences, past conversations, what happened — e.g., "Last refund for #12345 required approval"
- **Procedural memory:** How to do things — e.g., "How to validate bundle promotion"
- **Short-term:** Current session working memory
- **Long-term:** Cross-session persisted

**Implementations:**

- **MEMORY.md / progress.json:** Simple structured files, goals, observations, decisions, blockers — agent reads at start each session. Even 7B model can maintain useful memory files key is short and structured
- **Memory databases:** Mem0, Letta, Redis for semantic memory queries at scale — more powerful than flat files when agent accumulates hundreds facts. Architectural patterns covered in How to Build Agent Memory That Actually Works
- **Google Always-On Memory Agent:** SQLite 3 subagents Ingest/Consolidate/Query replaces RAG for memory — Ingest subagent writes raw facts, Consolidate deduplicates and synthesizes, Query retrieves relevant on demand
- **Structured task logs:** For multi-step tasks write each completed step and result to log file. Agent reads only log summary instead of keeping full tool output history

**Memory as part of context pipeline:**

When building context engineering workflow you are engineering context pipeline so LLM gets to see right information in right format at right time. Nothing fancy.

### 12. Context Engineering Stack — OKF, MCP, A2A, File Search Tool, Knowledge Catalog

**Stack components 2026:**

**OpenAI stack:**

- AGENTS.md TOC + docs/ + custom linters + garbage-collection + progress.json
- File Search Tool one API call replaces RAG
- progress.json structured JSON not markdown + init script

**Anthropic stack:**

- CLAUDE.md pilot checklist + offloading + compaction + Playwright MCP
- MCP stateless spec July 28 2026
- Tools: Read, Grep, Glob, Bash, TodoWrite, compaction node

**LangChain stack:**

- LangGraph StateGraph + compaction node + routing + 52.8%→66.5% improvement
- Workflow-with-embedded-AI-steps production standard: deterministic flow with LLM-powered extraction
- Agent-gated-workflows (agent classifies workflow executes), workflow-orchestrating-agents (workflow routes agents handle complex subtasks)

**Google stack:**

- File Search Tool one API call replaces RAG
- Always-On Memory SQLite + Agentic RAG sufficient context + 2M context
- Open Knowledge Format (OKF) — directory Markdown + YAML frontmatter, concept-per-file, path = ID, links = graph, portable Git-reviewable bundle. Solves context sprawl. Minimal spec type required. Tooling Kiso, OKF4net, google-okf PyPI, GitBook Git Sync
- MCP + A2A layered: MCP for agent-to-tool/context access (hands), A2A for agent-to-agent coordination (voices), Kafka for memory

**Practical context layer workflow:**

1. List available context: system instructions, user inputs, tools, databases, documents, memory, external data sources, OKF bundle
2. Map context to tasks: which context needed for planning vs execution vs validation
3. Select: tiered retrieval, progressive disclosure, intent router
4. Write: offload large outputs to files, keep reference + summary
5. Compress: rolling window, squashing, hierarchical summarization at 75% threshold
6. Isolate: sub-agents for noisy tasks, fan-out/fan-in for research, quarantines for conflicting data

**MCP moves context, does not create it.** At Gartner Data and Analytics Summit 2026 analyst Andres Garcia-Rodeja predicted 60% agentic analytics projects relying solely on MCP will fail by 2028 for want of consistent semantic layer underneath. Need OKF or Knowledge Catalog for semantic layer.

### 13. Production Patterns — Anthropic, OpenAI, LangChain, Google

**Pattern 1: Agentic Loops — ReAct needs compaction last 3 full older summarized, Planning needs different context per stage (planner gets architecture not tool outputs), Tool Retry needs error-specific docs not same context that failed**

**Pattern 2: Routing & JIT — Intent classifier → router → different agent gets minimal relevant context. Level 0 always loaded 5k, Level 1 on intent 10k, Level 2 on demand via tool calls**

**Pattern 3: Long-Horizon — progress.json + session_handoff.md — what done, pending, decisions, errors, next steps — enables 6-hour agents across sessions**

**Pattern 4: Progressive Disclosure — don't load everything upfront — start 5 core tools, dynamic discovery list_skills(intent) returns 3 relevant not 85 — saves 80% tokens**

**Pattern 5: Scratchpad & State — progress.json structured not markdown + session_handoff.md for next agent**

**Pattern 6: Few-Shot Dynamic — retrieve relevant examples + negative examples + self-generated from past successes — examples > instructions**

**Pattern 7: Assembly — dynamic per intent/stage — intent router: refund query → refund policies, coding → code files**

**Pattern 8: Pointer-Based Retrieval — instead of loading full data use pointers LLM can follow when necessary just like humans recall where to find info rather than memorizing everything**

**Pattern 9: State Projection — injects only necessary context for current step — key criterion for production readiness, unlike traditional prompts agent's context highly dynamic accumulating observations errors intermediate thoughts unmanaged context can lead to bloat increased latency higher costs**

### 14. Anti-Patterns & Failure Mode Fixes

**5 most common mistakes:**

1. Context dumping — including everything rather than relevant info
2. Ignoring context poisoning — hallucination enters and treated ground truth, no validation
3. No summarization strategy — every agent running 10+ turns needs compaction
4. Too many tool definitions — curate 5-8 max load others dynamically via MCP
5. System prompts covering every edge case — aim for principles not scripts
6. Treating window size as feature — 1M-token window ≠ use 1M tokens
7. Dumping entire files into context — retrieve specific lines needed
8. No tool result clearing — old outputs pile up

**Fixes mapping:**

| Failure | Fix Patterns |
|---|---|
| Poisoning | Validate critical facts, quarantine external data, compress with verification, write clean state |
| Distraction | Tiered retrieval, progressive disclosure, offload large outputs, compress rolling window, isolate sub-agents |
| Confusion | Curate 5-8 tools, dynamic loading via MCP, intent-level tools with strong validation, isolate roles |
| Clash | Sub-agent with clean context, squashing failed attempts, quarantines, hierarchical summarization with anchors |

**Context engineering delivers 5-10x improvement vs prompt engineering 2-3x** — key takeaway.

### 15. Measuring Context Quality — 10 Metrics

**Precision >80%** — % of context that is relevant to current step

**Recall >75%** — % of needed info actually retrieved

**Relevance >60%** — semantic relevance score of retrieved chunks

**Utilization >70%** — % of context tokens actually attended to (not ignored)

**Token Efficiency <100k/task** — tokens used per task completion

**Compaction Loss <2%** — critical entities preserved verbatim after summarization

**Overflow <5%** — % tasks hitting context limit

**Lost Middle <10%** — % critical facts lost when placed middle of long context (needle-in-haystack test)

**Stale <3%** — % outdated info in context (e.g., v1.0 not v2.3 policy)

**Cost & Latency** — TTFT and $ per task — every 1K tokens multiplies cost and latency

**Evaluation tests:**

- Needle-in-Haystack: inject critical fact middle 100k tokens, test if model retrieves
- Tool overload: 46 tools vs 19 tools same task — does accuracy drop?
- Long-horizon: 15-20 tool interactions, does agent still perform?
- Multi-turn degradation: same benchmark across multiple turns vs single turn — 39% drop indicates clash

### 16. Full Production Checklist & Implementation

**Checklist for production-ready context engineering:**

1. **Token budgeting:** Budget per component, enforce at runtime, trigger compaction at 80%, buffer 20% insurance, curate 5-8 tools max
2. **Progress files:** progress.json structured JSON not markdown with goal/done/pending/decisions/errors/next_steps, session_handoff.md for next agent
3. **AGENTS.md / CLAUDE.md:** 5-10 rules from failures, pilot checklist, TOC, docs/ references
4. **Memory agent:** Always-On Memory SQLite with 3 subagents Ingest/Consolidate/Query or Mem0/Letta for semantic memory
5. **Retrieval:** Hybrid dense+BM25+reranker+GraphRAG+File Search Tool+contextual compression — reduces failure 30%→8%
6. **Tool progressive disclosure:** Start 5 core tools, dynamic discovery list_skills(intent) returns 3 relevant not 85, saves 80% tokens, MCP for standardization
7. **Offloading:** Save large outputs to file, keep summary + path — saves 60% tokens, squashing failed attempts
8. **Compaction:** Hierarchical L0 raw→L1 turn→L2 session→L3 project, rolling window with anchors, incremental summarization every K turns, preserve entities verbatim, compaction loss <2%
9. **JIT skill routing:** Intent classifier → router → Level 0 always loaded 5k, Level 1 on intent 10k, Level 2 on demand via tool calls
10. **State management:** progress.json + session_handoff.md enables 6-hour agents across sessions
11. **Few-shot dynamic:** Retrieve relevant examples + negative examples + self-generated from past successes — examples > instructions
12. **Security:** PII masking, permission-scoped tools, hierarchy System>Developer>Memory>RAG hooks, no secrets in context
13. **Isolation:** Sub-agent pattern for noisy tasks, fan-out/fan-in for research, quarantines for conflicting data, role isolation planning vs execution vs validation
14. **Evaluation:** Precision >80%, Recall >75%, Relevance >60%, Utilization >70%, Overflow <5%, Lost Middle <10%, Stale <3%, needle-in-haystack test inject critical fact middle 100k
15. **Ratchet:** Every failure → new rule in AGENTS.md, garbage-collection, progress tracking to avoid loops

**Implementation skeleton (Python pseudo):**

```python
class ContextEngineer:
  def __init__(self):
    self.budget = {"system": 4000, "tools": 3000, "rag": 20000, "history": 35000, "working": 40000, "buffer": 25000}
    self.memory = MemoryDB() # Mem0 / SQLite
    self.okf_bundle = OKFLoader("knowledge-bundle/")
    self.mcp_client = MCPClient()
    
  def assemble_context(self, intent, stage):
    context = []
    # Level 0 always
    context.append(self.load_agents_md()) # 5k
    # Level 1 on intent
    if intent == "refund":
      context.append(self.okf_bundle.load(tags=["refund", "policy"])) # 10k
      context.append(self.mcp_client.list_tools(["refund_policy_check", "bundle_validation"]))
    # Level 2 on demand
    # Progressive disclosure, pointers
    return self.enforce_budget(context)
  
  def write(self, data, summary):
    path = f"/tmp/{uuid()}.json"
    save(path, data)
    return {"file_path": path, "summary": summary} # only summary in context
  
  def compress(self, history):
    if len(history.tokens) > 0.75 * MAX_TOKENS:
      summary = cheap_model.summarize(history, keep_anchors=True)
      write_to_file("progress.json", summary)
      return summary + last_n_turns(3)
  
  def isolate(self, subtask, clean_context):
    sub_agent = SubAgent(system_prompt=subtask.role, context=clean_context)
    result = sub_agent.run()
    return result.summary # discard messy thought process
```

**Context as Code:**

Because OKF diffable text fits engineering discipline, metric definitions and runbooks can be updated via PRs, reviewed by owners, rolled back when needed. Turns why did this number change into git blame instead of Slack archaeology. Version-control friendliness enabling detail.

**Final mantra:**

Context engineering marks shift in AI application development from mystical prompt tweaking to rigorous information architecture design. Best context does not contain everything; contains just right critical clues. By managing Agent's RAM through W-S-C-I strategies you can build production-grade AI systems that truly adapt to long-cycle complex scenarios.

From prompt to architecture.
