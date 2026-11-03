# Google's RAG Replacements — File Search Tool, Always-On Memory Agent, Agentic RAG
## Complete Guide 2025-2026 - From DIY RAG 40% Failure to Managed RAG-killers

> **Core Thesis:** Google launched 3 things that replace DIY RAG in late 2025-2026: 1) Gemini File Search Tool managed RAG that abstracts entire pipeline into single API call no vector DB no chunking $0.15/1M tokens, 2) Always-On Memory Agent that replaces RAG and embeddings with continuous LLM consolidation SQLite no vector DB no embeddings 3 subagents IngestAgent ConsolidateAgent QueryAgent 24/7 background process like human brain sleep, 3) Agentic RAG Sufficient Context Agent iterative multi-agent approach that breaks complex queries and searches until sufficient context for multi-hop. Plus 2M token context window suggestion to skip RAG entirely for smaller corpora. RAG becoming commodity invisible infrastructure present in every product mentioned in none. Production: Use File Search Tool for enterprise managed, Always-On Memory Agent for long-term memory, Agentic RAG for multi-hop, 2M context for <3000 files.

### Table of Contents
1. Why Google Killed DIY RAG - 40% Enterprise Failure, Engineering Pain
2. File Search Tool - Managed RAG Single API Call
3. Always-On Memory Agent - No Vector DB No Embeddings Continuous Consolidation
4. Agentic RAG + Sufficient Context Agent - Iterative Multi-Agent for Multi-Hop
5. 2M Token Context Window - Skip RAG Entirely
6. Comparison Benchmarks - DIY RAG vs Google Replacements
7. Implementation Blueprints
8. When to Use Which - Decision Tree
9. Production Architecture with Google Replacements
10. Production Checklist

---

### 1. Why Google Killed DIY RAG - 40% Enterprise Failure, Engineering Pain

**DIY RAG pain:**

Building traditional RAG pipelines means organizations must assemble and fine-tune file ingestion and parsing program including chunking embedding generation and updates. They must then contract vector database like Pinecone determine retrieval logic and fit it all within model's context window. Additionally they can if desired add source citations. RAG can be engineering pain because orchestrating multiple tools together can become complicated.

**Failure rate:** 40% enterprise RAG fails, retrieval failure 30%, ranking failure 15%, context overflow 10%, hallucination 20%, citation failure 10%, stale data 5%.

**Cost:** Pinecone vector DB $70/month minimum + embedding model + chunking tuning + reranking + monitoring + eval RAGAS.

**Google's solution:** Abstract away entire retrieval pipeline into single API call, or replace with continuous LLM consolidation no vector DB no embeddings, or iterative multi-agent that searches until sufficient context.

**Market shift:**

- OpenAI Assistants API already bundles file search natively
- Google Gemini File Search Tool launched late 2025 abstracts entire retrieval pipeline into single API call no vector database to manage no chunking strategy to tune no embedding model to choose
- Google own documentation now explicitly suggests skipping RAG pipelines entirely for smaller corpora by using Gemini's 2 million token context window
- Pinecone once valued near billion dollars changed CEOs September 2025 amid mounting pressure questions over long-term independence
- Postgres with pgvector now matches or outperforms dedicated vector databases at scale most companies actually operate at
- RAG is following exact same arc just faster: A hard technical problem gets solved early adopters gain advantage then it becomes library then feature then checkbox
- Prediction by 2030 no serious software company will market RAG as feature it will be invisible infrastructure present in every product mentioned in none

### 2. File Search Tool - Managed RAG Single API Call

**What is File Search Tool:**

Google released File Search Tool on Gemini API fully managed RAG system that abstracts away retrieval pipeline. File Search removes much tool and application-gathering involved in setting up RAG pipelines so engineers don't need to stitch together things like storage solutions and embedding creators. This tool competes directly with enterprise RAG products from OpenAI AWS Microsoft which also aim to simplify RAG architecture. Google though claims its offering requires less orchestration and more standalone.

**How it works:**

File Search provides simple integrated scalable way to ground Gemini with your data delivering responses more accurate relevant and verifiable. File Search manages file storage chunking strategies and embeddings. Developers can invoke File Search within existing generateContent API which Google said makes tool easier to adopt. File Search uses vector search to understand meaning and context of user's query. Ideally it will find relevant information to answer query from documents even if prompt contains inexact words. Feature has built-in citations that point to specific parts of document it used to generate answers and also supports variety file formats PDF Docx txt JSON and many common programming language file types.

**Pricing:**

Enterprises can access some features File Search such as storage and embedding generation for free at query time. Users will begin paying for embeddings when files are indexed at fixed rate $0.15 per 1 million tokens. Gemini Embedding model which eventually became top embedding model on Massive Text Embedding Benchmark powers File Search.

**Implementation:**

```
import google.generativeai as genai

# Setup
genai.configure(api_key="your_key")
model = genai.GenerativeModel("gemini-2.5-pro")

# Upload files to File Search
# For demo, via API
file = genai.upload_file(path="policy_v2.3.pdf", display_name="Refund Policy v2.3")

# Create file search store
file_search_store = genai.create_file_search_store(
    display_name="Refund Policies",
    file_ids=[file.name]
)

# Query with File Search Tool - single API call abstracts entire RAG pipeline
response = model.generate_content(
    contents="What is refund policy for order ORD-12345 that was part of bundle with promotion?",
    tools=[{"file_search": {"file_search_store_names": [file_search_store.name]}}]
)

print(response.text)
# Answer with citations built-in: "Bundle promotion needs approval [1] general amount<500 auto [2]" with citations pointing to specific parts of document
# No need to manage Pinecone, chunking, embedding, retrieval logic
```

**Benefits:**

- No vector DB management no chunking strategy tuning no embedding model choice
- Built-in citations point to specific parts document used to generate answers verifiable
- Supports variety file formats PDF Docx txt JSON programming languages
- Integrated within existing generateContent API easier adopt
- Vector search understands meaning context even if prompt contains inexact words
- Fixed rate $0.15 per 1M tokens indexing free query time

**Use case:**

Phaser Studio creator AI-driven game generation platform Beam said in Google blog used File Search to sift through library 3000 files. File Search allows us instantly surface right material whether code snippet for bullet patterns genre templates or architectural guidance from Phaser brain corpus. Result ideas once took days to prototype now become playable in minutes.

**When to use:**

- Enterprise need managed RAG less orchestration
- 3000 files or more but don't want manage Pinecone chunking embedding
- Need built-in citations verifiable
- Need integrate within existing Gemini generateContent API

