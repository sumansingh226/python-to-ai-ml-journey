# MCP & A2A Protocols: Agent Interoperability & Tool Standardization
## How Agents Talk to Tools and to Each Other in 2026

> **Core Thesis:** Before MCP, every agent framework had its own way to call tools — LangChain tools, OpenAI function calling, custom JSON. It was like the early internet without HTTP. MCP (Model Context Protocol) standardizes how agents talk to tools/data, and A2A (Agent-to-Agent) standardizes how agents talk to each other. Together they are the TCP/IP for agentic AI.

### Table of Contents
1. [The Integration Hell Before MCP](#1-the-integration-hell-before-mcp)
2. [Model Context Protocol (MCP) - Anthropic, Nov 2024](#2-model-context-protocol-mcp---anthropic-nov-2024)
3. [Agent-to-Agent (A2A) Protocol - Google, April 2025](#3-agent-to-agent-a2a-protocol---google-april-2025)
4. [MCP vs A2A: Complementary, Not Competing](#4-mcp-vs-a2a-complementary-not-competing)
5. [Architecture in Production](#5-architecture-in-production)
6. [Implementation Blueprint](#6-implementation-blueprint)
7. [Security & Guardrails for MCP/A2A](#7-security--guardrails-for-mcpa2a)
8. [Pros, Cons & Future](#8-pros-cons--future)

---

### 1. The Integration Hell Before MCP

Before November 2024, building an agent that could use 10 tools meant:

- Tool 1: LangChain Tool with `func` + `description`
- Tool 2: OpenAI Function with JSON Schema
- Tool 3: Custom REST API with manual prompt engineering
- Tool 4: Database connector with custom wrapper

Every framework reinvented tool definition. Switching from LangChain to AutoGen meant rewriting all tools. No reuse, no marketplace.

**Analogy:** Like building a website in 1993 where every website needed its own custom browser.

### 2. Model Context Protocol (MCP) - Anthropic, Nov 2024

MCP is an open standard introduced by Anthropic that defines how LLMs and agents communicate with external data sources and tools via a client-server model.

#### Core Concepts:

**a) MCP Host & Client & Server:**

- **Host:** The AI application (e.g., Claude Desktop, Cursor IDE, your agent orchestrator) that wants to use tools
- **MCP Client:** Inside host, maintains 1:1 connection to a server
- **MCP Server:** Lightweight program that exposes specific capabilities (e.g., Postgres server, GitHub server, Slack server)

```
Your Agent (Host)
  -> MCP Client 1 -> MCP Server: Postgres (exposes query, schema tools)
  -> MCP Client 2 -> MCP Server: GitHub (exposes create_issue, search_code)
  -> MCP Client 3 -> MCP Server: Filesystem (exposes read_file, write_file)
```

**b) What MCP Server Exposes (Three Primitives):**

1.  **Tools:** Functions agent can call (like function calling) — e.g., `query_database`, `create_github_issue`
2.  **Resources:** Read-only data sources agent can read — e.g., file contents, database schema, email inbox
3.  **Prompts:** Reusable prompt templates — e.g., `refund_policy_v2.3` prompt that server provides

**c) Transport:** Initially stdio (local process) and SSE (Server-Sent Events) for remote. In 2026, Streamable HTTP is standard.

**Why MCP won:**

- One MCP server (e.g., Postgres) works with Claude, Cursor, LangChain, OpenAI Agents SDK — write once, use everywhere
- Marketplace: In 2026 there are 2000+ MCP servers on mcp.so — Stripe, Notion, Linear, etc.
- Tool definitions include JSON Schema + descriptions, so agents automatically know how to use them via Structured Outputs

**Example MCP Server Definition (TypeScript):**

```typescript
// mcp-server-postgres
server.tool("query", {
  description: "Run read-only SQL query against analytics DB",
  inputSchema: {
    type: "object",
    properties: {
      sql: {type: "string", description: "SQL query, only SELECT allowed"},
    },
    required: ["sql"]
  },
  handler: async ({sql}) => {
    // Guardrail: Check for non-SELECT
    if (!sql.trim().toUpperCase().startsWith("SELECT")) throw new Error("Only SELECT allowed");
    const result = await pg.query(sql);
    return {content: [{type: "text", text: JSON.stringify(result.rows)}]};
  }
});
```

Agent automatically discovers this tool via MCP handshake — no manual integration.

### 3. Agent-to-Agent (A2A) Protocol - Google, April 2025

If MCP is about agent-to-tool, A2A is about agent-to-agent.

Google introduced A2A as an open protocol for agents built on different frameworks to discover, communicate, and collaborate, regardless of vendor.

#### Core Concepts:

**a) Agent Card:** Every A2A agent publishes a JSON card at `/.well-known/agent.json` describing:

```json
{
  "name": "Refund Specialist Agent",
  "description": "Handles refunds per policy v2.3",
  "url": "https://agents.company.com/refund",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {"id": "process_refund", "description": "Refund order if eligible"}
  ]
}
```

Other agents can discover this via URL — like robots.txt for agents.

**b) Communication Model:**

- **Task:** A2A's core object. One agent creates a task: `task = {id, goal, status}`
- **Message:** Agents exchange messages within task: user and agent roles, with parts (text, data, files)
- **Artifacts:** Result of task — e.g., refund receipt, email draft

```
Supervisor Agent (LangGraph)
  -> Discovers Refund Agent via Agent Card at https://agents.company.com/refund/.well-known/agent.json
  -> Creates A2A Task: "Refund ORD-12345"
  -> Sends message to Refund Agent
  -> Refund Agent executes (may use MCP tools internally)
  -> Returns artifact: {refund_id, status}
```

**c) Transport:** HTTP + JSON-RPC + SSE for streaming. Works across clouds.

**Why A2A matters:**

- Your LangGraph supervisor can delegate to a CrewAI refund agent and an AutoGen email agent without custom glue code — they all speak A2A
- Enterprise can have agents from different vendors (Salesforce Agentforce, Microsoft Copilot, custom) collaborate via A2A
- Built-in support for long-running tasks, streaming, push notifications, and human-in-the-loop (approval gates)

### 4. MCP vs A2A: Complementary, Not Competing

| Aspect | MCP | A2A |
| :--- | :--- | :--- |
| **What it connects** | Agent -> Tool / Data / Resource | Agent -> Agent |
| **Introduced by** | Anthropic (Nov 2024) | Google (Apr 2025) |
| **Scope** | Single agent's toolbelt | Multi-agent team collaboration |
| **Discovery** | Local config or registry | Agent Card at well-known URL |
| **Analogy** | USB-C for tools — standard plug for any tool | HTTP for agents — standard way for agents to talk |

**Production Architecture uses both:**

```
User Goal
  -> Supervisor Agent (Host)
    -> Uses MCP Clients to call tools: Postgres, GitHub, Slack (MCP servers)
    -> Uses A2A Client to delegate to specialist agents:
       - Refund Agent (via A2A, which internally uses MCP to call Stripe)
       - Email Agent (via A2A, which internally uses MCP to call Gmail)
```

MCP inside each agent, A2A between agents.

### 5. Architecture in Production

**Full Stack for Your Curriculum (Node.js + Postgres + ClickHouse):**

```
[UI Layer: Chat + Activity Stream + GenUI]
  |
[Orchestration: LangGraph Supervisor]
  |
  |-- A2A -- Refund Specialist Agent (Python, LangGraph)
  |         |-- MCP: Stripe Server (tools: create_refund, list_orders)
  |         |-- MCP: Postgres Server (tools: get_trust_score)
  |         |-- Policy Engine: Checks refund_policy_v2.3 DAG
  |
  |-- A2A -- Email Specialist Agent (Node.js, Vercel AI SDK)
  |         |-- MCP: Gmail Server
  |         |-- MCP: Template Server (resources: email_templates)
  |
  |-- Direct MCP Tools (for supervisor):
          |-- Filesystem MCP, Calendar MCP, etc.
  |
[Observability: OpenTelemetry GenAI -> ClickHouse + Langfuse]
[Memory: pgvector (semantic) + Postgres (episodic) + Redis (working)]
[Guardrails: Input/Output guardrails on all MCP tool results]
```

**Key:** Every MCP tool call goes through guardrails (input guardrail before sending to tool? No, action gate before execution) and is logged with OTel.

### 6. Implementation Blueprint

#### A. Create an MCP Server (Your Custom Tool)

```typescript
// mcp-server-refund-policy - exposes refund policy as resource + tool
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

const server = new McpServer({name: "refund-policy", version: "2.3"});

// Resource: Policy document
server.resource("refund_policy", "policy://refund_v2.3", async () => ({
  contents: [{uri: "policy://refund_v2.3", text: "If amount >500 or trust<30, escalate..."}]
}));

// Tool: Check policy
server.tool("check_refund_eligibility", {
  description: "Check if refund is eligible per policy v2.3",
  inputSchema: z.object({
    amount: z.number(),
    trust_score: z.number()
  })
}, async ({amount, trust_score}) => {
  const needsApproval = amount > 500 || trust_score < 30;
  return {
    content: [{type: "text", text: JSON.stringify({eligible: !needsApproval, needsApproval, policy_version: "v2.3"})}]
  };
});

// Start server via stdio
server.listen();
```

#### B. Use MCP Server in Agent (Python)

```python
# Agent using MCP client
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        tools = await session.list_tools() # Discovers check_refund_eligibility automatically
        
        # Agent can now call it
        result = await session.call_tool("check_refund_eligibility", {"amount": 1200, "trust_score": 15})
        print(result) # {eligible: false, needsApproval: true}
```

#### C. A2A Agent Card + Task

```python
# Refund Agent exposing A2A
from a2a.server import A2AServer

app = A2AServer(agent_card={
  "name": "Refund Agent",
  "url": "https://agents.company.com/refund",
  "skills": [{"id": "process_refund", "description": "Process refund"}]
})

@app.task_handler("process_refund")
async def handle_refund(task):
    # Inside, use MCP to call Stripe
    async with mcp_client() as session:
        await session.call_tool("create_refund", task.input)
    
    return {"artifact": {"refund_id": "REF-123", "status": "escalated_for_approval"}}

# Supervisor discovers and calls via A2A
from a2a.client import A2AClient

client = A2AClient("https://agents.company.com/refund")
agent_card = await client.get_agent_card() # Discovers capabilities
task = await client.create_task(goal="Refund ORD-12345", skill_id="process_refund")
async for event in client.stream_task(task.id):
    print(event) # Streaming thoughts + tool calls
```

### 7. Security & Guardrails for MCP/A2A

MCP/A2A introduce new attack surface:

**a) Tool Poisoning:** Malicious MCP server description says "This tool will delete all files but description says it reads files". Agent trusts description and calls it.

**Mitigation:**
- Only allow vetted MCP servers from internal registry, not public marketplace in prod
- Input guardrail scans MCP tool descriptions for prompt injection
- Action Gate: Check IAM before allowing MCP tool execution — `query` tool can only SELECT, not DELETE (enforce in server handler)
- Log all MCP tool calls with OTel, alert on spike in denied calls

**b) A2A Impersonation:** Malicious agent publishes fake Agent Card pretending to be Refund Agent but steals data.

