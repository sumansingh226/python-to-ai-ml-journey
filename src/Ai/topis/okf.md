# Google OKF — Open Knowledge Format: Complete Detailed Guide
## What It Is, Why Google Launched It June 2026, Spec, RAG vs OKF, Production Patterns

> **Core Thesis:** Google OKF = Open Knowledge Format, launched by Google Cloud Data Cloud team on June 12, 2026, v0.1 Apache-2.0, vendor-neutral. Definition: A directory of Markdown files with YAML frontmatter, each file = one Concept, file path = Concept ID, Markdown links = knowledge graph. Solves "context sprawl" — most important knowledge (metric definitions, caveats, ownership, join guidance, runbooks) scattered across wikis, tickets, dashboards, people's heads. Agents can't infer like humans. OKF turns scattered context into portable, versionable, Git-reviewable bundle that both humans and AI agents can consume reliably. Quote Google: "What's missing is a format, not another service." Builds on Andrej Karpathy's LLM Wiki gist + AGENTS.md pattern. Not replacement for Avro/Protobuf/OpenAPI/dbt — it's curation/metadata wrapper that points at sources of truth and adds context they don't capture. File-based packaging standard for curated knowledge, small enough to live in git, structured enough to index, neutral enough to move across tools.

### Table of Contents
1. What is Google OKF? Definition in One Sentence
2. Why OKF? The Real Problem — Context Sprawl
3. OKF vs OKR vs Knowledge Graph vs RAG vs Catalogs
4. How OKF Works — Building Blocks
5. The Spec v0.1 — YAML Frontmatter, Concept ID, Bundle Structure
6. Real Examples — Metrics, Tables, Runbooks, APIs
7. OKF vs RAG — Traversal vs Similarity Search
8. Adoption Patterns — 4 Production Patterns
9. Tooling & Ecosystem — Reference Implementation, Validators, Kiso, OKF4net
10. Why It Matters for Developers, Content Creators, Agentic AI
11. How to Build Your Own OKF Bundle — Step by Step
12. Production Checklist & Governance

---

### 1. What is Google OKF? Definition in One Sentence

**OKF in one sentence: a directory of Markdown + YAML frontmatter**

Per Google's announcement June 12, 2026 and SPEC.md: OKF is a vendor-neutral way to package curated organizational knowledge as a directory of Markdown files. Each file includes YAML frontmatter for structured metadata. Key idea: it's "just files." No required SDK, runtime, schema registry, or central service. Markdown + YAML deliberate trade: humans can review in PRs, diffs readable, tools can parse frontmatter to index and retrieve.

**Official definition from Google Cloud Blog June 12, 2026:**

> Open Knowledge Format (OKF) v0.1 is an open, vendor-neutral format for representing metadata, context, and curated knowledge that AI systems need, published as Apache-2.0. A Knowledge Bundle is a distributable directory tree. Each Concept is exactly one Markdown document. Concept ID is derived from file path minus .md. File path is concept's identity, so tables/orders.md has concept ID tables/orders.

**What OKF is not:**

- Not a replacement for domain-specific schemas or interface definitions such as Avro, Protobuf, OpenAPI, dbt models. Instead acts as curation and metadata wrapper. Points at sources of truth and adds context they don't capture well like usage guidance and operational notes. Reduces schema duplication avoids two sources of truth.
- Not same as Google Knowledge Graph / schema.org markup. OKF is for internal file-based knowledge bundles meant to be shared and used by tools and agents. Knowledge Graph Search API is hosted service that returns entity results as JSON-LD using schema.org types. OKF lives in repos and filesystems. Knowledge Graph is online entity search API.
- Not a runtime, so you do not install anything to use it.
- Not a search index, so does not retrieve or rank fragments for you.
- Not a model. Google puts plainly: "What's missing is a format, not another service."

**Minimally opinionated:** Only type is required. Producer decides what types exist and what other fields each document carries.

### 2. Why OKF? The Real Problem — Context Sprawl

Most teams don't suffer from lack of data. Suffer from lack of shared context. Definitions, caveats, ownership, how to use this safely guidance scattered across wikis, tickets, dashboards, people's heads. Google describes this as metadata, context, and curated knowledge spread across too many surfaces to share or reuse cleanly.

Fragmentation hurts humans. Hurts AI agents and cross-team work even more. People compensate with experience. They know which wiki is more correct, who to ask, which dashboard is legacy. Agents don't have intuition. When context is missing or split across systems, agent has to infer and guess. Leads to confident wrong answers and brittle automations.

**Separate data from context:**

- **Data:** table schemas, API contracts, dbt models
- **Context:** metric definitions, caveats, ownership, join guidance, deprecations, runbooks

Without context, two teams can query same table and still disagree what revenue means.

Before OKF, developer debugging revenue discrepancy might find SQL in dashboard, definition in wiki page, deprecation note buried in ticket. Then repeat same archaeology next week. OKF positioned as portable corpus that tools and agents can consume, not as another portal.

**OKF turns agent context into reviewable artifact instead of hidden integration layer.** For data and platform teams, value is not that Markdown is new; it is that Google is putting small explicit interchange convention around kind of knowledge bundles teams already keep in catalogs, wikis, docs repos, runbooks.

**Related patterns:**

- Andrej Karpathy's LLM Wiki gist named pattern
- AGENTS.md files, Obsidian vaults wired to coding agents, metadata as code repos all chase same idea
- Each one bespoke. No standard way to hand structured knowledge to agent, so every agent builder solves context assembly from scratch. OKF standardizes pattern.

