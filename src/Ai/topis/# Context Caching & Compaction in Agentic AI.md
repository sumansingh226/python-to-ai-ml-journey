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