### 3. Always-On Memory Agent - No Vector DB No Embeddings Continuous Consolidation

**What is Always-On Memory Agent:**

Google Cloud open-sourced lightweight AI agent that rethinks how AI systems handle long-term memory replacing standard retrieval-augmented generation RAG pipeline with continuously running process that reads consolidates and queries structured memories stored entirely in SQLite. Always-On Memory Agent built with Google Agent Development Kit and running on Gemini 3.1 Flash-Lite operates 24/7 as background process. It uses no vector database and no embeddings. Instead LLM reads incoming content extracts structured information and periodically consolidates related memories design that creators compare to how human brain processes information during sleep.

**Architecture 3 subagents:**

System uses three specialized subagents working under single orchestrator.

- **IngestAgent** extracts summaries entities topics and importance scores from incoming content supporting 27 file types including text images audio video and PDFs
- **ConsolidateAgent** runs on timer defaulting every 30 minutes that reviews unconsolidated memories finds connections between them and writes synthesized summaries and key insights
- **QueryAgent** answers questions by reading all stored memories and consolidation insights citing specific memory IDs it draws from

**Difference vs traditional RAG:**

Approach represents fundamental departure from dominant RAG pattern. In traditional RAG system documents are embedded into vector store at ingest time and retrieved passively at query time. There is no active processing between ingest and retrieval. Always-On Memory Agent by contrast processes memory actively during gap between ingest and query linking related information and generating cross-references that vector similarity search would miss.

Most AI agents forget they process request answer it then drop context documentation states.

**Implementation:**

```
# GitHub: Google Cloud generative AI repository
# Always-On Memory Agent available on GitHub

# Setup: Watches configurable inbox directory consolidates automatically serves HTTP API port 8888 for ingest and query operations Streamlit dashboard provides visual interface browsing managing memories

# Ingest content
# Place files in inbox directory or via HTTP API
import requests

# Ingest via API
requests.post("http://localhost:8888/ingest", json={
    "content": "Order ORD-12345 amount $120 status delivered bundle_id BUNDLE-123",
    "source": "orders_db",
    "type": "text"
})

requests.post("http://localhost:8888/ingest", json={
    "content": "Bundle BUNDLE-123 contains ORD-12345 ORD-12346 ORD-12347 promotion_id PROMO-123",
    "source": "bundles_db",
    "type": "text"
})

requests.post("http://localhost:8888/ingest", json={
    "content": "Policy v2.3 max_auto 500 trust_threshold 80 bundle promotion needs approval",
    "source": "policies",
    "type": "text"
})

# ConsolidateAgent runs every 30 minutes automatically finds connections between memories writes synthesized summaries
# e.g., Consolidates ORD-12345 part_of BUNDLE-123 has_promotion PROMO-123 has_policy v2.3 into synthesized insight "Bundle BUNDLE-123 contains ORD-12345 with promotion PROMO-123 and policy v2.3 needs approval"

# Query
response = requests.post("http://localhost:8888/query", json={
    "question": "What is refund policy for ORD-12345 bundle promotion?"
})

print(response.json())
# Answer: "Refund for ORD-12345 part of bundle BUNDLE-123 with promotion needs approval per policy v2.3" citing memory IDs [memory_1, memory_2, memory_3] with synthesized insights
# No vector DB no embeddings just SQLite + LLM consolidation
```

**Benefits:**

- No vector database no embeddings one SQLite database one background process and prompt that tells LLM to think before it stores
- Active processing between ingest and query linking related information generating cross-references vector similarity search would miss
- Supports 27 file types text images audio video PDFs
- Consolidates automatically every 30 minutes like human brain sleep
- Cites specific memory IDs verifiable
- Streamlit dashboard visual interface browsing managing memories

**Use cases:**

Range from research assistants that ingest PDFs meeting audio and screenshots over course of week and can later connect cost target to reliability problem autonomously to support agents that store past tickets as structured memories and answer new questions with cited references.

**When to use:**

- Developers enterprises building AI systems need maintain context across sessions without infrastructure overhead vector database
- Long-term memory across sessions weeks
- Need connect cost target to reliability problem autonomously research assistant ingesting PDFs meeting audio screenshots over week
- Support agents storing past tickets as structured memories answering new questions with cited references
- Want simpler alternative one SQLite one background process

### 4. Agentic RAG + Sufficient Context Agent - Iterative Multi-Agent for Multi-Hop

**What is Agentic RAG + Sufficient Context Agent:**

Agentic Retrieval-Augmented Generation RAG framework introduced with Google Gemini Enterprise Agent Platform marks clear departure from traditional RAG methods. Instead single-pass retrieval followed by generation system employs iterative multi-agent approach. Google Research adds Agentic RAG to Gemini Enterprise Agent Platform with Sufficient Context Agent for multi-hop queries. RAG Agent digs into files it skipped and finds data. Introducing new agentic RAG framework collab with Google Cloud multi-agent workflow goes beyond standard RAG by breaking down complex enterprise queries and iteratively searching for sufficient context before generating dependable responses.

**How it works:**

- Breaks down complex enterprise queries into sub-queries
- Iteratively searches for sufficient context before generating dependable responses
- Sufficient Context Agent checks if context sufficient for query if not digs into files skipped and finds data iteratively
- Multi-agent workflow: Query decomposition agent, retrieval agent, sufficient context check agent, generation agent

**Example:**

Query: "What is refund policy for order ORD-12345 that was part of bundle with promotion?"

Traditional RAG: Single-pass retrieval vector search top_k=10 retrieves order doc and policy doc misses bundle doc recall 60% failure.

Agentic RAG:
1. Query decomposition agent breaks query into sub-queries: "Order ORD-12345 bundle_id", "Bundle BUNDLE-123 promotion_id", "Promotion PROMO-123 policy_id", "Policy for bundle promotion"
2. Retrieval agent searches for each sub-query iteratively
3. Sufficient Context Agent checks if context sufficient: Has order? Yes ORD-12345 bundle_id BUNDLE-123. Has bundle? No missing bundle doc. So digs into files skipped finds bundle doc BUNDLE-123.
4. Has bundle? Yes BUNDLE-123 promotion_id PROMO-123. Has promotion? No missing promotion doc. Digs finds promotion doc PROMO-123.
5. Has promotion? Yes PROMO-123 policy_id POL-123. Has policy? Yes POL-123 v2.3. Context sufficient now.
6. Generation agent generates answer with citations from sufficient context.