### 3. OKF vs OKR vs Knowledge Graph vs RAG vs Catalogs

**User asked "Google OKF" — often confused with OKR. Clarify:**

**OKF = Open Knowledge Format (June 2026):** File format for AI agent knowledge bundles. Directory of markdown + YAML. Vendor-neutral. For context engineering.

**OKR = Objectives and Key Results (1999):** Goal-setting framework introduced to Google by John Doerr in 1999, learned from Intel Andy Grove. Backbone of Google strategic planning. Framework that allows organizations define clear goals measure progress through specific outcomes. Objective = what want achieve (qualitative ambitious), Key Results = how measure success (quantitative 2-4 per objective). Google uses two categories: committed goals (must hit 100%) and aspirational goals (stretch, 70% success considered success). Used by Google, Intel, Netflix. NOT related to OKF except both from Google culture.

**Quick table:**

| | OKF (Open Knowledge Format) | OKR (Objectives & Key Results) |
|---|---|---|
| Launched | June 12, 2026, Google Cloud | 1999 to Google by John Doerr from Intel |
| What | File format: Markdown + YAML bundle | Goal framework: Objective + Key Results |
| Purpose | Package knowledge for agents | Align teams around goals |
| Format | Directory tree, concept-per-file, path = ID | Objective (qualitative) + 2-4 KRs (quantitative) |
| Example | metrics/revenue_net.md with type: metric | Objective: Launch OKF adoption, KR: 10 teams ship bundle |

This doc focuses on OKF, but includes OKR appendix since confusion common.

**OKF vs other knowledge systems:**

| Dimension | OKF | RAG | Metadata Catalogs / OpenAPI | Google Knowledge Graph |
|---|---|---|---|---|
| Represents | Relationships between concepts | Relevant text chunks | Data structures | Public entities |
| Format | Markdown + YAML | Vector embeddings | Schema metadata (Avro, Protobuf, OpenAPI) | JSON-LD schema.org |
| Retrieval | Traversable knowledge graph via links | Similarity search | Inventory / shape | Entity search API |
| Human/AI | Both readable, Git-reviewable | Primarily retrieval-oriented | Primarily governance | API |
| Runtime | None, just files | Vector DB, embedding model | Catalog service | Hosted service |
| Identity | File path = concept ID | Vector ID | Schema registry ID | KG MID |
| Versioning | Git, tarball releases | Index rebuild | Registry version | Google managed |

**Key quote:** RAG answers "what text is similar to this query." Schema answers "what does this data look like." OKF answers "how does this knowledge fit together."

### 4. How OKF Works — Building Blocks

Once accept "it's just files," next question how files become something tools can index, link, retrieve. OKF answer small set filesystem-friendly rules.

**Knowledge Bundles, Concepts, Concept IDs:**

Spec defines filesystem-native mental model:

- **Knowledge Bundle:** distributable directory tree. Can be stored in Git, reviewed like docs, linked as graph, consumed by agent pipelines without proprietary runtime. Can ship as tarball, host in git repo, mount on filesystem.
- **Each Concept is exactly one Markdown document.**
- **Concept ID is derived from file path (minus .md).** Path-based IDs stay stable under version control. Make easy for tools reference concepts without inventing separate identifier scheme.

Example:

```
knowledge-bundle/
  datasets/
    ga4_ecommerce.md            # conceptId: datasets/ga4_ecommerce
  tables/
    ga4/events.md               # conceptId: tables/ga4/events
  metrics/
    revenue_net.md              # conceptId: metrics/revenue_net
  runbooks/
    revenue_discrepancy.md      # conceptId: runbooks/revenue_discrepancy
  apis/
    orders_api.md               # conceptId: apis/orders_api
  policies/
    refunds.md                  # conceptId: policies/refunds
```

**YAML frontmatter as queryable surface area:**

OKF keeps structure intentionally small. Google highlights compact set frontmatter fields type, title, description, resource, tags, timestamp that tools can index for filtering and routing. Spec defines normative rules. This makes "retrieve all runbooks tagged incident-response" metadata query instead of full-text guessing game.

Only type required. Producer decides types and other fields.

**Markdown body as human-first, agent-usable narrative layer:**

Uses plain Markdown body. Keeps content readable in GitHub or internal doc sites. Stays easy for agents to chunk, quote, follow links. Links express relationships beyond folders. For example metric can point to source table and runbook for incidents.

```
See source table: ../tables/ga4/events.md
Incident response: ../runbooks/revenue_discrepancy.md
```

**index.md and log.md conventions:**

- index.md files act as entry points and offer progressive disclosure. Root carries okf_version.
- log.md files record chronological change history. Both optional but recommended.

**Link resolution:** Just path resolution, so agent traverses deliberately rather than guessing. No SDK, no runtime, no proprietary schema sits between agent and files.

### 5. The Spec v0.1 — YAML Frontmatter, Concept ID, Bundle Structure

**v0.1 Spec fits on single page. Published June 12, 2026 Apache-2.0 by Google Cloud Data Cloud team. GitHub SPEC.md.**

**Directory structure:**

```
.okf/
├── index.md                  # progressive disclosure (root carries okf_version)
├── datasets/
│   └── ga4_ecommerce.md
├── tables/
│   └── ga4/
│       └── events.md
├── metrics/
│   └── revenue_net.md
├── runbooks/
│   └── revenue_discrepancy.md
└── log.md                    # optional change history
```

**Frontmatter fields (reserved):**

