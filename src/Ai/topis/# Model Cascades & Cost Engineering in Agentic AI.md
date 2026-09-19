
## 3. Tiered Model Cascades: Designing the Hierarchy

A robust model cascade organizes language models into three functional tiers:

### Tier 1: Local / Edge SLMs (Sub-second, Minimal Cost)
* **Models:** Llama 3.2 (1B–3B), Phi-3.5 Mini, Mistral NeMo.
* **Role:** High-throughput, deterministic tasks:
  * Input classification & intent detection.
  * Schema extraction & formatting.
  * Deterministic regex generation.
  * Prompt sanitization & PII redaction.

### Tier 2: Mid-Tier Workhorses (Balanced Latency & Reasoning)
* **Models:** GPT-4o-mini, Claude 3.5 Haiku, Gemini 1.5 Flash.
* **Role:** Core sub-goal execution:
  * Tool argument generation.
  * Data summarization and retrieval parsing.
  * Peer review and basic reflection.

### Tier 3: Frontier Reasoning Engines (High Compute, Deep Planning)
* **Models:** Claude 3.5 Sonnet, GPT-4o, OpenAI o1 / o3, Gemini 1.5 Pro.
* **Role:** High-order cognitive governance:
  * Initial task decomposition and global planning.
  * Fallback reasoning when Tier 2 models fail or get stuck.
  * Final synthesis of multi-agent debates.

---