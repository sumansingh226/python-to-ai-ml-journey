# Prompts and Types of Prompts in AI

## 1. What is a Prompt?
A **prompt** is the natural language text, instruction, or code snippet provided to a Large Language Model (LLM) to elicit a specific output. In the era of generative AI, prompting is the primary interface layer between human intent and machine execution. 

A well-engineered prompt reduces ambiguity, provides necessary context, and structures the AI's generation process to yield accurate, deterministic, and highly relevant results.

---

## 2. Anatomy of a Prompt
A robust, production-grade prompt usually consists of four distinct components:
* **Instruction:** The specific task or directive you want the model to perform (e.g., "Summarize this article," "Write a Python script").
* **Context:** Background information that scopes the model's understanding (e.g., "You are a senior database administrator diagnosing a Sev-1 outage").
* **Input Data:** The actual payload or text the model needs to process (e.g., the raw text of the article, or the error logs).
* **Output Indicator:** The desired format of the response (e.g., "Return the result strictly as a JSON object," or "Provide a bulleted list").

---

## 3. Core Types of Prompts (Techniques)

### A. Zero-Shot Prompting
* **Definition:** Asking the model to perform a task without providing any examples of the desired input-output pairs. 
* **Example:** "Classify the sentiment of this review as Positive, Neutral, or Negative: 'The battery life is terrible.'"
* **Use Case:** Broad, general knowledge tasks where the model's pre-training is sufficient.

### B. Few-Shot Prompting (In-Context Learning)
* **Definition:** Providing the model with a few examples (1 to 5) of the desired input and output before giving it the actual task. This teaches the model the exact pattern, tone, or format required.
* **Example:** 
  `Review: The UI is clunky. -> Sentiment: Negative`
  `Review: I love the new dark mode! -> Sentiment: Positive`
  `Review: It crashes on startup. -> Sentiment: `
* **Use Case:** Highly specific formatting tasks, domain-specific classification, or overriding the model's default conversational tone.

### C. System Prompts
* **Definition:** A persistent, overarching instruction that dictates the model's behavior, persona, and boundaries for an entire conversation or agentic loop. It operates at a higher privilege level than user queries.
* **Example:** "You are an internal HR assistant. You must never reveal employee salary data. If asked, reply 'I cannot disclose that.' Always speak in a professional tone."
* **Use Case:** Guardrails, setting personas for multi-agent frameworks, and defining core application logic.

### D. Role-Playing (Persona Prompting)
* **Definition:** Instructing the model to adopt a specific identity or professional expertise before executing a task. 
* **Example:** "Act as a Staff Software Engineer reviewing a junior developer's pull request. Provide constructive feedback on this React component."
* **Use Case:** Unlocking specific domain vocabularies and mimicking expert-level critiques.

---

## 4. Advanced Reasoning Prompts (Agentic Prompting)

### A. Chain-of-Thought (CoT) Prompting
* **Definition:** Forcing the model to output its intermediate reasoning steps before providing the final answer. Often triggered by adding the phrase "Let's think step by step."
* **Use Case:** Complex mathematical word problems, logic puzzles, and multi-step data analysis where zero-shot attempts result in hallucinations.

### B. Least-to-Most Prompting
* **Definition:** Breaking a complex problem into smaller sub-problems, and asking the model to solve each sub-problem sequentially. The answer to the previous sub-problem is appended to the prompt for the next one.
* **Use Case:** highly complex routing tasks and multi-variable logic problems that overwhelm standard CoT.

### C. Meta-Prompting
* **Definition:** Prompting an LLM to write, refine, or critique a prompt for another LLM.
* **Use Case:** Automated prompt optimization pipelines (like DSPy) where the system continuously rewrites its own instructions to achieve a higher score on an evaluation benchmark.