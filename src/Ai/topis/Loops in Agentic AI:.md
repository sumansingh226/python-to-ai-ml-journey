# Loops in Agentic AI: Types, Patterns, and How to Break Infinite Loops
## The Core Primitive That Makes Agents Work (and Fail)

> **Core Thesis:** Loops are what separate agents from chatbots. A chatbot answers once; an agent loops: Think -> Act -> Observe -> Think until done. But loops are also the #1 source of cost blowups and infinite loops — 47% of ReAct failures are repetitive thought-action loops. Mastering loops is mastering agents.

### Table of Contents
1. [Why Loops?](#1-why-loops)
2. [Type 1: The ReAct Loop (Core Loop)](#2-type-1-the-react-loop-core-loop)
3. [Type 2: Self-Reflection / Reflexion Loop](#3-type-2-self-reflection--reflexion-loop)
4. [Type 3: Planning Loop (Decomposition)](#4-type-3-planning-loop-decomposition)
5. [Type 4: Tool Retry Loop](#5-type-4-tool-retry-loop)
6. [Type 5: Human-in-the-Loop (Approval) Loop](#6-type-5-human-in-the-loop-approval-loop)
7. [Type 6: Multi-Agent Loop (Supervisor -> Workers)](#7-type-6-multi-agent-loop-supervisor---workers)
8. [Infinite Loops: Why They Happen & How to Prevent](#8-infinite-loops-why-they-happen--how-to-prevent)
9. [Loop Control: Budget, Time, and Circuit Breakers](#9-loop-control-budget-time-and-circuit-breakers)
10. [Production Implementation Blueprint](#10-production-implementation-blueprint)

---

### 1. Why Loops?

**Chatbot (no loop):**
User: "Refund my order ORD-12345"
Bot: "I can help with refunds. Please provide order ID." — stops.

**Agent (with loop):**
```
Turn 1 Thought: Need to get order status for ORD-12345
Turn 1 Action: get_order_status(ORD-12345) -> $120, delivered
Turn 2 Thought: Need to check refund policy for $120
Turn 2 Action: get_policy(version=v2.3) -> <500 auto, >500 needs approval
Turn 3 Thought: $120 < $500, so auto-refund allowed, trust_score?
Turn 3 Action: get_trust_score(user) -> 85
Turn 4 Thought: Trust 85 >80, auto-refund allowed
Turn 4 Action: refund_order(ORD-12345, 120)
Turn 5 Thought: Task complete, need to notify user
Turn 5 Action: send_email(user, "Refund $120 processed")
Done.
```
Loop until `done` condition.

**Why loops are needed:**
- Tasks require multiple tool calls, not one
- Need to handle failures and retry
- Need to decompose complex tasks
- Need to verify and reflect

### 2. Type 1: The ReAct Loop (Core Loop)

**The default loop for 90% of agents — from Yao et al. 2022 paper "ReAct: Synergizing Reasoning and Acting in Language Models"**

Pattern: `Thought -> Action -> Observation -> Thought -> Action -> Observation ... -> Final Answer`

**Pseudocode:**

```python
def react_loop(user_goal, max_steps=20):
    history = [user_goal]
    for step in range(max_steps):
        thought = llm.generate(f"History: {history}\nWhat to do next? Think step by step")
        action = llm.generate(f"Thought: {thought}\nAction (tool + args):")
        observation = execute_tool(action) # e.g., Stripe API, DB query
        
        history.append(thought)
        history.append(action)
        history.append(observation)
        
        if is_done(observation, thought):
            break
    
    return final_answer(history)
```

**Pros:**
- Simple, general — works for any task with tools
- Reasoning helps plan and recover from errors
- Actions ground reasoning in real observations (prevents hallucination)

**Cons:**
- **47% of failures are repetitive loops** — agent repeats same Thought/Action because it doesn't learn from Observation
- No long-term memory — repeats same mistake every trajectory
- No planning ahead — greedy next step, not optimal path

**When to use:** Default for all agents. Start here.

**Cost:** Each loop iteration = 1 LLM call + 1 tool call. 10-turn loop @ $0.05 per call = $0.50

### 3. Type 2: Self-Reflection / Reflexion Loop

**Adds outer loop: Try -> Fail -> Reflect -> Retry with lesson learned**

From Shinn et al. 2023 Reflexion paper: Store failures in episodic memory and reflect to avoid repeating.

**Pseudocode:**

```python
def reflexion_loop(user_goal, max_retries=3):
    episodic_memory = []
    for retry in range(max_retries):
        history = [user_goal] + episodic_memory # Include past failures
        for step in range(max_steps):
            thought = llm.generate(f"History: {history}\nPast failures: {episodic_memory}\nThink")
            action = llm.generate(...)
            observation = execute_tool(action)
            history.append((thought, action, observation))
            if is_done(): break
        
        if success(history):
            # Store success pattern
            episodic_memory.append(f"Success pattern: {history[-3:]}")
            break
        else:
            # Reflect on failure
            reflection = llm.generate(f"Failed trajectory: {history}\nWhy did it fail? What lesson?")
            episodic_memory.append(f"Failure: {reflection} - Don't repeat {history[-1]}")
            # Retry with lesson in memory
```

**Example:**
- Retry 1: Tries `refund_order` without checking trust_score -> fails with "trust_score required"
- Reflection: "I failed because I didn't check trust_score before refund. Need to check trust_score first."
- Retry 2: `get_trust_score` -> 85 -> `refund_order` -> success

**Pros:**
- Success rate 70% -> 90% on retry tasks
- Learns from failures — doesn't repeat same mistake
- Episodic memory enables cross-task learning

**Cons:**
- 2-3x cost per task (retries)
- Reflection can hallucinate lessons
- Needs episodic memory store (pgvector)

**When to use:** Tasks where first attempt often fails (coding, complex refunds with policy checks). Your curriculum recommends this for 80%+ success tasks.

### 4. Type 3: Planning Loop (Decomposition)

**Adds planning phase: Decompose goal into sub-goals, then loop over sub-goals**

Pattern: `Plan (sub-goals) -> Execute sub-goal 1 (ReAct loop) -> Execute sub-goal 2 -> ... -> Synthesize`

**Pseudocode:**

```python
def planning_loop(user_goal):
    # Planning phase
    plan = llm.generate(f"Goal: {user_goal}\nDecompose into 3-5 sub-goals with dependencies", temperature=0.4)
    # e.g., [Check order, Check policy, Check trust, Refund, Notify]
    
    results = []
    for sub_goal in plan.sub_goals:
        # Each sub-goal is a ReAct loop
        result = react_loop(sub_goal, max_steps=5)
        results.append(result)
        if failed(result) and sub_goal.critical:
            # Re-plan
            plan = llm.generate(f"Sub-goal {sub_goal} failed, re-plan remaining", temperature=0.4)
    
    final = llm.generate(f"Results: {results}\nSynthesize final answer")
    return final
```

**Techniques:**
- **Chain-of-Thought (CoT):** Plan step-by-step
- **Tree-of-Thought (ToT):** Search tree over plans, evaluate multiple plans, pick best — expensive but 20% better for high-value tasks
- **Self-Consistency:** Generate 3 plans, vote

**Pros:**
- Handles complex multi-step tasks that single ReAct loop can't
- Clear sub-goals enable parallel execution (multi-agent)
- Easier to debug — see which sub-goal failed

**Cons:**
- Planning itself costs 1-2 LLM calls
- Plan can be wrong — need re-planning logic
- ToT is expensive (10x cost for search tree)

**When to use:** Complex tasks with 5+ steps, dependencies, or that need multi-agent parallelization.

### 5. Type 4: Tool Retry Loop

**Inner loop for handling tool failures — retry with exponential backoff**

**Pseudocode:**

```python
def execute_tool_with_retry(tool, args, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = tool.execute(args)
            return result
        except RateLimitError as e:
            wait = 2**attempt + random.uniform(0,1) # Exponential backoff + jitter
            sleep(wait)
        except TransientError as e:
            if attempt == max_retries-1:
                raise
            sleep(1)
        except PermanentError as e:
            # Don't retry permanent errors (e.g., invalid order ID)
            raise
```

**Pros:**
- Handles transient failures (Stripe 429, DB timeout)
- Prevents trajectory failure due to flaky tools

**Cons:**
- Can hide permanent errors if retrying too much
- Adds latency

**When to use:** ALWAYS for external API calls (Stripe, email, etc.) — 3 retries with exponential backoff.

### 6. Type 5: Human-in-the-Loop (Approval) Loop

**Loop that pauses for human approval on high-risk actions**

From your Hard Approval Gates module:

**Pseudocode:**

```python
def approval_loop(user_goal):
    history = [user_goal]
    for step in range(max_steps):
        thought = llm.generate(f"History: {history}\nShould I take high-risk action?")
        if is_high_risk(thought, action): # e.g., amount > $500, PII external, delete
            # Pause loop, serialize state to Postgres, free worker
            serialize_state(task_id, history, status="waiting_approval", reason=f"Amount {amount} >500")
            queue.ack(task_id)
            send_webhook_to_human(task_id, reason)
            return # Exit loop, wait for webhook
        
        action = llm.generate(...)
        observation = execute_tool(action)
        history.append((thought, action, observation))
    
    return final_answer(history)

# On approval webhook
@app.post("/approve/{task_id}")
def approve(task_id):
    state = load_state(task_id)
    state.status = "approved"
    queue.enqueue(task_id) # Resume loop
```

**Pros:**
- Prevents autonomous high-value mistakes (refund $10K)
- Provides audit trail for SOC2 / EU AI Act Art 14 human oversight
- Enables compliance

**Cons:**
- Adds latency (human may take hours)
- Need queue + state serialization to free worker while waiting

**When to use:** ALWAYS for high-risk actions — amount >$500, PII external sharing, delete operations, policy exceptions. This is mandatory for SOC2 and EU AI Act.

### 7. Type 6: Multi-Agent Loop (Supervisor -> Workers)

**Outer loop: Supervisor decomposes and delegates to workers, workers run ReAct loops, supervisor synthesizes**

**Pseudocode:**

```python
def supervisor_loop(user_goal):
    # Supervisor plans
    sub_goals = supervisor_llm.generate(f"Goal: {user_goal}\nDecompose for 3 specialists")
    
    # Parallel worker loops
    worker_results = []
    for sub_goal in sub_goals:
        # Each worker is a ReAct loop running in parallel
        worker_task = queue.enqueue(sub_goal, agent=assign_worker(sub_goal))
        worker_results.append(worker_task)
    
    # Wait for all workers
    results = wait_for_all(worker_results)
    
    # Supervisor synthesizes
    final = supervisor_llm.generate(f"Sub-goal results: {results}\nSynthesize final answer, resolve conflicts")
    return final
```

**Pros:**
- Parallelization — 3 workers in parallel = 3x faster than sequential
- Specialization — refund worker fine-tuned for refunds, email worker for email
- Scalable

**Cons:**
- Coordination overhead
- Conflict resolution needed if workers disagree
- More expensive (3x LLM calls if parallel)

**When to use:** Enterprise tasks requiring multiple specialties (refund + fraud check + email).

### 8. Infinite Loops: Why They Happen & How to Prevent

**47% of ReAct failures are repetitive loops — agent stuck repeating same Thought/Action**

**Why:**

1.  **Tool returns same error, agent doesn't learn:** `get_order_status(ORD-123) -> Error: Invalid ID` -> Thought: "Need to get order status" -> Action: `get_order_status(ORD-123)` -> same error -> loop
2.  **Hallucinated tool args:** Agent generates invalid JSON repeatedly because it doesn't check schema
3.  **No progress check:** Agent doesn't check if observation changed state

**Prevention:**

**a) Loop detection:**
```python
def detect_loop(history, window=3):
    # Check if last 3 actions are identical
    last_actions = [h.action for h in history[-window:]]
    if len(set(last_actions)) == 1 and len(last_actions) == window:
        return True # Loop detected
    # Check if observations identical
    last_obs = [h.observation for h in history[-window:]]
    if len(set(last_obs)) == 1 and len(last_obs) == window:
        return True
    return False

if detect_loop(history):
    # Break loop, trigger reflection
    reflection = llm.generate(f"Stuck in loop repeating {history[-1].action}, why? What different action?")
    history.append(reflection)
```

**b) Max steps + circuit breaker:**
```python
MAX_STEPS = 20
MAX_COST = 1.00 # $1.00 per task

if step > MAX_STEPS or total_cost > MAX_COST:
    fail_task(task_id, reason="Loop budget exceeded - possible infinite loop")
    alert("Infinite loop detected", task_id=task_id, history=history)
    break
```

**c) Progress check:**
```python
def has_progress(history):
    # Check if observation changed world state or gave new info
    # If last 3 observations identical and no new info, no progress
    ...

if not has_progress(history[-3:]):
    llm.generate("No progress in last 3 steps, try different approach")
```

**d) Temperature increase on loop:**
```python
if detect_loop(history):
    temperature = min(temperature + 0.2, 1.0) # Increase creativity to break loop
```

### 9. Loop Control: Budget, Time, and Circuit Breakers

**At 10K tasks/day, infinite loop bug can cost $10K in minutes — need guardrails:**

**a) Per-task budget:**
```python
MAX_STEPS = 20
MAX_COST_PER_TASK = 1.00
MAX_TIME_PER_TASK = 300 # 5 min

if steps > MAX_STEPS or cost > MAX_COST or time > MAX_TIME:
    fail_task(task_id, reason="Budget exceeded")
    clickhouse.log(task_id=task_id, failure_reason="loop_budget_exceeded", cost=cost)
    break
```

**b) Cost velocity guardrail (global):**
```python
# In ClickHouse, monitor cost per minute
cost_per_min = clickhouse.query("SELECT sum(cost) FROM traces WHERE timestamp > now() - 60s")

if cost_per_min > 10: # $10/min threshold
    queue.pause() # Stop picking new tasks
    alert_pagerduty("Cost velocity high - possible loop bug - queue paused")
```

**c) Tool call budget:**
```python
MAX_TOOL_CALLS = 10
MAX_SAME_TOOL_REPEATS = 3

if tool_call_count > MAX_TOOL_CALLS:
    fail_task(...)

if count_repeats(tool_name, history) > MAX_SAME_TOOL_REPEATS:
    fail_task(..., reason=f"Tool {tool_name} repeated {MAX_SAME_TOOL_REPEATS}x - loop")
```

### 10. Production Implementation Blueprint

**Full loop with all protections:**

```python
def production_agent_loop(task_id, user_goal):
    MAX_STEPS = 20
    MAX_COST = 1.00
    MAX_SAME_TOOL_REPEATS = 3
    
    history = [user_goal]
    total_cost = 0
    start_time = time.now()
    episodic_memory = load_episodic_memory(user_id) # For Reflexion
    
    for step in range(MAX_STEPS):
        # Budget checks
        if total_cost > MAX_COST:
            fail_task(task_id, reason="Cost budget exceeded")
            break
        if time.now() - start_time > 300:
            fail_task(task_id, reason="Time budget exceeded")
            break
        
        # Loop detection
        if detect_loop(history, window=3):
            reflection = llm.generate(f"Stuck repeating {history[-1].action}, reflect and try different", temperature=0.7)
            history.append(reflection)
            episodic_memory.append(reflection) # Learn
            continue
        
        # Progress check
        if step > 3 and not has_progress(history[-3:]):
            reflection = llm.generate("No progress last 3 steps, re-plan")
            history.append(reflection)
            continue
        
        # Tool repeat check
        if count_repeats(last_tool, history) > MAX_SAME_TOOL_REPEATS:
            fail_task(task_id, reason=f"Tool {last_tool} repeated {MAX_SAME_TOOL_REPEATS}x")
            break
        
        # Generate thought and action
        thought = llm.generate(f"Goal: {user_goal}\nHistory: {history}\nEpisodic: {episodic_memory}\nThink", temperature=0.0)
        action = llm.generate(f"Thought: {thought}\nAction:", temperature=0.0)
        
        # High-risk check - human-in-the-loop
        if is_high_risk(action):
            serialize_state(task_id, history, status="waiting_approval")
            queue.ack(task_id)
            send_webhook(task_id, reason=f"High-risk: {action}")
            return # Pause loop
        
        # Execute tool with retry
        try:
            observation = execute_tool_with_retry(action.tool, action.args, max_retries=3)
        except PermanentError as e:
            observation = f"Tool failed permanently: {e}"
            history.append(observation)
            # Trigger reflection
            reflection = llm.generate(f"Tool {action.tool} failed permanently: {e}, what alternative?")
            history.append(reflection)
            continue
        
        history.append((thought, action, observation))
        total_cost += cost_of_step(thought, action)
        save_state(task_id, history, total_cost) # Save after each step for resume
        
        # Done check
        if is_done(observation, thought):
            # Success - store pattern in episodic memory
            episodic_memory.append(f"Success: {history[-3:]}")
            save_episodic_memory(user_id, episodic_memory)
            break
    
    # Cost velocity check (global)
    check_cost_velocity()
    
    return final_answer(history)
```

**Monitoring in ClickHouse:**

```sql
-- Detect loops
SELECT task_id, count(*) as steps, countDistinct(action) as unique_actions, sum(cost_usd)
FROM traces
WHERE date = today()
GROUP BY task_id
HAVING steps > 15 AND unique_actions < 3 -- Loop: many steps, few unique actions

-- Cost per loop type
SELECT loop_type, avg(cost_usd), avg(steps), countIf(status='failed')/count() as failure_rate
FROM agent_trajectories
GROUP BY loop_type
```

---

**Bottom Line:** Loops are the core primitive of agents — ReAct loop is default, Reflexion loop adds retry with learning (70%->90% success), Planning loop adds decomposition for complex tasks, Tool Retry loop handles flaky APIs, Approval loop pauses for human on high-risk, Multi-Agent loop parallelizes. But loops cause infinite loops — 47% of failures. Prevent with loop detection (identical actions 3x), progress checks, max steps 20, max cost $1.00, max same-tool repeats 3, cost velocity circuit breaker $10/min, and Reflexion to learn from loops. Save state after each step for resume.

---
*Module: Loops in Agentic AI - Types, Patterns, and Infinite Loop Prevention - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026*
*Reference: ReAct paper Yao et al. 2022, Reflexion Shinn et al. 2023*
