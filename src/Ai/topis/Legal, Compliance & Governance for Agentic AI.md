# Legal, Compliance & Governance for Agentic AI
## SOC2, GDPR, Liability, and Audit-Ready Agents

> **Core Thesis:** An agent that can send emails, refund money, and access PII is not just a feature — it's a regulated actor. When it hallucinates a refund or leaks another user's data, you are liable. Compliance is not a checkbox after building; it's architecture — memory deletion, audit logs, policy versioning, and human-in-the-loop gates that prove to auditors what happened.

### Table of Contents
1. [Why Agents Create New Legal Risk](#1-why-agents-create-new-legal-risk)
2. [GDPR & Data Privacy for Agents](#2-gdpr--data-privacy-for-agents)
3. [SOC2 & Audit Requirements](#3-soc2--audit-requirements)
4. [Liability & Accountability](#4-liability--accountability)
5. [Policy Versioning & Prove-It Problem](#5-policy-versioning--prove-it-problem)
6. [Implementation Blueprint](#6-implementation-blueprint)
7. [Production Checklist](#7-production-checklist)

---

### 1. Why Agents Create New Legal Risk

Traditional software: Deterministic code, same input → same output, easy to audit.

Agent: Non-deterministic LLM + tools + memory that can:
- Leak PII from one user's episodic memory to another user (missing access control)
- Hallucinate refund policy and refund $10K when policy says $500 max
- Retain data after GDPR deletion request because it lives in pgvector semantic memory
- Send email from your domain that is defamation — who is liable?

New risks:
- **Data Retention:** Agent memory (semantic, episodic) stores PII beyond intended retention
- **Cross-User Contamination:** Shared pgvector without user_id filter → User A sees User B's data
- **Autonomous Actions:** Agent refunds without approval — financial compliance violation
- **Audit Trail:** Auditor asks "Why did agent refund $1200 on 2026-08-01?" — can you prove which policy version, which tools, which human approved?

### 2. GDPR & Data Privacy for Agents

**Right to be Forgotten:** User requests deletion — you must delete from:
- Postgres (OLTP) — easy
- pgvector (semantic memory) — need to delete embeddings for that user_id
- Episodic memory (trajectories) — delete trajectories
- ClickHouse (analytics) — anonymize or delete
- LLM training data — if you fine-tuned on user data, need to retrain or use machine unlearning
- External tools — if you sent PII to Stripe, need to request deletion there too

**Implementation:**

```python
def gdpr_delete(user_id):
    # 1. Postgres
    pg.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    pg.execute("DELETE FROM agent_trajectories WHERE user_id=%s", (user_id,))
    
    # 2. pgvector - semantic memory
    pgvector.delete(filter={"user_id": user_id})
    
    # 3. Redis - working memory
    redis.delete(f"scratchpad:{user_id}")
    
    # 4. ClickHouse - anonymize
    clickhouse.execute("ALTER TABLE traces UPDATE user_id='DELETED' WHERE user_id=%s", (user_id,))
    
    # 5. Audit log
    audit.log(action="gdpr_delete", user_id=user_id, timestamp=now(), policy_version="v2.3")
```

**Data Minimization:** Don't store raw PII in memory. Store redacted version. Example: Store `email: ***@gmail.com` not full email, unless needed for tool.

**Access Control:** Every memory read must filter by user_id:

```python
# WRONG - leaks other users' data
results = pgvector.search(query_emb)

# CORRECT - scoped to user
results = pgvector.search(query_emb, filter={"user_id": current_user_id})
```

### 3. SOC2 & Audit Requirements

SOC2 requires you to prove:
- **Who did what, when:** Every tool call logged with user_id, agent_id, timestamp, policy_version
- **What policy was in effect:** Policy version pinned to trajectory
- **Who approved high-risk actions:** Human approval gate logs with approver_id, reason
- **Data retention:** How long you keep trajectories, how you delete

**Audit Log Schema:**

```sql
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY,
  task_id TEXT,
  user_id TEXT,
  agent_id TEXT,
  action TEXT, -- tool_call, approval, memory_write
  tool_name TEXT,
  tool_args JSONB,
  policy_version TEXT, -- v2.3
  guardrail_verdict TEXT, -- pass, deny
  cost_usd FLOAT,
  timestamp TIMESTAMPTZ,
  trace_id TEXT -- OTel trace
);
```

**Immutable Logs:** Use ClickHouse with `ReplicatedMergeTree` — append-only, can't be modified. Auditor trusts it.

### 4. Liability & Accountability

**When agent does wrong, who is liable?**

- If agent refunds $10K due to hallucination and no human approval gate → Company liable (excessive agency)
- If agent leaks PII due to missing access control → Company liable (negligence)
- If agent sends defamatory email → Company liable (publisher)

**Mitigations:**
- Hard Approval Gates for high-value actions (> $500, PII external, delete) — proves human in loop
- Policy Engine as deterministic layer — proves you enforced policy, not just LLM
- Disclaimer in UI: "AI-generated, verify before acting" — but not enough alone, need technical controls

### 5. Policy Versioning & Prove-It Problem

From Guardrails module: Auditor asks "Why did you refund $500 on Aug 1?"

You must prove:
- Policy v2.3 was in effect on Aug 1 (which says refund <500 auto, >500 needs approval)
- Agent checked trust_score (85) via tool
- No approval needed per policy
- Cost $0.12

**Implementation:**

```python
# Every trajectory stores policy_version
trajectory = {
  "task_id": "task_123",
  "policy_version": "v2.3", # Pinned at time of execution
  "policy_dag_hash": "sha256:abc...", # Hash of DAG JSON
  "steps": [...],
  "approval": None # or {approver_id, timestamp, reason}
}

# Policy versions stored immutably
CREATE TABLE policy_versions (
  version TEXT PRIMARY KEY,
  dag_json JSONB,
  dag_hash TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  created_by TEXT
);
```

Now you can replay: "On Aug 1, policy v2.3 effective, which says..."

### 6. Implementation Blueprint

Full compliance architecture:

```python
# 1. Access control on every memory access
def memory_search(user_id, query_emb):
    return pgvector.search(query_emb, filter={"user_id": user_id})

# 2. Policy version pinned to every task
def execute_task(task_id, user_id):
    policy = get_active_policy_version() # v2.3
    state = {"policy_version": policy.version, "policy_hash": policy.hash}
    
    # 3. All tool calls go through audit log
    def audited_tool_call(tool_name, args):
        result = tool.execute(args)
        audit.log(
            task_id=task_id,
            user_id=user_id,
            tool_name=tool_name,
            tool_args=redact_pii(args),
            policy_version=policy.version,
            trace_id=otel_trace_id
        )
        return result
    
    # 4. Hard approval gate for high-risk
    if amount > 500:
        serialize_and_wait_for_approval(task_id, reason=f"Amount {amount} >500")
        audit.log(action="approval_requested", task_id=task_id, reason="high_value")
    
    # 5. GDPR delete handler
    # As above

# 6. Retention policy
# Delete trajectories after 90 days, keep audit logs for 7 years
```

### 7. Production Checklist

1.  **GDPR delete deletes from ALL stores** — Postgres, pgvector, Redis, ClickHouse, fine-tune data
2.  **Access control on every memory read** — filter by user_id, never global search
3.  **Immutable audit logs** in ClickHouse — append-only, with policy_version, tool_args, approver_id
4.  **Policy versioning** — every trajectory pinned to policy version + hash, store versions immutably
5.  **Hard Approval Gates** for high-risk actions — proves human in loop for auditors
6.  **Data minimization** — redact PII before memory write, store hashed or masked
7.  **Retention policy** — trajectories 90 days, audit logs 7 years, document it
8.  **Disclaimer + technical controls** — disclaimer alone not enough, need approval gates + policy engine
9.  **SOC2 evidence** — quarterly export of audit logs, policy versions, approval logs for auditor
10. **Liability insurance** — get AI liability insurance for autonomous actions

---

**Bottom Line:** Agents are regulated actors that store PII, take autonomous financial actions, and generate content you are liable for. Build GDPR deletion that cleans all stores, access control on every memory read, immutable audit logs with policy version pinned, and hard approval gates for high-risk actions. This is how you prove to auditors and courts that you acted responsibly — not just "the LLM did it."

In your curriculum, this module sits after Security & Deployment, because compliance is the final gate before production.

---
