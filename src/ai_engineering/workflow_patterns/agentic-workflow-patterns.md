# Agentic Workflow Patterns: Chaining, Routing, Parallelization, Orchestrator-Workers, Evaluator-Optimizer

## 1. Workflows vs Agents

| | Workflow | Agent |
|---|---|---|
| Control flow | Fixed in code, LLM fills the steps | LLM decides the next step |
| Predictability | High | Lower |
| Cost / latency | Lower, bounded | Higher, open-ended |
| Debugging | Easy, each step is inspectable | Harder, path varies per run |
| Best for | Well-understood tasks | Open-ended tasks where steps can't be predicted |

Rule of thumb: start with a single LLM call, add retrieval and tools, then move to a workflow, and only use a full agent when the path truly cannot be written down in advance.

## 2. The Five Core Patterns

### 2.1 Prompt Chaining
Break a task into a fixed sequence. Each step's output feeds the next, with optional programmatic **gates** between steps.

```
Input -> LLM 1 -> [gate] -> LLM 2 -> [gate] -> LLM 3 -> Output
```

- Use when the task decomposes cleanly into subtasks.
- Trades latency for accuracy: each call is simpler.
- Examples: write an outline, check it, then write the document; generate copy, then translate it.
- Gate ideas: schema validation, length check, a cheap classifier, a regex.

```python
def chain(llm, text):
    outline = llm(f"Create an outline for: {text}")
    if len(outline.splitlines()) < 3:
        raise ValueError("outline too short")
    draft = llm(f"Write the document from this outline:\n{outline}")
    return llm(f"Edit for clarity and tone:\n{draft}")
```

### 2.2 Routing
Classify the input, then send it to a specialised prompt, model or tool chain.

```
Input -> Classifier -> Route A (specialised prompt)
                    -> Route B (specialised prompt)
                    -> Route C (cheap model)
```

- Use when inputs fall into distinct categories that need different handling.
- Enables **model routing**: easy queries to a small model, hard ones to a large model.
- Examples: support tickets (billing / technical / refund), query difficulty routing.
- Failure mode: misclassification. Add a fallback route and log low-confidence classifications.

```python
ROUTES = {"billing": billing_chain, "technical": tech_chain, "other": general_chain}

def route(llm, query):
    label = llm(f"Classify as billing, technical or other. Reply with one word:\n{query}").strip().lower()
    return ROUTES.get(label, general_chain)(query)
```

### 2.3 Parallelization
Run LLM calls at the same time and aggregate. Two variants:

- **Sectioning**: split a task into independent subtasks and run them in parallel.
- **Voting**: run the same task several times and aggregate the results for confidence.

```
          -> LLM A ->
Input ->  -> LLM B ->  Aggregator -> Output
          -> LLM C ->
```

- Sectioning examples: guardrail check running alongside the main answer; evaluating several criteria at once.
- Voting examples: multiple code-vulnerability reviews; multiple prompts judging whether content is unsafe.
- Cost scales with the number of branches. Latency stays roughly that of the slowest branch.

```python
import asyncio

async def parallel(llm, prompts):
    return await asyncio.gather(*(llm(p) for p in prompts))

def majority(votes):
    return max(set(votes), key=votes.count)
```

### 2.4 Orchestrator-Workers
A central LLM decides the subtasks **dynamically**, delegates them to worker LLMs, then synthesises the results.

```
Input -> Orchestrator -> Worker 1 --\
                      -> Worker 2 ---> Orchestrator (synthesis) -> Output
                      -> Worker N --/
```

- Looks like parallelization, but the subtasks are not known in advance.
- Use when the number and kind of subtasks depend on the input.
- Examples: coding changes that touch an unknown number of files; multi-source research.
- Risks: orchestrator picks wrong subtasks, workers lack shared context, synthesis loses detail. Pass each worker only the context it needs, and require structured outputs.

### 2.5 Evaluator-Optimizer
One LLM generates, another evaluates and gives feedback, in a loop until the criteria pass or a limit is hit.

```
Input -> Generator -> Evaluator --pass--> Output
            ^            |
            +--feedback--+
```

- Use when there are clear evaluation criteria and iteration measurably improves quality.
- Examples: translation with nuance, search tasks needing several rounds, code that must pass tests.
- Always set a **max iteration** count and a stop condition to avoid infinite loops.

```python
def refine(llm, task, max_rounds=3):
    draft = llm(task)
    for _ in range(max_rounds):
        review = llm(f"Review against the task. Reply PASS or give feedback.\nTask: {task}\nDraft: {draft}")
        if review.strip().startswith("PASS"):
            return draft
        draft = llm(f"Task: {task}\nDraft: {draft}\nFeedback: {review}\nRevise.")
    return draft
```

## 3. Choosing a Pattern

| Situation | Pattern |
|---|---|
| Fixed steps, each easier than the whole | Prompt chaining |
| Different input types need different handling | Routing |
| Independent subtasks, or need confidence | Parallelization |
| Subtasks unknown until the input is seen | Orchestrator-workers |
| Quality improves with critique | Evaluator-optimizer |
| Steps and tools unpredictable, long-horizon | Autonomous agent |

## 4. Combining Patterns

Patterns compose. Common combinations:

- Routing -> chaining: route the request, then run a type-specific chain.
- Orchestrator-workers with evaluator-optimizer on the final synthesis.
- Parallel guardrails around any of the above.
- Chaining where one step is itself an autonomous agent with tools.

## 5. Production Considerations

- **Observability**: trace every step and branch with a shared run ID; log inputs, outputs, latency and token cost per node.
- **Failure handling**: timeouts, retries with backoff, and a defined fallback per node. Parallel branches should tolerate one branch failing.
- **Cost control**: cap iterations, branch counts and total tokens per run; route easy work to smaller models.
- **Testing**: evaluate each node on its own as well as end to end. Gates and routers deserve their own test sets.
- **State**: keep intermediate results explicit (typed objects, not free text) so a run can be resumed or replayed.
- **Human checkpoints**: place approval gates before irreversible actions.

## 6. Common Mistakes

1. Using an agent where a two-step chain would do.
2. Chains with no validation gates, so errors compound silently.
3. Evaluator and generator sharing the same blind spots (same model, same prompt style).
4. Unbounded evaluator-optimizer loops.
5. Orchestrators that send full context to every worker, inflating cost.
6. Frameworks hiding prompts and responses, which makes debugging hard. Start with plain API calls and add a framework only when it clearly helps.

## 7. Summary

Pick the simplest pattern that solves the problem, measure it, and add complexity only when the measurements justify it. Chaining and routing cover most real workloads; parallelization, orchestrator-workers and evaluator-optimizer add power at a cost in latency and spend; fully autonomous agents come last.
