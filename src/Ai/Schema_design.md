# Schema Design for AI Agents — A Practical Guide

> Stack assumed: **LangChain (Node.js) + React.js frontend + PostgreSQL (transactional/vector) + ClickHouse (analytics/logs)**

---

## 1. What "Schema Design" Means in an AI System

In traditional software, schema design is about modeling entities and relationships (users, orders, products). In **AI agent systems**, you're modeling additional entity types that don't exist in classic CRUD apps:

| Traditional Schema | AI Agent Schema (adds) |
|---|---|
| Users, Orders, Products | Conversations, Messages, Agent Runs |
| Foreign keys, indexes | Embeddings (vectors), similarity search |
| CRUD transactions | Tool calls, agent steps, reasoning traces |
| Simple audit logs | Token usage, cost tracking, eval scores |
| Static data | Semi-structured LLM outputs (JSON, variable schema) |

So AI schema design = **modeling the lifecycle of an agent's "thoughts and actions"** (conversation → reasoning → tool calls → memory → output) in a way that's queryable, debuggable, and cost-trackable — split correctly across an **OLTP store (Postgres)** for live state and an **OLAP store (ClickHouse)** for logs/analytics at scale.

### Core building blocks you'll almost always need

1. **Conversation / Session schema** — who talked to what agent, when
2. **Message schema** — the actual turns (user/assistant/tool/system)
3. **Memory schema** — short-term (buffer) and long-term (vector/summary) memory
4. **Agent run / trace schema** — every step an agent takes (thought → action → observation)
5. **Tool / function-call schema** — what tools were invoked, with what args, what result
6. **Embedding / vector schema** — for RAG retrieval
7. **Evaluation & feedback schema** — thumbs up/down, human review, automated scoring
8. **Usage & cost schema** — tokens, latency, model version (usually ClickHouse)

---

## 2. Postgres: Core Transactional Schema (LangChain.js compatible)

Postgres holds **live, mutable, relational state** — the data your Node.js backend reads/writes on every request. Use `pgvector` for embeddings so retrieval and app data live together.

```sql
-- Enable extension for vector search (RAG)
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users / Tenants (multi-tenant SaaS pattern)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    plan TEXT DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 2. Agents (configurable agent definitions — think "assistants")
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id),
    name TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    model TEXT NOT NULL DEFAULT 'claude-sonnet-5',
    tools JSONB DEFAULT '[]',            -- list of tool names/configs enabled
    temperature NUMERIC DEFAULT 0.3,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Conversations (a "session" between a user and an agent)
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id),
    user_id UUID REFERENCES users(id),
    title TEXT,
    status TEXT DEFAULT 'active',        -- active | closed | escalated
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_conversations_user ON conversations(user_id);

-- 4. Messages (chat turns — matches LangChain BaseMessage shape)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('system','user','assistant','tool')),
    content TEXT,
    tool_call_id TEXT,                   -- links tool result -> tool call
    tool_calls JSONB,                    -- [{name, args, id}] if assistant requested tools
    token_count INT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);

-- 5. Long-term memory / vector store (RAG knowledge base per org)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id),
    source TEXT,                         -- e.g. 'confluence', 'pdf-upload', 'website'
    content TEXT NOT NULL,
    embedding VECTOR(1536),              -- match your embedding model dims
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_documents_embedding ON documents
    USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 6. Agent memory summaries (LangChain ConversationSummaryMemory pattern)
CREATE TABLE conversation_summaries (
    conversation_id UUID PRIMARY KEY REFERENCES conversations(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    last_message_id UUID REFERENCES messages(id),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 7. Human feedback (RLHF-lite / product quality loop)
CREATE TABLE message_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id),
    rating SMALLINT CHECK (rating IN (-1, 1)),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

**Why Postgres for this layer:** it's transactional (a message write must succeed atomically with a conversation update), relationally constrained (foreign keys keep integrity), and `pgvector` gives you RAG retrieval without a separate vector DB for small-to-mid scale (< ~5M vectors comfortably; beyond that, consider Pinecone/Qdrant/Weaviate, but keep the *pointer* schema in Postgres).

---

## 3. ClickHouse: Observability, Traces & Analytics Schema

Agent systems generate **huge, append-only, time-series event volumes** (every LLM call, every tool call, every token). This is a terrible fit for Postgres at scale — it's a perfect fit for ClickHouse.

```sql
-- 1. Agent run traces (every top-level invocation of an agent)
CREATE TABLE agent_runs (
    run_id UUID,
    conversation_id UUID,
    agent_id UUID,
    org_id UUID,
    started_at DateTime64(3),
    ended_at DateTime64(3),
    status Enum8('success' = 1, 'error' = 2, 'timeout' = 3),
    input_tokens UInt32,
    output_tokens UInt32,
    total_cost_usd Decimal(10, 6),
    model String,
    latency_ms UInt32,
    error_message Nullable(String)
) ENGINE = MergeTree()
ORDER BY (org_id, started_at)
PARTITION BY toYYYYMM(started_at);

