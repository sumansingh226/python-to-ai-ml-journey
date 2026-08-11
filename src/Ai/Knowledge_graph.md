# Knowledge Graphs for AI

## 1. What is a Knowledge Graph?

A **Knowledge Graph (KG)** is a structured way of representing knowledge as **entities and relationships**.

Instead of storing information only as text or rows in a database, a knowledge graph connects related pieces of information.

For example:

```text
Alice ── works_at ──> OpenAI
Alice ── knows ──> Bob
OpenAI ── develops ──> AI Models
AI Model ── used_for ──> Natural Language Processing
```

The basic structure is:

```text
Entity → Relationship → Entity
```

This is commonly called a **triple**:

```text
Subject → Predicate → Object
```

Example:

```text
Alice → works_at → OpenAI
```

---

## 2. Main Components

### Entities / Nodes

Entities represent things that exist in the knowledge domain.

Examples:

* Person
* Company
* Product
* Document
* Location
* Concept
* Organization
* AI Model

Example:

```text
Alice
OpenAI
GPT
Delhi
Machine Learning
```

---

### Relationships / Edges

Relationships describe how entities are connected.

Examples:

```text
works_at
created_by
located_in
knows
belongs_to
uses
develops
related_to
```

Example:

```text
Alice → works_at → OpenAI
OpenAI → develops → AI Models
```

---

### Properties

Properties provide additional information about entities or relationships.

Example:

```text
Person:
    name: Alice
    age: 30
    role: Engineer
```

A graph might look like:

```text
Alice
 ├── name → Alice
 ├── age → 30
 ├── role → Engineer
 └── works_at → OpenAI
```

---

# 3. Graph Structure

A simple knowledge graph can be represented as:

```text
                    ┌──────────────┐
                    │    Alice     │
                    └──────┬───────┘
                           │
                       works_at
                           │
                           ▼
                    ┌──────────────┐
                    │    OpenAI    │
                    └──────┬───────┘
                           │
                       develops
                           │
                           ▼
                    ┌──────────────┐
                    │   AI Model   │
                    └──────┬───────┘
                           │
                         used_for
                           │
                           ▼
                    ┌──────────────┐
                    │ NLP / AI     │
                    └──────────────┘
```

The important idea is that the graph represents **meaning and connections**, not just individual pieces of data.

---

# 4. Knowledge Graph vs Traditional Database

A traditional relational database might contain:

```text
Users

| id | name  | company |
|----|-------|---------|
| 1  | Alice | OpenAI  |
```

A knowledge graph represents the same information as:

```text
Alice → works_at → OpenAI
```

The graph becomes especially useful when there are many relationships.

For example:

```text
Alice
 ├── works_at → OpenAI
 ├── knows → Bob
 ├── created → Project X
 └── interested_in → Machine Learning

Project X
 ├── uses → GPT
 ├── related_to → NLP
 └── documented_in → Research Paper
```

---

# 5. Why Knowledge Graphs Are Important in AI

Knowledge graphs are useful because AI systems often need to understand **relationships and context**.

An LLM may know that:

```text
Apple
```

can refer to either:

```text
Apple Inc.
```

or:

```text
apple (fruit)
```

A knowledge graph can explicitly represent:

```text
Apple Inc. → type → Company
Apple → type → Fruit
```

This helps AI systems reason about entities more precisely.

---

# 6. Knowledge Graphs + LLMs

Knowledge graphs can be combined with Large Language Models (LLMs).

A typical architecture looks like:

```text
User Question
      │
      ▼
    LLM
      │
      ▼
Entity Extraction
      │
      ▼
Knowledge Graph
      │
      ▼
Relevant Facts
      │
      ▼
    LLM
      │
      ▼
Final Answer
```

Example question:

```text
"Who works with Alice and what projects are they involved in?"
```

The system could search the graph:

```text
Alice
 ├── works_with → Bob
 │                  │
 │                  └── works_on → Project A
 │
 └── works_with → Sarah
                    │
                    └── works_on → Project B
```

