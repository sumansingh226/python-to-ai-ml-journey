# AI System Design - Developer Roadmap

> A complete learning path for designing, building, and shipping production-grade AI systems. Use this as a checklist, not a textbook.

---

## 1. Foundations
- What is an AI System vs ML Model vs AI Product
- Types of AI Systems: Predictive, Generative, Agentic, Recommender, Search/RAG
- System Design Basics: Requirements, Constraints, Tradeoffs (CAP, Latency vs Cost vs Accuracy)
- How to approach an AI System Design Interview / Problem

## 2. Machine Learning & Deep Learning Essentials (for System Designers)
- Supervised, Unsupervised, Self-supervised Learning
- Bias-Variance Tradeoff, Overfitting, Underfitting
- Loss Functions, Optimizers, Regularization
- Neural Networks: CNNs, RNNs, Transformers (high-level)
- Foundation Models & Transfer Learning Concept

## 3. Data Layer - The Most Important Layer
- Data Sources & Ingestion (Batch vs Streaming)
- Data Storage: Data Lake, Warehouse, Lakehouse
- Data Processing: ETL/ELT, Spark, Kafka, Flink
- Data Quality, Validation, Versioning (DVC, LakeFS)
- Data Labeling & Human-in-the-Loop (Label Studio, Scale AI)
- Feature Store (Feast, Tecton) - Offline vs Online Features
- Data Privacy, PII, Governance, Compliance

## 4. Model Development & Experimentation
- Training Data Preparation & Feature Engineering
- Experiment Tracking (MLflow, Weights & Biases)
- Model Registry & Versioning
- Hyperparameter Tuning
- Distributed Training (Data Parallel, Model Parallel, FSDP, DeepSpeed)
- Evaluation: Offline Metrics vs Online Metrics

## 5. Generative AI & LLM System Design
- LLM Fundamentals: Tokens, Context Window, Embeddings, Attention
- Prompt Engineering & Prompt Management
- Fine-tuning: Full FT, LoRA, QLoRA, PEFT
- RLHF & Alignment Basics
- Inference Optimization: Quantization (INT8/INT4), Distillation, KV-Cache
- Function Calling & Tool Use
- Multimodal Systems (Text + Image + Audio + Video)

## 6. Retrieval Augmented Generation (RAG) - Core Building Block
- Why RAG: Hallucination, Freshness, Private Data
- RAG Pipeline: Chunking -> Embedding -> Vector DB -> Retrieval -> Reranking -> Generation
- Chunking Strategies
- Embedding Models: Open vs Closed
- Vector Databases: Pinecone, Weaviate, Qdrant, Milvus, pgvector
- Retrieval Strategies: Dense, Sparse (BM25), Hybrid Search
- Reranking (Cross-encoders, Cohere Rerank)
- Advanced RAG: GraphRAG, Self-RAG, Agentic RAG

## 7. AI Agent Systems
- Agent Anatomy: LLM + Memory + Tools + Planner
- ReAct, Chain-of-Thought, Tree-of-Thoughts
- Tool Use & MCP (Model Context Protocol)
- Memory: Short-term, Long-term, Vector Memory
- Multi-Agent Orchestration (CrewAI, LangGraph, AutoGen)
- Planning & Reflection Patterns

## 8. Model Serving & Inference Architecture
- Online vs Offline vs Nearline Inference
- Model Servers: TorchServe, Triton, vLLM, TGI, Ollama
- API Design: REST, gRPC, Streaming Responses
- Batching, Caching (Semantic Cache), Rate Limiting
- GPU vs CPU vs Edge Inference
- Scaling: Autoscaling, Load Balancing, Cold Starts
- Cost Optimization: Spot Instances, Serverless GPUs

## 9. MLOps / LLMOps - Production Lifecycle
- CI/CD for ML: Training Pipelines (Airflow, Kubeflow, SageMaker Pipelines)
- Model Deployment Strategies: Blue/Green, Canary, Shadow
- Monitoring: Data Drift, Concept Drift, Model Decay
- Logging, Tracing, Observability for LLMs (LangSmith, Langfuse, Phoenix)
- Feedback Loops & Continuous Training
- Security: Prompt Injection, Data Leakage, Model Stealing

## 10. Evaluation & Safety
- LLM Evaluation: BLEU, ROUGE, BERTScore, Human Eval, LLM-as-a-Judge
- Benchmarks: MMLU, HumanEval, HELM
- A/B Testing & Interleaving for AI Features
- Guardrails: Content Filters, PII Redaction, Toxicity Detection
- Hallucination Detection & Mitigation
- Responsible AI: Fairness, Explainability (SHAP, LIME), Audit

## 11. System Design Patterns - Real World Systems
- Design: AI Search Engine (like Perplexity)
- Design: Chatbot / Copilot (ChatGPT-like)
- Design: Recommendation System (YouTube, Netflix, Amazon)
- Design: AI Code Assistant
- Design: AI Voice Assistant (Alexa/Siri)
- Design: Fraud Detection System
- Design: Ad Ranking System
- Design: Autonomous Agent for Customer Support

## 12. Non-Functional Requirements
- Latency: p50, p95, p99 for AI responses
- Throughput & QPS
- Cost: Training Cost vs Inference Cost per 1k tokens/requests
- Availability & Fault Tolerance
- Scalability to Millions of Users
- Privacy & Compliance: GDPR, SOC2, HIPAA for AI

## 13. Tech Stack to Learn (Hands-on)
- Languages: Python (must), SQL
- Frameworks: PyTorch, Hugging Face Transformers, LangChain / LlamaIndex
- Vector DBs: Qdrant / Pinecone
- Infra: Docker, Kubernetes, FastAPI
- Cloud: AWS / GCP / Azure AI services
- Orchestration: LangGraph, CrewAI

## 14. Learning Order - Suggested 90-Day Plan
- **Weeks 1-2:** Foundations + Data Layer + ML Essentials
- **Weeks 3-4:** Model Dev + Serving + MLOps
- **Weeks 5-6:** LLM Fundamentals + Prompting + Fine-tuning
- **Weeks 7-8:** RAG Deep Dive + Vector DBs + Build 1 RAG Project
- **Weeks 9-10:** Agents + Tools + Build 1 Agent Project
- **Weeks 11-12:** System Design Patterns + Mock Design Interviews + Cost & Eval

## 15. Resources & What to Build
- Must-Build Projects: 1) RAG over your docs, 2) Agent with tools, 3) Realtime Recommendation or Search
- Reading: Designing Machine Learning Systems (Chip Huyen), A Pattern Language for LLMOps

---
