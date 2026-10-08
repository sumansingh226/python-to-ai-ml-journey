# Agentic RAG & GraphRAG: From Vector Search to Knowledge Graphs to Agentic Reasoning (Full Production Guide)
## Complete Guide to Multi-Hop Reasoning, Community Detection, and Agentic Loops

> **Core Thesis:** Traditional RAG retrieves chunks. GraphRAG retrieves relationships. Agentic RAG retrieves *by reasoning* — planning, traversing, validating, and synthesizing across a knowledge network to solve multi-hop problems that vector search alone cannot. Microsoft GraphRAG 2024 adds community detection + map-reduce for global questions. Result: 60% -> 85% accuracy on multi-hop QA (+25%), auditable paths for EU AI Act compliance.

### Table of Contents
1. What is Agentic RAG & GraphRAG?
2. Why Traditional RAG Fails at Scale (40% Multi-Hop Failure)
3. Why GraphRAG is Needed
4. Architecture: Full Pipeline from Ingestion to Query
5. Step 1: Extract Knowledge Graph from Docs (LLM Extraction)
6. Step 2: Build Vector Index (pgvector)
7. Step 3: Community Detection (Microsoft GraphRAG 2024 - Leiden)
8. Step 4: Query Time - Hybrid Retrieval (Vector + Graph + Community)
9. Step 5: Synthesis with Auditable Paths for Compliance
10. Core Architectural Patterns (Hybrid, Doc Graph, Agentic DAG)
11. Agentic GraphRAG Loop: Plan -> Traverse -> Reason -> Replan (Reflexion)
12. Local vs Global Search (Microsoft GraphRAG)
13. Implementation Stack: Postgres + pgvector + Neo4j + LangGraph
14. Pros and Cons with Production Numbers
15. Benchmarks, Cost, Latency
16. Real-World Applications
17. Design Checklist for Production

---

### 1. What is Agentic RAG & GraphRAG?

Traditional RAG uses vector DBs to fetch chunks based on semantic similarity. Struggles with fragmented data.

GraphRAG: Advanced RAG that incorporates graph-structured data. Instead of only text chunks, GraphRAG indexes data into graph structure of entities (nodes) and relationships (edges). Retrieval becomes graph traversal, not just vector similarity.

Agentic RAG: Moves beyond passive retrieval to active problem-solving. Agent plans, executes multiple graph queries, reasons based on results to replan, validate, summarize.

In short:
- RAG = Query -> Embed -> Vector Search -> Chunks -> LLM Answer
- GraphRAG = Query -> Entity Extraction -> Graph Traversal -> Subgraph -> LLM Answer
- Agentic GraphRAG = Goal -> Plan Queries -> Traverse Graph + Vector Store -> Reflect -> Replan -> Synthesize

Microsoft GraphRAG (2024): Extract KG + detect communities via Leiden clustering + summarize each community + Local Search (entity-specific) or Global Search (map-reduce over community summaries).

### 2. Why Traditional RAG Fails at Scale (40% Multi-Hop Failure)

Example Docs:
Doc1: "Feature X is a new dashboard built by Team Y in Q1 2026."
Doc2: "Team Y is the Analytics team managed by Alice Smith."
Doc3: "Alice Smith (alice@company.com) is Senior Manager."

Query: "Email of manager of team that built Feature X?"

Vector RAG fails:
- Embedding query: "email manager team built Feature X"
- Top 3: Doc1 "Feature X built by Team Y" (0.85), random doc (0.80), Doc1 again (0.78)
- Misses Doc2 and Doc3 because "Team Y managed by Alice" has low similarity to "email manager team built Feature X" — no lexical overlap with "email" vs "managed by"
- Result: Fails

Why:
1. Loss of Relationship: Chunks isolated. Doc A "John works at Acme" and Doc B "Acme acquired Beta" — vector may return both, but doesn't know they connect.
2. Multi-hop Failure: "Who are suppliers of our supplier's supplier?" requires chaining. Vector is 1-hop only.
3. Context Fragmentation: Top-k similar chunks, not full community/network around entity.
4. No Validation: LLM can hallucinate relationship. No ground truth to check.

Stats: 40% of enterprise QA is multi-hop (2-3 hops) — vector RAG 60% accuracy.

GraphRAG succeeds:
- Builds KG: (Feature X)-[built_by]->(Team Y)-[managed_by]->(Alice)-[email]->(alice@company.com)
- Traverses 3 hops
- Returns auditable path: Feature X -> Team Y -> Alice -> alice@company.com
- 85% accuracy (+25% vs vector)

