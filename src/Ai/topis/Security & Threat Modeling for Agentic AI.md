Security & Threat Modeling for Agentic AI
OWASP Top 10 for LLM Agents and Defense-in-Depth
Core Thesis: An agent is not just an LLM — it is an LLM with tools, memory, and autonomy that can read your database, send emails, and spend money. Traditional LLM safety (no toxicity) is insufficient. You need threat modeling for what happens when an agent is tricked into doing something destructive, not just saying something bad.

Table of Contents
Why Agent Security is Different from LLM Security
OWASP Top 10 for LLM Agents (2025-2026)
Prompt Injection & Indirect Injection Deep Dive
Tool Poisoning & MCP/A2A Threats
Data Exfiltration & Memory Poisoning
Defense-in-Depth Architecture
Implementation Blueprint
Red Teaming & Continuous Testing


1. Why Agent Security is Different from LLM Security
LLM security: Prevent model from saying disallowed content (toxicity, bias, illegal advice).

Agent security: Prevent model from doing disallowed actions via tools — deleting database, refunding $10K, sending phishing email from your domain, exfiltrating PII to external URL.

Attack surface multiplies:

LLM alone: Input -> Output (text)
Agent: Input + Tool Outputs (untrusted web pages, docs) + Memory (poisoned past episodes) + MCP Servers (third-party code) + A2A Agents (other agents) -> Actions (API calls, DB writes, emails)
Each new input is a potential injection vector.