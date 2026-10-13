Function Calling vs Tool Calling Deep-Dive: OpenAI Tools, Parallel Calls, Error Handling
Complete Production Guide - From Legacy Functions to Modern Tools
Core Thesis: Function Calling (2023) = legacy single function per turn, Tool Calling (2023 Dec+) = modern parallel tools, strict schema, 99.9% valid with constrained decoding. Tool Calling is mandatory for production: supports parallel calls (refund + email in one turn = 50% latency cut), tool_choice auto/required/none, and structured outputs. Function Calling deprecated. Production agents: Always use Tools API with T=0.0 + JSON Schema + allowlist + retry with backoff, parallel when independent (get_order + get_policy in parallel), sequential when dependent (get_trust -> refund).

Table of Contents
History: From Function Calling to Tool Calling
Function Calling (Legacy) - How It Worked
Tool Calling (Modern) - How It Works
OpenAI Tools API Deep-Dive
Parallel Tool Calls - When and How
Tool Choice: Auto, Required, None, Specific Tool
Error Handling: Invalid Tool, Invalid Args, Tool Execution Error, Retry
Constrained Decoding for Tool Calling - 99.9% Valid
Tool Design Best Practices for LLM Use
Multi-Turn Tool Calling Loop - ReAct with Tools
Benchmarks: Function vs Tool Calling, Parallel vs Sequential
Implementation Blueprint - Production Agent
Production Checklist