| Field | Required | Description | Example |
|---|---|---|---|
| type | Yes | Concept type, producer-defined | metric, table, dataset, runbook, api-endpoint, policy |
| title | No but recommended | Human title | "Revenue (Net)" |
| description | No | Short description | "Net revenue excluding refunds and chargebacks." |
| resource | No | Pointer to source of truth | bigquery://analytics.metrics/revenue_net or https://api.example.com/openapi.yaml#/paths/~1v1~1orders/post |
| tags | No | List for filtering | [finance, gaap, executive-dashboard, deprecated, oncall] |
| timestamp | No | Freshness signal ISO8601 | 2026-06-12T00:00:00Z |

Spec defines normative rules for frontmatter.

**Example 1: Metric**

```
---
type: metric
title: "Revenue (Net)"
description: "Net revenue excluding refunds and chargebacks."
resource: bigquery://analytics.metrics/revenue_net
tags: [finance, gaap, executive-dashboard, revenue]
timestamp: 2026-06-12T00:00:00Z
---

Metric notes, caveats, and links go here in Markdown.

## Definition
SUM(gross) - SUM(refunds) - SUM(chargebacks) where refund_status != 'pending'

## Caveats
- Excludes test orders (order_id LIKE 'TEST%')
- Delayed 2h due to ETL

## Ownership
Owner: finance-data-team@

Derived from [Orders table](../tables/orders.md). Refund handling: [Refund policy](../policies/refunds.md).

See incident response: [Revenue discrepancy runbook](../runbooks/revenue_discrepancy.md)
```

**Example 2: API Endpoint**

```
---
type: api-endpoint
title: POST /v1/orders
description: Create order with idempotency
resource: https://api.example.com/openapi.yaml#/paths/~1v1~1orders/post
tags: [orders, public-api]
timestamp: 2026-06-12T00:00:00Z
---

Use `Idempotency-Key` for retries. Deprecated fields: `promoCode` (use `discounts[]`).

## Auth
Bearer token required

## Related
Source table: [orders table](../tables/orders.md)
```

**Example 3: Runbook**

```
---
type: runbook
title: Revenue discrepancy triage
description: Triage and mitigation steps for revenue mismatch
tags: [incident-response, revenue, oncall]
timestamp: 2026-06-12T00:00:00Z
---

## Symptoms
Revenue dashboard shows drop >5% vs source

## Diagnosis
1. Check BigQuery job status
2. Compare metrics/revenue_net.md definition vs query

## Mitigation
...

## Escalation
Owner: data-oncall
```

**Example 4: Refund Policy (for your agentic AI curriculum)**

```
---
type: policy
title: Refund Policy v2.3 — Bundle Promotion Rule
description: Bundle promotions require approval, never auto-refund
resource: docs/policies/refund_v2.3.md
tags: [refund, bundle, policy, approval-required]
timestamp: 2026-10-24T00:00:00Z
---

## Rule
Per page 25 of refund policy: Bundle promotion refunds need approval per policy page 25 - never auto-refund bundles.

## Validation Steps
1. Check order has bundle_id
2. If bundle_id present, check if promotion active
3. If promotion active, require approval_flow

## Related
Orders: ../tables/orders.md
Approval: ../runbooks/approval_flow.md
```

**Validation:** File path is concept identity, so tables/orders.md has concept ID tables/orders (OKF v0.1 spec). Concept-per-file rule easiest when organize by domain folders. Express relationships as links rather than mega-pages.

### 6. Real Examples — Metrics, Tables, Runbooks, APIs (Full Bundle)

**Complete knowledge-bundle example for SaaS:**

```
knowledge-bundle/
├── .okf/
│   └── index.md  # okf_version: 0.1, entry points
├── metrics/
│   ├── revenue_net.md
│   ├── wau.md  # weekly active users
│   └── churn_rate.md
├── tables/
│   ├── orders.md
│   ├── ga4/
│   │   └── events.md
│   └── users.md
├── datasets/
│   └── ga4_ecommerce.md
├── apis/
│   ├── orders_api.md
│   └── users_api.md
├── policies/
│   ├── refunds.md
│   └── privacy.md
├── runbooks/
│   ├── revenue_discrepancy.md
│   ├── payments_latency.md
│   └── approval_flow.md
└── log.md
```

**index.md (progressive disclosure):**

```
---
type: index
okf_version: 0.1
title: Knowledge Bundle Index
---

# Knowledge Bundle

## Metrics
- [Revenue Net](./metrics/revenue_net.md)
- [WAU](./metrics/wau.md)

## Tables
- [Orders](./tables/orders.md)

## Runbooks
- [Revenue Discrepancy](./runbooks/revenue_discrepancy.md)

Start here for onboarding.
```

**How agent navigates:**

Agent navigates bundle by reading index.md, scoping to topic, then following links same way you would click through wiki. Link resolution is just path resolution, so agent traverses deliberately rather than guessing. No SDK.

Incident bot can pull runbook and route to right owner. Analytics agent can retrieve metric concept to avoid using wrong definition.

### 7. OKF vs RAG — Traversal vs Similarity Search

**RAG process:** Pulls fragments at query time. Embed docs, store vectors, at runtime system fetches chunks that look closest to question. Agent never sees how chunks relate. Guesses at structure from whatever text happens to land in context window. Chops documents into fragments retrieves by similarity but relationships between concepts often have to be inferred rather than explicitly represented.

