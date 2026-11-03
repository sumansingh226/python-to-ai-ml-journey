# Cost & Latency at Scale — Speculative Decoding, KV-Cache, Prompt Caching 90% Cut
## Full Production Guide 2026: How to Cut LLM Bills 80-90% and TTFT 40-85% + 2-3x Throughput Without Changing Model

> **Core Thesis:** In 2026 foundation model providers (Anthropic Claude, OpenAI, DeepSeek) and open-weight inference engines (vLLM, SGLang) leverage Key-Value cache state persistence to eliminate redundant compute. By caching compiled prompt prefixes in GPU memory or edge caches engineering teams achieve 50% to 90% cost reductions on input tokens alongside 40% to 85% drop in Time-to-First-Token latency. Top throughput lever? KV cache reuse with PagedAttention plus continuous batching (vLLM default since 2023 refined through 2026). Speculative decoding payoff? 1.5x to 3x throughput when draft model accepts ~70% proposed tokens. Prompt caching cuts input-token costs by 90% or more (OpenAI says cached input can cost up to 95% less than uncached, depending on model). Most developers still are not using it correctly as of Oct 26 2026. GPT-6 Astra, Claude Fable 5.1, Gemini 4 Argon each expose caching layer that can cut input-token costs 90%+ (OpenAI cached input 90% less than uncached, Anthropic cache read tokens billed at 0.1x base input rate 90% reduction while writing to cache costs 1.25x base and cache holds 5-min sliding window by default refreshed on hit). Notion cut its Claude API costs 90% and cut latency up to 85% after restructuring prompts around caching per Anthropic case study. KV cache memory grows with batch size and context length and is primary GPU memory bottleneck. That is the KV cache hit rate Inferoa AI measured during real agentic coding task: for every 100 tokens agent processed only 2.2 were computed from scratch rest were free. Full conversation history: 71.0% task completion 1,480,996 tokens consumed 14.56 hours per run. Pruning to last 5 tool call/response pairs: 79.0% completion 535,274 tokens — less context better agents arXiv 2606.10209. In agentic multi-turn: initial prompt 8000 tokens codebase context schema definitions tool instructions followed by dozens iterative tool calls — traditional engines every single tool turn re-evaluates entire 8000-token prefix from scratch saturating GPU memory bandwidth causing massive queue bottlenecks. SGLang RadixAttention organizes KV cache as radix tree when new request arrives that shares identical system prompt documentation block or previous turn history SGLang reuses existing KV tensor in memory with zero re-computation sub-50ms prefill latency reducing TTFT from 1200ms to under 45ms multi-turn conversations up to 5x higher throughput over standard serving. Three themes dominate June 2026 infrastructure: speculative decoding reaching production maturity, disaggregated serving architectures becoming mainstream, multi-tier KV cache management enabling dramatically higher throughput — DFlash speculative decoding on Blackwell achieving up to 15x inference speedups. This guide gives you full stack to get 90% cost cut.

### Table of Contents
1. Why Cost & Latency Explode in Agentic AI
2. The 4 Latency Components — TTFT, ITL, Prefill, Decode
3. Prompt Caching — 90% Bill Cut Provider-Side (Anthropic vs OpenAI 2026)
4. KV-Cache Deep Dive — PagedAttention, RadixAttention, Multi-Tier, Quantization
5. Speculative Decoding — Draft-Target 2-3x Throughput, 15x on Blackwell
6. Disaggregated Serving — Prefill/Decode Separation
7. SGLang vs vLLM vs TensorRT-LLM Benchmark Matrix
8. 90% Cost Cut Playbook — 10 Production Patterns
9. Node.js Production Implementation — Prompt Structure, Caching, Batching
10. Self-Hosted Stack — vLLM PagedAttention + SGLang RadixTree + LMCache
11. Observability — Track cached_tokens, KV Hit Rate, TTFT, ITL, Cost per Task
12. Database Schema — Cost Tracking Postgres + ClickHouse
13. Anti-Patterns That Kill Cache Hit Rate

---

### 1. Why Cost & Latency Explode in Agentic AI

**Agentic workload ≠ chat workload:**

Chat: 1 turn, 500 tokens prompt, 200 tokens output, done.

Agentic loop: 10-50 turns, each turn includes system prompt 2000 tokens + tool definitions 1000 tokens + conversation history growing 5000 tokens + tool outputs + new reasoning. Traditional inference engine every single tool turn re-evaluates entire 8000-token prefix from scratch saturating GPU memory bandwidth causing massive queue bottlenecks.

**Cost explosion example (without caching):**

Customer support chatbot GPT-5.4:

- 50,000 requests/day
- Average prompt: 1500 tokens (1400 stable system prompt + 100 user message)
- Average output: 200 tokens

Without caching: 50,000 × (1500 × $2.50 + 200 × $15)/1M = $337.50/day

With caching 90% input tokens hit cache after warm-up:

- Cached input: 50k × 1400 × 0.9 × $0.25 /1M = $15.75/day
- Uncached input: 50k × (1400×0.1+100)×$2.50/1M = $30/day
- Output: 50k×200×$15/1M = $150/day
- Total $195.75/day net saving ~42% total bill or ~85% input-token portion — workloads longer inputs bigger total savings

Real agentic coding task Inferoa AI measured: for every 100 tokens agent processed only 2.2 computed from scratch rest free — KV cache hit rate.

**ArXiv Less Context Better Agents 2606.10209 GPT-5 configs 50-task enterprise expense itemization benchmark:**

- Full conversation history: 71.0% task completion, 1,480,996 tokens consumed, 14.56 hours per run
- Pruning to last 5 tool call/response pairs: 79.0% completion, 535,274 tokens — less context better agents

**Implication:** KV cache memory grows with batch size and context length and is primary GPU memory bottleneck — need reuse + pruning + compression.

### 2. The 4 Latency Components — TTFT, ITL, Prefill, Decode

| Component | What | Target 2026 | Lever |
|---|---|---|---|
| TTFT Time-to-First-Token | Time from request to first output token — includes prefill encoding input | <500ms chat, sub-50ms with cache reuse | Prefix/KV caching 50-80% reduction |
| Prefill | Encoding input prompt into KV cache — compute-bound | 1200ms → 45ms with RadixTree reuse | PagedAttention, RadixAttention, FlashAttention |
| ITL Inter-Token Latency | Time between output tokens — decode phase memory-bound | <30ms | Speculative decoding 2-3x throughput |
| Total latency | End-to-end task with 20 tool calls | Hours → minutes with caching + parallel | Batching, disaggregated serving, compaction |

**Inference optimization matrix:**

| Technique | Optimizes | Gain | Effort |
|---|---|---|---|
| Prefix / KV Caching | TTFT | 50-80% reduction | Low prompt structuring |
| Speculative Decoding | ITL | 2-3x throughput (70% acceptance) up to 15x Blackwell DFlash | Medium vLLM/TensorRT-LLM config |
| Continuous Batching + PagedAttention | Throughput | 3-5x more concurrent streams per GPU | vLLM default since 2023 refined 2026 |
| RadixAttention | Multi-turn cache reuse | 3.8-5.2x baseline throughput agent loops sub-50ms prefill | SGLang |
| Prompt Caching (provider) | Cost + TTFT | 90% off input tokens + 40-85% TTFT drop | Low stable prefix first |

### 3. Prompt Caching — 90% Bill Cut Provider-Side (Anthropic vs OpenAI 2026)

**What it caches and why:** Like Anthropic's OpenAI prompt cache is provider-side prefix-attention caching. When request arrives with prompt prefix provider has seen recently OpenAI serves cached attention state rather than recomputing from scratch. Response still generated token-by-token; what gets discounted is input-token billing on cached portion.

Mechanism conceptually simple: model has to encode input prompt into internal representation before generating response. For long stable system prompts (often thousands tokens instructions retrieved context tool definitions) encoding step non-trivial compute. If same prefix shows repeatedly provider can reuse cached representation. OpenAI passes savings as 90% input-token discount on cached portion.

Catch opaque you can't directly inspect what's cached you can only observe effects via cached_tokens field returned in response usage block provider decides what to cache and for how long you control whether prompts are cacheable by keeping prefix stable.

**Pricing math mid-2026 snapshot per million tokens current as Aug 2026:**

| Token category | Price multiplier vs base input | Notes |
|---|---|---|
| Normal input uncached | 1.0x | Standard |
| Cached input | 0.1x | 90% discount applies automatically prompts ≥1024 tokens (OpenAI) or with cache_control marker (Anthropic) |
| Output | normal output pricing | Unchanged |
| Cache write Anthropic | 1.25x (5-min TTL) / 2x (1-hr TTL) | Write premium |
| Cache write OpenAI | No write premium | First request pays normal input subsequent hits 0.1x break-even immediate every cache hit pure saving |

Concretely:

- GPT-5.5: $5.00/M input → $0.50/M cached saving $4.50/M every cached token
- GPT-5.4: $2.50/M → $0.25/M cached
- GPT-5.4 Mini: $0.75/M → $0.075/M cached
- Claude Fable 5.1: explicit cache_control 2048-4096 min, 90% off 0.1x, 1.25x 5-min / 2x 1-hr TTL 5 minutes refreshed on hit
- Both Anthropic and OpenAI newest flagships now bill cached reads at 10% standard input rate 90% discount started as Anthropic signature got matched quietly when GPT-5.4 launched — GPT-5.4 and GPT-5.5 dropped cached input to $0.50/M against $5/M standard that is 90% matching Anthropic read rate

**Provider differences mid-2026 snapshot:**

| Feature | OpenAI (GPT-5.5, GPT-5.6+) | Anthropic (Claude Fable 5.1) |
|---|---|---|
| Discount on cached input | 90% off 0.1x | 90% off 0.1x |
| Write premium | None | 5-min cache +25% 1.25x base; 1-hour +100% 2x base |
| Default TTL | ~5-10 min empirical active workloads continuous hits reset warming window | 5 min sliding |
| Custom TTL | Not exposed | 1-hour extended TTL option with higher write premium |
| Caller-side config | None automatic — nothing to deploy, cache engages automatically any prompt over 1024 tokens; cached portions billed at 10% normal input price savings show in cached_tokens field usage block; no markers SDK upgrade caller config; if application has system prompt over 1024 tokens stable across requests — almost every production app — discount already engaging or engaging moment you stabilise leading content | Explicit cache_control field either once top level automatic breakpoint management or individual blocks fine control usage response itemises write and read tokens |
| Minimum prompt length | 1024 tokens minimum + 128-token boundary for additional caching beyond base 1024 OpenAI caches additional content 128-token chunks practical 2200 tokens may cache around 2176 closest 128 boundary below | ~few hundred tokens with marker 1024 Sonnet/Opus |
| How to read | cached_tokens field in prompt_tokens_details usage block | usage response itemises write and read tokens |
| Break-even | Immediate | After few hits due write premium |

**OpenAI vs Anthropic surprising near-tie:** For most prompt-caching era conventional wisdom Anthropic for max savings 90% OpenAI for simplicity 50%. That conventional wisdom now wrong as of mid-2026 both providers offer same 90% discount cached input tokens difference now structural not magnitude. OpenAI now wins operational simplicity AND matches savings no marker discipline no write premium no SDK changes and 90% discount previously Anthropic-exclusive right default for teams that want discount without engineering investment. Anthropic only remaining structural advantage explicit 1-hour TTL option for predictable but spaced-out workloads e.g. one request every 20-30 minutes against same prompt Anthropic 1-hour cache +2x write premium can beat OpenAI ~5-10 min auto-cache that may expire between requests for typical continuous-traffic workloads difference invisible. Most production deployments running both providers capture both automatic discount OpenAI traffic marker-driven discount Anthropic traffic both at 90% off.

**What invalidates cache:**

- Any change leading content — different system prompt different tool definitions different leading messages fingerprint changes cache misses
- Different model parameter — cache entries per-model GPT-5.4 cache doesn't serve GPT-5.4-mini request
- Variable content at start prompt — timestamps user IDs session IDs injected into system prompt invalidate cache per request most common cause caching not engaging
- Cache TTL elapsed ~5-10 minutes inactivity same prefix
- Things that don't invalidate: variable user messages at end — cache key leading content user message variable suffix doesn't affect caching — different sampling parameters temperature top_p max_tokens affect generation not cache match — different request IDs metadata headers not part cache key

**Anti-patterns that defeat cache:**

- Timestamps in system prompt "You are responding at [timestamp] [Instructions...]" cache fingerprint changes per request caching never engages strip timestamp if need put in user message or metadata field
- Per-user customisation injected into system prompt "You are assistant for user [user_id] [Generic instructions...]" same problem system prompt varies per user cache invalidates per request move per-user customisation to user message itself or keep generic in system prompt inject user-specific behaviour via fewer variable points
- Short system prompts sub-1024 tokens minimum threshold means short prompts don't cache at all if system prompt only 500 tokens not benefiting either pad with useful content additional instructions examples until cross 1024 tokens or rely different cost-reduction techniques

**Production patterns maximise hit rate:**

