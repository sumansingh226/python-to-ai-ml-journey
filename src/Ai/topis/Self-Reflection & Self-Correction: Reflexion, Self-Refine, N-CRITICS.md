# Self-Reflection & Self-Correction: Reflexion, Self-Refine, N-CRITICS
## Complete Production Guide - How Agents Learn From Failure Without Weight Updates

> **Core Thesis:** Self-reflection turns failure into memory without retraining. Reflexion = ReAct + Verbal Reflection (why failed) + Episodic Memory + Retry, 90% success (+20% over ReAct) for coding, $500+ refunds. Self-Refine = Generate->Feedback->Refine loop for writing, 85% quality vs 60% single shot. N-CRITICS = Multiple specialized critics (policy, security, UX) critique in parallel, 88% vs 70% single critic. Production agents: Always reflection after failure with T=0.7 creative, store lesson in memory, retry with lesson, max 3 trials, cost 2x for 20% success gain - worth for high-value tasks.

### Table of Contents
1. Why Self-Correction? The No-Retraining Learning
2. Reflexion: ReAct + Reflection + Episodic Memory
3. Self-Refine: Generate->Feedback->Refine Loop
4. N-CRITICS: Multiple Specialized Critics
5. CRITIC: Tool-Augmented Self-Correction
6. Comparison Table
7. Episodic Memory: Store and Retrieve Lessons
8. Reflection Prompts: Good vs Bad
9. Benchmarks
10. Implementation Blueprint
11. Failure Modes and Fixes
12. Production Checklist

---

### 1. Why Self-Correction? The No-Retraining Learning

**Problem:** LLM weights frozen, cannot learn from failure via gradient update in production. Agent fails same way repeatedly.

**Traditional ML:** Failure -> gradient update -> weight update -> next time better. Cost: retraining, expensive, slow.

**Self-reflection learning (no retraining):** Failure -> Verbal Reflection (why failed, what lesson) -> Store lesson in episodic memory (text) -> Retry with lesson in prompt -> Success without weight update. Cost: 1 extra LLM call for reflection, cheap, fast.

**Example:**

Trial 1 (no memory):
- Thought: Trust 70, try refund
- Action: refund_order(ORD-12345, 120) -> fails trust 70<80 need approval
- Observation: Error TRUST_LOW
- Final: Failed

Reflection (after failure, T=0.7 creative):
"Failed because trust 70 <80 threshold 80 per policy v2.3. Lesson: For trust <80, need approval, not auto refund. For ORD-12345 trust 70, use request_approval not refund_order."

Memory: Store lesson {"task": "Refund ORD-12345", "lesson": "Trust 70<80 need approval", "error_code": "TRUST_LOW"}

Trial 2 (with memory):
- History includes lesson: Previous trial failed: Trust 70<80 need approval
- Thought: Trust 70<80 per lesson, need approval not auto refund
- Action: request_approval(ORD-12345, 120, reason="Trust 70<80") -> approval_id waiting
- Final: Success "Refund $120 for ORD-12345 needs approval due to trust 70<80. Approval ID appr_123 waiting."

**Why it works:**
- Verbal reinforcement: Reflection as text lesson, not gradient
- Episodic memory: Store lessons, retrieve relevant lessons for similar tasks
- No weight update: No retraining, cheap, fast

Cost: Reflection 1 LLM call + memory + retry 1-2 trials = 2x cost for 20% success gain (70% -> 90%), worth for high-value.

### 2. Reflexion: ReAct + Reflection + Episodic Memory

**From Shinn et al. 2023 Reflexion - Verbal Reinforcement Learning.**

**How it works:**
1. Try: ReAct loop Thought->Action->Observation with max steps
2. Evaluate: Check if success (refund_id or approval_id present)
3. Fail: If fails, Reflection: LLM reflects why failed, what lesson, what different approach next trial, T=0.7 creative
4. Memory: Store reflection lesson in episodic memory (vector DB)
5. Retry: ReAct loop again with lesson in memory, up to max trials 3

**Pseudocode:**