-- 2. Agent steps (LangChain AgentExecutor intermediate_steps — the "trace")
-- One row per Thought -> Action -> Observation cycle
CREATE TABLE agent_steps (
    step_id UUID,
    run_id UUID,
    step_index UInt16,
    step_type Enum8('thought' = 1, 'tool_call' = 2, 'observation' = 3, 'final_answer' = 4),
    tool_name Nullable(String),
    tool_input Nullable(String),
    tool_output Nullable(String),
    duration_ms UInt32,
    timestamp DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (run_id, step_index)
PARTITION BY toYYYYMM(timestamp);

-- 3. Raw event stream (every LLM API call, for cost/latency analytics)
CREATE TABLE llm_events (
    event_id UUID,
    run_id UUID,
    org_id UUID,
    model String,
    prompt_tokens UInt32,
    completion_tokens UInt32,
    cost_usd Decimal(10, 6),
    latency_ms UInt32,
    cache_hit UInt8,
    timestamp DateTime64(3)
) ENGINE = MergeTree()
ORDER BY (org_id, timestamp)
PARTITION BY toYYYYMM(timestamp)
TTL timestamp + INTERVAL 90 DAY;  -- auto-expire raw logs after 90 days

-- 4. Materialized view: daily cost/usage rollup per org (fast dashboards)
CREATE MATERIALIZED VIEW daily_usage_mv
ENGINE = SummingMergeTree()
ORDER BY (org_id, day)
AS SELECT
    org_id,
    toDate(timestamp) AS day,
    count() AS requests,
    sum(prompt_tokens) AS total_prompt_tokens,
    sum(completion_tokens) AS total_completion_tokens,
    sum(cost_usd) AS total_cost_usd
FROM llm_events
GROUP BY org_id, day;
```

**Why ClickHouse for this layer:** columnar storage + `MergeTree` gives you sub-second aggregation over billions of rows ("what's our p95 latency and cost per org, last 30 days"), which Postgres chokes on at volume. Keep **operational, foreign-keyed data in Postgres**, and **high-volume, append-only events in ClickHouse**. Link them by `run_id` / `conversation_id` (UUIDs shared across both stores).

---

## 4. LangChain.js Integration Notes

```js
// Example: PostgresChatMessageHistory maps directly onto the `messages` table above
import { PostgresChatMessageHistory } from "@langchain/community/stores/message/postgres";

const chatHistory = new PostgresChatMessageHistory({
  sessionId: conversationId,   // -> conversations.id
  pool: pgPool,
  tableName: "messages",       // reuse the schema above with LangChain's expected columns
});

// Example: PGVectorStore maps onto the `documents` table for RAG
import { PGVectorStore } from "@langchain/community/vectorstores/pgvector";

const vectorStore = await PGVectorStore.initialize(embeddings, {
  pool: pgPool,
  tableName: "documents",
  columns: {
    idColumnName: "id",
    contentColumnName: "content",
    vectorColumnName: "embedding",
    metadataColumnName: "metadata",
  },
});
```

Emit `agent_runs` / `agent_steps` rows from your `AgentExecutor` callbacks (`handleAgentAction`, `handleToolEnd`, `handleLLMEnd`) and batch-insert into ClickHouse asynchronously (don't block the response path on analytics writes).

---

## 5. Industry-Based Examples

### 🛒 E-commerce — Product Recommendation Agent

**Need:** agent that answers "what shoes go with this jacket," calls a product-search tool, remembers user preferences across sessions.

- `agents` row: `system_prompt` = styling assistant persona, `tools` = `["search_products","get_user_purchase_history"]`
- `documents` table stores product catalog embeddings (RAG over product descriptions)
- Extra table:
```sql
CREATE TABLE user_preferences (
    user_id UUID REFERENCES users(id),
    preference_key TEXT,     -- 'preferred_color', 'size', 'brand_affinity'
    preference_value TEXT,
    confidence NUMERIC,      -- inferred confidence from agent, 0-1
    updated_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, preference_key)
);
```
- ClickHouse tracks `tool_name = 'search_products'` frequency → feeds a "trending searches with no results" dashboard for merchandising.

---

### 🏥 Healthcare — Clinical Intake Assistant

**Need:** strict auditability, PII isolation, human-in-the-loop review before any clinical suggestion reaches a patient.

- Separate **PII vault** table, encrypted at rest, referenced by ID only (never joined into logs):
```sql
CREATE TABLE patient_pii (
    patient_id UUID PRIMARY KEY,
    encrypted_name BYTEA,
    encrypted_dob BYTEA,
    -- decryption happens in app layer only, with access logging
);