- Stable system prompt + retrieved context + user message canonical pattern system prompt and tool definitions go at very start prompt stable retrieved context follows semi-stable often cached after warm-up user message at end variable never cached almost every production LLM workload looks like this
- Prompt-template versioning when you update system prompt cache invalidates wholesale plan deploy prompt updates during low-traffic windows so re-warming pain bounded 5-10 min TTL means caches re-populate quickly once new requests start flowing
- Co-location variable content if application has multiple variable elements e.g. user session history + current message put them together at end prompt rather than scattered through reduces accidental invalidations from interleaving variable content into otherwise-stable sections
- Cache-warming predictable workloads if traffic pattern predictable e.g. business-hours support chatbot ramps up 9 AM fire synthetic warm-up request at start active window populate cache first real user request hits warmed cache instead paying full input price

**Reading cache hits:**

```python
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5-4",
    messages=[
        {"role": "system", "content": "...(long stable system prompt 1200 tokens)..."},
        {"role": "user", "content": "How do I reset my password?"}
    ]
)
print(response.usage)
# CompletionUsage(prompt_tokens=1532, completion_tokens=87, total_tokens=1619,
# prompt_tokens_details=PromptTokensDetails(cached_tokens=1408, audio_tokens=0))
# cached_tokens count input tokens served from cache billed at 0.1x

def calculate_openai_cost(usage, input_price_per_million, output_price_per_million):
    cached = usage.prompt_tokens_details.cached_tokens
    uncached = usage.prompt_tokens - cached
    cost = (
        uncached * input_price_per_million / 1_000_000
        + cached * input_price_per_million * 0.1 / 1_000_000   # 90% discount
        + usage.completion_tokens * output_price_per_million / 1_000_000
    )
    return cost
```

First thing to check deploying prompt caching: is cached_tokens non-zero on second and subsequent requests? If yes caching working. If zero something wrong either prefix shorter than 1024 tokens or drifting per request.

**Good structure stable content first:**

```
GOOD STRUCTURE (stable content first):
┌─────────────────────────────────────┐
│ System prompt (1,200 tokens)        │ ← cached after first hit
│ Tool definitions (400 tokens)       │ ← cached after first hit
│ Retrieved context (variable, 600t)  │ ← cacheable if stable across users
│ User message (variable, 50 tokens)  │ ← not cached
└─────────────────────────────────────┘

BAD STRUCTURE (variable content first):
┌─────────────────────────────────────┐
│ User message (50 tokens)            │ ← cache key starts here
│ System prompt (1,200 tokens)        │ ← invalidated by user message variation
│ Tool definitions (400 tokens)       │ ← invalidated
└─────────────────────────────────────┘
```

If application has bad structure fix one-time refactor pays for itself within hours deployment on any meaningful traffic.

**Anthropic explicit caching:**

```python
# Anthropic cache_control
response = anthropic.messages.create(
  model="claude-fable-5.1",
  max_tokens=1024,
  system=[
    {"type": "text", "text": "You are refund specialist... long instructions 2000 tokens", "cache_control": {"type": "ephemeral"}},
    {"type": "text", "text": "Tool definitions..."}
  ],
  messages=[{"role": "user", "content": "Refund order #12345"}]
)
# usage: cache_creation_input_tokens, cache_read_input_tokens
# cache_creation 1.25x, cache_read 0.1x (90% off)
```

**TTL behavior:**

- OpenAI doesn't officially publish precise TTL empirically cache stays warm approximately 5-10 minutes inactivity active workloads consistent traffic see continuous cache hits because each request resets warming window bursty traffic e.g. concentrated during business hours caches expire overnight each morning first requests pay full price cache warms within few requests subsequent traffic hits warm cache acceptable sparse traffic e.g. one request every 30 minutes cache expires between requests caching effectively never engages other techniques response-level caching model-tier routing carry more weight
- Anthropic default cache TTL quietly reverted from 1 hour to 5 minutes for weeks early 2026 with no announcement per developer reports — need monitor
- Lack explicit TTL control one structural difference vs Anthropic Anthropic offers explicit 1-hour extended-TTL option with higher write premium OpenAI doesn't expose TTL as caller-side dial

### 4. KV-Cache Deep Dive — PagedAttention, RadixAttention, Multi-Tier, Quantization

**What is KV cache:** During prefill model computes Key and Value tensors for every input token. During decode to generate next token model reuses those KVs rather than recomputing. KV cache memory grows with batch size and context length primary GPU memory headroom bottleneck.

KV cache memory per token: DeepSeek cut memory cost cached token from ~390,000 bytes to 890 bytes — 438x reduction in just under 3 years via quantization + compression — what did each step cost and buy.

**PagedAttention (vLLM default since 2023 refined through 2026):**

- Like OS virtual memory paging — KV cache stored non-contiguous pages rather than contiguous — eliminates fragmentation — allows sharing prefix across requests
- Top throughput lever KV cache reuse with PagedAttention plus continuous batching vLLM default since 2023 refined through 2026
- Unified memory managers such as PagedAttention abstract GPU memory
- Reduces VRAM fragmentation reclaims cold KV blocks dynamically without thrashing GPU memory

**RadixAttention (SGLang 2026 — specifically optimized multi-turn agents, code gen loops, structured JSON outputs):**

- Organizes KV cache as radix tree — retains and shares prefix KV caches across branching multi-turn agent calls eliminating redundant attention re-computation
- When new request arrives that shares identical system prompt documentation block or previous turn history SGLang reuses existing KV tensor in memory with zero re-computation
- Sub-50ms prefill latency reusing cached prefixes reduces TTFT from 1200ms to under 45ms multi-turn conversations
- Up to 5x higher throughput over standard serving — dramatically reduces TTFT and GPU memory fragmentation under heavy agentic traffic — allows serving 3x to 5x more concurrent agent streams per GPU node without degrading response quality
- SGLang programmatic agent call: s += sgl.system(codebase_context) automatically caches 10k token context in RadixTree s += sgl.user(user_goal) enforces strict JSON grammar at full generation speed via compressed finite state machines FSMs directly within GPU decoding kernel near full generation speeds without latency penalties constrained decoding & structured outputs — SGLang reuses system cache across all 100 iterations with 0ms prefill

**Benchmark Matrix SGLang vs vLLM production 8x H100 clusters Llama 3.3 DeepSeek-V3 workloads:**

| Metric | SGLang (RadixAttention) | vLLM (PagedAttention v2) | TensorRT-LLM |
|---|---|---|---|
| Multi-Turn Cache Reuse | Automatic Radix Tree Match | Prefix Caching Limited | Manual Buffer Management |
| Constrained JSON Decoding Speed | Native Full Generation Speed | Outlines Slow Fallback | Requires Custom Engine Plugins |
| Throughput under Agent Loops | 3.8x - 5.2x baseline | 1.8x - 2.4x baseline | 2.1x - 3.0x baseline |
| TTFT multi-turn | <45ms | 200-500ms | 300-600ms |
| Setup Developer Ergonomics | Pythonic Intuitive | Standardized Popular | Complex C++ Compilation |
| VRAM Fragmentation | Dramatically Reduced reclaims cold blocks dynamically | Reduced | Manual |

**Multi-Tier KV Cache Management (2026 theme):**

- Hierarchical sparse KV cache that dynamically shifts entries between GPU memory and overflow based on load instead of fixed resident/evicted split — Adaptive DHiSparse speculative decoding over load-adaptive KV hierarchy 2026-10-09 combines speculative decoding with hierarchical sparse KV cache dynamically shifts entries between GPU memory and overflow based on load at 500K context concurrency 512
- KVSculpt ArXiv 2026 distillation approach optimizing small continuous set KVs
- DUAL-BLADE ICDCS 2026 tightly couples NVMe and GPU DMA to trim 30-40% from latency
- KV Prefetching Speculative Cache SpeCache keeps reduced-precision
- Google TurboQuant ICLR 26 presented near-optimal 2-stage vector quantizer PolarQuant + 1-bit QJL achieving quality-neutral KV quantization ~3.5 bits
- Multi-tier: GPU HBM hot cache → CPU RAM warm → NVMe cold → re-compute on demand
- Cache is the Model — Inferoa AI measured KV cache hit rate during real agentic coding task for every 100 tokens agent processed only 2.2 computed from scratch rest free

**KV Cache Optimization Checklist:**

- KV Cache Prefix Alignment: Structure system prompts so static instructions JSON schemas tool definitions sit at exact beginning context window — enables prefix reuse
- Quantization: Google TurboQuant 3.5 bits quality-neutral — 438x reduction DeepSeek 390KB→890 bytes — optional native MTP speculative decoding validated with LMCache MTP acceptance rate unchanged 0.947 vs 0.952 cached prefix KV — speculative decoding with cached prefix preserves score-level equivalence gsm8k 0.95 computed vs 0.96 retrieved within sampling error leaves draft layer
- PagedAttention v2: reduces fragmentation
- RadixAttention: automatic radix tree match across branching multi-turn agent calls
- Less Context Better Agents: pruning to last 5 tool call/response pairs 79% completion 535k tokens vs full history 71% completion 1.48M tokens — pruning + caching better than full history
- Continuous batching: one weight read serves every request in batch enemy of latency but friend throughput

### 5. Speculative Decoding — Draft-Target 2-3x Throughput, 15x on Blackwell

**What:** Technique accelerating autoregressive decoding phase LLM inference by predicting multiple tokens per iteration — predicting multiple tokens per iteration rather than one-by-one sequential.

High-throughput enterprise Generative AI inference 2026 requires software architects combine speculative decoding dynamic model routing token telemetry proxies reduce p99 latency cloud compute overhead.

**How:**

- Draft model (small fast e.g. 1B Qwen, SmolLM2 1.7B) generates k tokens quickly (e.g. k=4)
- Target model (large e.g. 7B, 70B) verifies k tokens in parallel single forward pass — accepts those that match its distribution, rejects rest
- Payoff: When draft accepts ~70% proposed tokens → 1.5x to 3x throughput — reduces decode latency by 2x to 3x for predictable structured outputs requires careful KV cache memory allocation prevent OOM on shared GPU memory

**Guideline NVIDIA: Increase speculative decoding draft length to push GEMMs into compute-bound region without increasing KV cache capacity pressure — for reasoning and agentic workloads attention tends dominate execution time throughput-oriented region**

**Enterprise patterns:**

- Draft: Qwen 2.5 1.5B or Llama 3.2 1B or TinyLlama 1.1B — fast on consumer GPU
- Target: Llama 3.2 3B, Qwen 2.5 7B, Phi-4 Mini 3.8B — your refund specialist
- Acceptance rate: ~70% typical structured JSON outputs higher acceptance (predictable) — speculative decoding payoff 1.5x to 3x throughput when draft accepts roughly 70% tokens
- Tools: vLLM and AWS Trainium evolved support configurations by optimizing KV cache management for both draft and target models memory footprint KV cache significant concern storing two sets hidden
- Unified stacks like SpecForge v0.3.0 allow disaggregated and colocated deployment strategies as of Sept 2026 industry moved beyond simple draft-target pairs toward unified stacks
- DFlash speculative decoding on Blackwell achieving up to 15x inference speedups — NVIDIA own Dynamo framework targets full-stack agentic inference optimization tackling same problem from hardware side finding ways

**Speculative decoding + KV cache synergy:**

Speculative decoding with cached prefix preserves score-level equivalence gsm8k 0.95 computed vs 0.96 retrieved within sampling error — MTP acceptance rate unchanged 0.947 vs 0.952 with cached prefix KV — means you can combine prompt caching + speculative decoding without accuracy loss.

**When speculative decoding wins:**

- Structured outputs JSON tool calls — predictable — high acceptance
- Code generation loops — draft predicts next tool call quickly
- Customer support with repetitive templates — refund classification
- Agentic loops where many tokens are boilerplate reasoning
- When ITL is bottleneck not TTFT — decode latency 2x to 3x reduction

**When not:**

- Creative generation high novelty — draft poor predictor
- Very short outputs — overhead not worth
- When GPU memory limited storing two KV caches (draft+target) may OOM — need unified memory manager PagedAttention abstract

**vLLM config example:**

```python
from vllm import LLM, SamplingParams

# vLLM with speculative decoding
llm = LLM(
  model="microsoft/phi-4-mini",  # target
  speculative_model="Qwen/Qwen2.5-1.5B-Instruct",  # draft
  num_speculative_tokens=4,  # draft length k
  use_v2_block_manager=True,  # PagedAttention v2
  enable_prefix_caching=True,  # KV cache reuse
  max_num_seqs=256,  # continuous batching
)

# SGLang with RadixAttention + speculative decoding
import sglang as sgl

@sgl.function
def agent_loop(s, codebase_context, user_goal):
  s += sgl.system(codebase_context)  # 10k token context cached RadixTree 0ms prefill after first
  s += sgl.user(user_goal)
  s += sgl.assistant(sgl.gen("action", regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}'))  # constrained JSON at full speed FSM in GPU kernel
```

### 6. Disaggregated Serving — Prefill/Decode Separation

Three themes dominate June 2026 infrastructure: speculative decoding reaching production maturity, disaggregated serving architectures becoming mainstream, multi-tier KV cache management enabling dramatically higher throughput.

Disaggregated serving: Separate prefill (compute-bound encoding input) and decode (memory-bound generating tokens) onto different GPU pools — prefill on high-compute GPUs, decode on high-memory bandwidth GPUs — reduces interference — NVIDIA Dynamo framework targets full-stack agentic inference optimization tackling same problem hardware side.

Why matters for agentic: agentic workloads have long prefill (8000 tokens codebase) repeated many times + short decode (tool call JSON 50 tokens) — disaggregating prevents long prefill blocking short decodes queue bottlenecks.

