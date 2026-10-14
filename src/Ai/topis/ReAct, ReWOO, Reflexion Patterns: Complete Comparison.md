ReAct, ReWOO, Reflexion Patterns: Complete Comparison
From Reasoning + Acting to Reasoning Without Observation to Self-Correction
Core Thesis: ReAct = Reasoning + Acting loop Thought->Action->Observation, most used, 70% success, simple. ReWOO = Reasoning Without Observation, plans all tool calls upfront without observations, 50% latency cut, 30% cost cut, 80% success when tools independent. Reflexion = ReAct + Reflection (why failed) + Retry with memory, 90% success (+20% over ReAct) with 2x cost. Production: Use ReAct default, ReWOO when tools independent (get_order + get_policy + get_trust parallel), Reflexion when high-value tasks need self-correction ($500+ refunds, coding).

Table of Contents