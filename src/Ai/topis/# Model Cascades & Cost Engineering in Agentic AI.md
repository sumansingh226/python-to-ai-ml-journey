## 4. Cascading Strategies

### A. Fallback Cascading (Speculative Escalation)
The agent executes the task using a cheap Tier 2 model first. If output validation fails (e.g., JSON schema fails validation, or a unit test fails), the system intercepts the error and escalates the step to a Tier 3 frontier model, passing the failed attempt as negative feedback.

### B. Router Cascading (Complexity-Based Dispatch)
A fast classifier or semantic router inspects the incoming sub-task. If the task is labeled low-complexity (e.g., "Extract order status from JSON"), it routes directly to Tier 1/2. If the task requires architectural trade-offs or multi-variable logic, it routes directly to Tier 3.

### C. Self-Consistency Verification Cascade
Multiple cheap models generate candidate answers in parallel. If their outputs agree with high consensus, the answer is accepted. Only when candidate answers diverge is a frontier model engaged as an arbitrator.

---

## 5. Token Budgeting & Dynamic Halting

To prevent runaway spend, production agents enforce hard token and financial guardrails at the orchestrator level:

* **Trace-Level Token Caps:** Assigning a maximum token ceiling per user goal (e.g., maximum 100,000 tokens total per task).
* **Step-Count Quotas:** Setting a hard limit on trajectory depth (e.g., maximum 10 tool iterations).
* **Cost Velocity Throttling:** Monitoring burn rate ($USD per minute). If an agent exceeds expected spend velocity, execution is suspended and escalated to an Approval Gate.
* **Graceful Degradation:** When an agent reaches 85% of its token budget without completing the goal, it switches from an "exploration" prompt to a "wrap-up" prompt, instructing it to synthesize the best possible partial answer with its remaining budget.
