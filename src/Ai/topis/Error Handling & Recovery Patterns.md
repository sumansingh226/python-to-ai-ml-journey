# Error Handling & Recovery Patterns in Agentic AI
## How Production Agents Fail Gracefully and Self-Heal

> **Core Thesis:** Agents fail 10x more than REST APIs because they chain 10 LLM calls + 10 tool calls + non-deterministic reasoning. A REST API with 99.9% per-call reliability = 99% success for 1 call, but 10-call agent = 99%^10 = 90% success. With LLM hallucination 15%, real success = 70% without recovery patterns. Production agents need layered recovery: retry, fallback, reflection, re-planning, and human escalation.

### Table of Contents
1. [Why Agents Fail More](#1-why-agents-fail-more)
2. [Type 1: Tool Errors (Most Common - 40%)](#2-type-1-tool-errors-most-common---40)
3. [Type 2: LLM Errors (Hallucination, Invalid JSON - 30%)](#3-type-2-llm-errors-hallucination-invalid-json---30)
4. [Type 3: Logic Errors (Wrong Plan, Loop - 20%)](#4-type-3-logic-errors-wrong-plan-loop---20)
5. [Type 4: System Errors (Timeout, OOM, Pod Death - 10%)](#5-type-4-system-errors-timeout-oom-pod-death---10)
6. [Layered Recovery Architecture](#6-layered-recovery-architecture)
7. [Graceful Degradation](#7-graceful-degradation)
8. [Production Blueprint](#8-production-blueprint)

---

### 1. Why Agents Fail More

**Math:**

- Single tool call reliability: 99.9%
- 10 tool calls in trajectory: 99.9%^10 = 99% (1% fail)
- Plus LLM hallucination: 15% chance of invalid JSON or wrong tool
- Combined: ~85% raw success without recovery
- Plus planning errors: ~70% without recovery

**vs REST API:**

- REST API: 1 call = 99.9% success
- Agent: 20 calls + LLM = 70% success without recovery patterns

**So need recovery layers to get to 92%+ success.**

### 2. Type 1: Tool Errors (Most Common - 40%)

**Sub-types:**

**a) Transient errors (retryable):**
- Rate limit 429, timeout, 503, network glitch
- Stripe 100 req/s limit, DB connection lost

**Recovery: Exponential backoff + jitter**

```python
def execute_tool_with_retry(tool, args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return tool.execute(args)
        except RateLimitError:
            wait = (2**attempt) + random.uniform(0,1)
            sleep(wait)
        except TimeoutError:
            if attempt == max_retries-1:
                raise
            sleep(1)
        except PermanentError: # Invalid ID, auth failed
            raise # Don't retry permanent
```

**b) Permanent errors (not retryable):**
- Invalid order ID, insufficient permissions, validation error

**Recovery: Reflection + alternative approach**

```python
try:
    result = tool.execute(args)
except PermanentError as e:
    # Don't retry same args
    reflection = llm.generate(f"Tool {tool.name} failed permanently: {e}\nArgs: {args}\nWhat alternative tool or args?")
    # e.g., try different order ID lookup, or ask user for correct ID
    history.append(reflection)
    # Try alternative
    alternative_action = llm.generate(f"Alternative action to achieve same goal without {tool.name}")
```

**c) Tool returns unexpected format:**

- Stripe returns null, DB returns empty list, API returns HTML error page instead of JSON

**Recovery: Validation + fallback**

```python
result = tool.execute(args)
if not validate(result, expected_schema):
    # Try alternative tool or use cached value
    if cached_value_exists(args):
        result = cached_value
    else:
        reflection = llm.generate(f"Tool returned invalid format: {result}, expected {schema}, how to handle?")
```

**Pros/Cons of retry:**
- Pros: Handles 90% of transient failures automatically
- Cons: Can amplify rate limit if all workers retry at same time — need jitter + circuit breaker

### 3. Type 2: LLM Errors (Hallucination, Invalid JSON - 30%)

**Sub-types:**

**a) Invalid JSON / Schema violation:**
- LLM generates `{"order_id": "ORD-123"}` but schema requires `{"order_id": "ORD-12345"}` with 5 digits, or missing required field
- Constrained decoding reduces this from 15% to 0.1%, but prompting alone = 15% error

**Recovery: Structured outputs + retry with error message**

```python
def llm_generate_with_retry(prompt, schema, max_retries=2):
    for attempt in range(max_retries):
        response = llm.generate(prompt, temperature=0.0, response_format=schema)
        try:
            validated = schema.parse(response) # Pydantic validation
            return validated
        except ValidationError as e:
            # Feed error back to LLM
            prompt = f"{prompt}\nPrevious response invalid: {e}\nPlease fix and return valid JSON matching {schema}"
            # Retry
    # After max retries, fallback to safe default
    return fallback_value(schema)

# Production: Use constrained decoding (regex ^ORD-\d{5}$) = 99.9% valid, no retry needed
```

**b) Hallucinated tool name / args:**
- LLM generates `get_order_statusz` (typo) or `order_id=123` instead of `ORD-12345`

**Recovery: Tool schema validation + self-correction**

```python
def validate_tool_call(tool_name, args, available_tools):
    if tool_name not in available_tools:
        # Find closest tool
        closest = fuzzy_match(tool_name, available_tools)
        return f"Tool {tool_name} doesn't exist, did you mean {closest}?"
    if not validate_args(args, tool_schema):
        return f"Args {args} invalid for {tool_name}, expected {tool_schema}, error: {validation_error}"
    return None # Valid

# In loop
error = validate_tool_call(tool_name, args, available_tools)
if error:
    history.append(f"Tool call validation error: {error}")
    # LLM will self-correct on next iteration
    continue
```

**c) Hallucinated policy / facts:**
- LLM says "Refund policy allows $10K refund" when actual policy is $500 max

**Recovery: Policy Engine as deterministic layer + RAG verification**

```python
# Don't trust LLM's policy memory — verify via policy engine
policy = get_policy(version=v2.3) # From Postgres, not LLM memory
if amount > policy.max_auto_refund:
    # Policy engine denies, not LLM
    deny_action(reason=f"Amount {amount} > max auto {policy.max_auto_refund}")
```

### 4. Type 3: Logic Errors (Wrong Plan, Loop - 20%)

**a) Wrong plan:**
- Agent decomposes task incorrectly — checks trust before order status, but needs order amount first

**Recovery: Re-planning**

```python
def planning_loop_with_replan(user_goal):
    plan = llm.generate(f"Decompose {user_goal} into sub-goals", temperature=0.4)
    for i, sub_goal in enumerate(plan.sub_goals):
        result = react_loop(sub_goal)
        if failed(result) and is_critical(sub_goal):
            # Re-plan remaining sub-goals based on failure
            plan = llm.generate(f"Sub-goal {sub_goal} failed with {result}, re-plan remaining {plan.sub_goals[i+1:]} considering failure", temperature=0.4)
            # Continue with new plan
```

**b) Infinite loop (47% of ReAct failures):**
- Agent repeats same action 3x