```
def reflexion(user_goal, max_trials=3, max_steps=10):
    memory = []
    for trial in range(max_trials):
        history = [{"role": "user", "content": user_goal}]
        if memory:
            relevant = retrieve_lessons(user_goal, memory, top_k=3)
            lessons_text = join lessons
            history.append({"role": "user", "content": f"Previous lessons:\\n{lessons_text}\\nAvoid same failures."})
        
        success = False
        failure_reason = None
        
        for step in range(max_steps):
            # ReAct loop
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history,
                tools=tools,
                tool_choice="auto" if not is_done else "none",
                temperature=0.0 if tool_choice!="none" else 0.7
            )
            assistant_msg = response.choices[0].message
            if not assistant_msg.tool_calls:
                history.append({"role": "assistant", "content": assistant_msg.content})
                if is_success(history): success=True
                break
            # execute tools
            for tc in assistant_msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = execute_tool(tc.function.name, args)
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
                if "error" in result: failure_reason=result
        
        if success:
            return history[-1]["content"]
        
        # Reflection after failure
        reflection_prompt = """
        Goal: {user_goal}
        History: {history}
        Failure reason: {failure_reason}
        Reflect:
        1. Why failed? Root cause? Specific policy trust amount tool error_code.
        2. Lesson? Concise reusable lesson for memory.
        3. Next approach? Specific tool and args.
        4. Avoid? What not to do.
        Return JSON with reflection, lesson, next_approach, avoid
        """
        reflection_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": reflection_prompt}],
            tools=tools,
            tool_choice="none",
            temperature=0.7
        )
        lesson = parse JSON from reflection_response
        store_lesson(user_goal, lesson, error_code, trial)
    
    return f"Failed after {max_trials} trials. Last lesson: {memory[-1]}"
```

**Example trajectory:**
- Trial1: get_order -> 120 user_123, get_trust ->70, refund_order -> fails TRUST_LOW. Reflection: Failed because trust 70<80 threshold 80 per policy v2.3. Lesson: Trust 70<80 need approval not auto refund. Use request_approval.
- Trial2 with memory: Trust 70<80 per lesson need approval -> request_approval -> approval_id waiting -> Success.

**Pros:**
- Best success: 90% vs ReAct 70% (+20%)
- Verbal reinforcement, no weight update
- Episodic memory reusable

**Cons:**
- 2x cost avg (9 calls max 3 trials*3 calls =3x vs ReAct 3 calls, avg 6 calls 2x)
- Higher latency avg 6s vs 3s 2x
- Needs memory

**When to use:**
- High-value $500+ refunds, coding with tests, research
- Tasks where first attempt often fails
- Lesson reusable for similar tasks

### 3. Self-Refine: Generate->Feedback->Refine Loop

**From Madaan et al. 2023 Self-Refine.**

Loop: Generate initial output -> Feedback (self-critique what is wrong, how to improve) -> Refine output based on feedback -> loop

Example: Write refund email for ORD-12345 $120 refund_id ref_123
- Iteration0 Generate: "Refund $120 processed."
- Feedback: "Too short, not friendly, missing order ID, refund ID, timeline, thanks"
- Refine: "Great news! Your refund of $120 for order ORD-12345 has been processed and will appear in your account within 3-5 business days. Thanks!"
- Iteration1 Feedback: "Good but missing refund ID ref_123"
- Refine: "Great news! Your refund of $120 for order ORD-12345 (Refund ID ref_123) has been processed..."
- Iteration2 Feedback: "Perfect" -> Done

**Pseudocode:**
```
def self_refine(initial_prompt, max_iterations=3):
    output = llm.generate(initial_prompt, T=0.7)
    for i in range(max_iterations):
        feedback = llm.generate(f"Output: {output}\\nFeedback: What is wrong? How to improve? Specific actionable.", T=0.3)
        if "perfect" in feedback.lower(): break
        output = llm.generate(f"Output: {output}\\nFeedback: {feedback}\\nRefine based on feedback. Return only refined.", T=0.7)
    return output
```

