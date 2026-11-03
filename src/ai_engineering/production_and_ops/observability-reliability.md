# Observability & Reliability for Agentic AI: Tracing, Logging, Monitoring, Latency, Cost
## Complete Production Guide - OpenTelemetry, LangSmith, ClickHouse, Streaming, Budgeting

> **Core Thesis:** Agents are non-deterministic black boxes - without observability you cannot debug loops, cost blowups, or policy violations. Tracing with OpenTelemetry + LangSmith/Langfuse gives you full trajectory: Thought->Action->Observation with latency, cost, tokens, tool args. Logging to ClickHouse gives you per-agent per-task per-tool analytics. Latency optimization via streaming, parallel tool calls, speculation cuts 3s to 1.5s (50%). Cost tracking per-agent per-tool with budgeting prevents $1000 runaway. Production: Always trace every LLM call and tool call, log to ClickHouse, stream final answer, parallel independent tools, track cost with circuit breaker, alert if cost > budget or latency > SLA.

### Table of Contents
1. Why Observability & Reliability for Agents? The Black Box Problem
2. Tracing & Observability - OpenTelemetry, LangSmith, Langfuse
3. Logging & Monitoring for Agents - ClickHouse, Prometheus, Grafana Setup
4. Latency & Throughput Optimization - Streaming, Parallel, Speculation
5. Cost Tracking & Budgeting - Per-Agent, Per-Task, Per-Tool Cost
6. Complete Implementation Blueprint
7. Failure Modes: Loops, Cost Blowups, Policy Violations
8. Benchmarks
9. Production Checklist

---

### 1. Why Observability & Reliability for Agents? The Black Box Problem

**Problem:** Agent is non-deterministic, multi-step, tool calling, can loop, cost blowup, policy violation. Without observability you cannot debug.

Example without observability:
- User: Refund ORD-12345 $120
- Agent loops: get_order_status -> trust 70 -> refund_order -> fails TRUST_LOW -> get_order_status -> trust 70 -> refund_order -> fails TRUST_LOW -> ... loop 10 times
- Cost: 10 LLM calls * $0.01 = $0.10, latency 10s, user frustrated, no refund
- Without tracing: You see final "Failed" but not why loop, which tool failed, which policy, cost, latency per step
- Without logging: You cannot aggregate loop rate, cost per agent, failure rate
- Without cost tracking: Cost blowup $1000 runaway if agent loops 1000 times

**With observability:**
- Tracing: Full trajectory Thought->Action->Observation with latency, cost, tokens, tool args, error_code
  - Trace: Step1 get_order_status latency 0.5s cost $0.005 tokens 100, Step2 get_trust_score latency 0.5s cost $0.005, Step3 refund_order fails TRUST_LOW latency 0.5s cost $0.005 error_code TRUST_LOW, Step4 loop detection same action 3 times -> reflection T=0.7 -> request_approval -> success
  - You see loop, error_code, reflection breaks loop
- Logging to ClickHouse: Per-agent per-task per-tool analytics
  - SELECT agent_id, count(*) as loops WHERE error_code='TRUST_LOW' AND loop_detected=1 GROUP BY agent_id -> agent_123 loop rate 10%
  - SELECT tool_name, avg(cost) as avg_cost GROUP BY tool_name -> refund_order avg cost $0.01
  - Alert if loop rate >5% or cost > budget $100
- Latency optimization: Streaming final answer, parallel independent tools, speculation cuts latency 3s to 1.5s 50% cut
- Cost tracking: Per-agent per-task per-tool cost with budgeting, circuit breaker if cost > budget $100, prevents $1000 runaway

**Why need all four:**
- Tracing: Debug single trajectory why failed, loop, policy violation
- Logging & Monitoring: Aggregate analytics per-agent per-task per-tool, alert if loop rate high or cost blowup
- Latency Optimization: Streaming, parallel, speculation cuts latency, improves UX
- Cost Tracking & Budgeting: Per-agent per-task per-tool cost, budgeting, circuit breaker prevents runaway

**Production: Always trace every LLM call and tool call, log to ClickHouse, stream final answer, parallel independent tools, track cost with circuit breaker, alert if cost > budget or latency > SLA.**

### 2. Tracing & Observability - OpenTelemetry, LangSmith, Langfuse

**What is tracing:**

Trace = full trajectory of agent execution: User goal -> Thought->Action->Observation loop -> Final answer, with spans for each LLM call and tool call, with attributes latency, cost, tokens, tool args, error_code.

Example trace for refund $120:
- Trace ID: trace_123, Root span: agent_execution user_goal Refund ORD-12345 $120
  - Span1: LLM call planning, latency 0.5s, cost $0.005, tokens input 100 output 50, tool_choice auto, temperature 0.7
  - Span2: Tool call get_order_status, latency 0.3s, cost $0, args order_id ORD-12345, result amount 120 status delivered user_id user_123, error_code none
  - Span3: LLM call reasoning, latency 0.5s, cost $0.005, tokens 100/50
  - Span4: Tool call get_trust_score, latency 0.3s, args user_id user_123, result score 70, error_code none
  - Span5: LLM call reasoning, latency 0.5s
  - Span6: Tool call refund_order, latency 0.5s, args order_id ORD-12345 amount 120, result error TRUST_LOW trust 70<80 need approval, error_code TRUST_LOW
  - Span7: LLM call reflection, latency 0.5s, temperature 0.7, lesson Trust 70<80 need approval
  - Span8: Tool call request_approval, latency 0.5s, args order_id ORD-12345 amount 120 reason trust 70<80, result approval_id appr_123 waiting
  - Span9: LLM call final answer, latency 0.5s, temperature 0.7, tool_choice none, output Refund $120 needs approval approval_id appr_123

**OpenTelemetry:**

OpenTelemetry = open standard for tracing, metrics, logging, with SDK for Python, instrumentation for LLM calls and tool calls.

Setup:
```
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

Instrumentation for LLM calls and tool calls:
```
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Setup tracer provider
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# OTLP exporter to Jaeger or Honeycomb or LangSmith
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument LLM call
with tracer.start_as_current_span("llm_call") as span:
    span.set_attribute("llm.model", "gpt-4o-mini")
    span.set_attribute("llm.temperature", 0.0)
    span.set_attribute("llm.tool_choice", "auto")
    span.set_attribute("llm.input_tokens", 100)
    span.set_attribute("llm.output_tokens", 50)
    span.set_attribute("llm.cost", 0.005)
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        tools=tools,
        tool_choice="auto",
        temperature=0.0
    )
    span.set_attribute("llm.output", response.choices[0].message.content)

# Instrument tool call
with tracer.start_as_current_span("tool_call") as span:
    span.set_attribute("tool.name", "get_order_status")
    span.set_attribute("tool.args", json.dumps({"order_id": "ORD-12345"}))
    result = execute_tool("get_order_status", {"order_id": "ORD-12345"})
    span.set_attribute("tool.result", json.dumps(result))
    span.set_attribute("tool.error_code", result.get("code", "none"))
    span.set_attribute("tool.latency", 0.3)
```

**LangSmith:**

LangSmith = LangChain tracing platform, auto instruments LangChain agents, LangGraph, with UI for traces, analytics, evaluation.

Setup:
```
pip install langsmith
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_key
export LANGCHAIN_PROJECT=refund_agent
```

Auto tracing for LangChain:
```
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# LangSmith auto traces
result = agent_executor.invoke({"input": "Refund ORD-12345 $120"})
# Trace in LangSmith UI: Full trajectory with latency, cost, tokens, tool calls
```

LangSmith features:
- Traces: Full trajectory with spans for LLM calls and tool calls, latency, cost, tokens
- Analytics: Aggregate latency, cost, success rate per agent, per tool
- Evaluation: Compare traces, evaluate quality, success rate
- Debugging: See why loop, which tool failed, which policy violated

**Langfuse:**

Langfuse = open source tracing platform, similar to LangSmith, with self-hosted option.

Setup:
```
pip install langfuse
export LANGFUSE_PUBLIC_KEY=pk-...
export LANGFUSE_SECRET_KEY=sk-...
export LANGFUSE_HOST=https://cloud.langfuse.com

from langfuse import Langfuse
from langfuse.openai import openai # Wrapper

langfuse = Langfuse()

# Wrap OpenAI client
import openai
openai_client = openai.OpenAI()

# Langfuse auto traces via wrapper
response = openai_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Refund ORD-12345 $120"}],
    tools=tools
)