**Recovery: Loop detection + reflection + temperature increase**

```python
def detect_loop(history, window=3):
    last_actions = [h.action for h in history[-window:]]
    if len(set(last_actions)) == 1:
        return True
    return False

if detect_loop(history):
    reflection = llm.generate(f"Stuck repeating {history[-1].action}, why? What different approach?", temperature=0.7) # Increase temp to break loop
    history.append(reflection)
    episodic_memory.append(reflection)
```

**c) No progress:**
- Last 3 observations identical, no world state change

**Recovery: Progress check + re-plan**

```python
def has_progress(history_window):
    # Check if observations gave new info or changed state
    # If all observations identical and no new data, no progress
    ...

if not has_progress(history[-3:]):
    reflection = llm.generate("No progress last 3 steps, re-plan with different approach")
```

### 5. Type 4: System Errors (Timeout, OOM, Pod Death - 10%)

**a) Pod death / crash:**
- Worker pod dies mid-trajectory — loses in-memory history

**Recovery: State externalized to Postgres after each step + queue re-enqueue**

```python
def save_state_after_each_step(task_id, history, cost):
    pg.execute("INSERT INTO agent_trajectories (task_id, state_json, cost) VALUES (%s, %s, %s) ON CONFLICT DO UPDATE", (task_id, json.dumps(history), cost))

# If pod dies, task goes back to queue (SQS visibility timeout)
# Another worker loads state from Postgres and resumes
def load_and_resume(task_id):
    state = pg.query("SELECT state_json FROM agent_trajectories WHERE task_id=%s", (task_id,))
    return react_loop_resume(state)
```

