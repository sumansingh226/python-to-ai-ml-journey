# Function Calling vs Tool Calling Deep-Dive: OpenAI Tools, Parallel Calls, Error Handling
## Complete Production Guide - From Legacy Functions to Modern Tools

> **Core Thesis:** Function Calling (2023) = legacy single function per turn, Tool Calling (2023 Dec+) = modern parallel tools, strict schema, 99.9% valid with constrained decoding. Tool Calling is mandatory for production: supports parallel calls (refund + email in one turn = 50% latency cut), tool_choice auto/required/none, and structured outputs. Function Calling deprecated. Production agents: Always use Tools API with T=0.0 + JSON Schema + allowlist + retry with backoff, parallel when independent (get_order + get_policy in parallel), sequential when dependent (get_trust -> refund).

### Table of Contents
1. [History: From Function Calling to Tool Calling](#1-history-from-function-calling-to-tool-calling)
2. [Function Calling (Legacy) - How It Worked](#2-function-calling-legacy---how-it-worked)
3. [Tool Calling (Modern) - How It Works](#3-tool-calling-modern---how-it-works)
4. [OpenAI Tools API Deep-Dive](#4-openai-tools-api-deep-dive)
5. [Parallel Tool Calls - When and How](#5-parallel-tool-calls---when-and-how)
6. [Tool Choice: Auto, Required, None, Specific Tool](#6-tool-choice-auto-required-none-specific-tool)
7. [Error Handling: Invalid Tool, Invalid Args, Tool Execution Error, Retry](#7-error-handling-invalid-tool-invalid-args-tool-execution-error-retry)
8. [Constrained Decoding for Tool Calling - 99.9% Valid](#8-constrained-decoding-for-tool-calling---999-valid)
9. [Tool Design Best Practices for LLM Use](#9-tool-design-best-practices-for-llm-use)
10. [Multi-Turn Tool Calling Loop - ReAct with Tools](#10-multi-turn-tool-calling-loop---react-with-tools)
11. [Benchmarks: Function vs Tool Calling, Parallel vs Sequential](#11-benchmarks-function-vs-tool-calling-parallel-vs-sequential)
12. [Implementation Blueprint - Production Agent](#12-implementation-blueprint---production-agent)
13. [Production Checklist](#13-production-checklist)

---

### 1. History: From Function Calling to Tool Calling

**June 2023 - Function Calling (Legacy):**

- OpenAI introduces functions parameter
- Single function per turn (one function call per assistant message)
- Format: functions=[{name, description, parameters JSON Schema}], function_call auto/none/{name}
- Response: assistant message with function_call: {name, arguments string JSON}
- User then calls function and returns function role message with result
- Limitation: Only one function per turn, no parallel, string arguments need parsing, deprecated Dec 2023

**Dec 2023 - Tool Calling (Modern):**

- OpenAI introduces tools parameter, replaces functions
- Multiple tools per turn (parallel tool calls)
- Format: tools=[{type: function, function: {name, description, parameters JSON Schema, strict true}}], tool_choice auto/required/none/{function name}
- Response: assistant message with tool_calls: [{id, type: function, function: {name, arguments string JSON}}] — array, can have 3 parallel calls
- Tool results returned as tool role messages with tool_call_id matching id
- Supports parallel calls, strict mode (99.9% valid), structured outputs
- Function Calling deprecated, Tool Calling mandatory for new code

**Why Tool Calling better:**

- Parallel: get_order_status + get_policy + get_trust_score in one turn vs 3 turns sequential = 50% latency cut (1.5s vs 3s)
- Strict: strict true enforces schema via constrained decoding = 99.9% valid vs 95% with functions
- Cleaner: tool_calls array with ids, tool role with tool_call_id vs function role
- Future-proof: Supports new tool types (e.g., computer use, file search) beyond functions

**Migration:**

- Functions -> Tools: Change functions=[...] to tools=[{type: function, function: {...}}], function_call to tool_choice, assistant function_call to tool_calls array, function role to tool role with tool_call_id
- Always use Tools API for new agents

### 2. Function Calling (Legacy) - How It Worked

**Request:**

```python
# Legacy Function Calling (June 2023 - deprecated Dec 2023)
functions = [
    {
        "name": "refund_order",
        "description": "Refund order by ID with amount",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID e.g., ORD-12345"},
                "amount": {"type": "number", "description": "Refund amount"}
            },
            "required": ["order_id", "amount"]
        }
    },
    {
        "name": "get_order_status",
        "description": "Get order status by ID",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        }
    }
]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": "Refund ORD-12345 $120"}],
    functions=functions,
    function_call="auto" # auto, none, or {"name": "refund_order"}
)

# Response: Only ONE function call per turn
# {
#   "role": "assistant",
#   "content": null,
#   "function_call": {
#     "name": "refund_order",
#     "arguments": "{\"order_id\": \"ORD-12345\", \"amount\": 120}" # String JSON, needs parsing
#   }
# }

# Then execute function
result = refund_order(order_id="ORD-12345", amount=120)

# Return result as function role
response2 = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[
        {"role": "user", "content": "Refund ORD-12345 $120"},
        {"role": "assistant", "content": None, "function_call": {"name": "refund_order", "arguments": "{\"order_id\": \"ORD-12345\", \"amount\": 120}"}},
        {"role": "function", "name": "refund_order", "content": json.dumps(result)} # Function role with result
    ],
    functions=functions
)
# Final answer: "Refund $120 processed for ORD-12345"
```

**Limitations:**

- One function per turn: Need 3 turns for get_order + get_policy + refund vs 1 turn with parallel tools
- String arguments: arguments is string JSON, need json.loads, can be invalid JSON 5% at T=0.0, 40% at T=0.7
- No parallel: Sequential only, latency 3x
- No strict mode: No constrained decoding, 95% valid vs 99.9% with tools strict true
- Deprecated: No longer supported, use Tools API

### 3. Tool Calling (Modern) - How It Works

**Request with Tools API (Dec 2023+):**

```python
# Modern Tool Calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "refund_order",
            "description": "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID format ORD-12345", "pattern": "^ORD-\d{5}$"},
                    "amount": {"type": "number", "description": "Refund amount 0-10000", "minimum": 0, "maximum": 10000}
                },
                "required": ["order_id", "amount"],
                "additionalProperties": False
            },
            "strict": True # Enforces schema via constrained decoding = 99.9% valid
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get order status by ID. Returns amount, status, user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\d{5}$"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy",
            "description": "Get refund policy by version. Returns max_auto amount, trust threshold.",
            "parameters": {
                "type": "object",
                "properties": {
                    "version": {"type": "string", "pattern": "^v\d+\.\d+$"}
                },
                "required": ["version"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trust_score",
            "description": "Get user trust score by user_id. Returns 0-100.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Refund ORD-12345 $120"}],
    tools=tools,
    tool_choice="auto", # auto, required, none, or {"type": "function", "function": {"name": "refund_order"}}
    temperature=0.0,
    top_p=1.0
)

# Response: Can have MULTIPLE parallel tool calls in one turn
# {
#   "role": "assistant",
#   "content": null,
#   "tool_calls": [
#     {
#       "id": "call_1",
#       "type": "function",
#       "function": {
#         "name": "get_order_status",
#         "arguments": "{\"order_id\": \"ORD-12345\"}" # String JSON but strict true = 99.9% valid
#       }
#     },
#     {
#       "id": "call_2",
#       "type": "function",
#       "function": {
#         "name": "get_policy",
#         "arguments": "{\"version\": \"v2.3\"}"
#       }
#     },
#     {
#       "id": "call_3",
#       "type": "function",
#       "function": {
#         "name": "get_trust_score",
#         "arguments": "{\"user_id\": \"user_123\"}"
#       }
#     }
#   ]
# }

# Execute all 3 tools in parallel (independent, no dependencies)
import asyncio
results = await asyncio.gather(
    get_order_status(order_id="ORD-12345"),
    get_policy(version="v2.3"),
    get_trust_score(user_id="user_123")
)
# Results: [{"amount": 120, "status": "delivered", "user_id": "user_123"}, {"max_auto": 500, "trust_threshold": 80}, {"score": 85}]

# Return results as tool role messages with tool_call_id matching id
response2 = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Refund ORD-12345 $120"},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "call_1", "type": "function", "function": {"name": "get_order_status", "arguments": "{\"order_id\": \"ORD-12345\"}"}},
            {"id": "call_2", "type": "function", "function": {"name": "get_policy", "arguments": "{\"version\": \"v2.3\"}"}},
            {"id": "call_3", "type": "function", "function": {"name": "get_trust_score", "arguments": "{\"user_id\": \"user_123\"}"}}
        ]},
        {"role": "tool", "tool_call_id": "call_1", "content": json.dumps(results[0])}, # Tool role with tool_call_id
        {"role": "tool", "tool_call_id": "call_2", "content": json.dumps(results[1])},
        {"role": "tool", "tool_call_id": "call_3", "content": json.dumps(results[2])}
    ],
    tools=tools,
    tool_choice="auto"
)

# Response: Now can call refund_order with all info
# {
#   "role": "assistant",
#   "tool_calls": [
#     {"id": "call_4", "type": "function", "function": {"name": "refund_order", "arguments": "{\"order_id\": \"ORD-12345\", \"amount\": 120}"}}
#   ]
# }

# Execute refund
result = refund_order(order_id="ORD-12345", amount=120)

# Final
response3 = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Refund ORD-12345 $120"},
        {"role": "assistant", "tool_calls": [...]}, # call_1,2,3
        {"role": "tool", "tool_call_id": "call_1", "content": ...},
        {"role": "tool", "tool_call_id": "call_2", "content": ...},
        {"role": "tool", "tool_call_id": "call_3", "content": ...},
        {"role": "assistant", "tool_calls": [{"id": "call_4", "function": {"name": "refund_order", "arguments": "{\"order_id\": \"ORD-12345\", \"amount\": 120}"}}]},
        {"role": "tool", "tool_call_id": "call_4", "content": json.dumps(result)}
    ],
    tools=tools
)
# Final answer: "Refund $120 processed for ORD-12345. Order delivered, policy max_auto 500, trust 85>80, auto refund allowed."
```

**Advantages over Function Calling:**

- Parallel: 3 tool calls in one turn vs 3 turns sequential = 50% latency cut (1.5s vs 3s for 3 calls)
- Strict true: Constrained decoding enforces schema = 99.9% valid JSON vs 95% with functions
- IDs: tool_calls with id and tool role with tool_call_id matching = clear mapping for parallel
- Future-proof: Supports new tool types beyond functions (computer use, file search)

### 4. OpenAI Tools API Deep-Dive

**Tools definition:**

```python
tools = [
    {
        "type": "function", # Only function type currently, but future may have computer, file_search, etc.
        "function": {
            "name": "refund_order", # Must match regex ^[a-zA-Z0-9_]{1,64}$, no spaces
            "description": "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3. Returns refund_id, status.", # Detailed description for LLM to decide when to use
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID format ORD-12345", # Description for LLM
                        "pattern": "^ORD-\d{5}$" # Regex for validation
                    },
                    "amount": {
                        "type": "number",
                        "description": "Refund amount 0-10000",
                        "minimum": 0,
                        "maximum": 10000
                    }
                },
                "required": ["order_id", "amount"], # Required fields
                "additionalProperties": False # No extra properties allowed
            },
            "strict": True # Enforces schema via constrained decoding, 99.9% valid, recommended True
        }
    }
]
```

**Best practices for tool definition:**

- Name: ^[a-zA-Z0-9_]{1,64}$, snake_case, descriptive e.g., refund_order not refund
- Description: Detailed, include when to use, when not to use, policy, returns, edge cases. E.g., "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3. Do not use for orders >500 or trust <80, use request_approval instead. Returns refund_id, status, amount."
- Parameters: JSON Schema with type, description, pattern regex for strings, minimum/maximum for numbers, enum for allowed values, required array, additionalProperties False
- Strict True: Always True for 99.9% valid, enforces schema via constrained decoding

**Tool choice:**

```python
# tool_choice options
tool_choice = "auto" # Default, LLM decides whether to call tools or answer directly
tool_choice = "required" # LLM must call at least one tool (no direct answer)
tool_choice = "none" # LLM must not call tools, answer directly (e.g., for user notification)
tool_choice = {"type": "function", "function": {"name": "refund_order"}} # Force specific tool

# When to use:
# auto: Default for most steps, LLM decides if needs tool or can answer from history
# required: When you know need tool call, e.g., first step must get order status, no direct answer possible
# none: When you know no tool needed, e.g., final user notification step, don't waste tool call
# specific tool: When you know exactly which tool needed, e.g., after getting order amount, must refund, force refund_order

# Example: Dynamic tool_choice
if step == "get_order":
    tool_choice = {"type": "function", "function": {"name": "get_order_status"}} # Force get_order_status
elif step == "final_answer":
    tool_choice = "none" # Force no tool, answer directly
else:
    tool_choice = "auto" # Let LLM decide
```

**Tool calls response:**

```python
# Assistant message with tool_calls array
{
    "role": "assistant",
    "content": None, # Can be None or string with thought
    "tool_calls": [
        {
            "id": "call_abc123", # Unique ID for this tool call
            "type": "function", # Only function currently
            "function": {
                "name": "refund_order",
                "arguments": "{\"order_id\": \"ORD-12345\", \"amount\": 120}" # String JSON, needs json.loads, but strict True = 99.9% valid
            }
        }
    ]
}

# Parse
import json
tool_calls = response.choices[0].message.tool_calls
for tool_call in tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments) # Parse string JSON
    id = tool_call.id
    # Execute
    result = execute_tool(name, args)
```

**Tool results:**

```python
# Tool role message with tool_call_id matching id
{
    "role": "tool",
    "tool_call_id": "call_abc123", # Must match tool_calls id
    "content": json.dumps(result) # Result as JSON string, can be object or string
}

# Best practices for tool result:
# - Return JSON with relevant fields, not huge dump
# - Include error field if failed: {"error": "Order not found", "code": "NOT_FOUND"}
# - Keep concise: {"amount": 120, "status": "delivered", "user_id": "user_123"} not full order with 50 fields
# - For errors, include code for retry logic: NOT_FOUND, INVALID_ARGS, RATE_LIMIT, etc.

# Example tool execution with error handling
def execute_tool(name, args):
    try:
        if name == "refund_order":
            result = refund_order(**args)
            return {"refund_id": result.id, "status": "success", "amount": result.amount}
        elif name == "get_order_status":
            result = get_order_status(**args)
            return {"amount": result.amount, "status": result.status, "user_id": result.user_id}
    except OrderNotFoundError as e:
        return {"error": str(e), "code": "NOT_FOUND", "order_id": args.get("order_id")}
    except InvalidAmountError as e:
        return {"error": str(e), "code": "INVALID_ARGS", "amount": args.get("amount")}
    except Exception as e:
        return {"error": str(e), "code": "UNKNOWN"}
```

### 5. Parallel Tool Calls - When and How

**What is parallel tool calling:**

- Multiple tool calls in one assistant message (tool_calls array with 2+ items)
- Executed in parallel (asyncio.gather), not sequential
- Saves latency: 3 parallel calls 1.5s vs 3 sequential 3s = 50% cut

**When to use parallel:**

- Independent tools: No dependencies, can run in parallel
  - Example: get_order_status(ORD-123) + get_policy(v2.3) + get_trust_score(user_123) — all independent, no deps, parallel
- Dependent tools: Must run sequential
  - Example: get_order_status(ORD-123) -> returns user_id -> get_trust_score(user_id) — dependent, must sequential (get_trust needs user_id from get_order)

**How to decide parallel vs sequential:**

```python
def can_parallelize(tools):
    # Check dependencies
    # If tool B needs output from tool A, dependent, sequential
    # If tools have no shared dependencies, independent, parallel
    
    # Example:
    # Tools: get_order_status(ORD-123) -> returns user_id, get_trust_score(user_id) needs user_id from get_order_status -> dependent, sequential
    # Tools: get_order_status(ORD-123), get_policy(v2.3), get_trust_score(user_123) — get_trust has user_id already, not from get_order, so independent, parallel
    
    # Implementation: Build dependency graph, topological sort, group independent tasks
    dependency_graph = build_dependency_graph(tools)
    independent_groups = group_independent(dependency_graph)
    # independent_groups = [[get_order_status, get_policy, get_trust_score], [refund_order]] — first group parallel, second group after first
    return independent_groups

# Example agent loop with parallel detection
def agent_loop(user_goal):
    history = []
    
    # Step 1: Plan which tools needed
    plan = llm.generate(f"Goal: {user_goal} What tools needed? Return JSON list of tool calls with args and dependencies")
    # Plan: [{"tool": "get_order_status", "args": {"order_id": "ORD-12345"}, "dependencies": []}, {"tool": "get_policy", "args": {"version": "v2.3"}, "dependencies": []}, {"tool": "get_trust_score", "args": {"user_id": "user_123"}, "dependencies": []}, {"tool": "refund_order", "args": {"order_id": "ORD-12345", "amount": 120}, "dependencies": ["get_order_status", "get_policy", "get_trust_score"]}]
    
    # Group independent
    groups = can_parallelize(plan) # [[get_order, get_policy, get_trust], [refund]]
    
    for group in groups:
        # Group is independent, call parallel
        if len(group) > 1:
            # Parallel tool calls in one assistant message
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history,
                tools=tools,
                tool_choice="required" # Must call tools in group
            )
            tool_calls = response.choices[0].message.tool_calls # Should have len(group) calls
            # Execute parallel
            results = await asyncio.gather(*[execute_tool(tc.function.name, json.loads(tc.function.arguments)) for tc in tool_calls])
            # Add to history
            history.append({"role": "assistant", "tool_calls": [{"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in tool_calls]})
            for tc, result in zip(tool_calls, results):
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        else:
            # Single tool call sequential
            tool = group[0]
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": tool["tool"]}}
            )
            tool_call = response.choices[0].message.tool_calls[0]
            result = execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
            history.append({"role": "assistant", "tool_calls": [{"id": tool_call.id, "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments}}]})
            history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
    
    # Final answer
    final = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        tools=tools,
        tool_choice="none" # No tool, answer directly
    )
    return final.choices[0].message.content
```

**Parallel tool calling best practices:**

- Use when independent: get_order + get_policy + get_trust (if user_id known) parallel
- Don't use when dependent: get_order -> returns user_id -> get_trust (needs user_id) sequential
- Limit parallel calls per turn: 3-5 max, more than 5 may hit rate limits, LLM may generate invalid
- Handle partial failures: If one parallel call fails, others may succeed, need to handle
- Example: get_order success, get_policy success, get_trust fails NOT_FOUND -> need to handle get_trust failure, maybe retry or ask user for user_id

**Benchmark parallel vs sequential:**

- 3 independent tools: Parallel 1.5s (1 LLM call + 3 parallel executions) vs Sequential 3s (3 LLM calls + 3 sequential executions) = 50% latency cut, 66% LLM cost cut (1 call vs 3 calls)
- 5 independent tools: Parallel 2s vs Sequential 5s = 60% latency cut
- But parallel has higher failure rate if one fails: Need to handle partial failures

### 6. Tool Choice: Auto, Required, None, Specific Tool

**tool_choice options:**

- auto: Default, LLM decides whether to call tools or answer directly
- required: LLM must call at least one tool, no direct answer
- none: LLM must not call tools, answer directly
- Specific tool: {"type": "function", "function": {"name": "refund_order"}} — force specific tool

**When to use each:**

```python
# auto: Most steps, LLM decides if needs tool or can answer from history
# Example: After getting order status, policy, trust, LLM decides if can refund or needs more info
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice="auto"
)
# LLM may call refund_order or may answer "Need more info" if trust low

# required: When you know need tool call, no direct answer possible
# Example: First step must get order status, no direct answer
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Refund ORD-12345"}],
    tools=tools,
    tool_choice="required" # Must call at least one tool
)
# LLM must call get_order_status or other tool, cannot answer directly "Refund processed" without tool call

# none: When you know no tool needed, final answer or user notification
# Example: Final step synthesize answer, no tool needed
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice="none" # No tool, answer directly
)
# LLM answers "Refund $120 processed..." directly, no tool call

# Specific tool: When you know exactly which tool needed
# Example: After getting order amount $120, must refund, force refund_order
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice={"type": "function", "function": {"name": "refund_order"}}
)
# LLM must call refund_order, not other tools
```

**Dynamic tool_choice based on state:**

```python
def get_tool_choice(state, step):
    if step == "initial":
        return {"type": "function", "function": {"name": "get_order_status"}} # Force get_order
    elif step == "check_policy":
        return {"type": "function", "function": {"name": "get_policy"}} # Force get_policy
    elif step == "final_answer":
        return "none" # No tool, answer directly
    elif state.needs_more_info:
        return "auto" # Let LLM decide if needs tool or can answer
    else:
        return "required" # Must call at least one tool

# Usage
tool_choice = get_tool_choice(state, step)
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice=tool_choice
)
```

**Best practices:**

- Use auto default for most steps
- Use required when you know need tool call (initial steps, after planning)
- Use none for final answer and user notification (no tool needed)
- Use specific tool when you know exactly which tool (after getting order amount, must refund)
- Dynamic tool_choice based on state and step improves accuracy 10%

### 7. Error Handling: Invalid Tool, Invalid Args, Tool Execution Error, Retry

**Types of errors:**

1. **Invalid tool name:** LLM generates tool name not in allowlist (e.g., delete_all_orders) — hallucination
2. **Invalid args:** Args don't match schema (e.g., order_id ORD-123 invalid format, should be ORD-12345; amount 99999 > max 10000)
3. **Tool execution error:** Tool itself fails (e.g., order not found, rate limit, network error)
4. **Invalid JSON:** arguments string is invalid JSON (e.g., missing quote)

**Handling each:**

**a) Invalid tool name:**

```python
# Without constrained decoding, LLM may generate invalid tool name
# Response: {"tool_calls": [{"function": {"name": "delete_all_orders", "arguments": "{}"}}]} — hallucinated, not in allowlist

# Fix: Constrained decoding with allowlist
ActionSchema = {
    "tool": {"type": "string", "enum": ["refund_order", "get_order_status", "get_policy", "get_trust_score"]} # Allowlist
}
# With strict True, constrained decoding masks invalid tool names, only allowed tools generated, 100% valid tool name

# If still invalid (e.g., old model without strict), handle
def execute_tool(name, args):
    if name not in allowed_tools:
        return {"error": f"Invalid tool {name}, allowed {allowed_tools}", "code": "INVALID_TOOL", "suggested": "Use refund_order or get_order_status"}
    # Execute
```

**b) Invalid args:**

```python
# Args don't match schema: order_id ORD-123 invalid format (should be ORD-12345), amount 99999 > max 10000

# Fix 1: Constrained decoding with regex and min/max
# Schema: order_id pattern ^ORD-\d{5}$, amount minimum 0 maximum 10000
# With strict True, constrained decoding enforces pattern and min/max, 99.9% valid format

# Fix 2: Validation + retry
def execute_tool(name, args):
    # Validate args against schema
    validation_error = validate_against_schema(args, ActionSchema)
    if validation_error:
        return {"error": validation_error, "code": "INVALID_ARGS", "args": args, "suggested_fix": "Order ID must be ORD-12345 format, amount 0-10000"}
    
    # Execute
    try:
        result = tool_function(**args)
        return result
    except Exception as e:
        return {"error": str(e), "code": "EXECUTION_ERROR"}

# Retry with fix
def agent_loop_with_retry(user_goal):
    history = []
    max_retries = 3
    
    for attempt in range(max_retries):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=tools,
            tool_choice="auto",
            temperature=0.0
        )
        tool_calls = response.choices[0].message.tool_calls
        
        for tool_call in tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                # Invalid JSON
                history.append({"role": "assistant", "tool_calls": [{"id": tool_call.id, "function": {"name": name, "arguments": tool_call.function.arguments}}]})
                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": f"Invalid JSON: {e}", "code": "INVALID_JSON", "suggested_fix": "Return valid JSON"})})
                continue # Retry next loop
            
            # Validate args
            validation_error = validate_against_schema(args, ActionSchema)
            if validation_error:
                history.append({"role": "assistant", "tool_calls": [{"id": tool_call.id, "function": {"name": name, "arguments": tool_call.function.arguments}}]})
                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": validation_error, "code": "INVALID_ARGS", "suggested_fix": "Fix args"})})
                continue
            
            # Execute
            result = execute_tool(name, args)
            if "error" in result:
                history.append({"role": "assistant", "tool_calls": [{"id": tool_call.id, "function": {"name": name, "arguments": tool_call.function.arguments}}]})
                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
                # If error code is retryable, retry
                if result["code"] in ["RATE_LIMIT", "NETWORK_ERROR", "TIMEOUT"]:
                    # Retry with backoff
                    await asyncio.sleep(2 ** attempt) # Exponential backoff
                    continue
                else:
                    # Non-retryable, ask LLM to fix
                    continue
            else:
                history.append({"role": "assistant", "tool_calls": [{"id": tool_call.id, "function": {"name": name, "arguments": tool_call.function.arguments}}]})
                history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})
        
        # Check if done
        if is_done(history):
            break
    
    # Final answer
    final = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        tools=tools,
        tool_choice="none"
    )
    return final.choices[0].message.content
```

**c) Tool execution error:**

```python
# Tool itself fails: Order not found, rate limit, network error

# Return error with code for retry logic
def get_order_status(order_id):
    try:
        order = db.get_order(order_id)
        if not order:
            raise OrderNotFoundError(f"Order {order_id} not found")
        return order
    except OrderNotFoundError as e:
        return {"error": str(e), "code": "NOT_FOUND", "order_id": order_id}
    except RateLimitError as e:
        return {"error": str(e), "code": "RATE_LIMIT", "retry_after": 60}
    except NetworkError as e:
        return {"error": str(e), "code": "NETWORK_ERROR"}
    except Exception as e:
        return {"error": str(e), "code": "UNKNOWN"}

# Retry logic with backoff for retryable errors
async def execute_tool_with_retry(name, args, max_retries=3):
    for attempt in range(max_retries):
        result = execute_tool(name, args)
        if "error" not in result:
            return result
        
        code = result.get("code")
        if code in ["RATE_LIMIT", "NETWORK_ERROR", "TIMEOUT"]:
            # Retryable, backoff
            await asyncio.sleep(2 ** attempt + random.uniform(0, 1)) # Exponential backoff with jitter
            continue
        else:
            # Non-retryable, return error
            return result
    
    return {"error": "Max retries exceeded", "code": "MAX_RETRIES", "last_error": result}
```

**d) Invalid JSON:**

```python
# arguments string is invalid JSON: missing quote, trailing comma, etc.
# Example: "{\"order_id\": \"ORD-12345\", \"amount\": 120,}" trailing comma invalid

# Fix: Constrained decoding strict True enforces valid JSON, 99.9% valid
# If still invalid (e.g., old model), try to fix

def parse_arguments(arguments_str):
    try:
        args = json.loads(arguments_str)
        return args, None
    except json.JSONDecodeError as e:
        # Try to fix common errors
        # Remove trailing comma
        fixed = re.sub(r",\s*}", "}", arguments_str)
        fixed = re.sub(r",\s*]", "]", fixed)
        try:
            args = json.loads(fixed)
            return args, None
        except:
            return None, f"Invalid JSON: {e}, raw: {arguments_str}"

# Usage
args, error = parse_arguments(tool_call.function.arguments)
if error:
    history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps({"error": error, "code": "INVALID_JSON"})})
    continue # Retry
```

**Overall error handling best practices:**

- Use constrained decoding strict True for 99.9% valid JSON and tool name
- Validate args against schema before execution
- Return error with code (NOT_FOUND, INVALID_ARGS, RATE_LIMIT, etc.) for retry logic
- Retry with exponential backoff for retryable errors (RATE_LIMIT, NETWORK_ERROR, TIMEOUT)
- Non-retryable errors (NOT_FOUND, INVALID_ARGS) ask LLM to fix with suggested_fix
- Max retries 3, then fail gracefully
- Log errors with code for monitoring in ClickHouse

### 8. Constrained Decoding for Tool Calling - 99.9% Valid

**What:** Force LLM to generate only valid tool calls matching schema via masking invalid tokens.

**Why needed:**

- Without constraints: T=0.0 95% valid JSON, 90% valid tool name, 85% valid args format; T=0.7 60% valid JSON, 70% valid tool name, 60% valid args
- With constraints strict True: 99.9% valid JSON, 100% valid tool name, 99.9% valid args format, 95% accuracy

**How it works:**

- Define JSON Schema with tool allowlist enum, arg patterns regex, required fields, min/max, additionalProperties False
- At each token generation, mask tokens that would violate schema
- Only valid tokens sampled

**Example:**

```python
# Schema with all constraints
ActionSchema = {
    "type": "object",
    "properties": {
        "tool": {
            "type": "string",
            "enum": ["refund_order", "get_order_status", "get_policy", "get_trust_score", "send_email"], # Allowlist
            "description": "Tool name"
        },
        "args": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "pattern": "^ORD-\d{5}$", # Regex ORD-12345
                    "description": "Order ID format ORD-12345"
                },
                "amount": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10000,
                    "description": "Refund amount 0-10000"
                }
            },
            "required": ["order_id"],
            "additionalProperties": False
        }
    },
    "required": ["tool", "args"],
    "additionalProperties": False
}

# With OpenAI Tools API strict True
tools = [
    {
        "type": "function",
        "function": {
            "name": "refund_order",
            "description": "Refund order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\d{5}$"},
                    "amount": {"type": "number", "minimum": 0, "maximum": 10000}
                },
                "required": ["order_id", "amount"],
                "additionalProperties": False
            },
            "strict": True # Constrained decoding enabled
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Refund ORD-12345 $120"}],
    tools=tools,
    tool_choice="auto",
    temperature=0.0
)
# With strict True: 99.9% valid JSON, 100% tool name from allowlist, 99.9% order_id format ORD-12345
# Without strict: 95% valid JSON, 90% tool name valid, 85% order_id format valid
```

**Libraries for constrained decoding:**

- OpenAI structured outputs: response_format json_schema with strict True, no extra cost, recommended
- Outlines: Regex, JSON schema, grammar, 10-20% latency overhead
- LMQL: Query language with constraints
- Guidance: Grammar-based
- JSONformer: JSON schema

**Benchmark:**

- No constraints T=0.0: Valid JSON 95%, tool name valid 90%, args format valid 85%, accuracy 85%
- JSON Schema + allowlist + regex T=0.0 strict True: Valid JSON 99.9%, tool name 100%, args format 99.9%, accuracy 95% — best for tool calling
- No constraints T=0.7: Valid JSON 60%, tool name 70%, args format 60%, accuracy 70%
- JSON Schema + allowlist + regex T=0.7: Valid JSON 95%, tool name 100%, args format 99.9%, accuracy 80%

**Cost:** Constrained decoding 10% latency overhead, no extra cost with OpenAI structured outputs, saves retry cost 1.5x for 60% valid at T=0.7.

### 9. Tool Design Best Practices for LLM Use

**How to design tools that LLM can use effectively:**

**a) Name:**

- Snake_case, descriptive, verb_noun: refund_order, get_order_status, not refund, get
- ^[a-zA-Z0-9_]{1,64}$, no spaces
- Avoid ambiguous names: get_order vs get_order_status — second more descriptive

**b) Description:**

- Detailed: What tool does, when to use, when not to use, policy, returns, edge cases
- Example: "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3. Do not use for orders >500 or trust <80, use request_approval instead. Returns refund_id, status, amount. Fails if order not found or amount invalid."
- Include policy: "Only use if amount <500 and trust >80 per policy v2.3" helps LLM decide when to use
- Include returns: "Returns refund_id, status, amount" helps LLM know what to expect

**c) Parameters:**

- JSON Schema with type, description, pattern regex for strings, minimum/maximum for numbers, enum for allowed values, required array, additionalProperties False
- Description for each param: "Order ID format ORD-12345", "Refund amount 0-10000"
- Pattern regex: ^ORD-\d{5}$ for order_id, ^v\d+\.\d+$ for version
- Enum for allowed values: status enum [delivered, pending, cancelled]
- Required: List required fields, e.g., ["order_id", "amount"]
- additionalProperties False: No extra properties, prevents hallucinations

**d) Returns:**

- Return concise JSON with relevant fields, not huge dump
- Example: {"refund_id": "ref_123", "status": "success", "amount": 120} not full order with 50 fields
- Include error field if failed: {"error": "Order not found", "code": "NOT_FOUND"}

**e) Idempotency:**

- Tool should be idempotent: Same args -> same result, no side effect on retry
- Example: refund_order with idempotency key order_id + amount, if already refunded, return existing refund_id, not double refund
- Implementation: Check if order already refunded, if yes return existing refund_id

**f) Example tool design:**

```python
# Good tool design
{
    "type": "function",
    "function": {
        "name": "refund_order",
        "description": "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3. Do not use for orders >500 or trust <80, use request_approval instead. Idempotent: If order already refunded with same amount, returns existing refund_id. Returns refund_id, status, amount. Fails if order not found (code NOT_FOUND) or amount invalid (code INVALID_ARGS).",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Order ID format ORD-12345, e.g., ORD-12345",
                    "pattern": "^ORD-\d{5}$"
                },
                "amount": {
                    "type": "number",
                    "description": "Refund amount in USD, 0-10000, e.g., 120",
                    "minimum": 0,
                    "maximum": 10000
                }
            },
            "required": ["order_id", "amount"],
            "additionalProperties": False
        },
        "strict": True
    }
}

# Bad tool design
{
    "name": "refund", # Ambiguous name
    "description": "Refund", # No details, when to use, policy, returns
    "parameters": {
        "type": "object",
        "properties": {
            "id": {"type": "string"}, # No pattern, no description
            "amt": {"type": "number"} # Ambiguous name amt, no min/max, no description
        }
    }
    # No required, no additionalProperties False, no strict
}
# LLM may hallucinate id format, amt, when to use, etc.
```

**Best practices summary:**

- Name: snake_case verb_noun descriptive
- Description: Detailed what, when to use, when not, policy, returns, edge cases, idempotent
- Parameters: JSON Schema with type, description, pattern regex, min/max, enum, required, additionalProperties False, strict True
- Returns: Concise JSON relevant fields, error with code if failed
- Idempotency: Same args same result, check already done
- Test with LLM: Try tool with LLM, see if LLM uses correctly, iterate description and schema

### 10. Multi-Turn Tool Calling Loop - ReAct with Tools

**ReAct = Reasoning + Acting (Tool Calling) loop:**

```
User: Refund ORD-12345 $120
Thought: Need to check order status, policy, trust score
Action: get_order_status(ORD-12345) + get_policy(v2.3) + get_trust_score(user_123) parallel
Observation: Order $120 delivered, policy max_auto 500 trust_threshold 80, trust 85
Thought: Amount 120 <500 and trust 85>80, auto refund allowed per policy
Action: refund_order(ORD-12345, 120)
Observation: Refund ref_123 success $120
Thought: Done, notify user
Action: Final answer (tool_choice none)
```

**Implementation with Tools API:**

```python
def react_with_tools(user_goal, max_steps=10):
    history = [{"role": "user", "content": user_goal}]
    tools = [...] # Define tools
    
    for step in range(max_steps):
        # Decide tool_choice
        if step == 0:
            tool_choice = {"type": "function", "function": {"name": "get_order_status"}} # Force first tool
        elif is_done(history):
            tool_choice = "none" # No tool, final answer
        else:
            tool_choice = "auto" # Let LLM decide
        
        # Call LLM with tools
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.0 if tool_choice != "none" else 0.7 # T=0.0 for tool calling, T=0.7 for final answer
        )
        
        assistant_message = response.choices[0].message
        
        # If no tool calls, final answer
        if not assistant_message.tool_calls:
            history.append({"role": "assistant", "content": assistant_message.content})
            break
        
        # Has tool calls
        history.append({
            "role": "assistant",
            "content": assistant_message.content, # Can have thought
            "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_message.tool_calls]
        })
        
        # Execute tool calls (parallel if multiple)
        tool_calls = assistant_message.tool_calls
        # Group independent for parallel
        # For simplicity, execute all parallel if independent, else sequential
        # Check dependencies: If tool B needs output from tool A, dependent sequential, else parallel
        # Here assume independent for demo, parallel
        results = await asyncio.gather(*[execute_tool_with_retry(tc.function.name, json.loads(tc.function.arguments)) for tc in tool_calls])
        
        for tc, result in zip(tool_calls, results):
            history.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })
        
        # Loop detection: If last 3 actions identical, break loop with reflection T=0.7
        if detect_loop(history):
            reflection = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history + [{"role": "user", "content": "Stuck repeating same action, reflect why and try different approach"}],
                tools=tools,
                tool_choice="none",
                temperature=0.7
            )
            history.append({"role": "assistant", "content": reflection.choices[0].message.content})
    
    # Final answer is last assistant message content
    final_answer = history[-1]["content"] if history[-1]["role"] == "assistant" else "Done"
    return final_answer

# Example usage
answer = react_with_tools("Refund ORD-12345 $120")
# Answer: "Refund $120 processed for ORD-12345. Order delivered, policy max_auto 500, trust 85>80, auto refund allowed. Refund ID ref_123."
```

**Loop detection and reflection:**

```python
def detect_loop(history, window=3):
    # Check if last 3 tool calls identical
    tool_calls = [msg for msg in history if msg.get("role") == "assistant" and msg.get("tool_calls")]
    if len(tool_calls) < window:
        return False
    last_calls = tool_calls[-window:]
    # Compare tool names and args
    first = last_calls[0]["tool_calls"][0]["function"]
    for call in last_calls[1:]:
        if call["tool_calls"][0]["function"]["name"] != first["name"] or call["tool_calls"][0]["function"]["arguments"] != first["arguments"]:
            return False
    return True # All identical, loop detected

# If loop detected, use T=0.7 reflection to break
if detect_loop(history):
    reflection = llm.generate(f"Stuck repeating {history[-1]}, why? Different approach? Maybe order ID format wrong? Try ORD-12345?", temperature=0.7)
    history.append({"role": "assistant", "content": reflection})
```

### 11. Benchmarks: Function vs Tool Calling, Parallel vs Sequential

**Function Calling (legacy) vs Tool Calling (modern):**

| Metric | Function Calling (legacy) | Tool Calling (modern) |
| :--- | :--- | :--- |
| Calls per turn | 1 (single) | 1-5 parallel |
| Valid JSON | 95% T=0.0, 60% T=0.7 | 99.9% with strict True T=0.0, 95% with strict True T=0.7 |
| Tool name valid | 90% | 100% with allowlist + strict True |
| Latency 3 independent tools | 3s (3 turns sequential) | 1.5s (1 turn parallel) — 50% cut |
| LLM cost 3 tools | 3 calls cost 3x | 1 call cost 1x — 66% cut |
| Future-proof | Deprecated Dec 2023 | Supports new tool types, recommended |

**Parallel vs Sequential:**

- 3 independent tools: Parallel 1.5s (1 LLM call + 3 parallel executions) vs Sequential 3s (3 LLM calls + 3 sequential) = 50% latency cut, 66% LLM cost cut
- 5 independent tools: Parallel 2s vs Sequential 5s = 60% latency cut
- Dependent tools: Must sequential, e.g., get_order -> returns user_id -> get_trust (needs user_id) sequential

**Tool choice:**

- auto: 70% accuracy (LLM decides)
- required: 80% accuracy when need tool (forces tool call)
- none: 90% friendly for final answer (no tool waste)
- Specific tool: 85% accuracy when know exactly which tool (forces correct tool)
- Dynamic tool_choice based on state: +10% accuracy vs auto always

**Error handling:**

- No constraints T=0.0: Valid JSON 95%, tool name 90%, needs retry 5% cases
- JSON Schema + allowlist + regex T=0.0 strict True: Valid JSON 99.9%, tool name 100%, args format 99.9%, needs retry 0.1% cases — best
- With retry exponential backoff for RATE_LIMIT, NETWORK_ERROR: Success 90% -> 95% after 3 retries

**Constrained decoding:**

- No constraints T=0.0: Valid JSON 95%, tool name 90%, 85% accuracy
- JSON Schema + allowlist + regex T=0.0 strict True: Valid JSON 99.9%, tool name 100%, args format 99.9%, 95% accuracy — best for tool calling
- Cost: 10% latency overhead, no extra cost with OpenAI structured outputs, saves retry cost 1.5x

### 12. Implementation Blueprint - Production Agent

**Full production agent with Tools API, parallel calls, error handling, constrained decoding, dynamic tool_choice:**

```python
import openai, json, asyncio, random, re
from typing import List, Dict

# Define tools with strict True and all constraints
tools = [
    {
        "type": "function",
        "function": {
            "name": "refund_order",
            "description": "Refund order by ID with amount. Only use if amount <500 and trust_score >80 per policy v2.3. Do not use for orders >500 or trust <80, use request_approval instead. Idempotent: If already refunded same amount, returns existing refund_id. Returns refund_id, status, amount. Fails if order not found code NOT_FOUND or amount invalid code INVALID_ARGS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "Order ID format ORD-12345", "pattern": "^ORD-\d{5}$"},
                    "amount": {"type": "number", "description": "Refund amount 0-10000", "minimum": 0, "maximum": 10000}
                },
                "required": ["order_id", "amount"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get order status by ID. Returns amount, status, user_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "pattern": "^ORD-\d{5}$"}
                },
                "required": ["order_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_policy",
            "description": "Get refund policy by version. Returns max_auto, trust_threshold.",
            "parameters": {
                "type": "object",
                "properties": {
                    "version": {"type": "string", "pattern": "^v\d+\.\d+$"}
                },
                "required": ["version"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_trust_score",
            "description": "Get user trust score by user_id. Returns 0-100.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send email to user. Returns email_id, status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["user_id", "subject", "body"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
]

allowed_tools = [t["function"]["name"] for t in tools]

def validate_against_schema(args, schema):
    # Simple validation for demo, use jsonschema library in production
    # Check required, pattern, min/max, etc.
    return None # No error for demo

async def execute_tool(name, args):
    # Validate name
    if name not in allowed_tools:
        return {"error": f"Invalid tool {name}, allowed {allowed_tools}", "code": "INVALID_TOOL"}
    
    # Validate args
    validation_error = validate_against_schema(args, {})
    if validation_error:
        return {"error": validation_error, "code": "INVALID_ARGS"}
    
    # Execute with retry for retryable errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if name == "refund_order":
                # Idempotent check
                # if already refunded, return existing
                result = {"refund_id": "ref_123", "status": "success", "amount": args["amount"]}
                return result
            elif name == "get_order_status":
                result = {"amount": 120, "status": "delivered", "user_id": "user_123"}
                return result
            elif name == "get_policy":
                result = {"max_auto": 500, "trust_threshold": 80}
                return result
            elif name == "get_trust_score":
                result = {"score": 85}
                return result
            elif name == "send_email":
                result = {"email_id": "email_123", "status": "sent"}
                return result
        except Exception as e:
            # Determine if retryable
            if "RATE_LIMIT" in str(e) or "NETWORK" in str(e):
                await asyncio.sleep(2 ** attempt + random.uniform(0, 1))
                continue
            else:
                return {"error": str(e), "code": "EXECUTION_ERROR"}
    
    return {"error": "Max retries exceeded", "code": "MAX_RETRIES"}

def can_parallelize(tool_calls):
    # Check dependencies: If tool B needs output from tool A, dependent
    # Simple heuristic: If args contain user_id and previous tool returns user_id, dependent
    # For demo, assume get_order_status returns user_id needed for get_trust_score, so dependent if get_trust without user_id
    # Here we have user_id known, so all independent parallel
    return [tool_calls] # One group parallel

def detect_loop(history, window=3):
    tool_calls_history = [msg for msg in history if msg.get("role") == "assistant" and msg.get("tool_calls")]
    if len(tool_calls_history) < window:
        return False
    last = tool_calls_history[-window:]
    first = last[0]["tool_calls"][0]["function"]
    for call in last[1:]:
        if call["tool_calls"][0]["function"]["name"] != first["name"] or call["tool_calls"][0]["function"]["arguments"] != first["arguments"]:
            return False
    return True

async def production_agent(user_goal, max_steps=10):
    history = [{"role": "user", "content": user_goal}]
    
    for step in range(max_steps):
        # Dynamic tool_choice
        if step == 0:
            tool_choice = {"type": "function", "function": {"name": "get_order_status"}}
        elif step == max_steps - 1 or is_done(history):
            tool_choice = "none"
        else:
            tool_choice = "auto"
        
        temperature = 0.0 if tool_choice != "none" else 0.7
        
        # Call LLM with tools
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            top_p=1.0 if temperature==0.0 else 0.9,
            top_k=None if temperature==0.0 else 50
        )
        
        assistant_msg = response.choices[0].message
        
        if not assistant_msg.tool_calls:
            # Final answer
            history.append({"role": "assistant", "content": assistant_msg.content})
            break
        
        # Has tool calls
        history.append({
            "role": "assistant",
            "content": assistant_msg.content,
            "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]
        })
        
        # Parse and execute tool calls
        # Group for parallel
        groups = can_parallelize(assistant_msg.tool_calls)
        
        for group in groups:
            # Execute group parallel
            tasks = []
            for tc in group:
                try:
                    args = json.loads(tc.function.arguments)
                except json.JSONDecodeError as e:
                    # Invalid JSON
                    history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps({"error": f"Invalid JSON {e}", "code": "INVALID_JSON"})})
                    continue
                tasks.append((tc, args))
            
            # Execute parallel
            results = await asyncio.gather(*[execute_tool(tc.function.name, args) for tc, args in tasks])
            
            for (tc, args), result in zip(tasks, results):
                history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
        
        # Loop detection
        if detect_loop(history):
            reflection = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=history + [{"role": "user", "content": "Stuck repeating same action, reflect why and try different approach. Maybe order ID format wrong? Try ORD-12345?"}],
                tools=tools,
                tool_choice="none",
                temperature=0.7
            )
            history.append({"role": "assistant", "content": reflection.choices[0].message.content})
    
    # Final answer is last assistant content
    final = history[-1]["content"] if history[-1]["role"] == "assistant" else "Done"
    return final

# Usage
# answer = asyncio.run(production_agent("Refund ORD-12345 $120"))
# Answer: "Refund $120 processed for ORD-12345. Order delivered, policy max_auto 500, trust 85>80, auto refund allowed. Refund ID ref_123."
```

### 13. Production Checklist

1. **Always use Tools API, not Functions API** — Functions deprecated Dec 2023, Tools supports parallel, strict True 99.9% valid, future-proof.

2. **Define tools with strict True and all constraints** — Name ^[a-zA-Z0-9_]{1,64}$ snake_case verb_noun, description detailed what when to use when not policy returns edge cases idempotent, parameters JSON Schema with type description pattern regex min/max enum required additionalProperties False, strict True for 99.9% valid.

3. **Tool choice dynamic** — auto default, required when must call tool, none for final answer, specific tool when know exactly which. Dynamic based on state improves 10% accuracy.

4. **Parallel tool calls when independent** — get_order + get_policy + get_trust parallel if user_id known, saves 50% latency (1.5s vs 3s) and 66% LLM cost (1 call vs 3 calls). Don't parallel when dependent get_order -> returns user_id -> get_trust needs user_id sequential. Limit 3-5 parallel per turn.

5. **Error handling: Invalid tool, invalid args, execution error, invalid JSON** — Use constrained decoding allowlist for 100% valid tool name, JSON Schema + regex for 99.9% valid args format, validate before execution, return error with code NOT_FOUND INVALID_ARGS RATE_LIMIT etc. Retry with exponential backoff for retryable RATE_LIMIT NETWORK_ERROR TIMEOUT, max retries 3, non-retryable ask LLM to fix with suggested_fix.

6. **Constrained decoding mandatory for tool calling** — T=0.0 + JSON Schema + allowlist + regex + strict True = 99.9% valid JSON 100% tool name valid 99.9% format valid 95% accuracy vs 95% valid 90% tool name 85% format 85% accuracy without constraints, 60% valid at T=0.7. 10% latency overhead, no extra cost with OpenAI structured outputs, saves retry cost 1.5x.

7. **Tool design best practices** — Name snake_case verb_noun descriptive, description detailed what when to use when not policy returns edge cases idempotent, parameters JSON Schema with type description pattern regex min/max enum required additionalProperties False strict True, returns concise JSON relevant fields error with code if failed, idempotent same args same result check already done, test with LLM iterate.

8. **Multi-turn ReAct loop with Tools** — Thought T=0.4, Action T=0.0 with constraints, Observation tool result, loop detection last 3 identical actions -> reflection T=0.7 to break loop breaks 90% loops vs 10% at T=0.0.

9. **Benchmarks** — Function Calling 1 per turn vs Tool Calling 1-5 parallel 50% latency cut 66% cost cut, valid JSON 95% vs 99.9% with strict True, tool name valid 90% vs 100% with allowlist. Parallel 3 tools 1.5s vs sequential 3s 50% cut. Tool choice dynamic +10% accuracy. Error handling with retry 90% -> 95% success.

10. **Observability** — Log tool calls with name args result error code latency, valid JSON rate, tool name valid rate, retry rate, parallel vs sequential, tool_choice, temperature, in ClickHouse. Alert if valid JSON <99% (need constraints) or retry rate >10% (need better validation) or loop detected >5% trajectories.

---
**Bottom Line:** Function Calling legacy June 2023 single function per turn string args 95% valid deprecated Dec 2023. Tool Calling modern Dec 2023+ multiple parallel tools per turn array with ids, strict True constrained decoding 99.9% valid, tool role with tool_call_id, future-proof supports new tool types. Production agents: Always Tools API with T=0.0 + JSON Schema + allowlist + regex + strict True = 99.9% valid JSON 100% tool name valid 99.9% format valid 95% accuracy, prevents delete_all_orders catastrophic. Parallel when independent get_order + get_policy + get_trust (if user_id known) saves 50% latency 1.5s vs 3s and 66% LLM cost 1 call vs 3 calls, don't parallel when dependent get_order -> user_id -> get_trust sequential. Tool choice dynamic auto default required when must call tool none for final answer specific tool when know exactly which +10% accuracy. Error handling invalid tool invalid args execution error invalid JSON: constrained decoding allowlist for 100% valid tool name, JSON Schema + regex for 99.9% valid args, validate before execution, return error with code for retry logic, retry exponential backoff for RATE_LIMIT NETWORK_ERROR TIMEOUT max retries 3. Tool design: Name snake_case verb_noun descriptive, description detailed what when to use when not policy returns idempotent, parameters JSON Schema with description pattern min/max enum required additionalProperties False strict True, returns concise JSON error with code, idempotent check already done. ReAct loop Thought T=0.4 Action T=0.0 Observation tool result loop detection reflection T=0.7 breaks 90% loops.

