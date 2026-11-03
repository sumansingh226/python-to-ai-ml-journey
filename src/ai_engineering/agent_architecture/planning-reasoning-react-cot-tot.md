Planning & Reasoning for Agents: ReAct, CoT, ToT, Reflection
> **Core Thesis:** An LLM that just generates the next token is not an agent. An agent reasons about *what to do next* before doing it. Planning and reasoning frameworks turn a stochastic generator into a deliberative problem-solver that can decompose goals, explore alternatives, and self-correct from failures.
Table of Contents
Why Agents Need Explicit Planning
Chain-of-Thought (CoT): The Foundation
ReAct: Reasoning + Acting
Tree-of-Thought (ToT) & Graph-of-Thought
Reflection, Self-Critique & Reflexion
Task Decomposition Strategies
Implementation Blueprint
Choosing the Right Reasoning Strategy
---
1. Why Agents Need Explicit Planning
Without planning, an agent is a greedy loop:
```
User: "Refund ORD-12345 and notify customer"
Agent: Calls get_order_status -> Gets result -> Calls refund -> Fails because didn't check trust score -> Loops
```
It has no global plan. It just reacts to last observation.
With planning, agent first decomposes:
```
Goal: Refund ORD-12345 and notify
Plan:
1. Get order status and amount
2. Check trust score and policy
3. If amount >500 or trust <30 -> escalate
4. Else -> initiate refund
5. Send notification email
6. Log outcome

Then executes step by step, with ability to replan if step fails.
```
Planning provides:
Global coherence: Steps serve final goal, not just last observation
Efficiency: Avoids redundant tool calls (don't call refund twice)
Error recovery: If step 2 fails, can replan remaining steps
Observability: Plan is auditable artifact — you can see why agent did what it did
2. Chain-of-Thought (CoT): The Foundation
Chain-of-Thought is prompting the model to show its intermediate reasoning steps before final answer.
Standard Prompt:
```
Q: Refund $1200 order with trust score 15. What to do?
A: Approve refund.
```
CoT Prompt:
```
Q: Refund $1200 order with trust score 15. What to do?
A: Let's think step by step. Policy says refund >500 requires approval. Trust 15 <30 also requires approval. Amount is 1200 which is >500. So both conditions trigger escalation. Therefore we must escalate to human, not auto-refund.
Final: escalate_to_human
```
Why it works: Forces model to use more compute (more tokens) for reasoning, reduces hallucination, makes decision traceable.
Zero-Shot CoT: Simply add "Let's think step by step" to prompt — improves accuracy 10-20% on reasoning tasks with no examples.
For Agents: CoT should be inside structured output, not freeform before JSON. See `structured_outputs_constrained_decoding.md`:
```json
{
  "chain_of_thought": "Policy check: amount 1200 > 500 true, trust 15 <30 true, so escalate",
  "action": "escalate_to_human",
  "parameters": {"order_id": "ORD-12345"}
}
```
3. ReAct: Reasoning + Acting (The Standard Agent Loop)
ReAct is the most used agent pattern in 2026 (from Yao et al. 2022). It interleaves reasoning and acting.
Loop:
```
Thought: I need to check order status first to know amount
Action: get_order_status(order_id=ORD-12345)
Observation: {status: delayed, amount: 1200, user_id: 123}
Thought: Amount is 1200 >500, need to check trust score per policy
Action: get_trust_score(user_id=123)
Observation: {trust_score: 15}
Thought: Both escalation conditions true, must escalate
Action: escalate_to_human(...)
```
Advantages over CoT alone:
Can interact with environment via tools
Reasoning is grounded in real observations, not just internal knowledge
Each thought is conditioned on latest tool result
Implementation:
```python
def react_loop(goal, max_steps=10):
    scratchpad = f"Goal: {goal}\n"
    for step in range(max_steps):
        # 1. Reason
        thought = llm.invoke(f"{scratchpad}\nThought:", temperature=0.4) # Planner temp
        
        # 2. Act (with constrained decoding)
        action = llm.invoke(
            f"{scratchpad}\nThought: {thought}\nAction:",
            response_format=ToolCallSchema,
            temperature=0.0 # Executor temp
        )
        
        # 3. Observe
        observation = execute_tool(action)
        
        # 4. Update scratchpad
        scratchpad += f"\nThought: {thought}\nAction: {action}\nObservation: {observation}"
        
        if action.is_final_answer:
            break
    
    return scratchpad
```
This is the backbone of LangChain Agents, OpenAI Assistants, and most production agents.
4. Tree-of-Thought (ToT) & Graph-of-Thought
CoT and ReAct explore one reasoning path linearly. If that path is wrong, agent fails.
Tree-of-Thought explores multiple reasoning paths in parallel like a search tree, then picks best.
How ToT Works:
Generate multiple thoughts: At each step, generate 3-5 candidate next thoughts (high temperature for diversity, T=0.7)
Evaluate: Use LLM-as-a-Judge to score each thought: "Is this promising for achieving goal? Score 1-10"
Prune: Keep top 2 most promising, discard others
Expand: From each kept thought, generate next level of thoughts
Backtrack: If all paths dead-end, backtrack to previous branching point
Example for refund planning:
```
Root: Goal refund ORD-12345
  Branch A: Check order status first -> Score 9/10 (good first step)
  Branch B: Directly refund without checks -> Score 2/10 (violates policy)
  Branch C: Ask user for more info -> Score 4/10 (we have order ID)
-> Keep A, prune B,C
  From A:
    A1: After status, check trust score -> Score 9/10
    A2: After status, directly escalate -> Score 5/10 (need trust first)
-> Keep A1
```
Graph-of-Thought (GoT): Extension where branches can merge. If two different paths reach same state (e.g., both have order status and trust score), merge them to save compute.
When to use ToT:
Complex planning with many possible sub-goals (e.g., coding agent with multiple implementation approaches)
When single ReAct path often gets stuck in loops
Costly — generates 3-5x more tokens than ReAct, so use only for high-value planning step (Tier 3 model), not every step
Implementation with Model Cascades:
Use Tier 3 frontier for ToT planning (generates diverse branches)
Use Tier 2 workhorse for evaluating branches
Use Tier 2 for execution once best path chosen
5. Reflection, Self-Critique & Reflexion
Even with good planning, agents fail. Reflection is ability to critique own past trajectory and improve next attempt.
A. Self-Reflection (After Failure)
After a tool fails or judge says answer is wrong, agent is prompted to reflect:
```
Previous attempt:
Thought: I will refund directly
Action: initiate_refund -> Failed: trust_score too low

Reflection: I failed because I didn't check trust score before refunding. Policy requires trust check. Next time I should check trust_score first and escalate if <30.
```
This reflection is stored in episodic memory and injected into next attempt.
B. Reflexion Framework (Shinn et al.)
Formal framework with Actor, Evaluator, Self-Reflection:
Actor: ReAct agent that attempts task
Evaluator: LLM-as-a-Judge that scores trajectory and gives feedback (e.g., "You failed because you didn't check policy")
Self-Reflection: Actor generates verbal reflection based on evaluator feedback, stores in memory
Retry: Actor retries task with reflection in prompt
This loop improves success rate 20-30% on second try without fine-tuning.
C. Self-Consistency + Reflection
Generate 3 candidate plans via CoT at high temp, then reflect to pick best. Used in self-consistency verification cascade (from Model Cascades module).
6. Task Decomposition Strategies
How to break big goal into sub-goals — the core of planning.
a) Top-Down Decomposition: Start with final goal, recursively break into smaller sub-goals until each is a single tool call.
```
Goal: Process refund and notify
 -> Subgoal 1: Get order details
   -> Tool: get_order_status
 -> Subgoal 2: Evaluate policy
   -> Tool: get_trust_score + check_policy
 -> Subgoal 3: Execute refund or escalate
 -> Subgoal 4: Notify customer
```
b) Bottom-Up (Least-to-Most): Solve easiest sub-problem first, then use its result to solve harder.
c) LLM-Driven Decomposition: Ask planner LLM to output plan as structured list:
```json
{
  "plan": [
    {"step": 1, "description": "Get order status", "tool": "get_order_status", "depends_on": []},
    {"step": 2, "description": "Check trust", "tool": "get_trust_score", "depends_on": [1]},
    {"step": 3, "description": "Conditional refund or escalate", "depends_on": [1,2]}
  ]
}
```
This plan becomes DAG that policy engine can validate before execution.
7. Implementation Blueprint
Combining ReAct + Reflection + ToT for high-value tasks:
```python
class ReasoningAgent:
    def __init__(self):
        self.planner = ChatOpenAI(model="claude-3-5-sonnet", temperature=0.4) # Planning
        self.executor = ChatOpenAI(model="gpt-4o-mini", temperature=0.0) # Tool calling with constraints
        self.evaluator = ChatOpenAI(model="gpt-4o", temperature=0.0) # Judge
        self.memory = EpisodicStore()
    
    def plan_with_tot(self, goal, branching_factor=3):
        # Generate multiple plans
        candidates = []
        for _ in range(branching_factor):
            plan = self.planner.invoke(
                f"Goal: {goal}\nGenerate a step-by-step plan. Think step by step.",
                temperature=0.7 # High for diversity
            )
            candidates.append(plan)
        
        # Evaluate and pick best
        scores = []
        for plan in candidates:
            score = self.evaluator.invoke(
                f"Goal: {goal}\nPlan: {plan}\nScore this plan 1-10 for feasibility and policy compliance."
            )
            scores.append(score)
        
        best_plan = candidates[argmax(scores)]
        return best_plan
    
    def react_with_reflection(self, goal, max_retries=2):
        # 1. Check episodic memory for similar tasks
        past_reflections = self.memory.search(goal, k=2)
        
        # 2. Plan with ToT
        plan = self.plan_with_tot(goal)
        
        scratchpad = f"Goal: {goal}\nPlan: {plan}\nPast lessons: {past_reflections}\n"
        
        for attempt in range(max_retries):
            for step in range(10): # Max steps per attempt
                thought = self.planner.invoke(f"{scratchpad}\nThought:")
                action = self.executor.invoke(
                    f"{scratchpad}\nThought: {thought}\nAction:",
                    response_format=ToolCallSchema
                )
                observation = execute_tool(action)
                scratchpad += f"\nThought: {thought}\nAction: {action}\nObservation: {observation}"
                
                if action.is_final:
                    # Evaluate final result
                    eval_score = self.evaluator.invoke(f"Goal: {goal}, Trajectory: {scratchpad}, Success?")
                    if eval_score.success:
                        self.memory.add({"goal": goal, "trajectory": scratchpad, "success": 1})
                        return scratchpad
                    else:
                        # Reflect and retry
                        reflection = self.planner.invoke(
                            f"Failed trajectory: {scratchpad}\nEvaluator feedback: {eval_score.feedback}\nReflect on what to improve."
                        )
                        scratchpad += f"\nReflection: {reflection}\nRetrying with lesson..."
                        self.memory.add({"goal": goal, "reflection": reflection, "success": 0})
                        break
        
        return scratchpad # Best effort after retries
```
8. Choosing the Right Reasoning Strategy
Strategy	Token Cost	Latency	Success Rate Gain	When to Use
CoT	+30%	Low	+10-15%	All tasks — baseline, put inside JSON
ReAct	+100% (multiple turns)	Medium	+25-40% vs CoT alone	Any task needing tools — standard agent loop
ToT (branch=3)	+300-500%	High	+10-20% vs ReAct	Complex planning where single path often fails, high-value tasks
Reflexion (retry)	+200% (2 attempts)	High	+20-30% on retry	Tasks where failure is costly, can afford retry
Self-Consistency (3 samples)	+200%	Medium	+5-15%	When you need confidence without full ToT
Production Rule:
Use ReAct as default for all agentic workflows
Add CoT inside structured output always
Add Reflection for Tier 2 tasks where failure rate >15%
Use ToT only for initial planning step with Tier 3 frontier, not for every step — too expensive otherwise
Store reflections in episodic memory to avoid repeating same mistake
---
Bottom Line: Reasoning is what separates an agent from a tool-calling script. CoT makes it think, ReAct makes it act based on thinking, ToT makes it explore alternatives, Reflection makes it learn from failure. Build your agent as ReAct by default, add ToT for planning when tasks are complex, and always add Reflexion loop for self-improvement — this is how you go from 70% to 90%+ success rate without bigger models.
In your curriculum, this module sits at the very beginning, before Tool Use & Function Calling, because reasoning is the engine that decides which tools to call.
---
Module: Planning & Reasoning for Agents - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026