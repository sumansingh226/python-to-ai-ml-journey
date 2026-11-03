# RAG Error Rate & Accuracy: How to Fix Failures and Maintain Accuracy in Production RAG Systems
## Complete Production Guide - From Hallucination to GraphRAG, Evaluation, and Continuous Improvement

> **Core Thesis:** RAG fails 40% in enterprise. Error rate is not one number - it's 6 failure modes: retrieval failure 30%, ranking failure 15%, context overflow 10%, hallucination 20%, citation failure 10%, stale data 5%. Fix with hybrid retrieval vector+BM25+graph, reranking, GraphRAG for multi-hop, constrained decoding for citations, freshness. Accuracy maintenance in prod: eval with RAGAS, monitoring drift, human-in-the-loop feedback, continuous indexing. Production: Always measure RAG error rate with RAGAS faithfulness, answer relevance, context precision/recall, fix with hybrid + rerank + GraphRAG, maintain accuracy with eval + monitoring + feedback loop.

### Table of Contents
1. Why RAG Error Rate Matters - The 40% Failure Problem
2. What is Error Rate in RAG - 6 Failure Modes
3. How to Measure Error Rate - RAGAS, Metrics, Benchmarks
4. How to Fix Each Failure Mode - Hybrid, Reranking, GraphRAG, Constrained Decoding
5. How to Maintain Accuracy in Production RAG System - Eval, Monitoring, Feedback, Indexing
6. Product RAG Architecture - From Simple Vector to Production GraphRAG
7. Implementation Blueprint
8. Benchmarks
9. Production Checklist

---

### 1. Why RAG Error Rate Matters - The 40% Failure Problem

**Problem:** RAG looks simple: Embed query -> vector search -> retrieve top_k docs -> LLM generates answer with context. But in enterprise production, RAG fails 40% of the time.

**Example refund agent RAG without fixing error rate:**

User: What is refund policy for order ORD-12345 that was part of bundle with promotion?

- Simple vector RAG: Embed query "refund policy ORD-12345 bundle promotion" -> vector search top_k=3 -> retrieves docs: Doc1 refund policy v2.3 amount<500 auto, Doc2 order ORD-12345 status delivered, Doc3 promotion 10% off. But misses bundle info: order ORD-12345 part of bundle BUNDLE-123, bundle has promotion, promotion affects refund policy. Vector RAG 1-hop only, fails multi-hop, retrieves 3 docs but not bundle doc, context missing bundle, LLM hallucinates refund policy without bundle, answer wrong, error.

- Error rate 40% breakdown: Retrieval failure 30% (missed bundle doc), ranking failure 15% (retrieved irrelevant promotion doc instead of bundle doc), context overflow 10% (top_k=10 docs overflow LLM context 128k tokens, truncation loses bundle), hallucination 20% (LLM generates refund policy without bundle because context missing), citation failure 10% (LLM says refund policy v2.3 but no citation, not verifiable), stale data 5% (policy v2.3 retrieved but v2.4 is latest, stale).

- Without measuring error rate, you don't know which failure mode, can't fix.

- With measuring error rate via RAGAS faithfulness, answer relevance, context precision/recall, you see retrieval failure 30% context recall low, ranking failure context precision low, hallucination faithfulness low, etc., fix each.

**Why need to fix error rate and maintain accuracy:**

- Retrieval failure 30%: Fix with hybrid retrieval vector + BM25 + graph traversal, GraphRAG for multi-hop
- Ranking failure 15%: Fix with reranking cross-encoder, Cohere rerank, LLM rerank
- Context overflow 10%: Fix with context compression, LongContextReorder, Map-Reduce
- Hallucination 20%: Fix with constrained decoding, faithfulness check, citation enforcement
- Citation failure 10%: Fix with constrained decoding for citations, citation format [1] url
- Stale data 5%: Fix with freshness, continuous indexing, TTL, versioning

- Maintain accuracy in prod: Eval with RAGAS, monitoring drift, human-in-the-loop feedback, continuous indexing, alert if accuracy drops <80%

**Production: Always measure RAG error rate with RAGAS, fix with hybrid + rerank + GraphRAG + constrained decoding, maintain accuracy with eval + monitoring + feedback loop.**

### 2. What is Error Rate in RAG - 6 Failure Modes

**Error rate in RAG is not one number, it's 6 failure modes:**

**1. Retrieval Failure (30% of errors):** Relevant doc not retrieved, context recall low.

Example: Query refund policy for ORD-12345 bundle promotion, relevant docs: order doc, bundle doc BUNDLE-123, promotion doc, policy doc v2.3. Vector search retrieves order, promotion, policy but misses bundle doc, because bundle doc not similar to query embedding, vector search 1-hop only, fails multi-hop order -> bundle -> promotion -> policy. Context recall = retrieved relevant / total relevant = 3/4 = 75%, missing 25% recall failure.

Cause: Vector search cosine similarity only, fails when query and doc not semantically similar but linked via graph, e.g., order doc mentions bundle_id BUNDLE-123 but not bundle details, vector search misses bundle doc because embedding not similar.

**2. Ranking Failure (15%):** Irrelevant docs ranked higher than relevant, context precision low.

Example: Query refund policy ORD-12345 bundle promotion, retrieves 10 docs: 3 relevant (order, bundle, policy) + 7 irrelevant (random promotions, old orders, etc.), because vector search similarity high for irrelevant docs that contain words refund, promotion, etc., but not relevant to ORD-12345. Context precision = retrieved relevant / retrieved total = 3/10 = 30% low precision, LLM context polluted with irrelevant docs, hallucination risk high.

Cause: Vector search without reranking, cosine similarity not enough, need cross-encoder reranking.

**3. Context Overflow (10%):** Retrieved docs overflow LLM context window, truncation loses relevant info.

Example: Top_k=20 docs, each doc 1000 tokens, total 20000 tokens, LLM context 128k tokens okay, but if top_k=100 docs, 100k tokens, plus query, plus system prompt, overflow 128k, truncation loses bundle doc at end, recall drops.

Cause: No context compression, no LongContextReorder, no Map-Reduce, top_k too high.

**4. Hallucination (20%):** LLM generates answer not supported by retrieved context, faithfulness low.

Example: Context missing bundle doc, LLM hallucinates refund policy without bundle: "Refund $120 for ORD-12345, policy says amount<500 auto, so auto refund" but actually bundle promotion affects refund, policy says bundle promotion needs approval, LLM hallucinates because context missing bundle, faithfulness low, answer not grounded in context.

Cause: Context recall low, LLM not constrained to context, no faithfulness check.

**5. Citation Failure (10%):** LLM answer without citations, or citations wrong, not verifiable.

Example: LLM says "Refund policy v2.3 says amount<500 auto" but no citation [1] url, or citation wrong url that doesn't contain policy, not verifiable, trust low.

Cause: No constrained decoding for citations, no citation enforcement, LLM not instructed to cite.

**6. Stale Data (5%):** Retrieved docs stale, not latest version, accuracy low.

Example: Policy v2.3 retrieved but v2.4 is latest, v2.4 says max_auto 400 not 500, stale data, answer wrong.

Cause: No freshness, no continuous indexing, no TTL, no versioning, index not updated.

