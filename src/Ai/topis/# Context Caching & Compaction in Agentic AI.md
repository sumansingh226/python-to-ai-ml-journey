# Context Caching & Compaction in Agentic AI
## Controlling Cost vs. Controlling Space in Long-Horizon Agents

> **Core Thesis:** In long-horizon agentic workflows, Context Caching is your cost control, and Context Compaction is your space control. They solve different problems and are architecturally in tension. Mastering their separation is the key to sustainable enterprise agents.

### Table of Contents
1. [The Long-Horizon Problem](#1-the-long-horizon-problem)
2. [Context Caching: Controlling Cost](#2-context-caching-controlling-cost)
3. [Context Compaction: Controlling Space](#3-context-compaction-controlling-space)
4. [The Architectural Tension](#4-the-architectural-tension)
5. [The Golden Rule: Stable vs. Volatile Context](#5-the-golden-rule-stable-vs-volatile-context)
6. [Production Implementation Blueprint](#6-production-implementation-blueprint)
7. [Common Anti-Patterns](#7-common-anti-patterns)
8. [Decision Framework](#8-decision-framework)

---

### 1. The Long-Horizon Problem

As AI agents move from answering single questions to executing complex workflows like software engineering, deep research, or multi-day customer onboarding, their conversation history grows exponentially.

A single agent loop might look like:
`User Goal -> Plan -> Tool Call -> Tool Output -> Reflection -> Tool Call -> Tool Output ... -> Final Answer`

After 50-100 turns, this history can easily exceed 150K tokens. A session might span hours or weeks, eventually maxing out the model's context window (e.g., 200K or 1M tokens) and driving API costs to unsustainable levels.

Two hard limits hit you at once:
1.  **Cost Limit:** You pay for all input tokens on every turn. If you send a 50K codebase + 50K history on every turn for 100 turns, you pay for 10M tokens.
2.  **Space Limit:** The model physically cannot accept more tokens than its window. You get a hard `context_length_exceeded` error.

To manage this, enterprise architectures rely on two distinct, yet often conflicting, runtime controls: **Context Caching** and **Context Compaction**.

### 2. Context Caching: Controlling Cost

#### What it is
Context caching is a runtime control that allows an agent to pay once to process a large, stable block of context, such as a system prompt, tool schemas, or an entire codebase. On subsequent turns, the agent reuses that stored computation, typically at about a tenth of the price.

It is currently the single largest cost lever in Agentic AI.

#### How it works
LLMs process prompts with a KV-cache. Caching exposes this at the API level.

1.  **Write:** You pay a small premium (e.g., 1.25x) to write a context block to the cache once. For example, you mark your system prompt + tool definitions + codebase as cacheable.
2.  **Read:** As long as the prefix remains byte-for-byte identical on the next API call, you pay a fraction of the cost to read it (e.g., 0.1x). The computation is skipped.
3.  **TTL:** The cache typically lives for 5-60 minutes and is refreshed on each hit.

#### Why it is used
Without caching, an agent re-sends and re-pays for the entire codebase on every single turn of its loop. With caching, turn 1 is expensive, but turns 2-100 are 90% cheaper for that stable prefix.

**Example Cost Model (100-turn coding agent):**
- Without Cache: 100 turns * (50K codebase + 20K avg history) = 7M input tokens
- With Cache: 1 * 50K cached write + 99 * 50K cached read (0.1x) + history cost = ~1.2M effective tokens. ~80% saving.

#### The Catch
Caching does *not* increase your context window limit. A cached token still occupies space in the context window; it just costs less and processes faster. It solves cost, not space. It also requires absolute prefix stability. Add one character to the beginning, and the entire cache is invalidated.

### 3. Context Compaction: Controlling Space

#### What it is
When the context window is genuinely full, the agent must reduce its size. Compaction is the process of automatically summarizing or extracting the crucial facts from the conversation history to free up tokens. It is a lossy compression.

#### How it works
Rather than just dropping old messages (naive truncation), the agent triggers a compaction event.

**Best Practice - Trigger Early:**
Trigger compaction at roughly 70-75% of the context window limit to avoid "context anxiety" where the model lacks the tokens to write a high-quality summary. If you wait until 95%, the model does not have enough output tokens left to produce a good summary, leading to catastrophic information loss.

**Best Practice - Structured Compaction:**
The best architectures use structured templates for compaction, explicitly extracting sections rather than relying on freeform summarization to prevent silent information loss.

**Structured Compaction Template:**
```markdown
# Conversation Summary - Compacted at [timestamp]
## Active Goals:
- Primary objective and current sub-goal

## Key Decisions & Rationale:
- Decision 1: Chose library X because Y

## Important Facts & Artifacts Created:
- File paths, API keys (redacted), user preferences

## Conversation History (Summarized):
- [Turns 1-45]: Agent tried approach A, failed because...

## Next Steps:
- What was about to be done next

## Open Questions:
```

This structured format forces the model to preserve actionable state.

**Best Practice - External Memory:**
Long-lived facts, such as architectural decisions or user preferences, should be explicitly offloaded to an external memory store on write, rather than relying on the compaction summary to capture them retroactively. Write to memory as soon as you learn it, do not hope compaction will remember it.

Compaction Strategies:
- **Summarization:** LLM summarizes old turns
- **Extraction:** LLM extracts facts/entities only
- **Rolling Window + Summary:** Keep last N turns verbatim, summarize the rest
- **Hierarchical:** Summarize summaries for very long horizons

### 4. The Architectural Tension

Caching and compaction are in fundamental tension.

*   Caching requires the prefix to remain absolutely stable. Any change invalidates it.
*   Compaction is a hard semantic break that invalidates all prior cached prefixes. When you rewrite the history with a summary, the byte-for-byte prefix is gone.

If you naively place everything in one big cache block:
`[System Prompt + Codebase + Conversation History]` <- cached

And then you compact the conversation history, you rewrite that block. The next call has a different prefix, so the entire cache misses. You lose the benefit of caching your massive 50K codebase, which was the whole point.

This creates a performance cliff: Right when your agent is longest-running (and needs caching the most), compaction fires and makes it expensive again.

### 5. The Golden Rule: Stable vs. Volatile Context

**The Golden Rule:** Every time a compaction event fires and rewrites the history, it invalidates the cached prefix. Therefore, system architects must strictly separate the stable prefix from the volatile conversation history, placing a cache breakpoint between them.

This ensures that even when the conversation history is compacted, the massive system prefix remains cached and cheap.

**Correct Architecture:**

```
[--- CACHE BLOCK 1: STABLE PREFIX (Cached, Rarely Changes) ---]
- System Prompt
- Agent Core Instructions
- Tool Schemas / Tool Definitions
- Codebase / Knowledge Base / Large Static Docs
[--- CACHE BREAKPOINT ---]

[--- VOLATILE HISTORY (Not Cached, or Cached Separately, Frequently Compacted) ---]
- Compacted Summary of Turns 1-80 (this gets rewritten)
- Recent Turns 81-100 (verbatim)
- Current User Message
```

Implementation:
- In Anthropic Claude, use `cache_control` breakpoints.
- In Gemini, use `cachedContent` for the stable part only.
- In OpenAI, use Prompt Caching automatically handles stable prefixes, but you must ensure stable content comes first.

**Rule of Thumb:** If it changes less than once per hour, put it in the stable cached prefix. If it changes every turn, keep it out.

### 6. Production Implementation Blueprint

```python
# Pseudocode for a production agent loop

STABLE_CONTEXT = load_system_prompt() + load_tool_schemas() + load_codebase()
CACHE_TTL = 60 # minutes

def agent_loop(user_goal):
    conversation_history = []
    external_memory = VectorDB()
    
    while not done:
        # Check if we need to compact
        total_tokens = count_tokens(STABLE_CONTEXT + conversation_history)
        if total_tokens > 0.75 * MAX_WINDOW:
            summary = llm_compact(
                template=STRUCTURED_TEMPLATE,
                history=conversation_history,
                memory=external_memory
            )
            conversation_history = [summary] + conversation_history[-10:] # Keep last 10 verbatim
            # NOTE: This invalidates only the history part, STABLE_CONTEXT cache remains valid

        # Build request with explicit cache breakpoint
        response = llm_call(
            messages=[
                {"role": "system", "content": STABLE_CONTEXT, "cache_control": {"type": "ephemeral"}}, # Cached Block
                {"role": "user", "content": conversation_history} # Volatile Block
            ]
        )
        
        # Execute tools, append to history, offload important facts
        # ...
```

### 7. Common Anti-Patterns

1.  **Caching Everything:** Putting the entire conversation history in the cache. Every turn invalidates it. No savings.
2.  **Late Compaction:** Waiting until 95% full. Leads to truncated, low-quality summaries.
3.  **Freeform Summarization:** "Summarize the conversation so far." Loses critical IDs, file paths, and decisions.
4.  **Hope-Based Memory:** Assuming compaction will remember user preferences. It will not. Explicitly write to external memory.
5.  **Ignoring Breakpoints:** Not using cache breakpoints, so a single changed character invalidates a 100K codebase cache.

### 8. Decision Framework

| Situation | Solution |
| :--- | :--- |
| Cost is too high, window is fine | Add Context Caching for stable prefix |
| Window is full, cost is fine | Add Context Compaction with structured template |
| Both cost and window are problems | Implement Golden Rule: Separate stable cached prefix + volatile compacted history |
| Need long-term personalization | Add External Memory Store, do not rely on context at all |

**Final Principle:** Treat context as a tiered storage system. Cache is your L1 (fast, cheap, stable), Conversation History is your RAM (volatile, limited), Compaction is your garbage collector, and External Memory is your disk (persistent, explicit).

---