**Variants:**
- Self-Refine with tool feedback: Generate code -> execute -> test fails -> feedback test failure -> refine code

**Pros:**
- Quality: 85% vs 60% single shot +25% for writing
- Iterative improvement

**Cons:**
- Cost 6 calls (3 iter*2) =6x vs single 1 call, avg 3x
- Latency 3s vs 1s 3x, avg 2x
- Feedback can be noisy

**When to use:** Writing tasks email creative writing, code generation with tests.

### 4. N-CRITICS: Multiple Specialized Critics

Multiple specialized critics critique output in parallel, each from different perspective, then refine based on all feedback.

Example: Refund ORD-12345 $120, Generate: refund_order(ORD-12345,120)
- Policy Critic: Policy says <500 auto if trust>80, need to check trust
- Security Critic: order_id format valid ORD-12345 okay, amount 0-10000 okay
- UX Critic: Need to notify user after refund, email missing
- Cost Critic: Amount $120 low-value auto okay

Feedback aggregated: Policy need trust check, Security format okay, UX need email, Cost low-value auto okay

Refine: get_trust_score ->85>80, then refund_order -> success, then send_email -> success

**Pseudocode:**
```
def n_critics(initial_prompt, critics, max_iterations=3):
    output = llm.generate(initial_prompt, T=0.7)
    for i in range(max_iterations):
        feedbacks = []
        for critic in critics:
            # parallel
            fb = llm.generate(f"You are {critic['role']} critic. Output: {output}. Critique from {critic['role']} perspective: {critic['focus']}", T=0.3)
            feedbacks.append({"critic": critic['role'], "feedback": fb})
        if all "good" in f["feedback"] or "perfect" in f["feedback"]: break
        feedback_text = join feedbacks
        output = llm.generate(f"Output: {output}\\nFeedback from multiple critics:\\n{feedback_text}\\nRefine based on all feedback.", T=0.7)
    return output

critics = [
    {"role": "Policy", "focus": "Check policy compliance: amount <500, trust >80, policy v2.3, need approval if trust <80 or amount >500"},
    {"role": "Security", "focus": "Check security: order_id format ORD-12345, amount 0-10000, no injection, PII"},
    {"role": "UX", "focus": "Check user experience: Need to notify user, friendly email, include refund ID, timeline"},
    {"role": "Cost", "focus": "Check cost: Amount low-value <500 auto okay, high-value >500 need approval"}
]
```

**Pros:**
- Best quality 88% vs 70% single critic +18% because multiple perspectives
- Parallel critics 0.5s vs sequential 2s =75% latency cut

**Cons:**
- Cost 18 calls max 3 iter*(1 gen+4 critics+1 refine)=18x vs single 1 call, avg 12 calls 12x
- Latency 4.5s max 9x vs 0.5s, avg 3s 6x
- Complexity defining critics, aggregate feedback

**When to use:** Complex tasks multiple perspectives needed policy security UX cost compliance, high-value tasks.

### 5. CRITIC: Tool-Augmented Self-Correction

**From Gou et al. 2023 CRITIC - Tool use for self-correction.**

Similar to Self-Refine but feedback from tools, not just self-critique.

Example: Generate refund_order(ORD-12345,120), Tool feedback: Execute -> fails TRUST_LOW trust 70<80 need approval, Feedback: Tool says trust low need approval, need request_approval not refund_order, Refine: request_approval(ORD-12345,120, reason="Trust 70<80"), Tool feedback: approval_id waiting, Refine: Success.

**Pseudocode:**
```
def critic(initial_prompt, tools, max_iterations=3):
    history = [{"role": "user", "content": initial_prompt}]
    for i in range(max_iterations):
        response = openai.chat.completions.create(messages=history, tools=tools, tool_choice="auto", T=0.7)
        assistant_msg = response.choices[0].message
        # execute tools
        for tc in assistant_msg.tool_calls:
            result = execute_tool(tc.function.name, args)
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        if is_success(history): break
        # feedback from tool result
        feedback = llm.generate(f"History: {history}\\nTool feedback: {result}\\nWhat wrong, how to improve based on tool feedback?", T=0.3)
        history.append({"role": "user", "content": f"Feedback: {feedback}\\nRefine based on feedback."})
    return history[-1]["content"]
```