# Trace in Langfuse UI
```

Langfuse features similar to LangSmith, plus self-hosted, open source.

**Best practices for tracing:**

- Trace every LLM call and tool call with span, attributes latency, cost, tokens, tool args, error_code, model, temperature, tool_choice
- Use OpenTelemetry standard for interoperability with Jaeger, Honeycomb, LangSmith, Langfuse
- Use LangSmith or Langfuse for agent-specific tracing with UI, analytics, evaluation
- Add baggage: trace_id, user_id, session_id, agent_id for correlation
- Sample traces: 100% for errors, loops, high-cost, 10% for success low-cost to save cost
- Alert if trace has loop_detected or error_code TRUST_LOW or latency > SLA

**Cost of tracing:**

- OpenTelemetry: Free, open source, self-hosted
- LangSmith: Free tier 5000 traces/month, paid $39/month for 10000 traces
- Langfuse: Open source self-hosted free, cloud free tier 1000 traces/day, paid $39/month
- Overhead: 1-5% latency overhead for tracing, negligible

### 3. Logging & Monitoring for Agents - ClickHouse, Prometheus, Grafana Setup

**What is logging & monitoring:**

Logging = store structured logs of agent execution per step, with fields agent_id, task, tool_name, latency, cost, tokens, error_code, success, loop_detected, reflection lesson, in ClickHouse for analytics.

Monitoring = aggregate metrics from logs, e.g., avg latency, p95 latency, success rate, loop rate, cost per agent, per tool, per task, error rate per error_code, with Prometheus metrics and Grafana dashboards, alert if SLA violated.

**ClickHouse:**

ClickHouse = columnar database for analytics, fast aggregation, low cost, ideal for agent logs.

Setup:
```
# Docker
docker run -d --name clickhouse -p 9000:9000 -p 8123:8123 clickhouse/clickhouse-server

# Create table for agent logs
CREATE TABLE agent_logs (
    timestamp DateTime,
    trace_id String,
    agent_id String,
    user_id String,
    session_id String,
    task String,
    step UInt32,
    llm_model String,
    llm_temperature Float32,
    llm_tool_choice String,
    llm_input_tokens UInt32,
    llm_output_tokens UInt32,
    llm_cost Float32,
    llm_latency Float32,
    tool_name String,
    tool_args String,
    tool_result String,
    tool_error_code String,
    tool_latency Float32,
    tool_cost Float32,
    success Bool,
    loop_detected Bool,
    reflection_lesson String,
    error_code String
) ENGINE = MergeTree()
ORDER BY (timestamp, agent_id, trace_id)
```

Logging from agent:
```
import clickhouse_connect

client = clickhouse_connect.get_client(host='localhost', port=8123)

def log_agent_step(trace_id, agent_id, user_id, session_id, task, step, llm_model, llm_temperature, llm_tool_choice, llm_input_tokens, llm_output_tokens, llm_cost, llm_latency, tool_name, tool_args, tool_result, tool_error_code, tool_latency, tool_cost, success, loop_detected, reflection_lesson, error_code):
    client.insert('agent_logs', [[
        datetime.now(),
        trace_id,
        agent_id,
        user_id,
        session_id,
        task,
        step,
        llm_model,
        llm_temperature,
        llm_tool_choice,
        llm_input_tokens,
        llm_output_tokens,
        llm_cost,
        llm_latency,
        tool_name,
        json.dumps(tool_args),
        json.dumps(tool_result),
        tool_error_code,
        tool_latency,
        tool_cost,
        success,
        loop_detected,
        reflection_lesson,
        error_code
    ]], column_names=['timestamp', 'trace_id', 'agent_id', 'user_id', 'session_id', 'task', 'step', 'llm_model', 'llm_temperature', 'llm_tool_choice', 'llm_input_tokens', 'llm_output_tokens', 'llm_cost', 'llm_latency', 'tool_name', 'tool_args', 'tool_result', 'tool_error_code', 'tool_latency', 'tool_cost', 'success', 'loop_detected', 'reflection_lesson', 'error_code'])

# Usage in agent loop
for step in range(max_steps):
    # LLM call
    llm_start = time.time()
    response = openai.chat.completions.create(...)
    llm_latency = time.time() - llm_start
    llm_cost = calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens, model)
    
    log_agent_step(
        trace_id=trace_id,
        agent_id=agent_id,
        user_id=user_id,
        session_id=session_id,
        task=user_goal,
        step=step,
        llm_model="gpt-4o-mini",
        llm_temperature=temperature,
        llm_tool_choice=tool_choice,
        llm_input_tokens=response.usage.prompt_tokens,
        llm_output_tokens=response.usage.completion_tokens,
        llm_cost=llm_cost,
        llm_latency=llm_latency,
        tool_name=None,
        tool_args=None,
        tool_result=None,
        tool_error_code=None,
        tool_latency=None,
        tool_cost=None,
        success=False,
        loop_detected=False,
        reflection_lesson=None,
        error_code=None
    )
    
    # Tool call
    tool_start = time.time()
    result = execute_tool(tool_name, args)
    tool_latency = time.time() - tool_start
    tool_cost = 0 # Tool cost free or API cost
    
    log_agent_step(
        trace_id=trace_id,
        agent_id=agent_id,
        user_id=user_id,
        session_id=session_id,
        task=user_goal,
        step=step,
        llm_model=None,
        llm_temperature=None,
        llm_tool_choice=None,
        llm_input_tokens=None,
        llm_output_tokens=None,
        llm_cost=None,
        llm_latency=None,
        tool_name=tool_name,
        tool_args=args,
        tool_result=result,
        tool_error_code=result.get("code", "none"),
        tool_latency=tool_latency,
        tool_cost=tool_cost,
        success=is_success(result),
        loop_detected=detect_loop(history),
        reflection_lesson=None,
        error_code=result.get("code", "none")
    )
```

Analytics queries in ClickHouse:
```
-- Success rate per agent
SELECT agent_id, count(*) as total, sum(success) as successes, successes/total as success_rate FROM agent_logs GROUP BY agent_id

-- Loop rate per agent
SELECT agent_id, count(*) as total, sum(loop_detected) as loops, loops/total as loop_rate FROM agent_logs GROUP BY agent_id

-- Cost per agent
SELECT agent_id, sum(llm_cost + tool_cost) as total_cost FROM agent_logs GROUP BY agent_id ORDER BY total_cost DESC

-- Cost per tool
SELECT tool_name, sum(tool_cost) as total_cost, avg(tool_latency) as avg_latency, count(*) as calls FROM agent_logs WHERE tool_name IS NOT NULL GROUP BY tool_name ORDER BY total_cost DESC

-- Error rate per error_code
SELECT error_code, count(*) as errors FROM agent_logs WHERE error_code != 'none' GROUP BY error_code ORDER BY errors DESC

-- Latency p95 per agent
SELECT agent_id, quantile(0.95)(llm_latency + tool_latency) as p95_latency FROM agent_logs GROUP BY agent_id

-- Reflection lessons
SELECT reflection_lesson, count(*) as occurrences FROM agent_logs WHERE reflection_lesson IS NOT NULL GROUP BY reflection_lesson ORDER BY occurrences DESC
```

**Prometheus & Grafana:**

Prometheus = metrics database, Grafana = dashboard UI, for monitoring agent metrics.

Setup Prometheus metrics from agent:
```
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Metrics
agent_requests_total = Counter('agent_requests_total', 'Total agent requests', ['agent_id', 'task', 'success'])
agent_latency_seconds = Histogram('agent_latency_seconds', 'Agent latency', ['agent_id', 'task'])
agent_cost_dollars = Histogram('agent_cost_dollars', 'Agent cost', ['agent_id', 'task'])
agent_tool_calls_total = Counter('agent_tool_calls_total', 'Total tool calls', ['agent_id', 'tool_name', 'error_code'])
agent_loops_total = Counter('agent_loops_total', 'Total loops detected', ['agent_id'])
agent_errors_total = Counter('agent_errors_total', 'Total errors', ['agent_id', 'error_code'])

# Start Prometheus metrics server
start_http_server(8000)

# Usage in agent
def agent_with_metrics(user_goal, agent_id):
    start = time.time()
    try:
        result = agent(user_goal)
        success = True
    except Exception as e:
        success = False
        result = str(e)
    
    latency = time.time() - start
    cost = calculate_cost(...)
    
    agent_requests_total.labels(agent_id=agent_id, task=user_goal, success=str(success)).inc()
    agent_latency_seconds.labels(agent_id=agent_id, task=user_goal).observe(latency)
    agent_cost_dollars.labels(agent_id=agent_id, task=user_goal).observe(cost)
    
    return result