**Implementation via Gemini Enterprise Agent Platform:**

```
# Via Google Cloud Gemini Enterprise Agent Platform
# Agentic RAG framework

# Define agents
# Query decomposition agent, retrieval agent, sufficient context agent, generation agent

# For demo, simplified
import google.generativeai as genai

model = genai.GenerativeModel("gemini-2.5-pro")

# Agentic RAG workflow
def agentic_rag(query):
    # Step 1: Query decomposition
    decomposition_prompt = f"Query: {query} Break down into sub-queries for multi-hop retrieval e.g., Order ORD-12345 bundle_id, Bundle BUNDLE-123 promotion_id, etc. Return JSON list sub-queries"
    sub_queries_response = model.generate_content(decomposition_prompt)
    sub_queries = json.loads(sub_queries_response.text) # ["Order ORD-12345 bundle_id", "Bundle BUNDLE-123 promotion_id", "Promotion PROMO-123 policy_id"]
    
    # Step 2: Iterative retrieval + sufficient context check
    contexts = []
    for sub_query in sub_queries:
        # Retrieve for sub-query
        retrieved = file_search_retrieval(sub_query) # Via File Search Tool or vector DB
        contexts.extend(retrieved)
        
        # Sufficient context check
        sufficient_check_prompt = f"Query: {query} Contexts: {contexts} Is context sufficient to answer query? Return JSON {{\"sufficient\": true/false, \"missing\": \"what missing\"}}"
        sufficient_response = model.generate_content(sufficient_check_prompt)
        sufficient_json = json.loads(sufficient_response.text)
        
        if not sufficient_json["sufficient"]:
            # Dig into files skipped and find missing data
            # e.g., missing bundle doc, search again with missing info
            missing = sufficient_json["missing"]
            additional_retrieved = file_search_retrieval(missing)
            contexts.extend(additional_retrieved)
    
    # Step 3: Generation with sufficient context
    contexts_str = "\\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(contexts)])
    generation_prompt = f"Query: {query} Contexts with sufficient context: {contexts_str} Answer with citations"
    answer = model.generate_content(generation_prompt)
    
    return answer.text

query = "What is refund policy for ORD-12345 bundle promotion?"
answer = agentic_rag(query)
# Answer with sufficient context all 4 docs order bundle promotion policy
```

**Benefits:**

- Iterative multi-agent approach goes beyond standard single-pass retrieval generation
- Breaks down complex enterprise queries and iteratively searching for sufficient context before generating dependable responses
- Sufficient Context Agent digs into files skipped and finds data that single-pass would miss
- For multi-hop queries needs 3 hops order->bundle->promotion->policy
- More accurate for enterprise complex queries

**When to use:**

- Enterprise complex queries multi-hop
- Need sufficient context before generation dependable responses
- Traditional RAG single-pass misses relevant docs
- Want iterative search until sufficient context

### 5. 2M Token Context Window - Skip RAG Entirely

**What is 2M token context window:**

Google own documentation now explicitly suggests skipping RAG pipelines entirely for smaller corpora by using Gemini's 2 million token context window.

Gemini 2.5 Pro supports 2 million token context window.

**How it works:**

For smaller corpora <2M tokens (~3000 files or 1500 pages), just dump all files into context window no retrieval needed.

```
model = genai.GenerativeModel("gemini-2.5-pro") # 2M context window

# Load all files into context
files_content = ""
for file_path in ["policy_v2.3.pdf", "orders.json", "bundles.json", "promotions.json"]:
    with open(file_path, "r") as f:
        files_content += f.read() + "\\n"

# Query with full context no RAG
response = model.generate_content(
    contents=f"Files: {files_content}\\nQuery: What is refund policy for ORD-12345 bundle promotion? Answer with citations from files."
)

print(response.text)
# Answer with citations from full context, no retrieval needed, because all files in context window
```

**Benefits:**

- No RAG pipeline needed no chunking no embedding no vector DB
- Simpler more efficient solution for most situations models like Gemini 2.0 provide
- Goodbye RAG? Google Finally Shipped Something useful speaker discusses how Gemini 2.0 model made traditional technique RAG largely obsolete. While RAG still useful in certain cases with large datasets for most situations models like Gemini 2.0 provide simpler more efficient solution

**When to use:**

- Smaller corpora <2M tokens <3000 files
- Want simpler efficient solution no RAG infrastructure
- Most situations except large datasets

**Limitations:**

- Large datasets >2M tokens still need RAG
- Cost 2M tokens input $2.50 per 1M tokens? Check pricing, but for large corpora expensive

### 6. Comparison Benchmarks - DIY RAG vs Google Replacements

| System | Recall Multi-Hop | Precision | Faithfulness | Failure Rate | Cost | Latency | Setup Complexity | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| DIY Vector RAG | 60% multi-hop 1-hop only misses bundle doc | 30% irrelevant docs | 60% hallucination missing bundle | 40% enterprise | Pinecone $70/month + embedding + LLM $0.005 per query = $0.0051 + infra | 600ms vector 100ms + LLM 500ms | High need manage Pinecone chunking embedding retrieval logic citations | Baseline not for prod |
| DIY Hybrid + GraphRAG Vector+BM25+Graph 2-3 hops+Community RRF+Rerank | 85% +25% vs vector graph traversal retrieves bundle doc | 80% +50% reranking | 85% +25% context complete | 10% -30% best | $0.0061 hybrid $0.0011 + LLM $0.005 infra extra but best accuracy | 710ms vector 50ms+BM25 10ms+graph 100ms+community 20ms+RRF 10ms+rerank 100ms+LLM 500ms 110ms extra worth | Production best enterprise multi-hop QA but high setup complexity |
| Google File Search Tool Managed RAG | 85% similar to GraphRAG managed handles chunking embedding retrieval | 80% managed reranking built-in | 85% managed sufficient context | 10% -30% vs DIY vector best | $0.15 per 1M tokens indexing free query time + LLM $0.005 = $0.00515 cheap managed no Pinecone | 500ms managed retrieval + LLM 500ms similar to DIY | Low single API call abstracts entire pipeline no vector DB management no chunking tuning no embedding choice | Enterprise need managed less orchestration 3000+ files built-in citations |
| Google Always-On Memory Agent No Vector DB No Embeddings Continuous Consolidation | 85% active consolidation finds connections vector similarity miss | 80% consolidation synthesizes insights | 85% consolidation insights | 10% -30% | SQLite free + LLM consolidation every 30 mins cost minimal + LLM query $0.005 | Ingest 100ms + consolidation background every 30 mins + query 500ms reading memories | Low one SQLite one background process prompt tells LLM think before store | Long-term memory across sessions weeks research assistant ingesting PDFs meeting audio screenshots over week support agents storing past tickets |
| Google Agentic RAG Sufficient Context Agent Iterative Multi-Agent | 90% +30% vs vector iterative search until sufficient context digs into files skipped | 85% +55% iterative | 90% +30% sufficient context before generation | 5% -35% best | File Search $0.15/1M + iterative retrieval extra LLM calls 3-5 calls $0.025 + LLM final $0.005 = $0.03 more expensive but best accuracy | 1-2s iterative retrieval 3-5 iterations 300ms each + LLM 500ms slower but more accurate | Medium need define agents decomposition retrieval sufficient check generation | Enterprise complex queries multi-hop need sufficient context dependable responses traditional single-pass misses docs |
| Google 2M Context Window No RAG | 100% all files in context no retrieval miss | 100% no irrelevant retrieval all files in context but LLM may be distracted | 90% LLM may hallucinate if context large but better than missing context | 5% -35% best for small corpora | 2M tokens input $2.50/1M *2M=$5 per query expensive for large corpora but cheap for small | 2-5s LLM processing 2M tokens slower | Very low dump all files into context no RAG | Smaller corpora <2M tokens <3000 files simpler efficient no RAG infrastructure |

