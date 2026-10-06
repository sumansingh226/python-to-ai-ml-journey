# Graphs in Agentic AI: Knowledge Graphs, State Graphs, and Workflow Graphs
## The Data Structure That Connects Memory, Reasoning, and Orchestration

> **Core Thesis:** Graphs are the hidden backbone of production agents. Knowledge Graphs store facts with relationships for multi-hop reasoning, State Graphs (LangGraph) define agent workflows as nodes and edges with conditional routing, and Workflow Graphs represent task dependencies. Without graphs, agents are linear chatbots; with graphs, they reason over connected knowledge, branch conditionally, and orchestrate multi-agent teams.

### Table of Contents
1. [Why Graphs?](#1-why-graphs)
2. [Type 1: Knowledge Graphs for Memory & RAG](#2-type-1-knowledge-graphs-for-memory--rag)
3. [Type 2: State Graphs for Agent Workflows (LangGraph)](#3-type-2-state-graphs-for-agent-workflows-langgraph)
4. [Type 3: Task Dependency Graphs (DAGs)](#4-type-3-task-dependency-graphs-dags)
5. [Type 4: Agent Collaboration Graphs (Multi-Agent)](#5-type-4-agent-collaboration-graphs-multi-agent)
6. [Type 5: Conversation Graphs (Context Graphs)](#6-type-5-conversation-graphs-context-graphs)
7. [GraphRAG: Graphs + RAG for Multi-Hop QA](#7-graphrag-graphs--rag-for-multi-hop-qa)
8. [Implementation Blueprint with Postgres + pgvector + Neo4j](#8-implementation-blueprint-with-postgres--pgvector--neo4j)
9. [Production Checklist](#9-production-checklist)

---

### 1. Why Graphs?

**Without graphs:**

```
User: "Who is the manager of the team that built feature X?"
Agent (vector search only): Searches "manager team feature X" -> gets 5 chunks about feature X, but no chunk explicitly says "manager is Alice" because that fact is in another doc about team structure.
Fails — needs 2-hop reasoning: Feature X -> Team Y -> Manager Alice
```

**With graphs:**

```
Knowledge Graph:
(Feature X) -[built_by]-> (Team Y) -[managed_by]-> (Person Alice)

Graph query: MATCH (f:Feature {name:"X"})-[:built_by]->(t:Team)-[:managed_by]->(m:Person) RETURN m
Result: Alice

Multi-hop reasoning solved.
```

**Graphs solve:**
- Multi-hop QA (2+ hops)
- Relationship reasoning (who manages whom, what depends on what)
- Conditional workflows (if trust_score >80 then auto-refund else approval)
- Multi-agent orchestration (who talks to whom)
- Context that is not linear (conversation branches)

### 2. Type 1: Knowledge Graphs for Memory & RAG

**What:** Store entities (nodes) and relationships (edges) extracted from docs, conversations, tool outputs.

**Example:**

```
Nodes: (Order ORD-12345), (User U-123), (Product P-456), (Team Support)
Edges: (U-123)-[:placed]->(ORD-12345), (ORD-12345)-[:contains]->(P-456), (U-123)-[:trust_score 85]->(Trust)

Schema:
CREATE TABLE knowledge_graph_nodes (
  id TEXT PRIMARY KEY,
  type TEXT, -- User, Order, Product, Team, Policy
  properties JSONB -- {name, amount, status}
)

CREATE TABLE knowledge_graph_edges (
  from_id TEXT,
  to_id TEXT,
  type TEXT, -- placed, contains, managed_by, trust_score
  properties JSONB,
  PRIMARY KEY (from_id, to_id, type)
)
```

**Construction:**

```python
def extract_kg_from_text(text):
    # Use LLM to extract entities and relationships
    prompt = f"Text: {text}\nExtract entities and relationships as JSON: {{nodes: [{{id, type, props}}], edges: [{{from, to, type}}]}}"
    kg = llm.generate(prompt, schema=KGSchema, temperature=0.0)
    # Save to Postgres
    for node in kg.nodes:
        pg.execute("INSERT INTO kg_nodes VALUES (%s,%s,%s) ON CONFLICT DO UPDATE", (node.id, node.type, node.props))
    for edge in kg.edges:
        pg.execute("INSERT INTO kg_edges VALUES (%s,%s,%s,%s)", (edge.from_id, edge.to_id, edge.type, edge.props))

# Example: Extract from support ticket
text = "User john@example.com placed order ORD-12345 for $120, product P-456, needs refund"
kg = extract_kg_from_text(text)
# Nodes: (john@example.com:User), (ORD-12345:Order {amount:120}), (P-456:Product)
# Edges: (john)-[:placed]->(ORD-12345), (ORD-12345)-[:contains]->(P-456)
```

**Querying:**

```python
def kg_query(start_node, relationship_path):
    # e.g., start=ORD-12345, path=[placed_by_reverse, trust_score]
    # Returns user and trust_score
    query = """
    SELECT n2.id, e2.properties
    FROM kg_edges e1
    JOIN kg_edges e2 ON e1.from_id = e2.from_id
    JOIN kg_nodes n2 ON e2.to_id = n2.id
    WHERE e1.to_id = %s AND e1.type = 'placed' AND e2.type = 'trust_score'
    """
    return pg.query(query, (start_node,))

# Or use Cypher if Neo4j:
# MATCH (o:Order {id:"ORD-12345"})<-[:placed]-(u:User)-[t:trust_score]->(trust) RETURN u, t.value
```

**Pros:**
- Multi-hop reasoning (2-3 hops) that vector search can't do
- Explicit relationships — auditable
- Combines with vector search for hybrid (GraphRAG)

**Cons:**
- Extraction costs 1 LLM call per doc
- Graph can become noisy if extraction hallucinated
- Needs schema design

**When to use:** Enterprise knowledge bases where relationships matter — team structure, product dependencies, policy hierarchies, customer journeys.

### 3. Type 2: State Graphs for Agent Workflows (LangGraph)

**What:** Define agent workflow as graph: Nodes = agent steps (LLM call, tool call, condition), Edges = transitions (conditional routing based on state).

**LangGraph is the standard in 2026 — state graph with conditional edges, loops, and human-in-the-loop.**

**Example: Refund Agent Workflow Graph**

```
[Start] -> [Get Order Status] -> [Check Policy] -> {Is amount <500?}
                                          | No
                                          v Yes
                              [Request Approval] -> [Wait for Approval] -> [Refund]
                                          |                    |
                                          |<-------------------|
                                          v
                                      [Refund] -> [Notify User] -> [End]
                                          |
                                    (if denied)
                                          v
                                      [Notify Denied] -> [End]
```

**Implementation with LangGraph:**

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    order_id: str
    order_amount: float
    policy: dict
    trust_score: int
    approval_status: str
    messages: list

def get_order_status(state: AgentState):
    order = stripe.get_order(state["order_id"])
    return {"order_amount": order.amount, "messages": [f"Order amount: {order.amount}"]}

def check_policy(state: AgentState):
    policy = get_policy(version="v2.3")
    return {"policy": policy, "messages": [f"Policy max auto: {policy.max_auto}"]}

def should_auto_refund(state: AgentState):
    if state["order_amount"] < state["policy"]["max_auto"] and state["trust_score"] > 80:
        return "auto_refund"
    else:
        return "request_approval"

def request_approval(state: AgentState):
    serialize_state(task_id, state, status="waiting_approval")
    send_webhook(state)
    return {"messages": ["Waiting for approval"]}

def refund(state: AgentState):
    stripe.refund(state["order_id"], state["order_amount"])
    return {"messages": [f"Refunded ${state['order_amount']}"]}

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("get_order", get_order_status)
workflow.add_node("check_policy", check_policy)
workflow.add_node("request_approval", request_approval)
workflow.add_node("refund", refund)
workflow.add_node("notify", lambda s: {"messages": ["Notified user"]})

workflow.set_entry_point("get_order")
workflow.add_edge("get_order", "check_policy")
workflow.add_conditional_edges("check_policy", should_auto_refund, {
    "auto_refund": "refund",
    "request_approval": "request_approval"
})
workflow.add_edge("request_approval", "refund") # After approval webhook resumes
workflow.add_edge("refund", "notify")
workflow.add_edge("notify", END)

app = workflow.compile()
# Execute
result = app.invoke({"order_id": "ORD-12345", "messages": []})
```

**Pros:**
- Conditional routing — if/else based on state (trust_score, amount)
- Loops — can loop back to re-plan or retry
- Human-in-the-loop — pause graph, serialize state, resume on webhook
- Visualization — graph can be visualized, debugged
- State persistence — each node saves state to Postgres

**Cons:**
- More complex than linear ReAct loop
- Need to define schema for AgentState

**When to use:** ALWAYS for production agents with conditional logic (if amount >500 then approval else auto). LangGraph is the standard.

### 4. Type 3: Task Dependency Graphs (DAGs)

**What:** Represent task as DAG — nodes = sub-tasks, edges = dependencies. Enables parallel execution and optimal scheduling.

**Example:**

```
Task: "Process refund and update analytics and notify user"

DAG:
[Get Order Status] -> [Check Policy] -> [Check Trust] -> [Refund] -> [Notify User]
                                      |
                                      +-> [Update Analytics] (can run parallel with Refund)
```

**Implementation:**

```python
from collections import defaultdict

class TaskDAG:
    def __init__(self):
        self.graph = defaultdict(list) # task_id -> [dependent task_ids]
        self.tasks = {} # task_id -> task
    
    def add_task(self, task_id, task, dependencies=[]):
        self.tasks[task_id] = task
        for dep in dependencies:
            self.graph[dep].append(task_id)
    
    def get_ready_tasks(self, completed):
        # Tasks whose dependencies all completed
        ready = []
        for task_id, task in self.tasks.items():
            if task_id in completed:
                continue
            deps = [dep for dep, children in self.graph.items() if task_id in children]
            if all(dep in completed for dep in deps):
                ready.append(task_id)
        return ready
    
    def execute_parallel(self):
        completed = set()
        while len(completed) < len(self.tasks):
            ready = self.get_ready_tasks(completed)
            # Execute ready tasks in parallel (multi-agent)
            results = parallel_execute([self.tasks[tid] for tid in ready])
            for tid, result in zip(ready, results):
                completed.add(tid)
                # Save result

# Build DAG
dag = TaskDAG()
dag.add_task("get_order", get_order_status, dependencies=[])
dag.add_task("check_policy", check_policy, dependencies=["get_order"])
dag.add_task("check_trust", check_trust, dependencies=["get_order"])
dag.add_task("refund", refund, dependencies=["check_policy", "check_trust"])
dag.add_task("update_analytics", update_analytics, dependencies=["check_policy"]) # Parallel with refund
dag.add_task("notify", notify, dependencies=["refund"])

dag.execute_parallel()
# Executes: get_order -> (check_policy + check_trust in parallel) -> (refund + update_analytics in parallel) -> notify
```

**Pros:**
- Parallel execution — 2x faster than sequential
- Optimal scheduling — only runs tasks when dependencies met
- Clear dependencies — easy to debug

**Cons:**
- Need to define DAG upfront or generate via LLM planning
- More complex than linear

**When to use:** Complex tasks with 5+ sub-tasks and dependencies — use for multi-agent orchestration.

### 5. Type 4: Agent Collaboration Graphs (Multi-Agent)

**What:** Graph where nodes = agents, edges = communication channels. Defines who can talk to whom.

**Example: Supervisor pattern as graph**

```
Supervisor (central node)
  |
  +-> Refund Worker
  +-> Fraud Worker
  +-> Email Worker
  |
Workers communicate via blackboard (Postgres), not directly — star graph

vs Fully connected:
Refund Worker <-> Fraud Worker <-> Email Worker (all can talk to each other) — mesh graph, more complex
```

**Implementation:**

```python
class AgentCollaborationGraph:
    def __init__(self):
        self.agents = {} # agent_id -> agent
        self.edges = defaultdict(list) # agent_id -> [agent_ids it can talk to]
    
    def add_agent(self, agent_id, agent):
        self.agents[agent_id] = agent
    
    def add_communication(self, from_agent, to_agent):
        self.edges[from_agent].append(to_agent)
    
    def route_message(self, from_agent, message):
        # Route to allowed agents
        for to_agent in self.edges[from_agent]:
            self.agents[to_agent].receive(message)

# Supervisor pattern: Star graph
graph = AgentCollaborationGraph()
graph.add_agent("supervisor", supervisor)
graph.add_agent("refund_worker", refund_worker)
graph.add_agent("fraud_worker", fraud_worker)
graph.add_agent("email_worker", email_worker)

graph.add_communication("supervisor", "refund_worker")
graph.add_communication("supervisor", "fraud_worker")
graph.add_communication("supervisor", "email_worker")
graph.add_communication("refund_worker", "supervisor") # Workers reply to supervisor
graph.add_communication("fraud_worker", "supervisor")
graph.add_communication("email_worker", "supervisor")

# Execute
graph.route_message("supervisor", sub_goal_1) # -> refund_worker
```

**Pros:**
- Explicit communication — who can talk to whom, prevents unauthorized data sharing
- Scalable — add new agent as node + edges

**Cons:**
- Need to define communication protocol

**When to use:** Multi-agent systems — define collaboration graph upfront.

### 6. Type 5: Conversation Graphs (Context Graphs)

**What:** Conversation is not linear — it branches. User asks follow-up, agent clarifies, etc. Conversation graph stores branching with parent pointers.

**Example:**

```
User: "Refund ORD-123"
  |
Agent: "Order $120, refund?"
  |
User: "Yes, but also check my other order ORD-456" -> branches from root
  |
Agent: Need to handle two orders — creates two branches
  |
  Branch 1: ORD-123 refund -> success
  Branch 2: ORD-456 status -> $500 -> needs approval -> waiting
```

**Implementation:**

```python
class ConversationNode:
    def __init__(self, id, parent_id, role, content, branch_id):
        self.id = id
        self.parent_id = parent_id
        self.role = role # user, agent, tool
        self.content = content
        self.branch_id = branch_id # Which branch this node belongs to

# Store in Postgres
CREATE TABLE conversation_graph (
  id TEXT PRIMARY KEY,
  parent_id TEXT,
  task_id TEXT,
  branch_id TEXT,
  role TEXT,
  content TEXT,
  timestamp TIMESTAMPTZ
)

# Query branch
SELECT * FROM conversation_graph WHERE branch_id='branch_1' ORDER BY timestamp
```

**Pros:**
- Handles non-linear conversations — follow-ups, clarifications, parallel sub-tasks
- Enables undo — revert to parent node

**Cons:**
- More complex than linear history array

**When to use:** Complex conversations with branching, multi-tasking, or need undo.

### 7. GraphRAG: Graphs + RAG for Multi-Hop QA

**Combines Knowledge Graph + Vector Search for best of both:**

**Steps:**

1.  **Extract KG from docs** (entities + relationships) — LLM extraction
2.  **Build vector index** for chunks (pgvector)
3.  **For query:** 
    a. Vector search for relevant chunks
    b. KG query for multi-hop relationships
    c. Combine results — use KG to connect chunks that vector search alone misses

**Example:**

```
Docs: 
- Doc1: "Feature X built by Team Y"
- Doc2: "Team Y managed by Alice"
- Doc3: "Alice email alice@company.com"

Query: "Email of manager of team that built Feature X?"

Vector search: Finds Doc1 about Feature X, but not Doc2 or Doc3 because "manager email" not in Doc1
KG: (Feature X)-[built_by]->(Team Y)-[managed_by]->(Alice)-[email]->(alice@company.com)
GraphRAG: Vector finds Doc1, KG traverses 2 hops to Alice email, returns answer

Without KG: Fails
With GraphRAG: Success
```

**Implementation:**

```python
def graphrag_query(query):
    # 1. Vector search
    vector_results = pgvector.search(query_emb, top_k=5)
    
    # 2. KG extraction from query
    kg_query = llm.generate(f"Query: {query}\nExtract entities and relationship path to answer", schema=KGQuerySchema)
    # e.g., kg_query = {start: "Feature X", path: ["built_by", "managed_by", "email"]}
    
    # 3. KG traversal
    kg_results = kg_traverse(start=kg_query.start, path=kg_query.path)
    
    # 4. Combine
    context = vector_results + kg_results
    answer = llm.generate(f"Query: {query}\nContext: {context}\nAnswer with reasoning")
    return answer
```

**Microsoft GraphRAG (2024) adds community detection — clusters KG into communities, summarizes each community, then uses summaries for QA.**

**When to use:** Enterprise knowledge bases where multi-hop QA needed — team structure, product dependencies, customer journey.

### 8. Implementation Blueprint with Postgres + pgvector + Neo4j

**For small graphs (<100K nodes): Use Postgres only — simpler**

```sql
-- Knowledge Graph tables in Postgres
CREATE TABLE kg_nodes (id TEXT PRIMARY KEY, type TEXT, properties JSONB, embedding VECTOR(1536));
CREATE TABLE kg_edges (from_id TEXT, to_id TEXT, type TEXT, properties JSONB, PRIMARY KEY (from_id, to_id, type));

-- Vector search on nodes
CREATE INDEX ON kg_nodes USING ivfflat (embedding vector_cosine_ops);

-- Query: Find manager of team that built feature X
WITH feature_team AS (
  SELECT to_id as team_id FROM kg_edges WHERE from_id='Feature X' AND type='built_by'
),
team_manager AS (
  SELECT to_id as manager_id FROM kg_edges WHERE from_id=(SELECT team_id FROM feature_team) AND type='managed_by'
)
SELECT * FROM kg_nodes WHERE id=(SELECT manager_id FROM team_manager);
```

**For large graphs (>100K nodes): Use Neo4j for KG + Postgres pgvector for vectors**

```python
# Neo4j for graph traversal
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687")

def kg_traverse_neo4j(start, relationship_path):
    query = f"MATCH (start {{id: $start}})-[r1:{relationship_path[0]}]->(n1)-[r2:{relationship_path[1]}]->(n2) RETURN n2"
    with driver.session() as session:
        result = session.run(query, start=start)
        return result.data()

# pgvector for vector search, Neo4j for graph traversal — combine
```

**State Graphs with LangGraph + Postgres checkpointer:**

```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver

# Postgres checkpointer saves state after each node for resume
checkpointer = PostgresSaver.from_conn_string("postgresql://...")

workflow = StateGraph(AgentState)
workflow.add_node("get_order", get_order_status)
workflow.add_node("check_policy", check_policy)
# ... add edges

app = workflow.compile(checkpointer=checkpointer)
# State saved to Postgres after each node automatically — resume after pod death
result = app.invoke({"order_id": "ORD-12345"}, config={"configurable": {"thread_id": task_id}})
```

### 9. Production Checklist

1.  **Knowledge Graphs for multi-hop QA** — Extract entities + relationships from docs via LLM, store in Postgres (small) or Neo4j (large), query via path traversal for 2-3 hop reasoning
2.  **State Graphs for workflows** — Use LangGraph with conditional edges (if amount<500 then auto else approval), loops, human-in-the-loop pause/resume, Postgres checkpointer for state persistence
3.  **Task DAGs for dependencies** — Define sub-tasks + dependencies, execute ready tasks in parallel (multi-agent), optimal scheduling
4.  **Agent Collaboration Graphs** — Star graph for supervisor pattern, define who can talk to whom via edges, use blackboard Postgres for messages
5.  **Conversation Graphs for branching** — Store conversation as graph with parent pointers and branch_id, not linear array, enable undo and multi-tasking
6.  **GraphRAG = KG + Vector** — Vector search for chunks + KG traversal for relationships + combine for answer — solves multi-hop that vector alone fails
7.  **Use Postgres for <100K nodes, Neo4j for >100K** — Keep it simple, Postgres can do both graph tables and pgvector
8.  **LangGraph is standard for state graphs** — Conditional edges, loops, human-in-the-loop, checkpointer
9.  **Visualize graphs** — Use LangGraph studio or Neo4j browser to debug workflows
10. **Monitor graph size** — Alert if nodes >1M or edges >10M, need pruning or archiving

---

**Bottom Line:** Graphs are the data structure for production agents — Knowledge Graphs store facts with relationships for multi-hop QA (Feature X -> Team Y -> Manager Alice), State Graphs (LangGraph) define workflows as nodes + conditional edges (if trust>80 then auto else approval) with loops and human pause/resume, Task DAGs represent dependencies for parallel execution, Agent Collaboration Graphs define who talks to whom, Conversation Graphs handle branching. GraphRAG = KG + vector = best of both for enterprise knowledge bases. Use Postgres for small graphs, Neo4j for large, LangGraph for state graphs with Postgres checkpointer for resume.

---

