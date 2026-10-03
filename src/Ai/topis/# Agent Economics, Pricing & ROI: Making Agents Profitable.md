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