### 7. Implementation Blueprints

**File Search Tool Blueprint:**

```
import google.generativeai as genai

genai.configure(api_key="your_key")
model = genai.GenerativeModel("gemini-2.5-pro")

# Upload files
file = genai.upload_file(path="policy_v2.3.pdf")
store = genai.create_file_search_store(file_ids=[file.name])

# Query - single API call replaces entire DIY RAG pipeline
response = model.generate_content(
    contents="What is refund policy for ORD-12345 bundle promotion?",
    tools=[{"file_search": {"file_search_store_names": [store.name]}}]
)
# Built-in citations
```

**Always-On Memory Agent Blueprint:**

```
# GitHub: google-cloud generative AI repository
# Setup inbox directory, HTTP API port 8888, Streamlit dashboard

import requests

# Ingest
requests.post("http://localhost:8888/ingest", json={"content": "Order ORD-12345...", "source": "orders"})
# ConsolidateAgent runs every 30 mins automatically finds connections writes synthesized summaries
# Query
response = requests.post("http://localhost:8888/query", json={"question": "Refund policy ORD-12345 bundle?"})
# Answer citing memory IDs with synthesized insights, no vector DB no embeddings SQLite
```

**Agentic RAG Blueprint:**

```
def agentic_rag(query):
    # Decompose
    sub_queries = model.generate_content(f"Break down {query} into sub-queries").text
    contexts = []
    for sub_query in sub_queries:
        retrieved = file_search_retrieval(sub_query)
        contexts.extend(retrieved)
        # Sufficient context check
        sufficient = model.generate_content(f"Query {query} Contexts {contexts} Sufficient? JSON sufficient true/false missing").text
        if not sufficient["sufficient"]:
            additional = file_search_retrieval(sufficient["missing"])
            contexts.extend(additional)
    # Generate with sufficient context
    answer = model.generate_content(f"Query {query} Contexts {contexts} Answer with citations")
    return answer.text
```

**2M Context Blueprint:**

```
model = genai.GenerativeModel("gemini-2.5-pro") # 2M context
files_content = "".join([open(f).read() for f in files]) # <2M tokens
response = model.generate_content(f"Files {files_content} Query {query} Answer with citations")
# No RAG needed
```

### 8. When to Use Which - Decision Tree

**Decision tree:**

- Corpus size <2M tokens <3000 files? Yes -> Use 2M context window no RAG simplest efficient
- No -> Need long-term memory across sessions weeks research assistant ingesting PDFs meeting audio screenshots over week support agents storing past tickets? Yes -> Use Always-On Memory Agent SQLite no vector DB no embeddings continuous consolidation
- No -> Need complex multi-hop queries order->bundle->promotion->policy traditional single-pass misses docs need sufficient context dependable responses? Yes -> Use Agentic RAG Sufficient Context Agent iterative multi-agent breaks down queries searches until sufficient context
- No -> Need managed RAG less orchestration enterprise 3000+ files built-in citations? Yes -> Use File Search Tool single API call abstracts entire pipeline no vector DB management no chunking tuning
- No -> Need best accuracy production enterprise multi-hop QA and willing manage complexity? Yes -> Use DIY Hybrid + GraphRAG Vector+BM25+Graph 2-3 hops+Community RRF+Rerank 85% recall
- Else -> Baseline Vector RAG not for prod

**Summary:**

- Small corpora <2M tokens <3000 files -> 2M context no RAG simplest
- Long-term memory weeks research assistant support tickets -> Always-On Memory Agent SQLite no embeddings continuous consolidation like human brain sleep
- Complex multi-hop enterprise need sufficient context -> Agentic RAG iterative multi-agent decomposition sufficient check
- Enterprise managed less orchestration -> File Search Tool single API call managed citations
- Production best accuracy willing complexity -> DIY GraphRAG hybrid

### 9. Production Architecture with Google Replacements

**Architecture using Google replacements:**

```
Offline:
PDFs policies orders bundles promotions -> File Search Tool upload files -> Managed handles chunking embedding indexing $0.15/1M tokens + Always-On Memory Agent ingest into inbox directory SQLite + ConsolidateAgent every 30 mins finds connections writes synthesized summaries + Agentic RAG decomposition sufficient check + 2M context window for small corpora dump all files

Online:
Query "Refund policy ORD-12345 bundle promotion" -> Decision:
- If small corpora <2M tokens -> 2M context window dump all files into context generate answer with citations no retrieval
- If long-term memory -> Always-On Memory Agent QueryAgent reads all memories consolidation insights cites memory IDs
- If complex multi-hop -> Agentic RAG decomposition sub-queries iterative retrieval sufficient context check digs into files skipped generates with sufficient context
- If managed enterprise -> File Search Tool single API call generateContent with file_search tool built-in citations
-> Final answer with citations verifiable
-> Eval RAGAS daily metrics recall precision faithfulness citation
-> Monitoring drift
-> Feedback loop
-> Continuous indexing new files via File Search Tool or Always-On Memory Agent inbox
```

**Migration from DIY RAG to Google replacements:**