**OKF process:** Inverts process. Relationships written down before agent ever asks question. Concepts link to each other with markdown links, so agent can start at one file and walk to orders table, then to metric that depends on it, then to runbook that explains join. Traverses meaning deliberately instead of stitching together whatever retriever returned.

**Comparison:**

- **RAG failure modes:** Retrieval failure (relevant doc not retrieved), ranking failure (irrelevant higher), lost in middle, chunking breaks relationships, needs vector DB, embedding model, reranker, top_k tuning.
- **OKF advantages:** No vector DB, no embeddings, no chunking, no ranking — just files. Path-based IDs stable. Links explicit. Git-reviewable. Versionable. Human and AI readable. Interoperability without glue code: format not service — bundles are just files, so producers consumers only need filesystem access plus Markdown/YAML parser. Can keep bundle in git, publish pinned tarball for reproducible runs, or mount into environment where tools and agents can read it. Cross-stack reuse: data platform team can publish bundle once, then Python agent pipeline, TypeScript IDE helper, catalog ingestion job can all consume same directory tree.

**Many agent stacks will run both, using OKF for relational context and retrieval for long-tail lookups.** OKF for curated stable pre-compiled knowledge layer that agents can load into context directly. RAG for large unstructured corpus.

**Google Knowledge Catalog integration:** Google says Google Cloud Knowledge Catalog can ingest OKF and serve it to agents. Split useful: OKF stays interchange layer. Catalogs become optional UX and indexing layers, not only home for context.

### 8. Adoption Patterns — 4 Production Patterns

**Pattern 1: Concept-per-file bundles organized by domain**

Spec's concept-per-file rule easiest when organize by domain folders. Express relationships as links rather than mega-pages. Simple starting tree keeps concepts small enough to reuse.

```
knowledge-bundle/
  metrics/revenue_net.md
  tables/orders.md
  policies/refunds.md
  runbooks/revenue_discrepancy.md
```

Inside metrics/revenue_net.md keep YAML frontmatter queryable. Use Markdown links to connect graph.

**Pattern 2: Distribute OKF as artifact (repo, release, filesystem)**

Because bundles are just files, distribution is packaging decision. Use git repo for collaboration and review. Publish tarball releases for pinned reproducible consumption. Optionally sync to shared mount for runtime access.

For agents, pin explicitly: use bundle v2026.06 for this workflow run. Prevents retrieval drifting mid-incident.

```
tar -czf knowledge-bundle.tgz knowledge-bundle/
# attach knowledge-bundle.tgz to release like v2026.06
```

**Pattern 3: Pair OKF with catalog ingestion (Google Cloud Knowledge Catalog example)**

Google says Knowledge Catalog can ingest OKF and serve it to agents. OKF stays interchange layer. Catalogs become optional UX and indexing layers.

**Pattern 4: OKF as LLM-wiki + llms.txt + AGENTS.md**

Many teams already have AGENTS.md files, Obsidian vaults wired to coding agents, metadata as code repos. OKF turns LLM-wiki idea into standardized portable LLM-wiki pattern: write human-readable Markdown, add small amount structured metadata, ship result as bundle of files. A docs team can curate product-concepts bundle for feature behavior and deprecations. Data team can curate analytics-concepts bundle for metrics, tables, runbooks. Can publish both internally, open-source subset, or share across org boundaries.

**CI gates example:**

```python
# Example CI gate: fail if any concept link points to missing file
python scripts/check_links.py knowledge-bundle

# Fail if missing required frontmatter
python scripts/check_frontmatter.py knowledge-bundle --required type title description
```

Because OKF diffable text, fits normal engineering discipline. Metric definitions and runbooks can be updated via PRs, reviewed by owners, rolled back when needed. Turns why did this number change into git blame instead of Slack archaeology.

### 9. Tooling & Ecosystem — Reference Implementation, Validators, Kiso, OKF4net

**Official:**

- Google Cloud Blog announcement June 12, 2026
- GitHub SPEC.md (v0.1 fits single page, minimal)
- Reference tooling in knowledge-catalog repository
- Google Cloud Knowledge Catalog can ingest OKF

**Third-party (as of Oct 2026):**

- **Kiso:** Shows how OKF bundles can become static websites and llms.txt outputs
- **OKF4net 0.6.0:** .NET implementation of OKF v0.2 — core library and okf CLI — auditing what AI agent knows, zero-dependency .NET. Base implementation.
- **google-okf PyPI:** Python package — The Open Knowledge Format (OKF v0.1) is open vendor-neutral standard introduced by Google Cloud to formalize LLM Wiki pattern. Instead of feeding raw fragmented inconsistent documentation or database formats directly into vector databases, OKF structures knowledge into unified version-controlled Git-friendly directory tree.
- **GitBook:** Blog explains OKF — GitBook pages carry structured headings and metadata, so frontmatter fields OKF reserves have natural home. Git Sync keeps docs in version-controlled repository, which gives file-and-history backbone OKF expects. Also exposes machine-readable output, so agent can read same content readers see. Gives docs dual life: maintain one set of docs that publishes clean site for people and serves organized linked knowledge to agents reasoning over it.
- **Validators:** Community scripts check_links.py, check_frontmatter.py, auditing what agent knows.

**Ecosystem adoption watch:**

Adoption will matter more than announcement. Watch for ingestion support from catalog vendors, competing clouds, agent frameworks; validators that catch broken links and missing metadata; case studies showing OKF bundles improve retrieval quality or reduce integration work. Without ecosystem, OKF may remain clean draft spec rather than working interchange standard. Strongest feature also risk: minimal structure keeps adoption easy, but production value depends on disciplined curation and tooling around bundle.

