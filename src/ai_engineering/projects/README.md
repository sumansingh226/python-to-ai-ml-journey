# Projects

Hands-on builds that apply the concepts from the notes in `src/ai_engineering/`. Each project is self-contained with its own README, dependencies, `.gitignore` and `.env.example`.

| Project | What it builds | Stack | Related notes |
|---|---|---|---|
| [support_agent_graphrag](support_agent_graphrag/) | Customer support agent using vector RAG and GraphRAG, routed by a state machine | LangChain, LangGraph, Chroma, Neo4j | `../rag/`, `../knowledge_graphs/`, `../agent_architecture/` |

## Conventions

- One folder per project, named in `snake_case`.
- Each project has its own `README.md` with goal, success criteria, phases and setup.
- Secrets live in a local `.env`, never committed. Commit only `.env.example`.
- Data and generated indexes are git-ignored; keep folders with `.gitkeep`.
- Each phase ends with a measurable result recorded in the project's `docs/`.
