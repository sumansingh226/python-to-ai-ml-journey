# Agent Economics, Pricing & ROI: Making Agents Profitable
## From Cost Center to Profit Center

> **Core Thesis:** Most agent demos lose money — $0.50 per task with 80% success = negative ROI. Profitable agents need unit economics, pricing models, and ROI measurement that treats agents as employees, not features. The goal is $0.12 cost, 92% success, $5.00 value per task = 40x ROI.

### Table of Contents
1. [Unit Economics of Agents](#1-unit-economics-of-agents)
2. [Cost Breakdown](#2-cost-breakdown)
3. [Pricing Models](#3-pricing-models)
4. [ROI Measurement](#4-roi-measurement)
5. [The Path to 40x ROI](#5-the-path-to-40x-roi)
6. [Production Checklist](#6-production-checklist)

---

### 1. Unit Economics of Agents

**Formula:**

```
Value per task = Human cost saved + Revenue generated + Error reduction value
Cost per task = LLM cost + Tools cost + Infra cost + Human oversight cost
ROI = (Value - Cost) / Cost

Example Support Bot:
Value = $4.50 (human agent 10 min @ $27/hr) + $0.50 (CSAT improvement) = $5.00
Cost = $0.12 (LLM with cascade + caching) + $0.02 (Stripe API) + $0.01 (infra) + $0.05 (5% needs human) = $0.20
ROI = (5.00 - 0.20) / 0.20 = 24x
```

**Without optimization:**
Cost = $0.58 (no cascade, no caching) + $0.10 = $0.68
ROI = (5.00 - 0.68) / 0.68 = 6.3x — still profitable but 4x less

**With failure:**
If success rate 70%, 30% needs human redo = cost doubles + value lost
Effective ROI drops to 2x

### 2. Cost Breakdown

**LLM Cost (70% of total):**

- Prompt Caching saves 80% on stable prefix (system + tools + codebase 50K)
- Model Cascades saves 60-80%: Tier 1 70% calls @ $0.05, Tier 2 20% @ $0.50, Tier 3 10% @ $10
- Tool Result Caching saves 20% tool calls
- Average: $0.58 -> $0.12 per task

**Tool Cost (15%):**

- Stripe 2c per call, Email 0.5c, etc.
- Cache idempotent reads

**Infra (5%):**

- Postgres + pgvector + ClickHouse + Redis + K8s workers

**Human Oversight (10%):**

- 5% tasks need approval -> human 2 min @ $30/hr = $1.00, amortized = $0.05 per task average

### 3. Pricing Models

**a) Seat-based:** $99/agent/month — simple but doesn't scale with usage

**b) Usage-based:** $0.50 per successful task — aligns with value, best for enterprise

**c) Outcome-based:** $2.00 per refund processed, 10% of savings — highest value alignment, hardest to measure

**d) Hybrid:** $199/month base + $0.20 per task over 1000 — most common in 2026

**Recommendation:** Start usage-based, move to outcome-based once you have ROI data.

### 4. ROI Measurement

**Need to measure:**

- Success rate: % tasks completed without human intervention
- Time saved: Human minutes saved per task (via time tracking)
- Error rate: % tasks with errors vs human baseline
- Cost per task: From ClickHouse traces

**Dashboard:**

```sql
SELECT 
  date,
  count(*) as tasks,
  avg(cost_usd) as cost_per_task,
  avg(success) as success_rate,
  sum(human_minutes_saved) as total_minutes_saved,
  sum(human_minutes_saved)*27/60 as value_saved -- $27/hr
FROM agent_trajectories
GROUP BY date
```

### 5. The Path to 40x ROI

**Step 1: Reduce cost $0.58 -> $0.12**

- Prompt caching (80% saving on prefix)
- Cascades (70% calls to SLM)
- Tool caching (20% saving)

**Step 2: Increase success 70% -> 92%**

- Reflexion + episodic memory (70% -> 90%)
- Fine-tuning 8B on function calling (85% -> 95% tool accuracy)
- Structured outputs 99.9% valid

**Step 3: Increase value $5 -> $10**

- Add upsell/cross-sell capability
- Proactive outreach (agent identifies at-risk customers)
- 24/7 availability (human not available)

**Result:** Cost $0.12, Value $10, ROI = (10 - 0.12)/0.12 = 82x

### 6. Production Checklist

1.  Measure baseline human cost per task (time + error rate)
2.  Instrument cost per task in ClickHouse (LLM + tools + infra + human)
3.  Implement prompt caching + cascades + tool caching -> target $0.12/task
4.  Implement Reflexion + episodic memory + FT -> target 92% success
5.  Start with usage-based pricing $0.50/successful task
6.  Build ROI dashboard: tasks, cost/task, success rate, value saved, ROI
7.  Move to outcome-based once ROI proven: 10% of savings
8.  Report ROI monthly to stakeholders

---

**Bottom Line:** Agents are employees, not features — measure them like employees. Track cost per task, success rate, time saved, and ROI. Optimize cost via caching + cascades ($0.58->$0.12), success via Reflexion + FT (70%->92%), value via proactive capabilities ($5->$10). This is how you get 40-80x ROI and justify scaling to 10K tasks/day.

In your curriculum, this is the final capstone after Legal & Compliance, because you need to prove profitability to get budget for compliance.

---