The LLM can then turn those relationships into a natural-language answer.

---

# 7. Knowledge Graphs and RAG

Knowledge graphs can also be used with **Retrieval-Augmented Generation (RAG)**.

Traditional RAG often works like:

```text
Question
   ↓
Embedding
   ↓
Vector Search
   ↓
Documents
   ↓
LLM
```

Graph-based RAG can add relationships:

```text
Question
   ↓
Entity Detection
   ↓
Knowledge Graph
   ↓
Related Entities
   ↓
Documents + Relationships
   ↓
LLM
```

This can be useful when the answer depends on **multiple connected facts**.

---

# 8. Example: Company Knowledge Graph

Imagine an AI assistant for a company.

The graph could contain:

```text
Employees
Projects
Teams
Documents
Customers
Products
Technologies
```

Example:

```text
Alice
 ├── member_of → AI Team
 ├── works_on → Project Alpha
 └── uses → Python

Project Alpha
 ├── owned_by → AI Team
 ├── uses → Python
 ├── uses → PostgreSQL
 └── documented_in → Design Document

Design Document
 ├── describes → Project Alpha
 └── written_by → Alice
```

Now an AI assistant can answer questions such as:

```text
Who works on Project Alpha?

What technologies does Project Alpha use?

Which documents describe Project Alpha?

Who wrote the design document?

Which team owns Project Alpha?
```

---

# 9. Knowledge Graph Data Formats

Knowledge graphs can be represented using different formats.

## JSON

```json
{
  "entity": "Alice",
  "type": "Person",
  "relationships": [
    {
      "type": "works_at",
      "target": "OpenAI"
    }
  ]
}
```

## RDF

RDF represents information as triples:

```text
Alice → works_at → OpenAI
OpenAI → develops → AI Models
```

## Property Graph

A property graph stores nodes, relationships, and properties:

```text
(:Person {
    name: "Alice",
    role: "Engineer"
})
```

with a relationship:

```text
(Alice)-[:WORKS_AT]->(OpenAI)
```

---

# 10. Graph Databases

Knowledge graphs are commonly stored in graph databases.

Popular technologies include:

* Neo4j
* Amazon Neptune
* ArangoDB
* Apache Jena
* RDF databases / triplestores

A graph database is designed to efficiently traverse relationships between entities.

---

# 11. Example Query

Using a graph query language such as Cypher:

```cypher
MATCH (person:Person)-[:WORKS_AT]->(company:Company)
RETURN person.name, company.name;
```

This asks:

```text
Find people who work at companies
and return their names and companies.
```

Another example:

```cypher
MATCH (alice:Person {name: "Alice"})
      -[:WORKS_WITH]->(person)
RETURN person;
```

This finds people who work with Alice.

---

# 12. Knowledge Graph Construction

A typical process looks like:

```text
Raw Data
   ↓
Data Cleaning
   ↓
Entity Extraction
   ↓
Entity Resolution
   ↓
Relationship Extraction
   ↓
Schema / Ontology
   ↓
Knowledge Graph
   ↓
Query / Retrieval
   ↓
AI Application
```

### Step 1 — Collect Data

Sources can include:

* Documents
* Websites
* Databases
* APIs
* PDFs
* Emails
* Internal company systems

### Step 2 — Extract Entities

Example:

```text
"Alice works at OpenAI."
```

Extract:

```text
Alice → Person
OpenAI → Company
```

### Step 3 — Extract Relationships

```text
Alice → works_at → OpenAI
```

### Step 4 — Store the Graph

Store the entities and relationships in a graph database.

---

# 13. Entity Resolution

One important problem is determining whether two names refer to the same entity.

For example:

```text
OpenAI
OpenAI Inc.
OpenAI, Inc.
```

may all refer to the same organization.

A knowledge graph can normalize these into:

```text
OpenAI
```

This process is called **entity resolution** or **entity linking**.

---

# 14. Ontology Design

