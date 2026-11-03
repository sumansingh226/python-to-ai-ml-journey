#### Knowledge Graphs for AI

## Start with a problem, not a definition

Say you're building an internal AI assistant for a company. Someone asks it: *"Who works with Alice, and what are they building?"*

If all your AI has is a pile of documents and a vector database, it's in trouble. Vector search is great at finding text that *sounds like* the question — but this question isn't really about similar words. It's about a chain of facts: Alice knows Bob, Bob is on Project Alpha, Project Alpha is about to ship. No single document says all of that. The answer lives in the *connections between* facts, not in any one fact itself.

That's the gap a knowledge graph fills. It's not a fancier database — it's a different way of thinking about what "knowing something" even means.


## The core idea, in one line

A knowledge graph stores information as **things** and **the relationships between them**, instead of rows in a table.

```
Alice ──works_at──> OpenAI
```

That's it. That's the whole primitive. Everything else in this guide is just that pattern, repeated and scaled up: a subject, connected to an object, by a relationship. People in the field call this a **triple** — subject → predicate → object — but don't let the vocabulary intimidate you. It's just a sentence with the grammar made explicit.

Once you have a few of these, they start chaining into something more interesting:

```
Alice ──works_at──> OpenAI
Alice ──knows──> Bob
OpenAI ──develops──> AI Models
AI Models ──used_for──> Natural Language Processing
```

Follow the arrows and you can walk from Alice all the way to NLP without ever reading a paragraph of prose. That's the whole point: **the graph turns "here's a bunch of separate facts" into "here's how those facts relate."**

## What's actually in a graph

Every knowledge graph is built from just three ingredients.

**Entities** are the *things* — the nouns of your domain. Alice, OpenAI, a product, a city, a research paper. Nothing fancy: if you can point at it and give it a name, it's probably an entity.

**Relationships** are the *verbs* connecting them — `works_at`, `knows`, `develops`, `located_in`. This is the part people underrate. A graph with entities but weak relationships is just a list. The relationships are where the actual knowledge lives.

**Properties** are the extra detail hanging off an entity or a relationship — Alice's age, her job title, the date she joined. They don't connect to other entities; they just describe the one they belong to.

Put together, Alice's little corner of the graph looks like this:

```
Alice
 ├── name: Alice
 ├── age: 30
 ├── role: Engineer
 └── works_at ──> OpenAI
```

Notice the asymmetry: `works_at` points *outward* to another entity, while `name` and `age` just sit there as labels on Alice herself. That distinction — "does this fact point to another thing, or just describe this thing?" — is the entire skill of graph modeling in miniature.

## Why not just use a normal database?

A relational database would store the same fact like this:

| id | name  | company |
|----|-------|---------|
| 1  | Alice | OpenAI  |

Perfectly fine — for one relationship. But real knowledge doesn't stay this tidy. The moment Alice has *several* kinds of connections, a flat table starts fighting you:

```
Alice
 ├── works_at ──> OpenAI
 ├── knows ──> Bob
 ├── created ──> Project X
 └── interested_in ──> Machine Learning

Project X
 ├── uses ──> GPT
 ├── related_to ──> NLP
 └── documented_in ──> Research Paper
```

You *could* force this into rows and foreign keys, and people did that for decades. But every new relationship type means another join table, and every interesting question — "what connects Alice to this research paper, three hops away?" — turns into a query with five joins that gets slower as the data grows. A graph database is built to walk relationships instead of joining tables, so that same question stays fast no matter how many hops it takes.

## The disambiguation problem — a good reason this matters for AI specifically

Here's a scenario every NLP person has hit: the word "Apple" shows up in a sentence. Is it the company or the fruit? A language model, on its own, is guessing from context — usually a good guess, but a guess.

A knowledge graph lets you make the distinction explicit instead of implicit:

```
Apple Inc. ──type──> Company
Apple ──type──> Fruit
```

Now "knowing" isn't just a matter of the model's intuition about word patterns — there's a structured fact sitting behind it that any system can check. This is a small example, but it's the seed of a much bigger idea: **graphs give AI systems a place to store facts that are true regardless of how any particular sentence phrases them.**