Pros: Tool-augmented feedback more accurate than self-critique, 85% vs 70% +15% for tasks where tool feedback needed.
Cons: Cost similar to Self-Refine 6 calls + tool executions, latency 3s.

When to use: Tasks where tool feedback needed coding test execution refund trust check.

### 6. Comparison Table

| Pattern | How It Works | Cost | Latency | Success/Quality | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Reflexion | ReAct + Reflection why failed + Episodic Memory + Retry max 3 trials | 9 calls max 3*3=3x vs ReAct 3 calls, avg 6 calls 2x | 9s max 3*3s=3x vs 3s, avg 6s 2x | 90% success vs ReAct 70% +20% | High-value $500+ refunds coding research need self-correction with memory |
| Self-Refine | Generate->Feedback self-critique->Refine loop max 3 iter | 6 calls (3 iter*2) =6x vs single 1 call, avg 3 calls 3x | 3s vs 1s =3x, avg 2s 2x | 85% quality vs 60% single +25% writing | Writing tasks email creative writing |
| N-CRITICS | Multiple specialized critics parallel critique + Refine | 18 calls max 3 iter*(1 gen+4 critics+1 refine)=18x vs single, avg 12 calls 12x | 4.5s max 9x vs 0.5s, avg 3s 6x | 88% vs 70% single critic +18% | Complex tasks multiple perspectives policy security UX cost |
| CRITIC | Generate->Tool feedback->Refine loop | 6 calls + tool executions | 3s | 85% vs 70% +15% | Tasks where tool feedback needed coding test refund trust check |

Decision tree:
- Need memory of lessons for future similar tasks? Yes: Trust <80 need approval lesson reusable -> Reflexion. No: One-off -> Self-Refine or N-CRITICS or CRITIC
- Writing task or tool calling task? Writing email -> Self-Refine. Tool calling refund -> Reflexion or CRITIC or N-CRITICS
- Multiple perspectives needed? Yes: Policy, security, UX, cost critics needed -> N-CRITICS. No: Single perspective -> Reflexion or Self-Refine or CRITIC
- Tool feedback needed? Yes: Coding with test execution, refund with trust check needs real tool observation -> CRITIC or Reflexion. No: Writing where self-critique enough -> Self-Refine
- High-value task failure expensive? Yes: $500+ refund, coding, research -> Reflexion (90% success with memory, 2x cost worth it). No: $120 refund, simple FAQ -> ReAct or Self-Refine

### 7. Episodic Memory: Store and Retrieve Lessons

**What is episodic memory:**
- Store lessons from past trials as text with embedding, retrieve relevant lessons for similar tasks via vector search
- Unlike semantic memory (knowledge base), episodic memory is experience-based (what happened, what lesson)

**How to store:**
```
def store_lesson(task, lesson, reflection, error_code, trial):
    embedding = openai.embeddings.create(model="text-embedding-3-small", input=lesson).data[0].embedding
    memory.append({
        "task": task,
        "lesson": lesson,
        "reflection": reflection,
        "error_code": error_code,
        "embedding": embedding,
        "timestamp": now,
        "trial": trial
    })

store_lesson(
    task="Refund ORD-12345",
    lesson="Trust 70<80 need approval not auto refund. For trust <80 use request_approval not refund_order",
    reflection="Failed because trust 70 <80 threshold 80 per policy v2.3. Tried refund_order but policy requires approval for trust <80.",
    error_code="TRUST_LOW",
    trial=0
)
```