An **ontology** defines what types of entities and relationships exist in a domain.

For example:

```text
Person
Company
Product
Project
Document
Technology
```

Relationships:

```text
Person → works_at → Company
Person → works_on → Project
Project → uses → Technology
Document → describes → Project
Company → develops → Product
```

This is similar to designing a schema for a relational database, but it focuses heavily on **meaning and relationships**.

---

# 15. Knowledge Graphs for AI Agents

AI agents can use knowledge graphs as a persistent source of structured knowledge.

Example:

```text
AI Agent
   │
   ├── Search Web
   │
   ├── Query Database
   │
   ├── Query Knowledge Graph
   │
   └── Call APIs
```

The knowledge graph can provide the agent with structured context before it takes an action.

---

# 16. Practical AI Use Cases

Knowledge graphs are useful for:

### Enterprise Search

```text
Employee → Team → Project → Document
```

### Recommendation Systems

```text
User → likes → Product
Product → belongs_to → Category
Category → related_to → Product
```

### Customer Support

```text
Customer → owns → Product
Product → has_issue → Problem
Problem → solved_by → Solution
```

### Fraud Detection

```text
Person → owns → Account
Account → transfers_to → Account
Account → associated_with → Device
```

### Healthcare Research

```text
Disease → associated_with → Gene
Gene → associated_with → Protein
Protein → targeted_by → Drug
```

### AI Search

```text
Question
   ↓
Entities
   ↓
Graph relationships
   ↓
Relevant documents
   ↓
LLM
```

---

# 17. Key Skills to Learn

If you want to become good at knowledge graphs for AI, learn:

1. **Graph theory basics**
2. **Data modeling**
3. **Schema design**
4. **Ontology design**
5. **Entity resolution**
6. **Entity extraction**
7. **Relationship extraction**
8. **RDF and triples**
9. **Graph databases**
10. **Cypher**
11. **SPARQL**
12. **Embeddings**
13. **Vector databases**
14. **RAG**
15. **LLM tool calling**
16. **Graph RAG**
17. **AI agent architecture**

---

# 18. Simple Mental Model

Think about the difference like this:

```text
Traditional Data:

Alice
OpenAI
Project Alpha
Python
```

A knowledge graph adds the meaning:

```text
Alice
   │
   ├── works_at ──> OpenAI
   │
   └── works_on ──> Project Alpha
                         │
                         └── uses ──> Python
```

The **connections are the knowledge**.

---

# 19. Knowledge Graph vs Vector Database

These technologies solve different problems.

| Technology      | Best at                               |
| --------------- | ------------------------------------- |
| SQL Database    | Structured records and transactions   |
| Vector Database | Semantic similarity                   |
| Knowledge Graph | Relationships and connected facts     |
| Search Engine   | Keyword/information retrieval         |
| LLM             | Language understanding and generation |

Modern AI systems can combine all of them:

```text
                 ┌──────────────┐
                 │     LLM      │
                 └──────┬───────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
     Vector DB      Knowledge KG    SQL DB
          │             │             │
       Similarity    Relationships   Records
```

---

# 20. Learning Path

A practical learning path is:

```text
1. Graph concepts
       ↓
2. Nodes + edges
       ↓
3. Graph data modeling
       ↓
4. Neo4j
       ↓
5. Cypher
       ↓
6. Ontologies
       ↓
7. Entity extraction
       ↓
8. Entity resolution
       ↓
9. RAG
       ↓
10. Graph RAG
       ↓
11. LLM + Knowledge Graph
       ↓
12. AI Agents + Knowledge Graph
```

## Final Takeaway

A **Knowledge Graph** is a way to represent knowledge as connected entities and relationships.

The core idea is:

```text
Entity → Relationship → Entity
```

For AI, knowledge graphs become particularly powerful when combined with:

```text
LLMs
+
RAG
+
Vector Search
+
Graph Databases
+
AI Agents
```

This combination allows AI systems to work not only with text, but also with **structured knowledge, relationships, and context**.