### 3. Why GraphRAG is Needed

a) Multi-hop QA: Can walk Person -> WorksAt -> Company -> LocatedIn -> City -> HasRegulation -> Policy.
b) Consistency & Validation: Knowledge graph acts as factual validator. Check if edge exists — reduces hallucination.
c) Context Richness: Provides community summaries, central entities, relationship weights.
d) Global Questions: Vector answers "What does doc X say about Y?" GraphRAG answers "What are main themes across all docs about Y?" via community detection.
e) Auditable: Graph path provides audit trail for EU AI Act Art 12, SOC2 vs vector black box similarity score.

### 4. Architecture: Full Pipeline

Ingestion:
Docs -> Chunking (500 tokens, overlap 50) -> Parallel: Vector Index (pgvector) + KG Extraction (LLM -> kg_nodes/kg_edges) -> Community Detection (Leiden -> communities + summaries) -> Storage

Query:
Query "Email of manager of team that built Feature X?" -> Entity Extraction ["Feature X", path: built_by, managed_by, email] -> Parallel: Vector Search top5 + Graph Traversal MATCH (Feature X)-[:built_by]->(Team)-[:managed_by]->(Person)-[:email]->(Email) + Community Search -> Combine -> Synthesis with auditable path

### 5. Step 1: Extract Knowledge Graph from Docs

KG_EXTRACTION_PROMPT = "Text: {chunk_text} Extract entities and relationships as JSON: Nodes {id, type (Person, Team, Feature, Order, Product, Policy), properties {name, email, amount}} Edges {from_id, to_id, type (built_by, managed_by, placed, contains, email, reports_to), properties {}} Rules: id normalized, type from allowed list, only explicit relationships, don't hallucinate"

def extract_kg_from_chunk(chunk_text):
    response = llm.generate(prompt, schema=KGSchema, temperature=0.0)
    return KGSchema.parse(response)

Storage:
CREATE TABLE kg_nodes (id TEXT PRIMARY KEY, type TEXT, properties JSONB, embedding VECTOR(1536), source_chunk_id TEXT);
CREATE TABLE kg_edges (from_id TEXT, to_id TEXT, type TEXT, properties JSONB, source_chunk_id TEXT, PRIMARY KEY (from_id, to_id, type));

Cost: 10K chunks * $0.01 = $100 one-time

### 6. Step 2: Build Vector Index (pgvector)

def build_vector_index(chunks):
    for chunk in chunks:
        emb = embedding_model.embed(chunk.text)
        pg.execute("INSERT INTO chunks (id, text, embedding) VALUES (%s,%s,%s)", (chunk.id, chunk.text, emb))

### 7. Step 3: Community Detection (Microsoft GraphRAG 2024 - Leiden)

Why communities? KG huge (100K nodes) — can't fit all in context. Communities = clusters tightly connected.

import leidenalg, igraph as ig
def detect_communities(kg_nodes, kg_edges):
    g = ig.Graph()
    g.add_vertices([node.id for node in kg_nodes])
    g.add_edges([(edge.from_id, edge.to_id) for edge in kg_edges])
    partition = leidenalg.find_partition(g, leidenalg.ModularityVertexPartition)
    communities = []
    for community_id, nodes in enumerate(partition):
        community_nodes = [kg_nodes[i] for i in nodes]
        community_text = "\n".join([f"{n.id} ({n.type}): {n.properties}" for n in community_nodes])
        summary = llm.generate(f"Summarize this community:\n{community_text}\nSummary in 3-5 sentences.")
        communities.append({"id": community_id, "nodes": community_nodes, "summary": summary, "embedding": embedding_model.embed(summary)})
    return communities

CREATE TABLE communities (id TEXT PRIMARY KEY, node_ids TEXT[], summary TEXT, embedding VECTOR(1536));

Example summary: "Analytics team community: Team Y builds Feature X dashboard and Feature Z reports. Managed by Alice Smith (alice@company.com). Members Bob, Carol. Focus on revenue metrics."
Cost: 100 communities * $0.01 = $1

### 8. Step 4: Query Time - Hybrid Retrieval