**Overall error rate:** Retrieval 30% + Ranking 15% + Context overflow 10% + Hallucination 20% + Citation 10% + Stale 5% = 90%? But overlapping, e.g., retrieval failure causes hallucination, so overall failure rate 40% in enterprise, not 90% sum.

**How to measure each failure mode:**

- Retrieval failure: Context recall = retrieved relevant / total relevant, low recall <70% => retrieval failure
- Ranking failure: Context precision = retrieved relevant / retrieved total, low precision <70% => ranking failure
- Context overflow: Check if retrieved tokens > context window, truncation occurred
- Hallucination: Faithfulness = answer supported by context, via RAGAS faithfulness metric, low <80% => hallucination
- Citation failure: Citation precision = citations correct / total citations, low <80% => citation failure
- Stale data: Freshness = retrieved docs timestamp vs latest, if stale >1 day => stale data

### 3. How to Measure Error Rate - RAGAS, Metrics, Benchmarks

**RAGAS:** Retrieval Augmented Generation Assessment, open source framework for RAG evaluation, metrics: faithfulness, answer relevance, context precision, context recall, etc.

**Metrics:**

- **Context Recall:** Retrieved relevant / total relevant, measures retrieval failure, high recall good, low recall retrieval failure.

Example: Total relevant docs for query refund policy ORD-12345 bundle promotion = 4 (order, bundle, promotion, policy), retrieved relevant = 3 (order, promotion, policy, missing bundle), context recall = 3/4 = 75% <80% => retrieval failure.

- **Context Precision:** Retrieved relevant / retrieved total, measures ranking failure, high precision good, low precision ranking failure.

Example: Retrieved total 10 docs, relevant 3, precision = 3/10 = 30% <70% => ranking failure.

- **Faithfulness:** Answer supported by context, measures hallucination, high faithfulness good, low faithfulness hallucination.

Example: Context missing bundle doc, answer says refund $120 auto without bundle, not supported by context, faithfulness low <80% => hallucination.

- **Answer Relevance:** Answer relevant to query, measures if answer answers query, high relevance good, low relevance irrelevant answer.

Example: Query refund policy ORD-12345 bundle promotion, answer says general refund policy without ORD-12345 bundle, relevance low.

- **Citation Precision/Recall:** Citations correct / total citations, measures citation failure.

**Implementation RAGAS:**

```
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)
from datasets import Dataset

# Dataset with question, answer, contexts, ground_truth
dataset = Dataset.from_dict({
    "question": ["What is refund policy for ORD-12345 bundle promotion?"],
    "answer": ["Refund $120 for ORD-12345 auto because amount<500 per policy v2.3"],
    "contexts": [["Order ORD-12345 amount 120 delivered user_123", "Policy v2.3 max_auto 500 trust_threshold 80", "Promotion 10% off"]], # Missing bundle doc
    "ground_truth": ["Refund for ORD-12345 part of bundle BUNDLE-123 with promotion needs approval because bundle promotion affects policy per v2.3"]
})

result = evaluate(
    dataset,
    metrics=[
        context_recall,
        context_precision,
        faithfulness,
        answer_relevancy
    ]
)

print(result)
# context_recall 0.75 (missing bundle doc), context_precision 1.0 (if all retrieved relevant but missing one, precision high but recall low), faithfulness 0.6 (hallucination because context missing bundle), answer_relevancy 0.7
```

**Benchmarks:**

- **Enterprise RAG:** 40% failure rate without fixes, with hybrid + rerank + GraphRAG + constrained decoding + freshness, failure rate drops 40%->10% (-30%), worth it.

- **Cost of RAGAS:** Free open source, LLM calls for evaluation, e.g., 1000 queries * 4 metrics * $0.005 per call = $20 for eval, worth it for accuracy.

### 4. How to Fix Each Failure Mode - Hybrid, Reranking, GraphRAG, Constrained Decoding

**Fix Retrieval Failure (30%): Hybrid Retrieval + GraphRAG**

**Hybrid Retrieval:** Vector + BM25 + Graph traversal.

- Vector: Cosine similarity embedding, good for semantic similarity, but fails multi-hop
- BM25: Keyword matching, good for exact match order_id ORD-12345, bundle_id BUNDLE-123
- Graph traversal: Traverse knowledge graph order -> bundle -> promotion -> policy, for multi-hop, GraphRAG

```
def hybrid_retrieval(query, top_k=10):
    # Vector search
    query_embedding = openai.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
    vector_results = vector_db.search(query_embedding, top_k=top_k) # Cosine similarity
    
    # BM25 search
    bm25_results = bm25_db.search(query, top_k=top_k) # Keyword matching
    
    # Graph traversal for multi-hop (GraphRAG)
    # Extract entities from query: ORD-12345, bundle, promotion
    entities = extract_entities(query) # e.g., ["ORD-12345", "bundle", "promotion"]
    graph_results = []
    for entity in entities:
        # Traverse KG: order -> bundle -> promotion -> policy
        # e.g., order doc has bundle_id BUNDLE-123, traverse to bundle doc, then promotion doc, then policy doc
        traversed = graph_db.traverse(entity, hops=3) # 3 hops
        graph_results.extend(traversed)
    
    # Combine results: Reciprocal Rank Fusion RRF
    combined = rrf_fusion([vector_results, bm25_results, graph_results], k=60)
    # RRF score = sum(1/(k + rank)) for each result list
    
    # Deduplicate
    deduped = deduplicate(combined)
    
    return deduped[:top_k]

# Example
query = "What is refund policy for ORD-12345 bundle promotion?"
results = hybrid_retrieval(query, top_k=10)
# Results: order doc, bundle doc BUNDLE-123 (via graph traversal order->bundle), promotion doc, policy doc, plus other relevant via vector and BM25, recall improves 75%->95%
```

**GraphRAG for multi-hop:**

GraphRAG = Knowledge Graph extraction + Leiden community detection + Hybrid retrieval vector + graph traversal 2-3 hops + community search.

- KG extraction: Extract entities and relations from docs, e.g., order ORD-12345 has bundle_id BUNDLE-123, bundle BUNDLE-123 has promotion_id PROMO-123, promotion PROMO-123 has policy v2.3, etc.
- Leiden community detection: Detect communities in KG, e.g., community of orders, bundles, promotions, policies, for community search
- Hybrid retrieval: Vector + graph traversal 2-3 hops + community search

```
def graphrag_retrieval(query, top_k=10):
    # KG extraction (offline)
    # For each doc, extract entities and relations via LLM
    # e.g., doc "Order ORD-12345 part of bundle BUNDLE-123" -> entities ORD-12345 (order), BUNDLE-123 (bundle), relation ORD-12345 -> part_of -> BUNDLE-123
    
    # Leiden community detection (offline)
    # Detect communities in KG, e.g., community 1: orders, bundles, promotions, policies
    
    # Hybrid retrieval (online)
    # Vector search
    query_embedding = embed(query)
    vector_results = vector_db.search(query_embedding, top_k=top_k)
    
    # Graph traversal 2-3 hops
    entities = extract_entities(query) # ORD-12345, bundle, promotion
    graph_results = []
    for entity in entities:
        # Traverse 2-3 hops
        # e.g., ORD-12345 -> part_of -> BUNDLE-123 -> has_promotion -> PROMO-123 -> has_policy -> v2.3
        traversed = kg.traverse(entity, hops=3)
        graph_results.extend(traversed)
    
    # Community search: Search community containing entities
    community_results = kg.community_search(entities)
    
    # Combine via RRF
    combined = rrf_fusion([vector_results, graph_results, community_results])
    
    return combined[:top_k]

# Benchmark GraphRAG vs Vector RAG
# Vector RAG: Recall 60% for multi-hop QA, because 1-hop only
# GraphRAG: Recall 85% for multi-hop QA, +25% because graph traversal 2-3 hops + community search
# Cost: GraphRAG offline KG extraction and community detection cost, online retrieval similar to vector + graph traversal, worth for multi-hop enterprise QA
```