**How to retrieve:**
```
def retrieve_lessons(user_goal, memory, top_k=3):
    query_embedding = openai.embeddings.create(model="text-embedding-3-small", input=user_goal).data[0].embedding
    similarities = []
    for lesson in memory:
        sim = cosine_similarity(query_embedding, lesson["embedding"])
        similarities.append((lesson, sim))
    similarities.sort(key=lambda x: x[1], reverse=True)
    relevant = [lesson for lesson, sim in similarities if sim > 0.7][:top_k]
    return relevant

user_goal = "Refund ORD-67890 $200 trust 65"
relevant_lessons = retrieve_lessons(user_goal, memory, top_k=3)
# Returns lesson "Trust 70<80 need approval..." because trust 65 similar to trust 70, both <80
```

**Best practices:**
- Store lesson with error_code for filtering: TRUST_LOW, NOT_FOUND, INVALID_ARGS
- Store task, lesson, reflection, next_approach, avoid, timestamp, trial
- Generate embedding for lesson for vector search
- Retrieve top_k=3 relevant lessons similarity >0.7
- Add to history Previous lessons for similar tasks
- Manage growth limit 100 lessons delete old or summarize into community summaries GraphRAG
- Use Postgres + pgvector: CREATE TABLE lessons (id SERIAL, task TEXT, lesson TEXT, embedding VECTOR(1536), error_code TEXT, timestamp TIMESTAMPTZ)

**Benchmark:**
- No memory: Success 70% (ReAct fails same way repeatedly)
- With memory top_k=3 relevant lessons: Success 90% (+20%) because avoids same failure
- Cost: Embedding $0.0001 per lesson, storage negligible, retrieval 0.1s

### 8. Reflection Prompts: Good vs Bad

**Bad:** Failed, reflect why failed -> Response: Failed because something went wrong - vague, no lesson, no next approach

**Good:**
```
Goal: {user_goal}
History: {history}
Failure reason: {failure_reason}
Failed, reflect:
1. Why failed? What was root cause? Be specific, mention policy, trust, amount, tool, error code.
2. What lesson learned? Concise lesson for memory, reusable for similar tasks.
3. What different approach next trial? Specific tool and args.
4. What to avoid? What not to do next trial.

Return JSON with reflection, lesson, next_approach, avoid
```

Example good reflection:
- Goal: Refund ORD-12345 $120, History: get_order_status ->120 user_123, get_trust_score ->70, refund_order -> fails TRUST_LOW
- Failure reason: Trust 70 <80 need approval
- Response JSON: reflection Failed because trust 70 <80 threshold 80 per policy v2.3. Tried refund_order but policy requires approval for trust <80. Root cause: Did not check policy trust threshold before refund. Amount 120<500 okay but trust low fails policy. lesson Trust 70<80 need approval not auto refund. For trust <80 use request_approval not refund_order, next_approach For ORD-12345 trust 70, use request_approval with reason trust 70<80 per policy v2.3, amount 120, avoid Avoid refund_order when trust <80, always check trust before refund, check policy trust threshold

Lesson stored concise reusable includes error_code TRUST_LOW

**Best practices:**
- Be specific: Mention policy, trust, amount, tool, error code, root cause
- Structure: Why failed, lesson, next approach, avoid
- Return JSON: reflection, lesson, next_approach, avoid for easy parsing and storage
- Temperature: T=0.7 creative reflection, T=0.3 balanced evaluation
- Include history and failure reason in prompt
- Lesson should be concise, reusable, include error code

**Benchmark good vs bad reflection:**
- Bad vague: Success after retry 75% (lesson not reusable)
- Good specific with lesson: Success after retry 90% (+15%)

### 9. Benchmarks: Success Rate, Cost, Latency

| Pattern | Cost (3 tools) | Latency | Success Rate | Quality | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ReAct (no reflection) | 3 LLM calls cost 3x | 3s | 70% | 60% single shot | Default simple tasks |
| Reflexion | 9 calls max 3*3=3x vs ReAct 3 calls, avg 6 calls 2x | 9s max 3*3s=3x vs 3s, avg 6s 2x | 90% +20% over ReAct | N/A | High-value $500+ refunds coding research need self-correction with memory |
| Self-Refine | 6 calls (3 iter*2)=6x vs single 1 call, avg 3 calls 3x | 3s vs 1s=3x, avg 2s 2x | N/A | 85% vs 60% single +25% writing | Writing tasks email creative writing |
| N-CRITICS | 18 calls max 3 iter*(1 gen+4 critics+1 refine)=18x vs single, avg 12 calls 12x | 4.5s max 9x vs 0.5s, avg 3s 6x | N/A | 88% vs 70% single critic +18% | Complex tasks multiple perspectives policy security UX cost |
| CRITIC | 6 calls + tool executions | 3s | 85% vs 70% +15% | N/A | Tasks where tool feedback needed coding test refund trust check |