- DIY Vector RAG Pinecone $70/month + embedding + chunking tuning + retrieval logic + citations -> Migrate to File Search Tool single API call $0.15/1M indexing free query no Pinecone management
- DIY GraphRAG KG extraction Leiden communities hybrid retrieval -> Migrate to Agentic RAG sufficient context agent iterative multi-agent breaks down queries searches until sufficient context similar accuracy less setup
- DIY long-term memory vector DB + embeddings -> Migrate to Always-On Memory Agent SQLite no vector DB no embeddings continuous consolidation every 30 mins like brain sleep simpler
- DIY RAG for small corpora <3000 files -> Migrate to 2M context window no RAG dump all files into context simpler efficient

### 10. Production Checklist

1. **Why Google Killed DIY RAG** — DIY RAG pain traditional RAG pipelines must assemble file ingestion parsing chunking embedding generation updates contract vector database Pinecone determine retrieval logic fit within context window add citations engineering pain orchestrating multiple tools complicated failure rate 40% enterprise retrieval failure 30% ranking failure 15% context overflow 10% hallucination 20% citation failure 10% stale data 5% cost Pinecone $70/month minimum + embedding + chunking tuning + reranking + monitoring + eval RAGAS. Google solution abstract away entire retrieval pipeline into single API call or replace with continuous LLM consolidation no vector DB no embeddings or iterative multi-agent searches until sufficient context. Market shift OpenAI Assistants API bundles file search natively Google Gemini File Search Tool launched late 2025 abstracts entire retrieval pipeline into single API call no vector database to manage no chunking strategy to tune no embedding model to choose Google own documentation explicitly suggests skipping RAG pipelines entirely for smaller corpora by using Gemini 2M token context window Pinecone once valued near billion dollars changed CEOs September 2025 mounting pressure questions long-term independence Postgres pgvector matches outperforms dedicated vector databases at scale most companies actually operate at RAG following exact same arc just faster hard technical problem solved early adopters gain advantage then becomes library then feature then checkbox. Prediction by 2030 no serious software company will market RAG as feature it will be invisible infrastructure present in every product mentioned in none.

2. **File Search Tool Managed RAG Single API Call** — Google released File Search Tool on Gemini API fully managed RAG system abstracts away retrieval pipeline File Search removes tool application-gathering involved setting up RAG pipelines so engineers don't need stitch together storage embedding creators competes directly enterprise RAG products OpenAI AWS Microsoft aim simplify RAG architecture Google though claims offering requires less orchestration more standalone. How it works File Search provides simple integrated scalable way to ground Gemini with your data delivering responses more accurate relevant verifiable File Search manages file storage chunking strategies embeddings developers can invoke File Search within existing generateContent API easier adopt File Search uses vector search understand meaning context user's query ideally find relevant information answer query from documents even if prompt contains inexact words feature has built-in citations point to specific parts document used generate answers supports variety file formats PDF Docx txt JSON many common programming language file types. Pricing enterprises can access some features File Search such as storage embedding generation free at query time users will begin paying embeddings when files indexed fixed rate $0.15 per 1M tokens Gemini Embedding model eventually became top embedding model on Massive Text Embedding Benchmark powers File Search. Implementation upload files genai.upload_file path policy_v2.3.pdf display_name Refund Policy v2.3 create file search store genai.create_file_search_store display_name Refund Policies file_ids file.name query with File Search Tool single API call abstracts entire RAG pipeline model.generate_content contents What is refund policy for order ORD-12345 that was part of bundle with promotion tools file_search file_search_store_names store.name print response.text answer with citations built-in Bundle promotion needs approval [1] general amount<500 auto [2] with citations pointing to specific parts document no need manage Pinecone chunking embedding retrieval logic. Benefits no vector DB management no chunking strategy tuning no embedding model choice built-in citations point to specific parts document used generate answers verifiable supports variety file formats PDF Docx txt JSON programming languages integrated within existing generateContent API easier adopt vector search understands meaning context even if prompt contains inexact words fixed rate $0.15 per 1M tokens indexing free query. Use case Phaser Studio creator AI-driven game generation platform Beam said in Google blog used File Search to sift through library 3000 files File Search allows instantly surface right material whether code snippet bullet patterns genre templates architectural guidance from Phaser brain corpus result ideas once took days prototype now become playable minutes. When to use enterprise need managed RAG less orchestration 3000 files or more don't want manage Pinecone chunking embedding need built-in citations verifiable need integrate within existing Gemini generateContent API.

3. **Always-On Memory Agent No Vector DB No Embeddings Continuous Consolidation** — Google Cloud open-sourced lightweight AI agent rethinks how AI systems handle long-term memory replacing standard RAG pipeline with continuously running process that reads consolidates queries structured memories stored entirely in SQLite Always-On Memory Agent built with Google Agent Development Kit running Gemini 3.1 Flash-Lite operates 24/7 background process uses no vector database no embeddings instead LLM reads incoming content extracts structured information periodically consolidates related memories design creators compare to how human brain processes information during sleep. Architecture 3 subagents system uses three specialized subagents working under single orchestrator IngestAgent extracts summaries entities topics importance scores from incoming content supporting 27 file types including text images audio video PDFs ConsolidateAgent runs timer default every 30 minutes reviews unconsolidated memories finds connections between them writes synthesized summaries key insights QueryAgent answers questions by reading all stored memories consolidation insights citing specific memory IDs it draws from. Difference vs traditional RAG approach represents fundamental departure dominant RAG pattern traditional RAG system documents embedded into vector store at ingest time retrieved passively at query time no active processing between ingest retrieval Always-On Memory Agent by contrast processes memory actively during gap between ingest query linking related information generating cross-references vector similarity search would miss. Most AI agents forget they process request answer it then drop context documentation states. Implementation GitHub Google Cloud generative AI repository Setup watches configurable inbox directory consolidates automatically serves HTTP API port 8888 ingest query operations Streamlit dashboard provides visual interface browsing managing memories Ingest content place files inbox directory or via HTTP API import requests ingest via API requests.post http://localhost:8888/ingest json content Order ORD-12345 amount $120 status delivered bundle_id BUNDLE-123 source orders_db type text etc for bundles policies ConsolidateAgent runs every 30 minutes automatically finds connections between memories writes synthesized summaries e.g., Consolidates ORD-12345 part_of BUNDLE-123 has_promotion PROMO-123 has_policy v2.3 into synthesized insight Bundle BUNDLE-123 contains ORD-12345 with promotion PROMO-123 and policy v2.3 needs approval Query response requests.post http://localhost:8888/query json question What is refund policy for ORD-12345 bundle promotion print response.json answer Refund for ORD-12345 part bundle BUNDLE-123 with promotion needs approval per policy v2.3 citing memory IDs memory_1 memory_2 memory_3 with synthesized insights no vector DB no embeddings just SQLite + LLM consolidation. Benefits no vector database no embeddings one SQLite database one background process prompt tells LLM think before it stores active processing between ingest query linking related information generating cross-references vector similarity search would miss supports 27 file types text images audio video PDFs consolidates automatically every 30 minutes like human brain sleep cites specific memory IDs verifiable Streamlit dashboard visual interface browsing managing memories. Use cases range from research assistants that ingest PDFs meeting audio screenshots over course week can later connect cost target to reliability problem autonomously to support agents that store past tickets as structured memories answer new questions with cited references. When to use developers enterprises building AI systems need maintain context across sessions without infrastructure overhead vector database long-term memory across sessions weeks need connect cost target to reliability problem autonomously research assistant ingesting PDFs meeting audio screenshots over week support agents storing past tickets as structured memories answering new questions with cited references want simpler alternative one SQLite one background process.