**What to watch next:**

- OKF v0.2 frontmatter requirements, two ways to check folder
- Ingestion support from catalogs (Alation, Atlan, Collibra)
- Agent frameworks (LangGraph, CrewAI, AutoGen) native OKF loaders
- Competing clouds (AWS, Azure) support

### 10. Why It Matters for Developers, Content Creators, Agentic AI

**For developers: interoperability, workflows, agent grounding**

- Interoperability without glue code: format, not service. Bundles are just files, so producers consumers only need filesystem access plus Markdown/YAML parser. Keep bundle in git, publish pinned tarball for reproducible runs, or mount into environment where tools and agents can read it. Concrete payoff cross-stack reuse: data platform team can publish bundle once, then Python agent pipeline, TypeScript IDE helper, catalog ingestion job can all consume same directory tree.
- Knowledge as code practices applied to context: diffable text fits engineering discipline. Metric definitions and runbooks updated via PRs, reviewed by owners, rolled back when needed. Turns why did this number change into git blame instead of Slack archaeology. Spec's version-control friendliness enabling detail.
- Better agent grounding: fewer hallucinations, more reliable automation. Google frames OKF as way to ground agents with right context. Includes definitions, caveats, deprecations, operational procedures. Stable concept IDs plus queryable frontmatter let retrieval start narrow by type and tags. Tools can then traverse links to assemble full story for task.

**For content creators: LLM-wiki you can ship**

- OKF as standardized portable LLM-wiki pattern: Turns LLM-wiki idea into something teams can adopt without committing to one wiki product. Write human-readable Markdown, add small amount structured metadata, ship result as bundle of files. Portability unlock: docs team can curate product-concepts bundle for feature behavior and deprecations, data team can curate analytics-concepts bundle for metrics tables runbooks. Can publish both internally, open-source subset, or share across org boundaries.
- Metadata that makes content discoverable reusable: Tags let slice content by audience or lifecycle (deprecated, oncall, exec). resource anchors concept to system of record. timestamp provides freshness signal search and agents can respect. Over time editors can standardize templates per type so readers recognize shape quickly.
- Publishing and maintenance workflows that don't fight tools: Because uses Markdown renders cleanly on GitHub/GitLab. Can sync into internal docs portal without rewriting content. Google highlights shipping bundles as artifacts which maps well to editorial release trains. Example monthly data platform bundle release with changelogs review rotations style guide.

**For Agentic AI (your curriculum context):**

- **Solves context engineering problem:** OKF is curated stable pre-compiled knowledge layer that agents can load into context directly, unlike RAG which retrieves relevant chunks at inference using vector search.
- **Cheap way to stop each team rebuilding same context layer:** If teams shipping agents against internal data, OKF cheap way stop each team rebuilding same context layer.
- **Knowledge as code for agents:** Agents increasingly reading docs whether or not packaged as OKF, whether they scrape docs regularly or connect to MCP docs server. Same structural habits that make bundle useful make docs better for every reader.
- **For harness engineering:** OKF bundle can live in docs/ directory as part of harness knowledge base. AGENTS.md points to OKF bundle. Progress files reference OKF concept IDs.
- **For your refund agent:** Bundle with policies/refunds.md, tables/orders.md, runbooks/approval_flow.md — agent traverses links to assemble sufficient context before refund.

**Practical demands (for docs teams):**

- Structure content around clear concepts. Each page should cover one thing (feature, process, API endpoint). Pages that mix multiple concerns harder for agents to scope harder for humans to maintain.
- Add metadata consistently. OKF reserves fields type, title, description for reason: they make content queryable. Even outside OKF consistent frontmatter or page properties let tools reason about docs rather than just read them.
- Link related topics together. Explicit cross-links are how OKF builds knowledge graph. In any docs system links between related pages reduce chance agent or reader has to guess connections.
- Keep docs under version control. Git-backed history is load-bearing in OKF because keeps paths stable and lets you trust what agent reading. Same true for any team that needs audit changes or roll back bad edit.
- Reduce duplicated info across pages. Duplication enemy of structured knowledge. When same fact lives in three places updates break consistency agents may retrieve contradictory answers.

### 11. How to Build Your Own OKF Bundle — Step by Step

**Step 1: Create bundle directory**

```bash
mkdir -p knowledge-bundle/{metrics,tables,policies,runbooks,apis}
```

**Step 2: Create .okf/index.md with version**

```
---
type: index
okf_version: 0.1
title: My Org Knowledge Bundle
description: Curated knowledge for refund agent and data platform
---

# Knowledge Bundle

## Entry Points
- [Refund Policy](../policies/refunds.md)
- [Orders Table](../tables/orders.md)
- [Metrics](./metrics/)
```

**Step 3: Create concepts — one file per concept with required type**

Each file needs YAML frontmatter with at least type.

**Step 4: Add cross-links via Markdown links**

Inside metric file link to source table and runbook.

**Step 5: Add CI validation**

```bash
# check_links.py
import os, re, pathlib
bundle = pathlib.Path("knowledge-bundle")
for md in bundle.rglob("*.md"):
  links = re.findall(r"\[.*?\]\((.*?\.md)\)", md.read_text())
  for link in links:
    target = (md.parent / link).resolve()
    if not target.exists():
      print(f"BROKEN LINK in {md}: {link} -> {target} missing")
      exit(1)
```

**Step 6: Version and release**