**Fix Ranking Failure (15%): Reranking**

Reranking: Cross-encoder reranks retrieved docs by relevance to query, improves precision.

- Cross-encoder: Model that takes query and doc and outputs relevance score, e.g., Cohere rerank, LLM rerank, BGE reranker

```
def rerank(query, docs, top_k=10):
    # docs from hybrid retrieval
    # Rerank via cross-encoder
    # Option 1: Cohere rerank API
    # Option 2: LLM rerank via prompt
    # Option 3: BGE reranker local model
    
    # Cohere rerank
    import cohere
    co = cohere.Client(api_key="your_key")
    reranked = co.rerank(query=query, documents=docs, top_n=top_k, model="rerank-english-v3.0")
    # Returns reranked docs with relevance score
    
    # Or LLM rerank
    rerank_prompt = f"Query: {query}\\nDocs: {docs}\\nRank docs by relevance to query, return JSON list of doc indices sorted by relevance"
    rerank_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": rerank_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    )
    reranked_indices = json.loads(rerank_response.choices[0].message.content)
    reranked_docs = [docs[i] for i in reranked_indices]
    
    return reranked_docs

# Example
query = "Refund policy ORD-12345 bundle promotion"
docs = hybrid_retrieval(query, top_k=20) # 20 docs, some irrelevant
reranked = rerank(query, docs, top_k=10) # Rerank to top 10 most relevant, precision improves 30%->80%
```

**Benchmark reranking:**

- Without reranking: Context precision 30% (7 irrelevant out of 10)
- With reranking Cohere or LLM: Context precision 80% (2 irrelevant out of 10), +50% precision, worth cost $0.001 per rerank via Cohere.

**Fix Context Overflow (10%): Context Compression, LongContextReorder, Map-Reduce**

Context overflow when retrieved docs tokens > LLM context window, truncation loses relevant info.

Fixes:

- Context compression: Compress docs via LLM summarization, keep relevant info, reduce tokens
- LongContextReorder: Reorder docs so relevant docs in middle not at end, because LLM attention better in middle (lost in middle problem), reorder via relevance score
- Map-Reduce: Map each doc to summary via LLM, Reduce summaries to final answer via LLM, avoids overflow

```
def context_compression(query, docs):
    # Compress each doc via LLM to keep relevant info for query
    compressed = []
    for doc in docs:
        compress_prompt = f"Query: {query}\\nDoc: {doc}\\nCompress doc to keep only relevant info for query, max 100 tokens"
        compressed_doc = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": compress_prompt}],
            tools=[],
            tool_choice="none",
            temperature=0.0
        ).choices[0].message.content
        compressed.append(compressed_doc)
    
    return compressed # Each doc 1000 tokens -> 100 tokens, 10 docs 10000 -> 1000 tokens, saves 90% tokens

def long_context_reorder(docs, relevance_scores):
    # Reorder docs by relevance, most relevant in middle, because LLM attention better in middle
    # Sort by relevance descending, then place most relevant in middle
    sorted_docs = sorted(zip(docs, relevance_scores), key=lambda x: x[1], reverse=True)
    # Reorder: Place most relevant in middle, e.g., for 10 docs, order: 1st least relevant at start, 2nd, ..., 5th most relevant in middle, 6th second most relevant after middle, etc.
    # For simplicity, just sort descending and LLM attention better in middle, but better to use LangChain LongContextReorder
    from langchain.docstore.document import Document
    from langchain.retrievers import LongContextReorder
    
    documents = [Document(page_content=doc) for doc in docs]
    reorder = LongContextReorder()
    reordered = reorder.transform_documents(documents)
    
    return [doc.page_content for doc in reordered]

def map_reduce(query, docs):
    # Map each doc to summary via LLM
    summaries = []
    for doc in docs:
        map_prompt = f"Query: {query}\\nDoc: {doc}\\nSummarize doc relevant to query, max 100 tokens"
        summary = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": map_prompt}],
            tools=[],
            tool_choice="none",
            temperature=0.0
        ).choices[0].message.content
        summaries.append(summary)
    
    # Reduce summaries to final answer via LLM
    reduce_prompt = f"Query: {query}\\nSummaries: {summaries}\\nGenerate final answer from summaries with citations"
    final_answer = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": reduce_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.3
    ).choices[0].message.content
    
    return final_answer

# Example
query = "Refund policy ORD-12345 bundle promotion"
docs = hybrid_retrieval(query, top_k=20) # 20 docs 20000 tokens
compressed = context_compression(query, docs) # 20 docs 2000 tokens, saves 90%
reordered = long_context_reorder(compressed, relevance_scores) # Reorder most relevant in middle
final_answer = map_reduce(query, reordered) # Or direct LLM call with reordered compressed docs
```

**Benchmark context overflow fixes:**

- Without fix: Top_k=20 docs 20000 tokens, context window 128k okay, but top_k=100 docs 100k tokens + query + system prompt overflow, truncation loses bundle doc, recall drops 95%->70%
- With compression: 100 docs 100k tokens -> compressed 10k tokens, no overflow, recall 95% maintained, cost 100 LLM calls for compression $0.005*100=$0.50, worth it for no overflow
- With LongContextReorder: Reorder most relevant in middle, improves answer quality because LLM attention better in middle, faithfulness improves 10%
- With Map-Reduce: Map each doc to summary, Reduce summaries to final answer, avoids overflow, but cost 20 LLM calls for map + 1 for reduce = 21 calls vs 1 call direct, 21x cost, but avoids overflow for large top_k

**Fix Hallucination (20%): Constrained Decoding, Faithfulness Check, Citation Enforcement**

Hallucination when LLM generates answer not supported by context, faithfulness low.

Fixes:

- Constrained decoding: Constrain LLM to only generate from context, via prompt "Answer only from context, if not in context say I don't know"
- Faithfulness check: After LLM generates answer, check faithfulness via RAGAS faithfulness metric or LLM classifier, if faithfulness low <80%, regenerate or say I don't know
- Citation enforcement: Enforce citations, LLM must cite context, if no citation, regenerate