def graphrag_query(query):
    entity_extraction = llm.generate(f"Query: {query} Extract entities and path JSON {{entities: [], path: []}}", schema=EntityPathSchema, T=0.0)
    # {entities: ["Feature X"], path: ["built_by", "managed_by", "email"]}
    vector_results = vector_search(query, top_k=5)
    graph_results = kg_traverse(start=entity_extraction.entities[0], path=entity_extraction.path)
    # SQL: SELECT n3.props->>'email' FROM kg_edges e1 JOIN kg_edges e2 ON e1.to_id=e2.from_id JOIN kg_edges e3 ON e2.to_id=e3.from_id WHERE e1.from_id='Feature X' AND e1.type='built_by' AND e2.type='managed_by' AND e3.type='email'
    query_emb = embedding_model.embed(query)
    community_results = pg.query("SELECT summary FROM communities ORDER BY embedding <=> %s LIMIT 3", (query_emb,))
    context = {"vector": vector_results, "graph_path": graph_results, "communities": community_results}
    answer = llm.generate(f"Query: {query} Vector: {vector_results} Graph path: {graph_results} Community: {community_results} Answer with auditable path and citations.")
    return answer

### 9. Step 5: Synthesis with Auditable Paths

Answer: "Email is alice@company.com.
Reasoning:
- Feature X built by Team Y (built_by, source Doc1 chunk_123)
- Team Y managed by Alice Smith (managed_by, source Doc2 chunk_456)
- Alice email alice@company.com (email, source Doc3 chunk_789)
Path: Feature X -> Team Y -> Alice Smith -> alice@company.com
Community: Analytics team builds dashboards managed by Alice."

Required for EU AI Act Art 12 audit trail.

### 10. Core Architectural Patterns

Pattern A: Knowledge Graph + Text (Hybrid Retrieval)
User Query -> Extract Entities -> Parallel: Vector Search + Graph Query -> Merge [Text Chunks + Subgraph as triples] -> LLM Synthesis
Best for finance, healthcare, legal ontology.

Pattern B: Graph of Documents (Citation & Reference Graph)
Documents referencing each other (support tickets -> PRs -> policies) connected. Traversal retrieves connected set.

Pattern C: Agentic Graph Systems (DAG of Agents + Graph Tools)
Multiple agents coordinate via DAG. Planner breaks Q into sub-questions, Retriever executes Cypher + vector queries, Critic validates, Synthesizer produces final answer with path. Agentic because agent decides what to query next.

### 11. Agentic GraphRAG Loop: Plan -> Traverse -> Reason -> Replan (Reflexion)

def agentic_graphrag(query):
    plan = planner.create_plan(query)
    context_graph = Graph()
    for step in plan:
        cypher_query = llm_to_cypher(step, schema)
        subgraph = graph_db.execute(cypher_query)
        vector_chunks = vector_db.search(step)
        context_graph.merge(subgraph)
        reflection = critic.evaluate(context_graph, query)
        if reflection.needs_more_info:
            plan.add_next_step(reflection.next_query)
    return synthesizer.generate(query, context_graph, vector_chunks)

Key: Graph-Enhanced Prompting — feed LLM (Entity)-[RELATION]->(Entity) triples, grounds reasoning.
Reflexion: If traversal empty, reflect "No results for built_by, maybe relationship is developed_by? Try alternative." Stores lesson in episodic memory.

### 12. Local vs Global Search

Local Search: Entity-specific Q "Email of manager of team that built Feature X?" Uses entities in query to find relevant nodes + vector + community summaries
Global Search: High-level Q "What are main teams and their focus?" Uses community summaries only, map-reduce over community summaries

def global_search(query):
    communities = pg.query("SELECT summary FROM communities")
    intermediate = []
    for community in communities:
        ans = llm.generate(f"Community: {community.summary} Query: {query} If relevant, answer. Else 'No info'.")
        if "No info" not in ans:
            intermediate.append(ans)
    final = llm.generate(f"Intermediate: {intermediate} Query: {query} Combine into final answer.")
    return final

### 13. Implementation Stack

Graph DB: Neo4j, Neptune, TigerGraph | Vector DB: pgvector, Pinecone | Orchestration: LangGraph, LlamaIndex | Extraction: LLM KG construction | Query Language: Cypher, Gremlin, SPARQL

Small graphs <100K nodes: Postgres only
CREATE TABLE chunks (id TEXT PRIMARY KEY, text TEXT, embedding VECTOR(1536));
CREATE TABLE kg_nodes (id TEXT PRIMARY KEY, type TEXT, properties JSONB, embedding VECTOR(1536), source_chunk_id TEXT);
CREATE TABLE kg_edges (from_id TEXT, to_id TEXT, type TEXT, properties JSONB, source_chunk_id TEXT, PRIMARY KEY (from_id, to_id, type));
CREATE TABLE communities (id TEXT PRIMARY KEY, node_ids TEXT[], summary TEXT, embedding VECTOR(1536));