Batching standard fix throughput one weight read serves every request in batch — enemy of latency — but with disaggregated + continuous batching + PagedAttention balances.

**Speculative decoding + disaggregated + RadixAttention + PagedAttention + prompt caching = 2026 production stack.**

### 7. SGLang vs vLLM vs TensorRT-LLM Benchmark Matrix

Already covered but consolidated for decision:

| Metric | SGLang RadixAttention | vLLM PagedAttention v2 | TensorRT-LLM |
|---|---|---|---|
| Multi-Turn Cache Reuse | Automatic Radix Tree Match across branching multi-turn | Prefix Caching Limited | Manual Buffer Management |
| Constrained JSON Speed | Native Full Generation Speed FSM in GPU kernel | Outlines Slow Fallback | Requires Custom Engine Plugins |
| Throughput Agent Loops | 3.8x-5.2x baseline | 1.8x-2.4x baseline | 2.1x-3.0x baseline |
| TTFT multi-turn | Sub-50ms reuse cached prefixes reduces TTFT 1200ms→45ms | 200-500ms | 300-600ms |
| VRAM Fragmentation | Dramatically Reduced reclaims cold KV blocks dynamically without thrashing | Reduced | Manual |
| Cost-per-token | Superior 3x to 5x more concurrent streams per GPU node without degrading quality | Standard | Standard |
| Speculative Decoding | Native support SpecForge v0.3.0 disaggregated colocated | Native support num_speculative_tokens draft model | DFlash 15x Blackwell |
| Setup Ergonomics | Pythonic Intuitive runs efficiently any modern NVIDIA GPU RTX 3090 4090 A6000 A100 H100 Linux CUDA | Standardized Popular | Complex C++ Compilation |
| Best For | Agentic coding, code gen loops, structured JSON, multi-turn tool calls, 10k context reused 100 iterations 0ms prefill | General high-throughput serving, continuous batching default since 2023 refined 2026 | Blackwell hardware max speed, enterprise NVIDIA stack Dynamo |

**Recommendation for your Node.js + Postgres stack:**

- Self-hosted 7B model on RTX 4090: vLLM with enable_prefix_caching + speculative_model Qwen 1.5B → 2-3x throughput
- Agentic coding with 10k context repeated: SGLang RadixAttention → sub-50ms TTFT 5x throughput
- Cloud API: Prompt caching 90% off — structure stable content first → 80-90% input cost cut Notion case study 90% cost 85% latency
- Combine all three: Prompt caching (provider) + KV reuse (SGLang/vLLM) + speculative decoding (draft-target) + pruning (last 5 tool calls) → 71%→79% completion + 1.48M→535k tokens + 14.56h→~4h per run

### 8. 90% Cost Cut Playbook — 10 Production Patterns

**Pattern 1: Stable Prefix First — prompt structure discipline**

```
GOOD:
System prompt 1200 tokens (stable) ← cached after first hit 0.1x
Tool definitions 400 tokens (stable) ← cached
OKF bundle / Retrieved context 600 tokens (semi-stable) ← cacheable if stable across users
User message 50 tokens (variable) ← not cached

BAD:
User message 50 tokens ← cache key starts here
System prompt 1200 tokens ← invalidated by user variation
Tool definitions 400 tokens ← invalidated
```

Fix one-time refactor pays for itself within hours any meaningful traffic.

**Pattern 2: Provider Prompt Caching 90% off — OpenAI automatic, Anthropic explicit**

- OpenAI: nothing to deploy cache engages automatically any prompt over 1024 tokens cached portions billed at 10% normal input price savings show in cached_tokens field usage block no markers SDK upgrade required — if system prompt over 1024 tokens stable across requests discount already engaging or engaging moment you stabilise leading content — 128-token boundary additional caching beyond 1024 base — structure stable content first variable content last — cache key leading portion prompt everything before variable content has chance hit cache
- Anthropic: add cache_control field either once top level automatic breakpoint management or individual blocks fine control usage response itemises write read tokens — explicit 1024 tokens Sonnet/Opus 2048-4096 model-dependent — cache read 0.1x 90% off write 1.25x 5-min / 2x 1-hr — 5 minutes refreshed on hit — 1-hour extended TTL option structural advantage spaced-out workloads
- Both now 90% off cached input as of mid-2026 GPT-5.4 GPT-5.5 dropped cached input to $0.50/M against $5/M standard that is 90% matching Anthropic read rate — OpenAI wins operational simplicity matches savings no marker no write premium — Anthropic only remaining advantage 1-hour TTL
- Most production deployments running both providers capture both automatic discount OpenAI traffic marker-driven discount Anthropic traffic both at 90% off — customers reduce API costs 80-90% simultaneously improving response times 2-3x

**Pattern 3: KV Cache Reuse — PagedAttention + RadixAttention + Prefix Alignment**

- Top throughput lever KV cache reuse with PagedAttention plus continuous batching vLLM default since 2023 refined through 2026
- KV Cache Prefix Alignment: structure system prompts so static instructions JSON schemas tool definitions sit at exact beginning context window enables prefix reuse
- SGLang Radix-Tree KV Cache Reuse retains shares prefix KV caches across branching multi-turn agent calls eliminating redundant attention re-computation — sub-50ms prefill latency reducing TTFT 1200ms→45ms
- Up to 5x higher throughput over standard serving dramatically reduces TTFT GPU memory fragmentation under heavy agentic traffic
- Allows serving 3x to 5x more concurrent agent streams per GPU node without degrading quality
- For every 100 tokens agent processed only 2.2 computed from scratch rest free — Cache Is The Model Inferoa AI measured real agentic coding task
- Implementation: vLLM enable_prefix_caching True use_v2_block_manager True max_num_seqs 256 continuous batching; SGLang automatic RadixTree match Pythonic intuitive

**Pattern 4: Speculative Decoding 2-3x Throughput 70% Acceptance Up to 15x Blackwell**

- Technique accelerating autoregressive decoding phase predicting multiple tokens per iteration
- Enterprise serving environments deploy unified memory managers such as PagedAttention abstract
- Reduces decode latency 2x to 3x predictable structured outputs requires careful KV cache memory allocation prevent OOM shared GPU memory
- High-throughput enterprise Generative AI inference 2026 requires combine speculative decoding dynamic model routing token telemetry proxies reduce p99 latency cloud compute overhead
- Guideline Increase speculative decoding draft length to push GEMMs into compute-bound region without increasing KV cache capacity pressure for reasoning agentic workloads attention tends dominate execution time throughput-oriented region
- As of Sept 2026 industry moved beyond simple draft-target pairs toward unified stacks like SpecForge v0.3.0 allow disaggregated colocated deployment strategies
- Tools like vLLM AWS Trainium evolved support configurations by optimizing KV cache management for both draft target models memory footprint significant concern storing two sets hidden
- Tools vLLM AWS Trainium evolved support configurations by optimizing KV cache memory
- Draft: Qwen 2.5 1.5B SmolLM2 1.7B fast consumer GPU Target: Phi-4 Mini 3.8B Qwen 2.5 3B Llama 3.2 3B refund specialist Acceptance ~70% typical structured JSON higher
- Speculative decoding with cached prefix preserves score-level equivalence gsm8k 0.95 computed vs 0.96 retrieved within sampling error leaves draft layer — MTP acceptance unchanged 0.947 vs 0.952 cached prefix KV — can combine prompt caching + speculative decoding without accuracy loss
- DFlash speculative decoding on Blackwell up to 15x inference speedups NVIDIA Dynamo framework full-stack agentic inference optimization

**Pattern 5: Less Context Better Agents — Pruning + Compaction**

- arXiv 2606.10209 Less Context Better Agents tested GPT-5 configurations 50-task enterprise expense itemization benchmark full conversation history 71.0% task completion 1,480,996 tokens consumed 14.56 hours per run pruning to last 5 tool call/response pairs 79.0% completion 535,274 tokens — less context better agents
- Implementation: Keep system prompt stable cached, prune conversation history to last 5 tool pairs, summarize older into 1-line per failure via cheap model Gemini Flash — squashing 10 failures into 1 line hierarchical L0→L3 sliding window with anchors incremental summarization every K turns compact at 75% ~24K for 32K local
- For 32K local SLM compact at 75% ~24K — save 60% tokens write big data to file keep summary progress.json + session_handoff.md

**Pattern 6: Continuous Batching + Disaggregated Prefill/Decode**

- Batching standard fix throughput one weight read serves every request in batch enemy of latency — continuous batching vLLM default balances
- Disaggregated serving architectures becoming mainstream — separate prefill compute-bound encoding input and decode memory-bound generating tokens onto different GPU pools prefill high-compute GPUs decode high-memory bandwidth GPUs reduces interference — NVIDIA Dynamo framework full-stack agentic inference optimization
- Agentic workloads long prefill 8000 tokens codebase repeated many times + short decode tool call JSON 50 tokens — disaggregating prevents long prefill blocking short decodes queue bottlenecks
- Multi-turn memory mixed precision safer rollouts serving catches up agentic workloads edition LLM Inference Digest 2026-10-07 to 2026-10-14 new developments arXiv vLLM Hugging Face blogs Together AI Modal Latent Space

**Pattern 7: Multi-Tier KV Cache + Quantization + Compression**

- Hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load instead fixed resident/evicted split Adaptive DHiSparse speculative decoding over load-adaptive KV hierarchy 2026-10-09 combines speculative decoding with hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load at 500K context concurrency 512
- DeepSeek cut memory cost cached token from roughly 390,000 bytes to 890 bytes — 438x reduction just under 3 years what did each step cost and buy optional native MTP speculative decoding validated with LMCache MTP acceptance unchanged 0.947 vs 0.952 cached prefix KV speculative decoding with cached prefix preserves score-level equivalence gsm8k 0.95 computed vs 0.96 retrieved within sampling error
- Google TurboQuant ICLR 26 presented near-optimal 2-stage vector quantizer PolarQuant + 1-bit QJL achieving quality-neutral KV quantization ~3.5 bits
- KVSculpt ArXiv 26 distillation approach optimizing small continuous set KVs DUAL-BLADE ICDCS 26 tightly couples NVMe GPU DMA trim 30-40% from latency KV Prefetching Speculative Cache SpeCache keeps reduced-precision
- Multi-tier GPU HBM hot cache → CPU RAM warm → NVMe cold → re-compute demand — Cache Is The Model KV cache hit rate Inferoa AI measured real agentic coding task for every 100 tokens agent processed only 2.2 computed from scratch rest free
- Quantization 50% to 90% cost reductions input tokens alongside 40% to 85% drop TTFT latency per provider table

**Pattern 8: Constrained Decoding + Structured Outputs at Full Speed**