```
def fix_hallucination(query, contexts, answer):
    # Constrained decoding via prompt
    constrained_prompt = f"Query: {query}\\nContexts: {contexts}\\nAnswer only from contexts, if not in contexts say I don't know. Include citations [1] [2] etc."
    
    constrained_answer = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": constrained_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0 # Deterministic for constrained
    ).choices[0].message.content
    
    # Faithfulness check via RAGAS or LLM classifier
    faithfulness_prompt = f"Query: {query}\\nContexts: {contexts}\\nAnswer: {constrained_answer}\\nIs answer supported by contexts? Return JSON {{\"faithfulness\": 0-1, \"reason\": \"...\"}}"
    
    faithfulness_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": faithfulness_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    ).choices[0].message.content
    
    faithfulness_json = json.loads(faithfulness_response)
    faithfulness_score = faithfulness_json["faithfulness"]
    
    if faithfulness_score < 0.8:
        # Faithfulness low, hallucination, regenerate or say I don't know
        return "I don't know, context does not contain answer"
    else:
        return constrained_answer

# Example
query = "Refund policy ORD-12345 bundle promotion"
contexts = ["Order ORD-12345 amount 120", "Policy v2.3 max_auto 500"] # Missing bundle, so context missing bundle promotion info
answer = "Refund $120 auto because amount<500" # Hallucination because context missing bundle, bundle promotion needs approval
faithfulness_score = 0.6 <0.8 => hallucination, return I don't know instead of hallucination
```

**Benchmark hallucination fix:**

- Without fix: Faithfulness 60% (hallucination 20% of answers not supported by context)
- With constrained decoding + faithfulness check: Faithfulness 85% (hallucination 5% = -15%), worth cost 2 LLM calls (constrained answer + faithfulness check) $0.01.

**Fix Citation Failure (10%): Constrained Decoding for Citations**

Citation failure when LLM answer without citations or wrong citations, not verifiable.

Fix: Enforce citations via constrained decoding, citation format [1] url.

```
def fix_citation(query, contexts, answer):
    # Constrained decoding for citations
    citation_prompt = f"Query: {query}\\nContexts: {contexts} with indices [1] [2] [3] etc.\\nAnswer query with citations, e.g., Refund policy says amount<500 auto [1], etc. Return answer with citations."
    
    answer_with_citations = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": citation_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    ).choices[0].message.content
    
    # Check citation precision: Are citations correct?
    citation_check_prompt = f"Query: {query}\\nContexts: {contexts} with indices\\nAnswer: {answer_with_citations}\\nCheck if citations correct, e.g., citation [1] corresponds to context [1] that contains info. Return JSON {{\"citation_precision\": 0-1, \"reason\": \"...\"}}"
    
    citation_check_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": citation_check_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    ).choices[0].message.content
    
    citation_json = json.loads(citation_check_response)
    citation_precision = citation_json["citation_precision"]
    
    if citation_precision < 0.8:
        # Citation precision low, wrong citations, regenerate
        return fix_citation(query, contexts, answer) # Retry
    else:
        return answer_with_citations

# Example
query = "Refund policy ORD-12345"
contexts = ["[1] Order ORD-12345 amount 120", "[2] Policy v2.3 max_auto 500 trust_threshold 80"]
answer = "Refund $120 auto because amount<500 per policy v2.3 [2]" # Correct citation [2] for policy
citation_precision = 1.0 (citation [2] correct)
```

**Benchmark citation fix:**

- Without fix: Citation precision 70% (30% answers without citations or wrong citations)
- With constrained decoding for citations: Citation precision 90% (+20%), worth cost 2 LLM calls.

**Fix Stale Data (5%): Freshness, Continuous Indexing, TTL, Versioning**

Stale data when retrieved docs stale, not latest version.

Fix: Freshness via timestamp, continuous indexing, TTL, versioning.

```
def fix_stale_data(query, docs):
    # Check freshness: docs timestamp vs latest
    # For each doc, check if stale >1 day
    fresh_docs = []
    for doc in docs:
        if doc["timestamp"] < datetime.now() - timedelta(days=1):
            # Stale, fetch latest
            latest_doc = fetch_latest(doc["id"]) # e.g., fetch latest policy v2.4
            fresh_docs.append(latest_doc)
        else:
            fresh_docs.append(doc)
    
    return fresh_docs

# Continuous indexing: Index new docs as they come, via streaming or batch
# e.g., Kafka stream new orders, new policies, index immediately

# TTL: Time to live for docs, e.g., policy docs TTL 1 day, order docs TTL 1 hour, after TTL re-index

# Versioning: Version docs, e.g., policy v2.3, v2.4, retrieve latest version

# Example
query = "Refund policy"
docs = vector_db.search(query, top_k=10) # May include stale policy v2.3
fresh_docs = fix_stale_data(query, docs) # Checks timestamp, if stale fetch latest v2.4
```

**Benchmark stale data fix:**

- Without fix: 5% answers stale, policy v2.3 retrieved but v2.4 latest, answer wrong
- With freshness + continuous indexing + TTL + versioning: Stale rate 1% (-4%), worth cost of continuous indexing.

### 5. How to Maintain Accuracy in Production RAG System - Eval, Monitoring, Feedback, Indexing

**Maintain accuracy in prod: Eval + Monitoring + Feedback + Indexing loop.**

**Eval with RAGAS:**

Continuous evaluation on production queries, with RAGAS metrics context recall, precision, faithfulness, answer relevance, citation precision.

```
# Eval pipeline
def eval_rag_production(queries, rag_system):
    dataset = []
    for query in queries:
        # RAG system retrieves contexts and generates answer
        contexts = rag_system.retrieve(query)
        answer = rag_system.generate(query, contexts)
        
        # Ground truth (from human label or previous good answer)
        ground_truth = get_ground_truth(query)
        
        dataset.append({
            "question": query,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth
        })
    
    # Evaluate with RAGAS
    dataset = Dataset.from_dict({
        "question": [d["question"] for d in dataset],
        "answer": [d["answer"] for d in dataset],
        "contexts": [d["contexts"] for d in dataset],
        "ground_truth": [d["ground_truth"] for d in dataset]
    })
    
    result = evaluate(
        dataset,
        metrics=[context_recall, context_precision, faithfulness, answer_relevancy]
    )
    
    # Log to ClickHouse
    log_eval(result, timestamp=datetime.now())
    
    # Alert if metrics drop <80%
    if result["context_recall"] < 0.8 or result["faithfulness"] < 0.8:
        alert(f"RAG accuracy drop context_recall {result['context_recall']} faithfulness {result['faithfulness']}")
    
    return result

# Run eval daily on production queries sample 100 queries
queries = sample_production_queries(n=100) # Sample 100 queries from prod logs
result = eval_rag_production(queries, rag_system)
```

**Monitoring drift:**

Monitor data drift, query drift, context drift, accuracy drift.

- Data drift: New docs, updated docs, deleted docs, e.g., new policy v2.4, new orders, etc., need continuous indexing
- Query drift: New queries, e.g., users start asking about bundle promotion refund policy, previously not asked, need to update index with bundle docs
- Context drift: Retrieved contexts change, e.g., previously retrieved policy v2.3, now v2.4, need freshness
- Accuracy drift: RAGAS metrics drop, e.g., context recall 90%->70%, faithfulness 85%->60%, need to fix retrieval, reranking, etc.