# Prometheus config prometheus.yml
# scrape_configs:
#   - job_name: 'agent'
#     static_configs:
#       - targets: ['localhost:8000']
```

Grafana dashboard:
- Create dashboard with panels:
  - Success rate per agent: rate(agent_requests_total{success="True"}[5m]) / rate(agent_requests_total[5m])
  - Loop rate per agent: rate(agent_loops_total[5m])
  - Cost per agent: sum(agent_cost_dollars) by (agent_id)
  - Latency p95 per agent: histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m]))
  - Error rate per error_code: rate(agent_errors_total[5m]) by (error_code)
  - Tool calls per tool: rate(agent_tool_calls_total[5m]) by (tool_name)

Setup Grafana:
```
# Docker
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Add Prometheus data source: http://localhost:9090
# Create dashboard with panels above
```

**Best practices for logging & monitoring:**

- Log every LLM call and tool call with trace_id, agent_id, user_id, session_id, task, step, latency, cost, tokens, error_code, success, loop_detected, reflection_lesson
- Use ClickHouse for analytics, fast aggregation, low cost, retention 90 days
- Use Prometheus for metrics, Grafana for dashboards, alert if success rate <80% or loop rate >5% or cost > budget $100 or latency p95 > SLA 5s or error rate >10%
- Sample logs: 100% for errors, loops, high-cost, 10% for success low-cost to save cost
- Retention: ClickHouse 90 days, Prometheus 15 days, Grafana dashboards permanent

**Cost of logging & monitoring:**

- ClickHouse: Self-hosted free, cloud $0.01 per GB ingested, $0.01 per GB stored, for 1M agent logs ~1GB, cost $0.01/month negligible
- Prometheus: Self-hosted free, storage 15 days ~1GB for 1M metrics, cost negligible
- Grafana: Self-hosted free, cloud free tier 10000 metrics, paid $8/month
- Overhead: 1-5% latency overhead for logging, negligible

### 4. Latency & Throughput Optimization - Streaming, Parallel, Speculation

**What is latency & throughput optimization:**

Latency = time from user goal to final answer, e.g., 3s for refund $120 with 3 tool calls sequential. Throughput = requests per second, e.g., 10 rps.

Optimization techniques:
- Streaming: Stream final answer token by token, not wait for full answer, improves perceived latency
- Parallel tool calls: Execute independent tools parallel, not sequential, cuts latency 50%
- Speculation: Speculatively execute tool calls before LLM confirms, cuts latency
- Caching: Cache tool results, LLM calls, avoids recomputation
- Model cascades: Use small model for simple tasks, large model for complex, cuts cost and latency

**Streaming:**

Streaming = LLM generates tokens one by one, stream to user immediately, not wait for full answer.

Setup with OpenAI streaming:
```
import openai

# Streaming final answer
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice="none", # Final answer no tool
    temperature=0.7,
    stream=True # Enable streaming
)

# Stream tokens
for chunk in response:
    if chunk.choices[0].delta.content:
        token = chunk.choices[0].delta.content
        # Send token to user via WebSocket or SSE
        print(token, end='', flush=True)
        # For web UI, send via SSE: yield f"data: {token}\\n\\n"

# Perceived latency: User sees first token immediately, not wait for full answer 2s, improves UX
# Actual latency same, but perceived latency lower
```

Streaming with tool calls:
```
# For tool calling steps, cannot stream tool calls, but can stream thoughts
response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=history,
    tools=tools,
    tool_choice="auto",
    temperature=0.0,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        # Thought content streaming
        print(chunk.choices[0].delta.content, end='', flush=True)
    if chunk.choices[0].delta.tool_calls:
        # Tool calls not streamable, need full tool_calls array
        pass
```

Best practices for streaming:
- Stream final answer (tool_choice none) with temperature 0.7 friendly, improves perceived latency 2s to 0.5s first token
- For tool calling steps, stream thought content if present, but tool calls need full array
- Use SSE or WebSocket for web UI, send token by token
- Overhead: Streaming adds 5% latency overhead for chunking, negligible

**Parallel tool calls:**

Parallel = Execute independent tools in parallel via asyncio.gather, not sequential, cuts latency 50% for 3 independent tools 1.5s vs 3s.

Example:
```
# Independent tools: get_order_status + get_policy + get_trust_score with user_id known -> independent parallel
# Dependent tools: get_order_status -> returns user_id -> get_trust_score needs user_id -> dependent sequential

# Detect independent vs dependent
def can_parallelize(tool_calls, history):
    # Check if tool B needs output from tool A
    # For demo, assume get_order_status returns user_id needed for get_trust_score if user_id unknown
    # If user_id known, independent parallel, else dependent sequential
    dependencies = {}
    for tc in tool_calls:
        if tc["tool"] == "get_trust_score" and "user_id" not in tc["args"]:
            # Needs user_id from get_order_status
            dependencies[tc["id"]] = ["get_order_status"]
        else:
            dependencies[tc["id"]] = []
    
    # Topological sort
    sorted_groups = topological_sort(dependencies) # [[get_order_status, get_policy], [get_trust_score], [refund_order]] etc.
    return sorted_groups

# Execution
sorted_groups = can_parallelize(tool_calls, history)
for group in sorted_groups:
    # Group independent parallel
    results = await asyncio.gather(*[execute_tool(tc["tool"], tc["args"]) for tc in group])
    # Add to history
    for tc, result in zip(group, results):
        history.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(result)})

# Benchmark parallel vs sequential
# 3 independent tools: Parallel 1.5s (1 LLM call + 3 parallel executions 0.5s) vs Sequential 3s (3 LLM calls 0.5s each + 3 executions 0.5s each) = 50% latency cut, 66% LLM cost cut (1 call vs 3 calls)
# 5 independent tools: Parallel 2s vs Sequential 5s = 60% latency cut
```

Best practices for parallel:
- Use when independent: get_order + get_policy + get_trust with user_id known parallel
- Don't use when dependent: get_order -> returns user_id -> get_trust needs user_id sequential
- Limit parallel calls per turn 3-5 max, more than 5 may hit rate limits
- Handle partial failures: If one parallel call fails, others may succeed, need to handle
- Example: get_order success, get_policy success, get_trust fails NOT_FOUND -> handle get_trust failure, retry or ask user

**Speculation:**

Speculation = Speculatively execute tool calls before LLM confirms, based on prediction, cuts latency if prediction correct, wastes cost if wrong.

Example speculative execution:
```
# User: Refund ORD-12345 $120
# Predict next tool call likely get_order_status(ORD-12345) because refund needs order status
# Speculatively execute get_order_status(ORD-12345) before LLM call, latency 0.3s
# Then LLM call with history, if LLM indeed calls get_order_status(ORD-12345), result already available, save 0.3s latency
# If LLM calls different tool, wasted cost $0, but latency not saved

# Implementation
async def agent_with_speculation(user_goal):
    history = [{"role": "user", "content": user_goal}]
    
    # Speculative prediction: What tool likely next?
    # Use heuristics: If goal contains ORD-12345 and refund, likely get_order_status(ORD-12345)
    predicted_tool = predict_next_tool(user_goal, history) # e.g., get_order_status with ORD-12345
    
    # Speculatively execute predicted tool in background
    speculative_task = asyncio.create_task(execute_tool(predicted_tool["tool"], predicted_tool["args"]))
    
    # LLM call
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        tools=tools,
        tool_choice="auto",
        temperature=0.0
    )
    
    tool_calls = response.choices[0].message.tool_calls
    
    # Check if speculative prediction correct
    if tool_calls and tool_calls[0].function.name == predicted_tool["tool"] and json.loads(tool_calls[0].function.arguments) == predicted_tool["args"]:
        # Correct prediction, use speculative result
        result = await speculative_task
        history.append({"role": "assistant", "tool_calls": [{"id": tool_calls[0].id, "function": {"name": tool_calls[0].function.name, "arguments": tool_calls[0].function.arguments}}]})
        history.append({"role": "tool", "tool_call_id": tool_calls[0].id, "content": json.dumps(result)})
        latency_saved = 0.3 # Speculative execution saved 0.3s
    else:
        # Wrong prediction, cancel speculative task, execute actual tool calls
        speculative_task.cancel()
        for tc in tool_calls:
            args = json.loads(tc.function.arguments)
            result = await execute_tool(tc.function.name, args)
            history.append({"role": "assistant", "tool_calls": [{"id": tc.id, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}]})
            history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    
    # Continue loop...