- Unlike third-party regex wrappers slow generation to crawl SGLang compiles JSON schemas into compressed finite state machines FSMs directly within GPU decoding kernel — generates validated JSON regex-constrained tokens at near full generation speeds without latency penalties — zero-latency constrained decoding
- Example SGLang s += sgl.assistant(sgl.gen("action", regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}')) enforces strict JSON grammar at full generation speed — SGLang reuses system cache across all 100 iterations with 0ms prefill
- For refund agent need 99.9% JSON valid tool calls — constrained decoding eliminates parsing errors without latency penalty

**Pattern 9: Model Routing — SLM Drafts, LLM Verifies, SLM Handles 80%**

- Routing: SLM classifies incoming query routes to either local SLM for simple queries or LLM API for complex ones cuts cost dramatically because most production queries tend simple
- LLM as planner SLM as executor agentic systems LLM decomposes task SLM handles specific subtasks entity extraction slot filling retrieval filtering
- Speculative Decoding SLM generates draft token sequences quickly LLM verifies accepts corrects well-validated technique speeding up LLM inference without quality loss Google DeepMind published research demonstrating 2-3x speedups
- For your refund agent: SmolLM2 1.7B or Qwen 2.5 1.5B draft → Phi-4 Mini 3.8B target → only 20% complex multi-bundle routed to GPT-5.4 via A2A — 80% local cost ~$0 vs $0.03 API
- Cost comparison: Single GPT-4 API $0.03 Run 10k queries/day 6 months over $50k Fine-tuned SLM running $1500 GPU fraction cost data never leaving servers — biggest mistake defaulting LLM API when fine-tuned 3B model would handle job at 1/50th cost better latency full data control

**Pattern 10: Observability + Cost Tracking — Track cached_tokens, KV Hit, TTFT, ITL, Cost per Task**

- OpenAI returns cached_tokens field in response usage block prompt_tokens_details cached_tokens count input tokens served from cache billed at 0.1x — calculate cost def calculate_openai_cost usage input_price output_price uncached * input_price /1M + cached*input_price*0.1/1M + completion*output_price/1M return cost — first thing check deploying prompt caching is cached_tokens non-zero second subsequent requests yes working zero something wrong either prefix shorter than 1024 tokens or drifting per request
- Anthropic usage itemises cache_creation_input_tokens cache_read_input_tokens
- Track TTFT time-to-first-token target under 500ms chat sustained tokens-per-second per user GPU memory headroom
- Track KV cache hit rate — Inferoa AI measured 2.2% computed from scratch 97.8% free in agentic coding task
- Track speculative decoding acceptance rate ~70% typical 1.5-3x throughput payoff
- Track cost per task — 71%→79% completion + 1.48M→535k tokens + 14.56h→~4h per run Less Context Better Agents — measure improvement
- Providers can bill repeated input at ~10% normal price OpenAI GPT-5.5 cached input $0.50/MTok vs $5.00 — Anthropic bills cache writes at 1.25x normal input 5-min TTL 2x 1-hour TTL
- Provider differences mid-2026 snapshot OpenAI automatic older models no write charge GPT-5.5 $0.50 cached vs $5.00 normal input per MTok 90% discount From GPT-5.6 writes — Anthropic vs OpenAI prompt caching complete 2026 comparison We've seen customers reduce API costs 80-90% simultaneously improving response times 2-3x

**Combined 90% cut stack that actually ships:**

```
Layer 1 Prompt Caching (provider) 90% off input: stable system prompt 1200 tokens + tool definitions 400 tokens at beginning, variable user message at end, minimum 1024 tokens, 128-token boundary, TTL 5-10 min warm via synthetic request at 9 AM business-hours, cache_creation 1.25x Anthropic vs no write premium OpenAI, cache_read 0.1x both — saves 80-90% input cost 40-85% TTFT

Layer 2 KV Cache Reuse (inference engine) 3-5x throughput: PagedAttention v2 non-contiguous pages eliminates fragmentation sharing prefix across requests + RadixAttention radix tree automatic match across branching multi-turn agent calls zero re-computation sub-50ms prefill TTFT 1200ms→45ms 3.8-5.2x baseline throughput agent loops 3x-5x more concurrent streams per GPU node — sub-50ms prefill latency reusing cached prefixes — Cache Is The Model 97.8% free

Layer 3 Speculative Decoding 2-3x ITL up to 15x Blackwell: draft model 1.5B generates k=4 tokens quickly target 3.8B verifies parallel single forward pass 70% acceptance 1.5-3x throughput 2-3x decode latency predictable structured JSON outputs high acceptance code gen loops refund classification — SpecForge v0.3.0 disaggregated colocated DFlash 15x Blackwell NVIDIA Dynamo — combine with cached prefix preserves equivalence gsm8k 0.95 vs 0.96 MTP acceptance unchanged 0.947 vs 0.952

Layer 4 Less Context Better Agents 64% token cut + 8% accuracy gain: full history 71% completion 1.48M tokens 14.56h → prune last 5 tool pairs 79% completion 535k tokens — keep system prompt stable cached prune conversation history summarize older via cheap model Gemini Flash squashing 10 failures into 1 line hierarchical L0→L3 sliding window anchors incremental summarization every K turns compact at 75% ~24K for 32K local write big data to file keep summary progress.json + session_handoff.md enables 6-hour agents

Layer 5 Model Routing 80/20 SLM handles 80% local $0: SLM classifies routes local SLM simple queries LLM API complex cuts cost dramatically most production queries tend simple — LLM planner SLM executor — speculative decoding SLM drafts LLM verifies 2-3x speedups Google DeepMind — fine-tuned 3B handles job at 1/50th cost better latency full data control vs GPT-4 $0.03 10k/day 6mo $50k+ vs $1500 GPU fraction

Total: Input cost 90% off via prompt caching + TTFT 80% off via RadixAttention + ITL 2-3x via speculative decoding + throughput 5x via continuous batching + PagedAttention + tokens 64% off via pruning + 80% queries local $0 via SLM routing = ~90% total bill cut Notion case study 90% cost 85% latency simultaneous 80-90% API costs 2-3x response times
```

### 9. Node.js Production Implementation — Prompt Structure, Caching, Batching

**Prompt structure for 90% cache hit rate:**

```typescript
// GOOD STRUCTURE — stable content first cacheable
const SYSTEM_PROMPT = `
You are refund specialist agent for e-commerce.
Policy v2.3 page 25: bundle promotions require approval never auto-refund.
Tools: refund_policy_check, inventory_check, product_search, acp_create_checkout, ap2_create_intent_mandate
Schema: {"order_id": string, "action": "approve|reject", "reason": string}
... 1200 tokens stable ...
`.trim(); // 1200 tokens >1024 minimum for OpenAI automatic caching

const TOOL_DEFINITIONS = JSON.stringify([
  { name: "refund_policy_check", description: "Checks order against refund policy", parameters: { orderId: "string" } },
  { name: "acp_create_checkout", description: "Creates ACP checkout with SPT", parameters: { merchantId: "string", total: "number" } }
]); // 400 tokens stable

// In request — stable first variable last
const messages = [
  { role: "system", content: SYSTEM_PROMPT }, // cached 0.1x after first hit
  { role: "system", content: `Tool definitions: ${TOOL_DEFINITIONS}` }, // cached
  { role: "system", content: `OKF bundle: ${okfBundleConcepts}` }, // semi-stable cached if same across users
  { role: "user", content: `Refund order #${orderId}: ${userMessage}` } // variable not cached
];

// BAD — timestamp or user_id in system prompt invalidates cache per request
// "You are responding at ${new Date().toISOString()} for user ${userId}..." → cache never engages
// Fix: strip timestamp, put in user message or metadata field
```

**Anthropic explicit caching Node.js:**

```typescript
import Anthropic from "@anthropic-ai/sdk";
const anthropic = new Anthropic();

const response = await anthropic.messages.create({
  model: "claude-fable-5.1",
  max_tokens: 1024,
  system: [
    {
      type: "text",
      text: SYSTEM_PROMPT, // 1200 tokens
      cache_control: { type: "ephemeral" } // explicit marker for 5-min cache 1.25x write 0.1x read
    },
    {
      type: "text",
      text: TOOL_DEFINITIONS
    }
  ],
  messages: [{ role: "user", content: `Refund order #${orderId}` }]
});

// Track usage
console.log(response.usage);
// { cache_creation_input_tokens: 1200, cache_read_input_tokens: 0 } first request
// Second request same prefix: { cache_creation_input_tokens: 0, cache_read_input_tokens: 1200 } → 90% off
const cost = (response.usage.cache_creation_input_tokens * 1.25 + response.usage.cache_read_input_tokens * 0.1 + response.usage.output_tokens * 5) / 1_000_000 * inputPrice;
```

**OpenAI automatic caching Node.js:**

```typescript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.chat.completions.create({
  model: "gpt-5-4",
  messages: [
    { role: "system", content: SYSTEM_PROMPT }, // >1024 tokens automatic caching no markers SDK upgrade
    { role: "user", content: `Refund order #${orderId}` }
  ]
});

console.log(response.usage.prompt_tokens_details.cached_tokens); // 1408 tokens hit cache billed 0.1x

function calculateCost(usage, inputPricePerM, outputPricePerM) {
  const cached = usage.prompt_tokens_details.cached_tokens || 0;
  const uncached = usage.prompt_tokens - cached;
  return (uncached * inputPricePerM / 1_000_000 + cached * inputPricePerM * 0.1 / 1_000_000 + usage.completion_tokens * outputPricePerM / 1_000_000);
}
// First thing check is cached_tokens non-zero second subsequent requests yes working zero something wrong either prefix shorter than 1024 tokens or drifting per request

// Cache-warming predictable workloads business-hours 9 AM
await openai.chat.completions.create({ model: "gpt-5-4", messages: [{ role: "system", content: SYSTEM_PROMPT }, { role: "user", content: "warmup" }] });
// First real user request hits warmed cache instead paying full input price
```

**Continuous batching + queuing for agentic loops:**

```typescript
import { Queue } from "bullmq"; // or SQS, Temporal
const refundQueue = new Queue("refund-tasks");

// Enqueue refund tasks — batching standard fix throughput one weight read serves every request in batch enemy of latency but continuous batching balances
await refundQueue.add("refund", { orderId: "12345", userId: "user_789", priority: "high" }, { attempts: 3, backoff: { type: "exponential", delay: 1000 } });

// Worker with vLLM client continuous batching
import { LLM } from "vllm-client"; // pseudo
const llm = new LLM({
  model: "microsoft/phi-4-mini",
  speculative_model: "Qwen/Qwen2.5-1.5B-Instruct",
  num_speculative_tokens: 4,
  enable_prefix_caching: true, // KV reuse PagedAttention
  max_num_seqs: 256 // continuous batching
});

// Process batch — PagedAttention + RadixAttention reuse prefix across 256 concurrent refund checks
const results = await llm.generateBatch(prompts); // prompts share same SYSTEM_PROMPT 1200 tokens cached RadixTree 0ms prefill after first
```

### 10. Self-Hosted Stack — vLLM PagedAttention + SGLang RadixTree + LMCache

**vLLM production config:**

```python
from vllm import LLM, SamplingParams

# vLLM with prefix caching + speculative decoding + continuous batching
llm = LLM(
  model="microsoft/phi-4-mini",  # target 3.8B refund specialist
  speculative_model="Qwen/Qwen2.5-1.5B-Instruct",  # draft fast consumer GPU
  num_speculative_tokens=4,  # draft length k push GEMMs into compute-bound without increasing KV cache capacity pressure
  use_v2_block_manager=True,  # PagedAttention v2 eliminates fragmentation sharing prefix across requests unified memory managers PagedAttention abstract
  enable_prefix_caching=True,  # KV cache reuse top throughput lever PagedAttention + continuous batching vLLM default since 2023 refined 2026
  max_num_seqs=256,  # continuous batching one weight read serves every request in batch
  max_model_len=32768,
  gpu_memory_utilization=0.9,
  enable_chunked_prefill=True,  # for long 8000 token codebase contexts
)

# Prompt structure stable first
SYSTEM_PROMPT = "You are refund specialist... policy v2.3 page 25... tools..." # 1200 tokens
# All requests share same SYSTEM_PROMPT → RadixTree/PagedAttention reuses KV tensor zero re-computation sub-50ms prefill TTFT 1200ms→45ms

sampling_params = SamplingParams(
  temperature=0.2,  # low temp for refund classification deterministic
  max_tokens=200,
)

# Batch generation — 256 concurrent refund checks share same system prompt cached
outputs = llm.generate([SYSTEM_PROMPT + f"\nUser: Refund order #{oid}" for oid in order_ids], sampling_params)
# Cost: GPU memory 10GB for 7B model with PEFT freezing base isolating updates low-dimensional, throughput 3-5x more concurrent streams per GPU node
```

**SGLang production config for agentic coding loops:**

```python
import sglang as sgl