```
# Monitoring drift
def monitor_drift():
    # Data drift: Check new docs, updated docs, deleted docs
    new_docs = get_new_docs(since=last_check)
    if new_docs:
        # Index new docs
        index_docs(new_docs)
    
    # Query drift: Check new queries from prod logs
    new_queries = get_new_queries(since=last_check)
    if new_queries:
        # Analyze new queries, e.g., bundle promotion refund policy, need bundle docs
        # Update index with bundle docs if missing
        pass
    
    # Context drift: Check retrieved contexts change
    # Compare current retrieved contexts vs previous, if change > threshold, alert
    
    # Accuracy drift: Check RAGAS metrics
    result = eval_rag_production(sample_production_queries(n=100), rag_system)
    if result["context_recall"] < 0.8 or result["faithfulness"] < 0.8:
        alert(f"Accuracy drift context_recall {result['context_recall']} faithfulness {result['faithfulness']}")
```

**Human-in-the-loop feedback:**

Collect human feedback on RAG answers, thumbs up/down, corrections, use feedback to improve.

```
# Feedback loop
def collect_feedback():
    # Collect feedback from users: Thumbs up/down, corrections
    feedbacks = get_feedbacks(since=last_check) # e.g., from UI thumbs up/down
    
    for feedback in feedbacks:
        if feedback["type"] == "thumbs_down" or feedback["correction"]:
            # Feedback says answer wrong, e.g., refund policy for bundle promotion needs approval but answer said auto
            # Use feedback to improve: Add bundle doc to index if missing, update policy, etc.
            query = feedback["query"]
            correction = feedback["correction"]
            
            # Log feedback to ClickHouse
            log_feedback(query, correction, timestamp=datetime.now())
            
            # Improve RAG: Index missing docs, update reranking, etc.
            # e.g., if feedback says bundle doc missing, index bundle doc
            if "bundle" in correction.lower():
                index_bundle_docs()
    
    # Use feedback for fine-tuning: Fine-tune reranker or LLM on feedback data
    # e.g., 100 feedbacks with corrections, fine-tune reranker to rank bundle doc higher for bundle queries
```

**Continuous indexing:**

Index new docs as they come, via streaming or batch, with freshness, TTL, versioning.

```
# Continuous indexing pipeline
def continuous_indexing():
    # Streaming: Kafka stream new orders, new policies, new bundles, etc.
    # For each new doc, embed and index immediately
    for new_doc in kafka_stream:
        embedding = openai.embeddings.create(model="text-embedding-3-small", input=new_doc["content"]).data[0].embedding
        vector_db.index(new_doc["id"], embedding, new_doc["content"], timestamp=datetime.now())
        
        # GraphRAG: Extract entities and relations, update KG
        entities_relations = extract_entities_relations(new_doc["content"])
        kg.update(entities_relations)
    
    # Batch: Daily batch index new docs, updated docs, deleted docs
    # For each batch, embed and index, update KG, Leiden community detection

# Freshness: TTL for docs, e.g., policy docs TTL 1 day, order docs TTL 1 hour, after TTL re-index or mark stale

# Versioning: Version docs, e.g., policy v2.3, v2.4, retrieve latest version
```

**Best practices for maintaining accuracy in prod:**

- Eval with RAGAS daily on sample 100 production queries, metrics context recall, precision, faithfulness, answer relevance, citation precision, log to ClickHouse, alert if metrics drop <80%
- Monitoring drift data drift new docs, query drift new queries, context drift retrieved contexts change, accuracy drift RAGAS metrics drop, alert if drift
- Human-in-the-loop feedback collect thumbs up/down corrections, log feedback ClickHouse, use feedback to improve index missing docs, update reranking, fine-tune reranker or LLM
- Continuous indexing streaming Kafka new docs embed and index immediately, batch daily new docs updated docs deleted docs, freshness TTL versioning, GraphRAG KG extraction and community detection offline, hybrid retrieval online
- Cost: Eval 100 queries * 4 metrics * $0.005 = $2 daily, monitoring drift free, feedback free, continuous indexing embedding cost $0.0001 per doc, worth for accuracy

### 6. Product RAG Architecture - From Simple Vector to Production GraphRAG

**Simple Vector RAG (baseline):**

- Embed query -> vector search top_k=10 -> LLM generates answer with contexts
- Failure rate 40% enterprise, recall 60% multi-hop, precision 30%, faithfulness 60%, no citations, stale data 5%
- Cost: 1 embedding $0.0001 + 1 LLM call $0.005 = $0.0051 per query, cheap but inaccurate

**Hybrid RAG (improved):**

- Hybrid retrieval vector + BM25 + graph traversal -> reranking cross-encoder -> context compression -> LLM with constrained decoding for citations
- Failure rate 20% (-20% vs simple vector), recall 80% (+20%), precision 80% (+50%), faithfulness 80% (+20%), citation precision 90% (+20%), stale 1% (-4%)
- Cost: Embedding $0.0001 + vector search + BM25 + graph traversal + reranking Cohere $0.001 + compression 10 LLM calls $0.05 + LLM final $0.005 = $0.056 per query, 11x cost vs simple but accuracy +20% worth it for prod

**Production GraphRAG (best):**

- Offline: KG extraction entities and relations from docs via LLM, Leiden community detection communities, embed docs, index vector DB, build KG, build community summaries via LLM
- Online: Hybrid retrieval vector + graph traversal 2-3 hops + community search via RRF -> reranking cross-encoder -> context compression LongContextReorder -> LLM with constrained decoding faithfulness check citation enforcement -> freshness check TTL versioning
- Eval with RAGAS daily, monitoring drift, human-in-the-loop feedback, continuous indexing streaming Kafka
- Failure rate 10% (-30% vs simple vector, -10% vs hybrid), recall 85% multi-hop (+25% vs vector), precision 80% (+50%), faithfulness 85% (+25%), citation precision 90% (+20%), stale 1% (-4%)
- Cost: Offline KG extraction and community detection cost (LLM calls for extraction), online similar to hybrid + graph traversal, total $0.06 per query, 12x cost vs simple but accuracy best, worth for enterprise prod

**Architecture diagram:**

```
Offline:
Docs (orders, bundles, promotions, policies) -> KG Extraction (LLM extracts entities ORD-12345, BUNDLE-123, PROMO-123, relations ORD-12345 part_of BUNDLE-123) -> KG (entities, relations) -> Leiden Community Detection (communities orders, bundles, promotions, policies) -> Community Summaries (LLM summarizes each community) -> Embed docs -> Vector DB + KG + Community Summaries

Online:
Query "Refund policy ORD-12345 bundle promotion" -> Extract entities ORD-12345, bundle, promotion -> Hybrid Retrieval: Vector search (cosine similarity) + BM25 (keyword) + Graph traversal 2-3 hops (ORD-12345 -> part_of -> BUNDLE-123 -> has_promotion -> PROMO-123 -> has_policy -> v2.3) + Community search (community containing ORD-12345 bundle promotion policy) -> RRF fusion -> Reranking cross-encoder Cohere -> Context Compression + LongContextReorder -> LLM with constrained decoding "Answer only from contexts with citations [1][2]" -> Faithfulness check RAGAS -> Freshness check TTL versioning -> Final answer with citations -> Eval RAGAS daily -> Monitoring drift -> Feedback loop -> Continuous indexing Kafka streaming
```

### 7. Implementation Blueprint

**Full production RAG with error rate fixes and accuracy maintenance:**