Detailed for refund $120:
- ReAct: 4 LLM calls =4x cost, 4s latency, 70% success (fails 30% when trust low need approval but tries refund)
- Reflexion: Trial1 fails trust low, reflects lesson need approval, Trial2 success with approval, 2 trials*4 calls=8 calls cost 8x vs ReAct 4 calls=2x cost, latency 8s vs 4s=2x latency, 90% success
- Self-Refine: For writing email 3 iter*2 calls=6 calls cost 6x vs single 1 call, 3s latency vs 1s=3x latency, quality 85% vs 60% +25%
- N-CRITICS: 4 critics parallel + generate + refine=6 calls per iteration, 2 iterations avg=12 calls cost 12x vs single 1 call, latency 3s vs 0.5s=6x, quality 88% vs 70% single critic +18%
- CRITIC: Similar to Reflexion but tool feedback, 6 calls + tool executions, 85% success vs 70% +15%

Recommendation:
- Simple low-value tasks ($120 refund, FAQ): ReAct (70% success, low cost, low latency)
- High-value tasks ($500+ refund, coding, research) where failure expensive: Reflexion (90% success, 2x cost and latency worth it)
- Writing tasks (email): Self-Refine (85% quality, 3x cost)
- Complex tasks with multiple perspectives (policy, security, UX, cost): N-CRITICS (88% quality, 12x cost)
- Tasks where tool feedback needed (coding with tests): CRITIC (85% success)

### 10. Implementation Blueprint - Production Agent with All Three

Production agent with Reflexion + Self-Refine + N-CRITICS hybrid:

- Step1: Reflexion with episodic memory: Try ReAct loop, evaluate success, fail -> reflection why failed root cause specific, lesson concise reusable, next approach specific tool args, avoid what not to do, store lesson in memory with embedding and error_code, retry with relevant lessons top_k=3 retrieved via vector search similarity >0.7, max trials 3.
- Step2: Self-Refine for writing final answer friendly: After success, refine final answer friendly with feedback loop max 2 iterations.
- Step3: N-CRITICS for complex high-value tasks: If high-value task, use N-CRITICS multiple critics policy security UX cost parallel critique + refine.

See previous module function_calling_vs_tool_calling.md for execute_tool, is_success, store_lesson, retrieve_lessons, self_refine, n_critics, is_high_value, production_agent_with_reflection full code.

Usage:
answer = asyncio.run(production_agent_with_reflection("Refund ORD-12345 $120"))
Answer: "Great news! Your refund of $120 for order ORD-12345 (Refund ID ref_123) has been processed and will appear in your account within 3-5 business days. Thanks for your patience!"
With reflection if trust low: Trial1 fails trust 70<80, reflects lesson need approval, Trial2 success with approval, refined with Self-Refine friendly, N-CRITICS checks policy security UX cost.

### 11. Failure Modes and Fixes

Failure 1: Reflection vague, no lesson
- Bad reflection: Failed because something went wrong - vague, no lesson, not reusable
- Result: Next trial fails same way, no improvement
- Fix: Good reflection prompt with structure: Why failed root cause specific policy trust amount tool error code, lesson concise reusable, next approach specific tool args, avoid what not to do. Return JSON reflection lesson next_approach avoid.

Failure 2: Memory grows unbounded, retrieval noisy
- Memory 1000 lessons, retrieval top_k=3 returns irrelevant lessons
- Result: Irrelevant lessons in prompt, confusion, success rate drops
- Fix: Limit memory size 100 lessons, delete old lessons, summarize lessons into community summaries (GraphRAG community detection), use vector search similarity threshold 0.7, retrieve top_k=3 relevant, filter by error_code.