def predict_next_tool(user_goal, history):
    # Heuristics: If user_goal contains ORD-12345 and refund, predict get_order_status(ORD-12345)
    # For production, use small model to predict next tool call
    if "ORD-" in user_goal and "refund" in user_goal.lower():
        order_id = extract_order_id(user_goal) # Regex ORD-\d{5}
        return {"tool": "get_order_status", "args": {"order_id": order_id}}
    return None

# Benchmark speculation
# Without speculation: LLM call 0.5s + tool execution 0.3s = 0.8s per step
# With speculation correct prediction 80% of time: Speculative execution 0.3s in parallel with LLM call 0.5s, total 0.5s if correct (save 0.3s), if wrong 0.8s + wasted 0.3s cost
# Average latency: 0.8*0.2 + 0.5*0.8 = 0.56s vs 0.8s without = 30% latency cut for 80% correct prediction
# Cost: Wasted speculative executions 20% * tool cost, negligible if tool cost free
```

Best practices for speculation:
- Use when next tool predictable with high probability 80%+, e.g., refund always needs get_order_status first
- Speculative execution in background parallel with LLM call, save latency if correct
- Cancel speculative task if wrong prediction, waste cost but save latency if correct
- Use small model to predict next tool call for better accuracy
- Benchmark: 30% latency cut for 80% correct prediction, worth if tool cost low

**Caching:**

Caching = Cache tool results and LLM calls to avoid recomputation, cuts latency and cost.

Example caching:
```
from functools import lru_cache

# Cache tool results
@lru_cache(maxsize=100)
def get_order_status_cached(order_id):
    return get_order_status(order_id) # DB call

# Cache LLM calls with same prompt
@lru_cache(maxsize=100)
def llm_call_cached(prompt, model, temperature):
    response = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    return response.choices[0].message.content

# Usage
order = get_order_status_cached("ORD-12345") # First call DB, second call cache
answer = llm_call_cached("Refund ORD-12345 $120", "gpt-4o-mini", 0.0) # First call LLM, second call cache

# For agent, cache tool results per trace_id
tool_cache = {}
def execute_tool_with_cache(tool_name, args, trace_id):
    cache_key = f"{trace_id}:{tool_name}:{json.dumps(args, sort_keys=True)}"
    if cache_key in tool_cache:
        return tool_cache[cache_key]
    result = execute_tool(tool_name, args)
    tool_cache[cache_key] = result
    return result
```

Best practices for caching:
- Cache tool results that are idempotent and same args same result, e.g., get_order_status, get_policy, get_trust_score
- Don't cache non-idempotent tools: refund_order, request_approval (side effect)
- Cache LLM calls with same prompt, model, temperature, for deterministic T=0.0 calls
- Use Redis for distributed cache across agent instances
- TTL: Tool results cache 5 min, LLM calls cache 1 hour
- Benchmark: Cache hit 50% saves 50% cost and latency for repeated tasks

**Model cascades:**

Model cascades = Use small model for simple tasks, large model for complex, cuts cost and latency.

Example:
```
# Small model gpt-4o-mini for simple tasks: get_order_status, get_policy, get_trust_score, refund_order with T=0.0
# Large model gpt-4o for complex tasks: reasoning, reflection, planning, writing with T=0.7

def model_cascade(task):
    if task in ["get_order_status", "get_policy", "get_trust_score", "refund_order"]:
        # Simple tool calling, use small model gpt-4o-mini T=0.0 cost $0.005 per call
        model = "gpt-4o-mini"
        temperature = 0.0
    else:
        # Complex reasoning, reflection, writing, use large model gpt-4o T=0.7 cost $0.05 per call
        model = "gpt-4o"
        temperature = 0.7
    
    response = openai.chat.completions.create(
        model=model,
        messages=history,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature
    )
    return response

# Benchmark model cascades
# All tasks with large model gpt-4o: Cost $0.05 per call * 4 calls = $0.20 for refund $120 task
# Cascade: 3 simple tasks with small model gpt-4o-mini $0.005*3=$0.015 + 1 complex task with large model $0.05 = $0.065 total = 67% cost cut vs all large model $0.20
# Latency: Small model faster 0.3s vs large model 0.5s, latency cut 20%
```

Best practices for model cascades:
- Use small model for simple deterministic tasks: tool calling T=0.0, get_order_status, get_policy, get_trust_score
- Use large model for complex creative tasks: reasoning, reflection, planning, writing T=0.7
- Heuristics: If task contains tool call, use small model, else if task is reasoning or writing, use large model
- For production, use router model to decide small vs large model based on task complexity
- Benchmark: 67% cost cut, 20% latency cut with cascade vs all large model

**Overall latency optimization benchmarks:**

| Technique | Latency (3 tools) | Cost | Success | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| No optimization (sequential) | 3s (3 LLM calls 0.5s each + 3 tool executions 0.5s each) | 3 calls cost 3x | 70% | Default |
| Streaming final answer | Perceived latency 0.5s first token vs 2s full answer, actual 3s same, improves UX | Same | Same | Always stream final answer tool_choice none T=0.7 friendly |
| Parallel independent tools | 1.5s (1 LLM call + 3 parallel executions) vs 3s =50% cut | 1 call vs 3 calls =66% cost cut | 80% independent 60% dependent | Tools independent get_order + get_policy + get_trust with user_id known |
| Speculation 80% correct | 0.56s avg per step vs 0.8s =30% cut | Wasted 20% speculative executions | Same | Next tool predictable high probability 80%+ refund always needs get_order_status first |
| Caching 50% hit | 1.5s vs 3s =50% cut for repeated tasks | 50% cost cut for repeated | Same | Idempotent tool results get_order_status get_policy get_trust_score, deterministic LLM calls T=0.0 |
| Model cascades small for simple large for complex | 2.4s vs 3s =20% cut (small model faster 0.3s vs large 0.5s) | 67% cost cut $0.065 vs $0.20 all large | Same | Simple tool calling small model gpt-4o-mini T=0.0, complex reasoning large model gpt-4o T=0.7 |
| Combined: Streaming + Parallel + Caching + Cascades | 1.0s perceived 0.5s first token, actual 1.5s vs 3s =50% cut, UX improved | 70% cost cut $0.06 vs $0.20 | 80% | Production always use all |

### 5. Cost Tracking & Budgeting - Per-Agent, Per-Task, Per-Tool Cost

**What is cost tracking & budgeting:**

Cost tracking = Track cost per-agent per-task per-tool, with fields agent_id, task, tool_name, llm_model, input_tokens, output_tokens, cost, timestamp, in ClickHouse for analytics.

Budgeting = Set budget per-agent per-task per-user per-day, e.g., $100 per day per user, circuit breaker if cost > budget, prevents $1000 runaway if agent loops.

**Cost calculation:**

```
def calculate_cost(input_tokens, output_tokens, model):
    # OpenAI pricing per 1M tokens
    # gpt-4o-mini: $0.15 input, $0.60 output
    # gpt-4o: $2.50 input, $10 output
    pricing = {
        "gpt-4o-mini": {"input": 0.15/1_000_000, "output": 0.60/1_000_000},
        "gpt-4o": {"input": 2.50/1_000_000, "output": 10/1_000_000}
    }
    
    input_cost = input_tokens * pricing[model]["input"]
    output_cost = output_tokens * pricing[model]["output"]
    total_cost = input_cost + output_cost
    return total_cost

# Example: gpt-4o-mini input 100 tokens output 50 tokens cost 100*0.15/1M + 50*0.60/1M = $0.000015 + $0.00003 = $0.000045
# For refund $120 task with 4 LLM calls: 4 * $0.000045 = $0.00018, negligible
# But with loops 1000 times: 1000 * $0.000045 = $0.045, still low, but with large model gpt-4o $0.0025 per call *1000 = $2.5, runaway if loops 10000 times $25
```

**Cost tracking per-agent per-task per-tool:**

Logging to ClickHouse with cost per step:
```
CREATE TABLE agent_costs (
    timestamp DateTime,
    trace_id String,
    agent_id String,
    user_id String,
    task String,
    tool_name String,
    llm_model String,
    input_tokens UInt32,
    output_tokens UInt32,
    cost Float32
) ENGINE = MergeTree()
ORDER BY (timestamp, agent_id, user_id)

# Log cost per step
def log_cost(trace_id, agent_id, user_id, task, tool_name, llm_model, input_tokens, output_tokens, cost):
    client.insert('agent_costs', [[
        datetime.now(),
        trace_id,
        agent_id,
        user_id,
        task,
        tool_name,
        llm_model,
        input_tokens,
        output_tokens,
        cost
    ]], column_names=['timestamp', 'trace_id', 'agent_id', 'user_id', 'task', 'tool_name', 'llm_model', 'input_tokens', 'output_tokens', 'cost'])

