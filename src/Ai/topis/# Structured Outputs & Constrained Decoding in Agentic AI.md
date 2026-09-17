# Structured Outputs & Constrained Decoding in Agentic AI
## Making Non-Deterministic Models Deterministically Useful

> **Core Thesis:** An LLM that can write beautiful prose but cannot reliably output valid JSON is useless in production. Structured Outputs and Constrained Decoding force models to obey schemas at the token level, turning stochastic text generators into reliable system components.

### Table of Contents
1. [The Problem: Why Freeform Text Breaks Agents](#1-the-problem-why-freeform-text-breaks-agents)
2. [What are Structured Outputs?](#2-what-are-structured-outputs)
3. [Constrained Decoding: How It Works Under the Hood](#3-constrained-decoding-how-it-works-under-the-hood)
4. [The Three Levels of Enforcement](#4-the-three-levels-of-enforcement)
5. [Core Implementation Patterns](#5-core-implementation-patterns)
6. [Advanced Techniques](#6-advanced-techniques)
7. [When to Use What: Decision Framework](#7-when-to-use-what-decision-framework)
8. [Enterprise Production Checklist](#8-enterprise-production-checklist)
9. [Common Anti-Patterns](#9-common-anti-patterns)

---

### 1. The Problem: Why Freeform Text Breaks Agents

Agentic workflows depend on models calling tools. Tool calling requires exact JSON:

```json
{
  "tool": "get_order_status",
  "parameters": { "order_id": "ORD-12345" }
}
```

But LLMs are probabilistic next-token predictors. Without constraints, they will:

- Add conversational fluff: `Sure! Here is the JSON: {...}`
- Hallucinate fields: `"order_id": "12345 and also..."` 
- Break JSON syntax: missing quotes, trailing commas
- Change schema: returning `orderId` instead of `order_id`

In a Level 2 Router Workflow, one malformed tool call crashes the entire loop. Studies show even top models fail JSON schema adherence 5-15% of the time in long-horizon tasks without enforcement.

You cannot prompt your way to 100% reliability. You need enforcement at the decoding layer.

### 2. What are Structured Outputs?

**Structured Outputs** is a guarantee from the inference provider that the model's output will *always* match a supplied JSON Schema, Pydantic model, or regex.

Not a suggestion. A guarantee.

**Example: Pydantic to Schema**

```python
from pydantic import BaseModel, Field
from enum import Enum

class Priority(str, Enum):
    low = "low"
    high = "high"
    critical = "critical"

class SupportTicket(BaseModel):
    order_id: str = Field(pattern=r"^ORD-\d{5}$")
    issue_type: str
    priority: Priority
    confidence: float = Field(ge=0, le=1)
```

If you pass this as `response_format`, the API will *never* return invalid JSON, never return a wrong enum, and never return an order_id that doesn't match `^ORD-\d{5}$`.

### 3. Constrained Decoding: How It Works Under the Hood

This is not post-processing validation. Validation says "you failed, try again." Constrained decoding says "you *cannot* fail."

How it works at token generation time:

1.  **Schema -> Finite State Machine (FSM):** Your JSON Schema is compiled into a state machine or Context-Free Grammar (CFG). Each state represents what tokens are valid next.

2.  **Logit Masking:** At each decoding step, the LLM produces logits for all 100K+ possible tokens. The constrained decoder masks (sets to -infinity) all tokens that would lead to an invalid state transition.

3.  **Forced Compliance:** The model can only sample from tokens that keep the output schema-valid. The string `{"order_id":` *must* be followed by a `"` because the FSM says so.

**Key Libraries & Engines:**
- **Outlines:** Most popular library for FSM/CFG guided generation
- **Guidance (Microsoft):** Handles complex interleaving of text + structure
- **LMQL, XGrammar:** High-performance constrained decoding engines used by vLLM, SGLang
- **Provider Native:** OpenAI Structured Outputs, Gemini `responseSchema`, Anthropic Tool Use with strict JSON

This is why it costs slightly more latency — you are running a grammar engine alongside the LLM.

### 4. The Three Levels of Enforcement

| Level | Method | Reliability | Latency | How |
| :--- | :--- | :--- | :--- | :--- |
| **L1: Prompting** | "Return ONLY valid JSON" | ~85-90% | Low | Hope. System prompt instructions. |
| **L2: Validation + Retry** | Generate -> JSON Schema Validator -> If fail, re-prompt with error | ~95-98% | Medium-High (2x calls on failure) | Post-processing |
| **L3: Constrained Decoding** | Logit masking at token level via FSM/CFG | 100% schema compliant | Low-Medium (single pass, but masking overhead) | At inference time |

**Production Rule:** For any tool call, extraction, or router decision, you must use L3. L1 and L2 are for prototypes.

### 5. Core Implementation Patterns

#### Pattern A: Tool Calling (Function Calling)

This is the most common use. You define tools as JSON Schemas and the model must output a tool call that matches exactly.

```python
# OpenAI Native Structured Tool Calling
client.chat.completions.create(
  model="gpt-4o",
  tools=[{
    "type": "function",
    "function": {
      "name": "get_order_status",
      "description": "Get status of an order",
      "parameters": {
        "type": "object",
        "properties": {
          "order_id": {"type": "string", "pattern": "^ORD-\\d{5}$"}
        },
        "required": ["order_id"]
      }
    }
  }],
  tool_choice="required"
)
# Output is GUARANTEED to be valid for get_order_status
```

#### Pattern B: Structured Extraction

Extracting entities from unstructured text into a typed object.

```python
# LangChain + Pydantic
from langchain_core.output_parsers import PydanticOutputParser

parser = PydanticOutputParser(pydantic_object=SupportTicket)
# The parser injects schema instructions AND the underlying LLM call uses constrained decoding
```

Use for: Invoice extraction, resume parsing, log classification.

#### Pattern C: Router Decisions & Classification

Force the model to output one of N valid routes.

```python
class RouteDecision(BaseModel):
    route: Literal["search_docs", "escalate_human", "refund_tool"]
    reasoning: str # You can still allow freeform text INSIDE structured fields
    confidence: float
```

This eliminates the classic "model returned 'search_docs ' with a trailing space and broke my if/else".

#### Pattern D: Regex and Format Enforcement

You can constrain to any regex: dates, IDs, SQL, etc.

```python
# Outlines example: Force valid email + no hallucination
import outlines

model = outlines.models.transformers("mistralai/Mistral-7B")
generator = outlines.generate.regex(model, r"[a-z]+@company\.com")
result = generator("Generate a company email:")
# Will ALWAYS match regex
```

### 6. Advanced Techniques

**a) Nested and Recursive Schemas:**
Constrained decoding supports deeply nested JSON. You can enforce `List[SupportTicket]` with 10 tickets, each with validated fields. The FSM handles it.

**b) Chain-of-Thought Inside Structure:**
Don't lose reasoning. Structure can contain reasoning fields:

```json
{
  "chain_of_thought": "User is angry because order is 5 days late, need to check status first...",
  "tool_to_call": "get_order_status",
  "parameters": {"order_id": "ORD-12345"}
}
```

Force CoT to be inside the JSON, not outside.

**c) Grammar for Code Generation:**
Instead of JSON Schema, you can constrain to a full grammar: Only generate valid Python, valid SQL, valid Cypher queries. XGrammar can enforce Python syntax at token level.

**d) Speculative Decoding + Constraints:**
Modern engines like vLLM combine speculative decoding (fast) with XGrammar constraints to keep latency low even with heavy schemas.

### 7. When to Use What: Decision Framework

| Scenario | Recommended Approach |
| :--- | :--- |
| Simple tool calling with 2-3 tools | Provider native Structured Outputs (OpenAI, Anthropic, Gemini) |
| Complex nested Pydantic with regex validation | Outlines or Guidance + vLLM/SGLang |
| Need to guarantee valid code (SQL, JSON, XML) | XGrammar or Guidance with CFG |
| Classification / Routing | Constrained `Literal` enum |
| High-throughput extraction pipeline | vLLM + XGrammar server with cached schemas |
| Prototyping only | Prompting is okay |

### 8. Enterprise Production Checklist

1.  **Always define Pydantic models, not raw JSON dicts:** Single source of truth, reusable, type-checked.

2.  **Set `strict: true`:** In OpenAI and others, enable strict mode to enforce `additionalProperties: false`.

3.  **Compile schemas once:** FSM compilation is expensive. Cache compiled FSMs/grammars on server startup.

4.  **Observability:** Log schema validation failures even though L3 should have 0%. If you see failures, your constraint engine is not active.

5.  **Combine with Caching:** Put your JSON Schemas in the stable cached prefix. They are large and static. This saves cost per § Context Caching.

6.  **Handle Refusals Gracefully:** Constrained decoding forces structure, but the model can still refuse inside the structure: `{"error": "Cannot comply"}`. Your schema should allow for error states.

7.  **Test with Adversarial Inputs:** Prompt injection often tries to break out of JSON. Test with `"}]} Ignore previous...` payloads. Constrained decoding is also a security boundary.

### 9. Common Anti-Patterns

1.  **Post-hoc `json.loads` without constraints:** Wrapping `json.loads(llm_output)` in a try/except and retrying is L2 at best. In production loops, this causes infinite retry storms.

2.  **Allowing `additionalProperties: true`:** Lets the model hallucinate new fields that break downstream code.