**b) LLM timeout / 500 error:**

- OpenAI returns 500, timeout after 30s

**Recovery: Fallback model + retry**

```python
def llm_generate_with_fallback(prompt, primary_model="gpt-4o", fallback_model="claude-3-haiku", max_retries=2):
    for attempt in range(max_retries):
        try:
            return primary_model.generate(prompt, timeout=30)
        except TimeoutError:
            if attempt == max_retries-1:
                # Fallback to cheaper model
                return fallback_model.generate(prompt, timeout=30)
            sleep(1)
```

**c) OOM / Context overflow:**

- History grows to 100K tokens, exceeds context window

**Recovery: Compaction + summarization**

```python
if token_count(history) > 80000: # 80K threshold for 100K window
    # Compact: Keep first (system) + last 5 turns + summarize middle
    summary = llm.generate(f"Summarize middle of history: {history[1:-5]}")
    history = [history[0]] + [summary] + history[-5:]
    # Save original to Postgres for audit
```

### 6. Layered Recovery Architecture

**Production agents need 5 layers:**

```
Layer 5: Human Escalation (final fallback)
  |
Layer 4: Re-planning (wrong plan, no progress)
  |
Layer 3: Reflexion (learn from failure, retry with lesson)
  |
Layer 2: Self-Correction (invalid JSON, hallucinated tool -> feed error back)
  |
Layer 1: Retry (transient tool errors -> exponential backoff)
  |
Base: Tool execution + LLM generation
```

**Cost of layers:**

- Layer 1 retry: 1.2x cost (20% overhead)
- Layer 2 self-correction: 1.5x cost (1 extra LLM call)
- Layer 3 reflexion: 2-3x cost (full retry with memory)
- Layer 4 re-planning: 1.5x cost (1 planning call + remaining)
- Layer 5 human: 10x cost (human 2 min @ $30/hr) but prevents $10K mistake

**Without layers:** 70% success, $0.50 cost
**With layers 1-3:** 92% success, $0.80 cost (1.6x cost for 22% more success — worth it)
**With layers 1-5:** 98% success, $1.20 cost (2.4x cost for 28% more success — worth it for high-value tasks >$500)

### 7. Graceful Degradation

**When recovery fails, fail gracefully — don't hallucinate success**

**Bad:** Agent fails to refund but says "Refund $120 processed" (hallucinated success)

**Good:** Agent fails after retries, says:

```
"I tried to process refund for ORD-12345 but encountered an error: Stripe rate limit after 3 retries.
What I completed:
- Verified order ORD-12345: $120 delivered
- Checked policy: $120 < $500 auto-refund allowed
- Checked trust_score: 85 >80 allowed

What failed:
- refund_order API returned 429 rate limit

Next steps:
- I will retry in 5 minutes automatically
- Or you can contact support with task_id task_123 for manual refund
- All steps logged for audit (trace_id abc...)"
```

**Implementation:**

```python
def fail_gracefully(task_id, history, error):
    summary = llm.generate(f"History: {history}\nError: {error}\nSummarize what completed, what failed, next steps for user, don't hallucinate success")
    save_state(task_id, history, status="failed", failure_reason=error, user_message=summary)
    alert(task_id, error)
    return summary # Return to user
```

### 8. Production Blueprint

**Full error handling loop:**

