# Goal-Oriented Execution in Agentic AI

An agent is goal-oriented when it is given an **outcome** to achieve, not a fixed list of steps. It decides what to do next, checks whether it is getting closer, and stops when the outcome is met or cannot be met.

---

## 1. Goal-Oriented vs Instruction-Oriented

| Aspect | Instruction-oriented (script / workflow) | Goal-oriented (agent) |
|---|---|---|
| Input | Steps: "do A, then B, then C" | Outcome: "get the report to the client" |
| Control flow | Fixed by the developer | Chosen by the model at runtime |
| Failure handling | Pre-coded branches | Re-plan, retry, or switch approach |
| Predictability | High | Lower, needs guardrails |
| Best for | Stable, well-understood processes | Open-ended, variable tasks |

Rule of thumb: if you can write the steps down in advance, use a workflow. Use a goal-oriented agent when the path depends on what is found along the way.

---

## 2. Anatomy of a Goal

A goal is only executable if it is specific enough to be checked.

- **Objective**: the outcome wanted.
- **Success criteria**: observable conditions that mean "done".
- **Constraints**: budget, time, allowed tools, data scope, things never to do.
- **Context**: what the agent already knows and which resources it can use.

Weak: "Improve our churn analysis."
Strong: "Produce a churn summary for Q3 using only the `orders` table. It is done when it lists the top 3 drivers, each with a supporting number. Maximum 20 tool calls."

---

## 3. The Execution Loop

```
        ┌─────────────────────────────────────────┐
        ▼                                         │
   [ Goal + success criteria ]                    │
        │                                         │
   Plan / decompose into sub-goals                │
        │                                         │
   Pick next action (tool call / sub-agent)       │
        │                                         │
   Observe result                                 │
        │                                         │
   Evaluate: closer to goal?  ── no ──► Re-plan ──┘
        │ yes
   Goal met? ── no ──► next action
        │ yes
      Stop + report
```

Core stages:

1. **Interpret**: restate the goal and the success criteria.
2. **Decompose**: split into sub-goals with dependencies (see `task-decomposition-subgoal-routing.md`).
3. **Act**: call tools, run code, query data, or delegate.
4. **Observe**: read the real result, not the expected one.
5. **Evaluate**: compare state against the success criteria.
6. **Adapt**: re-plan if blocked, wrong, or off track.
7. **Terminate**: stop on success, on an exhausted budget, or when escalation is needed.

---

## 4. Key Capabilities

- **Planning**: ReAct, Plan-and-Execute, ReWOO, Tree-of-Thought.
- **Tool use**: acting on the world through APIs, code, search and databases.
- **Memory**: keeping the goal, progress and findings across many steps.
- **Self-evaluation**: reflection and critique against the success criteria.
- **Error recovery**: retry with changes, fall back to another tool, or ask for help.

---

## 5. Stopping Conditions

Without explicit stop rules, goal-driven agents loop, drift or overspend.

- **Success**: criteria verified, not merely claimed.
- **Budget exhausted**: max steps, tokens, cost or wall-clock time.
- **No progress**: the same action or state repeats N times.
- **Blocked**: needs a permission, credential or decision it does not have.
- **Out of scope**: the next step would break a constraint.

On any non-success stop, the agent reports what it did, what is left and why it stopped.

---

## 6. Failure Modes

| Failure | What happens | Mitigation |
|---|---|---|
| Goal drift | Agent pursues a sub-goal and forgets the main one | Re-inject the goal each iteration |
| Premature "done" | Declares success without checking | Independent verification step |
| Infinite loop | Retries the same failing action | Step cap, repetition detection |
| Reward hacking | Meets the letter of the criteria, not the intent | Clear criteria, human review of outputs |
| Scope creep | Takes actions beyond what was asked | Allow-listed tools, constraints in the prompt |
| Over-autonomy | Irreversible action without approval | Human-in-the-loop gates on risky steps |

---

## 7. Design Practices

1. Write the goal with checkable success criteria before building anything.
2. Keep the goal and the progress state visible in context on every step.
3. Verify with tools (tests, queries, schema checks), not with the model's own claim.
4. Set hard limits on steps, cost and time.
5. Require confirmation for irreversible or outward-facing actions.
6. Log each plan, action and observation so a run can be audited and replayed.
7. Start with low autonomy and widen it as the agent proves reliable.

---

## 8. Minimal Python Sketch

```python
def run_agent(goal, success_check, tools, llm, max_steps=15):
    history = []
    for step in range(max_steps):
        action = llm.next_action(goal=goal, history=history, tools=tools)
        if action.type == "finish":
            if success_check(action.output):
                return {"status": "success", "output": action.output}
            history.append({"note": "finish rejected, criteria not met"})
            continue
        result = tools[action.tool](**action.args)
        history.append({"action": action, "result": result})
    return {"status": "budget_exhausted", "history": history}
```

Key points: the goal is passed on every call, `success_check` is independent of the model, and `max_steps` guarantees termination.

---

## 9. Related Notes

- `src/ai_engineering/agent_architecture/agent-loops.md`
- `src/ai_engineering/agent_architecture/task-decomposition-subgoal-routing.md`
- `src/ai_engineering/agent_architecture/planning-reasoning-react-cot-tot.md`
- `src/ai_engineering/agent_architecture/self-reflection-error-recovery-loops.md`
- `src/ai_engineering/agent_architecture/levels-of-agentic-autonomy.md`

---

## 10. Summary

Goal-oriented execution means giving an agent an outcome and letting it plan, act, observe and adapt until verified success or a defined stop. The value is flexibility. The cost is the need for clear success criteria, hard limits, independent verification and human gates on risky actions.