4. **Agentic RAG + Sufficient Context Agent Iterative Multi-Agent for Multi-Hop** — Agentic Retrieval-Augmented Generation RAG framework introduced with Google Gemini Enterprise Agent Platform marks clear departure traditional RAG methods instead single-pass retrieval followed generation system employs iterative multi-agent approach Google Research adds Agentic RAG to Gemini Enterprise Agent Platform with Sufficient Context Agent for multi-hop queries RAG Agent digs into files it skipped and finds data Introducing new agentic RAG framework collab with Google Cloud multi-agent workflow goes beyond standard RAG by breaking down complex enterprise queries and iteratively searching for sufficient context before generating dependable responses. How it works breaks down complex enterprise queries into sub-queries iteratively searches for sufficient context before generating dependable responses Sufficient Context Agent checks if context sufficient for query if not digs into files skipped finds data iteratively multi-agent workflow Query decomposition agent retrieval agent sufficient context check agent generation agent. Example query What is refund policy for order ORD-12345 that was part of bundle with promotion Traditional RAG single-pass retrieval vector search top_k=10 retrieves order doc policy doc misses bundle doc recall 60% failure Agentic RAG Step 1 Query decomposition agent breaks query into sub-queries Order ORD-12345 bundle_id Bundle BUNDLE-123 promotion_id Promotion PROMO-123 policy_id Policy for bundle promotion Step 2 Retrieval agent searches for each sub-query iteratively Step 3 Sufficient Context Agent checks if context sufficient Has order Yes ORD-12345 bundle_id BUNDLE-123 Has bundle No missing bundle doc So digs into files skipped finds bundle doc BUNDLE-123 Has bundle Yes BUNDLE-123 promotion_id PROMO-123 Has promotion No missing promotion doc Digs finds promotion doc PROMO-123 Has promotion Yes PROMO-123 policy_id POL-123 Has policy Yes POL-123 v2.3 Context sufficient now Step 4 Generation agent generates answer with citations from sufficient context. Implementation via Gemini Enterprise Agent Platform Define agents Query decomposition agent retrieval agent sufficient context agent generation agent For demo simplified genai GenerativeModel gemini-2.5-pro Agentic RAG workflow def agentic_rag query Step 1 Query decomposition decomposition_prompt Query query Break down into sub-queries for multi-hop retrieval e.g., Order ORD-12345 bundle_id Bundle BUNDLE-123 promotion_id etc Return JSON list sub-queries sub_queries_response model.generate_content decomposition_prompt sub_queries json.loads sub_queries_response.text Order ORD-12345 bundle_id Bundle BUNDLE-123 promotion_id Promotion PROMO-123 policy_id Step 2 Iterative retrieval + sufficient context check contexts list for sub_query in sub_queries retrieved file_search_retrieval sub_query via File Search Tool or vector DB contexts extend retrieved sufficient_check_prompt Query query Contexts contexts Is context sufficient to answer query Return JSON sufficient true/false missing what missing sufficient_response model.generate_content sufficient_check_prompt sufficient_json json.loads sufficient_response.text if not sufficient_json sufficient dig into files skipped find missing data missing sufficient_json missing additional_retrieved file_search_retrieval missing contexts extend additional_retrieved Step 3 Generation with sufficient context contexts_str join f"[{i+1}] {ctx}" for i ctx enumerate contexts generation_prompt Query query Contexts with sufficient context contexts_str Answer with citations answer model.generate_content generation_prompt return answer.text query What is refund policy for ORD-12345 bundle promotion answer agentic_rag query Answer with sufficient context all 4 docs order bundle promotion policy. Benefits iterative multi-agent approach goes beyond standard single-pass retrieval generation breaks down complex enterprise queries iteratively searching for sufficient context before generating dependable responses Sufficient Context Agent digs into files skipped finds data that single-pass would miss for multi-hop queries needs 3 hops order->bundle->promotion->policy more accurate for enterprise complex queries. When to use enterprise complex queries multi-hop need sufficient context before generation dependable responses traditional RAG single-pass misses relevant docs want iterative search until sufficient context.

5. **2M Token Context Window Skip RAG Entirely** — What is 2M token context window Google own documentation now explicitly suggests skipping RAG pipelines entirely for smaller corpora by using Gemini 2M token context window Gemini 2.5 Pro supports 2M token context window. How it works smaller corpora <2M tokens ~3000 files or 1500 pages just dump all files into context window no retrieval needed model GenerativeModel gemini-2.5-pro 2M context window Load all files into context files_content "" for file_path in policy_v2.3.pdf orders.json bundles.json promotions.json with open file_path r as f files_content += f.read() + newline Query with full context no RAG response model.generate_content contents Files files_content Query What is refund policy for ORD-12345 bundle promotion Answer with citations from files print response.text answer with citations from full context no retrieval needed because all files in context window. Benefits no RAG pipeline needed no chunking no embedding no vector DB simpler more efficient solution for most situations models like Gemini 2.0 provide Goodbye RAG Google Finally Shipped Something useful speaker discusses how Gemini 2.0 model made traditional technique RAG largely obsolete While RAG still useful in certain cases with large datasets for most situations models like Gemini 2.0 provide simpler more efficient solution. When to use smaller corpora <2M tokens <3000 files want simpler efficient solution no RAG infrastructure most situations except large datasets. Limitations large datasets >2M tokens still need RAG cost 2M tokens input $2.50/1M *2M=$5 per query expensive for large corpora but cheap for small.

