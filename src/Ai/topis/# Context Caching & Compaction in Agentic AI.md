# Context Caching & Compaction in Agentic AI

## 1. The Long-Horizon Problem
As AI agents move from answering single questions to executing complex workflows (like software engineering or extended research), their conversation history grows exponentially. A session might span hours or weeks, eventually maxing out the model's context window (e.g., 200K or 1M tokens) and driving API costs to unsustainable levels.

To manage this, enterprise architectures rely on two distinct, yet often conflicting, runtime controls: **Context Caching** and **Context Compaction**.

---

## 2. Context Caching (Controlling Cost)
**What it is:** Context caching is a runtime control that allows an agent to pay once to process a large, stable block of context, such as a system prompt, tool schemas, or an entire codebase [cite: 1.2.1]. On subsequent turns, the agent reuses that stored computation, typically at about a tenth of the price [cite: 1.2.1].

* **How it works:** You pay a small premium to write the context block to the cache once [cite: 1.2.1]. As long as the prefix remains byte-for-byte identical on the next API call, you pay a fraction of the cost to read it [cite: 1.2.1].
* **Why it is used:** Without caching, an agent re-sends and re-pays for the entire codebase on every single turn of its loop [cite: 1.2.1]. Caching is currently the single largest cost lever in Agentic AI [cite: 1.2.1].
* **The Catch:** Caching does *not* increase your context window limit [cite: 1.2.1]. A cached token still occupies space in the context window; it just costs less and processes faster [cite: 1.2.1].

---

## 3. Context Compaction (Controlling Space)
**What it is:** When the context window is genuinely full, the agent must reduce its size. Compaction is the process of automatically summarizing or extracting the crucial facts from the conversation history to free up tokens.

* **How it works:** Rather than just dropping old messages, the agent triggers a compaction event. A common best practice is to trigger compaction at roughly 70–75% of the context window limit to avoid "context anxiety" where the model lacks the tokens to write a high-quality summary [cite: 1.2.2].
* **Structured Compaction:** The best architectures use structured templates for compaction, explicitly extracting sections like Active Goals, Key Decisions, and Next Steps, rather than relying on freeform summarization to prevent silent information loss [cite: 1.2.2].
* **External Memory:** Long-lived facts, such as architectural decisions or user preferences, should be explicitly offloaded to an external memory store on write, rather than relying on the compaction summary to capture them retroactively [cite: 1.2.2].

---

## 4. The Architectural Tension
Caching and compaction are in fundamental tension [cite: 1.2.2]. 

* Caching requires the prefix to remain absolutely stable.
* Compaction is a hard semantic break that invalidates all prior cached prefixes [cite: 1.2.2]. 

**The Golden Rule:** Every time a compaction event fires and rewrites the history, it invalidates the cached prefix [cite: 1.2.2]. Therefore, system architects must strictly separate the stable prefix (tool schemas, core instructions) from the volatile conversation history, placing a cache breakpoint between them [cite: 1.2.2]. This ensures that even when the conversation history is compacted, the massive system prefix remains cached and cheap.
