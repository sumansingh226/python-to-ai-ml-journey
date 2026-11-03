Multi-Agent Orchestration & Communication
From Single Agent Loops to Teams of Specialized Agents
> **Core Thesis:** A single agent that tries to do everything becomes a bottleneck — it juggles planning, tool calling, verification, and domain expertise in one prompt. Multi-agent systems split the work across specialized agents that communicate, debate, and delegate, achieving higher accuracy and reliability through division of labor.
Table of Contents
Why Single Agent Fails at Scale
The 4 Orchestration Patterns
Communication Protocols
Shared Memory & State Management
Conflict Resolution & Consensus
Implementation Blueprint
Pros and Cons
Production Checklist
---
1. Why Single Agent Fails at Scale
A single ReAct agent loop that does planning + tool calling + reflection in one prompt hits three walls:
a) Context Contamination: The planning prompt gets polluted with low-level tool outputs (5000-row SQL results). The agent loses track of original goal. This is why Context Compaction is needed, but multi-agent solves it structurally — planner never sees raw tool outputs, only summaries from worker.
b) Prompt Bloat: To make one agent good at refunds, shipping, fraud detection, and email writing, you need a 10K token system prompt with all policies, all tool descriptions. It becomes unmanageable and expensive. Specialized agents have small, focused prompts (500 tokens each).
c) Single Point of Failure: If the single agent hallucinates a tool call, entire task fails. In multi-agent, a verifier agent can catch it.
Solution: Divide labor like a human team — Planner, Executor, Verifier, Domain Experts.
2. The 4 Orchestration Patterns
Pattern 1: Supervisor / Router (Most Common in Production)
One central supervisor agent receives user goal, decomposes it, and routes sub-tasks to specialist workers. Workers report back to supervisor.
```
User Goal: "Refund ORD-12345 and notify customer"
  -> Supervisor (Tier 3 frontier, T=0.4): Decomposes into [get_order_status, check_policy, initiate_refund, send_email]
  -> Worker 1 (Refund Specialist, Tier 2): Executes refund workflow
  -> Worker 2 (Email Specialist, Tier 2): Drafts notification email
  -> Supervisor: Synthesizes final answer from worker results
```
Best for: Enterprise workflows with clear domain boundaries (refund team, shipping team). Easy to audit — supervisor logs all delegations.
Implementation: LangGraph with `StateGraph` where supervisor node routes to worker nodes via conditional edges. See `levels_of_autonomy.md` for Router Workflow.
Pattern 2: Hierarchical (Manager -> Team Leads -> Workers)
Supervisor delegates to team leads, who delegate to workers. Multi-level.
```
CEO Agent (Global Planner)
  -> Refund Lead: Manages refund policy checks + trust scoring
    -> Policy Checker Worker
    -> Trust Score Worker
  -> Communication Lead: Manages email + SMS
    -> Email Drafter Worker
```
Best for: Complex orgs where refund itself has sub-steps requiring specialization. Reduces supervisor bottleneck.
Trade-off: More latency due to multi-hop delegation. Need careful state serialization.
Pattern 3: Swarm / Peer-to-Peer (Decentralized)
No central supervisor. Agents communicate peer-to-peer, negotiate, and self-organize. Inspired by OpenAI Swarm (2024).
```
Agent A: "I can handle refund, but need order status"
Agent B: "I have order status tool, here's result: {...}"
Agent C: "I see refund amount >500, I should handle approval"
-> They negotiate via broadcast channel until task completes
```
Best for: Research, creative tasks, brainstorming where no clear hierarchy exists. High diversity.
Cons: Hard to debug, no single audit trail, can loop infinitely if agents disagree. Not recommended for production financial workflows.
Pattern 4: Sequential Pipeline (Assembly Line)
Agents execute in fixed sequence, each passing output to next. Like Unix pipes.
```
User Input -> Intent Classifier Agent -> Entity Extractor Agent -> Policy Checker Agent -> Executor Agent -> Verifier Agent -> Final Response
```
Best for: High-throughput, deterministic workflows where order is fixed (e.g., support ticket triage). Easy to test — each agent is a stage.
Cons: Inflexible — if step 3 fails, whole pipeline fails. No dynamic replanning.
Choosing Pattern:
Pattern	Reliability	Flexibility	Auditability	Latency	Use When
Supervisor	High	Medium	High	Medium	Most enterprise tasks
Hierarchical	High	High	Medium	High	Complex domains with sub-teams
Swarm	Low	Very High	Low	Variable	Brainstorming, research
Sequential	Very High	Low	High	Low	Fixed workflows, triage
3. Communication Protocols
How agents talk matters more than how they think.
A. Message Format: Structured, Not Freeform
Never let agents communicate via freeform text alone — it leads to misinterpretation. Use structured outputs with schema.
```json
{
  "from": "refund_worker",
  "to": "supervisor",
  "type": "result",
  "task_id": "refund_001",
  "status": "success",
  "payload": {"refund_id": "REF-123", "amount": 500},
  "confidence": 0.92,
  "next_steps": ["notify_customer"]
}
```
Types: `task_assignment`, `result`, `clarification_request`, `error`, `escalation`
B. Blackboard Pattern (Shared Message Board)
Instead of direct messages, agents post to shared blackboard (e.g., Redis or Postgres table) that all can read. Reduces coupling.
```
Blackboard (Postgres table: agent_messages)
- Agent A posts: "Need order status for ORD-12345"
- Agent B (listening for order_status requests) picks it up, executes, posts result
- Supervisor sees result, continues
```
Best for: Decoupling — workers don't need to know who supervisor is. Easy to add new workers.
C. Direct Delegation with Handoff
Supervisor directly invokes worker via function call, passing context. Worker returns result.
```
supervisor.invoke(worker="refund_worker", input={order_id: "ORD-12345", context: {...}})
```
Best for: Tight control, low latency. LangGraph and OpenAI Swarm use this.
4. Shared Memory & State Management
Multi-agent systems need shared memory architecture — otherwise each agent has its own amnesia.
From Memory Systems module, apply:
Working Memory: Shared scratchpad in Redis that all agents can read/write (e.g., `scratchpad: {order_status: delayed, trust_score: 85}`)
Semantic Memory: Shared pgvector for facts — all agents retrieve same user preferences
Episodic Memory: Shared trajectory store — when refund worker succeeds, episode is visible to email worker
Procedural Memory: Each agent has its own specialized LoRA adapter (refund LoRA vs email LoRA)
Critical: State Serialization for Pausing
When supervisor triggers Hard Approval Gate (e.g., refund >$500), entire multi-agent state must be serialized (all workers paused), not just supervisor. Use same serialization pattern as `hard_approval_gates.md`.
5. Conflict Resolution & Consensus
What happens when two agents disagree?
Example: Refund worker says "Approve refund $500", Fraud worker says "Deny, trust score too low (12)".
Resolution Strategies:
a) Supervisor as Arbitrator (Most Common):
Supervisor receives both opinions with confidence scores and makes final decision via policy engine. Policy engine has deterministic rule: `if trust_score <30, deny regardless of amount`.
b) Voting / Weighted Consensus:
Multiple workers vote, supervisor takes majority or weighted by confidence/expertise.
```
Refund Worker (confidence 0.9, expertise: refund): Approve
Fraud Worker (confidence 0.95, expertise: fraud): Deny
-> Fraud Worker wins due to higher confidence + relevant expertise
```
c) Debate (Multi-Agent Debate):
Agents debate for 2-3 rounds, each seeing other's reasoning, then converge. Used in research for higher accuracy on ambiguous tasks. Expensive but improves accuracy 10-15% on complex reasoning.
Implementation:
```python
def resolve_conflict(opinions: List[AgentOpinion]):
    # Use policy engine as source of truth
    policy_result = policy_engine.evaluate(opinions)
    if policy_result.confident:
        return policy_result.decision
    
    # Fallback to debate
    return debate_agents(opinions, rounds=2)
```
6. Implementation Blueprint
Full supervisor pattern with LangGraph + memory + guardrails:
```python
from langgraph.graph import StateGraph
from typing import TypedDict

class AgentState(TypedDict):
    goal: str
    scratchpad: dict # Shared working memory
    messages: list
    next: str # Who should act next
    cost: float

# Define specialized workers
def refund_worker(state: AgentState):
    # Only sees relevant context, not entire history
    result = refund_llm.invoke(
        f"Task: {state['goal']}, Scratchpad: {state['scratchpad']}",
        tools=[get_order_status, initiate_refund]
    )
    state["scratchpad"]["refund_result"] = result
    state["next"] = "supervisor"
    return state

def email_worker(state: AgentState):
    result = email_llm.invoke(
        f"Draft email for refund: {state['scratchpad']['refund_result']}",
        tools=[send_email]
    )
    state["scratchpad"]["email_result"] = result
    state["next"] = "supervisor"
    return state

def supervisor(state: AgentState):
    # Tier 3 frontier for planning
    decision = supervisor_llm.invoke(
        f"Goal: {state['goal']}, Scratchpad: {state['scratchpad']}, What next?",
        tools=[refund_worker, email_worker] # Supervisor can delegate
    )
    
    # Policy check before delegation
    if decision.next == "refund_worker" and state["scratchpad"].get("amount", 0) > 500:
        state["next"] = "human_approval" # Hard Approval Gate
    else:
        state["next"] = decision.next
    
    return state

# Build graph
graph = StateGraph(AgentState)
graph.add_node("supervisor", supervisor)
graph.add_node("refund_worker", refund_worker)
graph.add_node("email_worker", email_worker)
graph.add_node("human_approval", human_approval_node)

graph.add_conditional_edges("supervisor", lambda s: s["next"])
graph.add_edge("refund_worker", "supervisor")
graph.add_edge("email_worker", "supervisor")
graph.set_entry_point("supervisor")

app = graph.compile()

# Execute with observability
for event in app.stream({"goal": "Refund ORD-12345", "scratchpad": {}, "cost": 0}):
    print(f"Agent {event['next']} acting, cost: {event['cost']}")
    otel_tracer.log(event) # From observability module
```
Tech Stack:
Orchestration: LangGraph, AutoGen, OpenAI Swarm, CrewAI
Communication: Redis pub/sub or Postgres for blackboard
Memory: pgvector + Postgres (from memory systems module)
Guardrails: Policy engine checks before each delegation (from guardrails module)
7. Pros and Cons
Pros
Specialization: Each agent has small, focused prompt (500 tokens) vs one agent with 10K token mega-prompt — cheaper, more accurate
Parallelism: Workers can execute in parallel (refund + email drafting simultaneously) — reduces latency 30-50%
Reliability via Verification: Verifier agent catches hallucinations from executor agent — increases success rate 15-20%
Modularity: Add new domain expert (e.g., shipping specialist) without retraining entire system
Cons
Complexity: Managing 5 agents, their prompts, their memory, their communication is 5x more engineering than 1 agent
Cost of Coordination: Supervisor + workers means 2-3 LLM calls per step vs 1 — can increase cost if not managed via Model Cascades (Tier 2 workers + Tier 3 supervisor)
Debugging: Tracing failure across 3 agents is harder than single agent trace — need robust OTel tracing with `agent_id`
Latency: Sequential delegation adds hops — hierarchical pattern can be 2-3x slower than single agent for simple tasks
8. Production Checklist
Start with Supervisor pattern: Most reliable, auditable, easiest to implement. Avoid Swarm for production financial tasks.
Use structured communication: JSON with type/status/confidence, not freeform text
Shared memory via Redis/pgvector: All agents see same semantic and episodic memory
Tiered models: Tier 3 frontier for supervisor (planning), Tier 2 workhorses for workers — saves 60% cost (from Model Cascades)
Policy engine before delegation: Supervisor must check policy before routing to worker that does destructive action
OTel with agent_id: Every span must have `gen_ai.agent.id` to debug which agent failed
Hard Approval Gate for multi-agent: When supervisor triggers approval, serialize entire graph state, not just supervisor
Implement conflict resolution: Deterministic policy engine first, debate only as fallback
Test with chaos: Kill a worker mid-task — does supervisor retry or escalate? Include in Tier 3 synthetic env tests
Monitor delegation depth: Alert if supervisor delegates >10 times for one goal — indicates looping
---
Bottom Line: Single agent is a generalist who knows a little about everything and does everything averagely. Multi-agent is a team of specialists who know a lot about one thing and do it well, coordinated by a manager. For enterprise tasks with clear domain boundaries, multi-agent wins on accuracy, cost (via specialization and parallelism), and reliability (via verification). But it costs complexity — start with supervisor, add hierarchy only when needed.
In your curriculum, this module sits after Memory Systems and Model Cascades, because multi-agent needs shared memory and tiered models to be economical, and before Testing & CI/CD because you must test orchestration patterns.
---
Module: Multi-Agent Orchestration & Communication - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026