Failure 3: Self-Refine feedback noisy, wrong
- Feedback: Output good but missing refund ID but output already has refund ID, feedback wrong
- Result: Refine removes refund ID, worse
- Fix: Use N-CRITICS multiple critics, aggregate feedback, check if feedback says perfect no improvement needed, use tool feedback CRITIC (real tool execution feedback) not just self-critique, temperature T=0.3 balanced feedback not T=0.7 creative noisy.

Failure 4: N-CRITICS critics conflict, cannot satisfy all
- Policy critic: Need approval for trust <80, Cost critic: Low-value $120 auto okay no need approval (conflict)
- Result: Cannot satisfy both, stuck
- Fix: Prioritize critics, policy critic highest priority, cost critic lower priority, aggregate feedback with priority, use weighted voting, or sequential critics: Policy first, then security, then UX, then cost.

Failure 5: Reflexion retries same failure, loop
- Trial1 fails trust low, reflection lesson need approval, Trial2 still tries refund_order not request_approval, fails again, loop
- Result: 3 trials fail same way, cost 3x, no success
- Fix: Check lesson in memory, force next approach from reflection next_approach field, use tool_choice specific tool to force request_approval, detect loop last 3 identical actions -> reflection T=0.7 creative alternative.

### 12. Production Checklist

1. Self-reflection turns failure into memory without retraining — Failure -> Verbal Reflection why failed what lesson (T=0.7 creative) -> Store lesson in episodic memory (vector DB) -> Retry with lesson in prompt -> Success without weight update. Cost 1 extra LLM call for reflection + memory + retry 2x cost for 20% success gain (70%->90%) worth for high-value tasks.

2. Reflexion: ReAct + Reflection + Episodic Memory + Retry max 3 trials — Try ReAct loop, Evaluate success refund_id approval_id, Fail -> Reflection why failed root cause specific policy trust amount tool error code, lesson concise reusable, next approach specific tool args, avoid what not to do, Return JSON reflection lesson next_approach avoid, Store lesson in memory with embedding and error_code, Retry with relevant lessons top_k=3 retrieved via vector search similarity >0.7, max trials 3. 90% success +20% over ReAct 70%, cost 9 calls max 3x vs ReAct 3 calls avg 6 calls 2x, latency 9s max 3x vs 3s avg 6s 2x, worth for $500+ refunds coding research.

3. Self-Refine: Generate->Feedback self-critique->Refine loop max 3 iterations — Generate initial T=0.7 creative, Feedback what wrong how to improve T=0.3 balanced, Refine based on feedback T=0.7 creative, loop until perfect or max iterations. 85% quality vs 60% single shot +25% for writing, cost 6 calls 6x vs single 1 call avg 3 calls 3x, latency 3s vs 1s 3x avg 2s 2x. Use for writing tasks email creative writing.

4. N-CRITICS: Multiple specialized critics parallel critique + Refine — Define critics Policy Security UX Cost, each specialized prompt, Multiple critics parallel 0.5s vs sequential 2s =75% latency cut, Aggregate feedback, Refine based on all feedback. 88% quality vs 70% single critic +18%, cost 18 calls max 18x vs single avg 12 calls 12x, latency 4.5s max 9x vs 0.5s avg 3s 6x. Use for complex tasks multiple perspectives needed.

5. CRITIC: Tool-augmented self-correction — Generate->Tool feedback real execution->Refine loop, tool feedback more accurate than self-critique. 85% success vs 70% +15% for tasks where tool feedback needed coding test refund trust check.

6. Episodic memory: Store lessons with embedding, retrieve relevant via vector search — Table lessons (id, task, lesson, reflection, error_code, embedding VECTOR, timestamp, trial), Store with error_code for filtering, embedding for vector search, Retrieve top_k=3 relevant similarity >0.7, Add to history Previous lessons for similar tasks, Manage growth limit 100 lessons delete old or summarize into community summaries GraphRAG. No memory 70% success, with memory top_k=3 90% +20% avoids same failure, cost embedding $0.0001 per lesson.

