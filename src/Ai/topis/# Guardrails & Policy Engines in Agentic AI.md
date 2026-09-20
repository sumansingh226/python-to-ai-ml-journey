# Guardrails & Policy Engines in Agentic AI

## 1. The "Prove It" Problem
AI agents inherently operate on probability, interpreting prompts at runtime and producing varying outputs [cite: 1.2.2]. For enterprise adoption, this variance is unacceptable. When a regulator or customer asks why a decision was made, organizations must solve the "prove it" problem by showing the exact rules and inputs that produced the outcome [cite: 1.2.1]. 

**Guardrails** and **Policy Engines** provide this missing layer of deterministic control, compliance, and security [cite: 1.2.1][cite: 1.2.2].

---

## 2. Agent Guardrails (The Boundary Layer)
Guardrails sit at the boundary of the language model, screening what goes in and what comes out [cite: 1.1.4]. 

* **Input Guardrails:** These intercept user prompts and tool results before the LLM processes them [cite: 1.1.4]. They block adversarial prompt injections, enforce topic constraints, and sanitize external data [cite: 1.1.4].
* **Output Guardrails:** These analyze model responses before they are returned or trigger actions [cite: 1.1.3]. They catch inadvertently generated PII, flag hallucinated facts, filter toxic content, and validate structured outputs [cite: 1.1.4].
* **Action Gates:** These evaluate tool calls before execution to verify permissions (e.g., checking IAM roles) [cite: 1.1.4]. A spike in denied tool calls acts as an early indicator of misbehaving agents or active capability abuse [cite: 1.1.4].
