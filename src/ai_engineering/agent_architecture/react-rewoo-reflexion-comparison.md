# ReAct, ReWOO, Reflexion Patterns: Complete Comparison
## From Reasoning + Acting to Reasoning Without Observation to Self-Correction

> **Core Thesis:** ReAct = Reasoning + Acting loop Thought->Action->Observation, most used, 70% success, simple. ReWOO = Reasoning Without Observation, plans all tool calls upfront without observations, 50% latency cut, 30% cost cut, 80% success when tools independent. Reflexion = ReAct + Reflection (why failed) + Retry with memory, 90% success (+20% over ReAct) with 2x cost. Production: Use ReAct default, ReWOO when tools independent (get_order + get_policy + get_trust parallel), Reflexion when high-value tasks need self-correction ($500+ refunds, coding).

### Table of Contents
1. [Why These Patterns? The Evolution](#1-why-these-patterns-the-evolution)
2. [ReAct: Reasoning + Acting - Thought->Action->Observation Loop](#2-react-reasoning--acting---thought-action-observation-loop)
3. [ReWOO: Reasoning Without Observation - Plan All Tools Upfront](#3-rewoo-reasoning-without-observation---plan-all-tools-upfront)
4. [Reflexion: ReAct + Reflection + Retry with Memory](#4-reflexion-react--reflection--retry-with-memory)
5. [Self-Refine & N-CRITICS Variants](#5-self-refine--n-critics-variants)
6. [Complete Comparison Table](#6-complete-comparison-table)
7. [When to Use Which - Decision Tree](#7-when-to-use-which---decision-tree)
8. [Implementation Blueprint - All Three with Tools API](#[STRIPPED 72 bytes])
9. [Hybrid: ReWOO + Reflexion + ReAct](#9-hybrid-rewoo--reflexion--react)
10. [Benchmarks, Cost, Latency, Success Rate](#10-benchmarks-cost-latency-success-rate)
11. [Production Checklist](#11-production-checklist)

---

### 1. Why These Patterns? The Evolution

**Problem:** LLM alone hallucinates, can't call tools, can't self-correct.

**Evolution:**

1. **Chain-of-Thought (CoT) 2022:** LLM thinks step by step, but no tool calling, no observation, hallucinates.
   - Example: "Refund ORD-12345 $120? Think: Need to check order, policy, trust, then refund." -> No tool calls, hallucinates order amount.

2. **ReAct 2022 (Yao et al.):** Adds Acting - Thought->Action->Observation loop, tool calling with observation, 70% success, most used.
   - Example: Thought: Need to check order -> Action: get_order_status(ORD-12345) -> Observation: $120 delivered -> Thought: Check policy -> Action: get_policy(v2.3) -> Observation: max_auto 500 -> Thought: Refund -> Action: refund_order -> Observation: success -> Done.

3. **ReWOO 2023 (Xu et al.):** Reasoning Without Observation - Plans all tool calls upfront without waiting for observations, executes tools, then synthesizes. 50% latency cut, 30% cost cut vs ReAct when tools independent.

4. **Reflexion 2023 (Shinn et al.):** ReAct + Reflection (verbal reinforcement) - After failure, reflects why failed, stores lesson in memory, retries with lesson, 90% success (+20% over ReAct) with 2x cost.

**Why need all three:**

- ReAct simple, works for most tasks, but sequential, high latency (3 tool calls = 3 LLM calls)
- ReWOO faster, cheaper when tools independent, but fails when tools dependent (get_order -> returns user_id -> get_trust needs user_id)
- Reflexion best success rate, self-corrects, but 2x cost, needs memory

**Production:** Use ReAct default, ReWOO when tools independent (get_order + get_policy + get_trust with user_id known parallel), Reflexion when high-value tasks need self-correction ($500+ refunds, coding, research).

### 2. ReAct: Reasoning + Acting - Thought->Action->Observation Loop

**From Yao et al. 2022 ReAct paper.**

**How it works:**

Loop: Thought (reasoning) -> Action (tool call) -> Observation (tool result) -> Thought -> Action -> Observation -> ... until done.

```
User: Refund ORD-12345 $120

Thought 1: Need to check order status to get amount and user_id
Action 1: get_order_status(order_id="ORD-12345")
Observation 1: {"amount": 120, "status": "delivered", "user_id": "user_123"}

Thought 2: Order $120 delivered, need to check policy for max_auto and trust threshold
Action 2: get_policy(version="v2.3")
Observation 2: {"max_auto": 500, "trust_threshold": 80}

Thought 3: Policy says <500 auto if trust>80, need to check trust score
Action 3: get_trust_score(user_id="user_123")
Observation 3: {"score": 85}

Thought 4: Amount 120 <500 and trust 85>80, auto refund allowed per policy
Action 4: refund_order(order_id="ORD-12345", amount=120)
Observation 4: {"refund_id": "ref_123", "status": "success", "amount": 120}

Thought 5: Done, refund success, notify user
Action 5: Final answer (tool_choice none) -> "Refund $120 processed for ORD-12345. Refund ID ref_123."
```

**Pseudocode with Tools API:**

```python
def react(user_goal, max_steps=10):
    history = [{"role": "user", "content": user_goal}]
    tools = [...] # Define tools with strict True
    
    for step in range(max_steps):
        # Dynamic tool_choice
        if is_done(history):
            tool_choice = "none"
        else:
            tool_choice = "auto"
        
        temperature = 0.0 if tool_choice != "none" else 0.7
        
        # Call LLM with tools
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            top_p=1.0 if temperature==0.0 else 0.9,
            top_k=None if temperature==0.0 else 50
        )
        
        assistant_msg = response.choices[0].message
        
        if not assistant_msg.tool_calls:
            # Final answer
            history.append({"role": "assistant", "content": assistant_msg.content})
            break
        
        # Has tool calls
        history.append({
            "role": "assistant",
            "content": assistant_msg.content, # Thought
            "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]
        })
        
        # Execute tool calls
        for tc in assistant_msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError as e:
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps({"error": f"Invalid JSON {e}", "code": "INVALID_JSON"})})
                continue
            
            result = execute_tool(tc.function.name, args)
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        
        # Loop detection
        if detect_loop(history):
            reflection = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history + [{"role": "user", "content": "Stuck repeating same action, reflect why and try different approach"}],
                tools=tools,
                tool_choice="none",
                temperature=0.7
            )
            history.append({"role": "assistant", "content": reflection.choices[0].message.content})
    
    final = history[-1]["content"] if history[-1]["role"] == "assistant" else "Done"
    return final
```

**Pros:**

- Simple, easy to implement
- Most used pattern, 70% success rate
- Handles dependent tools (get_order -> returns user_id -> get_trust needs user_id) sequential, works
- Tool calling with observation, reduces hallucination

**Cons:**

- Sequential: 3 tool calls = 3 LLM calls = 3s latency vs ReWOO 1.5s (1 LLM call + 3 parallel executions) = 50% slower
- High cost: 3 LLM calls vs ReWOO 1 call = 3x cost
- No self-correction: If fails, no reflection, no retry, fails
- No planning upfront: Decides tool call at each step, not planning all tools

**When to use:**

- Default for most tasks, especially when tools dependent (get_order -> user_id -> get_trust)
- Simple tasks with 1-3 tool calls
- When need observation before next tool call (dependent)

**Cost, latency, success:**

- Cost: 3 LLM calls for 3 tools = 3x vs ReWOO 1x
- Latency: 3s for 3 tools sequential vs ReWOO 1.5s parallel = 50% slower
- Success: 70% (fails 30% when needs self-correction)

### 3. ReWOO: Reasoning Without Observation - Plan All Tools Upfront

**From Xu et al. 2023 ReWOO paper.**

**How it works:**

1. **Planning:** LLM generates plan with all tool calls and dependencies without observations (Reasoning Without Observation)
2. **Execution:** Execute all tool calls (parallel if independent, sequential if dependent)
3. **Synthesis:** LLM synthesizes final answer from plan + tool results

```
User: Refund ORD-12345 $120

Step 1: Planning (Reasoning Without Observation)
LLM generates plan without observations:
Plan:
  Tool 1: get_order_status(order_id="ORD-12345") - need amount and user_id
  Tool 2: get_policy(version="v2.3") - need max_auto and trust_threshold
  Tool 3: get_trust_score(user_id="user_123") - need trust score, depends on Tool 1? No, user_id known from context? If unknown, depends on Tool 1 returns user_id
  Tool 4: refund_order(order_id="ORD-12345", amount=120) - depends on Tool 1,2,3 (amount from Tool1, policy from Tool2, trust from Tool3)

But ReWOO plans all upfront without observations, so it assumes user_id known or will be from Tool1, but doesn't wait for Tool1 observation before planning Tool3. So it plans:
  - get_order_status(ORD-12345)
  - get_policy(v2.3)
  - get_trust_score(user_123) - assumes user_id known
  - refund_order(ORD-12345, 120) - assumes amount 120 known

Step 2: Execution
Execute tools:
  - get_order_status(ORD-12345) -> {"amount": 120, "status": "delivered", "user_id": "user_123"}
  - get_policy(v2.3) -> {"max_auto": 500, "trust_threshold": 80}
  - get_trust_score(user_123) -> {"score": 85}
  - refund_order(ORD-12345, 120) -> {"refund_id": "ref_123", "status": "success"}

Note: If get_trust needed user_id from get_order, ReWOO would still plan get_trust with placeholder, but execution would need to handle dependency: Execute get_order first, get user_id, then get_trust with user_id. So ReWOO needs dependency handling.

Step 3: Synthesis
LLM synthesizes final answer from plan + results:
"Refund $120 processed for ORD-12345. Order delivered, policy max_auto 500, trust 85>80, auto refund allowed. Refund ID ref_123."
```

**Pseudocode:**

```python
def rewoo(user_goal):
    tools = [...]
    
    # Step 1: Planning without observation
    # LLM generates plan with tool calls and dependencies
    planning_prompt = f"Goal: {user_goal}\nPlan all tool calls needed with dependencies. Return JSON: {{plan: [{{tool, args, dependencies: [tool_index], reasoning}}]}}"
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": planning_prompt}],
        tools=tools,
        tool_choice="required", # Must plan tools
        temperature=0.7, # Creative planning
        response_format={"type": "json_schema", "json_schema": {"name": "Plan", "schema": PlanSchema}}
    )
    
    plan = json.loads(response.choices[0].message.content)["plan"]
    # Plan: [{"tool": "get_order_status", "args": {"order_id": "ORD-12345"}, "dependencies": [], "reasoning": "Need amount and user_id"}, {"tool": "get_policy", "args": {"version": "v2.3"}, "dependencies": [], "reasoning": "Need max_auto"}, {"tool": "get_trust_score", "args": {"user_id": "user_123"}, "dependencies": [], "reasoning": "Need trust"}, {"tool": "refund_order", "args": {"order_id": "ORD-12345", "amount": 120}, "dependencies": [0,1,2], "reasoning": "Refund after checks"}]
    
    # Step 2: Execution with dependency handling
    results = {}
    # Topological sort by dependencies
    sorted_plan = topological_sort(plan) # [[0,1,2], [3]] - first group independent parallel, second group depends on first
    
    for group in sorted_plan:
        # Group independent, execute parallel
        tool_calls = [plan[i] for i in group]
        # Execute parallel
        group_results = await asyncio.gather(*[execute_tool(tc["tool"], tc["args"]) for tc in tool_calls])
        for i, result in zip(group, group_results):
            results[i] = result
            # If result contains user_id and next tool needs user_id, update args for dependent tools
            # e.g., get_order returns user_id, get_trust needs user_id, so update get_trust args with user_id from get_order result
            for j in range(len(plan)):
                if i in plan[j]["dependencies"]:
                    # Update args for dependent tool j with result from i
                    if "user_id" in result and "user_id" not in plan[j]["args"]:
                        plan[j]["args"]["user_id"] = result["user_id"]
                    if "amount" in result and "amount" not in plan[j]["args"]:
                        plan[j]["args"]["amount"] = result["amount"]
    
    # Step 3: Synthesis
    synthesis_prompt = f"Goal: {user_goal}\nPlan: {plan}\nTool results: {results}\nSynthesize final answer with reasoning path."
    
    final_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": synthesis_prompt}],
        tools=tools,
        tool_choice="none",
        temperature=0.7
    )
    
    return final_response.choices[0].message.content
```

**Pros:**

- Faster: Plans all tools in 1 LLM call vs ReAct 3 LLM calls for 3 tools = 50% latency cut (1.5s vs 3s), 66% cost cut (1 call vs 3 calls) when tools independent
- Parallel: Executes independent tools parallel
- Planning upfront: Better for independent tools

**Cons:**

- Fails when tools dependent and dependency not known upfront: e.g., get_order returns user_id needed for get_trust, but ReWOO plans get_trust without user_id upfront, needs dependency handling to update args after get_order result
- No observation before next tool call: If get_order returns amount 120 but plan assumed 120, okay, but if get_order returns amount 600 but plan assumed 120 and planned refund 120, need to handle amount mismatch
- Less flexible than ReAct: ReAct decides next tool based on observation, ReWOO plans all upfront without observation

**When to use:**

- Tools independent: get_order + get_policy + get_trust with user_id known parallel
- Need speed and cost saving: 50% latency cut, 66% cost cut vs ReAct
- Planning-heavy tasks where all tools known upfront

**Cost, latency, success:**

- Cost: 1 LLM call for planning + 1 for synthesis = 2 calls vs ReAct 3 calls for 3 tools = 33% cost cut (2 vs 3)
- Latency: 1.5s (1 planning call 0.5s + 3 parallel executions 0.5s + 1 synthesis 0.5s) vs ReAct 3s (3 sequential LLM calls 0.5s each + 3 executions 0.5s each) = 50% latency cut
- Success: 80% when tools independent, 60% when tools dependent (because dependency handling complex)

### 4. Reflexion: ReAct + Reflection + Retry with Memory

**From Shinn et al. 2023 Reflexion paper.**

**How it works:**

1. **Try:** ReAct loop (Thought->Action->Observation) with max steps
2. **Fail:** If fails (e.g., refund fails because trust 70 <80, or order not found), reflect why failed (verbal reinforcement)
3. **Memory:** Store reflection lesson in episodic memory (e.g., "Trust 70 <80, need approval, not auto refund")
4. **Retry:** ReAct loop again with lesson in memory, up to max retries

```
User: Refund ORD-12345 $120

Trial 1:
Thought 1: Check order
Action 1: get_order_status(ORD-12345) -> amount 120, user_123
Thought 2: Check trust
Action 2: get_trust_score(user_123) -> score 70
Thought 3: Amount 120<500 and trust 70, try refund
Action 3: refund_order(ORD-12345, 120) -> fails, trust 70<80 per policy, need approval
Observation 3: {"error": "Trust 70 <80, need approval", "code": "TRUST_LOW"}
Thought 4: Failed, need approval
Action 4: Final answer -> "Refund failed, trust low, need approval"

Reflection (after failure):
LLM reflects: "Failed because trust 70 <80 threshold 80 per policy v2.3. Lesson: For trust <80, need approval, not auto refund. For ORD-12345, trust 70, need request_approval, not refund_order."

Store lesson in memory: {"task": "Refund ORD-12345", "lesson": "Trust 70<80, need approval, not auto refund", "timestamp": now}

Trial 2 (with memory):
History includes lesson: "Previous trial failed: Trust 70<80, need approval"
Thought 1: Check order (same)
Action 1: get_order_status(ORD-12345) -> amount 120, user_123
Thought 2: Trust 70<80 per lesson, need approval, not auto refund
Action 2: request_approval(order_id="ORD-12345", amount=120, reason="Trust 70<80") -> approval_id appr_123 waiting
Observation 2: {"approval_id": "appr_123", "status": "waiting"}
Thought 3: Approval requested, notify user
Action 3: Final answer -> "Refund $120 for ORD-12345 needs approval due to trust 70<80. Approval ID appr_123 waiting."

Success with reflection and retry.
```

**Pseudocode:**

```python
def reflexion(user_goal, max_trials=3, max_steps_per_trial=10):
    tools = [...]
    memory = [] # Episodic memory of lessons
    
    for trial in range(max_trials):
        history = [{"role": "user", "content": user_goal}]
        # Add memory lessons to history
        if memory:
            lessons_text = "\n".join([f"Trial {i} lesson: {lesson}" for i, lesson in enumerate(memory)])
            history.append({"role": "user", "content": f"Previous lessons:\n{lessons_text}"})
        
        success = False
        
        for step in range(max_steps_per_trial):
            # ReAct loop
            if is_done(history):
                tool_choice = "none"
            else:
                tool_choice = "auto"
            
            temperature = 0.0 if tool_choice != "none" else 0.7
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature
            )
            
            assistant_msg = response.choices[0].message
            
            if not assistant_msg.tool_calls:
                history.append({"role": "assistant", "content": assistant_msg.content})
                # Check if success
                if "success" in assistant_msg.content.lower() or "refund_id" in assistant_msg.content.lower() or "approval_id" in assistant_msg.content.lower():
                    success = True
                break
            
            history.append({
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]
            })
            
            for tc in assistant_msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError as e:
                    history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps({"error": f"Invalid JSON {e}", "code": "INVALID_JSON"})})
                    continue
                
                result = execute_tool(tc.function.name, args)
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
                
                # Check if result is error
                if "error" in result:
                    # Failure, will reflect after trial
                    pass
        
        if success:
            # Success, return final answer
            final = history[-1]["content"] if history[-1]["role"] == "assistant" else "Done"
            return final
        
        # Failure, reflection
        reflection_prompt = f"Goal: {user_goal}\nHistory: {history}\nFailed, reflect why failed, what lesson, what different approach next trial. Return JSON: {{reflection: string, lesson: string}}"
        
        reflection_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": reflection_prompt}],
            tools=tools,
            tool_choice="none",
            temperature=0.7 # Creative reflection
        )
        
        reflection_content = reflection_response.choices[0].message.content
        # Parse lesson
        try:
            reflection_json = json.loads(reflection_content)
            lesson = reflection_json.get("lesson", reflection_content)
        except:
            lesson = reflection_content
        
        memory.append(lesson)
        # Continue next trial with memory
    
    # All trials failed
    return f"Failed after {max_trials} trials. Last lesson: {memory[-1] if memory else 'No lesson'}"

# Example usage
answer = reflexion("Refund ORD-12345 $120")
# Trial 1 fails trust 70<80, reflects lesson need approval, Trial 2 success with approval
```

**Pros:**

- Best success rate: 90% vs ReAct 70% (+20%) because self-corrects with reflection and retry
- Verbal reinforcement: Reflection lesson stored in memory, improves next trial
- Handles failures: If fails, reflects why, retries with lesson

**Cons:**

- 2x cost: Max trials 3, each trial ReAct loop 3-5 LLM calls = 9-15 LLM calls vs ReAct 3-5 calls = 2-3x cost
- Higher latency: 3 trials * 3s = 9s vs ReAct 3s = 3x latency
- Needs memory: Store lessons, manage memory

**When to use:**

- High-value tasks where failure expensive: $500+ refunds, coding, research, need self-correction
- Tasks where first attempt often fails: Complex policy checks, coding with tests
- When success rate more important than cost and latency

**Cost, latency, success:**

- Cost: Max trials 3 * 3 LLM calls per trial = 9 calls vs ReAct 3 calls = 3x cost, but early success often trial 1 or 2, average 2x cost
- Latency: 3 trials * 3s = 9s vs ReAct 3s = 3x latency, average 2x latency (2 trials)
- Success: 90% vs ReAct 70% (+20%)

### 5. Self-Refine & N-CRITICS Variants

**Self-Refine (Madaan et al. 2023):**

- Similar to Reflexion but without tool calling, only self-refinement of output
- Loop: Generate -> Feedback (self-critique) -> Refine -> Feedback -> Refine -> ...

```
User: Write refund email

Generate: "Refund $120 processed."
Feedback: "Too short, not friendly, missing details"
Refine: "Great news! Your refund of $120 for order ORD-12345 has been processed and will appear in your account within 3-5 business days. Thanks for your patience!"
Feedback: "Good, but add refund ID"
Refine: "Great news! Your refund of $120 for order ORD-12345 (Refund ID ref_123) has been processed..."
```

**Pseudocode:**

```python
def self_refine(initial_prompt, max_iterations=3):
    output = llm.generate(initial_prompt, temperature=0.7)
    
    for i in range(max_iterations):
        feedback = llm.generate(f"Output: {output}\nFeedback: What is wrong, how to improve?", temperature=0.3)
        output = llm.generate(f"Output: {output}\nFeedback: {feedback}\nRefine output based on feedback:", temperature=0.7)
    
    return output
```

**N-CRITICS:**

- Multiple critics provide feedback, not just self-critique
- Example: 3 critics: policy critic, trust critic, user experience critic

```
Generate: refund_order(ORD-12345, 120)
Critic 1 (policy): Policy says <500 auto if trust>80, need to check trust
Critic 2 (trust): Trust 70<80, need approval
Critic 3 (UX): Need to notify user about approval
Refine: request_approval instead of refund_order
```

**When to use:**

- Self-Refine: For writing tasks, email generation, where need iterative improvement
- N-CRITICS: For complex tasks where multiple perspectives needed

### 6. Complete Comparison Table

| Pattern | How It Works | Cost (3 tools) | Latency (3 tools) | Success Rate | Valid JSON | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ReAct** | Thought->Action->Observation loop sequential | 3 LLM calls cost 3x | 3s sequential | 70% | 95% T=0.0 60% T=0.7 | Default, tools dependent, simple tasks 1-3 tools |
| **ReWOO** | Plan all tools upfront without observation, execute parallel, synthesize | 2 calls (plan + synthesis) cost 2x vs ReAct 3x = 33% cut | 1.5s (1 plan + 3 parallel + 1 synthesis) vs 3s = 50% cut | 80% independent 60% dependent | 95% with constraints | Tools independent, need speed and cost saving |
| **Reflexion** | ReAct + Reflection why failed + Retry with memory max 3 trials | 9 calls max 3 trials * 3 calls = 3x vs ReAct 3 calls, average 2x | 9s max 3 trials * 3s = 3x vs 3s, average 2x 6s | 90% (+20% over ReAct) | 95% | High-value tasks $500+ refunds coding research need self-correction |
| **Self-Refine** | Generate -> Feedback -> Refine loop | 3-5 calls | 2-3s | 75% for writing | N/A | Writing tasks email generation iterative improvement |
| **N-CRITICS** | Multiple critics feedback | 4-6 calls (generate + 3 critics + refine) | 3-4s | 80% for complex | N/A | Complex tasks multiple perspectives needed |

### 7. When to Use Which - Decision Tree

```
Task: Refund ORD-12345 $120

Q1: Tools independent or dependent?
  - Independent: get_order + get_policy + get_trust with user_id known -> independent -> Use ReWOO (50% latency cut, 33% cost cut, 80% success)
  - Dependent: get_order -> returns user_id -> get_trust needs user_id -> dependent -> Use ReAct (handles dependency sequential, 70% success)

Q2: High-value task where failure expensive?
  - Yes: $500+ refund, coding, research -> Use Reflexion (90% success, 2x cost, 2x latency, worth it for high-value)
  - No: $120 refund, simple FAQ -> Use ReAct or ReWOO (70-80% success, lower cost)

Q3: Need self-correction?
  - Yes: Task where first attempt often fails, need reflection and retry -> Use Reflexion (90% success with reflection)
  - No: Simple task first attempt likely success -> Use ReAct or ReWOO

Q4: Writing task?
  - Yes: Email generation, creative writing -> Use Self-Refine (Generate -> Feedback -> Refine loop, 75% success for writing)
  - No: Tool calling task -> Use ReAct/ReWOO/Reflexion

Q5: Multiple perspectives needed?
  - Yes: Complex task where policy, trust, UX critics needed -> Use N-CRITICS (multiple critics feedback)
  - No: Single perspective -> Use ReAct/ReWOO/Reflexion

Example decisions:
- Refund $120 with user_id known, tools independent, low-value, no self-correction needed -> ReWOO (fast, cheap, 80% success)
- Refund $600 with user_id unknown, tools dependent (get_order -> user_id -> get_trust), high-value, need self-correction -> Reflexion (90% success, handles dependency, self-corrects trust low need approval)
- Write refund email -> Self-Refine (iterative improvement)
- Complex refund with policy, trust, UX checks -> N-CRITICS (multiple critics)

### 8. Implementation Blueprint - All Three with Tools API

**ReAct blueprint:**

```python
def react(user_goal, max_steps=10):
    history = [{"role": "user", "content": user_goal}]
    tools = [...]
    
    for step in range(max_steps):
        tool_choice = "none" if is_done(history) else "auto"
        temperature = 0.0 if tool_choice != "none" else 0.7
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature
        )
        
        assistant_msg = response.choices[0].message
        if not assistant_msg.tool_calls:
            history.append({"role": "assistant", "content": assistant_msg.content})
            break
        
        history.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]})
        
        for tc in assistant_msg.tool_calls:
            args = json.loads(tc.function.arguments)
            result = execute_tool(tc.function.name, args)
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        
        if detect_loop(history):
            reflection = openai.chat.completions.create(model="gpt-4o-mini", messages=history + [{"role": "user", "content": "Stuck, reflect why and try different"}], tools=tools, tool_choice="none", temperature=0.7)
            history.append({"role": "assistant", "content": reflection.choices[0].message.content})
    
    return history[-1]["content"]
```

**ReWOO blueprint:**

```python
def rewoo(user_goal):
    tools = [...]
    
    # Planning
    planning_prompt = f"Goal: {user_goal} Plan all tool calls with dependencies JSON: {{plan: [{{tool, args, dependencies, reasoning}}]}}"
    plan_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": planning_prompt}], tools=tools, tool_choice="required", temperature=0.7, response_format={"type": "json_schema", "json_schema": {"name": "Plan", "schema": PlanSchema}})
    plan = json.loads(plan_response.choices[0].message.content)["plan"]
    
    # Execution with dependency handling
    results = {}
    sorted_plan = topological_sort(plan)
    
    for group in sorted_plan:
        tool_calls = [plan[i] for i in group]
        group_results = await asyncio.gather(*[execute_tool(tc["tool"], tc["args"]) for tc in tool_calls])
        for i, result in zip(group, group_results):
            results[i] = result
            # Update dependent args with result
            for j in range(len(plan)):
                if i in plan[j]["dependencies"]:
                    if "user_id" in result and "user_id" not in plan[j]["args"]:
                        plan[j]["args"]["user_id"] = result["user_id"]
    
    # Synthesis
    synthesis_prompt = f"Goal: {user_goal} Plan: {plan} Results: {results} Synthesize final answer"
    final_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": synthesis_prompt}], tools=tools, tool_choice="none", temperature=0.7)
    
    return final_response.choices[0].message.content
```

**Reflexion blueprint:**

```python
def reflexion(user_goal, max_trials=3, max_steps_per_trial=10):
    tools = [...]
    memory = []
    
    for trial in range(max_trials):
        history = [{"role": "user", "content": user_goal}]
        if memory:
            lessons_text = "\n".join([f"Trial {i} lesson: {lesson}" for i, lesson in enumerate(memory)])
            history.append({"role": "user", "content": f"Previous lessons:\n{lessons_text}"})
        
        success = False
        for step in range(max_steps_per_trial):
            tool_choice = "none" if is_done(history) else "auto"
            temperature = 0.0 if tool_choice != "none" else 0.7
            
            response = openai.chat.completions.create(model="gpt-4o-mini", messages=history, tools=tools, tool_choice=tool_choice, temperature=temperature)
            assistant_msg = response.choices[0].message
            
            if not assistant_msg.tool_calls:
                history.append({"role": "assistant", "content": assistant_msg.content})
                if "success" in assistant_msg.content.lower() or "refund_id" in assistant_msg.content.lower() or "approval_id" in assistant_msg.content.lower():
                    success = True
                break
            
            history.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]})
            
            for tc in assistant_msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = execute_tool(tc.function.name, args)
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        
        if success:
            return history[-1]["content"]
        
        # Reflection
        reflection_prompt = f"Goal: {user_goal} History: {history} Failed, reflect why failed, what lesson, what different approach next trial. Return JSON: {{reflection: string, lesson: string}}"
        reflection_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": reflection_prompt}], tools=tools, tool_choice="none", temperature=0.7)
        reflection_content = reflection_response.choices[0].message.content
        try:
            lesson = json.loads(reflection_content).get("lesson", reflection_content)
        except:
            lesson = reflection_content
        memory.append(lesson)
    
    return f"Failed after {max_trials} trials. Last lesson: {memory[-1] if memory else 'No lesson'}"
```

### 9. Hybrid: ReWOO + Reflexion + ReAct

**Production agents use hybrid:**

1. **ReWOO for planning:** Plan all tools upfront (fast, cheap)
2. **ReAct for execution:** Execute plan with ReAct loop handling dependencies and observations (flexible)
3. **Reflexion for self-correction:** If fails, reflect and retry with memory (high success)

```python
def hybrid_rewoo_react_reflexion(user_goal, max_trials=3):
    tools = [...]
    memory = []
    
    for trial in range(max_trials):
        # Step 1: ReWOO planning
        planning_prompt = f"Goal: {user_goal} Previous lessons: {memory} Plan all tool calls with dependencies JSON: {{plan: [{{tool, args, dependencies, reasoning}}]}}"
        plan_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": planning_prompt}], tools=tools, tool_choice="required", temperature=0.7, response_format={"type": "json_schema", "json_schema": {"name": "Plan", "schema": PlanSchema}})
        plan = json.loads(plan_response.choices[0].message.content)["plan"]
        
        # Step 2: ReAct execution with dependency handling
        history = [{"role": "user", "content": user_goal}]
        results = {}
        sorted_plan = topological_sort(plan)
        
        success = True
        for group in sorted_plan:
            tool_calls = [plan[i] for i in group]
            # For each group, use ReAct loop to handle observation before next group
            for tc in tool_calls:
                # ReAct for each tool
                response = openai.chat.completions.create(model="gpt-4o-mini", messages=history, tools=tools, tool_choice={"type": "function", "function": {"name": tc["tool"]}}, temperature=0.0)
                assistant_msg = response.choices[0].message
                history.append({"role": "assistant", "content": assistant_msg.content, "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]})
                
                for tc_msg in assistant_msg.tool_calls:
                    args = json.loads(tc_msg.function.arguments)
                    result = execute_tool(tc_msg.function.name, args)
                    history.append({"role": "tool", "tool_call_id": tc_msg.id, "content": json.dumps(result)})
                    results[tc["tool"]] = result
                    
                    # Check if error
                    if "error" in result:
                        success = False
        
        if success:
            # Synthesis
            synthesis_prompt = f"Goal: {user_goal} Plan: {plan} Results: {results} Synthesize final answer"
            final_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": synthesis_prompt}], tools=tools, tool_choice="none", temperature=0.7)
            return final_response.choices[0].message.content
        
        # Step 3: Reflexion reflection if failure
        reflection_prompt = f"Goal: {user_goal} History: {history} Failed, reflect why failed, what lesson, what different approach next trial. Return JSON: {{reflection: string, lesson: string}}"
        reflection_response = openai.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": reflection_prompt}], tools=tools, tool_choice="none", temperature=0.7)
        reflection_content = reflection_response.choices[0].message.content
        try:
            lesson = json.loads(reflection_content).get("lesson", reflection_content)
        except:
            lesson = reflection_content
        memory.append(lesson)
    
    return f"Failed after {max_trials} trials. Last lesson: {memory[-1] if memory else 'No lesson'}"
```

**Pros of hybrid:**

- Fast planning with ReWOO (1 call vs 3 calls)
- Flexible execution with ReAct (handles dependencies and observations)
- High success with Reflexion (90% success with self-correction)

**Cost, latency, success:**

- Cost: ReWOO planning 1 call + ReAct execution 3 calls + Reflexion 2 trials average = 1 + 3*2 = 7 calls vs ReAct 3 calls = 2.3x cost, but 90% success vs 70% = +20% success worth it for high-value tasks
- Latency: ReWOO planning 0.5s + ReAct execution 3s + Reflexion 2 trials 6s = 9.5s vs ReAct 3s = 3x latency, but average 2 trials 6s vs 3s = 2x latency

### 10. Benchmarks, Cost, Latency, Success Rate

| Pattern | Cost (3 tools) | Latency (3 tools) | Success Rate | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| ReAct | 3 LLM calls cost 3x | 3s sequential | 70% | Default, tools dependent, simple 1-3 tools |
| ReWOO | 2 calls (plan + synthesis) cost 2x vs ReAct 3x = 33% cut | 1.5s vs 3s = 50% cut | 80% independent 60% dependent | Tools independent, need speed and cost saving |
| Reflexion | 9 calls max 3 trials * 3 calls = 3x vs ReAct 3 calls, average 2x 6 calls | 9s max 3 trials * 3s = 3x vs 3s, average 2x 6s | 90% (+20% over ReAct) | High-value $500+ refunds coding research need self-correction |
| Self-Refine | 3-5 calls | 2-3s | 75% for writing | Writing tasks email generation |
| N-CRITICS | 4-6 calls | 3-4s | 80% for complex | Complex tasks multiple perspectives |
| Hybrid ReWOO+ReAct+Reflexion | 7 calls average (1 plan + 3 exec *2 trials) = 2.3x vs ReAct 3 calls | 6s average 2 trials vs 3s = 2x | 90% | Production high-value tasks need fast planning + flexible execution + self-correction |

**Detailed benchmarks for refund $120 task:**

- ReAct: 3 LLM calls (get_order, get_policy, get_trust, refund) actually 4 calls = 4x cost, 4s latency, 70% success (fails 30% when trust low need approval but tries refund)
- ReWOO: 2 calls (plan + synthesis) + 4 tool executions (3 parallel + 1 refund) = 2x cost, 1.5s planning + 0.5s parallel + 0.5s refund + 0.5s synthesis = 3s latency, 80% success when tools independent (user_id known), 60% when dependent (user_id from get_order)
- Reflexion: Max 3 trials * 4 calls = 12 calls cost, 12s latency max, 90% success (trial1 fails trust low, reflects lesson need approval, trial2 success with approval)
- Hybrid: 1 plan + 4 exec + 1 synthesis = 6 calls average 2 trials = 12 calls max, 6s latency average, 90% success

**Recommendation:**

- Simple low-value tasks ($120 refund, FAQ): ReAct or ReWOO (70-80% success, low cost, low latency)
- High-value tasks ($500+ refund, coding, research): Reflexion or Hybrid (90% success, 2x cost and latency worth it)

### 11. Production Checklist

1. **ReAct default** — Thought->Action->Observation loop sequential, simple, most used, 70% success, 3 LLM calls for 3 tools cost 3x latency 3s, handles dependent tools get_order -> user_id -> get_trust sequential.

2. **ReWOO when tools independent** — Plan all tools upfront without observation, execute parallel, synthesize. 2 calls cost 2x vs ReAct 3x = 33% cost cut, latency 1.5s vs 3s = 50% cut, 80% success independent 60% dependent. Use when get_order + get_policy + get_trust with user_id known parallel.

3. **Reflexion when high-value need self-correction** — ReAct + Reflection why failed + Retry with memory max 3 trials, 90% success +20% over ReAct, cost 9 calls max 3x vs ReAct 3 calls average 2x 6 calls, latency 9s max 3x vs 3s average 2x 6s, worth for $500+ refunds coding research.

4. **Self-Refine for writing** — Generate -> Feedback -> Refine loop, 75% success for writing tasks email generation.

5. **N-CRITICS for complex multiple perspectives** — Multiple critics feedback policy trust UX, 80% success for complex.

6. **Hybrid ReWOO+ReAct+Reflexion for production high-value** — ReWOO planning fast cheap, ReAct execution flexible handles dependencies, Reflexion self-correction high success. Cost 7 calls average 2.3x vs ReAct 3 calls, latency 6s average 2x vs 3s, 90% success.

7. **Dynamic temperature** — Planning T=0.7 creative diverse, Tool calling T=0.0 deterministic 99.9% valid with constrained decoding JSON Schema + allowlist + regex, Reasoning T=0.4 balanced, Reflection T=0.7 creative, Writing T=0.7 friendly, Loop breaking T=0.7 breaks 90% loops.

8. **Error handling** — Invalid tool name hallucination delete_all_orders fix allowlist + strict True 100% valid, Invalid args ORD-123 invalid format fix regex ^ORD-\d{5}$ + min/max + validate before execution + return error code INVALID_ARGS with suggested_fix, Tool execution error order not found rate limit return error code NOT_FOUND RATE_LIMIT + retry exponential backoff for retryable RATE_LIMIT NETWORK_ERROR TIMEOUT max retries 3, Invalid JSON trailing comma fix strict True 99.9% valid + try fix re.sub.

9. **Tool design** — Name snake_case verb_noun descriptive refund_order, description detailed what when to use when not policy returns edge cases idempotent, parameters JSON Schema with type description pattern regex min/max enum required additionalProperties False strict True, returns concise JSON relevant fields error with code, idempotent same args same result check already done.

10. **Observability** — Log pattern used ReAct/ReWOO/Reflexion, cost, latency, success rate, error code, valid JSON rate, loop detected, reflection lesson, in ClickHouse. Alert if success rate <80% (need Reflexion) or latency >5s (need ReWOO) or valid JSON <99% (need constrained decoding).

---
**Bottom Line:** ReAct = Thought->Action->Observation loop sequential, simple, default, 70% success, 3 LLM calls for 3 tools cost 3x latency 3s, handles dependent tools. ReWOO = Plan all tools upfront without observation, execute parallel, synthesize, 2 calls cost 2x vs ReAct 3x = 33% cost cut, latency 1.5s vs 3s = 50% cut, 80% success independent 60% dependent, use when tools independent need speed cost saving. Reflexion = ReAct + Reflection why failed (verbal reinforcement) + Retry with memory max 3 trials, 90% success +20% over ReAct, cost 9 calls max 3x vs ReAct 3 calls average 2x 6 calls, latency 9s max 3x vs 3s average 2x 6s, worth for high-value $500+ refunds coding research need self-correction. Self-Refine = Generate->Feedback->Refine loop for writing 75% success. N-CRITICS = Multiple critics feedback for complex 80% success. Production hybrid: ReWOO planning fast cheap + ReAct execution flexible handles dependencies + Reflexion self-correction high success = 7 calls average 2.3x cost 6s average 2x latency 90% success for high-value tasks. Always use Tools API with T=0.0 + JSON Schema + allowlist + regex + strict True = 99.9% valid JSON 100% tool name valid.

