# Forward Deployed Engineer (FDE) Roadmap — Complete Guide

> **What is an FDE?** A Forward Deployed Engineer is a software engineer who works directly with customers, embedded in their environment, to turn messy real-world problems into working production software. Think: **engineer + consultant + product manager + solutions architect**. The role was popularized by Palantir and is now common at AI companies (Anthropic, OpenAI, Scale AI, Databricks, Snowflake, Ramp, Rippling, etc.).
>
> **Core loop:** Understand customer problem → integrate with their data/systems → build fast → deploy → iterate with the customer → feed learnings back to the core product.

**How to use this file:** Work top to bottom. Each topic has subtopics, learning links, and a "done when" check. Tick the boxes as you go. Links point to official docs or well-known free resources; if one has moved, search the title.

---

## Table of Contents

0. [FDE Role Overview & Mindset](#0-fde-role-overview--mindset)
1. [Programming Foundations](#1-programming-foundations)
2. [Computer Science Fundamentals (DSA)](#2-computer-science-fundamentals-dsa)
3. [Linux, Shell, Git & Dev Tooling](#3-linux-shell-git--dev-tooling)
4. [Databases & SQL](#4-databases--sql)
5. [APIs & Backend Engineering](#5-apis--backend-engineering)
6. [Frontend Basics](#6-frontend-basics)
7. [Data Engineering & Integration](#7-data-engineering--integration)
8. [Cloud & Infrastructure](#8-cloud--infrastructure)
9. [Containers, CI/CD & DevOps](#9-containers-cicd--devops)
10. [Security, Auth & Enterprise Requirements](#10-security-auth--enterprise-requirements)
11. [System Design](#11-system-design)
12. [AI / LLM Engineering (Critical for modern FDE)](#12-ai--llm-engineering)
13. [Observability & Debugging in Production](#13-observability--debugging-in-production)
14. [Customer-Facing & Soft Skills](#14-customer-facing--soft-skills)
15. [Product Thinking & Business Acumen](#15-product-thinking--business-acumen)
16. [Industry Domain Knowledge](#16-industry-domain-knowledge)
17. [Portfolio Projects](#17-portfolio-projects)
18. [Interview Preparation](#18-interview-preparation)
19. [24-Week Study Plan](#19-24-week-study-plan)
20. [Books, Blogs & Communities](#20-books-blogs--communities)
21. [Progress Tracker](#21-progress-tracker)

---

## 0. FDE Role Overview & Mindset

### Subtopics
- [ ] FDE vs Software Engineer vs Solutions Engineer vs Sales Engineer vs Consultant
- [ ] "Dev vs Delta" — product engineering (Dev) vs customer-specific engineering (Delta)
- [ ] Typical day: discovery calls, data integration, building prototypes, deploying, on-site work
- [ ] Ownership mindset: you own the customer outcome end to end
- [ ] Travel, ambiguity, and context-switching expectations
- [ ] Career paths: Staff FDE, Solutions Architect, Product Manager, Founder, Engineering Manager

### Learning Links
- Palantir — Dev versus Delta: https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87
- Palantir — A Day in the Life of a Forward Deployed Software Engineer: https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1
- Palantir Careers (read real FDE job descriptions): https://www.palantir.com/careers/
- Search job boards for "Forward Deployed Engineer" at Anthropic, OpenAI, Databricks, Scale AI, Ramp to see current requirements.

### Done when
You can explain in 60 seconds how an FDE differs from a standard SWE and from a Solutions Engineer.

---

## 1. Programming Foundations

### 1.1 Python (primary language)
- [ ] Syntax, data types, control flow, functions, comprehensions
- [ ] OOP: classes, inheritance, dataclasses, protocols
- [ ] Error handling, context managers, decorators, generators
- [ ] Virtual envs & packaging (`venv`, `pip`, `uv`, `poetry`)
- [ ] Typing (`typing`, `mypy`, `pydantic`)
- [ ] Async (`asyncio`, `aiohttp`, `httpx`)
- [ ] Testing (`pytest`, fixtures, mocking)
- [ ] Standard library: `json`, `csv`, `pathlib`, `logging`, `argparse`, `subprocess`

**Links**
- Official tutorial: https://docs.python.org/3/tutorial/
- Real Python: https://realpython.com/
- Automate the Boring Stuff (free): https://automatetheboringstuff.com/
- Pydantic: https://docs.pydantic.dev/
- pytest: https://docs.pytest.org/
- asyncio: https://docs.python.org/3/library/asyncio.html
- uv (fast package manager): https://docs.astral.sh/uv/

### 1.2 TypeScript / JavaScript (secondary language)
- [ ] JS fundamentals, ES6+, closures, promises, async/await
- [ ] TypeScript types, generics, interfaces
- [ ] Node.js runtime, npm/pnpm, modules
- [ ] Testing (Jest / Vitest)

**Links**
- MDN JavaScript Guide: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide
- javascript.info: https://javascript.info/
- TypeScript Handbook: https://www.typescriptlang.org/docs/handbook/intro.html
- Node.js Learn: https://nodejs.org/en/learn
- Vitest: https://vitest.dev/

### 1.3 Optional (nice-to-have)
- [ ] Java or Go (many enterprise customers run Java; Go for infra tooling)
- [ ] Bash scripting (see section 3)
- [ ] Rust basics (only if targeting infra-heavy roles)

**Links**
- Go Tour: https://go.dev/tour/
- Java (Dev.java): https://dev.java/learn/

### Done when
You can build a CLI tool and a small REST service in Python with tests and type hints, without tutorials.

---

## 2. Computer Science Fundamentals (DSA)

### Subtopics
- [ ] Big-O analysis
- [ ] Arrays, strings, hash maps, sets
- [ ] Linked lists, stacks, queues, deques
- [ ] Trees, BSTs, tries, heaps / priority queues
- [ ] Graphs: BFS, DFS, topological sort, shortest path
- [ ] Sorting & searching, binary search
- [ ] Recursion, backtracking
- [ ] Dynamic programming (basics)
- [ ] Two pointers, sliding window, intervals
- [ ] OS basics: processes, threads, memory, I/O
- [ ] Networking basics: TCP/IP, DNS, HTTP, TLS

### Links
- NeetCode roadmap & 150: https://neetcode.io/roadmap
- LeetCode: https://leetcode.com/
- CS50 (Harvard, free): https://cs50.harvard.edu/x/
- Big-O cheat sheet: https://www.bigocheatsheet.com/
- Visualgo (visualize algorithms): https://visualgo.net/
- Computer Networking top-down (Kurose): https://gaia.cs.umass.edu/kurose_ross/index.php
- Beej's Guide to Network Programming: https://beej.us/guide/bgnet/

### Done when
You can solve LeetCode mediums in ~25–30 min; target 100–150 problems, focused on practical patterns (hash maps, graphs, strings, parsing).

> **FDE note:** FDE interviews weight DSA lower than pure SWE roles, but most still have a coding round. Practical/data-manipulation problems matter more than hard DP.

---

## 3. Linux, Shell, Git & Dev Tooling

### Subtopics
- [ ] Linux filesystem, permissions, processes, signals
- [ ] Shell: pipes, redirects, `grep`, `awk`, `sed`, `jq`, `curl`, `xargs`
- [ ] Bash scripting, cron, systemd basics
- [ ] SSH, keys, tunnels, port forwarding (essential for on-prem customers)
- [ ] Git: branching, rebasing, cherry-pick, bisect, stash, conflicts
- [ ] Pull-request workflow, code review
- [ ] Editor/IDE mastery (VS Code / Neovim), debuggers
- [ ] Makefiles, task runners

### Links
- The Missing Semester (MIT): https://missing.csail.mit.edu/
- Linux Journey: https://linuxjourney.com/
- Pro Git (free book): https://git-scm.com/book/en/v2
- Learn Git Branching (interactive): https://learngitbranching.js.org/
- jq manual: https://jqlang.github.io/jq/manual/
- Explain Shell: https://explainshell.com/
- OverTheWire Bandit (shell practice): https://overthewire.org/wargames/bandit/

### Done when
You can SSH into a fresh box, diagnose a failing service from logs, and script a fix — all from the terminal.

---

## 4. Databases & SQL

### 4.1 SQL (non-negotiable for FDE)
- [ ] SELECT, WHERE, GROUP BY, HAVING, ORDER BY
- [ ] JOINs (inner, left, right, full, cross, self)
- [ ] Subqueries & CTEs
- [ ] Window functions (`ROW_NUMBER`, `RANK`, `LAG/LEAD`, running totals)
- [ ] Indexes, `EXPLAIN` / query plans, performance tuning
- [ ] Transactions, ACID, isolation levels, locks
- [ ] Schema design, normalization vs denormalization
- [ ] Migrations (Alembic, Flyway, Prisma)

### 4.2 Database types
- [ ] Relational: PostgreSQL (primary), MySQL, SQL Server, Oracle (customers often use these)
- [ ] Document: MongoDB
- [ ] Key-value / cache: Redis
- [ ] Search: Elasticsearch / OpenSearch
- [ ] Graph: Neo4j (concepts)
- [ ] Vector: pgvector, Pinecone, Weaviate, Qdrant (see section 12)
- [ ] Warehouses: Snowflake, BigQuery, Redshift, Databricks

### Links
- SQLBolt: https://sqlbolt.com/
- SQLZoo: https://sqlzoo.net/
- PostgreSQL official tutorial: https://www.postgresql.org/docs/current/tutorial.html
- PostgreSQL Tutorial site: https://www.postgresqltutorial.com/
- Use The Index, Luke: https://use-the-index-luke.com/
- Window functions explained: https://www.postgresql.org/docs/current/tutorial-window.html
- LeetCode SQL 50: https://leetcode.com/studyplan/top-sql-50/
- DataLemur SQL practice: https://datalemur.com/
- MongoDB University: https://learn.mongodb.com/
- Redis University: https://university.redis.io/
- Snowflake docs: https://docs.snowflake.com/
- BigQuery docs: https://cloud.google.com/bigquery/docs

### Done when
You can write multi-CTE queries with window functions from memory, and read a query plan to explain why something is slow.

---

## 5. APIs & Backend Engineering

### Subtopics
- [ ] HTTP deep dive: methods, status codes, headers, caching, cookies, CORS
- [ ] REST design principles, pagination, filtering, idempotency, versioning
- [ ] GraphQL basics
- [ ] gRPC & Protocol Buffers
- [ ] Webhooks & event-driven integration
- [ ] WebSockets / Server-Sent Events (streaming)
- [ ] OpenAPI / Swagger specs
- [ ] Rate limiting, retries with backoff, circuit breakers
- [ ] Frameworks: FastAPI / Flask / Django (Python); Express / NestJS (Node)
- [ ] Background jobs & queues (Celery, RQ, BullMQ, SQS)
- [ ] Consuming third-party APIs reliably (pagination, auth, rate limits, SDKs)
- [ ] Message queues: RabbitMQ, Kafka, SQS, Pub/Sub

### Links
- MDN HTTP: https://developer.mozilla.org/en-US/docs/Web/HTTP
- FastAPI: https://fastapi.tiangolo.com/
- Django: https://docs.djangoproject.com/
- Flask: https://flask.palletsprojects.com/
- Express: https://expressjs.com/
- NestJS: https://docs.nestjs.com/
- REST API tutorial: https://restfulapi.net/
- OpenAPI spec: https://spec.openapis.org/oas/latest.html
- GraphQL learn: https://graphql.org/learn/
- gRPC: https://grpc.io/docs/
- Postman Learning Center: https://learning.postman.com/
- Stripe API docs (gold standard for API design): https://docs.stripe.com/api
- Kafka docs: https://kafka.apache.org/documentation/
- Celery: https://docs.celeryq.dev/
- Tenacity (Python retries): https://tenacity.readthedocs.io/

### Done when
You can read an unfamiliar vendor's API docs, write a resilient client (auth, pagination, retries), and expose your own documented API.

---

## 6. Frontend Basics

FDEs often ship internal dashboards, demos, and customer-facing UIs quickly. You don't need to be a design expert, but you must be able to build a functional UI.

### Subtopics
- [ ] HTML/CSS fundamentals, flexbox, grid
- [ ] React: components, hooks, state, effects, context
- [ ] Next.js basics (routing, SSR/SSG, API routes)
- [ ] Data fetching (React Query / SWR), forms, tables, charts
- [ ] UI kits: Tailwind CSS, shadcn/ui
- [ ] Rapid-prototyping tools: Streamlit, Gradio, Retool, Dash
- [ ] Charting: Recharts, D3 basics, Plotly

### Links
- MDN Learn Web Development: https://developer.mozilla.org/en-US/docs/Learn_web_development
- React docs: https://react.dev/learn
- Next.js Learn: https://nextjs.org/learn
- Tailwind CSS: https://tailwindcss.com/docs
- shadcn/ui: https://ui.shadcn.com/
- TanStack Query: https://tanstack.com/query/latest
- Streamlit: https://docs.streamlit.io/
- Gradio: https://www.gradio.app/docs
- Plotly: https://plotly.com/python/

### Done when
You can ship a working data dashboard (auth + table + chart + filters) in one day.

---

## 7. Data Engineering & Integration

Integrating with a customer's messy data is the heart of FDE work.

### Subtopics
- [ ] ETL vs ELT, batch vs streaming
- [ ] Data formats: CSV, JSON, XML, Parquet, Avro, Excel, fixed-width, EDI
- [ ] Data cleaning, schema mapping, dedupe, entity resolution
- [ ] pandas / Polars / DuckDB
- [ ] Orchestration: Airflow, Dagster, Prefect
- [ ] Transformation: dbt
- [ ] Big data: Spark / PySpark, Databricks
- [ ] Streaming: Kafka, Flink (concepts), Kinesis
- [ ] Data modeling: star schema, data vault, medallion architecture
- [ ] Data quality: Great Expectations, Soda
- [ ] Connectors/ingestion: Fivetran, Airbyte, custom connectors
- [ ] Legacy integration: SFTP, mainframes, flat files, ODBC/JDBC, SOAP
- [ ] Data governance, lineage, PII handling

### Links
- pandas getting started: https://pandas.pydata.org/docs/getting_started/index.html
- Polars: https://docs.pola.rs/
- DuckDB: https://duckdb.org/docs/
- Apache Airflow: https://airflow.apache.org/docs/
- Dagster: https://docs.dagster.io/
- Prefect: https://docs.prefect.io/
- dbt Learn: https://learn.getdbt.com/
- dbt docs: https://docs.getdbt.com/
- PySpark docs: https://spark.apache.org/docs/latest/api/python/
- Databricks Academy (free tier): https://www.databricks.com/learn
- Airbyte: https://docs.airbyte.com/
- Great Expectations: https://docs.greatexpectations.io/
- Data Engineering Zoomcamp (free): https://github.com/DataTalksClub/data-engineering-zoomcamp
- Medallion architecture: https://www.databricks.com/glossary/medallion-architecture

### Done when
You can take 3 messy CSV/JSON/API sources, build a pipeline that cleans, joins, and loads them into a warehouse, and schedule it.

---

## 8. Cloud & Infrastructure

### Subtopics
- [ ] Core cloud concepts: regions, AZs, IAM, VPC, subnets, security groups
- [ ] Compute: EC2/VMs, Lambda/Cloud Functions, ECS/Fargate, Cloud Run
- [ ] Storage: S3/GCS/Blob, EBS, EFS
- [ ] Databases: RDS, DynamoDB, Cloud SQL
- [ ] Networking: load balancers, DNS (Route 53), CDN, VPN, PrivateLink / peering
- [ ] Serverless patterns & event-driven architecture
- [ ] Infrastructure as Code: Terraform, Pulumi, CloudFormation
- [ ] Cost awareness & FinOps basics
- [ ] On-prem / air-gapped / hybrid deployment (common in gov, finance, healthcare, defense)
- [ ] Multi-cloud differences (AWS vs Azure vs GCP naming)

### Links
- AWS Skill Builder (free tier): https://skillbuilder.aws/
- AWS Cloud Practitioner: https://aws.amazon.com/certification/certified-cloud-practitioner/
- AWS Solutions Architect Associate: https://aws.amazon.com/certification/certified-solutions-architect-associate/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/
- Google Cloud Skills Boost: https://www.cloudskillsboost.google/
- Microsoft Learn (Azure): https://learn.microsoft.com/en-us/training/azure/
- Terraform tutorials: https://developer.hashicorp.com/terraform/tutorials
- Pulumi: https://www.pulumi.com/docs/
- Cloud service map (AWS/Azure/GCP): https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison
- A Cloud Guru / freeCodeCamp AWS course on YouTube (search "freeCodeCamp AWS Certified Cloud Practitioner")

### Done when
You can deploy a containerized app behind a load balancer with a database, secrets, and IAM roles — using Terraform — in one cloud.

---

## 9. Containers, CI/CD & DevOps

### Subtopics
- [ ] Docker: images, layers, Dockerfile best practices, multi-stage builds, compose
- [ ] Kubernetes: pods, deployments, services, ingress, configmaps, secrets, Helm
- [ ] Deploying into customer-managed Kubernetes / OpenShift
- [ ] CI/CD: GitHub Actions, GitLab CI, Jenkins, ArgoCD (GitOps)
- [ ] Release strategies: blue/green, canary, feature flags, rollbacks
- [ ] Config & secrets management: Vault, AWS Secrets Manager, SOPS
- [ ] Artifact registries, SBOMs, image scanning
- [ ] Packaging software for air-gapped delivery

### Links
- Docker Get Started: https://docs.docker.com/get-started/
- Docker best practices: https://docs.docker.com/build/building/best-practices/
- Kubernetes tutorials: https://kubernetes.io/docs/tutorials/
- Kubernetes the Hard Way: https://github.com/kelseyhightower/kubernetes-the-hard-way
- Helm: https://helm.sh/docs/
- GitHub Actions: https://docs.github.com/en/actions
- ArgoCD: https://argo-cd.readthedocs.io/
- HashiCorp Vault: https://developer.hashicorp.com/vault/tutorials
- KodeKloud (hands-on labs): https://kodekloud.com/
- Play with Docker: https://labs.play-with-docker.com/
- Killercoda (K8s labs): https://killercoda.com/

### Done when
You can containerize an app, write a CI pipeline that tests and deploys it to Kubernetes, and roll back a bad release.

---

## 10. Security, Auth & Enterprise Requirements

Enterprise customers will block you until security is satisfied. FDEs must speak this language.

### Subtopics
- [ ] AuthN vs AuthZ, RBAC, ABAC
- [ ] OAuth 2.0, OpenID Connect, JWT
- [ ] SSO: SAML, SCIM provisioning, Okta / Entra ID (Azure AD)
- [ ] API keys, secrets handling, key rotation
- [ ] TLS/mTLS, certificates, encryption at rest & in transit
- [ ] OWASP Top 10, input validation, SQL injection, XSS, SSRF
- [ ] Network security: firewalls, VPN, allowlists, zero trust
- [ ] Compliance: SOC 2, ISO 27001, GDPR, HIPAA, FedRAMP, PCI-DSS
- [ ] Data residency, PII/PHI handling, audit logging
- [ ] Customer security questionnaires & vendor reviews
- [ ] LLM-specific risks: prompt injection, data leakage, tool misuse (see section 12)

### Links
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheet Series: https://cheatsheetseries.owasp.org/
- OAuth 2.0 simplified: https://www.oauth.com/
- OpenID Connect: https://openid.net/developers/how-connect-works/
- JWT intro: https://jwt.io/introduction
- PortSwigger Web Security Academy (free labs): https://portswigger.net/web-security
- Okta developer docs: https://developer.okta.com/docs/
- SOC 2 overview (AICPA): https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
- GDPR overview: https://gdpr.eu/what-is-gdpr/
- OWASP Top 10 for LLM Applications: https://owasp.org/www-project-top-10-for-large-language-model-applications/

### Done when
You can integrate an app with a customer's SSO, explain your data flow in a security review, and answer "where does our data live?" confidently.

---

## 11. System Design

### Subtopics
- [ ] Requirements gathering, back-of-envelope estimation
- [ ] Load balancing, caching, CDNs
- [ ] Sharding, replication, consistency (CAP, eventual consistency)
- [ ] Queues, pub/sub, event sourcing, CQRS
- [ ] Microservices vs monolith trade-offs
- [ ] Idempotency, exactly-once vs at-least-once
- [ ] Reliability: SLOs, SLAs, graceful degradation
- [ ] Designing for multi-tenancy
- [ ] Designing integrations: adapters, anti-corruption layers, sync vs async
- [ ] Classic designs: URL shortener, rate limiter, notification system, chat, search, data pipeline, document ingestion + RAG system

### Links
- System Design Primer: https://github.com/donnemartin/system-design-primer
- ByteByteGo: https://bytebytego.com/
- High Scalability: https://highscalability.com/
- Martin Kleppmann, *Designing Data-Intensive Applications* (book): https://dataintensive.net/
- Google SRE Book (free): https://sre.google/sre-book/table-of-contents/
- Awesome System Design: https://github.com/madd86/awesome-system-design
- Microservices patterns: https://microservices.io/patterns/index.html
- Excalidraw (for diagramming): https://excalidraw.com/

### Done when
You can whiteboard an end-to-end integration architecture for a customer in 35 minutes, stating trade-offs.

---

## 12. AI / LLM Engineering

The fastest-growing area of FDE work: deploying LLM-powered solutions inside customer organizations.

### 12.1 LLM Fundamentals
- [ ] Tokens, context windows, temperature, sampling
- [ ] Transformers (conceptual), pretraining vs fine-tuning vs RLHF
- [ ] Model families & trade-offs (capability, cost, latency)
- [ ] Hallucinations and their mitigations

### 12.2 Prompt Engineering
- [ ] System prompts, few-shot, chain-of-thought, structured output
- [ ] XML / JSON schema outputs, tool-use schemas
- [ ] Prompt iteration & versioning

### 12.3 RAG (Retrieval-Augmented Generation)
- [ ] Document parsing/OCR (PDFs, tables, scans)
- [ ] Chunking strategies
- [ ] Embeddings & vector search
- [ ] Hybrid search (BM25 + vectors), reranking
- [ ] Citations & grounding
- [ ] Vector DBs: pgvector, Pinecone, Qdrant, Weaviate, Chroma

### 12.4 Agents & Tool Use
- [ ] Function/tool calling
- [ ] Agent loops, planning, memory
- [ ] Model Context Protocol (MCP)
- [ ] Multi-agent patterns, orchestration
- [ ] Human-in-the-loop & approval flows
- [ ] Frameworks: Claude Agent SDK, LangChain/LangGraph, LlamaIndex

### 12.5 Evaluation & Reliability
- [ ] Building eval sets from real customer data
- [ ] LLM-as-judge, golden datasets, regression testing
- [ ] Latency/cost monitoring, caching, batching
- [ ] Guardrails, PII redaction, moderation
- [ ] Prompt injection & jailbreak defenses

### 12.6 Fine-tuning & Deployment (awareness level)
- [ ] When to fine-tune vs prompt vs RAG
- [ ] Open-source models (Llama, Mistral, Qwen), serving with vLLM / Ollama
- [ ] Hugging Face ecosystem

### Links
- Anthropic docs: https://docs.claude.com/
- Anthropic prompt engineering overview: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview
- Anthropic Courses (GitHub): https://github.com/anthropics/courses
- Anthropic Cookbook: https://github.com/anthropics/anthropic-cookbook
- Building Effective Agents (Anthropic): https://www.anthropic.com/engineering/building-effective-agents
- Model Context Protocol: https://modelcontextprotocol.io/
- OpenAI platform docs: https://platform.openai.com/docs
- OpenAI Cookbook: https://cookbook.openai.com/
- Hugging Face LLM course: https://huggingface.co/learn/llm-course
- Andrej Karpathy — Neural Networks: Zero to Hero: https://karpathy.ai/zero-to-hero.html
- 3Blue1Brown — Neural Networks: https://www.3blue1brown.com/topics/neural-networks
- DeepLearning.AI short courses: https://www.deeplearning.ai/short-courses/
- LangChain: https://python.langchain.com/docs/
- LangGraph: https://langchain-ai.github.io/langgraph/
- LlamaIndex: https://docs.llamaindex.ai/
- pgvector: https://github.com/pgvector/pgvector
- Pinecone Learn: https://www.pinecone.io/learn/
- Qdrant docs: https://qdrant.tech/documentation/
- Chroma: https://docs.trychroma.com/
- vLLM: https://docs.vllm.ai/
- Ollama: https://ollama.com/
- Hamel Husain — Your AI product needs evals: https://hamel.dev/blog/posts/evals/
- Eugene Yan — Patterns for building LLM systems: https://eugeneyan.com/writing/llm-patterns/
- Simon Willison's blog (prompt injection, practical LLM): https://simonwillison.net/
- Promptfoo (eval tool): https://www.promptfoo.dev/docs/intro/
- Ragas (RAG eval): https://docs.ragas.io/

### Done when
You can ship a RAG + tool-using agent over customer documents with citations, an eval suite, and guardrails.

---

## 13. Observability & Debugging in Production

### Subtopics
- [ ] Logging best practices (structured logs, correlation IDs)
- [ ] Metrics: RED/USE methods, Prometheus, Grafana
- [ ] Tracing: OpenTelemetry, Jaeger
- [ ] Error tracking: Sentry
- [ ] APM tools: Datadog, New Relic, Honeycomb
- [ ] Alerting, on-call, runbooks, incident response, postmortems
- [ ] Debugging with limited access (no prod shell, customer-controlled logs)
- [ ] LLM observability: Langfuse, LangSmith, Arize Phoenix, Helicone

### Links
- OpenTelemetry docs: https://opentelemetry.io/docs/
- Prometheus: https://prometheus.io/docs/introduction/overview/
- Grafana tutorials: https://grafana.com/tutorials/
- Sentry docs: https://docs.sentry.io/
- Honeycomb learn: https://www.honeycomb.io/resources
- Google SRE Workbook: https://sre.google/workbook/table-of-contents/
- Langfuse: https://langfuse.com/docs
- Arize Phoenix: https://docs.arize.com/phoenix
- Atlassian incident management guide: https://www.atlassian.com/incident-management

### Done when
You can instrument a service with logs, metrics, and traces, and write a blameless postmortem.

---

## 14. Customer-Facing & Soft Skills

This is what separates a great FDE from a good engineer.

### Subtopics
- [ ] **Discovery:** asking great questions, finding the real problem behind the stated one
- [ ] **Stakeholder mapping:** champion, economic buyer, blocker, end user
- [ ] **Active listening & note-taking**, summarizing back to confirm
- [ ] **Translating** between technical and business language
- [ ] **Scoping & expectation-setting:** saying "no" / "not yet" gracefully
- [ ] **Demos & storytelling:** show value in 5 minutes
- [ ] **Written communication:** status updates, design docs, emails, RFCs
- [ ] **Presenting** to executives & to engineers
- [ ] **Managing ambiguity & prioritization** under pressure
- [ ] **Conflict & difficult customer handling**
- [ ] **Working on-site:** building trust, working inside their processes
- [ ] **Feedback loop to product:** writing crisp, evidence-backed feature requests
- [ ] **Time management & context switching** across multiple customers
- [ ] **Bias to action:** prototype first, perfect later

### Links
- *The Mom Test* (book/site): https://www.momtestbook.com/
- *Never Split the Difference* — summary & negotiation basics: https://www.blackswanltd.com/the-edge
- *Crucial Conversations*: https://cruciallearning.com/crucial-conversations/
- *The Pyramid Principle* (structured communication, Barbara Minto): https://www.barbaraminto.com/
- *Radical Candor*: https://www.radicalcandor.com/
- Julia Evans — comics on technical communication: https://jvns.ca/
- Toastmasters (public speaking practice): https://www.toastmasters.org/
- Stripe Press — *Working in Public* / Stripe's writing culture (search "Stripe writing culture")
- Amazon 6-pager approach: search "Amazon narrative memo 6-pager"
- Google Tech Writing courses (free): https://developers.google.com/tech-writing
- Lenny's Newsletter (product + customer insights): https://www.lennysnewsletter.com/

### Practice drills
- [ ] Record yourself explaining a technical concept to a non-technical person (3 min)
- [ ] Run a mock discovery call with a friend playing a vague customer
- [ ] Write a 1-page design doc for a hypothetical customer integration
- [ ] Give a 5-minute demo of one of your projects, no slides

### Done when
You can run a 30-minute discovery call and leave with a clear problem statement, success metrics, and next steps.

---

## 15. Product Thinking & Business Acumen

### Subtopics
- [ ] Problem → solution fit; jobs-to-be-done
- [ ] Metrics: ROI, time saved, revenue impact, adoption, retention
- [ ] MVP scoping, prioritization frameworks (RICE, MoSCoW, impact/effort)
- [ ] Build vs buy vs configure
- [ ] Pricing, contracts, SLAs, POCs/pilots, and how deals progress (land & expand)
- [ ] Customer success metrics: NPS, churn, time-to-value
- [ ] Reading a customer's business: P&L basics, org charts, operations
- [ ] Writing a PRD / one-pager

### Links
- Shape Up (Basecamp, free): https://basecamp.com/shapeup
- *Inspired* / SVPG articles: https://www.svpg.com/articles/
- Jobs To Be Done overview: https://jtbd.info/
- RICE scoring: https://www.intercom.com/blog/rice-simple-prioritization-for-product-managers/
- Y Combinator Startup School: https://www.startupschool.org/
- Reforge blog: https://www.reforge.com/blog
- Harvard Business Review — customer discovery articles: https://hbr.org/
- Investopedia — business/finance basics: https://www.investopedia.com/

### Done when
You can frame a POC with explicit success criteria and a measurable business outcome.

---

## 16. Industry Domain Knowledge

Pick 1–2 verticals to specialize in; FDE value compounds with domain expertise.

| Vertical | What to learn | Starter links |
|---|---|---|
| **Finance / Banking** | Payments, KYC/AML, risk, ledgers, ISO 20022, fraud | https://stripe.com/guides · https://www.investopedia.com/ |
| **Healthcare** | HL7 / FHIR, EHRs (Epic/Cerner), HIPAA, claims | https://www.hl7.org/fhir/ · https://www.hhs.gov/hipaa/ |
| **Government / Defense** | FedRAMP, IL levels, air-gapped deployment, clearances | https://www.fedramp.gov/ |
| **Supply chain / Manufacturing** | ERP (SAP), MES, IoT, demand forecasting | https://www.sap.com/products/erp.html · https://www.ascm.org/ |
| **Energy / Utilities** | SCADA, time-series data, grid ops | https://www.energy.gov/ |
| **Retail / E-commerce** | Inventory, pricing, recommendations, POS | https://shopify.dev/docs |
| **Insurance** | Underwriting, claims, actuarial basics | https://www.iii.org/ |
| **Legal / Compliance** | Contracts, e-discovery, regulation tracking | — |
| **Telecom** | OSS/BSS, CDRs, network data | https://www.tmforum.org/ |

Also useful: **Enterprise software ecosystems** — Salesforce, SAP, ServiceNow, Workday, Snowflake.
- Salesforce Trailhead (free): https://trailhead.salesforce.com/
- ServiceNow developer: https://developer.servicenow.com/
- SAP Learning: https://learning.sap.com/

---

## 17. Portfolio Projects

Build 3–4 solid projects. Each should have: a README, architecture diagram, demo link/video, tests, and a "customer problem" framing.

### Project 1 — Messy Data Integration Pipeline
- Ingest data from 3 sources (REST API + CSV + SQL DB), clean, join, load to Postgres/DuckDB
- Add Airflow/Dagster scheduling, dbt transforms, data-quality checks
- Dashboard in Streamlit/React
- **Skills:** SQL, ETL, APIs, orchestration, UI

### Project 2 — RAG Assistant over Enterprise Docs
- Parse PDFs/Confluence/Notion exports, chunk, embed, store in pgvector
- Hybrid search + reranking, citations, permission-aware retrieval
- Eval suite with 50+ Q&A pairs; track accuracy over iterations
- **Skills:** LLMs, RAG, evals, security

### Project 3 — Tool-Using AI Agent for a Business Workflow
- Example: support-ticket triage agent that reads tickets, queries a DB, calls a CRM API, drafts replies, escalates with human approval
- Expose tools via an MCP server
- Logging/tracing with Langfuse; guardrails; cost tracking
- **Skills:** agents, MCP, observability, product sense

### Project 4 — Deploy-Anywhere Packaged Product
- Dockerize + Helm chart + Terraform for AWS
- SSO integration (Okta/Auth0), RBAC, audit logs
- CI/CD with GitHub Actions; document an "air-gapped install" guide
- **Skills:** DevOps, security, deployment, documentation

### Project 5 (Capstone) — Mock Customer Engagement
- Pick a real-world-ish business (e.g., a regional hospital, logistics firm)
- Write: discovery notes, problem statement, success metrics, architecture, 2-week plan, demo, and a retrospective
- This doubles as a story bank for interviews.

### Where to find data & problems
- Kaggle datasets: https://www.kaggle.com/datasets
- Public APIs list: https://github.com/public-apis/public-apis
- data.gov: https://data.gov/
- Hugging Face datasets: https://huggingface.co/datasets
- SEC EDGAR filings: https://www.sec.gov/edgar
- Synthea (synthetic health data): https://synthetichealth.github.io/synthea/

---

## 18. Interview Preparation

### Typical FDE interview loop
1. **Recruiter screen** — motivation, travel comfort, communication
2. **Coding round** — practical Python/SQL, data manipulation, API work
3. **System design / decomposition** — design an integration or data platform for a customer scenario
4. **Customer scenario / case study** — ambiguous problem, you ask questions & propose a plan
5. **Behavioral / values** — ownership, conflict, ambiguity, impact
6. **Hiring manager** — fit, depth of past projects
7. **(Some companies) Take-home or live build** — build a small integration or app in a few hours

### Preparation checklist
- [ ] 100–150 LeetCode problems (arrays, hash maps, strings, graphs, parsing)
- [ ] SQL: 50+ problems incl. window functions
- [ ] 5 system design walkthroughs (data pipeline, RAG system, multi-tenant SaaS, webhook processor, rate limiter)
- [ ] 8–10 STAR stories (conflict, failure, ambiguity, leadership, customer win, tight deadline, learned fast, influenced without authority)
- [ ] Mock "customer scenario" interviews (practice asking clarifying questions *before* solving)
- [ ] Research the company's product, customers, recent news, and FDE job description
- [ ] Prepare 5 thoughtful questions to ask the interviewer
- [ ] Practice explaining each portfolio project in 2 min and 10 min versions

### Sample customer-scenario prompts to practice
- "A hospital wants to reduce readmissions using their EHR data. Where do you start?"
- "A logistics company's data is in 12 spreadsheets and an old SQL Server. They want a live dashboard in 2 weeks."
- "A bank wants an LLM assistant for compliance analysts but is nervous about data leaving their network."
- "Your POC works but the customer's IT blocks all outbound traffic. What now?"

### Links
- NeetCode: https://neetcode.io/
- LeetCode: https://leetcode.com/
- DataLemur: https://datalemur.com/
- Pramp (free mock interviews): https://www.pramp.com/
- interviewing.io: https://interviewing.io/
- STAR method guide: https://www.themuse.com/advice/star-interview-method
- Exponent (system design/PM mock questions): https://www.tryexponent.com/
- Glassdoor interview reviews (search "<company> Forward Deployed Engineer interview"): https://www.glassdoor.com/
- Blind (community): https://www.teamblind.com/
- *Cracking the Coding Interview* (book)
- *System Design Interview* by Alex Xu (book): https://bytebytego.com/

---

## 19. 24-Week Study Plan

Assumes ~10–15 hours/week. Compress or extend as needed.

| Weeks | Focus | Deliverable |
|---|---|---|
| **1–2** | Python deep-dive, Git, Linux/shell | CLI tool with tests on GitHub |
| **3–4** | SQL + PostgreSQL (window functions, indexing) | 50 SQL problems solved; schema design exercise |
| **5–6** | APIs & backend (FastAPI), HTTP, auth basics | REST service + client w/ retries & pagination |
| **7–8** | DSA part 1 (arrays, hashing, strings, trees) | 50 LeetCode problems |
| **9–10** | Data engineering (pandas/DuckDB, Airflow, dbt) | **Project 1** complete |
| **11–12** | Docker, CI/CD, cloud (AWS core), Terraform | Deployed app on AWS via IaC |
| **13–14** | LLM fundamentals, prompting, RAG | **Project 2** started |
| **15–16** | Agents, tool use, MCP, evals, guardrails | **Project 2** done, **Project 3** started |
| **17–18** | Security/auth (OAuth, SSO, OWASP), observability | **Project 3** done; add tracing |
| **19–20** | Kubernetes basics, packaging, enterprise deployment | **Project 4** complete |
| **21** | System design deep-dive (5 designs) | Written design docs |
| **22** | Customer-facing skills: discovery drills, demos, writing | **Project 5** capstone |
| **23** | DSA part 2 + mock coding interviews | 100+ LeetCode total |
| **24** | Full mock loops, resume/LinkedIn polish, applications | Applications out; interview calendar |

**Weekly rhythm suggestion**
- Mon–Thu: learn + build (1.5–2 hrs/day)
- Fri: review + write notes/blog
- Sat: longer project block (3–4 hrs)
- Sun: rest / light reading

---

## 20. Books, Blogs & Communities

### Books
- *Designing Data-Intensive Applications* — Martin Kleppmann
- *The Pragmatic Programmer* — Hunt & Thomas
- *Staff Engineer* — Will Larson (also https://staffeng.com/)
- *An Elegant Puzzle* — Will Larson
- *The Mom Test* — Rob Fitzpatrick
- *Crossing the Chasm* — Geoffrey Moore (enterprise adoption)
- *The Phoenix Project* — Gene Kim et al. (DevOps narrative)
- *Site Reliability Engineering* — Google (free online)
- *AI Engineering* — Chip Huyen
- *The Pyramid Principle* — Barbara Minto
- *Software Engineering at Google* (free online): https://abseil.io/resources/swe-book

### Blogs / Newsletters
- Palantir Blog: https://blog.palantir.com/
- Pragmatic Engineer: https://newsletter.pragmaticengineer.com/
- ByteByteGo newsletter: https://blog.bytebytego.com/
- Latent Space (AI engineering): https://www.latent.space/
- Simon Willison: https://simonwillison.net/
- Eugene Yan: https://eugeneyan.com/
- Chip Huyen: https://huyenchip.com/blog/
- Hamel Husain: https://hamel.dev/
- Netflix / Uber / Stripe engineering blogs (real-world architectures)

### Communities
- r/cscareerquestions, r/ExperiencedDevs, r/dataengineering (Reddit)
- Hacker News: https://news.ycombinator.com/
- Latent Space Discord, Hugging Face Discord, MLOps Community: https://mlops.community/
- Data Talks Club Slack: https://datatalks.club/
- Local meetups (Meetup.com) and AI hackathons — great for networking and demos

### YouTube channels
- freeCodeCamp, Fireship, ByteByteGo, NeetCode, TechWorld with Nana, Andrej Karpathy, 3Blue1Brown, Anthropic, AI Engineer

---

## 21. Progress Tracker

Copy this table into your notes and update weekly.

| Area | Level (0–5) | Last reviewed | Next action |
|---|---|---|---|
| Python | | | |
| TypeScript/JS | | | |
| DSA | | | |
| SQL | | | |
| APIs/Backend | | | |
| Frontend | | | |
| Data Engineering | | | |
| Cloud (AWS/GCP/Azure) | | | |
| Docker/K8s/CI-CD | | | |
| Security/Auth | | | |
| System Design | | | |
| LLM/RAG/Agents | | | |
| Observability | | | |
| Communication/Discovery | | | |
| Product/Business | | | |
| Domain knowledge | | | |

**Level guide:** 0 = unfamiliar · 1 = aware · 2 = can follow tutorials · 3 = can build independently · 4 = can teach / debug deeply · 5 = expert

### Weekly review questions
1. What did I ship this week?
2. What confused me, and did I resolve it?
3. Which customer-facing skill did I practice?
4. What's the one thing to do next week that moves the needle most?

---

### Final advice
- **Depth in 2–3 areas, working knowledge in the rest.** FDEs are T-shaped.
- **Build in public:** write short posts about what you learn and ship.
- **Always frame work as customer problems and outcomes**, not just technologies.
- **Speed + judgment** beats perfection: ship a prototype, get feedback, iterate.
- Revisit this roadmap every month and adjust to the job descriptions you're targeting.
