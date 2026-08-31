# Task Decomposition & Sub-goal Routing in Agentic AI


## 1. What is Task Decomposition & Sub-goal Routing?
When a human receives a massive, ambiguous project (e.g., "Organize a tech conference for 500 people"), they don't try to do it all in one chaotic step. They break it down into smaller, actionable items: venue booking, speaker outreach, catering, and marketing. 

In Agentic AI:
* **Task Decomposition** is the process of an LLM taking a broad, complex user prompt and breaking it down into a structured sequence or graph of smaller, deterministic sub-tasks.
* **Sub-goal Routing** is the orchestration mechanism that takes those smaller sub-tasks and assigns them to the appropriate specialized tool, API, or sub-agent to be executed.


## 2. Why is it Used?
* **Managing Complexity:** LLMs struggle to maintain focus and logic over very long horizons in a single zero-shot generation. Breaking tasks down ensures higher accuracy for each individual step.
* **Specialization (Expertise):** Instead of one monolithic "God Model" trying to do everything, you can route tasks to specialized agents (e.g., routing a math sub-task to a Python-executing agent, and a creative writing sub-task to Claude 3.5).
* **Parallel Execution:** If a plan requires gathering data on three different competitors, task decomposition allows the system to route those three sub-goals to run in parallel, drastically reducing latency.
* **Deterministic Fallbacks:** If step 3 of a 10-step plan fails, the agent only needs to retry or re-route step 3, rather than starting the entire prompt over from scratch.
