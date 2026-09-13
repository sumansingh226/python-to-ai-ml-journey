# Context Caching & Compaction in Agentic AI

## 1. The Long-Horizon Problem
As AI agents move from answering single questions to executing complex workflows (like software engineering or extended research), their conversation history grows exponentially. A session might span hours or weeks, eventually maxing out the model's context window (e.g., 200K or 1M tokens) and driving API costs to unsustainable levels.

To manage this, enterprise architectures rely on two distinct, yet often conflicting, runtime controls: **Context Caching** and **Context Compaction**.

---