```bash
git add knowledge-bundle
git commit -m "Add OKF bundle v2026.10 — refund policies"
git tag okf-v2026.10
tar -czf knowledge-bundle-v2026.10.tgz knowledge-bundle/
gh release create okf-v2026.10 knowledge-bundle-v2026.10.tgz
```

**Step 7: Consume in agent**

```python
# Python agent loader (pseudo)
import yaml, pathlib

def load_okf_bundle(path, tags_filter=None):
  bundle = pathlib.Path(path)
  concepts = {}
  for md_file in bundle.rglob("*.md"):
    text = md_file.read_text()
    frontmatter = yaml.safe_load(text.split("---")[1])
    if tags_filter and not any(t in frontmatter.get("tags", []) for t in tags_filter):
      continue
    concept_id = str(md_file.relative_to(bundle))[:-3]  # remove .md
    concepts[concept_id] = {"frontmatter": frontmatter, "body": text.split("---")[2]}
  return concepts

# Load only refund-related
refund_context = load_okf_bundle("knowledge-bundle", tags_filter=["refund", "bundle"])
# Agent can now traverse links
```

**Step 8: Ingest into catalog (optional)**

If using Google Cloud Knowledge Catalog or GitBook, ingest bundle so agents can query by type/tags.

### 12. Production Checklist & Governance

**Checklist for OKF bundle ready for production:**

1. **One concept per file:** Each .md covers one thing (metric, table, runbook). No mega-pages mixing multiple concerns.
2. **Required frontmatter:** Every file has type field. Recommended title, description, resource, tags, timestamp.
3. **Consistent types:** Define allowed types for org: metric, table, dataset, runbook, policy, api-endpoint. Document in index.md.
4. **Path = ID stability:** File paths stable under version control. Avoid renaming freely — breaks graph. Use Git-backed versioning.
5. **Cross-links:** Explicit Markdown links between related concepts. Metric → source table, table → runbook, policy → approval flow.
6. **No duplication:** Same fact lives in one place, linked elsewhere. Reduces inconsistency.
7. **Git-reviewable:** Bundle lives in Git, PRs reviewable, diffs readable, git blame for why number changed.
8. **CI gates:** check_links.py fails if any concept link points to missing file. check_frontmatter.py fails if missing required fields. Style guide enforcement.
9. **Versioned releases:** Publish tarball releases for pinned reproducible consumption. Agents pin version: use bundle v2026.06 for this workflow run — prevents retrieval drifting mid-incident.
10. **Freshness signals:** timestamp field respected by search and agents. Stale bundle detection.
11. **Ownership:** resource field anchors concept to system of record. Owner field in body.
12. **Progressive disclosure:** index.md entry points, not everything loaded at once. Agent reads index, scopes to topic, follows links.
13. **Security:** No secrets in bundle. PII masked. Permission-scoped bundles if needed.
14. **Human + AI readable:** Headings map cleanly to concepts, because agent uses structure to scope what it reads. Frontmatter consistent across pages.
15. **Evaluation:** Measure if OKF bundle improves agent accuracy vs RAG alone. Needle-in-haystack test: can agent traverse from metric to source table via link?

**Governance:**

- Who counts as trusted knowledge? Define producers (data platform team, finance team) and review process.
- How updates reviewed? PR + owner approval + CI gates.
- How consumption agents handle unknown types or stale context? Fallback + timestamp check.
- What counts as trusted? Curated, stable, pre-compiled knowledge layer, not raw fragmented docs.

**Future:** OKF v0.2 frontmatter, what spec requires, two ways to check folder. Watch for catalog vendors ingestion support, validators, agent frameworks native loaders, case studies.

---

### Appendix: Google OKR — Since Often Confused with OKF

**What is OKR?**

OKR stands for Objective + Key Results. Simple goal-setting framework used by Google, Intel, thousands fast-growing companies — works for 3-person consultancy as does for 3000-person company. Introduced to Google in 1999 by John Doerr investor and key advisor who learned framework during time at Intel. Since then OKRs become backbone of Google strategic planning ensuring all employees from developers to executives work aligned toward same objectives.

**Structure:**

- **Objective:** Qualitative, ambitious, time-bound, inspiring. What you want to achieve. Example: "Launch OKF adoption across data platform"
- **Key Results:** Quantitative, measurable outcomes, 2-4 per objective, grading 0-1.0. How you'll measure success. Example: KR1: 10 teams ship OKF bundle, KR2: Reduce context-related agent failures 50%, KR3: Publish 50 concepts in bundle

**Two categories Google uses:**

- **Committed OKRs:** Must hit 100%, tied to resources, roadmap. Example: Ship OKF v0.1 spec.
- **Aspirational OKRs (Stretch):** Designed to be more challenging than typical KPIs, encourage innovation, 70% considered success. Example: 100% of agents use OKF bundle.

**Grading:**

0.0-0.3: Failed, 0.4-0.6: Progress but short, 0.7: Success for aspirational, 1.0: Success for committed.

**Why Google uses OKR to encourage innovation:** Setting aspirational goals that are more challenging than typical KPIs. Encourages teams aim higher than comfortable.

**Example Google-style OKRs for OKF project:**

```
Company Objective: Organize world's information make universally accessible useful

Team Objective: Make agent context portable and Git-reviewable
KR1: Publish OKF v0.1 spec Apache-2.0 with <10 fields
KR2: Reference tooling in knowledge-catalog repo
KR3: 3 third-party projects (Kiso, OKF4net, GitBook) integrate OKF
KR4: 10 case studies showing OKF improves retrieval quality

Individual Objective: Ship OKF bundle for refund agent
KR1: Create 20 concepts (metrics, tables, policies, runbooks) with cross-links
KR2: CI gates for link validation and frontmatter
KR3: Agent accuracy +25% vs RAG alone
```