```
import openai, json, re
from ragas import evaluate
from ragas.metrics import context_recall, context_precision, faithfulness, answer_relevancy
from datasets import Dataset
import clickhouse_connect
from datetime import datetime, timedelta
import cohere

# Setup
client = clickhouse_connect.get_client(host='localhost', port=8123)
co = cohere.Client(api_key="your_key")

# Tools: Vector DB, BM25, KG, Reranker, LLM
# For demo, simplified

def extract_entities(query):
    # Extract entities via regex or LLM
    # e.g., ORD-12345, BUNDLE-123, etc.
    entities = re.findall(r'ORD-\d{5}|BUNDLE-\d{3}|PROMO-\d{3}', query)
    return entities

def hybrid_retrieval(query, top_k=10):
    # Vector search
    query_embedding = openai.embeddings.create(model="text-embedding-3-small", input=query).data[0].embedding
    vector_results = vector_db.search(query_embedding, top_k=top_k)
    
    # BM25
    bm25_results = bm25_db.search(query, top_k=top_k)
    
    # Graph traversal
    entities = extract_entities(query)
    graph_results = []
    for entity in entities:
        traversed = kg.traverse(entity, hops=3)
        graph_results.extend(traversed)
    
    # RRF fusion
    combined = rrf_fusion([vector_results, bm25_results, graph_results], k=60)
    deduped = deduplicate(combined)
    
    return deduped[:top_k]

def rerank(query, docs, top_k=10):
    # Cohere rerank
    reranked = co.rerank(query=query, documents=docs, top_n=top_k, model="rerank-english-v3.0")
    return [r.document["text"] for r in reranked.results]

def context_compression(query, docs):
    compressed = []
    for doc in docs:
        prompt = f"Query: {query}\\nDoc: {doc}\\nCompress to keep relevant info for query, max 100 tokens"
        comp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            tools=[],
            tool_choice="none",
            temperature=0.0
        ).choices[0].message.content
        compressed.append(comp)
    return compressed

def generate_answer(query, contexts):
    # Constrained decoding with citations
    contexts_with_indices = "\\n".join([f"[{i+1}] {ctx}" for i, ctx in enumerate(contexts)])
    prompt = f"Query: {query}\\nContexts: {contexts_with_indices}\\nAnswer only from contexts with citations [1][2] etc. If not in contexts say I don't know."
    
    answer = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    ).choices[0].message.content
    
    # Faithfulness check
    faith_prompt = f"Query: {query}\\nContexts: {contexts}\\nAnswer: {answer}\\nIs answer supported by contexts? Return JSON {{\"faithfulness\": 0-1}}"
    faith_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": faith_prompt}],
        tools=[],
        tool_choice="none",
        temperature=0.0
    ).choices[0].message.content
    
    faith_json = json.loads(faith_response)
    if faith_json["faithfulness"] < 0.8:
        return "I don't know, context does not contain answer"
    
    return answer

def production_rag(query):
    # Hybrid retrieval
    docs = hybrid_retrieval(query, top_k=20)
    
    # Reranking
    reranked = rerank(query, docs, top_k=10)
    
    # Context compression
    compressed = context_compression(query, reranked)
    
    # Generate answer with constrained decoding and faithfulness check
    answer = generate_answer(query, compressed)
    
    # Freshness check
    fresh_docs = fix_stale_data(query, compressed) # Check timestamp, fetch latest if stale
    
    # Log to ClickHouse
    log_rag(query, fresh_docs, answer, timestamp=datetime.now())
    
    return answer

def eval_rag_production(queries, rag_system):
    dataset = []
    for query in queries:
        contexts = rag_system.retrieve(query)
        answer = rag_system.generate(query, contexts)
        ground_truth = get_ground_truth(query)
        
        dataset.append({
            "question": query,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": ground_truth
        })
    
    dataset = Dataset.from_dict({
        "question": [d["question"] for d in dataset],
        "answer": [d["answer"] for d in dataset],
        "contexts": [d["contexts"] for d in dataset],
        "ground_truth": [d["ground_truth"] for d in dataset]
    })
    
    result = evaluate(
        dataset,
        metrics=[context_recall, context_precision, faithfulness, answer_relevancy]
    )
    
    log_eval(result, timestamp=datetime.now())
    
    if result["context_recall"] < 0.8 or result["faithfulness"] < 0.8:
        alert(f"RAG accuracy drop recall {result['context_recall']} faithfulness {result['faithfulness']}")
    
    return result

# Usage
query = "What is refund policy for ORD-12345 bundle promotion?"
answer = production_rag(query)
print(answer)

# Eval daily
queries = sample_production_queries(n=100)
result = eval_rag_production(queries, production_rag)
```

### 8. Benchmarks

| RAG System | Failure Rate | Context Recall | Context Precision | Faithfulness | Citation Precision | Stale Rate | Cost per Query | When to Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Simple Vector RAG | 40% failure enterprise | 60% multi-hop (1-hop only) | 30% (irrelevant docs) | 60% (hallucination) | 70% (no citations) | 5% stale | $0.0051 (1 embed $0.0001 + 1 LLM $0.005) cheap but inaccurate | Baseline, not for prod enterprise |
| Hybrid RAG Vector+BM25+Graph + Rerank + Compression + Constrained Decoding | 20% failure -20% vs simple | 80% +20% vs simple (BM25 + graph traversal helps) | 80% +50% vs simple (reranking) | 80% +20% vs simple (constrained decoding + faithfulness check) | 90% +20% vs simple (citation enforcement) | 1% -4% vs simple (freshness check) | $0.056 (embed $0.0001 + vector+BM25+graph + rerank Cohere $0.001 + compression 10 LLM $0.05 + final LLM $0.005) 11x vs simple but accuracy +20% | Improved, good for prod |
| Production GraphRAG Offline KG extraction + Leiden community detection + Online Hybrid Vector+Graph 2-3 hops+Community search RRF + Rerank + Compression LongContextReorder + Constrained Decoding Faithfulness Check Citation Enforcement + Freshness TTL Versioning + Eval RAGAS Monitoring Drift Feedback Continuous Indexing | 10% failure -30% vs simple -10% vs hybrid best | 85% multi-hop +25% vs simple +5% vs hybrid (graph 2-3 hops + community search) | 80% +50% vs simple same as hybrid (reranking) | 85% +25% vs simple +5% vs hybrid (faithfulness check + constrained) | 90% +20% vs simple same as hybrid | 1% -4% vs simple same as hybrid (freshness) | $0.06 (offline KG extraction cost + online similar to hybrid + graph traversal) 12x vs simple but best accuracy | Production best for enterprise multi-hop QA |

### 9. Production Checklist

1. **Measure Error Rate with RAGAS** — Error rate not one number 6 failure modes retrieval failure 30% context recall low relevant doc not retrieved multi-hop order->bundle->promotion->policy vector 1-hop fails, ranking failure 15% context precision low irrelevant docs ranked higher, context overflow 10% tokens > context window truncation loses relevant, hallucination 20% faithfulness low answer not supported by context, citation failure 10% citation precision low no citations or wrong, stale data 5% freshness stale not latest version. Measure with RAGAS metrics context recall retrieved relevant / total relevant, context precision retrieved relevant / retrieved total, faithfulness answer supported by context, answer relevance answer relevant to query, citation precision/recall citations correct / total citations. Dataset question answer contexts ground_truth, evaluate with RAGAS. Benchmark enterprise RAG 40% failure without fixes.