# Usage in agent loop
for step in range(max_steps):
    response = openai.chat.completions.create(...)
    cost = calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens, model)
    log_cost(trace_id, agent_id, user_id, task, tool_name, model, response.usage.prompt_tokens, response.usage.completion_tokens, cost)
```

Analytics queries:
```
-- Cost per agent
SELECT agent_id, sum(cost) as total_cost FROM agent_costs GROUP BY agent_id ORDER BY total_cost DESC

-- Cost per task
SELECT task, sum(cost) as total_cost, avg(cost) as avg_cost, count(*) as calls FROM agent_costs GROUP BY task ORDER BY total_cost DESC

-- Cost per tool
SELECT tool_name, sum(cost) as total_cost, avg(cost) as avg_cost, count(*) as calls FROM agent_costs WHERE tool_name IS NOT NULL GROUP BY tool_name ORDER BY total_cost DESC

-- Cost per user per day
SELECT user_id, toDate(timestamp) as day, sum(cost) as daily_cost FROM agent_costs GROUP BY user_id, day ORDER BY daily_cost DESC

-- Cost per model
SELECT llm_model, sum(cost) as total_cost FROM agent_costs GROUP BY llm_model ORDER BY total_cost DESC
```

**Budgeting & Circuit Breaker:**

Budgeting = Set budget per-agent per-task per-user per-day, e.g., $100 per day per user, circuit breaker if cost > budget, prevents $1000 runaway.

Implementation:
```
# Budget config
budgets = {
    "per_user_per_day": 100, # $100 per user per day
    "per_agent_per_day": 1000, # $1000 per agent per day
    "per_task": 1, # $1 per task max
    "per_tool": 0.1 # $0.1 per tool call max
}

def check_budget(user_id, agent_id, task, tool_name, cost):
    # Check per-user per-day budget
    daily_cost_user = get_daily_cost_user(user_id) # SELECT sum(cost) FROM agent_costs WHERE user_id={user_id} AND toDate(timestamp)=today()
    if daily_cost_user + cost > budgets["per_user_per_day"]:
        raise BudgetExceededError(f"User {user_id} daily budget ${budgets['per_user_per_day']} exceeded, daily cost ${daily_cost_user}, new cost ${cost}")
    
    # Check per-agent per-day budget
    daily_cost_agent = get_daily_cost_agent(agent_id)
    if daily_cost_agent + cost > budgets["per_agent_per_day"]:
        raise BudgetExceededError(f"Agent {agent_id} daily budget ${budgets['per_agent_per_day']} exceeded")
    
    # Check per-task budget
    task_cost = get_task_cost(task)
    if task_cost + cost > budgets["per_task"]:
        raise BudgetExceededError(f"Task {task} budget ${budgets['per_task']} exceeded")
    
    # Check per-tool budget
    tool_cost = get_tool_cost(tool_name)
    if tool_cost + cost > budgets["per_tool"]:
        raise BudgetExceededError(f"Tool {tool_name} budget ${budgets['per_tool']} exceeded")

def get_daily_cost_user(user_id):
    # Query ClickHouse
    result = client.query(f"SELECT sum(cost) as daily_cost FROM agent_costs WHERE user_id='{user_id}' AND toDate(timestamp)=today()")
    return result.result_rows[0][0] or 0

# Usage in agent loop with circuit breaker
for step in range(max_steps):
    response = openai.chat.completions.create(...)
    cost = calculate_cost(response.usage.prompt_tokens, response.usage.completion_tokens, model)
    
    try:
        check_budget(user_id, agent_id, task, tool_name, cost)
    except BudgetExceededError as e:
        # Circuit breaker: Stop agent execution, return error
        log_agent_step(..., error_code="BUDGET_EXCEEDED", success=False)
        raise e
    
    log_cost(trace_id, agent_id, user_id, task, tool_name, model, response.usage.prompt_tokens, response.usage.completion_tokens, cost)
    
    # Continue...
```

**Best practices for cost tracking & budgeting:**

- Track cost per-agent per-task per-tool per-user per-day in ClickHouse
- Set budgets per-user per-day $100, per-agent per-day $1000, per-task $1, per-tool $0.1, adjust based on use case
- Circuit breaker if cost > budget, stop execution, return error, alert
- Alert if cost > 80% budget, warning
- Use model cascades small for simple large for complex to cut cost 67%
- Use caching to cut cost 50% for repeated tasks
- Sample logs 10% for success low-cost to save logging cost
- Retention ClickHouse 90 days for cost analytics

**Cost of cost tracking:**

- ClickHouse storage for agent_costs table: 1M rows ~100MB, cost $0.01/month negligible
- Overhead: 1% latency for cost calculation and logging, negligible
- Savings: Budgeting prevents $1000 runaway, worth it

**Benchmark cost tracking:**

- Without tracking and budgeting: Agent loops 1000 times with gpt-4o $2.5 per call *1000 = $2500 runaway cost, no alert
- With tracking and budgeting per-user per-day $100: Circuit breaker after $100 cost, stops execution, alert, prevents $2500 runaway, saves $2400
- Cost of tracking: $0.01/month ClickHouse storage, negligible vs savings $2400

### 6. Complete Implementation Blueprint

**Full production agent with tracing, logging, monitoring, latency optimization, cost tracking, budgeting:**

```
import openai, json, asyncio, time, datetime
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import clickhouse_connect
from prometheus_client import Counter, Histogram, start_http_server

# Setup OpenTelemetry tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Setup ClickHouse logging
client = clickhouse_connect.get_client(host='localhost', port=8123)

# Setup Prometheus metrics
start_http_server(8000)
agent_requests_total = Counter('agent_requests_total', 'Total agent requests', ['agent_id', 'task', 'success'])
agent_latency_seconds = Histogram('agent_latency_seconds', 'Agent latency', ['agent_id', 'task'])
agent_cost_dollars = Histogram('agent_cost_dollars', 'Agent cost', ['agent_id', 'task'])
agent_tool_calls_total = Counter('agent_tool_calls_total', 'Total tool calls', ['agent_id', 'tool_name', 'error_code'])
agent_loops_total = Counter('agent_loops_total', 'Total loops detected', ['agent_id'])
agent_errors_total = Counter('agent_errors_total', 'Total errors', ['agent_id', 'error_code'])

# Tools definition with strict True
tools = [...] # Same as previous modules

# Budgets
budgets = {
    "per_user_per_day": 100,
    "per_agent_per_day": 1000,
    "per_task": 1,
    "per_tool": 0.1
}

def calculate_cost(input_tokens, output_tokens, model):
    pricing = {
        "gpt-4o-mini": {"input": 0.15/1_000_000, "output": 0.60/1_000_000},
        "gpt-4o": {"input": 2.50/1_000_000, "output": 10/1_000_000}
    }
    return input_tokens * pricing[model]["input"] + output_tokens * pricing[model]["output"]

def get_daily_cost_user(user_id):
    result = client.query(f"SELECT sum(cost) as daily_cost FROM agent_costs WHERE user_id='{user_id}' AND toDate(timestamp)=today()")
    return result.result_rows[0][0] or 0

def check_budget(user_id, agent_id, task, tool_name, cost):
    daily_cost_user = get_daily_cost_user(user_id)
    if daily_cost_user + cost > budgets["per_user_per_day"]:
        raise Exception(f"BudgetExceeded: User {user_id} daily budget ${budgets['per_user_per_day']} exceeded")

def log_agent_step(...): # Same as earlier
    client.insert('agent_logs', [[...]], column_names=[...])

def log_cost(...): # Same as earlier
    client.insert('agent_costs', [[...]], column_names=[...])

def detect_loop(history, window=3): # Same as earlier
    tool_calls_history = [msg for msg in history if msg.get("role") == "assistant" and msg.get("tool_calls")]
    if len(tool_calls_history) < window: return False
    last = tool_calls_history[-window:]
    first = last[0]["tool_calls"][0]["function"]
    for call in last[1:]:
        if call["tool_calls"][0]["function"]["name"] != first["name"] or call["tool_calls"][0]["function"]["arguments"] != first["arguments"]:
            return False
    return True

async def execute_tool(name, args):
    # Same as previous with retry
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if name == "refund_order":
                result = {"refund_id": "ref_123", "status": "success", "amount": args["amount"]}
                return result
            # ... other tools
        except Exception as e:
            if "RATE_LIMIT" in str(e) or "NETWORK" in str(e):
                await asyncio.sleep(2 ** attempt)
                continue
            else:
                return {"error": str(e), "code": "EXECUTION_ERROR"}
    return {"error": "Max retries exceeded", "code": "MAX_RETRIES"}