## Combining knowledge graphs with LLMs

An LLM is a brilliant reasoner but a shaky rememberer — it can *reason beautifully* about facts you hand it, but it wasn't built to reliably store and retrieve millions of precise, current facts about your specific company or domain. A knowledge graph is the opposite: a perfect rememberer, no reasoning at all. Put them together and each covers the other's weak spot.

A common pattern looks like this:

```
User asks a question
        │
        ▼
   LLM identifies the entities in the question
        │
        ▼
   Those entities are looked up in the knowledge graph
        │
        ▼
   The graph returns the relevant facts and connections
        │
        ▼
   The LLM turns those facts into a natural-language answer
```

Back to our opening question — *"Who works with Alice, and what projects are they involved in?"* — here's what the graph lookup might surface:

```
Alice
 ├── works_with ──> Bob ──works_on──> Project A
 └── works_with ──> Sarah ──works_on──> Project B
```

The LLM never had to "remember" this. It just had to read a small, precise slice of the graph and describe it in plain English. That division of labor — graph for facts, LLM for language — is a big part of why knowledge graphs have made a comeback in the AI world.

## Where this connects to RAG

If you've worked with Retrieval-Augmented Generation, you've seen the classic pipeline:

```
Question → Embedding → Vector Search → Matching Documents → LLM
```

This works well when the answer sits inside *one* document that happens to be semantically similar to the question. It works less well when the answer is scattered across several documents that are connected by a *fact*, not by similar wording. "Which vendor supplies the component that failed in last month's incident?" — no single paragraph says that; it's a chain.

**Graph-based RAG** adds a relationship-following step before you ever touch the documents:

```
Question → Entity Detection → Knowledge Graph → Related Entities → Relevant Documents + Relationships → LLM
```

You're not just fetching what *sounds* relevant anymore — you're fetching what's *actually connected*, and only then handing the LLM the documents to explain it in words.

## Watching it work end-to-end

Let's build a small graph for a real use case: an AI assistant that helps a company's employees find who's doing what.

```
Alice
 ├── member_of ──> AI Team
 ├── works_on ──> Project Alpha
 └── uses ──> Python

Project Alpha
 ├── owned_by ──> AI Team
 ├── uses ──> Python
 ├── uses ──> PostgreSQL
 └── documented_in ──> Design Document

Design Document
 ├── describes ──> Project Alpha
 └── written_by ──> Alice
```

With just these three entities and their connections, the assistant can now answer a whole family of questions without a single one of them being pre-written as an FAQ: *Who works on Project Alpha? What tech does it use? Who wrote the design doc? Which team owns it?* Every answer is just a short walk along the arrows.

## How you'd actually query one

Most graph databases use a query language built around this "walk the arrows" idea. Neo4j's language, Cypher, reads almost like the diagrams above:

```cypher
MATCH (person:Person)-[:WORKS_AT]->(company:Company)
RETURN person.name, company.name;
```

In plain English: *find every person connected to a company by a WORKS_AT edge, and give me both names.* Or, to find Alice's collaborators specifically:

```cypher
MATCH (alice:Person {name: "Alice"})-[:WORKS_WITH]->(person)
RETURN person;
```

If you've written SQL before, this should feel oddly comfortable — it's still declarative, still "describe the pattern you want and let the database find it." The difference is that the pattern is a *shape in a graph* instead of a set of joined tables.

## How a graph actually gets built

Nobody hand-types thousands of triples. In practice, a knowledge graph is assembled through a pipeline:

```
Raw data (docs, DBs, APIs, emails...)
        │
        ▼
Clean it up
        │
        ▼
Extract entities  ("Alice works at OpenAI" → Alice [Person], OpenAI [Company])
        │
        ▼
Extract relationships  (Alice → works_at → OpenAI)
        │
        ▼
Resolve duplicate entities
        │
        ▼
Store in a graph database
        │
        ▼
Query it from your AI application
```

Two of these steps deserve a closer look, because they're where most of the real difficulty hides.

**Entity resolution** is the problem of realizing that "OpenAI," "OpenAI Inc.," and "OpenAI, Inc." are the same company wearing three different outfits. Skip this step and your graph fills up with duplicate ghosts of the same entity, each holding a different slice of the truth. Get it right, and all three mentions collapse into one node that carries everything you know about OpenAI.

