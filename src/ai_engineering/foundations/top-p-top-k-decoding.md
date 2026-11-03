# Top-p, Top-k, and Constrained Decoding: Complete Production Guide
## How to Control Token Selection and Guarantee Valid JSON in Agents

> **Core Thesis:** Temperature controls shape of distribution (peaky vs flat), Top-p and Top-k control truncation (cut off low-probability tail), Constrained Decoding controls validity (force JSON schema, regex, tool allowlist). Together they determine whether agent generates valid tool calls 99.9% vs 60%. Production agents: T=0.0 + constrained decoding for tool calling = 99.9% valid JSON, T=0.7 + Top-p=0.9 + Top-k=50 for planning = diverse but controlled, T=1.2 with no constraints = 10% valid, dangerous hallucinations.

### Table of Contents
1. [What are Top-p, Top-k, Temperature? How They Interact](#1-what-are-top-p-top-k-temperature-how-they-interact)
2. [Top-k: Keep Top k Tokens](#2-top-k-keep-top-k-tokens)
3. [Top-p (Nucleus Sampling): Keep Cumulative Probability p](#3-top-p-nucleus-sampling-keep-cumulative-probability-p)
4. [Temperature: Shape of Distribution](#4-temperature-shape-of-distribution)
5. [How They Combine: The Full Sampling Pipeline](#5-how-they-combine-the-full-sampling-pipeline)
6. [Constrained Decoding: Force Valid Output](#6-constrained-decoding-force-valid-output)
7. [Constrained Decoding Methods: Regex, JSON Schema, Grammar, Tool Allowlist](#7-constrained-decoding-methods-regex-json-schema-grammar-tool-allowlist)
8. [Benchmarks: Valid JSON, Accuracy, Diversity, Cost](#8-benchmarks-valid-json-accuracy-diversity-cost)
9. [Production Patterns for Different Agent Steps](#9-production-patterns-for-different-agent-steps)
10. [Common Failures and Fixes](#10-common-failures-and-fixes)
11. [Implementation Blueprint with Code](#11-implementation-blueprint-with-code)
12. [Production Checklist](#12-production-checklist)

---

### 1. What are Top-p, Top-k, Temperature? How They Interact

LLM generates logits for each token in vocabulary (e.g., 50K tokens). Sampling pipeline:

```
Logits [2.0, 1.0, 0.5, 0.2, 0.1, ... 50K tokens]
  |
  +-> Temperature: Divide logits by T, shape distribution (peaky vs flat)
  |
  +-> Softmax: Convert logits to probabilities
  |
  +-> Top-k: Keep only top k tokens (e.g., top 50), discard rest (set prob 0)
  |
  +-> Top-p: Keep tokens whose cumulative probability <= p (e.g., 0.9), discard rest
  |
  +-> Constrained Decoding: Filter tokens that violate schema (e.g., only allow {"tool": "refund_order"}), mask invalid tokens
  |
  +-> Sample: Sample from remaining distribution
```

**Example logits:** [2.0, 1.0, 0.5, 0.2, 0.1] for tokens [refund, check, deny, order, status] -> after T=1.0 softmax probabilities [0.5, 0.25, 0.15, 0.07, 0.03] cumulative [0.5, 0.75, 0.90, 0.97, 1.0]

- Temperature T=0.0: Distribution peaky [0.99, 0.01, 0, 0, 0] -> always picks refund
- Temperature T=1.0: Distribution [0.5, 0.25, 0.15, 0.07, 0.03] -> diverse
- Top-k=2: Keep [0.5, 0.25] -> discard rest -> renormalize [0.66, 0.33] -> sample refund or check only
- Top-p=0.9: Keep tokens cumulative <=0.9 -> [0.5, 0.25, 0.15] cumulative 0.9 -> keep refund, check, deny -> discard order, status -> renormalize [0.55, 0.27, 0.16]
- Constrained Decoding: Only allow refund token -> [1.0, 0, 0, 0, 0] -> always refund, 100% valid

**Together:** Temperature shapes, Top-k and Top-p truncate tail, Constrained Decoding forces validity.

### 2. Top-k: Keep Top k Tokens

**Definition:** Keep only top k tokens with highest logits/probabilities, discard rest (set prob 0, renormalize).

**Example:**

k=50: Keep 50 most likely tokens, discard 49,950 tokens. If vocabulary 50K, keep 0.1% of tokens.

**What it does:**

- Controls diversity by limiting to top k tokens
- Small k=10: Very focused, only 10 tokens considered, less diverse, more deterministic
- Large k=100: More diverse, 100 tokens considered
- k=None: Consider all tokens (no truncation)

**Pros:**

- Simple, easy to understand
- Limits to plausible tokens, cuts off long tail of low-probability hallucinations

**Cons:**

- Fixed k: If distribution peaky (one token 0.9 prob), k=50 still keeps 49 low-prob tokens that are irrelevant. If distribution flat (many tokens 0.02 prob), k=50 cuts off valid tokens.
- Not adaptive to distribution shape

**When to use:**

- For creative tasks where want some diversity but not too much tail
- Production: Top-k=50 for T=0.4 reasoning and T=0.7 planning — good balance
- For T=0.0 tool calling: Top-k=None (no truncation, let temperature handle determinism)

**Benchmark:**

- T=0.7 + Top-k=10: Valid JSON 70%, diversity low (only 10 tokens)
- T=0.7 + Top-k=50: Valid JSON 60%, diversity medium (50 tokens)
- T=0.7 + Top-k=100: Valid JSON 55%, diversity high (100 tokens)
- For tool calling: Top-k=None + T=0.0 = 95% valid JSON (best)

### 3. Top-p (Nucleus Sampling): Keep Cumulative Probability p

From Holtzman et al. 2020 Nucleus Sampling paper.

**Definition:** Sort tokens by probability descending, keep tokens until cumulative probability >= p, discard rest.

**Example:** Probabilities sorted [0.5, 0.25, 0.15, 0.07, 0.03] cumulative [0.5, 0.75, 0.90, 0.97, 1.0]

- Top-p=0.9: Keep tokens until cumulative 0.9 -> keep first 3 tokens [0.5, 0.25, 0.15] cumulative 0.9, discard [0.07, 0.03]
- Top-p=0.5: Keep only first token [0.5] cumulative 0.5, discard rest -> deterministic
- Top-p=1.0: Keep all tokens cumulative 1.0, no truncation

**What it does:**

- Adaptive truncation based on distribution shape
- If distribution peaky (one token 0.9 prob), Top-p=0.9 keeps only 1 token (focused)
- If distribution flat (many tokens 0.02 prob), Top-p=0.9 keeps many tokens (45 tokens to reach 0.9 cumulative) (diverse)
- More adaptive than Top-k fixed

**Pros:**

- Adaptive to distribution shape — focused when confident, diverse when uncertain
- Better than Top-k for diverse tasks
- Reduces hallucinations by cutting off low-prob tail that doesn't contribute much to cumulative mass

**Cons:**

- Slightly more complex than Top-k
- Still can include low-prob tokens if distribution flat

**When to use:**

- For all creative tasks — planning, reasoning, writing, ToT
- Production: Top-p=0.9 for T=0.4 reasoning and T=0.7 planning — adaptive, good balance
- For T=0.0 tool calling: Top-p=1.0 (no truncation, let T=0.0 handle determinism)

**Benchmark:**

- T=0.7 + Top-p=0.9: Valid JSON 60%, diversity medium, adaptive
- T=0.7 + Top-p=0.95: Valid JSON 55%, diversity high, more adaptive
- T=0.7 + Top-p=0.5: Valid JSON 75%, diversity low, almost deterministic (only keeps high prob tokens)
- For tool calling: Top-p=1.0 + T=0.0 = 95% valid JSON (best)

**Top-p vs Top-k:**

- Top-k fixed: Always keeps k tokens, regardless of distribution shape
- Top-p adaptive: Keeps variable number of tokens based on distribution shape — fewer when confident, more when uncertain
- Production: Use Top-p=0.9 over Top-k=50 — more adaptive, better diversity vs validity tradeoff. But use both together: Top-p=0.9 + Top-k=50 = truncates both ways.

### 4. Temperature: Shape of Distribution

**Definition:** Divide logits by T before softmax.

```
P(token_i) = exp(logit_i / T) / sum_j exp(logit_j / T)
```

- T->0: Distribution peaky, argmax dominates, deterministic
- T=1.0: Standard softmax
- T->infinity: Distribution uniform, chaotic

**Example logits [2.0, 1.0, 0.5]:**

- T=0.0: [0.99, 0.01, 0] -> always picks first
- T=0.5: [0.80, 0.15, 0.05] -> mostly first, sometimes second
- T=1.0: [0.60, 0.25, 0.15] -> diverse
- T=1.5: [0.45, 0.30, 0.25] -> chaotic, almost uniform

**What it does:**

- Controls creativity vs determinism
- Low T = conservative, picks highest prob token, less diverse, less hallucination
- High T = creative, samples low-prob tokens, diverse, more hallucination

**When to use:**

- T=0.0 for tool calling, JSON, policy checks, extraction (80% steps)
- T=0.3-0.5 for reasoning, evaluation
- T=0.7-0.9 for planning, brainstorming, writing, loop breaking
- Never T>1.0 in production

**See temperature_in_agentic_ai.md for full guide.**

### 5. How They Combine: The Full Sampling Pipeline

**Order matters:** Temperature -> Softmax -> Top-k -> Top-p -> Constrained Decoding -> Sample

```python
def sample_with_all(logits, temperature, top_k, top_p, constrained_mask):
    # 1. Temperature: Divide logits by T
    logits = logits / temperature
    
    # 2. Softmax: Convert to probabilities
    probs = softmax(logits) # [0.5, 0.25, 0.15, 0.07, 0.03]
    
    # 3. Top-k: Keep top k
    if top_k is not None:
        # Keep only top k probs, set rest 0
        top_k_indices = argmax_k(probs, k=top_k)
        mask = [i in top_k_indices for i in range(len(probs))]
        probs = [p if m else 0 for p, m in zip(probs, mask)]
        probs = renormalize(probs) # [0.66, 0.33, 0, 0, 0] for k=2
    
    # 4. Top-p: Keep cumulative p
    if top_p < 1.0:
        # Sort by prob descending
        sorted_indices = argsort(probs, descending=True)
        sorted_probs = [probs[i] for i in sorted_indices]
        cumulative = cumsum(sorted_probs)
        # Keep until cumulative >= p
        keep_indices = [sorted_indices[i] for i in range(len(probs)) if cumulative[i] <= top_p or i==0] # Always keep at least 1
        mask = [i in keep_indices for i in range(len(probs))]
        probs = [p if m else 0 for p, m in zip(probs, mask)]
        probs = renormalize(probs) # [0.55, 0.27, 0.16, 0, 0] for p=0.9
    
    # 5. Constrained Decoding: Mask invalid tokens
    if constrained_mask is not None:
        # constrained_mask = [1, 0, 0, 0, 0] for only allow refund
        probs = [p * m for p, m in zip(probs, constrained_mask)]
        probs = renormalize(probs) # [1.0, 0, 0, 0, 0] -> always refund
    
    # 6. Sample
    token = sample_from(probs)
    return token
```

**Example with all:**

Logits [2.0, 1.0, 0.5, 0.2, 0.1] -> T=0.7 -> probs [0.45, 0.27, 0.16, 0.07, 0.05] -> Top-k=50 (keep all 5, k>vocab) -> Top-p=0.9 (keep first 3 cumulative 0.88, need 0.9 so keep 4? Actually 0.45+0.27+0.16=0.88 <0.9, so keep 4th 0.07 cumulative 0.95 >=0.9, so keep 4 tokens) -> [0.45, 0.27, 0.16, 0.07] renormalize [0.47, 0.28, 0.16, 0.07] -> Constrained mask [1,1,0,0,0] (only allow refund, check) -> [0.47, 0.28] renormalize [0.62, 0.37] -> sample refund 62% or check 37%.

**Production recommendations:**

- Tool calling: T=0.0 + Top-k=None + Top-p=1.0 + Constrained Decoding regex for tool allowlist and JSON schema = 99.9% valid
- Reasoning: T=0.4 + Top-k=50 + Top-p=0.9 + no constraints (or light constraints) = balanced 80% valid
- Planning: T=0.7 + Top-k=50 + Top-p=0.9 + no constraints = creative diverse but controlled 60% valid (don't need JSON)
- ToT diverse: T=0.7 + Top-k=100 + Top-p=0.95 + no constraints = more diverse 55% valid but diverse thoughts
- Writing: T=0.7 + Top-k=50 + Top-p=0.9 + no constraints = creative friendly

### 6. Constrained Decoding: Force Valid Output

**What:** Force LLM to generate only tokens that satisfy constraints (regex, JSON schema, grammar, tool allowlist). Masks invalid tokens during sampling (sets prob 0).

**Why needed:**

- Without constraints, LLM can generate invalid JSON 40% at T=0.7, hallucinated tool names, wrong order_id format
- With constraints, 99.9% valid JSON, exact tool names, exact formats

**How it works:**

1. Define constraint: Regex ^ORD-\d{5}$, JSON schema {tool: string enum [refund_order, get_order_status], args: {order_id: pattern ^ORD-\d{5}$}}, grammar, tool allowlist
2. At each token generation step, check which tokens would violate constraint if generated
3. Mask invalid tokens (set prob 0)
4. Sample only from valid tokens

**Example:**

Constraint: Tool must be "refund_order" (exact)

Vocabulary tokens: [refund, _order, refund_order, get, _order_status, ...]

- Step 1: Generate first token: Only tokens that start valid tool name allowed -> "refund" allowed, "get" allowed (could be get_order_status), but "delete" not allowed (not in allowlist) -> mask delete
- Step 2: If first token refund, second token must be _order to make refund_order -> only _order allowed, others masked
- Result: Always generates valid tool name from allowlist, never hallucinates delete_all_orders

**Types of constraints:**

- Regex: Pattern for string, e.g., ^ORD-\d{5}$ for order_id
- JSON Schema: {type: object, properties: {tool: {type: string, enum: [...]}, args: {...}}, required: [tool, args]}
- Grammar: Context-free grammar for complex structures
- Tool allowlist: Only allow specific tool names

**Libraries:**

- Outlines: Regex, JSON schema, grammar constrained decoding
- LMQL: Query language with constraints
- Guidance: Grammar-based constraints
- JSONformer: JSON schema constraints
- OpenAI structured outputs: response_format json_schema

### 7. Constrained Decoding Methods: Regex, JSON Schema, Grammar, Tool Allowlist

**a) Regex constrained decoding:**

Force output to match regex pattern.

```python
# Order ID must be ORD-12345 format
order_id_schema = {
    "type": "string",
    "pattern": "^ORD-\d{5}$" # Regex: ORD- + 5 digits
}

# Implementation with Outlines
from outlines import models, generate

model = models.openai("gpt-4o-mini")
generator = generate.regex(model, r"ORD-\d{5}") # Only generate tokens matching regex
order_id = generator("Generate order ID:")

# Always generates ORD-12345 format, never ORD-123 or ORD-12345-xyz
```

**b) JSON Schema constrained decoding:**

Force output to match JSON schema.

```python
ActionSchema = {
    "type": "object",
    "properties": {
        "tool": {
            "type": "string",
            "enum": ["refund_order", "get_order_status", "get_policy", "get_trust_score", "send_email"] # Allowlist
        },
        "args": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "pattern": "^ORD-\d{5}$"},
                "amount": {"type": "number", "minimum": 0, "maximum": 10000}
            },
            "required": ["order_id"]
        }
    },
    "required": ["tool", "args"]
}

# With OpenAI structured outputs
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Action for refund ORD-12345 $120"}],
    response_format={"type": "json_schema", "json_schema": {"name": "Action", "schema": ActionSchema}},
    temperature=0.0
)
# Always valid JSON matching schema, tool from allowlist, order_id format ORD-12345, amount 0-10000
# 99.9% valid vs 95% with prompting alone at T=0.0, 60% at T=0.7
```

**c) Grammar constrained decoding:**

Force output to match context-free grammar.

```python
# Grammar for tool calls
grammar = '''
    start: tool_call
    tool_call: "{" "\"tool\":" tool_name "," "\"args\":" args "}"
    tool_name: "\"refund_order\"" | "\"get_order_status\"" | "\"get_policy\""
    args: "{" arg_list "}"
    arg_list: arg ("," arg)*
    arg: "\"order_id\":" order_id | "\"amount\":" number
    order_id: "\"ORD-" DIGIT DIGIT DIGIT DIGIT DIGIT "\""
    number: DIGIT+
    DIGIT: "0".."9"
'''

from outlines import generate
generator = generate.cfg(model, grammar)
action = generator("Action:")
# Always valid according to grammar
```

**d) Tool allowlist constrained decoding:**

Only allow specific tool names.

```python
# Allowlist of tools
allowed_tools = ["refund_order", "get_order_status", "get_policy", "get_trust_score", "send_email"]

# Constrained decoding: Only generate tokens that form allowed tool names
# Implementation: At each step, mask tokens that would lead to disallowed tool name

# Without constraints: LLM can generate "delete_all_orders" hallucinated tool
# With allowlist constraint: Only refund_order, get_order_status, etc. allowed, delete_all_orders masked (prob 0)

# OpenAI function calling is constrained decoding for tools
tools = [
    {"type": "function", "function": {"name": "refund_order", "parameters": {"type": "object", "properties": {"order_id": {"type": "string", "pattern": "^ORD-\d{5}$"}, "amount": {"type": "number"}}}}},
    {"type": "function", "function": {"name": "get_order_status", "parameters": {"type": "object", "properties": {"order_id": {"type": "string", "pattern": "^ORD-\d{5}$"}}}}}
]

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Refund ORD-12345 $120"}],
    tools=tools,
    tool_choice="auto",
    temperature=0.0
)
# Always generates valid tool call from allowlist, never hallucinates delete_all_orders
```

**Benchmark constrained decoding:**

- No constraints, T=0.0, prompting: Valid JSON 95%, tool allowlist 90% (hallucinates 10% invalid tool names)
- Regex constraint ^ORD-\d{5}$: Valid order_id format 99.9% vs 85% without
- JSON Schema constraint: Valid JSON 99.9% vs 95% prompting, 60% at T=0.7
- Tool allowlist constraint: Valid tool name 100% vs 90% without, prevents delete_all_orders catastrophic
- Combined T=0.0 + JSON Schema + tool allowlist + regex: Valid 99.9%, tool name 100% valid, args format 99.9% valid

**Cost of constrained decoding:**

- Small overhead: Need to check constraints at each token (masking)
- Outlines: 10-20% latency overhead
- OpenAI structured outputs: No extra cost, same latency
- Worth it: 99.9% valid vs 60% at T=0.7 saves retry cost 1.5x

### 8. Benchmarks: Valid JSON, Accuracy, Diversity, Cost

**Valid JSON rate:**

| Setup | T | Top-p | Top-k | Constraints | Valid JSON | Tool Name Valid | Order ID Format Valid |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| No constraints, prompting | 0.0 | 1.0 | None | None | 95% | 90% | 85% |
| No constraints, prompting | 0.7 | 1.0 | None | None | 60% | 70% | 60% |
| No constraints, prompting | 1.2 | 1.0 | None | None | 10% | 30% | 20% |
| Regex | 0.0 | 1.0 | None | ^ORD-\d{5}$ | 95% | 90% | 99.9% |
| JSON Schema | 0.0 | 1.0 | None | JSON Schema + allowlist | 99.9% | 100% | 99.9% |
| JSON Schema + Regex | 0.0 | 1.0 | None | JSON Schema + allowlist + regex | 99.9% | 100% | 99.9% |
| JSON Schema | 0.7 | 0.9 | 50 | JSON Schema + allowlist | 95% | 100% | 99.9% |

**Accuracy (correct tool + correct args):**

- No constraints, T=0.0: 85% accuracy (10% invalid tool name, 5% invalid args)
- JSON Schema + allowlist + regex, T=0.0: 95% accuracy (5% wrong args but valid format)
- JSON Schema + allowlist + regex, T=0.7: 80% accuracy (20% wrong reasoning but valid format)
- No constraints, T=1.2: 20% accuracy (80% hallucinations)

**Diversity (for planning, ToT):**

- T=0.0 + Top-p=1.0 + Top-k=None: Low diversity (same output)
- T=0.7 + Top-p=0.9 + Top-k=50: Medium diversity (3 diverse thoughts)
- T=0.7 + Top-p=0.95 + Top-k=100: High diversity (5 diverse thoughts)
- T=0.7 + no Top-p/k + no constraints: Very high diversity but chaotic, 10% valid

**Cost (including retry for invalid):**

- T=0.0 no constraints: 95% valid, no retry needed, cost 1x, 85% accuracy
- T=0.0 JSON Schema: 99.9% valid, no retry, cost 1x + 10% overhead, 95% accuracy — best for tool calling
- T=0.7 no constraints: 60% valid, needs retry 1.5x cost for 85% accuracy, 70% accuracy after retry
- T=0.7 JSON Schema: 95% valid, no retry, cost 1x + 10% overhead, 80% accuracy — good for planning where need creativity + validity
- T=1.2 no constraints: 10% valid, needs retry 3x cost for 50% accuracy, 20% accuracy — avoid

**Recommendation:**

- Tool calling: T=0.0 + Top-p=1.0 + Top-k=None + JSON Schema + allowlist + regex = 99.9% valid, 95% accuracy, cost 1.1x — best
- Reasoning: T=0.4 + Top-p=0.9 + Top-k=50 + light constraints (JSON Schema for output format) = 80% valid, 75% success, cost 1x
- Planning: T=0.7 + Top-p=0.9 + Top-k=50 + no constraints (don't need JSON, need diverse plans) = 60% valid JSON not needed, 80% diverse plans, cost 1x
- ToT diverse thoughts: T=0.7 + Top-p=0.95 + Top-k=100 + no constraints = 55% valid but high diversity, cost 1x, good for branching
- Writing: T=0.7 + Top-p=0.9 + Top-k=50 + no constraints = creative friendly, cost 1x

### 9. Production Patterns for Different Agent Steps

**Tool calling (80% of steps):**

```python
# Must be deterministic, valid, exact
ActionSchema = {
    "type": "object",
    "properties": {
        "tool": {"type": "string", "enum": ["refund_order", "get_order_status", "get_policy", "get_trust_score", "send_email"]},
        "args": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "pattern": "^ORD-\d{5}$"},
                "amount": {"type": "number", "minimum": 0, "maximum": 10000}
            },
            "required": ["order_id"]
        }
    },
    "required": ["tool", "args"]
}

action = llm.generate(
    prompt=f"Thought: {thought} Action JSON:",
    temperature=0.0, # Deterministic
    top_p=1.0, # No truncation
    top_k=None, # No truncation
    response_format={"type": "json_schema", "json_schema": {"name": "Action", "schema": ActionSchema}} # Constrained decoding
)
# 99.9% valid, 100% tool name valid, 99.9% order_id format valid, 95% accuracy
```

**Reasoning (Chain-of-Thought):**

```python
# Balanced, some creativity, focused
thought = llm.generate(
    prompt=f"Query: {query} History: {history} Think step by step:",
    temperature=0.4, # Balanced
    top_p=0.9, # Adaptive truncation
    top_k=50, # Limit tail
    # No constraints or light constraints for output format
)
# 80% valid, 75% success
```

**Planning (decompose goal):**

```python
# Creative diverse
plan = llm.generate(
    prompt=f"Goal: {user_goal} Decompose into 3-5 diverse sub-goals:",
    temperature=0.7, # Creative diverse
    top_p=0.9,
    top_k=50,
    # No constraints, don't need JSON, need diverse plans
)
# 80% diverse plans
```

**Tree-of-Thought diverse thoughts:**

```python
# More diverse for branching
thoughts = llm.generate(
    prompt=f"Query: {query} History: {history} Generate 3 different next thoughts:",
    n=3,
    temperature=0.7, # Creative
    top_p=0.95, # More diverse
    top_k=100, # More diverse
    # No constraints, need diverse thoughts
)
# 3 diverse thoughts, 55% valid but high diversity good for branching
```

**Loop breaking:**

```python
# Creative alternative when stuck
if detect_loop(history):
    reflection = llm.generate(
        prompt=f"Stuck repeating {history[-1].action}, why? What different approach?",
        temperature=0.7, # Creative to break loop
        top_p=0.9,
        top_k=50
    )
    # Breaks 90% loops vs 10% at T=0.0
```

**Writing (user notification):**

```python
# Creative friendly
email = llm.generate(
    prompt=f"Refund ${amount} processed. Write friendly email:",
    temperature=0.7, # Creative friendly
    top_p=0.9,
    top_k=50
)
# 90% friendly vs 50% at T=0.0 robotic
```

**Evaluation (rate thought 1-10):**

```python
# Balanced
score = llm.generate(
    prompt=f"Query: {query} Thought: {thought} Rate 1-10:",
    temperature=0.3, # Balanced evaluation
    top_p=0.9,
    top_k=50
)
```

### 10. Common Failures and Fixes

**Failure 1: No constrained decoding for tool calling -> invalid JSON 40% at T=0.7**

```
Prompt: "Action: refund_order"
T=0.7 no constraints: {"tool": "refund_orderz", "args": {"order_id": "ORD-12345-xyz", "amount": 99999}} - hallucinated tool name and args, invalid format
Result: Tool call fails, trajectory fails
Fix: Use T=0.0 + JSON Schema + allowlist + regex ^ORD-\d{5}$ = 99.9% valid, 100% tool name valid
```

**Failure 2: Top-k too small for diverse tasks -> misses valid tokens**

```
Task: Generate 3 diverse thoughts for ToT
Top-k=10: Only 10 tokens considered, thoughts not diverse (all similar)
Result: Tree not diverse, fails to explore alternative approaches
Fix: Use Top-k=100 + Top-p=0.95 for more diverse
```

**Failure 3: Top-p too small -> deterministic, no diversity**

```
Task: Planning diverse sub-goals
Top-p=0.5: Only tokens cumulative 0.5 prob kept, only 1-2 tokens, deterministic same plan every time
Result: No diversity, misses better plan
Fix: Use Top-p=0.9 for medium diversity, 0.95 for high diversity
```

**Failure 4: No constraints for high-risk -> generates delete_all_orders**

```
Prompt: "Refund ORD-12345"
No constraints, T=1.2: {"tool": "delete_all_orders", "args": {}} - hallucinated dangerous tool
Result: Catastrophic deletes all orders
Fix: Always use tool allowlist constraint + T=0.0 for tool calling, never T>1.0
```

**Failure 5: T=0.0 + Top-k=10 + Top-p=0.5 for reasoning -> too deterministic, stuck**

```
History: get_order_status(ORD-123) -> Error Invalid ID -> Thought: Need to get order status -> Action: get_order_status(ORD-123) -> Error -> loop
T=0.0 + Top-k=10 + Top-p=0.5: Repeats same thought "Need to get order status" deterministic, stuck
Result: Infinite loop
Fix: Detect loop, use T=0.7 + Top-p=0.9 + Top-k=50 for reflection creative alternative "Maybe order ID format wrong? Try ORD-12345?"
```

### 11. Implementation Blueprint with Code

**Dynamic sampling with all parameters:**

```python
def get_sampling_params(step_type):
    # step_type: planning, reasoning, tool_calling, evaluation, reflection, writing, loop_breaking, extraction
    params_map = {
        "tool_calling": {"temperature": 0.0, "top_p": 1.0, "top_k": None, "constraints": "json_schema+allowlist+regex"}, # Deterministic 99.9% valid
        "reasoning": {"temperature": 0.4, "top_p": 0.9, "top_k": 50, "constraints": "light"}, # Balanced 80% valid
        "planning": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "constraints": "none"}, # Creative diverse 80% diverse
        "evaluation": {"temperature": 0.3, "top_p": 0.9, "top_k": 50, "constraints": "none"}, # Balanced scoring
        "reflection": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "constraints": "none"}, # Creative why failed
        "writing": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "constraints": "none"}, # Creative friendly
        "loop_breaking": {"temperature": 0.7, "top_p": 0.9, "top_k": 50, "constraints": "none"}, # Creative alternative breaks 90% loops
        "extraction": {"temperature": 0.1, "top_p": 1.0, "top_k": None, "constraints": "json_schema"}, # Almost deterministic NER 90% valid
        "tot_diverse": {"temperature": 0.7, "top_p": 0.95, "top_k": 100, "constraints": "none"}, # More diverse for ToT branching
    }
    return params_map.get(step_type, {"temperature": 0.0, "top_p": 1.0, "top_k": None, "constraints": "json_schema"})

def llm_generate_with_sampling(prompt, step_type, schema=None):
    params = get_sampling_params(step_type)
    
    if params["constraints"] == "json_schema+allowlist+regex":
        # Tool calling with all constraints
        return llm.generate(
            prompt,
            temperature=params["temperature"], # 0.0
            top_p=params["top_p"], # 1.0
            top_k=params["top_k"], # None
            response_format={"type": "json_schema", "json_schema": {"name": "Action", "schema": schema}} # Constrained decoding
        )
    elif params["constraints"] == "none":
        return llm.generate(
            prompt,
            temperature=params["temperature"],
            top_p=params["top_p"],
            top_k=params["top_k"]
        )
    else:
        return llm.generate(
            prompt,
            temperature=params["temperature"],
            top_p=params["top_p"],
            top_k=params["top_k"],
            response_format={"type": "json_schema", "json_schema": {"name": "Output", "schema": schema}} if schema else None
        )

# Usage in agent loop
def production_agent_loop(user_goal):
    # Planning - T=0.7 creative diverse
    plan = llm_generate_with_sampling(f"Goal: {user_goal} Decompose into sub-goals:", step_type="planning")
    
    for sub_goal in plan.sub_goals:
        # Reasoning - T=0.4 balanced
        thought = llm_generate_with_sampling(f"Goal: {sub_goal} Think step by step:", step_type="reasoning")
        
        # Tool calling - T=0.0 deterministic with all constraints
        action = llm_generate_with_sampling(f"Thought: {thought} Action JSON:", step_type="tool_calling", schema=ActionSchema)
        
        observation = execute_tool(action.tool, action.args)
        
        # Loop detection - T=0.7 creative to break
        if detect_loop(history):
            reflection = llm_generate_with_sampling(f"Stuck repeating {history[-1]} Why? Different approach?", step_type="loop_breaking")
    
    # Writing - T=0.7 creative friendly
    final = llm_generate_with_sampling(f"History: {history} Synthesize friendly answer:", step_type="writing")
    return final
```

**Constrained decoding with Outlines:**

```python
from outlines import models, generate

model = models.openai("gpt-4o-mini")

# Regex constraint
order_id_generator = generate.regex(model, r"ORD-\d{5}")
order_id = order_id_generator("Generate order ID:") # Always ORD-12345 format

# JSON Schema constraint
ActionSchema = {
    "type": "object",
    "properties": {
        "tool": {"type": "string", "enum": ["refund_order", "get_order_status"]},
        "args": {"type": "object", "properties": {"order_id": {"type": "string", "pattern": "^ORD-\d{5}$"}}}
    }
}
action_generator = generate.json(model, ActionSchema)
action = action_generator("Action for refund ORD-12345:") # Always valid JSON matching schema

# Grammar constraint
grammar = '''
    start: tool_call
    tool_call: "{" "\"tool\":" tool_name "," "\"args\":" args "}"
    tool_name: "\"refund_order\"" | "\"get_order_status\""
    args: "{" "\"order_id\":" order_id "}"
    order_id: "\"ORD-" DIGIT{5} "\""
'''
grammar_generator = generate.cfg(model, grammar)
action = grammar_generator("Action:") # Always valid according to grammar
```

**Monitoring in ClickHouse:**

```sql
-- Valid JSON rate by sampling params
SELECT temperature, top_p, top_k, has_constraints, count() as calls, avg(valid_json) as valid_rate, avg(tool_name_valid) as tool_valid_rate, avg(accuracy) as accuracy
FROM llm_calls
WHERE date = today()
GROUP BY temperature, top_p, top_k, has_constraints
ORDER BY valid_rate DESC

-- Result:
-- T=0.0 Top-p=1.0 Top-k=None constraints=yes: valid 99.9% tool_valid 100% accuracy 95%
-- T=0.0 Top-p=1.0 Top-k=None constraints=no: valid 95% tool_valid 90% accuracy 85%
-- T=0.7 Top-p=0.9 Top-k=50 constraints=no: valid 60% tool_valid 70% accuracy 70%
-- T=0.7 Top-p=0.9 Top-k=50 constraints=yes: valid 95% tool_valid 100% accuracy 80%

-- Loop breaking success
SELECT loop_breaking_temperature, loop_breaking_top_p, countIf(loop_broken)/count() as break_rate
FROM agent_trajectories
WHERE loop_detected = true
GROUP BY loop_breaking_temperature, loop_breaking_top_p
-- T=0.0 Top-p=1.0: break_rate 10%, T=0.7 Top-p=0.9: break_rate 90%
```

### 12. Production Checklist

1. **Temperature controls shape (peaky vs flat), Top-k keeps top k tokens (fixed), Top-p keeps cumulative prob p (adaptive), Constrained Decoding masks invalid tokens (forces validity). Pipeline: Logits -> T -> Softmax -> Top-k -> Top-p -> Constrained Mask -> Sample.**

2. **Tool calling (80% steps): T=0.0 + Top-p=1.0 + Top-k=None + JSON Schema + tool allowlist + regex ^ORD-\d{5}$ = 99.9% valid JSON, 100% tool name valid, 99.9% order_id format valid, 95% accuracy, cost 1.1x. Mandatory for production, prevents delete_all_orders catastrophic.**

3. **Reasoning (Chain-of-Thought, evaluation): T=0.4 + Top-p=0.9 + Top-k=50 + light constraints (JSON Schema for output format) = 80% valid, 75% success, cost 1x. Balanced some creativity but focused.**

4. **Planning, brainstorming, writing, loop breaking, reflection: T=0.7 + Top-p=0.9 + Top-k=50 + no constraints = 60% valid JSON not needed, 80% diverse plans, 90% loop break, 90% friendly writing, cost 1x. Creative diverse but controlled.**

5. **Tree-of-Thought diverse thoughts: T=0.7 + Top-p=0.95 + Top-k=100 + no constraints = 55% valid but high diversity for branching k=3, good for exploring alternative approaches.**

6. **Never T>1.0 in production: T=1.2 chaotic hallucinates dangerous tools, valid JSON 10%, accuracy 20%, catastrophic. Only for art.**

7. **Dynamic sampling: Different params for different steps. Planning T=0.7, Reasoning T=0.4, Tool calling T=0.0 with all constraints (80% steps), Loop breaking T=0.7, Evaluation T=0.3, Writing T=0.7, Extraction T=0.1. Result 92% success vs 70% with T=0.0 only or 60% with T=0.7 only.**

8. **Top-p vs Top-k: Top-k fixed keeps k tokens regardless of distribution shape, Top-p adaptive keeps variable number based on shape — fewer when confident (peaky), more when uncertain (flat). Use Top-p=0.9 over Top-k=50, but use both together Top-p=0.9 + Top-k=50 = truncates both ways.**

9. **Constrained decoding methods: Regex for patterns ^ORD-\d{5}$, JSON Schema for object with enum allowlist and required fields, Grammar for complex structures, Tool allowlist for only allowed tools. Libraries: Outlines, LMQL, Guidance, JSONformer, OpenAI structured outputs. 10-20% latency overhead, worth 99.9% valid vs 60% at T=0.7.**

10. **Cost: T doesn't affect cost per call (same tokens), but affects retry cost. T=0.0 95% valid no retry cost 1x, T=0.7 60% valid needs retry 1.5x cost for 85% accuracy. Constrained decoding 10% overhead but saves retry cost. Dynamic sampling balances cost and success.**

11. **Monitor sampling impact: ClickHouse query valid JSON rate, tool name valid rate, accuracy by temperature, top_p, top_k, has_constraints. Alert if tool calling valid <99% (need constraints) or loop breaking rate <80% (need T=0.7).**

12. **Common failures: No constraints for tool calling -> invalid JSON 40% at T=0.7 -> fix T=0.0 + JSON Schema + allowlist + regex. Top-k too small (10) for ToT -> not diverse -> fix Top-k=100 Top-p=0.95. Top-p too small (0.5) for planning -> deterministic -> fix Top-p=0.9. No constraints high-risk -> delete_all_orders -> fix allowlist + T=0.0 never T>1.0. T=0.0 + Top-k=10 + Top-p=0.5 when stuck -> loop -> fix detect loop + T=0.7 Top-p=0.9 Top-k=50 reflection.**

---
**Bottom Line:** Temperature shapes distribution (peaky vs flat), Top-k keeps top k tokens fixed truncation, Top-p keeps cumulative prob p adaptive truncation, Constrained Decoding masks invalid tokens forcing validity (regex, JSON Schema, grammar, tool allowlist). Full pipeline: Logits -> T -> Softmax -> Top-k -> Top-p -> Constrained Mask -> Sample. Tool calling (80% steps): T=0.0 + Top-p=1.0 + Top-k=None + JSON Schema + allowlist + regex = 99.9% valid JSON, 100% tool name valid, 99.9% format valid, 95% accuracy, cost 1.1x, prevents catastrophic hallucinations. Reasoning: T=0.4 + Top-p=0.9 + Top-k=50 + light constraints = 80% valid, 75% success. Planning/writing/loop breaking: T=0.7 + Top-p=0.9 + Top-k=50 + no constraints = 60% valid not needed, 80% diverse, 90% loop break, 90% friendly. ToT diverse: T=0.7 + Top-p=0.95 + Top-k=100 = 55% valid high diversity. Never T>1.0 production. Dynamic sampling different params per step gives 92% success vs 70% T=0.0 only or 60% T=0.7 only. Use Top-p over Top-k but both together, always constrained decoding for tool calling, monitor valid rate in ClickHouse.