async def production_agent_with_observability(user_goal, agent_id, user_id, session_id, trace_id):
    history = [{"role": "user", "content": user_goal}]
    start_time = time.time()
    
    with tracer.start_as_current_span("agent_execution") as root_span:
        root_span.set_attribute("agent.id", agent_id)
        root_span.set_attribute("user.id", user_id)
        root_span.set_attribute("session.id", session_id)
        root_span.set_attribute("task", user_goal)
        
        for step in range(10): # max steps
            # Check loop
            if detect_loop(history):
                with tracer.start_as_current_span("loop_detected") as span:
                    span.set_attribute("loop.detected", True)
                    span.set_attribute("loop.step", step)
                agent_loops_total.labels(agent_id=agent_id).inc()
                log_agent_step(trace_id, agent_id, user_id, session_id, user_goal, step, None, None, None, None, None, None, None, None, None, None, None, None, None, None, False, True, None, "LOOP_DETECTED")
                
                # Reflection T=0.7 to break loop
                with tracer.start_as_current_span("reflection") as span:
                    span.set_attribute("reflection.temperature", 0.7)
                    reflection_response = openai.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=history + [{"role": "user", "content": "Stuck repeating same action, reflect why and try different approach"}],
                        tools=tools,
                        tool_choice="none",
                        temperature=0.7
                    )
                    span.set_attribute("reflection.output", reflection_response.choices[0].message.content)
                history.append({"role": "assistant", "content": reflection_response.choices[0].message.content})
                continue
            
            # LLM call with tracing
            with tracer.start_as_current_span("llm_call") as span:
                tool_choice = "none" if step==9 or is_done(history) else "auto"
                temperature = 0.0 if tool_choice!="none" else 0.7
                model = "gpt-4o-mini" if tool_choice!="none" else "gpt-4o" # Cascade small for tool calling, large for final answer
                
                span.set_attribute("llm.model", model)
                span.set_attribute("llm.temperature", temperature)
                span.set_attribute("llm.tool_choice", tool_choice)
                
                llm_start = time.time()
                response = openai.chat.completions.create(
                    model=model,
                    messages=history,
                    tools=tools,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    top_p=1.0 if temperature==0.0 else 0.9
                )
                llm_latency = time.time() - llm_start
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                cost = calculate_cost(input_tokens, output_tokens, model)
                
                span.set_attribute("llm.input_tokens", input_tokens)
                span.set_attribute("llm.output_tokens", output_tokens)
                span.set_attribute("llm.cost", cost)
                span.set_attribute("llm.latency", llm_latency)
                span.set_attribute("llm.output", response.choices[0].message.content[:1000] if response.choices[0].message.content else "")
                
                # Check budget
                try:
                    check_budget(user_id, agent_id, user_goal, None, cost)
                except Exception as e:
                    span.set_attribute("error", str(e))
                    span.set_attribute("error_code", "BUDGET_EXCEEDED")
                    log_agent_step(trace_id, agent_id, user_id, session_id, user_goal, step, model, temperature, tool_choice, input_tokens, output_tokens, cost, llm_latency, None, None, None, None, None, None, False, False, None, "BUDGET_EXCEEDED")
                    agent_errors_total.labels(agent_id=agent_id, error_code="BUDGET_EXCEEDED").inc()
                    raise e
                
                # Log
                log_agent_step(trace_id, agent_id, user_id, session_id, user_goal, step, model, temperature, tool_choice, input_tokens, output_tokens, cost, llm_latency, None, None, None, None, None, None, False, False, None, "none")
                log_cost(trace_id, agent_id, user_id, user_goal, None, model, input_tokens, output_tokens, cost)
                agent_cost_dollars.labels(agent_id=agent_id, task=user_goal).observe(cost)
                
                assistant_msg = response.choices[0].message
                
                if not assistant_msg.tool_calls:
                    # Final answer, streaming
                    history.append({"role": "assistant", "content": assistant_msg.content})
                    # Stream final answer
                    # For demo, print tokens
                    # In production, yield via SSE
                    # for token in assistant_msg.content.split():
                    #     yield token
                    break
                
                history.append({
                    "role": "assistant",
                    "content": assistant_msg.content,
                    "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_msg.tool_calls]
                })
            
            # Tool calls with tracing, parallel if independent
            tool_calls = assistant_msg.tool_calls
            # Group independent for parallel (simplified)
            # For demo, all parallel
            with tracer.start_as_current_span("tool_calls") as span:
                span.set_attribute("tool.calls_count", len(tool_calls))
                
                tasks = []
                for tc in tool_calls:
                    args = json.loads(tc.function.arguments)
                    tasks.append((tc, args))
                
                # Execute parallel
                results = await asyncio.gather(*[execute_tool(tc.function.name, args) for tc, args in tasks])
                
                for (tc, args), result in zip(tasks, results):
                    with tracer.start_as_current_span("tool_call") as tool_span:
                        tool_span.set_attribute("tool.name", tc.function.name)
                        tool_span.set_attribute("tool.args", json.dumps(args))
                        tool_span.set_attribute("tool.result", json.dumps(result)[:1000])
                        tool_span.set_attribute("tool.error_code", result.get("code", "none"))
                        
                        tool_start = time.time()
                        # Already executed, latency measured earlier
                        tool_latency = 0.3 # Example
                        tool_cost = 0
                        
                        tool_span.set_attribute("tool.latency", tool_latency)
                        tool_span.set_attribute("tool.cost", tool_cost)
                        
                        history.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
                        
                        log_agent_step(trace_id, agent_id, user_id, session_id, user_goal, step, None, None, None, None, None, None, None, tool_calls[0].function.name, args, result, result.get("code", "none"), tool_latency, tool_cost, "error" not in result, False, None, result.get("code", "none"))
                        log_cost(trace_id, agent_id, user_id, user_goal, tc.function.name, None, 0, 0, tool_cost)
                        agent_tool_calls_total.labels(agent_id=agent_id, tool_name=tc.function.name, error_code=result.get("code", "none")).inc()
                        
                        if "error" in result:
                            agent_errors_total.labels(agent_id=agent_id, error_code=result.get("code", "UNKNOWN")).inc()
        
        total_latency = time.time() - start_time
        total_cost = sum([log["llm_cost"] or 0 + log["tool_cost"] or 0 for log in agent_logs]) # Simplified
        
        root_span.set_attribute("agent.total_latency", total_latency)
        root_span.set_attribute("agent.total_cost", total_cost)
        root_span.set_attribute("agent.success", is_success(history))
        
        agent_requests_total.labels(agent_id=agent_id, task=user_goal, success=str(is_success(history))).inc()
        agent_latency_seconds.labels(agent_id=agent_id, task=user_goal).observe(total_latency)
        
        final_answer = history[-1]["content"] if history[-1]["role"] == "assistant" else "Done"
        return final_answer

