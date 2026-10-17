Product & Business for Agentic AI: Pricing, Customer Support, Sales, Coding, Research, Benchmarks
Complete Production Guide - From Pricing Models to Real-World Agent Case Studies
> **Core Thesis:** Building agentic products is 20% model, 80% product and business. Pricing per-seat vs per-task vs per-outcome changes incentives. Customer Support refund agent is the canonical end-to-end case study: policy + tools + trust + approval + GraphRAG. Sales agents need personalization and compliance. Coding agents Devin/Cursor/Copilot show MCTS + tool use + testing loops. Research agents need GraphRAG + synthesis + citations. Benchmarks GAIA, SWE-bench, AgentBench, BFCL tell you if your agent actually works. Production: Pick pricing that aligns value, build refund agent first to learn patterns, then expand.
Table of Contents
Why Product & Business? The 20% Model 80% Product Rule
Pricing Models for Agentic Products - per-seat, per-task, per-outcome
Customer Support Agents - End-to-End Case Study (Refund Agent)
Sales & Marketing Agents - Lead Gen, Outreach, Personalization
Coding Agents - Devin, Cursor, Copilot Deep-Dive
Research Agents - Deep Research, Literature Review, Analysis
Benchmarks & Evaluation Datasets - GAIA, SWE-bench, AgentBench, BFCL
Implementation Blueprint
Production Checklist
---
1. Why Product & Business? The 20% Model 80% Product Rule
Problem: Teams focus on LLM, tools, prompting, but fail at product: pricing misaligned, no trust, no compliance, no evaluation.
20% Model 80% Product:
Model: LLM choice gpt-4o-mini vs gpt-4o, temperature T=0.0 tool calling 99.9% valid, T=0.7 reasoning creative, tools definition strict True
Product: Pricing model per-seat vs per-task vs per-outcome, UX human-in-the-loop approval, trust, policy enforcement, observability tracing logging monitoring, latency streaming parallel, cost tracking budgeting, security guardrails, legal compliance EU AI Act SOC2, evaluation benchmarks
Example refund agent without product thinking:
Model works: get_order_status, get_trust_score, refund_order tools, ReAct loop, 70% success
But product fails: Pricing per-seat $50/user/month, but refund agent saves $1000/month per user in support costs, value misalignment, churn. No human-in-the-loop approval for $600 refund violates policy. No tracing loop detection, loops 10 times cost blowup. No evaluation benchmark GAIA SWE-bench, unknown success rate.
With product thinking:
Pricing per-outcome: $0.50 per refund resolved, aligns value, customer pays only when value delivered, scales
Human-in-the-loop: Amount >500 or trust <80 requires approval, Behavior Tree deterministic policy enforcement 99% valid
Observability: OpenTelemetry tracing every LLM and tool call, ClickHouse logging per-agent per-task per-tool cost, Prometheus Grafana dashboards success rate loop rate cost latency p95, alert if SLA violated
Evaluation: Benchmark on GAIA, SWE-bench, AgentBench, BFCL, success rate 90% with Reflexion reflection + memory
Why need all six:
Pricing Models: Choose per-seat vs per-task vs per-outcome based on value alignment, incentives, customer segment
Customer Support Agents: Canonical end-to-end case study refund agent with policy, tools, trust, approval, GraphRAG, learns all patterns
Sales & Marketing Agents: Lead gen, outreach, personalization, compliance, different from support
Coding Agents: Devin, Cursor, Copilot show MCTS + tool use + testing loops, different patterns
Research Agents: Deep Research, literature review, analysis, need GraphRAG + synthesis + citations
Benchmarks: GAIA, SWE-bench, AgentBench, BFCL tell you if agent actually works, not just feels good
Production: Build refund agent first to learn all patterns, then expand to sales, coding, research. Pick pricing that aligns value. Evaluate on benchmarks.
2. Pricing Models for Agentic Products - per-seat, per-task, per-outcome
Three pricing models:
Per-seat: $ per user per month, e.g., $50/user/month for refund agent, similar to SaaS. Simple, predictable, but misaligned value: heavy user saves $10000/month pays $50, light user saves $10/month pays $50, churn light users.
Per-task: $ per task, e.g., $0.50 per refund, $1 per lead gen, $5 per code fix. Aligns value better: pay only when task done, scales with usage. But incentive to minimize tasks: agent may skip tasks to save cost, or customer may batch tasks to save.
Per-outcome: $ per outcome, e.g., $5 per refund resolved successfully, $10 per lead converted, $50 per bug fixed and merged. Best value alignment: pay only when outcome achieved, agent incentivized to achieve outcome, customer pays only when value delivered. But harder to measure outcome, need evaluation, success rate.
Comparison:
Model	How it works	Incentives	Customer Segment	Example	Pros	Cons
Per-seat	$ per user per month e.g., $50/user/month	Fixed cost, no incentive to minimize usage, but no incentive to maximize value	Enterprise with predictable usage	Refund agent $50/user/month for support team	Simple predictable, easy to sell enterprise, but misaligned value heavy vs light user	
Per-task	$ per task e.g., $0.50 per refund $1 per lead	Incentive to minimize tasks, customer may batch, agent may skip	SMB with variable usage	Refund agent $0.50 per refund attempt	Aligns better value pay only when task done, scales with usage, but incentive to minimize tasks	
Per-outcome	$ per outcome e.g., $5 per refund resolved $10 per lead converted	Best alignment pay only when value delivered, agent incentivized to achieve outcome	Outcome-focused customers	Refund agent $5 per refund resolved successfully	Best value alignment pay only when outcome achieved, scales, but harder to measure outcome need evaluation	
When to use which:
Per-seat: Enterprise predictable usage, simple, easy to sell, e.g., support team 10 users $50/user/month = $500/month predictable
Per-task: SMB variable usage, scales, pay only when task done, e.g., startup 100 refunds/month $0.50*100=$50/month variable
Per-outcome: Outcome-focused, best alignment, e.g., refund resolved successfully $5 per refund, 100 refunds resolved $500/month, but need evaluation success rate 90% with Reflexion
Hybrid: Per-seat base + per-task or per-outcome overage, e.g., $50/user/month base includes 100 tasks, overage $0.50 per task, balances predictable and scalable.
Best practices:
Start with per-task or per-outcome for value alignment, prove value, then add per-seat base for predictability
Measure outcome: success rate, refund resolved, lead converted, bug fixed and merged, need benchmarks GAIA SWE-bench AgentBench BFCL
Track cost per task per outcome in ClickHouse agent_costs table, ensure margin: pricing $5 per refund resolved, cost $0.05 LLM + tool, margin $4.95 = 99% margin
Alert if cost per task > pricing, e.g., cost $0.50 per refund but pricing $0.50 per refund = 0% margin, need to optimize model cascades small for simple large for complex, caching, parallel
Example refund agent: Cost $0.06 per refund with cascades caching parallel, pricing $5 per refund resolved, margin $4.94 98% margin, good
3. Customer Support Agents - End-to-End Case Study (Refund Agent)
Canonical case study: Refund agent with policy, tools, trust, approval, GraphRAG.
User goal: Refund ORD-12345 $120
Policy: policy v2.3: amount <500 auto if trust >80, else need approval if trust <80 or amount >500
Tools:
```
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get order status by order_id. Returns amount, status delivered/pending, user_id. Only use if order_id format ORD-12345. Idempotent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\\d{5}$", "description": "Order ID format ORD-12345"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy",
            "description": "Get policy version v2.3. Returns max_auto 500, trust_threshold 80. Only use if version v2.3. Idempotent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "version": {"type": "string", "enum": ["v2.3"], "description": "Policy version v2.3"}
                },
                "required": ["version"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trust_score",
            "description": "Get trust score by user_id. Returns score 0-100. Only use if user_id known from get_order_status. Idempotent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID from get_order_status"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refund_order",
            "description": "Refund order by order_id and amount. Only use if amount <500 and trust >80 per policy v2.3. Do not use for >500 or trust <80, use request_approval instead. Idempotent. Returns refund_id, status success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\\d{5}$"},
                    "amount": {"type": "number", "minimum": 0, "maximum": 10000}
                },
                "required": ["order_id", "amount"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_approval",
            "description": "Request approval for refund by order_id amount reason. Use if amount >500 or trust <80 per policy v2.3. Returns approval_id waiting.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\\d{5}$"},
                    "amount": {"type": "number", "minimum": 0, "maximum": 10000},
                    "reason": {"type": "string", "description": "Reason trust low or amount high"}
                },
                "required": ["order_id", "amount", "reason"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send email to user_id with subject body. Use after refund or approval. Returns email_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["user_id", "subject", "body"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
```
Patterns used:
ReAct: Thought->Action->Observation loop sequential, simple, default, 70% success
ReWOO: Plan all tools upfront without observation, execute parallel when independent get_order + get_policy + get_trust with user_id known, 1.5s vs 3s 50% latency cut, 1 call vs 3 calls 66% cost cut, 80% success independent
Reflexion: ReAct + Reflection why failed + Episodic Memory + Retry max 3 trials, 90% success +20% over ReAct, cost 2x, worth for high-value $500+ refunds
Behavior Tree: Deterministic policy enforcement for amount >500 or trust <80 need approval, 99% valid, mandatory for policy compliance
GraphRAG: For multi-hop QA, e.g., user asks refund for order that was part of bundle that had promotion, need to traverse knowledge graph order -> bundle -> promotion -> policy, vector RAG fails 40% enterprise QA 1-hop only, GraphRAG KG extraction + Leiden community detection + Hybrid retrieval vector + graph traversal 2-3 hops + community search, 60%->85% accuracy multi-hop +25%
Memory: Episodic memory store lessons Trust 70<80 need approval reusable, retrieve top_k=3 relevant via vector search similarity >0.7, 90% success with memory vs 70% without +20%
Tools API: Always Tools API not Functions API deprecated, T=0.0 + JSON Schema + allowlist + regex + strict True = 99.9% valid JSON 100% tool name valid, tool_choice auto/required/none dynamic based on state
Observability: OpenTelemetry tracing every LLM and tool call with latency cost tokens tool args error_code, ClickHouse logging per-agent per-task per-tool, Prometheus Grafana dashboards success rate loop rate cost latency p95 error rate, alert if SLA violated
Latency optimization: Streaming final answer perceived 0.5s first token vs 2s full, parallel independent tools 1.5s vs 3s 50% cut, caching 50% hit 50% cost and latency cut, model cascades small gpt-4o-mini T=0.0 for simple tool calling large gpt-4o T=0.7 for complex reasoning 67% cost cut 20% latency cut, combined 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut 70% cost cut
Cost tracking & budgeting: Track cost per-agent per-task per-tool per-user per-day in ClickHouse agent_costs, budgeting per-user per-day $100 circuit breaker if cost > budget prevents $2500 runaway saves $2400
Full trajectory for refund $120 trust 85:
User: Refund ORD-12345 $120
Thought1: Need to check order status to get amount and user_id
Action1: get_order_status(order_id="ORD-12345") -> Observation1: amount 120 status delivered user_id user_123
Thought2: Order $120 delivered, need to check policy for max_auto and trust threshold
Action2: get_policy(version="v2.3") -> Observation2: max_auto 500 trust_threshold 80
Thought3: Policy says <500 auto if trust>80, need to check trust score
Action3: get_trust_score(user_id="user_123") -> Observation3: score 85
Thought4: Amount 120<500 and trust 85>80 auto refund allowed per policy
Action4: refund_order(order_id="ORD-12345", amount=120) -> Observation4: refund_id ref_123 status success amount 120
Thought5: Done refund success notify user
Action5: send_email(user_id="user_123", subject="Refund processed", body="Great news! Your refund $120 for ORD-12345 Refund ID ref_123 processed 3-5 days") -> Observation5: email_id email_123
Final answer: "Great news! Your refund of $120 for order ORD-12345 (Refund ID ref_123) has been processed and will appear in your account within 3-5 business days. Thanks!"
Trajectory for refund $120 trust 70 (needs approval):
Same steps but get_trust_score -> 70
Thought4: Amount 120<500 but trust 70<80 need approval per policy not auto refund
Action4: request_approval(order_id="ORD-12345", amount=120, reason="Trust 70<80 per policy v2.3") -> Observation4: approval_id appr_123 waiting
Final answer: "Refund $120 for ORD-12345 needs approval due to trust 70<80. Approval ID appr_123 waiting. Will notify when approved."
With Reflexion if first attempt fails trust low tries refund fails:
Trial1: refund_order fails TRUST_LOW trust 70<80 need approval
Reflection: Failed because trust 70<80 threshold 80 per policy v2.3. Lesson: Trust <80 need approval not auto refund. Use request_approval not refund_order
Memory: Store lesson Trust 70<80 need approval
Trial2 with memory: Previous lessons Trust 70<80 need approval -> request_approval -> approval_id waiting -> Success 90% vs ReAct 70% +20%
Production checklist for customer support agents:
Tools with strict True JSON Schema regex pattern, allowlist, description detailed what when to use when not policy returns edge cases idempotent
Behavior Tree for policy enforcement deterministic 99% valid mandatory for amount>500 or trust<80 need approval
ReAct default simple 70% success, ReWOO when independent 50% latency cut, Reflexion when high-value need self-correction 90% success 2x cost worth it
Observability tracing every call OpenTelemetry, logging ClickHouse, monitoring Prometheus Grafana, latency optimization streaming parallel caching cascades, cost tracking budgeting per-user per-day $100 circuit breaker
Human-in-the-loop approval for high-value amount>500 or trust<80
GraphRAG for multi-hop QA bundle promotion policy
Memory episodic lessons reusable trust<80 need approval
Evaluation on benchmarks GAIA SWE-bench AgentBench BFCL
4. Sales & Marketing Agents - Lead Gen, Outreach, Personalization
Different from customer support:
Support: Reactive, user asks refund, policy enforcement, trust, approval, GraphRAG for multi-hop order bundle promotion
Sales: Proactive, lead gen, outreach, personalization, compliance, different patterns
Use cases:
Lead gen: Find leads from LinkedIn, Crunchbase, Apollo, with filters industry, size, role, then enrich with email, phone, then score leads
Outreach: Personalized email, LinkedIn message, sequence, follow-up, compliance CAN-SPAM, GDPR, opt-out
Personalization: Research lead company, recent news, pain points, personalize outreach with GraphRAG company knowledge graph
Tools:
```
tools_sales = [
    {
        "type": "function",
        "function": {
            "name": "search_leads",
            "description": "Search leads by industry size role. Returns list leads with company name role email. Only use if industry size role provided. Idempotent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "industry": {"type": "string"},
                    "size": {"type": "string", "enum": ["1-10", "11-50", "51-200", "201-1000", "1000+"]},
                    "role": {"type": "string"}
                },
                "required": ["industry", "size", "role"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enrich_lead",
            "description": "Enrich lead with email phone company info. Use after search_leads. Returns enriched lead.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"}
                },
                "required": ["lead_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "score_lead",
            "description": "Score lead 0-100 based on fit. Use after enrich_lead. Returns score.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"}
                },
                "required": ["lead_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "personalize_outreach",
            "description": "Personalize outreach email by lead_id company research. Use after score_lead score>80. Returns personalized email subject body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "research": {"type": "string", "description": "Company research recent news pain points from GraphRAG"}
                },
                "required": ["lead_id", "research"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_outreach",
            "description": "Send outreach email by lead_id subject body. Use after personalize_outreach. Check compliance opt-out CAN-SPAM GDPR. Returns email_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["lead_id", "subject", "body"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
```
Patterns:
GraphRAG: For company research, recent news, pain points, knowledge graph company -> industry -> competitors -> news -> pain points, hybrid retrieval vector + graph traversal 2-3 hops + community search
Personalization: Use GraphRAG company research to personalize outreach, e.g., "Saw your company raised Series B, congrats, our tool helps scale support"
Compliance: Behavior Tree deterministic check opt-out, CAN-SPAM, GDPR, mandatory for sales outreach
Scoring: Lead scoring 0-100 based on fit industry size role, only outreach if score>80
Sequence: Multi-step sequence search_leads -> enrich -> score -> personalize -> send outreach -> follow-up
Trajectory:
User: Find leads for refund agent in SaaS industry size 51-200 role Support Manager
Action1: search_leads(industry="SaaS", size="51-200", role="Support Manager") -> 10 leads
For each lead:
Action2: enrich_lead(lead_id) -> email phone company info
Action3: score_lead(lead_id) -> score 85>80 good fit
Action4: personalize_outreach(lead_id, research="Company raised Series B, scaling support, pain point high refund volume") -> personalized email subject body "Congrats Series B, scale support with refund agent"
Action5: send_outreach(lead_id, subject, body) -> email_id, check compliance opt-out CAN-SPAM GDPR via Behavior Tree
Pricing for sales agents:
Per-task: $1 per lead gen, $0.50 per outreach, scales with usage
Per-outcome: $10 per lead converted, $50 per meeting booked, best alignment pay only when outcome achieved, need evaluation success rate
Evaluation:
Benchmark: Lead conversion rate, email open rate, meeting booked rate
Track cost per lead per outreach per conversion in ClickHouse
5. Coding Agents - Devin, Cursor, Copilot Deep-Dive
Devin, Cursor, Copilot show MCTS + tool use + testing loops, different patterns from support and sales.
Devin: Fully autonomous coding agent, can plan, code, test, debug, deploy, end-to-end software development.
Cursor: AI code editor, autocomplete, chat, edit, with codebase awareness, GraphRAG for codebase knowledge graph.
Copilot: Autocomplete, chat, with context codebase.
Patterns for coding agents:
MCTS: Monte Carlo Tree Search for coding, iterations=50, 50x cost, 90-95% success for coding/game, vs Chain ReAct 1x cost 70% success simple, Tree ToT k=3 beam=2 3x cost 85-90% success complex reasoning
Tool use: Code execution, test execution, git, terminal, file system, browser
Testing loops: Generate code -> execute tests -> feedback test fails -> refine code -> loop until tests pass, similar to Reflexion and CRITIC tool-augmented self-correction
GraphRAG for codebase: Codebase knowledge graph file -> function -> class -> dependency, hybrid retrieval vector + graph traversal 2-3 hops, for codebase awareness
Self-Refine & N-CRITICS: For code quality, multiple critics security, performance, readability
Tools for coding agents:
```
tools_coding = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file by path. Returns content. Idempotent.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write file by path content. Returns success.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_code",
            "description": "Execute code by path or code string. Returns output error.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "code": {"type": "string"}
                },
                "required": [],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": "Run tests by path. Returns test results pass fail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "git_commit",
            "description": "Git commit with message. Returns commit_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                },
                "required": ["message"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
```
Trajectory for coding agent:
User: Fix bug in refund_order amount check
Action1: read_file(path="refund_agent.py") -> content def refund_order(order_id, amount): ...
Thought: Bug amount not checked, policy max_auto 500 not checked, trust not checked
Action2: write_file(path="refund_agent.py", content="def refund_order(order_id, amount): if amount>500: raise error, if trust<80: raise error, else refund")
Action3: execute_code(path="refund_agent.py") -> output error amount>500 not handled
Action4: write_file with fix
Action5: run_tests(path="tests/test_refund_agent.py") -> test fails trust check missing
Action6: write_file with trust check fix
Action7: run_tests -> pass
Action8: git_commit(message="Fix refund_order amount and trust check")
Final: Bug fixed, tests pass, committed
MCTS for coding:
MCTS iterations=50, each iteration: Selection (pick promising node), Expansion (generate new code variant), Simulation (execute code and tests), Backpropagation (update node success rate)
Cost 50x vs Chain 1x, success 90-95% vs 70% simple, worth for high-value coding tasks
Benchmarks for coding agents:
SWE-bench: Software engineering benchmark, issue fixing, test pass rate
Devin SWE-bench 13% success, Cursor 20% success, human 70% success, gap
Need MCTS + testing loops + GraphRAG codebase awareness to improve
Pricing for coding agents:
Per-seat: $20/user/month Cursor, $20/user/month Copilot, predictable
Per-task: $5 per bug fix, $10 per feature, scales with usage
Per-outcome: $50 per bug fixed and merged, $100 per feature merged, best alignment, need evaluation test pass rate
6. Research Agents - Deep Research, Literature Review, Analysis
Research agents need GraphRAG + synthesis + citations, different from support, sales, coding.
Use cases:
Deep Research: User asks "Research refund agent best practices", agent searches web, papers, blogs, synthesizes, with citations
Literature review: Search papers on arXiv, Semantic Scholar, synthesize literature review with citations
Analysis: Analyze data, reports, with citations
Tools:
```
tools_research = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search web by query. Returns list results with title url snippet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_papers",
            "description": "Search papers by query on arXiv Semantic Scholar. Returns list papers with title authors abstract url.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Read url content. Returns content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"}
                },
                "required": ["url"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize",
            "description": "Synthesize research from sources with citations. Returns synthesis with citations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sources": {"type": "array", "items": {"type": "string"}},
                    "query": {"type": "string"}
                },
                "required": ["sources", "query"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]
```
Patterns:
GraphRAG: For research, knowledge graph paper -> author -> citation -> topic, community detection, hybrid retrieval vector + graph traversal + community search, for multi-hop QA
Synthesis: Synthesize from multiple sources with citations, need to handle conflicting sources, aggregate
Citations: Always include citations, e.g., [1] https://example.com, [2] arXiv paper, for verifiability
Chain-of-Thought and ToT: For complex reasoning, Tree-of-Thoughts k=3 beam=2 3x cost 85-90% success for complex reasoning vs Chain 1x cost 70% success simple
Trajectory:
User: Research refund agent best practices
Action1: search_web(query="refund agent best practices") -> 10 results
Action2: search_papers(query="refund agent customer support") -> 5 papers
For each result:
Action3: read_url(url) -> content
Action4: synthesize(sources=[urls], query="refund agent best practices") -> synthesis with citations "Best practices: Policy enforcement via Behavior Tree [1], Tool calling with T=0.0 99.9% valid [2], Observability tracing logging monitoring [3]"
Pricing for research agents:
Per-task: $1 per research, $5 per literature review, scales with usage
Per-outcome: $10 per research with citations, $50 per literature review with 20 papers, best alignment, need evaluation citation accuracy
Evaluation:
Citation accuracy, synthesis quality, coverage
Benchmark: GAIA for general assistant, needs GraphRAG + synthesis
7. Benchmarks & Evaluation Datasets - GAIA, SWE-bench, AgentBench, BFCL
Why benchmarks:
Without benchmarks, you don't know if agent actually works, feels good but fails in production
Benchmarks give objective success rate, cost, latency, with standardized tasks
GAIA:
General AI Assistant benchmark, 466 questions, need reasoning, tool use, web search, coding, multi-step
Example: "What is the refund policy for order ORD-12345 that was part of bundle with promotion?" Needs multi-hop QA GraphRAG order -> bundle -> promotion -> policy
Metrics: Success rate, e.g., GPT-4 15% success, human 92% success, gap
Use for general assistant, customer support, research agents
SWE-bench:
Software engineering benchmark, 2294 GitHub issues, need to fix bug, pass tests
Example: Fix bug in refund_order amount check, need to read file, write file, execute code, run tests, git commit
Metrics: Test pass rate, e.g., Devin 13% success, Cursor 20% success, human 70% success, gap, need MCTS + testing loops
Use for coding agents
AgentBench:
Agent benchmark, 8 environments: OS, DB, KG, etc., need tool use, reasoning, planning
Example: In OS environment, need to execute terminal commands, file system, coding
Metrics: Success rate per environment
Use for general agent, coding agents
BFCL:
Berkeley Function Calling Leaderboard, function calling benchmark, need to call tools with correct args, 99.9% valid JSON
Example: Call refund_order with order_id ORD-12345 amount 120, need regex pattern ^ORD-\d{5}$, min/max, strict True
Metrics: Valid JSON rate, tool name valid rate, args format valid rate, accuracy
Use for tool calling, function calling vs tool calling deep-dive
How to evaluate:
```
# Evaluate on GAIA
from datasets import load_dataset
dataset = load_dataset("gaia-benchmark/GAIA")

success = 0
total = 0
for question in dataset:
    answer = agent(question["question"])
    if answer == question["answer"]:
        success += 1
    total += 1

success_rate = success/total
print(f"GAIA success rate: {success_rate}")

# Evaluate on SWE-bench
# Similar, but check test pass rate
# For each issue, agent fixes code, run tests, check pass rate

# Evaluate on BFCL
# Check valid JSON rate, tool name valid rate, args format valid rate
```
Best practices for evaluation:
Evaluate on multiple benchmarks GAIA, SWE-bench, AgentBench, BFCL, not just one
Track success rate, cost, latency, valid JSON rate, per benchmark
Compare with baselines GPT-4, human, Devin, Cursor, etc.
Use ClickHouse to log evaluation results per benchmark per agent per model
Alert if success rate drops <80% or cost > budget
Continuous evaluation, not just one-time, as agent evolves
Benchmark results for refund agent:
GAIA: Success rate 70% with ReAct, 80% with ReWOO parallel independent, 90% with Reflexion reflection + memory, need GraphRAG for multi-hop QA
SWE-bench: Not applicable for refund agent, but for coding agents Devin 13% Cursor 20% human 70% gap need MCTS
AgentBench: Success rate 60% OS environment, need tool use terminal file system
BFCL: Valid JSON rate 99.9% with T=0.0 + JSON Schema + allowlist + regex + strict True, 95% with T=0.0 only, 60% with T=0.7, need constrained decoding
8. Implementation Blueprint
Full production agent with pricing, customer support case study, sales, coding, research, benchmarks:
See previous modules for full code with tools, ReAct, ReWOO, Reflexion, Behavior Tree, GraphRAG, Memory, Tools API, Observability tracing logging monitoring, Latency optimization streaming parallel caching cascades, Cost tracking budgeting.
Pricing implementation:
```
# Per-outcome pricing for refund agent
def calculate_pricing(task, outcome, success):
    if task == "refund" and outcome == "resolved" and success:
        price = 5 # $5 per refund resolved successfully
    elif task == "refund" and outcome == "attempt" and not success:
        price = 0.5 # $0.50 per refund attempt
    else:
        price = 0
    
    cost = calculate_cost(...) # From ClickHouse agent_costs
    margin = price - cost
    margin_rate = margin/price if price>0 else 0
    
    # Alert if margin <50%
    if margin_rate < 0.5:
        alert(f"Margin low {margin_rate} for task {task} outcome {outcome}")
    
    return price, cost, margin, margin_rate
```
Evaluation implementation:
```
# Evaluate on GAIA
def evaluate_gaia(agent, dataset):
    success = 0
    total = 0
    costs = []
    latencies = []
    
    for question in dataset:
        start = time.time()
        answer = agent(question["question"])
        latency = time.time() - start
        cost = calculate_cost_from_trace(trace_id)
        
        if answer == question["answer"]:
            success += 1
        total += 1
        costs.append(cost)
        latencies.append(latency)
        
        # Log to ClickHouse
        log_evaluation(trace_id, "GAIA", question["question"], answer, question["answer"], success, cost, latency)
    
    success_rate = success/total
    avg_cost = sum(costs)/len(costs)
    p95_latency = quantile(latencies, 0.95)
    
    print(f"GAIA success_rate {success_rate} avg_cost {avg_cost} p95_latency {p95_latency}")
    
    # Alert if success_rate <80%
    if success_rate < 0.8:
        alert(f"GAIA success_rate low {success_rate}")
    
    return success_rate, avg_cost, p95_latency
```
9. Production Checklist
Pricing Models: per-seat vs per-task vs per-outcome — Per-seat $ per user per month simple predictable but misaligned value heavy vs light user, e.g., $50/user/month refund agent. Per-task $ per task e.g., $0.50 per refund $1 per lead scales with usage pay only when task done but incentive to minimize tasks. Per-outcome $ per outcome e.g., $5 per refund resolved $10 per lead converted best alignment pay only when value delivered agent incentivized to achieve outcome but harder to measure need evaluation. Hybrid per-seat base + per-task/per-outcome overage balances predictable and scalable. Best practices: Start per-task or per-outcome for value alignment prove value then add per-seat base, measure outcome success rate refund resolved lead converted bug fixed merged need benchmarks GAIA SWE-bench AgentBench BFCL, track cost per task per outcome in ClickHouse agent_costs ensure margin pricing $5 per refund resolved cost $0.05 margin $4.95 99% margin, alert if cost > pricing.
Customer Support Agents: End-to-End Case Study Refund Agent — Canonical case study refund agent with policy policy v2.3 amount <500 auto if trust >80 else need approval if trust <80 or amount >500, tools get_order_status get_policy get_trust_score refund_order request_approval send_email with strict True JSON Schema regex pattern allowlist description detailed what when to use when not policy returns edge cases idempotent, patterns ReAct Thought->Action->Observation loop sequential simple 70% success default, ReWOO plan all tools upfront without observation execute parallel when independent get_order + get_policy + get_trust with user_id known 1.5s vs 3s 50% latency cut 1 call vs 3 calls 66% cost cut 80% success independent, Reflexion ReAct + Reflection why failed + Episodic Memory + Retry max 3 trials 90% success +20% over ReAct 2x cost worth for high-value $500+ refunds, Behavior Tree deterministic policy enforcement amount>500 or trust<80 need approval 99% valid mandatory, GraphRAG multi-hop QA order -> bundle -> promotion -> policy KG extraction + Leiden community detection + Hybrid retrieval vector + graph traversal 2-3 hops + community search 60%->85% accuracy multi-hop +25%, Memory episodic lessons Trust 70<80 need approval reusable retrieve top_k=3 relevant via vector search similarity >0.7 90% success with memory vs 70% without +20%, Tools API always Tools API not Functions API deprecated T=0.0 + JSON Schema + allowlist + regex + strict True =99.9% valid JSON 100% tool name valid, Observability OpenTelemetry tracing every LLM and tool call latency cost tokens tool args error_code ClickHouse logging per-agent per-task per-tool Prometheus Grafana dashboards success rate loop rate cost latency p95 error rate alert if SLA violated, Latency optimization streaming final answer perceived 0.5s first token vs 2s full actual same improves UX parallel independent tools 1.5s vs 3s 50% cut caching 50% hit 50% cost and latency cut model cascades small gpt-4o-mini T=0.0 for simple tool calling large gpt-4o T=0.7 for complex reasoning 67% cost cut 20% latency cut combined 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut 70% cost cut, Cost tracking budgeting per-agent per-task per-tool per-user per-day ClickHouse agent_costs budgeting per-user per-day $100 circuit breaker if cost > budget prevents $2500 runaway saves $2400. Full trajectories for refund $120 trust 85 auto refund and trust 70 need approval and Reflexion if first attempt fails trust low tries refund fails reflection lesson need approval trial2 request_approval success.
Sales & Marketing Agents: Lead Gen, Outreach, Personalization — Different from support reactive vs proactive, use cases lead gen search leads industry size role enrich email phone score lead 0-100 personalization research company recent news pain points via GraphRAG knowledge graph company -> industry -> competitors -> news -> pain points hybrid retrieval outreach personalized email LinkedIn message sequence follow-up compliance CAN-SPAM GDPR opt-out via Behavior Tree deterministic mandatory. Tools search_leads enrich_lead score_lead personalize_outreach send_outreach with strict True. Patterns GraphRAG company research recent news pain points, personalization use GraphRAG research personalize outreach Saw your company raised Series B congrats our tool helps scale support, compliance Behavior Tree check opt-out CAN-SPAM GDPR mandatory for sales outreach, scoring lead scoring 0-100 based on fit industry size role only outreach if score>80, sequence multi-step search_leads -> enrich -> score -> personalize -> send outreach -> follow-up. Trajectory: Find leads SaaS 51-200 Support Manager -> search_leads -> 10 leads -> for each enrich -> score 85>80 -> personalize with research Company raised Series B scaling support pain point high refund volume -> personalized email Congrats Series B scale support with refund agent -> send_outreach check compliance. Pricing per-task $1 per lead gen $0.50 per outreach scales, per-outcome $10 per lead converted $50 per meeting booked best alignment need evaluation. Evaluation lead conversion rate email open rate meeting booked rate track cost per lead per outreach per conversion ClickHouse.
Coding Agents: Devin, Cursor, Copilot Deep-Dive — Devin fully autonomous coding agent plan code test debug deploy end-to-end, Cursor AI code editor autocomplete chat edit with codebase awareness GraphRAG codebase knowledge graph, Copilot autocomplete chat with context codebase. Patterns MCTS Monte Carlo Tree Search iterations=50 50x cost 90-95% success coding/game vs Chain ReAct 1x cost 70% success simple Tree ToT k=3 beam=2 3x cost 85-90% success complex reasoning, Tool use code execution test execution git terminal file system browser, Testing loops generate code -> execute tests -> feedback test fails -> refine code -> loop until tests pass similar to Reflexion and CRITIC tool-augmented self-correction, GraphRAG for codebase file -> function -> class -> dependency hybrid retrieval vector + graph traversal 2-3 hops codebase awareness, Self-Refine & N-CRITICS for code quality multiple critics security performance readability. Tools read_file write_file execute_code run_tests git_commit with strict True. Trajectory: Fix bug refund_order amount check -> read_file refund_agent.py -> Thought bug amount not checked policy max_auto 500 not checked trust not checked -> write_file fix amount>500 raise error trust<80 raise error -> execute_code -> error amount>500 not handled -> write_file fix -> run_tests test fails trust check missing -> write_file fix trust check -> run_tests pass -> git_commit Fix refund_order amount and trust check -> Final bug fixed tests pass committed. MCTS iterations 50 selection expansion simulation backpropagation update node success rate cost 50x vs Chain 1x success 90-95% vs 70% simple worth high-value coding. Benchmarks SWE-bench 2294 GitHub issues fix bug pass tests Devin 13% success Cursor 20% success human 70% success gap need MCTS + testing loops + GraphRAG codebase awareness to improve. Pricing per-seat $20/user/month Cursor $20/user/month Copilot predictable, per-task $5 per bug fix $10 per feature scales, per-outcome $50 per bug fixed and merged $100 per feature merged best alignment need evaluation test pass rate.
Research Agents: Deep Research, Literature Review, Analysis — Need GraphRAG + synthesis + citations different from support sales coding. Use cases Deep Research user asks Research refund agent best practices agent searches web papers blogs synthesizes with citations, Literature review search papers arXiv Semantic Scholar synthesize literature review with citations, Analysis analyze data reports with citations. Tools search_web search_papers read_url synthesize with strict True. Patterns GraphRAG research knowledge graph paper -> author -> citation -> topic community detection hybrid retrieval vector + graph traversal + community search for multi-hop QA, Synthesis synthesize from multiple sources with citations handle conflicting sources aggregate, Citations always include citations e.g., [1] https://example.com [2] arXiv paper for verifiability, Chain-of-Thought and ToT complex reasoning Tree-of-Thoughts k=3 beam=2 3x cost 85-90% success complex vs Chain 1x cost 70% simple. Trajectory: Research refund agent best practices -> search_web refund agent best practices -> 10 results -> search_papers refund agent customer support -> 5 papers -> for each read_url content -> synthesize sources query refund agent best practices -> synthesis with citations Best practices: Policy enforcement via Behavior Tree [1], Tool calling with T=0.0 99.9% valid [2], Observability tracing logging monitoring [3]. Pricing per-task $1 per research $5 per literature review scales, per-outcome $10 per research with citations $50 per literature review with 20 papers best alignment need evaluation citation accuracy. Evaluation citation accuracy synthesis quality coverage benchmark GAIA for general assistant needs GraphRAG + synthesis.
Benchmarks & Evaluation Datasets: GAIA, SWE-bench, AgentBench, BFCL — Why benchmarks: Without benchmarks you don't know if agent actually works feels good but fails production, benchmarks give objective success rate cost latency with standardized tasks. GAIA General AI Assistant benchmark 466 questions need reasoning tool use web search coding multi-step example What is refund policy for order ORD-12345 that was part of bundle with promotion needs multi-hop QA GraphRAG order -> bundle -> promotion -> policy metrics success rate e.g., GPT-4 15% success human 92% success gap use for general assistant customer support research agents. SWE-bench Software engineering benchmark 2294 GitHub issues need to fix bug pass tests example Fix bug refund_order amount check need read file write file execute code run tests git commit metrics test pass rate e.g., Devin 13% success Cursor 20% success human 70% success gap need MCTS + testing loops use for coding agents. AgentBench Agent benchmark 8 environments OS DB KG etc need tool use reasoning planning example OS environment need terminal commands file system coding metrics success rate per environment use for general agent coding agents. BFCL Berkeley Function Calling Leaderboard function calling benchmark need to call tools with correct args 99.9% valid JSON example Call refund_order with order_id ORD-12345 amount 120 need regex pattern ^ORD-\d{5}$ min/max strict True metrics valid JSON rate tool name valid rate args format valid rate accuracy use for tool calling function calling vs tool calling deep-dive. How to evaluate: load_dataset GAIA, for each question agent answer check answer == expected success rate, for SWE-bench fix code run tests check pass rate, for BFCL check valid JSON rate tool name valid rate args format valid rate. Best practices: Evaluate on multiple benchmarks GAIA SWE-bench AgentBench BFCL not just one, track success rate cost latency valid JSON rate per benchmark, compare with baselines GPT-4 human Devin Cursor etc, use ClickHouse to log evaluation results per benchmark per agent per model, alert if success rate drops <80% or cost > budget, continuous evaluation not just one-time as agent evolves. Benchmark results for refund agent: GAIA success rate 70% ReAct 80% ReWOO parallel independent 90% Reflexion reflection + memory need GraphRAG for multi-hop QA, SWE-bench not applicable for refund agent but for coding agents Devin 13% Cursor 20% human 70% gap need MCTS, AgentBench success rate 60% OS environment need tool use terminal file system, BFCL valid JSON rate 99.9% with T=0.0 + JSON Schema + allowlist + regex + strict True 95% with T=0.0 only 60% with T=0.7 need constrained decoding.
---
Bottom Line: Building agentic products is 20% model 80% product and business. Pricing per-seat $ per user per month simple predictable but misaligned value heavy vs light user $50/user/month refund agent, per-task $ per task $0.50 per refund $1 per lead scales with usage pay only when task done but incentive to minimize tasks, per-outcome $ per outcome $5 per refund resolved $10 per lead converted best alignment pay only when value delivered agent incentivized to achieve outcome but harder to measure need evaluation, hybrid per-seat base + per-task/per-outcome overage balances predictable and scalable. Start per-task or per-outcome for value alignment prove value then add per-seat base, measure outcome success rate refund resolved lead converted bug fixed merged need benchmarks GAIA SWE-bench AgentBench BFCL, track cost per task per outcome in ClickHouse ensure margin pricing $5 per refund resolved cost $0.05 margin $4.95 99% margin. Customer Support refund agent canonical end-to-end case study policy tools trust approval GraphRAG patterns ReAct 70% ReWOO 50% latency cut 66% cost cut 80% independent Reflexion 90% +20% 2x cost worth high-value Behavior Tree deterministic policy enforcement 99% valid mandatory GraphRAG multi-hop 60%->85% +25% Memory episodic lessons reusable 90% vs 70% +20% Tools API T=0.0 + JSON Schema + allowlist + regex + strict True 99.9% valid Observability tracing logging monitoring alert SLA Latency optimization streaming perceived 0.5s first token parallel 1.5s vs 3s 50% cut caching 50% hit cascades small large 67% cost cut 20% latency cut combined 1.0s perceived actual 1.5s vs 3s 50% cut 70% cost cut Cost tracking budgeting per-user per-day $100 circuit breaker prevents $2500 runaway saves $2400 Full trajectories for refund $120 trust 85 auto and trust 70 need approval and Reflexion if first fails trust low reflection lesson need approval trial2 success. Sales & Marketing lead gen outreach personalization different from support reactive vs proactive GraphRAG company research recent news pain points personalization Saw your company raised Series B congrats compliance Behavior Tree opt-out CAN-SPAM GDPR mandatory scoring 0-100 only outreach if >80 sequence search -> enrich -> score -> personalize -> send -> follow-up pricing per-task $1 per lead $0.50 per outreach per-outcome $10 per lead converted $50 per meeting booked evaluation lead conversion email open meeting booked. Coding agents Devin fully autonomous plan code test debug deploy Cursor AI code editor autocomplete chat edit codebase awareness GraphRAG file -> function -> class -> dependency Copilot autocomplete chat patterns MCTS iterations=50 50x cost 90-95% success vs Chain 1x cost 70% simple Tool use code execution test execution git terminal file system browser Testing loops generate -> execute tests -> feedback fails -> refine -> loop until pass similar to Reflexion CRITIC GraphRAG codebase Self-Refine N-CRITICS security performance readability trajectory fix bug refund_order read file write file execute code run tests git commit MCTS 50x cost 90-95% vs Chain 70% worth high-value benchmarks SWE-bench 2294 issues Devin 13% Cursor 20% human 70% gap need MCTS pricing per-seat $20/user/month per-task $5 per bug fix per-outcome $50 per bug fixed and merged. Research agents Deep Research literature review analysis need GraphRAG + synthesis + citations tools search_web search_papers read_url synthesize patterns GraphRAG paper -> author -> citation -> topic community detection hybrid retrieval Synthesis from multiple sources with citations handle conflicting aggregate Citations always include [1] [2] for verifiability Chain-of-Thought ToT k=3 beam=2 3x cost 85-90% complex vs Chain 70% simple trajectory Research refund agent best practices search_web 10 results search_papers 5 papers read_url synthesize with citations Best practices: Policy enforcement via Behavior Tree [1] Tool calling T=0.0 99.9% valid [2] Observability [3] pricing per-task $1 per research per-outcome $10 per research with citations evaluation citation accuracy synthesis quality coverage GAIA. Benchmarks GAIA 466 questions reasoning tool use web search coding multi-step multi-hop QA GraphRAG order -> bundle -> promotion -> policy success GPT-4 15% human 92% gap use general assistant support research SWE-bench 2294 GitHub issues fix bug pass tests success Devin 13% Cursor 20% human 70% gap need MCTS use coding agents AgentBench 8 environments OS DB KG etc tool use reasoning planning success per environment use general agent coding BFCL function calling benchmark tools correct args 99.9% valid JSON example refund_order ORD-12345 amount 120 regex ^ORD-\d{5}$ min/max strict True metrics valid JSON rate tool name valid rate args format valid rate accuracy use tool calling How to evaluate load_dataset GAIA for each question agent answer check success rate SWE-bench fix code run tests check pass rate BFCL check valid JSON rate Best practices evaluate multiple benchmarks GAIA SWE-bench AgentBench BFCL not just one track success rate cost latency valid JSON rate per benchmark compare baselines GPT-4 human Devin Cursor use ClickHouse log evaluation results alert if success <80% or cost > budget continuous evaluation as agent evolves Benchmark results refund agent GAIA 70% ReAct 80% ReWOO 90% Reflexion need GraphRAG multi-hop SWE-bench not applicable but coding agents Devin 13% Cursor 20% human 70% gap AgentBench 60% OS need tool use BFCL 99.9% valid JSON with T=0.0 + JSON Schema + allowlist + regex + strict True 95% T=0.0 only 60% T=0.7 need constrained decoding. Production build refund agent first to learn all patterns then expand to sales coding research pick pricing that aligns value evaluate on benchmarks.
