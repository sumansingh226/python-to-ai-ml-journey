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

## 3. Policy Engines (The Deterministic Layer)
A policy engine converts plain English business rules into compiled, versioned execution logic [cite: 1.2.2]. It defines what the agent can do, when it must escalate to a human, and how decisions are logged [cite: 1.2.2].

* **Execution Plans:** Policies are parsed into directed acyclic graphs (DAGs) before any processing begins [cite: 1.2.2]. The plan does not change dynamically at runtime [cite: 1.2.2].
* **Hybrid Execution:** The engine separates deterministic operations (like numeric comparisons or field validation, which run in milliseconds with zero token cost) from judgment calls (which use structured LLM extraction) [cite: 1.2.2].
* **Escalation Triggers:** Policies define strict "Human-in-the-Loop" (HITL) checkpoints for scenarios involving high value, high risk, or low confidence [cite: 1.2.1].

---

## 4. Prominent Open-Source Frameworks

### NVIDIA NeMo Guardrails
* An open-source toolkit that enables developers to add programmable guardrails and control conversation flows using a state-machine approach [cite: 1.1.1][cite: 1.1.3]. 
* It uses a language called Colang to define the dialog paths and behaviors [cite: 1.1.1]. 
* It