**Mitigation:**
- Mutual TLS + OAuth for A2A calls
- Verify Agent Card signature
- Policy Engine checks: Only agents from allowlist `agents.company.com/*` can be delegated to

**c) Data Exfiltration via Resources:** MCP resource could contain 10M row table, agent tries to load all into context, causes DoS and cost explosion.

**Mitigation:**
- MCP servers enforce pagination + row limits (max 1000 rows)
- Output guardrail checks size of MCP resource before injecting into LLM context
- Context compaction: Summarize large MCP results via Tier 2 workhorse before adding to working memory

### 8. Pros, Cons & Future

#### Pros
*   **Interoperability:** Write MCP server once, works with Claude, Cursor, OpenAI Agents SDK, LangChain — no rewrite
*   **Ecosystem:** 2000+ pre-built servers in 2026 — you don't build Stripe integration, you use `stripe-mcp-server`
*   **Multi-Agent Standard:** A2A allows heterogeneous agents (LangGraph + CrewAI + Salesforce) to collaborate without custom glue
*   **Auditability:** MCP handshake and A2A tasks are logged — you know which tools agent discovered and which agents it delegated to

#### Cons
*   **Maturity:** MCP auth is still evolving — OAuth for MCP servers was added mid-2025, not all servers support it yet
*   **Latency:** Each MCP tool call adds 50-100ms overhead vs direct function call
*   **Tool Sprawl:** Easy to give agent 50 MCP tools — agent gets confused (too many tools problem). Need careful curation — max 10-15 tools per agent (see Tool Use module)
*   **Versioning:** MCP server v2.3 vs v2.4 — breaking changes in tool schema can break agents. Need version pinning.

#### Future (Late 2026+):

- **MCP Registry + Signing:** Central registry with signed servers, like npm for tools
- **A2A + MCP Convergence:** A2A tasks will be able to directly expose MCP tools — supervisor can call worker's MCP tools transparently
- **Agent Payments:** A2A will add payment primitives — agent can pay another agent for task (e.g., Refund Agent charges $0.01 per refund check)

---

**Bottom Line:** MCP standardizes agent-to-tool, A2A standardizes agent-to-agent. Together they turn the wild west of custom integrations into a composable, marketplace-driven ecosystem. Build your tools as MCP servers, expose your specialist agents via A2A Agent Cards, and your supervisor can orchestrate a team of heterogeneous agents that all speak the same protocol — with guardrails and observability at every boundary.

In your curriculum, this module sits after Multi-Agent Orchestration and Tool Use, because it is the standard that makes both interoperable, and before Security & Guardrails, because MCP/A2A are new attack surfaces.

---
*Module: MCP & A2A Protocols - Part of Advanced Agentic AI Curriculum - v1.0 - September 2026*