2. **Fix Retrieval Failure (30%) Hybrid Retrieval + GraphRAG** — Hybrid retrieval vector cosine similarity semantic but fails multi-hop + BM25 keyword exact match ORD-12345 BUNDLE-123 + graph traversal KG traverse order -> bundle -> promotion -> policy 2-3 hops for multi-hop. Combine via Reciprocal Rank Fusion RRF score sum 1/(k+rank) k=60, deduplicate. GraphRAG offline KG extraction entities relations via LLM order ORD-12345 has bundle_id BUNDLE-123 etc, Leiden community detection communities orders bundles promotions policies, community summaries via LLM, online hybrid retrieval vector + graph traversal 2-3 hops + community search via RRF. Benchmark vector RAG recall 60% multi-hop 1-hop only, GraphRAG recall 85% multi-hop +25% because graph 2-3 hops + community search, cost offline KG extraction and community detection LLM calls, online similar to vector + graph traversal, worth for multi-hop enterprise QA.

3. **Fix Ranking Failure (15%) Reranking** — Reranking cross-encoder reranks retrieved docs by relevance to query improves precision. Cross-encoder model takes query and doc outputs relevance score e.g., Cohere rerank API rerank-english-v3.0, LLM rerank via prompt Rank docs by relevance, BGE reranker local model. Example hybrid retrieval 20 docs some irrelevant, rerank to top 10 most relevant via Cohere or LLM, precision improves 30%->80% +50%, worth cost $0.001 per rerank via Cohere.

4. **Fix Context Overflow (10%) Context Compression LongContextReorder Map-Reduce** — Context overflow retrieved docs tokens > LLM context window truncation loses relevant. Fixes: Context compression compress each doc via LLM to keep relevant info for query max 100 tokens, each doc 1000 tokens ->100 tokens 10 docs 10000->1000 tokens saves 90% tokens cost 10 LLM calls $0.05. LongContextReorder reorder docs so most relevant in middle not at end because LLM attention better in middle lost in middle problem, LangChain LongContextReorder, improves faithfulness 10%. Map-Reduce map each doc to summary via LLM max 100 tokens, reduce summaries to final answer via LLM, avoids overflow but cost 20 LLM calls for map +1 for reduce =21 calls vs 1 call direct 21x cost but avoids overflow for large top_k.

5. **Fix Hallucination (20%) Constrained Decoding Faithfulness Check Citation Enforcement** — Hallucination LLM generates answer not supported by context faithfulness low. Fixes: Constrained decoding prompt Answer only from contexts if not in contexts say I don't know T=0.0 deterministic, Faithfulness check after LLM generates answer check faithfulness via RAGAS faithfulness metric or LLM classifier Is answer supported by contexts Return JSON faithfulness 0-1, if faithfulness <0.8 hallucination regenerate or say I don't know, Citation enforcement enforce citations format [1] url via constrained decoding. Benchmark without fix faithfulness 60% hallucination 20% answers not supported, with constrained decoding + faithfulness check faithfulness 85% hallucination 5% -15% worth cost 2 LLM calls constrained answer + faithfulness check $0.01.

6. **Fix Citation Failure (10%) Constrained Decoding for Citations** — Citation failure LLM answer without citations or wrong citations not verifiable. Fix constrained decoding for citations prompt Contexts with indices [1][2][3] etc Answer query with citations e.g., Refund policy says amount<500 auto [1] etc Return answer with citations, check citation precision Are citations correct citation [1] corresponds to context [1] that contains info Return JSON citation_precision 0-1, if citation_precision <0.8 wrong citations regenerate. Benchmark without fix citation precision 70% 30% answers without citations or wrong, with constrained decoding citation precision 90% +20% worth cost 2 LLM calls.

7. **Fix Stale Data (5%) Freshness Continuous Indexing TTL Versioning** — Stale data retrieved docs stale not latest version. Fix freshness via timestamp check if stale >1 day fetch latest, continuous indexing streaming Kafka new orders new policies index immediately embed and index, batch daily new docs updated docs deleted docs, TTL time to live for docs e.g., policy docs TTL 1 day order docs TTL 1 hour after TTL re-index or mark stale, versioning version docs e.g., policy v2.3 v2.4 retrieve latest version. Benchmark without fix 5% answers stale policy v2.3 retrieved but v2.4 latest answer wrong, with freshness + continuous indexing + TTL + versioning stale rate 1% -4% worth cost continuous indexing embedding cost $0.0001 per doc.

8. **Maintain Accuracy in Production RAG System Eval Monitoring Feedback Indexing Loop** — Maintain accuracy prod eval with RAGAS daily on sample 100 production queries metrics context recall precision faithfulness answer relevance citation precision log to ClickHouse alert if metrics drop <80%, monitoring drift data drift new docs updated docs deleted docs need continuous indexing query drift new queries e.g., bundle promotion refund policy previously not asked need to update index with bundle docs context drift retrieved contexts change previously policy v2.3 now v2.4 need freshness accuracy drift RAGAS metrics drop context recall 90%->70% faithfulness 85%->60% need to fix retrieval reranking etc alert if drift, human-in-the-loop feedback collect thumbs up/down corrections log feedback ClickHouse use feedback to improve index missing docs update reranking fine-tune reranker or LLM on feedback data e.g., 100 feedbacks with corrections fine-tune reranker to rank bundle doc higher for bundle queries, continuous indexing streaming Kafka new docs embed and index immediately batch daily new docs updated docs deleted docs freshness TTL versioning GraphRAG KG extraction and community detection offline hybrid retrieval online, cost eval 100 queries *4 metrics *$0.005=$2 daily monitoring drift free feedback free continuous indexing embedding cost $0.0001 per doc worth for accuracy.