Large graphs >100K: Neo4j + pgvector
from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687")
def kg_traverse_neo4j(start, path):
    cypher = f"MATCH (s {{id: $start}})-[r1:{path[0]}]->(n1)-[r2:{path[1]}]->(n2)-[r3:{path[2]}]->(n3) RETURN n3.properties.email"
    with driver.session() as session:
        return session.run(cypher, start=start).data()

LangGraph with Postgres checkpointer:
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
workflow = StateGraph(AgentState)
app = workflow.compile(checkpointer=checkpointer)

### 14. Pros and Cons

Pros: Accuracy 60%->85% multi-hop +25%, 40%->75% global QA via community summaries, Community Detection identifies customer segments fraud rings A->B->C->A product ecosystems, Explainability exact path auditable with source chunk IDs for EU AI Act, Hallucination Reduction graph as factual constraint
Cons: Complexity designing schemas ontologies, Latency 2-5x vs vector lookup 1s->1.8s, Ingestion Cost 10K chunks $100 vs $1 vector only 100x build, Query Cost $0.03 vs $0.01 3x

### 15. Benchmarks, Cost, Latency

Accuracy: Multi-hop (2-3 hops) Vector 60% GraphRAG 85% (+25%), Single-hop Vector 80% GraphRAG 82%, Global QA Vector 40% GraphRAG 75%
Build one-time 10K chunks: Vector embedding $1, KG extraction $100, Community summarization $1, Total ~$102 vs $1 vector only
Query: Vector RAG 1 vector search + 1 LLM = $0.01, 1s, GraphRAG 1 vector + 1 graph traversal + 1 community search + 1 entity extraction + 1 synthesis = $0.03, 1.8s
When worth it: Enterprise KB with 40% multi-hop queries — 25% accuracy gain worth 3x cost. For single-hop FAQ — vector sufficient.

### 16. Real-World Applications

1. Financial Fraud Detection: Tracing high-value paths detecting circular transactions A->B->C->A that vector search would never catch.
2. Equipment Diagnostics & IoT: Graph links Sensor Alert -> Part -> Machine Model -> Past Failure -> Fix Procedure.
3. Customer 360 & Support: Connecting support tickets, product usage, billing, documentation into one graph to answer "Why is this enterprise customer churning?" with full lineage.
4. Drug Discovery & Legal Research: Multi-hop reasoning over research papers, patents, clinical trials.

### 17. Design Checklist for Production

1. Do not start with graph. Start Hybrid RAG (vector + graph) for quick wins. Measure multi-hop failure rate — if >30%, add GraphRAG
2. Define ontology first. What entities and relationships matter?
3. Separate stable vs volatile graph. Core product ontology stable and cacheable; transactional volatile.
4. Extract KG via LLM with Pydantic schema {nodes, edges}, T=0.0, normalized ids, only explicit relationships, store source_chunk_id for audit
5. Build communities via Leiden clustering — 50-100 communities, summarize each via LLM, embed summary for global search
6. Query: Entity extraction + hybrid retrieval — Extract entities + path from query, parallel vector + graph traversal + community search, combine
7. Synthesis with auditable path — Direct answer + reasoning path with relationship types and source chunk IDs (EU AI Act Art 12) + cite docs
8. Use Postgres for <100K nodes, Neo4j for >100K
9. LangGraph is standard for state graphs — Conditional edges, loops, human-in-the-loop, Postgres checkpointer for resume
10. Local vs Global search — Local for entity-specific QA, Global for high-level QA using map-reduce over community summaries
11. Observability: Log Cypher queries, traversal depth, token cost per agentic loop. Max traversal depth 3 hops to prevent blowup
12. Human-in-the-Loop for KG construction: Review step for auto-extracted triples

Bottom Line: Vector RAG fails 40% enterprise QA because 1-hop only. GraphRAG solves by building Knowledge Graph from docs (entities + relationships via LLM extraction) + community detection (Leiden clustering + summaries) + hybrid retrieval at query time (vector + graph traversal 2-3 hops + community search) + synthesis with auditable path. Result: 60%->85% accuracy on multi-hop (+25%), 40%->75% on high-level QA. Build cost $102 vs $1 for 10K chunks (100x), query cost $0.03 vs $0.01 (3x), latency 1.8s vs 1s. Worth it when 30%+ queries multi-hop. Use Postgres for small graphs, Neo4j for large, always include auditable path for compliance, and implement agentic loop with planning + traversal + reflection + replanning.