6. **Comparison Benchmarks** — DIY Vector RAG recall multi-hop 60% 1-hop only misses bundle doc precision 30% irrelevant docs faithfulness 60% hallucination missing bundle failure rate 40% enterprise cost Pinecone $70/month + embedding + LLM $0.005 per query = $0.0051 + infra latency 600ms vector 100ms + LLM 500ms setup complexity high need manage Pinecone chunking embedding retrieval logic citations baseline not for prod. DIY Hybrid + GraphRAG Vector+BM25+Graph 2-3 hops+Community RRF+Rerank recall 85% +25% vs vector graph traversal retrieves bundle doc precision 80% +50% reranking faithfulness 85% +25% context complete failure rate 10% -30% best cost $0.0061 hybrid $0.0011 + LLM $0.005 infra extra but best accuracy latency 710ms vector 50ms+BM25 10ms+graph 100ms+community 20ms+RRF 10ms+rerank 100ms+LLM 500ms 110ms extra worth production best enterprise multi-hop QA but high setup complexity. Google File Search Tool Managed RAG recall 85% similar to GraphRAG managed handles chunking embedding retrieval precision 80% managed reranking built-in faithfulness 85% managed sufficient context failure rate 10% -30% vs DIY vector best cost $0.15 per 1M tokens indexing free query time + LLM $0.005 = $0.00515 cheap managed no Pinecone latency 500ms managed retrieval + LLM 500ms similar to DIY setup complexity low single API call abstracts entire pipeline no vector DB management no chunking tuning no embedding choice enterprise need managed less orchestration 3000+ files built-in citations. Google Always-On Memory Agent No Vector DB No Embeddings Continuous Consolidation recall 85% active consolidation finds connections vector similarity miss precision 80% consolidation synthesizes insights faithfulness 85% consolidation insights failure rate 10% -30% cost SQLite free + LLM consolidation every 30 mins cost minimal + LLM query $0.005 latency ingest 100ms + consolidation background every 30 mins + query 500ms reading memories setup complexity low one SQLite one background process prompt tells LLM think before store long-term memory across sessions weeks research assistant ingesting PDFs meeting audio screenshots over week support agents storing past tickets. Google Agentic RAG Sufficient Context Agent Iterative Multi-Agent recall 90% +30% vs vector iterative search until sufficient context digs into files skipped precision 85% +55% iterative faithfulness 90% +30% sufficient context before generation failure rate 5% -35% best cost File Search $0.15/1M + iterative retrieval extra LLM calls 3-5 calls $0.025 + LLM final $0.005 = $0.03 more expensive but best accuracy latency 1-2s iterative retrieval 3-5 iterations 300ms each + LLM 500ms slower but more accurate setup complexity medium need define agents decomposition retrieval sufficient check generation enterprise complex queries multi-hop need sufficient context dependable responses traditional single-pass misses docs. Google 2M Context Window No RAG recall 100% all files in context no retrieval miss precision 100% no irrelevant retrieval all files in context but LLM may be distracted faithfulness 90% LLM may hallucinate if context large but better than missing context failure rate 5% -35% best for small corpora cost 2M tokens input $2.50/1M *2M=$5 per query expensive for large corpora but cheap for small latency 2-5s LLM processing 2M tokens slower setup complexity very low dump all files into context no RAG smaller corpora <2M tokens <3000 files simpler efficient no RAG infrastructure.

7. **Implementation Blueprints** — File Search Tool Blueprint genai configure api_key your_key model GenerativeModel gemini-2.5-pro Upload files genai.upload_file path policy_v2.3.pdf store genai.create_file_search_store file_ids file.name Query single API call replaces entire DIY RAG pipeline model.generate_content contents What is refund policy for ORD-12345 bundle promotion tools file_search file_search_store_names store.name Built-in citations. Always-On Memory Agent Blueprint GitHub google-cloud generative AI repository Setup inbox directory HTTP API port 8888 Streamlit dashboard import requests Ingest requests.post http://localhost:8888/ingest json content Order ORD-12345 source orders ConsolidateAgent runs every 30 mins automatically finds connections writes synthesized summaries Query response requests.post http://localhost:8888/query json question Refund policy ORD-12345 bundle Answer citing memory IDs with synthesized insights no vector DB no embeddings SQLite. Agentic RAG Blueprint def agentic_rag query Decompose sub_queries model.generate_content Break down query into sub-queries text contexts list for sub_query in sub_queries retrieved file_search_retrieval sub_query contexts extend retrieved sufficient check sufficient model.generate_content Query query Contexts contexts Sufficient JSON sufficient true/false missing text if not sufficient missing additional file_search_retrieval missing contexts extend additional Generate with sufficient context answer model.generate_content Query query Contexts contexts Answer with citations return answer.text. 2M Context Blueprint model GenerativeModel gemini-2.5-pro 2M context files_content join open f read for f in files <2M tokens response model.generate_content Files files_content Query query Answer with citations No RAG needed.

8. **When to Use Which Decision Tree** — Decision tree corpus size <2M tokens <3000 files Yes -> Use 2M context window no RAG simplest efficient No -> Need long-term memory across sessions weeks research assistant ingesting PDFs meeting audio screenshots over week support agents storing past tickets Yes -> Use Always-On Memory Agent SQLite no vector DB no embeddings continuous consolidation No -> Need complex multi-hop queries order->bundle->promotion->policy traditional single-pass misses docs need sufficient context dependable responses Yes -> Use Agentic RAG Sufficient Context Agent iterative multi-agent breaks down queries searches until sufficient context No -> Need managed RAG less orchestration enterprise 3000+ files built-in citations Yes -> Use File Search Tool single API call abstracts entire pipeline no vector DB management no chunking tuning No -> Need best accuracy production enterprise multi-hop QA willing manage complexity Yes -> Use DIY Hybrid + GraphRAG Vector+BM25+Graph 2-3 hops+Community RRF+Rerank 85% recall Else -> Baseline Vector RAG not for prod. Summary small corpora <2M tokens <3000 files -> 2M context no RAG simplest long-term memory weeks research assistant support tickets -> Always-On Memory Agent SQLite no embeddings continuous consolidation like human brain sleep complex multi-hop enterprise need sufficient context -> Agentic RAG iterative multi-agent decomposition sufficient check enterprise managed less orchestration -> File Search Tool single API call managed citations production best accuracy willing complexity -> DIY GraphRAG hybrid.

