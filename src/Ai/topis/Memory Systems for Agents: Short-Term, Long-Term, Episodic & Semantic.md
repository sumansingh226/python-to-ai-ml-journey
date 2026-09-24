# Memory Systems for Agents: Short-Term, Long-Term, Episodic & Semantic

> **Core Thesis:** An agent without memory is a goldfish — it re-asks the same questions, forgets what it just did, and can't learn from past failures. Production agents need a memory architecture that mirrors human memory: short-term working memory for the current task, long-term semantic memory for facts, episodic memory for past experiences, and procedural memory for skills.

### Table of Contents
1. [Why Agents Need Memory](#1-why-agents-need-memory)
2. [The 4 Types of Agent Memory](#2-the-4-types-of-agent-memory)
3. [Short-Term / Working Memory](#3-short-term--working-memory)
4. [Long-Term Semantic Memory (RAG)](#4-long-term-semantic-memory-rag)
5. [Episodic Memory (Experience Replay)](#5-episodic-memory-experience-replay)
6. [Procedural Memory (Skills & Tool Mastery)](#6-procedural-memory-skills--tool-mastery)
7. [Memory Management Strategies](#7-memory-management-strategies)
8. [Implementation Blueprint](#8-implementation-blueprint)

---

### 1. Why Agents Need Memory

Context window is not memory. A 128K context window is like a very large desk — you can pile more papers on it, but if you never file anything, you will lose important papers, hit the limit, and slow down.

Problems without memory system:
- **Re-asking:** Agent asks user for order ID it already collected 5 minutes ago in another thread
- **No learning:** Agent fails the same way on same error 100 times, never learns from past failures
- **No personalization:** Doesn't remember user prefers INR, not USD
- **Context bloat:** Keeps entire conversation history forever, hits token limit and cost explodes (compounding problem)

Memory systems solve this by separating what to keep in working context vs what to store in external stores vs what to forget.

### 2. The 4 Types of Agent Memory

Borrowed from cognitive science:

| Type | Human Analogy | Agent Implementation | Retention |
| :--- | :--- | :--- | :--- |
| **Short-Term / Working** | What you're thinking about right now | Current message history + scratchpad | Seconds to minutes, limited to context window |
| **Long-Term Semantic** | Facts about world (Paris is capital of France) | Vector DB (pgvector) + Knowledge Graph | Months to years, explicit facts |
| **Episodic** | Memories of specific experiences (last time I refunded, I needed approval) | Trajectory store in Postgres/ClickHouse with embeddings | Weeks to months, past interactions |
| **Procedural** | Skills you learned (how to ride bike) | Fine-tuned LoRA adapters, prompt templates, tool mastery | Permanent, implicit skills |

Most RAG tutorials only cover semantic memory. Production agents need all four.

### 3. Short-Term / Working Memory

This is the agent's immediate context — what it holds in its prompt right now.

**Components:**
- Recent conversation turns (last 5-10 messages)
- Current scratchpad / chain-of-thought
- Active tool outputs from this trajectory
- Current plan and sub-goals

**Management (ties to Context Caching & Compaction module):**

1.  **Sliding Window:** Keep only last N turns + summary of older turns. E.g., keep last 6 messages verbatim, summarize previous 20 into 200 tokens.
2.  **Scratchpad:** Dedicated field where agent writes intermediate notes: `scratchpad: "User wants refund, but trust score low, need approval. Don't forget to check policy v2.3"`
3.  **Context Compaction:** When approaching token limit, compress tool outputs (e.g., 5000-row SQL result -> summary: "Found 5000 rows, top customer is Acme $50K").

**Anti-pattern:** Dumping entire 100-message history into every LLM call. This causes compounding token cost and degrades reasoning.

**Implementation:**

```python
class WorkingMemory:
    def __init__(self, max_tokens=4000):
        self.recent = deque(maxlen=10) # Last 10 messages verbatim
        self.summary = "" # Compressed older history
        self.scratchpad = {}
    
    def add(self, message):
        self.recent.append(message)
        if self.token_count() > self.max_tokens:
            self.compact()
    
    def compact(self):
        # Summarize oldest 5 into summary via small LLM
        old = [self.recent.popleft() for _ in range(5)]
        self.summary = summarizer_llm(f"Previous summary: {self.summary}\nNew: {old}")
```

### 4. Long-Term Semantic Memory (RAG)

This is factual knowledge about world — your docs, product catalog, policies, user preferences.

**This is RAG.** See `rag_complete_tutorial.md` and `agentic_rag_and_graphrag_full.md` for full implementation.

But for memory architecture, key points:

- **Storage:** pgvector for vectors + Postgres for metadata + ClickHouse for analytics
- **What to store:** Company policies, product specs, user profile (prefers INR, timezone IST), resolved entities
- **Retrieval:** Hybrid search (dense + sparse) + reranking + metadata filtering (e.g., filter by user_id)
- **Write path:** When user says "Remember I prefer INR", extract fact and upsert into semantic memory: `user_preference: currency=INR`

**Example:**

```
User: "My order is in INR"
-> Semantic Memory Write: {"fact": "user prefers INR", "type": "preference", "user_id": "123", "confidence": 0.9}
-> Next time agent retrieves: "User prefers INR" automatically added to context
```

### 5. Episodic Memory (Experience Replay)

This is the most underrated and most powerful for agents. Episodic memory stores *specific past experiences* — full trajectories of past tasks, including failures.

**Why it matters:** When agent encounters new task "Refund ORD-67890", it can search episodic memory: "Have I seen similar refund task before? What did I do? Did it succeed? What was the approval flow?"

This is how humans learn: "Last time I refunded $1200, I needed manager approval and it took 2 days. This one is $1200 too, so I should escalate early."

**Storage:**
- Postgres table: `episodic_memories (id, user_id, task_type, task_input, trajectory, final_state, success, timestamp, embedding)`
- Embedding of task_input + trajectory for similarity search
- ClickHouse for analytics: Which episodes are retrieved most? Which lead to success?

**Retrieval:**
- Given new task, embed it, search episodic memory for top 3 similar past episodes (by embedding similarity)
- Inject summarized episodes into prompt: "Similar past experience: On 2026-08-15, you refunded ORD-11111 for $1000. You escalated to human because amount >500 and it succeeded in 2 hours."

**Write:**
- After each task completes (success or failure), write episode to memory. Include reflection: "What worked? What failed?"
- Use LLM to generate reflection: `reflection_llm("Given trajectory, what lesson should be learned for future similar tasks?")`

**Benefits:**
- Reduces steps: Agent that remembers past approval flow takes 2 steps instead of 5 exploring policy
- Avoids repeated failures: If last 3 refunds with low trust score failed when auto-refunded, agent learns to escalate early
- Personalization: Remembers user-specific patterns

**Example Implementation:**

```python
def handle_new_task(task_input):
    # 1. Search episodic memory
    similar_episodes = episodic_store.search(task_input, k=3, filter={"success": 1})
    
    # 2. Add to context
    context = f"""
    Similar past experiences:
    {format_episodes(similar_episodes)}
    
    Current task: {task_input}
    """
    
    # 3. Execute
    result = agent.run(context)
    
    # 4. Write new episode with reflection
    reflection = reflection_llm(f"Task: {task_input}, Trajectory: {result.trace}, Success: {result.success}. What lesson?")
    episodic_store.add({
        "task_input": task_input,
        "trajectory": result.trace,
        "reflection": reflection,
        "success": result.success,
        "embedding": embed(task_input)
    })
```

### 6. Procedural Memory (Skills & Tool Mastery)

This is implicit knowledge — how to do things, not facts about things. It is baked into model weights or prompt templates, not retrieved.

**Types:**

**a) Fine-Tuned Adapters (LoRA):** Model learns to call your specific tools correctly. This is procedural memory — after fine-tuning, model *knows how* to call `get_order_status` without needing examples. See `fine_tuning_autonomous_agents.md`.

**b) Prompt Templates & Skills Library:** Reusable skill definitions that agent can invoke:

```
Skill: refund_order
  Description: How to process refunds per policy v2.3
  Steps: 1. Check order status 2. Check trust score 3. If amount >500 escalate...
  Tools: [get_order_status, get_trust_score, escalate_to_human]
```

Agent retrieves relevant skill from library based on task (like semantic memory, but for procedures).

**c) Tool Mastery via Self-Play:** Agent practices calling tools in synthetic environment until it masters them, storing mastery as improved prompts or LoRA.

Procedural memory is permanent and doesn't need retrieval at runtime — it's part of agent's weights or core prompts.

### 7. Memory Management Strategies

#### Forgetting: What to Forget

Not all memories are worth keeping forever. Implement:

- **TTL:** Episodic memories older than 90 days with low retrieval count get archived
- **Relevance Scoring:** If memory hasn't been retrieved in last 30 tasks, decay its score
- **Conflict Resolution:** If new fact contradicts old semantic memory (user says "Actually I prefer USD now"), overwrite old fact with new, keep version history

#### Consolidation: From Episodic to Semantic

Over time, repeated episodic memories should be consolidated into semantic facts:

- If 5 episodic memories show "User always asks for INR", consolidate into semantic memory: `user_preference: currency=INR (confidence 0.95, derived from 5 episodes)`

This is like sleep consolidation in humans.

#### Privacy & Compliance

- Semantic and episodic memories contain PII — must be encrypted at rest, with user-level access control
- User can request deletion: Must delete all episodic memories for that user_id (GDPR)
- Don't store tool outputs with secrets in episodic memory — redact first via guardrails

### 8. Implementation Blueprint

Full memory architecture combining all 4 types:

```python
class AgentMemorySystem:
    def __init__(self):
        self.working = WorkingMemory(max_tokens=6000) # Short-term
        self.semantic = PGVectorStore(collection="semantic") # Long-term facts (RAG)
        self.episodic = EpisodicStore(postgres + pgvector) # Past experiences
        self.procedural = SkillLibrary() # Skills + LoRA adapters
    
    def before_task(self, task_input, user_id):
        # 1. Retrieve semantic memory (facts, preferences)
        semantic_facts = self.semantic.search(task_input, filter={"user_id": user_id}, k=5)
        
        # 2. Retrieve episodic memory (similar past tasks)
        episodes = self.episodic.search(task_input, filter={"user_id": user_id, "success": 1}, k=3)
        
        # 3. Retrieve relevant skill (procedural)
        skill = self.procedural.get_relevant_skill(task_input)
        
        # 4. Build enriched context for working memory
        enriched_prompt = f"""
        Semantic Memory (facts):
        {semantic_facts}
        
        Episodic Memory (past experiences):
        {episodes}
        
        Procedural Skill:
        {skill.description}
        
        Current Task: {task_input}
        Working Scratchpad: {self.working.scratchpad}
        """
        return enriched_prompt
    
    def after_task(self, task_input, trajectory, success, user_id):
        # 5. Update working memory
        self.working.add({"task": task_input, "result": trajectory.final})
        
        # 6. Write episodic memory with reflection
        reflection = reflection_llm(trajectory)
        self.episodic.add({
            "user_id": user_id,
            "task_input": task_input,
            "trajectory": trajectory,
            "reflection": reflection,
            "success": success
        })
        
        # 7. Potentially consolidate to semantic
        if self.should_consolidate(user_id):
            facts = consolidation_llm(self.episodic.get_recent(user_id))
            self.semantic.add(facts)

# Usage
memory = AgentMemorySystem()
context = memory.before_task("Refund ORD-12345", user_id="123")
result = agent.run(context)
memory.after_task("Refund ORD-12345", result.trace, result.success, user_id="123")
```

**Tech Stack for Your Stack (Node.js + Postgres + ClickHouse):**
- Working: In-memory + Redis for scratchpad
- Semantic: pgvector (primary) + ClickHouse for analytics on retrieval hit rates
- Episodic: Postgres table + pgvector embedding column + ClickHouse for trajectory analytics
- Procedural: LoRA adapters stored in S3 + Skill definitions in Postgres

---

**Bottom Line:** Memory is what turns a stateless LLM call into a stateful agent that learns, personalizes, and improves. Short-term is your desk, semantic is your filing cabinet, episodic is your diary of experiences, procedural is your muscle memory. Build all four, implement forgetting and consolidation, and your agent stops being a goldfish and starts being a colleague who remembers.

In your curriculum, this module sits after RAG & GraphRAG and before Fine-Tuning, because semantic memory is RAG, episodic memory feeds fine-tuning data, and procedural memory is fine-tuned.

---
*Module: Memory Systems for Agents - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026*