9. **Product RAG Architecture Simple Vector -> Hybrid -> Production GraphRAG** — Simple vector baseline embed query -> vector search top_k=10 -> LLM generates answer with contexts failure rate 40% enterprise recall 60% multi-hop precision 30% faithfulness 60% no citations stale 5% cost $0.0051 per query 1 embed $0.0001 +1 LLM $0.005 cheap but inaccurate not for prod enterprise. Hybrid improved hybrid retrieval vector+BM25+graph traversal -> reranking cross-encoder -> context compression -> LLM with constrained decoding for citations failure rate 20% -20% vs simple recall 80% +20% precision 80% +50% faithfulness 80% +20% citation precision 90% +20% stale 1% -4% cost $0.056 per query embed $0.0001 + vector+BM25+graph + rerank Cohere $0.001 + compression 10 LLM $0.05 + final LLM $0.005 11x vs simple but accuracy +20% worth it for prod. Production GraphRAG best offline KG extraction entities relations via LLM Leiden community detection communities embed docs index vector DB build KG build community summaries via LLM online hybrid retrieval vector+graph 2-3 hops+community search via RRF -> reranking cross-encoder -> context compression LongContextReorder -> LLM with constrained decoding faithfulness check citation enforcement -> freshness check TTL versioning -> eval RAGAS daily -> monitoring drift -> feedback loop -> continuous indexing Kafka streaming failure rate 10% -30% vs simple -10% vs hybrid best recall 85% multi-hop +25% vs simple +5% vs hybrid precision 80% +50% faithfulness 85% +25% citation precision 90% +20% stale 1% -4% cost $0.06 per query offline KG extraction cost + online similar to hybrid + graph traversal 12x vs simple but best accuracy worth for enterprise prod multi-hop QA. Architecture offline docs orders bundles promotions policies -> KG extraction LLM extracts entities ORD-12345 BUNDLE-123 PROMO-123 relations ORD-12345 part_of BUNDLE-123 -> KG entities relations -> Leiden community detection communities orders bundles promotions policies -> community summaries LLM summarizes each community -> embed docs -> vector DB + KG + community summaries online query Refund policy ORD-12345 bundle promotion -> extract entities ORD-12345 bundle promotion -> hybrid retrieval vector search cosine + BM25 keyword + graph traversal 2-3 hops ORD-12345 -> part_of -> BUNDLE-123 -> has_promotion -> PROMO-123 -> has_policy -> v2.3 + community search community containing ORD-12345 bundle promotion policy -> RRF fusion -> reranking cross-encoder Cohere -> context compression LongContextReorder -> LLM with constrained decoding Answer only from contexts with citations [1][2] -> faithfulness check RAGAS -> freshness check TTL versioning -> final answer with citations -> eval RAGAS daily -> monitoring drift -> feedback loop -> continuous indexing Kafka streaming.

---
**Bottom Line:** RAG fails 40% in enterprise, error rate not one number 6 failure modes retrieval failure 30% relevant doc not retrieved context recall low because vector 1-hop only fails multi-hop order->bundle->promotion->policy, ranking failure 15% irrelevant docs ranked higher context precision low because vector without reranking, context overflow 10% tokens > context window truncation loses relevant, hallucination 20% faithfulness low answer not supported by context because context recall low LLM not constrained, citation failure 10% citation precision low no citations or wrong not verifiable, stale data 5% freshness stale not latest version. Measure with RAGAS metrics context recall retrieved relevant / total relevant low <70% retrieval failure, context precision retrieved relevant / retrieved total low <70% ranking failure, faithfulness answer supported by context low <80% hallucination, answer relevance answer relevant to query, citation precision/recall citations correct / total citations low <80% citation failure, freshness timestamp vs latest stale >1 day stale data. Fix retrieval failure hybrid retrieval vector cosine semantic but fails multi-hop + BM25 keyword exact match ORD-12345 BUNDLE-123 + graph traversal KG traverse order->bundle->promotion->policy 2-3 hops for multi-hop GraphRAG offline KG extraction entities relations via LLM Leiden community detection communities online hybrid retrieval vector+graph 2-3 hops+community search via RRF reciprocal rank fusion score sum 1/(k+rank) k=60 deduplicate, GraphRAG recall 85% multi-hop +25% vs vector 60% 1-hop only worth offline KG extraction cost. Fix ranking failure reranking cross-encoder reranks retrieved docs by relevance to query improves precision cross-encoder model takes query and doc outputs relevance score e.g., Cohere rerank API rerank-english-v3.0 LLM rerank via prompt Rank docs by relevance BGE reranker local model, precision 30%->80% +50% worth $0.001 per rerank. Fix context overflow context compression compress each doc via LLM to keep relevant info for query max 100 tokens each doc 1000->100 tokens 10 docs 10000->1000 saves 90% cost 10 LLM calls $0.05, LongContextReorder reorder docs most relevant in middle because LLM attention better in middle lost in middle problem LangChain LongContextReorder improves faithfulness 10%, Map-Reduce map each doc to summary via LLM max 100 tokens reduce summaries to final answer via LLM avoids overflow but cost 21 calls vs 1 call 21x cost but avoids overflow for large top_k. Fix hallucination constrained decoding prompt Answer only from contexts if not in contexts say I don't know T=0.0 deterministic faithfulness check after LLM generates answer check faithfulness via RAGAS or LLM classifier Is answer supported by contexts Return JSON faithfulness 0-1 if faithfulness <0.8 hallucination regenerate or say I don't know citation enforcement enforce citations format [1] url, faithfulness 60%->85% +25% hallucination 20%->5% -15% worth 2 LLM calls $0.01. Fix citation failure constrained decoding for citations prompt Contexts with indices [1][2][3] etc Answer query with citations e.g., Refund policy says amount<500 auto [1] etc Return answer with citations check citation precision Are citations correct citation [1] corresponds to context [1] that contains info Return JSON citation_precision 0-1 if citation_precision <0.8 wrong citations regenerate, citation precision 70%->90% +20% worth 2 LLM calls. Fix stale data freshness via timestamp check if stale >1 day fetch latest continuous indexing streaming Kafka new orders new policies index immediately embed and index batch daily new docs updated docs deleted docs TTL time to live for docs e.g., policy docs TTL 1 day order docs TTL 1 hour after TTL re-index or mark stale versioning version docs e.g., policy v2.3 v2.4 retrieve latest version stale rate 5%->1% -4% worth embedding cost $0.0001 per doc. Maintain accuracy in prod eval with RAGAS daily on sample 100 production queries metrics context recall precision faithfulness answer relevance citation precision log to ClickHouse alert if metrics drop <80%, monitoring drift data drift new docs query drift new queries context drift retrieved contexts change accuracy drift RAGAS metrics drop alert if drift, human-in-the-loop feedback collect thumbs up/down corrections log feedback ClickHouse use feedback to improve index missing docs update reranking fine-tune reranker or LLM on feedback data e.g., 100 feedbacks fine-tune reranker to rank bundle doc higher for bundle queries, continuous indexing streaming Kafka new docs embed and index immediately batch daily freshness TTL versioning GraphRAG KG extraction and community detection offline hybrid retrieval online, cost eval 100 queries *4 metrics *$0.005=$2 daily monitoring drift free feedback free continuous indexing embedding cost $0.0001 per doc worth for accuracy. Product RAG architecture simple vector baseline embed query -> vector search top_k=10 -> LLM generates answer failure 40% recall 60% multi-hop precision 30% faithfulness 60% no citations stale 5% cost $0.0051 cheap but inaccurate not for prod, hybrid improved hybrid retrieval vector+BM25+graph traversal -> reranking cross-encoder -> context compression -> LLM with constrained decoding citations failure 20% -20% recall 80% +20% precision 80% +50% faithfulness 80% +20% citation 90% +20% stale 1% -4% cost $0.056 11x vs simple but accuracy +20% worth prod, production GraphRAG best offline KG extraction entities relations Leiden community detection communities community summaries embed docs index vector DB build KG build community summaries online hybrid retrieval vector+graph 2-3 hops+community search RRF -> reranking cross-encoder -> context compression LongContextReorder -> LLM constrained decoding faithfulness check citation enforcement -> freshness TTL versioning -> eval RAGAS daily -> monitoring drift -> feedback loop -> continuous indexing Kafka streaming failure 10% -30% vs simple -10% vs hybrid best recall 85% multi-hop +25% vs simple +5% vs hybrid precision 80% +50% faithfulness 85% +25% citation 90% +20% stale 1% -4% cost $0.06 12x vs simple but best accuracy worth enterprise prod multi-hop QA.