@sgl.function
def refund_agent_loop(s, codebase_context, order_id):
  # SGLang automatically caches 10k token context in RadixTree 0ms prefill after first
  s += sgl.system(codebase_context)  # OKF bundle policies/concepts 10k tokens cached RadixTree
  s += sgl.user(f"Refund order #{order_id} bundle promotion")
  # Enforces strict JSON grammar at full generation speed FSM in GPU kernel zero-latency constrained decoding
  s += sgl.assistant(sgl.gen("action", regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}'))
  # SGLang reuses system cache across all 100 iterations with 0ms prefill

# Run 100 iterations — system cache reused 0ms prefill each
for order_id in order_ids:
  state = refund_agent_loop.run(codebase_context=okf_bundle, order_id=order_id)
  print(state.get_meta_info("action"))

# Benchmark: Sub-50ms prefill latency reusing cached prefixes reduces TTFT 1200ms→under 45ms multi-turn conversations dramatically reduced VRAM fragmentation radix tree memory management reclaims cold KV blocks dynamically without thrashing GPU memory superior cost-per-token allows serving 3x to 5x more concurrent agent streams per GPU node without degrading response quality
```

**Multi-Tier KV Cache Management 2026:**

- GPU HBM hot cache → CPU RAM warm → NVMe cold → re-compute demand
- Adaptive DHiSparse speculative decoding over load-adaptive KV hierarchy 2026-10-09 combines speculative decoding with hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load at 500K context concurrency 512
- DUAL-BLADE ICDCS 26 tightly couples NVMe GPU DMA trim 30-40% latency
- Google TurboQuant ICLR 26 near-optimal 2-stage vector quantizer PolarQuant + 1-bit QJL quality-neutral KV quantization ~3.5 bits — 438x reduction DeepSeek 390KB→890 bytes
- KVSculpt distillation optimizing small continuous set KVs
- SpeCache KV Prefetching Speculative Cache keeps reduced-precision
- LMCache validated with MTP speculative decoding optional native MTP speculative decoding validated with LMCache MTP acceptance unchanged 0.947 vs 0.952 cached prefix KV speculative decoding with cached prefix preserves score-level equivalence

**Disaggregated serving:**

- Separate prefill compute-bound encoding input and decode memory-bound generating tokens onto different GPU pools prefill high-compute GPUs decode high-memory bandwidth GPUs reduces interference NVIDIA Dynamo full-stack agentic inference optimization tackling same problem hardware side finding ways
- Three themes dominate June 2026 infrastructure speculative decoding reaching production maturity disaggregated serving architectures becoming mainstream multi-tier KV cache management enabling dramatically higher throughput DFlash speculative decoding on Blackwell up to 15x inference speedups

### 11. Observability — Track cached_tokens, KV Hit Rate, TTFT, ITL, Cost per Task

**What to track for 90% cost cut verification:**

- cached_tokens field in response usage block prompt_tokens_details cached_tokens count input tokens served from cache billed at 0.1x — calculate cost uncached*inputPrice + cached*inputPrice*0.1 + completion*outputPrice — first thing check deploying prompt caching is cached_tokens non-zero second subsequent requests yes working zero something wrong either prefix shorter than 1024 tokens or drifting per request
- KV cache hit rate — Inferoa AI measured real agentic coding task for every 100 tokens agent processed only 2.2 computed from scratch rest free 97.8% hit rate — target >90%
- TTFT time-to-first-token target under 500ms chat sub-50ms with RadixAttention reuse cached prefixes reduces TTFT 1200ms→45ms multi-turn — measure 50-80% reduction with prefix/KV caching
- ITL inter-token latency target <30ms — speculative decoding 2-3x throughput when draft accepts roughly 70% proposed tokens — track acceptance rate
- Cost per task — full history 71% completion 1.48M tokens 14.56h per run vs pruning last 5 tool pairs 79% completion 535k tokens — less context better agents — track tokens consumed per task
- Cost per 1k inferences — single GPT-4 API $0.03 10k queries/day 6mo $50k+ fine-tuned SLM running $1500 GPU fraction cost — biggest mistake defaulting LLM API when fine-tuned 3B handles job at 1/50th cost better latency full data control second biggest skipping dataset prep evaluation wondering why hallucinates
- Prompt cache fingerprint stability — track cache invalidation causes timestamps per-user customisation injected system prompt short system prompts sub-1024 tokens — discipline matches prompt cache fingerprinting discipline keep leading content stable cache hits

**OpenTelemetry + ClickHouse + Prometheus:**

```typescript
// Track in Node.js
import { trace } from "@opentelemetry/api";

async function refundTask(orderId) {
  const span = trace.getTracer("agentic").startSpan("refund_task");
  span.setAttribute("order_id", orderId);
  
  const start = Date.now();
  const response = await openai.chat.completions.create({...});
  const ttft = Date.now() - start; // simplified TTFT measurement
  
  const cachedTokens = response.usage.prompt_tokens_details?.cached_tokens || 0;
  const totalPromptTokens = response.usage.prompt_tokens;
  const hitRate = cachedTokens / totalPromptTokens;
  
  span.setAttribute("cached_tokens", cachedTokens);
  span.setAttribute("prompt_tokens", totalPromptTokens);
  span.setAttribute("kv_hit_rate", hitRate);
  span.setAttribute("ttft_ms", ttft);
  span.setAttribute("cost", calculateCost(response.usage, 2.5, 15));
  
  // Send to ClickHouse for analytics
  await clickhouse.insert({
    table: "agent_commerce_events",
    values: [{ event_id: uuid(), timestamp: new Date(), user_id: "user_789", agent_id: "refund-agent", merchant_id: "etsy", event_type: "refund", protocol: "acp", checkout_session_id: orderId, amount: 12900, cached_tokens: cachedTokens, kv_hit_rate: hitRate, ttft_ms: ttft, cost: calculateCost(...) }]
  });
  
  span.end();
}
```

**Dashboard metrics:**

- Input cost 90% off via prompt caching 40-85% TTFT drop
- TTFT 1200ms→45ms via RadixAttention sub-50ms prefill latency reusing cached prefixes
- ITL 2-3x via speculative decoding 70% acceptance up to 15x Blackwell DFlash
- Throughput 3-5x via continuous batching PagedAttention plus RadixTree 3.8-5.2x baseline agent loops 3x-5x more concurrent streams per GPU node
- Token consumption 64% cut via Less Context Better Agents pruning last 5 tool pairs 71%→79% completion 1.48M→535k tokens 14.56h→~4h
- Cost per task 80-90% cut via SLM routing 80% local $0 20% routed LLM + prompt caching + KV reuse + speculative decoding — Notion cut Claude API costs 90% latency up to 85% after restructuring prompts around caching Anthropic case study We've seen customers reduce API costs 80-90% simultaneously improving response times 2-3x

### 12. Database Schema — Cost Tracking Postgres + ClickHouse

**Postgres (cost tracking per task):**

```sql
CREATE TABLE refund_tasks (
  id TEXT PRIMARY KEY,
  order_id TEXT,
  user_id TEXT,
  status TEXT,
  -- Cost tracking
  prompt_tokens INT,
  cached_tokens INT,
  completion_tokens INT,
  kv_hit_rate FLOAT, -- cached_tokens / prompt_tokens
  ttft_ms INT,
  itl_ms FLOAT,
  cost_usd FLOAT,
  model TEXT, -- gpt-5-4, claude-fable-5.1, phi-4-mini self-hosted $0
  cache_hit BOOLEAN,
  speculative_acceptance_rate FLOAT, -- 70% typical
  created_at TIMESTAMP DEFAULT NOW()
);

-- Index for cost analysis
CREATE INDEX idx_refund_tasks_created ON refund_tasks(created_at);
CREATE INDEX idx_refund_tasks_cost ON refund_tasks(cost_usd);
CREATE INDEX idx_refund_tasks_kv_hit ON refund_tasks(kv_hit_rate);

-- Daily cost rollup
CREATE VIEW daily_cost AS
SELECT 
  DATE(created_at) as day,
  COUNT(*) as tasks,
  SUM(prompt_tokens) as total_prompt_tokens,
  SUM(cached_tokens) as total_cached_tokens,
  AVG(kv_hit_rate) as avg_hit_rate,
  SUM(cost_usd) as total_cost,
  SUM(completion_tokens) as total_completion_tokens
FROM refund_tasks
GROUP BY DATE(created_at)
ORDER BY day DESC;
```

**ClickHouse (analytics, observability, high-throughput):**

```sql
CREATE TABLE agent_commerce_events (
  event_id UUID,
  timestamp DateTime,
  user_id String,
  agent_id String,
  merchant_id String,
  event_type Enum('discovery', 'authorization', 'payment', 'fulfillment', 'refund'),
  protocol Enum('acp', 'ap2', 'x402', 'mpp', 'ucp', 'mcp', 'a2a', 'visa_tap', 'prompt_cache', 'kv_cache', 'speculative'),
  checkout_session_id String,
  ap2_mandate_id String,
  amount Int32,
  currency String,
  status String,
  latency_ms Int32,
  -- Cost & latency at scale fields
  prompt_tokens Int32,
  cached_tokens Int32,
  completion_tokens Int32,
  kv_hit_rate Float32,
  ttft_ms Int32,
  itl_ms Float32,
  speculative_acceptance_rate Float32,
  cost_usd Float32,
  model String,
  error String,
  metadata String
) ENGINE = MergeTree() ORDER BY timestamp;

-- Query for 90% cost cut verification
-- SELECT DATE(timestamp) as day, SUM(cost_usd) as total_cost, AVG(kv_hit_rate) as hit_rate, AVG(ttft_ms) as avg_ttft FROM agent_commerce_events WHERE timestamp > NOW() - INTERVAL 7 DAY GROUP BY day ORDER BY day DESC;
-- SELECT protocol, COUNT(*) as events, AVG(kv_hit_rate) as avg_hit_rate, AVG(cost_usd) as avg_cost FROM agent_commerce_events GROUP BY protocol;
-- SELECT model, COUNT(*) as tasks, SUM(cost_usd) as total_cost, AVG(speculative_acceptance_rate) as acceptance FROM agent_commerce_events WHERE protocol = 'speculative' GROUP BY model;
```

**Progress tracking for 6-hour agents:**

```json
// progress.json structured JSON not markdown enables 6-hour agents
{
  "task_id": "refund_12345",
  "status": "working",
  "steps": [
    {"step": "refund_policy_check", "status": "completed", "cached_tokens": 1200, "ttft_ms": 45, "cost": 0.002},
    {"step": "bundle_validation", "status": "completed", "cached_tokens": 1200, "ttft_ms": 42, "cost": 0.001},
    {"step": "acp_checkout", "status": "working", "cached_tokens": 0, "ttft_ms": 1200, "cost": 0.01}
  ],
  "total_cost": 0.013,
  "total_cached_tokens": 2400,
  "total_prompt_tokens": 3600,
  "avg_kv_hit_rate": 0.66,
  "avg_ttft_ms": 429,
  "speculative_acceptance_rate": 0.72,
  "next_action": "verify AP2 mandate and issue SPT"
}
// session_handoff.md for next agent
```

### 13. Anti-Patterns That Kill Cache Hit Rate

**Top 3 patterns that defeat OpenAI prompt cache (and cost you 90% discount):**

1. Timestamps in system prompt "You are responding at [timestamp] [Instructions...]" cache fingerprint changes per request caching never engages strip timestamp if need put in user message or metadata field
2. Per-user customisation injected into system prompt "You are assistant for user [user_id] [Generic instructions...]" same problem system prompt varies per user cache invalidates per request move per-user customisation to user message itself or keep generic in system prompt inject user-specific behaviour via fewer variable points
3. Short system prompts sub-1024 tokens minimum threshold means short prompts don't cache at all if system prompt only 500 tokens not benefiting from prompt caching either pad with useful content additional instructions examples until cross 1024 tokens or rely different cost-reduction techniques

**Additional anti-patterns:**

- Variable content at start prompt — user message 50 tokens at beginning cache key starts here system prompt 1200 tokens invalidated by user variation tool definitions invalidated — fix one-time refactor stable content first variable content last cache key leading portion prompt everything before variable content chance hit cache — GOOD STRUCTURE stable content first BAD STRUCTURE variable content first — if application has bad structure fix one-time refactor pays for itself within hours deployment any meaningful traffic
- Any change leading content different system prompt different tool definitions different leading messages fingerprint changes cache misses — different model parameter cache entries per-model GPT-5.4 cache doesn't serve GPT-5.4-mini request — variable content at start prompt timestamps user IDs session IDs injected system prompt invalidate cache per request most common cause caching not engaging — cache TTL elapsed ~5-10 minutes inactivity same prefix — prompt-template versioning when you update system prompt cache invalidates wholesale plan deploy prompt updates during low-traffic windows so re-warming pain bounded 5-10 min TTL means caches re-populate quickly once new requests start flowing
- Co-location variable content if application has multiple variable elements e.g. user session history + current message put them together at end prompt rather than scattered through reduces accidental invalidations from interleaving variable content into otherwise-stable sections
- Not tracking cached_tokens — first thing check deploying prompt caching is cached_tokens non-zero second subsequent requests yes working zero something wrong either prefix shorter than 1024 tokens or drifting per request
- Ignoring KV cache memory grows with batch size context length primary GPU memory bottleneck — need PagedAttention RadixAttention multi-tier quantization — for every 100 tokens agent processed only 2.2 computed from scratch rest free — without reuse every single tool turn re-evaluates entire 8000-token prefix from scratch saturating GPU memory bandwidth causing massive queue bottlenecks
- Ignoring speculative decoding — decode latency 2x to 3x predictable structured outputs requires careful KV cache memory allocation prevent OOM shared GPU memory — without it ITL high p99 latency
- Full conversation history 71% completion 1.48M tokens 14.56h per run vs pruning last 5 tool pairs 79% completion 535k tokens — less context better agents — without pruning token consumption explodes cost
- Short system prompts sub-1024 tokens — minimum threshold means short prompts don't cache at all — pad with useful content additional instructions examples until cross 1024 tokens or rely different techniques
- Not using constrained decoding — third-party regex wrappers slow generation to crawl — SGLang compiles JSON schemas into compressed finite state machines FSMs directly within GPU decoding kernel generates validated JSON regex-constrained tokens at near full generation speeds without latency penalties — need for refund agent 99.9% JSON valid tool calls

**Production checklist for 90% cut:**

1. Structure prompt stable content first variable content last — system prompt 1200 tokens + tool definitions 400 tokens at beginning stable cached after first hit 0.1x — retrieved context 600 tokens semi-stable cacheable if stable across users — user message 50 tokens variable not cached — minimum 1024 tokens for OpenAI automatic — 128-token boundary additional caching — stable first variable last — cache key leading portion
2. Enable provider prompt caching — OpenAI automatic nothing to deploy cache engages automatically any prompt over 1024 tokens cached portions billed at 10% normal input price savings show in cached_tokens field usage block no markers SDK upgrade required — if system prompt over 1024 tokens stable across requests almost every production app discount already engaging or engaging moment you stabilise leading content — Anthropic explicit cache_control field once top level automatic breakpoint management or individual blocks fine control usage response itemises write read tokens — explicit 1024 Sonnet Opus 2048-4096 model-dependent — cache read 0.1x 90% off write 1.25x 5-min 2x 1-hr 5 minutes refreshed on hit — both now 90% off as of mid-2026 GPT-5.4 GPT-5.5 dropped cached input to $0.50/M against $5/M standard that is 90% matching Anthropic — OpenAI wins operational simplicity matches savings — Anthropic only remaining advantage 1-hour TTL predictable spaced-out workloads one request every 20-30 minutes — most production deployments capture both automatic discount OpenAI marker-driven discount Anthropic both at 90% off — customers reduce API costs 80-90% simultaneously improving response times 2-3x — Notion cut Claude API costs 90% latency up to 85% after restructuring prompts around caching
3. Enable KV cache reuse — top throughput lever KV cache reuse with PagedAttention plus continuous batching vLLM default since 2023 refined 2026 — KV Cache Prefix Alignment structure system prompts so static instructions JSON schemas tool definitions sit at exact beginning context window enables prefix reuse — SGLang Radix-Tree KV Cache Reuse retains shares prefix KV caches across branching multi-turn agent calls eliminating redundant attention re-computation sub-50ms prefill latency reducing TTFT 1200ms→under 45ms up to 5x higher throughput over standard serving dramatically reduces TTFT GPU memory fragmentation under heavy agentic traffic allows serving 3x to 5x more concurrent agent streams per GPU node without degrading quality — for every 100 tokens agent processed only 2.2 computed from scratch rest free — enable_prefix_caching True use_v2_block_manager True max_num_seqs 256
4. Enable speculative decoding — draft model 1.5B generates k=4 tokens quickly target 3.8B verifies parallel single forward pass 70% acceptance 1.5-3x throughput 2x-3x decode latency predictable structured JSON high acceptance code gen loops refund classification — SpecForge v0.3.0 disaggregated colocated DFlash 15x Blackwell NVIDIA Dynamo — combine with cached prefix preserves equivalence gsm8k 0.95 vs 0.96 MTP acceptance unchanged 0.947 vs 0.952 — can combine prompt caching + speculative decoding without accuracy loss — vLLM speculative_model Qwen 2.5 1.5B num_speculative_tokens 4 use_v2_block_manager enable_prefix_caching max_num_seqs 256
5. Prune context Less Context Better Agents — full history 71% completion 1.48M tokens 14.56h → prune last 5 tool pairs 79% completion 535k tokens — keep system prompt stable cached prune conversation history summarize older via cheap model Gemini Flash squashing 10 failures into 1 line hierarchical L0→L3 sliding window anchors incremental summarization every K turns compact at 75% ~24K for 32K local write big data to file keep summary progress.json + session_handoff.md enables 6-hour agents
6. Continuous batching + disaggregated prefill/decode — batching standard fix throughput one weight read serves every request in batch enemy of latency continuous batching balances — disaggregated serving architectures becoming mainstream separate prefill compute-bound and decode memory-bound onto different GPU pools prefill high-compute GPUs decode high-memory bandwidth GPUs reduces interference — agentic workloads long prefill 8000 tokens codebase repeated many times + short decode tool call JSON 50 tokens — disaggregating prevents long prefill blocking short decodes queue bottlenecks
7. Multi-tier KV cache + quantization + compression — hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load instead fixed resident/evicted split Adaptive DHiSparse speculative decoding over load-adaptive KV hierarchy 2026-10-09 combines speculative decoding with hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load at 500K context concurrency 512 — DeepSeek cut memory cost cached token from roughly 390,000 bytes to 890 bytes 438x reduction just under 3 years optional native MTP speculative decoding validated with LMCache MTP acceptance unchanged 0.947 vs 0.952 cached prefix KV speculative decoding with cached prefix preserves score-level equivalence — Google TurboQuant ICLR 26 near-optimal 2-stage vector quantizer PolarQuant + 1-bit QJL quality-neutral KV quantization ~3.5 bits — KVSculpt distillation optimizing small continuous set KVs DUAL-BLADE ICDCS 26 tightly couples NVMe GPU DMA trim 30-40% latency KV Prefetching Speculative Cache SpeCache keeps reduced-precision multi-tier GPU HBM hot cache → CPU RAM warm → NVMe cold → re-compute demand Cache Is The Model KV cache hit rate Inferoa AI measured real agentic coding task for every 100 tokens agent processed only 2.2 computed from scratch rest free — quantization 50% to 90% cost reductions input tokens alongside 40% to 85% drop TTFT latency
8. Constrained decoding structured outputs at full speed — unlike third-party regex wrappers slow generation to crawl SGLang compiles JSON schemas into compressed finite state machines FSMs directly within GPU decoding kernel generates validated JSON regex-constrained tokens at near full generation speeds without latency penalties zero-latency constrained decoding — SGLang s += sgl.assistant(sgl.gen("action", regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}')) enforces strict JSON grammar at full generation speed SGLang reuses system cache across all 100 iterations with 0ms prefill — for refund agent need 99.9% JSON valid tool calls eliminates parsing errors without latency penalty
9. Model routing SLM drafts LLM verifies SLM handles 80% — routing SLM classifies incoming query routes to either local SLM for simple queries or LLM API for complex ones cuts cost dramatically because most production queries tend simple — LLM as planner SLM as executor agentic systems LLM decomposes task SLM handles specific subtasks entity extraction slot filling retrieval filtering — speculative decoding SLM generates draft token sequences quickly LLM verifies accepts corrects well-validated technique speeding up LLM inference without quality loss Google DeepMind published research demonstrating 2-3x speedups — for your refund agent SmolLM2 1.7B or Qwen 2.5 1.5B draft → Phi-4 Mini 3.8B target → only 20% complex multi-bundle routed to GPT-5.4 via A2A — 80% local cost $0 vs $0.03 API — single GPT-4 API $0.03 Run 10k queries/day 6 months over $50k Fine-tuned SLM running $1500 GPU fraction cost data never leaving servers biggest mistake defaulting LLM API when fine-tuned 3B handles job at 1/50th cost better latency full data control
10. Observability track cached_tokens KV hit TTFT ITL cost per task — OpenAI returns cached_tokens field response usage block prompt_tokens_details cached_tokens count input tokens served from cache billed at 0.1x calculate cost def calculate_openai_cost usage input_price output_price uncached*input_price/1M + cached*input_price*0.1/1M + completion*output_price/1M return cost first thing check deploying prompt caching is cached_tokens non-zero second subsequent requests yes working zero something wrong either prefix shorter than 1024 tokens or drifting per request — Anthropic usage itemises cache_creation_input_tokens cache_read_input_tokens — track TTFT time-to-first-token target under 500ms chat sub-50ms with RadixAttention reuse cached prefixes reduces TTFT 1200ms→under 45ms multi-turn — track KV cache hit rate Inferoa AI measured 2.2% computed from scratch 97.8% free agentic coding task target >90% — track speculative decoding acceptance rate ~70% typical 1.5-3x throughput payoff — track cost per task 71%→79% completion + 1.48M→535k tokens + 14.56h→~4h per run Less Context Better Agents measure improvement — providers can bill repeated input at ~10% normal price OpenAI GPT-5.5 cached input $0.50/MTok vs $5.00 — Anthropic bills cache writes at 1.25x normal input 5-min TTL 2x 1-hour TTL — provider differences mid-2026 snapshot OpenAI automatic older models no write charge GPT-5.5 $0.50 cached vs $5.00 normal input per MTok 90% discount From GPT-5.6 writes — Anthropic vs OpenAI prompt caching complete 2026 comparison We've seen customers reduce API costs 80-90% simultaneously improving response times 2-3x — database schema Postgres refund_tasks id order_id user_id status prompt_tokens cached_tokens completion_tokens kv_hit_rate ttft_ms itl_ms cost_usd model cache_hit speculative_acceptance_rate created_at daily_cost view ClickHouse agent_commerce_events event_id timestamp user_id agent_id merchant_id event_type discovery authorization payment fulfillment refund protocol acp ap2 x402 mpp ucp mcp a2a visa_tap prompt_cache kv_cache speculative checkout_session_id ap2_mandate_id amount currency status latency_ms prompt_tokens cached_tokens completion_tokens kv_hit_rate ttft_ms itl_ms speculative_acceptance_rate cost_usd model error metadata — progress tracking 6-hour agents progress.json structured JSON not markdown steps cached_tokens ttft_ms cost total_cost total_cached_tokens total_prompt_tokens avg_kv_hit_rate avg_ttft_ms speculative_acceptance_rate next_action session_handoff.md next agent

**Combined 90% cut stack that actually ships summary:** Layer 1 Prompt Caching provider 90% off input stable system prompt 1200 tokens + tool definitions 400 tokens at beginning variable user message at end minimum 1024 tokens 128-token boundary TTL 5-10 min warm via synthetic request at 9 AM business-hours cache_creation 1.25x Anthropic vs no write premium OpenAI cache_read 0.1x both saves 80-90% input cost 40-85% TTFT Layer 2 KV Cache Reuse inference engine 3-5x throughput PagedAttention v2 non-contiguous pages eliminates fragmentation sharing prefix across requests + RadixAttention radix tree automatic match across branching multi-turn agent calls zero re-computation sub-50ms prefill TTFT 1200ms→45ms 3.8-5.2x baseline throughput agent loops 3x-5x more concurrent streams per GPU node sub-50ms prefill latency reusing cached prefixes Cache Is The Model 97.8% free Layer 3 Speculative Decoding 2-3x ITL up to 15x Blackwell draft model 1.5B generates k=4 tokens quickly target 3.8B verifies parallel single forward pass 70% acceptance 1.5-3x throughput 2-3x decode latency predictable structured JSON outputs high acceptance code gen loops refund classification SpecForge v0.3.0 disaggregated colocated DFlash 15x Blackwell NVIDIA Dynamo combine with cached prefix preserves equivalence gsm8k 0.95 vs 0.96 MTP acceptance unchanged 0.947 vs 0.952 Layer 4 Less Context Better Agents 64% token cut + 8% accuracy gain full history 71% completion 1.48M tokens 14.56h → prune last 5 tool pairs 79% completion 535k tokens keep system prompt stable cached prune conversation history summarize older via cheap model Gemini Flash squashing 10 failures into 1 line hierarchical L0→L3 sliding window anchors incremental summarization every K turns compact at 75% ~24K for 32K local write big data to file keep summary progress.json + session_handoff.md enables 6-hour agents Layer 5 Model Routing 80/20 SLM handles 80% local $0 SLM classifies routes local SLM simple queries LLM API complex cuts cost dramatically most production queries tend simple LLM planner SLM executor speculative decoding SLM drafts LLM verifies 2-3x speedups Google DeepMind fine-tuned 3B handles job at 1/50th cost better latency full data control vs GPT-4 $0.03 10k/day 6mo $50k+ vs $1500 GPU fraction Total Input cost 90% off via prompt caching + TTFT 80% off via RadixAttention + ITL 2-3x via speculative decoding + throughput 5x via continuous batching + PagedAttention + tokens 64% off via pruning + 80% queries local $0 via SLM routing = ~90% total bill cut Notion case study 90% cost 85% latency simultaneous 80-90% API costs 2-3x response times

---
*Module: Cost & Latency at Scale — Speculative Decoding, KV-Cache, Prompt Caching 90% Cut — Part of Advanced Agentic AI Curriculum — v1.0 — October 2026*
*Reference: Prompt caching cut API costs 90% most developers still not using correctly as of Oct 26 2026 GPT-6 Astra Claude Fable 5.1 Gemini 4 Argon each expose caching layer cut input-token costs 90%+ OpenAI cached input up to 95% less than uncached depending model Claude Fable 5.1 explicit cache_control 2048-4096 model-dependent 90% off 0.1x 1.25x 5-min / 2x 1-hr 5 minutes refreshed on hit GPT-6 Astra automatic Anthropic most Anthropic models OpenAI GPT-5.6 later bill cache read tenth input rate cache read tokens billed at 0.1 times base input rate 90% reduction while writing to cache costs 1.25 times base cache holds 5-min sliding window default Anthropic docs specific size discount cache read 0.1x 90% reduction write 1.25x 5-min TTL 2x 1-hr Anthropic prompt caching docs OpenAI applies caching automatically on GPT-5.6 later bills writes at 1.25 times uncached inp repeated portion billed roughly one-tenth normal input rate application prompts mostly static context translates input-cost reduction approaching 90 percent no change model output product behavior figures per million tokens current as Aug 2026 provider pricing changes often confirm against live pricing page before committing budget cached portions billed at 10% normal input price 90% discount savings show in cached_tokens field response usage block as of mid-2026 both providers same 90% discount cached input tokens discount cached input 90% off 0.1x 90% off 0.1x In 2026 prompt caching KV cache reuse offers up to 90% discounts input tokens Prompt Caching OpenAI Anthropic typically automatic ephemeral 5-15 min TTL caches KV state prefix conversation System prompt + previous turns automatically if prefix matches exactly usually >1024 tokens discounts ~50% OpenAI to ~90% Anthropic Both Anthropic OpenAI newest flagships now bill cached reads at 10% standard input rate 90% discount started as Anthropic signature got matched quietly when GPT-5.4 launched Quick Specs Anthropic vs OpenAI Prompt Caching Discount cache read 90% 0.1x input 50% gpt-4o gpt-4.1 / 90% gpt-5.4 gpt-5.5 GPT-5.4 and GPT-5.5 dropped cached input to $0.50/M against $5/M standard that is 90% matching Anthropic read rate tokens as of Aug 2026 OpenAI publishes same shape cached input on gpt-5.5 at $0.50 against $5.00 standard Developers see 90 percent discount advertised assume applies whole request then wonder why invoice barely moved Anthropic makes caching explicit You add cache control field either once top level automatic breakpoint management or individual blocks fine control usage response itemises write read tokens OpenAI appl Prompt Caching Architecture Slashing LLM Input Token Costs by 50 Percent In 2026 foundation model providers Anthropic Claude OpenAI DeepSeek open-weight inference engines vLLM SGLang leverage Key-Value KV cache state persistence eliminate redundant compute By caching compiled prompt prefixes in GPU memory or edge caches engineering teams achieve 50% to 90% cost reductions input tokens alongside 40% to 85% drop Time-to-First-Token TTFT latency Anthropic Claude API explicit cache_control 1024 tokens Sonnet/Opus We've seen customers reduce API costs 80-90% simultaneously improving response times 2-3x Cost Efficiency High Frequency Anthropic 90% discount beats 50% cache-heavy workloads Prompt caching 90% discount most AI teams never claim PUBLISHED 2026-07-10 UPDATED 2026-10-27 providers can bill repeated input at ~10% normal price OpenAI GPT-5.5 cached input $0.50/MTok vs $5.00 Provider differences mid-2026 snapshot OpenAI automatic older models no write charge GPT-5.5 $0.50 cached vs $5.00 normal input per MTok 90% discount From GPT-5.6 writes OpenAI prompt caching explained automatic free to enable 90% off cached input tokens DEV Community OpenAI prompt caching easiest LLM cost-reduction technique deploy because nothing to deploy cache engages automatically any prompt over 1024 tokens cached portions billed at 10% normal input price 90% discount savings show in cached_tokens field response usage block No markers attach no SDK upgrade required no caller-side configuration If application has system prompt over 1024 tokens stable across requests which is almost every production application discount already engaging or engaging moment you stabilise leading content pairs with Anthropic prompt caching deep dive same underlying concept similar discount different implementation parent guide AI API caching broader caching strategy OpenAI-specific deep dive What it caches and why Like Anthropic OpenAI prompt cache is provider-side prefix-attention caching When request arrives with prompt prefix provider has seen recently OpenAI serves cached attention state rather than recomputing from scratch Response still generated token-by-token what gets discounted input-token billing cached portion Mechanism conceptually simple model has to encode input prompt into internal representation before generating response For long stable system prompts often thousands tokens instructions retrieved context tool definitions encoding step non-trivial compute If same prefix shows repeatedly provider can reuse cached representation OpenAI passes savings as 90% input-token discount cached portion Catch opaque you can't directly inspect what's cached you can only observe effects via cached_tokens field returned response usage block provider decides what to cache for how long you control whether prompts are cacheable by keeping prefix stable pricing math Token category Price multiplier vs base input price Notes Normal input uncached 1.0x Standard input pricing Cached input 0.1x 90% discount applies automatically prompts ≥1024 tokens Output normal output pricing Unchanged Concretely GPT-5.5 $5.00/M input → $0.50/M cached $4.50/M saving every cached token GPT-5.4 $2.50/M → $0.25/M cached GPT-5.4 Mini $0.75/M → $0.075/M cached No write premium Unlike Anthropic 25%-or-100% write premium first writes OpenAI doesn't charge extra cache writes First request pays normal input price subsequent cache hits pay 0.1x Break-even immediate every cache hit pure saving Worked savings typical workload Assume customer support chatbot built GPT-5.4 50000 requests/day Average prompt 1500 tokens 1400-token stable system prompt + 100-token user message Average output 200 tokens Without caching 50000×(1500×$2.50+200×$15)/1M = $337.50/day With caching assume 90% input tokens hit cache after warm-up Cached input 50000×1400×0.9×$0.25/1M = $15.75/day Uncached input 50000×(1400×0.1+100)×$2.50/1M = $30/day Output 50000×200×$15/1M = $150/day Total $195.75/day Net saving ~42% total bill or ~85% input-token portion Workloads longer outputs see smaller total bill reduction because output isn't discounted workloads longer inputs see bigger total savings VERIFY founder replace worked example with one drawn from real Prism customer or representative aggregated data at current OpenAI pricing illustrative numbers reasonable worth grounding production data 1024-token minimum + 128-token boundary Two structural rules determine whether caching engages Minimum prompt length 1024 tokens Prompts shorter than this aren't cached Most production applications have system prompts comfortably cross threshold toy examples short tool-call workflows often don't 128-token boundary additional caching Beyond 1024-token base OpenAI caches additional content 128-token chunks practical implication if prompt 2200 tokens OpenAI may cache around 2176 tokens closest 128-token boundary below prompt length treat remaining ~24 tokens as uncached Strategic implication structure your prompt with stable content first variable content last Cache key leading portion prompt everything before variable content has chance hit cache GOOD STRUCTURE stable content first System prompt 1200 tokens ← cached after first hit Tool definitions 400 tokens ← cached after first hit Retrieved context variable 600t ← cacheable if stable across users User message variable 50 tokens ← not cached BAD STRUCTURE variable content first User message 50 tokens ← cache key starts here System prompt 1200 tokens ← invalidated by user message variation Tool definitions 400 tokens ← invalidated If application has bad structure fix one-time refactor pays for itself within hours deployment any meaningful traffic Reading cache hits from response OpenAI returns cached-tokens count response usage block from openai import OpenAI client = OpenAI() response = client.chat.completions.create model=gpt-5-4 messages=[role system content ...(long stable system prompt)... role user content How do I reset my password?] print(response.usage) CompletionUsage(prompt_tokens=1532 completion_tokens=87 total_tokens=1619 prompt_tokens_details=PromptTokensDetails(cached_tokens=1408 1408 tokens hit cache audio_tokens=0) cached_tokens field count input tokens served from cache billed at 0.1x Total cost calculation def calculate_openai_cost usage input_price_per_million output_price_per_million cached = usage.prompt_tokens_details.cached_tokens uncached = usage.prompt_tokens - cached cost = uncached*input_price_per_million/1_000_000 + cached*input_price_per_million*0.1/1_000_000 + usage.completion_tokens*output_price_per_million/1_000_000 return cost First thing check when deploying prompt caching is cached_tokens non-zero second subsequent requests If yes caching working If zero something wrong either prefix shorter than 1024 tokens or drifting per request TTL when cache expires OpenAI doesn't officially publish precise TTL Empirically cache stays warm approximately 5-10 minutes inactivity Active workloads consistent traffic see continuous cache hits because each request resets warming window Workloads hits every few minutes see consistent caching Workloads hits every hour more typically see cache expire between requests pay full input price each time Production implications Continuous traffic → cache stays warm continuously Best case Bursty traffic e.g. concentrated during business hours → caches expire overnight Each morning first requests pay full price cache warms within few requests subsequent traffic hits warm cache Acceptable Sparse traffic e.g. one request every 30 minutes → cache expires between requests Caching effectively never engages Other techniques response-level caching model-tier routing carry more weight sparse workloads Lack explicit TTL control one structural difference vs Anthropic Anthropic offers explicit 1-hour extended-TTL option with higher write premium OpenAI doesn't expose TTL as caller-side dial What invalidates cache Cache match requires byte-exact match leading prompt content Things that invalidate Any change leading content Different system prompt different tool definitions different leading messages Fingerprint changes cache misses Different model parameter Cache entries per-model GPT-5.4 cache doesn't serve GPT-5.4-mini request Variable content at start prompt Timestamps user IDs session IDs injected into system prompt invalidate cache per request Most common cause caching not engaging Cache TTL elapsed ~5-10 minutes inactivity same prefix Things that don't invalidate Variable user messages at end Cache key leading content user message variable suffix doesn't affect caching Different sampling parameters temperature top_p max_tokens Affect generation not cache match Different request IDs metadata headers Not part cache key Discipline matches broader prompt cache fingerprinting discipline keep leading content stable cache hits Production patterns maximise hit rate shapes that work in production Stable system prompt + retrieved context + user message canonical pattern System prompt and tool definitions go at very start prompt stable retrieved context follows semi-stable often cached after warm-up user message at end variable never cached Almost every production LLM workload looks like this Prompt-template versioning When you update system prompt cache invalidates wholesale Plan deploy prompt updates during low-traffic windows so re-warming pain bounded 5-10 minute TTL means caches re-populate quickly once new requests start flowing Co-location variable content If application has multiple variable elements e.g. user session history + current message put them together at end prompt rather than scattered through Reduces accidental invalidations from interleaving variable content into otherwise-stable sections Cache-warming predictable workloads If traffic pattern predictable e.g. business-hours support chatbot ramps up at 9 AM fire synthetic warm-up request at start active window populate cache First real user request hits warmed cache instead paying full input price Anti-patterns Three patterns that defeat OpenAI prompt cache Timestamps in system prompt You are responding at [timestamp] [Instructions...] Cache fingerprint changes per request Caching never engages Strip timestamp if need put in user message or metadata field Per-user customisation injected into system prompt You are assistant for user [user_id] [Generic instructions...] Same problem system prompt varies per user cache invalidates per request Move per-user customisation to user message itself or keep generic in system prompt inject user-specific behaviour via fewer variable points Short system prompts sub-1024 tokens Minimum threshold means short prompts don't cache at all If system prompt only 500 tokens not benefiting from prompt caching Either pad with useful content additional instructions examples until cross 1024 tokens or rely different cost-reduction techniques OpenAI vs Anthropic surprising near-tie For most prompt-caching era conventional wisdom Anthropic for max savings 90% OpenAI for simplicity 50% That conventional wisdom now wrong As of mid-2026 both providers offer same 90% discount cached input tokens difference now structural not magnitude Feature Discount cached input 90% off 0.1x 90% off 0.1x Write premium None 5-min cache +25% 1.25x base 1-hour cache +100% 2x base Default TTL ~5-10 min empirical 5 min Custom TTL Not exposed 1-hour extended TTL option with higher write premium Caller-side config None automatic Explicit cache_control marker required Minimum prompt length 1024 tokens few hundred tokens with marker OpenAI now wins operational simplicity AND matches on savings No marker discipline no write premium no SDK changes and 90% discount previously Anthropic-exclusive Right default for teams that want discount without engineering investment Anthropic only remaining structural advantage explicit 1-hour TTL option For predictable but spaced-out workloads e.g. one request every 20-30 minutes against same prompt Anthropic 1-hour cache +2x write premium can beat OpenAI ~5-10 minute auto-cache that may expire between requests For typical continuous-traffic workloads difference invisible Most production deployments running both providers which is most production deployments capture both automatic discount OpenAI traffic marker-driven discount Anthropic traffic both at 90% off Deeper comparison provider-native caching glossary How Prism handles OpenAI prompt caching Prism request handler fully transparent OpenAI automatic caching SGLang RadixAttention Optimizing KV Cache Multi-Turn Agentic Production Pipelines 2026 velocity innovation LLM Infrastructure High-Performance Serving transforming how digital builders software engineers founders construct modern software architecture Selecting optimal tools workflow patterns essential unlocking extreme operational leverage reducing latency maximizing ROI Executive Summary Core Findings Radix-Tree KV Cache Reuse Retains shares prefix KV caches across branching multi-turn agent calls eliminating redundant attention re-computation Constrained Decoding Structured Outputs Generates validated JSON regex-constrained tokens at near full generation speeds without latency penalties Up to 5x Higher Throughput over Standard Serving Dramatically reduces Time-to-First-Token GPU memory fragmentation under heavy agentic traffic 1 KV Cache Crisis Multi-Agent Workflows Modern agentic architectures involve long multi-turn interactions initial prompt 8000 tokens codebase context schema definitions tool instructions followed by dozens iterative tool calls traditional inference engines every single tool turn re-evaluates entire 8000-token prefix from scratch saturating GPU memory bandwidth causing massive queue bottlenecks RadixAttention Prefix Tree Breakthrough SGLang introduces RadixAttention which organizes Key-Value KV cache as radix tree When new request arrives that shares identical system prompt documentation block or previous turn history SGLang reuses existing KV tensor in memory with zero re-computation Zero-Latency Constrained Decoding Unlike third-party regex wrappers slow generation to crawl SGLang compiles JSON schemas into compressed finite state machines FSMs directly within GPU decoding kernel High-Performance SGLang Programmatic Agent Call import sglang as sgl @sgl.function def agent_loop(s codebase_context user_goal) SGLang automatically caches 10000 token context in RadixTree s += sgl.system(codebase_context) s += sgl.user(user_goal) Enforces strict JSON grammar at full generation speed s += sgl.assistant(sgl.gen("action" regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}')) SGLang reuses system cache across all 100 iterations with 0ms prefill 2 Benchmark Matrix SGLang vs vLLM Production Empirical throughput testing 8x H100 GPU clusters running Llama 3.3 DeepSeek-V3 workloads Sub-50ms Prefill Latency Reusing cached prefixes reduces Time-to-First-Token 1200ms to under 45ms multi-turn conversations Dramatically Reduced VRAM Fragmentation Radix tree memory management reclaims cold KV blocks dynamically without thrashing GPU memory Superior Cost-Per-Token Allows serving 3x to 5x more concurrent agent streams per GPU node without degrading response quality Comprehensive Frontier Benchmark Architectural Matrix Metric SGLang RadixAttention vLLM PagedAttention v2 TensorRT-LLM Multi-Turn Cache Reuse Automatic Radix Tree Match Prefix Caching Limited Manual Buffer Management Constrained JSON Decoding Speed Native Full Generation Speed Outlines Slow Fallback Requires Custom Engine Plugins Throughput under Agent Loops 3.8x -5.2x baseline 1.8x-2.4x baseline 2.1x-3.0x baseline Setup Developer Ergonomics Pythonic Intuitive Standardized Popular Complex C++ Compilation FAQ What is RadixAttention why matter RadixAttention stores previously computed prompt token caches in tree structure When agent sends prompt with same system instructions chat history GPU skips re-computing those tokens reducing latency near zero How does SGLang compare vLLM While vLLM pioneered PagedAttention general throughput SGLang RadixAttention specifically optimized multi-turn agents code generation loops structured JSON outputs delivering superior speed complex agent pipelines Can SGLang run consumer NVIDIA GPUs Yes SGLang runs efficiently any modern NVIDIA GPU RTX 3090 4090 A6000 A100 H100 Linux CUDA Published 2026-10-12, Speculative Decoding KV Cache Optimization Agentic AI Latency 2026 Multi-Turn Memory Mixed Precision Safer Rollouts Serving Catches Up Agentic Workloads edition LLM Inference Digest covers new developments 2026-10-07 to 2026-10-14 arXiv vLLM Hugging Face blogs Together AI Modal Latent Space Adaptive DHiSparse Speculative Decoding over Load-Adaptive KV Hierarchy 2026-10-09 combines speculative decoding with hierarchical sparse KV cache dynamically shifts entries between GPU memory overflow based on load instead fixed resident/evicted split At 500K context concurrency 512 LLM Inference 2026 Speed Cost Optimization Guide TL;DR LLM Inference at a Glance 2026 TTFT under 500ms chat sustained tokens-per-second per user GPU memory headroom Top throughput lever KV cache reuse with PagedAttention plus continuous batching vLLM default since 2023 refined through 2026 Speculative decoding payoff 1.5x to 3x throughput when draft model accepts roughly 70 percent proposed tokens KV cache memory grows with batch size context length primary GPU memory SGLang RadixAttention Optimizing KV Cache Multi-Turn Agentic Production Pipelines Radix-Tree KV Cache Reuse Retains shares prefix KV caches across branching multi-turn agent calls eliminating redundant attention re-computation Constrained Decoding Structured Outputs Generates validated JSON regex-constrained tokens at near full generation speeds without latency penalties Up to 5x Higher Throughput over Standard Serving Dramatically reduces Time-to-First-Token GPU memory fragmentation under heavy agentic traffic 1 KV Cache Crisis Multi-Agent Workflows Modern agentic architectures involve long multi-turn interactions initial prompt 8000 tokens codebase context schema definitions tool instructions followed by dozens iterative tool calls traditional inference engines every single tool turn re-evaluates entire 8000-token prefix from scratch saturating GPU memory bandwidth causing massive queue bottlenecks RadixAttention Prefix Tree Breakthrough SGLang introduces RadixAttention which organizes Key-Value KV cache as radix tree When new request arrives that shares identical system prompt documentation block or previous turn history SGLang reuses existing KV tensor in memory with zero re-computation Zero-Latency Constrained Decoding Unlike third-party regex wrappers slow generation to crawl SGLang compiles JSON schemas into compressed finite state machines FSMs directly within GPU decoding kernel High-Performance SGLang Programmatic Agent Call import sglang as sgl @sgl.function def agent_loop(s codebase_context user_goal) SGLang automatically caches 10000 token context in RadixTree s += sgl.system(codebase_context) s += sgl.user(user_goal) Enforces strict JSON grammar at full generation speed s += sgl.assistant(sgl.gen("action" regex=r'\{"tool": "(read|write|test)", "file": "[^"]+"\}')) SGLang reuses system cache across all 100 iterations with 0ms prefill 2 Benchmark Matrix SGLang vs vLLM Production Empirical throughput testing 8x H100 GPU clusters running Llama 3.3 DeepSeek-V3 workloads Sub-50ms Prefill Latency Reusing cached prefixes reduces Time-to-First-Token 1200ms to under 45ms multi-turn conversations Dramatically Reduced VRAM Fragmentation Radix tree memory management reclaims cold KV blocks dynamically without thrashing GPU memory Superior Cost-Per-Token Allows serving 3x to 5x more concurrent agent streams per GPU node without degrading response quality Comprehensive Frontier Benchmark Architectural Matrix Metric SGLang RadixAttention vLLM PagedAttention v2 TensorRT-LLM Multi-Turn Cache Reuse Automatic Radix Tree Match Prefix Caching Limited Manual Buffer Management Constrained JSON Decoding Speed Native Full Generation Speed Outlines Slow Fallback Requires Custom Engine Plugins Throughput under Agent Loops 3.8x -5.2x baseline 1.8x-2.4x baseline 2.1x-3.0x baseline Setup Developer Ergonomics Pythonic Intuitive Standardized Popular Complex C++ Compilation FAQ What is RadixAttention why matter RadixAttention stores previously computed prompt token caches in tree structure When agent sends prompt with same system instructions chat history GPU skips re-computing those tokens reducing latency near zero How does SGLang compare vLLM While vLLM pioneered PagedAttention general throughput SGLang RadixAttention specifically optimized multi-turn agents code generation loops structured JSON outputs delivering superior speed complex agent pipelines Can SGLang run consumer NVIDIA GPUs Yes SGLang runs efficiently any modern NVIDIA GPU RTX 3090 4090 A6000 A100 H100 Linux CUDA Published 2026-10-12 Speculative Decoding and Multi-Model Routing Scaling High-Throughput Enterprise LLM Inference 2026 High-throughput enterprise Generative AI inference 2026 requires software architects combine speculative decoding dynamic model routing token telemetry proxies reduce p99 latency cloud compute overhead Reduces decode latency by 2x to 3x predictable structured outputs requires careful KV cache memory allocation prevent out-of-memory OOM shared GPU memory Enterprise serving environments deploy unified memory managers such as PagedAttention abstract From 390 KB to 890 Bytes how did DeepSeek cut memory cost cached token from roughly 390000 bytes to 890 bytes — 438x reduction just under three years what did each step cost and buy optional native MTP speculative decoding validated with LMCache MTP acceptance rate unchanged 0.947 vs 0.952 cached prefix KV speculative decoding with cached prefix preserves score-level equivalence gsm8k 0.95 computed vs 0.96 retrieved within sampling error leaves draft laye Co-Designing AI Models Using Speculative Decoding Faster LLM Inference Guideline 1 Increase speculative decoding draft length to push GEMMs into compute-bound region without increasing KV cache capacity pressure For reasoning agentic workloads attention tends dominate execution time throughput-oriented region Inference Optimization Wave How AI Infrastructure Getting Faster Cheaper Complex Three themes dominate June 2026 infrastructure landscape speculative decoding reaching production maturity disaggregated serving architectures becoming mainstream multi-tier KV cache management enabling dramatically higher throughput DFlash speculative decoding on Blackwell achieving up to 15x inference speedups NVIDIA own Dynamo framework which targets full-stack agentic inference optimization tackling same problem from hardware side finding ways Cache Is Model KV Cache Optimization PhantomByte That is KV cache hit rate Inferoa AI measured during real agentic coding task For every 100 tokens agent processed only 2.2 computed from scratch rest were free arXiv 2606.10209 Less Context Better Agents tested GPT-5 configurations 50-task enterprise expense itemization benchmark Full conversation history 71.0% task completion 1480996 tokens consumed 14.56 hours per run Pruning to last 5 tool call/response pairs 79.0% completion 535274 toke LocalHouseLLM Research KV Cache Optimization Large Language Model Google TurboQuant ICLR26 presented near-optimal 2-stage vector quantizer PolarQuant + 1-bit QJL achieving quality-neutral KV quantization at ~3.5 bits Latest 2026 includes KVSculpt ArXiv26 distillation approach optimizing small continuous set KVs DUAL-BLADE ICDCS26 tightly couples NVMe GPU DMA trim 30-40% latency KV Prefetching Speculative Cache SpeCache Keeps reduced-precision How Can Engineers Implement Speculative Decoding Optimization Achieve Production-Grade Inference Speeds 2026 As of September 2026 industry moved beyond simple draft-target pairs toward unified stacks like SpecForge v0.3.0 allow disaggregated colocated deployment strategies Latency High Sequential Low Parallelized Tools like vLLM AWS Trainium evolved support configurations by optimizing KV cache management for both draft target models memory footprint KV cache significant concern storing two sets hidden Architecting Production-Grade Agentic AI Systems Memory Orchestration Latency Optimization 3 Inference Optimization Latency Engineering Prefix / KV Caching Time-To-First-Token TTFT 50% – 80% reduction Low Prompt structuring Speculative Decoding Inter-Token Latency ITL 2x – 3x throughput Medium vLLM / TensorRT-LLM config KV Cache Prefix Alignment Structure system prompts so static instructions JSON schemas tool definitions sit at exact beginning context window Speculative Decoding Pair lightwei Fastest LLM Inference Lowest Latency Most Tokens per Second software techniques speculative decoding FlashAttention Flash-Decoding CUDA graphs tensor parallelism disaggregated prefill decode KV cache placement Batching standard fix throughput one weight read serves every request in batch enemy of la, LLM Prompt Caching Cut API Costs 90% 2026 as of Oct 26 2026 most developers still not using it correctly GPT-6 Astra Claude Fable 5.1 Gemini 4 Argon each expose caching layer can cut input-token costs by 90% or more OpenAI says cached input can cost up to 95% less than uncached input depending on model Claude Fable 5.1 Anthropic Explicit cache_control 2048-4096 model-dependent 90% off 0.1x 1.25x 5-min / 2x 1-hr 5 minutes refreshed on hit GPT-6 Astra OpenAI Automatic Prompt Caching 90% Bill Cut You Never Turned On most Anthropic models OpenAI GPT-5.6 later bill cache read tenth input rate Anthropic docs specific size discount cache read tokens billed at 0.1 times base input rate 90% reduction while writing to cache costs 1.25 times base cache holds 5-minute sliding window default Anthropic prompt caching docs OpenAI applies caching automatically on GPT-5.6 later bills writes at 1.25 times uncached inp Prompt Caching 90% LLM Discount Most Apps Skip When configured correctly repeated portion prompt billed at roughly one-tenth normal input rate For application whose prompts mostly static context translates into input-cost reduction approaching 90 percent no change model output product behavior figures below per million tokens current as Aug 2026 provider pricing changes often confirm against live pricing page before committing budget OpenAI prompt caching explained automatic free to enable 90% off cached input tokens cached portions prompt billed at 10% normal input price 90% discount savings show in cached_tokens field response usage block As of mid-2026 both providers offer same 90% discount cached input tokens Discount cached input 90% off 0.1x 90% off 0.1x Hidden Cost Intelligence Token Pricing Cache Hits 2026 In 2026 prompt caching KV Cache reuse offers up to 90% discounts input tokens Prompt Caching OpenAI Anthropic typically automatic ephemeral 5-15 min TTL caches KV state prefix conversation System prompt + previous turns automatically if prefix matches exactly usually >1024 tokens Discounts ~50% OpenAI to ~90% Anthropic Anthropic vs OpenAI Prompt Caching 2026 Cost Math + 3 Cache-Miss Fixes Both Anthropic OpenAI newest flagships now bill cached reads at 10% standard input rate 90% discount started as Anthropic signature got matched quietly when GPT-5.4 launched Quick Specs Anthropic vs OpenAI Prompt Caching Discount cache read 90% 0.1x input 50% gpt-4o gpt-4.1 / 90% gpt-5.4 gpt-5.5 GPT-5.4 and GPT-5.5 dropped cached input to $0.50/M against $5/M standard that is 90% matching Anthropic read rate What Prompt Caching Means When AI Coding Bill Arrives tokens as of Aug 2026 OpenAI publishes same shape cached input on gpt-5.5 at $0.50 against $5.00 standard Developers see 90 percent discount advertised assume applies whole request then wonder why invoice barely moved Anthropic makes caching explicit You add cache control field either once top level automatic breakpoint management or individual blocks fine control usage response itemises write read tokens OpenAI appl Prompt Caching Architecture Slashing LLM Input Token Costs by 50 Percent In 2026 foundation model providers Anthropic Claude OpenAI DeepSeek open-weight inference engines vLLM SGLang leverage Key-Value KV cache state persistence eliminate redundant compute By caching compiled prompt prefixes in GPU memory or edge caches engineering teams achieve 50% to 90% cost reductions input tokens alongside 40% to 85% drop Time-to-First-Token TTFT latency Anthropic Claude API explicit cache_control 1024 tokens Sonnet/Opus We've seen customers reduce API costs 80-90% simultaneously improving response times 2-3x Cost Efficiency High Frequency Anthropic 90% discount beats 50% cache-heavy workloads Prompt caching the 90% discount most AI teams never claim PUBLISHED 2026-07-10 UPDATED 2026-10-27 providers can bill repeated input at ~10% normal price OpenAI GPT-5.5 cached input is $0.50/MTok vs $5.00 Anthropic for instance bills cache writes at 1.25x normal input standard 5-minute TTL 2x 1-hour TTL OpenAI vs Anthropic API Pricing 2026 After Price Cuts All prices checked against vendors official pricing pages reputable press reporting Sept 17 2026 API pricing changes frequently confirm before you commit budget Prompt caching both providers repeated context billed at fraction Anthropic structure most transparent cache hits cost 0.1x 90% off cache writes 1.25x–2x depending duration OpenAI offers cached-input discounts implicit caching GPT-5.6 models plus prompt-caching usage da How Does Prompt Caching Work LLMs Why It Cuts Bills in Half Anthropic charges 1.25x standard input price write 5-minute cache 2x write 1-hour cache but only 0.1x 90 percent discount read from it Notion cut its Claude API costs 90 percent cut latency up to 85 percent after restructuring prompts around caching according Anthropic own published case study Anthropic default cache TTL quietly reverted from 1 hour to 5 minutes for weeks early 2026 with no announcement according developer reports on Git*