CREATE TABLE clinical_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patient_pii(patient_id),
    requires_human_review BOOLEAN DEFAULT true,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);
```
- **Every** `agent_steps` row where `tool_name` touches a clinical database gets flagged `requires_human_review = true` — no auto-send to patient.
- ClickHouse `llm_events` table adds a `phi_redacted UInt8` column — compliance dashboards prove no raw PHI hit the LLM prompt.

---

### 🏦 Fintech — Fraud-Triage Agent

**Need:** agent investigates a flagged transaction, calls internal risk-scoring tools, produces a structured decision, fully auditable for regulators.

```sql
CREATE TABLE fraud_investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    transaction_id UUID NOT NULL,
    run_id UUID,                          -- links to ClickHouse agent_runs
    decision TEXT CHECK (decision IN ('approve','deny','escalate')),
    decision_reason TEXT,
    risk_score NUMERIC,
    model_version TEXT NOT NULL,          -- REQUIRED for regulatory reproducibility
    created_at TIMESTAMPTZ DEFAULT now()
);
```
- `model_version` and full `agent_steps` trace are mandatory — regulators require you to reconstruct *why* a decision was made, months later.
- ClickHouse `agent_steps` gives sub-second query: "show every step where `tool_name = 'check_sanctions_list'` failed in the last 24h."

---

### 🎧 SaaS — Customer Support Copilot

**Need:** agent drafts replies to support tickets, escalates to humans, learns from edited replies.

```sql
CREATE TABLE support_tickets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id),
    status TEXT DEFAULT 'open',
    escalated BOOLEAN DEFAULT false,
    csat_score SMALLINT
);

-- Track human edits to AI drafts — this is your fine-tuning gold data
CREATE TABLE draft_edits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id),
    original_draft TEXT NOT NULL,
    edited_final TEXT NOT NULL,
    editor_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);
```
- ClickHouse rollup: `edit_distance(original_draft, edited_final)` trend over time = objective measure of agent quality improvement.

---

## 6. Design Principles Checklist

- [ ] **Separate hot/live state (Postgres) from append-only event logs (ClickHouse).** Don't put trace-level logging in Postgres — it'll bloat and slow your transactional tables.
- [ ] **Use UUIDs everywhere** so IDs correlate across Postgres and ClickHouse without collision.
- [ ] **Store `model_version` on every agent-generated row.** LLM behavior changes between model versions; without this, you can't debug regressions.
- [ ] **JSONB for variable LLM output, real columns for anything you filter/aggregate on.** Don't over-normalize tool call args; do normalize cost/tokens/status.
- [ ] **Design for redaction.** PII should be isolatable/deletable independent of conversation history (GDPR "right to be forgotten").
- [ ] **Partition ClickHouse by month + org** for both fast queries and easy data retention/TTL policies.
- [ ] **Keep a `tool_calls` audit trail** — this is your primary debugging tool when an agent misbehaves.
- [ ] **Version your `agents` table** (system prompts change often) — consider `agent_versions` if you need rollback/A-B testing.

---

## 7. Suggested Repo Structure (Node.js + LangChain)

```
/db
  /migrations         -- Postgres migrations (Drizzle/Knex/Prisma)
  /clickhouse          -- ClickHouse DDL scripts
/src
  /agents              -- LangChain agent definitions
  /memory              -- PostgresChatMessageHistory wrappers
  /tools               -- tool implementations + JSON schemas
  /observability        -- ClickHouse event emitters (async, non-blocking)
  /api                 -- Express/Fastify routes consumed by React frontend
```

---

*This schema is a starting template — scale/compliance requirements (HIPAA, SOC2, PCI-DSS) will require additional constraints (encryption, row-level security, retention policies) beyond what's shown here.*