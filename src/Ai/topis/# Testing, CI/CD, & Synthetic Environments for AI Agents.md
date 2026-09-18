# Testing, CI/CD, & Synthetic Environments for AI Agents

## 1. The Challenge of Testing Non-Deterministic Agents
Traditional software testing relies on deterministic assertions: given input $X$, output must equal $Y$. 

AI agents, however, are fundamentally stochastic and non-deterministic. An agent may take 4 steps today and 6 steps tomorrow to achieve the exact same goal, or choose alternative API calls based on slight model variance or updated web contexts. 

Testing agents therefore requires shifting from **deterministic unit tests** to **probabilistic assertions, trajectory analysis, and synthetic simulation environments**.

---