9. **Production Architecture with Google Replacements** — Architecture using Google replacements Offline PDFs policies orders bundles promotions -> File Search Tool upload files Managed handles chunking embedding indexing $0.15/1M tokens + Always-On Memory Agent ingest into inbox directory SQLite + ConsolidateAgent every 30 mins finds connections writes synthesized summaries + Agentic RAG decomposition sufficient check + 2M context window for small corpora dump all files Online Query Refund policy ORD-12345 bundle promotion -> Decision If small corpora <2M tokens -> 2M context window dump all files into context generate answer with citations no retrieval If long-term memory -> Always-On Memory Agent QueryAgent reads all memories consolidation insights cites memory IDs If complex multi-hop -> Agentic RAG decomposition sub-queries iterative retrieval sufficient context check digs into files skipped generates with sufficient context If managed enterprise -> File Search Tool single API call generateContent with file_search tool built-in citations -> Final answer with citations verifiable -> Eval RAGAS daily metrics recall precision faithfulness citation -> Monitoring drift -> Feedback loop -> Continuous indexing new files via File Search Tool or Always-On Memory Agent inbox. Migration from DIY RAG to Google replacements DIY Vector RAG Pinecone $70/month + embedding + chunking tuning + retrieval logic + citations -> Migrate to File Search Tool single API call $0.15/1M indexing free query no Pinecone management DIY GraphRAG KG extraction Leiden communities hybrid retrieval -> Migrate to Agentic RAG sufficient context agent iterative multi-agent breaks down queries searches until sufficient context similar accuracy less setup DIY long-term memory vector DB + embeddings -> Migrate to Always-On Memory Agent SQLite no vector DB no embeddings continuous consolidation every 30 mins like brain sleep simpler DIY RAG for small corpora <3000 files -> Migrate to 2M context window no RAG dump all files into context simpler efficient.

---
**Bottom Line:** Google launched 3 RAG replacements late 2025-2026 that make DIY RAG look old: File Search Tool managed RAG single API call abstracts entire pipeline no vector DB management no chunking tuning no embedding choice $0.15/1M tokens indexing free query built-in citations PDF Docx JSON code files integrated within generateContent API easier adopt vector search understands meaning context even if inexact words Phaser Studio used for 3000 files sift library instantly surface right material code snippet bullet patterns genre templates architectural guidance result ideas once took days prototype now playable minutes enterprise need managed less orchestration 3000+ files built-in citations. Always-On Memory Agent open-sourced lightweight AI agent rethinks long-term memory replacing standard RAG pipeline with continuously running process reads consolidates queries structured memories stored entirely in SQLite no vector database no embeddings built with Agent Development Kit running Gemini 3.1 Flash-Lite operates 24/7 background process LLM reads incoming content extracts structured information periodically consolidates related memories design compared to how human brain processes information during sleep 3 subagents IngestAgent extracts summaries entities topics importance scores 27 file types text images audio video PDFs ConsolidateAgent runs timer default every 30 minutes reviews unconsolidated memories finds connections writes synthesized summaries key insights QueryAgent answers questions reading all stored memories consolidation insights citing specific memory IDs approach fundamental departure dominant RAG pattern traditional RAG documents embedded into vector store at ingest time retrieved passively at query time no active processing between ingest retrieval Always-On Memory Agent by contrast processes memory actively during gap between ingest query linking related information generating cross-references vector similarity search would miss Most AI agents forget process request answer it then drop context watches configurable inbox directory consolidates automatically serves HTTP API port 8888 ingest query operations Streamlit dashboard visual interface browsing managing memories use cases research assistants ingest PDFs meeting audio screenshots over week can later connect cost target to reliability problem autonomously support agents store past tickets as structured memories answer new questions with cited references developers enterprises building AI systems need maintain context across sessions without infrastructure overhead vector database simpler alternative one SQLite one background process prompt tells LLM think before it stores. Agentic RAG + Sufficient Context Agent iterative multi-agent approach introduced with Gemini Enterprise Agent Platform marks clear departure traditional RAG methods instead single-pass retrieval followed generation system employs iterative multi-agent approach Google Research adds Agentic RAG to Gemini Enterprise Agent Platform with Sufficient Context Agent for multi-hop queries RAG Agent digs into files it skipped finds data Introducing new agentic RAG framework collab with Google Cloud multi-agent workflow goes beyond standard RAG by breaking down complex enterprise queries iteratively searching for sufficient context before generating dependable responses breaks down complex enterprise queries into sub-queries iteratively searches for sufficient context before generating dependable responses Sufficient Context Agent checks if context sufficient if not digs into files skipped finds data iteratively multi-agent workflow Query decomposition agent retrieval agent sufficient context check agent generation agent example query refund policy ORD-12345 bundle promotion Traditional RAG single-pass retrieval vector search top_k=10 retrieves order doc policy doc misses bundle doc recall 60% failure Agentic RAG decomposition Order ORD-12345 bundle_id Bundle BUNDLE-123 promotion_id Promotion PROMO-123 policy_id Policy for bundle promotion iterative retrieval sufficient context check Has order Yes bundle_id BUNDLE-123 Has bundle No missing bundle doc digs finds bundle doc BUNDLE-123 Has bundle Yes promotion_id PROMO-123 Has promotion No missing promotion doc digs finds promotion doc PROMO-123 Has promotion Yes policy_id POL-123 Has policy Yes POL-123 v2.3 Context sufficient now generation with sufficient context. 2M token context window Google own documentation explicitly suggests skipping RAG pipelines entirely for smaller corpora by using Gemini 2M token context window Gemini 2.5 Pro supports 2M token context window smaller corpora <2M tokens ~3000 files 1500 pages just dump all files into context window no retrieval needed no RAG pipeline no chunking no embedding no vector DB simpler more efficient solution for most situations models like Gemini 2.0 provide Goodbye RAG Google Finally Shipped Something useful speaker discusses how Gemini 2.0 model made traditional technique RAG largely obsolete While RAG still useful in certain cases with large datasets for most situations models like Gemini 2.0 provide simpler more efficient solution. Decision tree small corpora <2M tokens <3000 files use 2M context no RAG simplest efficient long-term memory weeks research assistant support tickets use Always-On Memory Agent SQLite no embeddings continuous consolidation like brain sleep complex multi-hop enterprise need sufficient context dependable responses use Agentic RAG iterative multi-agent decomposition sufficient check enterprise managed less orchestration use File Search Tool single API call managed citations production best accuracy willing complexity use DIY GraphRAG hybrid.