7. Reflection prompts good vs bad — Bad vague Failed something wrong no lesson not reusable -> success after retry 75%. Good specific with structure Why failed root cause specific policy trust amount tool error code, lesson concise reusable, next approach specific tool args, avoid what not to do, Return JSON reflection lesson next_approach avoid -> success after retry 90% +15%. Temperature T=0.7 creative reflection, T=0.3 balanced evaluation.

8. Hybrid production agent: Reflexion + Self-Refine + N-CRITICS — Reflexion for self-correction with memory 90% success, Self-Refine for writing final answer friendly 85% quality, N-CRITICS for complex high-value tasks with multiple perspectives 88% quality. Cost 7 calls avg 2.3x vs ReAct 3 calls, latency 6s avg 2x vs 3s, 90% success worth for high-value.

9. Failure modes and fixes — Reflection vague no lesson -> fix good prompt structure with JSON. Memory unbounded noisy retrieval -> fix limit 100 lessons delete old summarize community similarity threshold 0.7 top_k=3 filter error_code. Self-Refine feedback noisy wrong -> fix N-CRITICS multiple critics aggregate check perfect, use tool feedback CRITIC real observation, T=0.3 balanced not T=0.7 creative noisy. N-CRITICS critics conflict cannot satisfy all -> fix prioritize critics policy highest, weighted voting, sequential. Reflexion retries same failure loop -> fix check lesson force next approach from reflection next_approach field tool_choice specific tool force request_approval detect loop last 3 identical -> reflection T=0.7 creative alternative.

10. Observability — Log pattern used Reflexion Self-Refine N-CRITICS CRITIC, cost, latency, success rate, quality, reflection lesson, memory size, retrieval similarity, error code, valid JSON rate, loop detected, in ClickHouse. Alert if success rate <80% need Reflexion, quality <80% need Self-Refine or N-CRITICS, memory size >100 need cleanup, retrieval similarity <0.7 irrelevant lessons.

---
**Bottom Line:** Self-reflection turns failure into memory without retraining: Failure -> Verbal Reflection why failed what lesson (T=0.7 creative) -> Store lesson in episodic memory (vector DB) with embedding and error_code -> Retry with relevant lessons top_k=3 retrieved via vector search similarity >0.7 -> Success without weight update. Reflexion = ReAct + Reflection why failed root cause specific + Episodic Memory + Retry max 3 trials, 90% success +20% over ReAct 70%, cost 9 calls max 3x vs ReAct 3 calls avg 6 calls 2x, latency 9s max 3x vs 3s avg 6s 2x, worth for high-value $500+ refunds coding research where failure expensive and lesson reusable trust <80 need approval. Self-Refine = Generate->Feedback self-critique what wrong how improve (T=0.3 balanced)->Refine based on feedback (T=0.7 creative) loop max 3 iterations, 85% quality vs 60% single +25% for writing, cost 6 calls 6x vs single 1 call avg 3 calls 3x, latency 3s vs 1s 3x avg 2s 2x, use for writing tasks email. N-CRITICS = Multiple specialized critics Policy Security UX Cost parallel critique 0.5s vs sequential 2s 75% latency cut + Refine based on all feedback, 88% vs 70% single critic +18%, cost 18 calls max 18x vs single 1 call avg 12 calls 12x, latency 4.5s max 9x vs 0.5s avg 3s 6x, use for complex tasks multiple perspectives needed. CRITIC = Tool-augmented self-correction Generate->Tool feedback real execution->Refine, 85% vs 70% +15% for tasks where tool feedback needed. Production hybrid: Reflexion for self-correction with memory 90% + Self-Refine for writing friendly 85% + N-CRITICS for complex high-value 88%. Always good reflection prompt structure Why failed lesson next approach avoid Return JSON, store lesson concise reusable, manage memory growth limit 100.
