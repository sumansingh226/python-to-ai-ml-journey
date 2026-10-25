Google OKF — Open Knowledge Format: Complete Detailed Guide


What It Is, Why Google Launched It June 2026, Spec, RAG vs OKF, Production Patterns
Core Thesis: Google OKF = Open Knowledge Format, launched by Google Cloud Data Cloud team on June 12, 2026, v0.1 Apache-2.0, vendor-neutral. Definition: A directory of Markdown files with YAML frontmatter, each file = one Concept, file path = Concept ID, Markdown links = knowledge graph. Solves "context sprawl" — most important knowledge (metric definitions, caveats, ownership, join guidance, runbooks) scattered across wikis, tickets, dashboards, people's heads. Agents can't infer like humans. OKF turns scattered context into portable, versionable, Git-reviewable bundle that both humans and AI agents can consume reliably. Quote Google: "What's missing is a format, not another service." Builds on Andrej Karpathy's LLM Wiki gist + AGENTS.md pattern. Not replacement for Avro/Protobuf/OpenAPI/dbt — it's curation/metadata wrapper that points at sources of truth and adds context they don't capture. File-based packaging standard for curated knowledge, small enough to live in git, structured enough to index, neutral enough to move across tools.