**Book:** Measure What Matters by John Doerr — most famous OKR book.

---

**Bottom Line:** Google OKF Open Knowledge Format v0.1 launched June 12, 2026 by Google Cloud Data Cloud team Apache-2.0 vendor-neutral directory of Markdown files with YAML frontmatter each file one Concept file path is Concept ID Markdown links knowledge graph. Solves context sprawl most important knowledge metadata context curated knowledge scattered across wikis tickets dashboards people's heads. People compensate with experience know which wiki more correct who to ask which dashboard legacy. Agents don't have intuition when context missing or split across systems agent has to infer guess leads to confident wrong answers brittle automations. Without context two teams can query same table still disagree what revenue means. Before OKF developer debugging revenue discrepancy might find SQL in dashboard definition in wiki page deprecation note buried in ticket repeat same archaeology next week. OKF positioned as portable corpus that tools and agents can consume not as another portal. Simplest understanding OKF file-based packaging standard for curated knowledge small enough to live in git structured enough to index neutral enough to move across tools. OKF in one sentence directory of Markdown + YAML frontmatter per announcement and specification vendor-neutral way to package curated organizational knowledge as directory of Markdown files each file includes YAML frontmatter for structured metadata it's just files No required SDK runtime schema registry central service. Markdown plus YAML deliberate trade humans can review in PRs diffs readable tools can parse frontmatter to index retrieve. Example frontmatter type metric title Revenue Net description Net revenue excluding refunds chargebacks resource bigquery://analytics.metrics/revenue_net tags finance gaap timestamp 2026-06-12T00:00:00Z body metric notes caveats links. What OKF is not not replacement for Avro Protobuf OpenAPI dbt models instead acts as curation metadata wrapper points at sources truth adds context they don't capture well like usage guidance operational notes reduces schema duplication avoids two sources truth. Not same as Knowledge Graph / schema.org markup OKF for internal file-based knowledge bundles meant to be shared used by tools agents Knowledge Graph hosted service returns entity results as JSON-LD using schema.org types OKF lives in repos filesystems Knowledge Graph online entity search API. Building blocks filesystem-native mental model Knowledge Bundle distributable directory tree Each Concept exactly one Markdown document Concept ID derived from file path minus .md Path-based IDs stay stable under version control easy for tools reference concepts without inventing separate identifier scheme Example knowledge-bundle datasets/ga4_ecommerce.md conceptId datasets/ga4_ecommerce tables/ga4/events.md conceptId tables/ga4/events metrics/revenue_net.md conceptId metrics/revenue_net runbooks/revenue_discrepancy.md conceptId runbooks/revenue_discrepancy. YAML frontmatter as queryable surface area keeps structure small Google highlights compact set frontmatter fields type title description resource tags timestamp tools can index for filtering routing spec defines normative rules This makes retrieve all runbooks tagged incident-response metadata query instead of full-text guessing game Only type required producer decides what types exist. Markdown body as human-first agent-usable narrative layer uses plain Markdown readable in GitHub internal doc sites easy for agents chunk quote follow links Links express relationships beyond folders Example metric can point to source table and runbook for incidents. index.md log.md conventions Knowledge Bundle distributable directory tree Each Concept exactly one Markdown document Concept ID derived from file path minus .md File path is concept identity Link resolution just path resolution agent traverses deliberately rather than guessing No SDK no runtime proprietary schema. Adoption patterns concept-per-file bundles organized by domain spec concept-per-file rule easiest when organize by domain folders Express relationships as links rather than mega-pages Simple starting tree keeps concepts small enough reuse Example knowledge-bundle metrics/revenue_net.md tables/orders.md policies/refunds.md runbooks/revenue_discrepancy.md Inside metrics/revenue_net.md keep YAML frontmatter queryable Use Markdown links to connect graph Derived from Orders table Refund handling Refund policy. Distribute OKF as artifact repo release filesystem Because bundles are just files distribution packaging decision Use git repo for collaboration review Publish tarball releases for pinned reproducible consumption Optionally sync to shared mount for runtime access For agents pin explicitly use bundle v2026.06 for this workflow run Prevents retrieval drifting mid-incident tar -czf knowledge-bundle.tgz knowledge-bundle/ attach to release. Pair OKF with catalog ingestion Google Cloud Knowledge Catalog example Google says Knowledge Catalog can ingest OKF serve it to agents Split useful OKF stays interchange layer Catalogs become optional UX indexing layers not only home for context. Tooling Official Google Cloud Blog announcement June 12 2026 GitHub SPEC.md v0.1 fits single page minimal Reference tooling in knowledge-catalog repository Google Cloud Knowledge Catalog can ingest OKF Third-party Kiso shows how OKF bundles can become static websites llms.txt outputs OKF4net 0.6.0 .NET implementation of OKF v0.2 core library okf CLI auditing what AI agent knows zero-dependency .NET google-okf PyPI Python package Open Knowledge Format OKF v0.1 open vendor-neutral standard introduced by Google Cloud to formalize LLM Wiki pattern Instead of feeding raw fragmented inconsistent documentation or database formats directly into vector databases OKF structures knowledge into unified version-controlled Git-friendly directory tree GitBook Blog explains OKF GitBook pages carry structured headings metadata so frontmatter fields OKF reserves have natural home Git Sync keeps docs in version-controlled repository gives file-and-history backbone OKF expects Also exposes machine-readable output so agent can read same content readers see Gives docs dual life maintain one set of docs that publishes clean site for people and serves organized linked knowledge to agents reasoning over it Validators community scripts check_links.py check_frontmatter.py. Why matters for developers interoperability without glue code format not service Bundles just files so producers consumers only need filesystem access plus Markdown/YAML parser Keep bundle in git publish pinned tarball for reproducible runs or mount into environment where tools agents can read it Concrete payoff cross-stack reuse data platform team can publish bundle once then Python agent pipeline TypeScript IDE helper catalog ingestion job can all consume same directory tree Knowledge as code practices applied to context Because OKF diffable text fits normal engineering discipline Metric definitions runbooks can be updated via PRs reviewed by owners rolled back when needed Turns why did this number change into git blame instead of Slack archaeology Spec version-control friendliness enabling detail Better agent grounding fewer hallucinations more reliable automation Google frames OKF as way to ground agents with right context Includes definitions caveats deprecations operational procedures Stable concept IDs plus queryable frontmatter let retrieval start narrow by type tags Tools can then traverse links to assemble full story for task. For content creators OKF as standardized portable LLM-wiki pattern Turns LLM-wiki idea into something teams can adopt without committing to one wiki product Write human-readable Markdown add small amount structured metadata ship result as bundle of files Portability unlock docs team can curate product-concepts bundle for feature behavior deprecations data team can curate analytics-concepts bundle for metrics tables runbooks Can publish both internally open-source subset or share across org boundaries Metadata that makes content discoverable reusable Tags let slice content by audience or lifecycle deprecated oncall exec resource anchors concept to system of record timestamp provides freshness signal search agents can respect Over time editors can standardize templates per type so readers recognize shape quickly. For Agentic AI curriculum context Solves context engineering problem OKF is curated stable pre-compiled knowledge layer that agents can load into context directly unlike RAG which retrieves relevant chunks at inference using vector search Cheap way to stop each team rebuilding same context layer If teams shipping agents against internal data OKF cheap way stop each team rebuilding same context layer Knowledge as code for agents Agents increasingly reading docs whether or not packaged as OKF whether they scrape docs regularly or connect to MCP docs server Same structural habits that make bundle useful make docs better for every reader For harness engineering OKF bundle can live in docs/ directory as part of harness knowledge base AGENTS.md points to OKF bundle Progress files reference OKF concept IDs For refund agent Bundle with policies/refunds.md tables/orders.md runbooks/approval_flow.md agent traverses links to assemble sufficient context before refund. How to build Step1 Create bundle directory mkdir -p knowledge-bundle/{metrics,tables,policies,runbooks,apis} Step2 Create .okf/index.md with version type index okf_version 0.1 title My Org Knowledge Bundle Step3 Create concepts one file per concept with required type Step4 Add cross-links via Markdown links Step5 Add CI validation check_links.py links regex MD files Step6 Version and release git add commit tag tar czf knowledge-bundle.tgz gh release create Step7 Consume in agent Python loader yaml pathlib load_okf_bundle path tags_filter concepts dict concept_id relative path Step8 Ingest into catalog optional If using Google Cloud Knowledge Catalog or GitBook ingest bundle so agents can query by type tags. Production checklist One concept per file Each .md covers one thing metric table runbook No mega-pages Required frontmatter Every file has type Recommended title description resource tags timestamp Consistent types Define allowed types for org metric table dataset runbook policy api-endpoint Document in index.md Path = ID stability File paths stable under version control Avoid renaming freely breaks graph Git-backed versioning Cross-links Explicit Markdown links between related concepts Metric → source table table → runbook policy → approval flow No duplication Same fact lives one place linked elsewhere Reduces inconsistency Git-reviewable Bundle lives in Git PRs reviewable diffs readable git blame for why number changed CI gates check_links.py fails if any concept link points to missing file check_frontmatter.py fails if missing required fields Style guide enforcement Versioned releases Publish tarball releases for pinned reproducible consumption Agents pin version use bundle v2026.06 for workflow run Prevents retrieval drifting mid-incident Freshness signals timestamp field respected by search agents Stale bundle detection Ownership resource field anchors concept to system of record Owner field in body Progressive disclosure index.md entry points not everything loaded at once Agent reads index scopes to topic follows links Security No secrets in bundle PII masked Permission-scoped bundles if needed Human + AI readable Headings map cleanly to concepts because agent uses structure to scope what it reads Frontmatter consistent across pages Evaluation Measure if OKF bundle improves agent accuracy vs RAG alone Needle-in-haystack test can agent traverse from metric to source table via link Governance Who counts as trusted knowledge Define producers data platform team finance team review process How updates reviewed PR + owner approval + CI gates How consumption agents handle unknown types or stale context Fallback + timestamp check What counts as trusted Curated stable pre-compiled knowledge layer not raw fragmented docs Future OKF v0.2 frontmatter what spec requires two ways to check folder Watch for catalog vendors ingestion support validators agent frameworks native loaders case studies. Bottom line OKF solves context sprawl curated portable Git-reviewable bundle human and AI readable path = ID links = graph format not service vendor-neutral Apache-2.0 June 12 2026 Google Cloud minimal spec type required rest producer-defined vs RAG traversal vs similarity vs Catalogs vs Knowledge Graph vs OKR goal framework 1999 John Doerr Objectives Key Results committed vs aspirational grading 0.0-1.0.