**Ontology design** is deciding, up front, what *kinds* of things and relationships are even allowed to exist in your graph — Person, Company, Project, Document; `works_at`, `works_on`, `uses`, `documents`. This is the graph equivalent of designing a database schema, except instead of asking "what columns does this table need," you're asking "what *kinds of meaning* can this domain contain." Skip it, and you end up with a graph where one team calls something `belongs_to` and another calls the identical relationship `is_owned_by` — technically two facts, semantically one.

## Different shapes for different jobs

Not every graph technology represents things the same way. It's worth knowing the vocabulary, even briefly:

- **RDF** treats everything as pure triples — subject, predicate, object — and is the closest to the "Entity → Relationship → Entity" idea in its rawest form.
- **Property graphs** (what Neo4j uses) let nodes and relationships each carry their own bag of properties, which tends to feel more natural for application development — you can put `role: "Engineer"` directly on the Alice node rather than modeling it as yet another triple.
- **JSON** is often just the transport format — how you'd serialize a chunk of the graph to send over an API.

None of these is "more correct." They're different trade-offs between purity and practicality.

## Where this shows up in real systems

The pattern repeats across a surprising number of domains once you start looking for it:

- **Enterprise search**: `Employee → Team → Project → Document`, so a search for "who worked on the Q3 launch" can actually answer instead of just keyword-matching.
- **Recommendations**: `User → likes → Product → belongs_to → Category → related_to → other Products`, letting you recommend things a user never searched for but is connected to by taste.
- **Customer support**: `Customer → owns → Product → has_issue → Problem → solved_by → Solution`, so a support bot can trace a known issue straight to its fix.
- **Fraud detection**: `Person → owns → Account → transfers_to → Account → associated_with → Device` — fraud rings are, structurally, just unusually dense clusters in a graph.
- **Healthcare research**: `Disease → associated_with → Gene → associated_with → Protein → targeted_by → Drug`, a chain that's exactly how drug-repurposing research actually works.

Different industries, same underlying move: turn scattered facts into a walkable structure.

## Knowing when to reach for a graph — and when not to

It's tempting, once this clicks, to want to graph-ify everything. Resist that. Each of these tools is good at something different, and the best AI systems usually lean on more than one at once:

| Technology       | What it's actually good at                  |
|------------------|-----------------------------------------------|
| SQL database     | Structured records, transactions, exact lookups |
| Vector database  | "Find me things that mean something similar"  |
| Knowledge graph  | "Find me things connected by a specific fact" |
| Search engine    | Keyword and full-text retrieval               |
| LLM              | Understanding and generating language         |

A mature architecture often looks like all of them feeding one LLM at query time — vector search for "what's semantically relevant," the graph for "what's factually connected," SQL for "what's the exact current record" — with the LLM doing the final job of turning all three answers into one coherent response.

## If you want to actually build with this

There's no shortcut around building intuition step by step, but here's a sane order to learn things in — each one makes the next one click faster:

1. Nodes and edges as a concept (you basically already have this now)
2. Practical graph data modeling — deciding what's an entity vs. a property
3. A real graph database, like Neo4j, and its query language, Cypher
4. Ontology design — defining the "schema" of meaning for your domain
5. Entity extraction and entity resolution from raw text
6. RDF and SPARQL, if you need interoperability with the broader semantic-web world
7. Standard RAG, then graph-augmented RAG
8. Wiring a knowledge graph into an LLM's tool-calling loop
9. Letting an AI agent query the graph as one of several tools it has access to

## The one thing to remember

Strip away every diagram and code snippet in this guide, and you're left with a single idea:

```
Entity → Relationship → Entity
```

That's not a simplification for beginners — it's genuinely the whole mechanism, all the way up to graphs with billions of nodes. What makes knowledge graphs matter for AI right now isn't the idea alone, though; it's that we finally have language models capable of reading a graph's output and turning it into a fluent answer, and extraction techniques good enough to build the graph from messy real-world text in the first place.

The connections were always the knowledge. We just finally have the tools to use them.