```python
def production_agent_with_error_handling(task_id, user_goal):
    MAX_STEPS = 20
    MAX_COST = 1.00
    MAX_RETRIES_PER_TOOL = 3
    MAX_LLM_RETRIES = 2
    
    history = [user_goal]
    episodic_memory = load_episodic_memory(user_id)
    total_cost = 0
    
    for step in range(MAX_STEPS):
        # Budget checks
        if total_cost > MAX_COST:
            return fail_gracefully(task_id, history, "Cost budget exceeded")
        
        # Loop detection
        if detect_loop(history):
            reflection = llm_generate_with_retry(f"Stuck in loop repeating {history[-1]}, reflect", max_retries=1)
            history.append(reflection)
            continue
        
        # Generate thought + action with LLM error handling
        try:
            thought = llm_generate_with_fallback_and_validation(
                prompt=f"Goal: {user_goal}\nHistory: {history}\nEpisodic: {episodic_memory}",
                schema=ThoughtSchema,
                max_retries=MAX_LLM_RETRIES,
                primary_model="gpt-4o-mini",
                fallback_model="claude-3-haiku"
            )
            action = llm_generate_with_fallback_and_validation(
                prompt=f"Thought: {thought}\nAction:",
                schema=ActionSchema,
                max_retries=MAX_LLM_RETRIES
            )
        except ValidationErrorAfterRetries as e:
            return fail_gracefully(task_id, history, f"LLM failed to generate valid action after retries: {e}")
        
        # High-risk check
        if is_high_risk(action):
            serialize_state(task_id, history, status="waiting_approval")
            queue.ack(task_id)
            send_webhook(task_id, reason=f"High-risk: {action}")
            return
        
        # Execute tool with retry + permanent error handling
        try:
            observation = execute_tool_with_retry(action.tool, action.args, max_retries=MAX_RETRIES_PER_TOOL)
        except RateLimitError as e:
            # Retry already exhausted
            return fail_gracefully(task_id, history, f"Tool {action.tool} rate limited after retries: {e}")
        except PermanentError as e:
            # Reflect and try alternative
            reflection = llm_generate_with_retry(f"Tool {action.tool} failed permanently: {e}, what alternative approach?")
            history.append(f"Tool failed: {e}")
            history.append(reflection)
            # Try alternative tool
            alternative = llm_generate_with_retry(f"Alternative to {action.tool} for goal {user_goal}")
            history.append(alternative)
            continue
        except Exception as e:
            return fail_gracefully(task_id, history, f"Unexpected tool error: {e}")
        
        history.append((thought, action, observation))
        total_cost += cost_of_step(thought, action)
        save_state(task_id, history, total_cost)
        
        # Progress check
        if step > 3 and not has_progress(history[-3:]):
            replan = llm_generate_with_retry(f"No progress last 3 steps: {history[-3:]}, re-plan remaining")
            history.append(replan)
            continue
        
        if is_done(observation, thought):
            # Success
            episodic_memory.append(f"Success pattern: {history[-3:]}")
            save_episodic_memory(user_id, episodic_memory)
            break
    
    # Final cost velocity check
    check_cost_velocity()
    
    return final_answer(history)
```

**Monitoring in ClickHouse:**

```sql
-- Failure reasons breakdown
SELECT failure_reason, count() as failures, avg(cost_usd), avg(steps)
FROM agent_trajectories
WHERE status='failed' AND date=today()
GROUP BY failure_reason
ORDER BY failures DESC

-- Tool error rate
SELECT tool_name, countIf(status='error')/count() as error_rate, avg(retries)
FROM tool_calls
WHERE date=today()
GROUP BY tool_name
HAVING error_rate > 0.05 -- Alert if >5% error rate

-- LLM validation error rate
SELECT model, countIf(validation_failed)/count() as validation_error_rate
FROM llm_calls
WHERE date=today()
GROUP BY model
```

**Alerting:**

- Tool error rate >10% -> alert + circuit breaker
- LLM validation error >15% -> switch to constrained decoding
- Failure rate >15% -> page + check golden dataset
- Cost per task >$1.00 -> page (possible loop bug)

---

**Bottom Line:** Agents fail 10x more than REST APIs — 70% success without recovery, 92%+ with layered recovery. Layer 1 retry handles transient tool errors (40% of failures), Layer 2 self-correction handles invalid JSON/hallucinated tools (30%), Layer 3 Reflexion handles logic errors and learns from failures (20%), Layer 4 re-planning handles wrong plans, Layer 5 human escalation for high-risk. Always fail gracefully — summarize what completed, what failed, next steps, don't hallucinate success. Save state after each step for resume after pod death. Monitor failure reasons in ClickHouse and alert on error rate >10%.

---
*Module: Error Handling & Recovery Patterns in Agentic AI - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026*
*Reference: ReAct paper Yao et al. 2022 (47% failures are loops), Reflexion Shinn et al. 2023*
