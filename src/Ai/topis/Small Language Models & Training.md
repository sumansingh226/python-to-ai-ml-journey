Small Language Models (SLM) and Their Training 

From 270M to 14B: Why Small is Winning, Architecture, 3 Training Paths, PEFT, Distillation, Quantization, Production
Core Thesis: SLMs aren't just "small LLMs" — they are different engineering discipline. SLM = transformer language model typically under 4B parameters (industry consensus 1M to ~14B, sweet spot enterprise 1B-7B), small enough to run inference on single consumer GPU, CPU-only server, or directly on phone without cloud API call. Single GPT-4 API call $0.03 → 10k queries/day for 6 months = $50k+. Fine-tuned SLM running on $1500 GPU does same job fraction cost, data never leaving servers. Phi-4 Mini 3.8B scores 91.1% SimpleQA competitive with models 10x size. Gap closing fast especially domain-specific tasks. By 2026 SLMs leading transformation — path to AGI may not be through massive scale but through intelligent efficient design. Microsoft proved with Phi-3: textbook-quality synthetic data 3.8B competes with models 25x larger. SLM wins when task specific, data focused, latency/privacy matters.


Table of Contents
What Counts as Small Language Model? Definition & Landscape 2026
Why SLMs Now — Economics, Latency, Privacy, Edge
How SLMs Work — Transformer Architecture Optimizations for Small
The 3 Paths to Train SLM — From Scratch vs Fine-Tune vs Distillation
Step 1: Dataset Preparation — Quality > Quantity, PII, Synthetic
Step 2: Base Model Selection & Hardware — Consumer GPU is Enough
Step 3: Training Techniques — LoRA/QLoRA, PEFT Matrix, Distillation, Pruning, Quantization
Step 4: Optimization Stack — Quantization (GPTQ/AWQ/GGUF), GQA, Sliding Window, SwiGLU
Step 5: Evaluation — Benchmark, LLM-as-Judge, Side-by-Side, A/B Prod
Step 6: Deployment — Self-Hosted vLLM/Ollama, Edge, Hybrid Routing, Speculative Decoding
P-KD-Q Pipeline — Pruning → Distillation → Quantization Production Framework
Advanced Frontiers 2026 — DEFT, Agentic SLM, Tool-Calling Data Generation
When SLM is Wrong Choice
Production Checklist