# Usage
# answer = asyncio.run(production_agent_with_observability("Refund ORD-12345 $120", agent_id="agent_123", user_id="user_123", session_id="sess_123", trace_id="trace_123"))
```

### 7. Failure Modes: Loops, Cost Blowups, Policy Violations

**Failure 1: Loop - Agent repeats same action**

Without observability:
- Agent loops get_order_status -> trust 70 -> refund_order fails TRUST_LOW -> get_order_status -> trust 70 -> refund_order fails -> ... 10 times
- Cost $0.10, latency 10s, no refund, user frustrated
- Without tracing, you see final Failed but not why loop

With observability:
- Tracing: Span loop_detected True step 3, 4, 5 same action refund_order same args, reflection T=0.7 breaks loop
- Logging: SELECT agent_id, count(*) as loops WHERE loop_detected=1 GROUP BY agent_id -> agent_123 loop rate 10%
- Alert if loop rate >5%
- Fix: Detect loop last 3 identical actions -> reflection T=0.7 creative alternative -> request_approval instead of refund_order -> success
- Monitoring: Prometheus agent_loops_total counter, Grafana dashboard loop rate panel, alert if loop rate >5%

**Failure 2: Cost blowup - Agent loops 1000 times**

Without cost tracking and budgeting:
- Agent loops 1000 times with gpt-4o $2.5 per call *1000 = $2500 runaway cost, no alert, no circuit breaker
- User billed $2500

With cost tracking and budgeting:
- Cost tracking: Log cost per step to ClickHouse agent_costs table
- Budgeting: Set budget per-user per-day $100, check budget before each LLM call, circuit breaker if cost > budget
- Daily cost user: SELECT sum(cost) FROM agent_costs WHERE user_id=user_123 AND toDate(timestamp)=today() -> $90
- Next call cost $20 -> daily cost $110 > budget $100 -> BudgetExceededError, stop execution, alert, prevent $2500 runaway, save $2400
- Monitoring: Prometheus agent_cost_dollars histogram, Grafana dashboard cost per user per day panel, alert if cost >80% budget

**Failure 3: Policy violation - Agent refunds $600 without approval**

Without tracing and logging:
- Agent refunds $600 without approval, policy says <500 auto, >500 need approval, violation
- Without tracing, you see final Refund $600 processed but not why policy violation, which policy version, trust score

With tracing and logging:
- Tracing: Span tool call refund_order args order_id ORD-12345 amount 600, policy max_auto 500, trust 85, amount 600>500 should need approval but refunded, error_code POLICY_VIOLATION
- Logging: SELECT * FROM agent_logs WHERE tool_name=refund_order AND tool_args LIKE '%600%' AND error_code=POLICY_VIOLATION
- Alert if policy violation rate >1%
- Fix: Behavior Tree for policy enforcement deterministic 99% valid, check amount<500 and trust>80 before refund, if amount>500 or trust<80 use request_approval, not refund_order
- Monitoring: Prometheus agent_errors_total with error_code POLICY_VIOLATION, Grafana dashboard error rate per error_code panel, alert if policy violation >1%

**Failure 4: Latency SLA violation - Agent takes 10s**

Without latency optimization and monitoring:
- Agent takes 10s sequential 3 tool calls 3s each + LLM calls, user waits 10s, poor UX, SLA 5s violated

With latency optimization and monitoring:
- Optimization: Streaming final answer perceived latency 0.5s first token vs 2s full answer, parallel independent tools 1.5s vs 3s 50% cut, caching 50% hit 1.5s vs 3s 50% cut, model cascades small for simple large for complex 2.4s vs 3s 20% cut, combined 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut
- Monitoring: Prometheus agent_latency_seconds histogram, Grafana dashboard latency p95 per agent panel, alert if p95 latency > SLA 5s
- Tracing: Span latency per LLM call and tool call, see which step slow, e.g., get_order_status latency 2s slow DB query, fix DB index
- Fix: Optimize slow tool, use caching, parallel, streaming, model cascades

### 8. Benchmarks

| Technique | Latency (3 tools) | Cost | Success | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| No observability, no optimization (sequential) | 3s (3 LLM calls 0.5s each + 3 tool executions 0.5s each) | 3 calls cost 3x $0.20 all large model | 70% | Default without observability, fails loop cost blowup policy violation not debuggable |
| Tracing OpenTelemetry + LangSmith | Same latency +1-5% overhead, but debuggable why loop, which tool failed, which policy violated | Same cost + tracing cost free self-hosted or $39/month LangSmith | Same success but debuggable, loop rate visible, cost per tool visible | Always trace every LLM call and tool call, 1-5% overhead worth it |
| Logging ClickHouse | Same latency +1% overhead for logging | Same cost + ClickHouse storage $0.01/month negligible | Same success but analytics per-agent per-task per-tool, alert if loop rate >5% cost > budget | Always log to ClickHouse, 1% overhead worth it |
| Monitoring Prometheus + Grafana | Same latency +1% overhead for metrics | Same cost + Prometheus storage 1GB 15 days negligible + Grafana free self-hosted or $8/month | Same success but dashboards success rate, loop rate, cost, latency p95, error rate, alert if SLA violated | Always monitor with Prometheus metrics and Grafana dashboards, 1% overhead worth it |
| Streaming final answer | Perceived latency 0.5s first token vs 2s full answer, actual 3s same, improves UX | Same cost | Same success | Always stream final answer tool_choice none T=0.7 friendly, perceived latency 0.5s vs 2s |
| Parallel independent tools | 1.5s vs 3s =50% cut | 1 call vs 3 calls =66% cost cut $0.065 vs $0.20 | 80% independent 60% dependent | Tools independent get_order + get_policy + get_trust with user_id known |
| Speculation 80% correct | 0.56s avg per step vs 0.8s =30% cut | Wasted 20% speculative executions cost negligible if tool cost free | Same | Next tool predictable high probability 80%+ refund always needs get_order_status first |
| Caching 50% hit | 1.5s vs 3s =50% cut for repeated tasks | 50% cost cut for repeated | Same | Idempotent tool results get_order_status get_policy get_trust_score, deterministic LLM calls T=0.0 |
| Model cascades small for simple large for complex | 2.4s vs 3s =20% cut (small model faster 0.3s vs large 0.5s) | 67% cost cut $0.065 vs $0.20 all large | Same | Simple tool calling small model gpt-4o-mini T=0.0, complex reasoning large model gpt-4o T=0.7 |
| Cost tracking & budgeting per-user per-day $100 | Same latency +1% overhead for cost calc and check | Same cost + ClickHouse storage $0.01/month negligible, but prevents $2500 runaway saves $2400 | Same success but prevents cost blowup | Always track cost per-agent per-task per-tool per-user per-day, set budgets, circuit breaker if cost > budget |
| Combined: Tracing + Logging + Monitoring + Streaming + Parallel + Caching + Cascades + Cost tracking & budgeting | 1.0s perceived 0.5s first token, actual 1.5s vs 3s =50% cut, UX improved, debuggable, analytics, dashboards, cost blowup prevented | 70% cost cut $0.06 vs $0.20 all large, plus prevents $2500 runaway saves $2400 | 80% with parallel independent, 90% with Reflexion reflection self-correction | Production always use all: Trace every call, log to ClickHouse, monitor Prometheus Grafana, stream final answer, parallel independent tools, cache idempotent, cascade small large, track cost per-agent per-task per-tool per-user per-day, budget per-user per-day $100 circuit breaker |

### 9. Production Checklist

1. **Tracing with OpenTelemetry, LangSmith, Langfuse** — Trace every LLM call and tool call with span, attributes latency, cost, tokens, tool args, error_code, model, temperature, tool_choice, trace_id, agent_id, user_id, session_id, task. Use OpenTelemetry standard for interoperability with Jaeger, Honeycomb, LangSmith, Langfuse. Use LangSmith or Langfuse for agent-specific tracing with UI, analytics, evaluation. Sample traces 100% for errors, loops, high-cost, 10% for success low-cost. Overhead 1-5% latency, cost free self-hosted or $39/month LangSmith, worth it for debugging loops, cost blowups, policy violations.

2. **Logging to ClickHouse** — Log every LLM call and tool call with fields timestamp, trace_id, agent_id, user_id, session_id, task, step, llm_model, llm_temperature, llm_tool_choice, llm_input_tokens, llm_output_tokens, llm_cost, llm_latency, tool_name, tool_args, tool_result, tool_error_code, tool_latency, tool_cost, success, loop_detected, reflection_lesson, error_code, in ClickHouse MergeTree ORDER BY timestamp agent_id trace_id. Analytics queries: success rate per agent, loop rate per agent, cost per agent, cost per tool, error rate per error_code, latency p95 per agent, reflection lessons. Retention 90 days. Overhead 1% latency, cost $0.01/month for 1M logs negligible.

3. **Monitoring with Prometheus and Grafana** — Prometheus metrics: agent_requests_total Counter with labels agent_id task success, agent_latency_seconds Histogram with labels agent_id task, agent_cost_dollars Histogram with labels agent_id task, agent_tool_calls_total Counter with labels agent_id tool_name error_code, agent_loops_total Counter with labels agent_id, agent_errors_total Counter with labels agent_id error_code. Grafana dashboards: success rate per agent rate(agent_requests_total{success="True"}[5m])/rate(agent_requests_total[5m]), loop rate per agent rate(agent_loops_total[5m]), cost per agent sum(agent_cost_dollars) by (agent_id), latency p95 per agent histogram_quantile(0.95, rate(agent_latency_seconds_bucket[5m])), error rate per error_code rate(agent_errors_total[5m]) by (error_code), tool calls per tool rate(agent_tool_calls_total[5m]) by (tool_name). Alert if success rate <80% or loop rate >5% or cost > budget $100 or latency p95 > SLA 5s or error rate >10% or policy violation >1%. Overhead 1% latency, cost Prometheus self-hosted free storage 1GB 15 days negligible, Grafana self-hosted free or $8/month cloud.

4. **Latency optimization: Streaming, Parallel, Speculation, Caching, Model Cascades** — Streaming final answer tool_choice none T=0.7 friendly via SSE or WebSocket token by token, perceived latency 0.5s first token vs 2s full answer, actual same, improves UX, overhead 5% latency for chunking. Parallel independent tools via asyncio.gather, detect independent vs dependent via dependency graph, topological sort, group independent parallel, limit 3-5 parallel per turn, handle partial failures, 50% latency cut 1.5s vs 3s for 3 independent tools, 66% cost cut 1 call vs 3 calls. Speculation speculatively execute predicted next tool before LLM confirms, prediction heuristics or small model, background parallel with LLM call, save latency if correct 80% correct 30% latency cut 0.56s avg per step vs 0.8s, waste cost 20% if wrong negligible if tool cost free. Caching cache idempotent tool results get_order_status get_policy get_trust_score and deterministic LLM calls T=0.0, LRU cache or Redis distributed, TTL tool results 5 min LLM calls 1 hour, 50% hit saves 50% cost and latency for repeated tasks. Model cascades small model gpt-4o-mini T=0.0 for simple tool calling, large model gpt-4o T=0.7 for complex reasoning reflection planning writing, heuristics tool call small model else large model or router model, 67% cost cut $0.065 vs $0.20 all large, 20% latency cut 2.4s vs 3s. Combined streaming + parallel + caching + cascades 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut, 70% cost cut $0.06 vs $0.20.

5. **Cost tracking & budgeting per-agent per-task per-tool per-user per-day** — Track cost per step in ClickHouse agent_costs table fields timestamp trace_id agent_id user_id task tool_name llm_model input_tokens output_tokens cost. Analytics queries cost per agent, per task, per tool, per user per day, per model. Calculate cost from input_tokens output_tokens model pricing gpt-4o-mini $0.15 input $0.60 output per 1M, gpt-4o $2.50 input $10 output per 1M. Budgeting set budgets per-user per-day $100, per-agent per-day $1000, per-task $1, per-tool $0.1, adjust based on use case, check budget before each LLM call and tool call, circuit breaker if cost > budget stop execution return error alert, prevents $1000 runaway e.g., loops 1000 times gpt-4o $2.5 per call *1000=$2500 runaway, with budgeting per-user per-day $100 circuit breaker after $100 cost stops execution saves $2400. Alert if cost >80% budget warning. Overhead 1% latency for cost calc and check, cost ClickHouse storage $0.01/month negligible, savings $2400 worth it.

6. **Failure modes: Loops, Cost blowups, Policy violations, Latency SLA violations** — Loop: Agent repeats same action, without observability final Failed not why loop, with tracing span loop_detected True step, logging loop rate per agent, monitoring agent_loops_total counter Grafana dashboard loop rate panel alert if loop rate >5%, fix detect loop last 3 identical actions -> reflection T=0.7 creative alternative -> request_approval instead of refund_order -> success. Cost blowup: Agent loops 1000 times $2500 runaway, without tracking no alert, with tracking cost per step to ClickHouse, budgeting per-user per-day $100 circuit breaker after $100 stops execution saves $2400, monitoring cost per user per day dashboard alert if cost >80% budget. Policy violation: Agent refunds $600 without approval policy says <500 auto >500 need approval, without tracing final Refund $600 processed not why violation, with tracing span tool call refund_order args amount 600 policy max_auto 500 error_code POLICY_VIOLATION, logging SELECT WHERE tool_name refund_order AND amount 600 AND error_code POLICY_VIOLATION, monitoring agent_errors_total error_code POLICY_VIOLATION dashboard error rate per error_code alert if policy violation >1%, fix Behavior Tree for policy enforcement deterministic 99% valid check amount<500 and trust>80 before refund if amount>500 or trust<80 use request_approval. Latency SLA violation: Agent takes 10s sequential, without optimization poor UX SLA 5s violated, with optimization streaming perceived 0.5s first token, parallel 1.5s vs 3s 50% cut, caching 50% hit 1.5s vs 3s, cascades 2.4s vs 3s 20% cut, combined 1.0s perceived actual 1.5s vs 3s 50% cut, monitoring latency p95 per agent dashboard alert if p95 > SLA 5s, tracing span latency per step see which slow e.g., get_order_status 2s slow DB query fix DB index.

7. **Benchmarks** — No observability no optimization sequential 3s latency 3 calls cost 3x $0.20 all large 70% success fails loop cost blowup policy violation not debuggable. Tracing + logging + monitoring + streaming + parallel + caching + cascades + cost tracking & budgeting combined 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut UX improved debuggable analytics dashboards cost blowup prevented 70% cost cut $0.06 vs $0.20 plus prevents $2500 runaway saves $2400 80% with parallel independent 90% with Reflexion reflection self-correction. Production always use all: Trace every call, log to ClickHouse, monitor Prometheus Grafana, stream final answer, parallel independent tools, cache idempotent, cascade small large, track cost per-agent per-task per-tool per-user per-day, budget per-user per-day $100 circuit breaker.

8. **Implementation blueprint** — Full production agent with OpenTelemetry tracing BatchSpanProcessor OTLPSpanExporter to Jaeger Honeycomb LangSmith, ClickHouse logging agent_logs and agent_costs tables MergeTree, Prometheus metrics agent_requests_total Counter agent_latency_seconds Histogram agent_cost_dollars Histogram agent_tool_calls_total Counter agent_loops_total Counter agent_errors_total Counter start_http_server 8000, Grafana dashboard success rate loop rate cost latency p95 error rate tool calls, latency optimization streaming final answer via SSE WebSocket token by token, parallel independent tools via asyncio.gather topological sort group independent limit 3-5 parallel handle partial failures, speculation speculative execution predicted next tool background parallel with LLM call save latency if correct 80% correct 30% cut, caching LRU cache or Redis distributed TTL tool results 5 min LLM calls 1 hour 50% hit saves 50% cost latency, model cascades small gpt-4o-mini T=0.0 for simple tool calling large gpt-4o T=0.7 for complex reasoning reflection planning writing heuristics tool call small else large or router model 67% cost cut 20% latency cut, cost tracking calculate_cost from input_tokens output_tokens model pricing, log cost to ClickHouse agent_costs, budgeting check_budget per-user per-day $100 per-agent per-day $1000 per-task $1 per-tool $0.1 circuit breaker if cost > budget stop execution alert, failure handling loop detection last 3 identical actions -> reflection T=0.7 creative alternative, cost blowup budgeting circuit breaker, policy violation Behavior Tree deterministic policy enforcement, latency SLA violation streaming parallel caching cascades optimization monitoring alert.

---
**Bottom Line:** Agents are non-deterministic black boxes - without observability you cannot debug loops, cost blowups, policy violations. Tracing with OpenTelemetry + LangSmith/Langfuse gives full trajectory Thought->Action->Observation with latency, cost, tokens, tool args, error_code. Logging to ClickHouse gives per-agent per-task per-tool analytics success rate loop rate cost per agent per tool error rate latency p95 reflection lessons. Monitoring with Prometheus metrics agent_requests_total agent_latency_seconds agent_cost_dollars agent_tool_calls_total agent_loops_total agent_errors_total and Grafana dashboards success rate loop rate cost latency p95 error rate tool calls alert if SLA violated success <80% loop >5% cost > budget $100 latency p95 >5s error >10% policy violation >1%. Latency optimization streaming final answer perceived latency 0.5s first token vs 2s full answer actual same improves UX, parallel independent tools 1.5s vs 3s 50% cut 66% cost cut, speculation 80% correct 30% latency cut, caching 50% hit 50% cost and latency cut for repeated tasks, model cascades small for simple large for complex 67% cost cut 20% latency cut, combined streaming + parallel + caching + cascades 1.0s perceived 0.5s first token actual 1.5s vs 3s 50% cut 70% cost cut $0.06 vs $0.20. Cost tracking per-agent per-task per-tool per-user per-day in ClickHouse agent_costs table calculate cost from input_tokens output_tokens model pricing, budgeting per-user per-day $100 per-agent per-day $1000 per-task $1 per-tool $0.1 check budget before each call circuit breaker if cost > budget stop execution alert prevents $1000 runaway e.g., loops 1000 times gpt-4o $2.5 per call *1000=$2500 runaway with budgeting per-user per-day $100 circuit breaker after $100 saves $2400. Production always trace every LLM call and tool call, log to ClickHouse, monitor Prometheus Grafana, stream final answer, parallel independent tools, cache idempotent, cascade small large, track cost per-agent per-task per-tool per-user per-day, budget per-user per-day $100 circuit breaker, alert if cost > budget or latency > SLA.

