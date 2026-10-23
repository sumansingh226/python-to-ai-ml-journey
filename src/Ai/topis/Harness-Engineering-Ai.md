# Agentic AI — What is Harness Engineering? Complete Detailed Guide
## From Prompt Engineering to Harness Engineering — Agent = Model + Harness

> **Core Thesis:** Prompt engineering shapes what agent *tries*, Context engineering shapes what agent *knows*, Harness engineering shapes what agent *can and cannot do*. Term popularized by Mitchell Hashimoto creator of Terraform and Ghostty early 2026 and Addy Osmani Google engineering leader May 2026: "Every time an agent makes a mistake, you don't just tell it to do better next time. You change the system so that specific mistake becomes structurally harder to repeat." Agent = Model + Harness. If you are not the model, you are the harness. Decent model with great harness beats great model with bad harness. LangChain raised accuracy 52.8% to 66.5% by changing only harness same model. OpenAI Codex team shipped 1M lines production code in 5 months with 3 engineers using harness engineering. Production: Harness is body, nervous system, safety rails around brain (model).

### Table of Contents
1. What is Harness? Agent = Model + Harness
2. Why Harness? Prompt and Context Engineering Broke Down
3. The Two Fundamental Ways AI Agents Fail
4. The Seven Pillars of Harness Engineering
5. Planner-Generator-Evaluator Architecture (Inspired by GANs)
6. Three Operational Layers — Context, Constraints, Feedback Loops
7. Real-World Proof — OpenAI 1M Lines, LangChain 52.8%→66.5%, 51-Agent System
8. Agent Harness vs Platform Harness
9. Harness Engineer Role — What Does Engineer Actually Do?
10. The Ratchet Principle — Every Mistake Becomes Rule
11. How to Build Your Own Harness — Practical Steps
12. Harness-as-a-Service — Industry Shift
13. Production Checklist

---

### 1. What is Harness? Agent = Model + Harness

**Definition:**

Harness engineering is the discipline of designing and maintaining everything wrapped around an AI model that turns it from a text generator into a working agent. Core equation:

**Agent = Model + Harness. If you are not the model, you are the harness.**

A raw model is not an agent. It only becomes one when a harness provides it with state, tool execution, feedback loops, memory, and enforceable constraints. Harness includes system prompts, tool definitions, context management policies, sandboxed execution environments, subagent orchestration, hooks for deterministic checks, and observability layers that track every decision agent makes.

**What harness actually is — software layer around AI that defines not only what should be done but also how task itself should be executed. Harness defines agent's behavior: which stages it should go through, which tools it should use, what needs to be checked after execution, when it should go back, what counts as error, and at what point it can actually say work is finished.**

**Critical insight:** Model is merely one input into running agent. Rest is scaffolding. Most interesting engineering work is not selecting model but designing scaffolding.

**Analogy:** Harness evokes saddle or safety belt — something that lets you safely channel powerful but uncontrollable force. Model provides intelligence, harness is body, nervous system, safety rails.

**Two uses of word harness:**

1. **AI Agent Harness:** Software around AI model that lets it read files, run tools, act — Jediah Katz longtime agent-harness engineer at Cursor and now SpaceX definition: harness is software around AI model that lets it read files run tools act
2. **Test Harness:** Bench that runs program to test it — model benchmarks kept meaning evaluation harness runs model on tasks scores result

**For businesses evaluating AI:** Question is not "which model does this use?" It is "what harness wraps around it?" Platforms like Claude Code, Cursor, Codex, Aider, Cline behave differently despite often using same underlying models. They are all harnesses. Model might be identical but behavior dominated by harness.

### 2. Why Harness? Prompt and Context Engineering Broke Down

**Three eras:**

**Prompt Engineering (2022-2024):** Emerged when models used for single-turn tasks. You wrote prompt, got response, evaluated it. Whole interaction lived in one exchange. Got very good at improving that exchange.

**Context Engineering (2024-2025):** Emerged as tasks got more complex multi-turn. Content of what you sent model started mattering as much as how you phrased it — retrieved documents, memory, session history, structured state. Context engineering addressed what model knows at inference time.

**Harness Engineering (2025-2026):** Needed when agents started running autonomously for hours writing real code making real decisions chaining dozens tool calls across multiple sessions.

**Why prompt and context broke down:**

Both broke down moment agents started running autonomously for hours writing real code making real decisions chaining dozens tool calls across multiple sessions. Reason simple: neither prompt engineering nor context engineering has any mechanism to stop agent from doing something. Well-crafted prompt can influence what agent tries to do. It cannot prevent agent from rewriting entire codebase if nothing architecturally stopping it. Retrieved context can give agent accurate information. It cannot catch verification failure or break doom loop. Those are structural problems need structural solutions. That is what harness engineering is for.

**Summary:**

- Prompt engineering shapes what agent *tries*
- Context engineering shapes what agent *knows*
- Harness engineering shapes what agent *can and cannot do*

**What happens without harness:**

Picture agent tasked fixing single bug. Without harness no architectural constraints telling it what it can cannot touch. No verification gate checking whether fix actually works before declares success. No loop detection to stop it from trying same broken approach twelve times in row. No progress file so when session ends starts from scratch next time. Agent edits files across codebase marks task complete because believes succeeded and two days later fix surfaces in production as different bug entirely. This is not model capability problem model was capable enough to attempt task. It is harness problem and exactly kind failure became unavoidable as agents moved from controlled demos into real engineering workflows.

### 3. The Two Fundamental Ways AI Agents Fail

Anthropic formalized two root causes: **Context Instability** and **Self-Evaluation Bias**

**1. Context Instability:**

Tendency of AI to lose track of earlier work as session grows. Anyone who's used ChatGPT or Claude in long threads seen this: You remind it "We already discussed that earlier" and behaves like first time heard it.

For small Q&A tasks annoying. For multi-step codebases or documents requiring dozens incremental edits catastrophic. Forgotten constraints and earlier decisions pile up into subtle inconsistencies regressions until final artifact internally broken.

**2. Self-Evaluation Bias:**

Even more dangerous. Appears when same model that created work also asked to judge it. Anthropic engineer put bluntly: "I watched it identify legitimate issue then talk itself into deciding they weren't big deal and approved work anyway."

Mirrors human psychology — most people overestimate quality of own writing or code during self-review. But LLMs optimized to make things sound okay so exceptionally good at rationalizing away problems they created.

Seen in automated test generation: model writes code and tests then confidently declares everything passes even when obvious edge cases missing. Harness engineering breaks this loop by forcing different agents to plan produce evaluate separately.

### 4. The Seven Pillars of Harness Engineering

Every production-ready agent harness needs seven components. Each has distinct job. If cannot name specific behavior component exists to deliver should be removed.

**1. System Prompts and Rule Files:**

Flat markdown file at root project like AGENTS.md or CLAUDE.md still highest-leverage configuration point any agent setup. Must be treated like pilot's checklist not style guide. Keep short. Ensure every rule earned through past failure.

Best system prompts do not describe what agent should do in general terms. They encode specific constraints born from specific mistakes. "Never comment out tests. Delete or fix them." "Always run test suite before committing." "Never use em dashes in client emails." Each rule exists because agent once violated it.

**2. Tools and Skills:**

Tools how agent interacts with world. Harness defines which tools exist what they do how agent discovers them. Ten highly focused tools always outperform fifty overlapping ones.

This is where security risks enter. Tool descriptions populate agent's prompt. Malicious or sloppy external integrations such as unverified MCP servers can inject bad instructions into agent before even starts working. Every tool in harness should be audited purposeful.

**3. Filesystem and Version Control:**

Filesystem foundational. Models can only operate on what fits in context window. Filesystem provides workspace to read data place to offload intermediate work and surface for multiple agents to coordinate.

Adding Git provides free versioning. Agent can track progress branch experiments rollback errors. For any business deploying agents that modify code documents configurations Git-backed filesystems non-negotiable.

**4. Sandboxes and Safe Execution:**

Bash access gives agents general-purpose problem-solving ability but only if runs safely. Sandboxes provide isolated environments where agents can run code inspect files verify work without risking host machine.

Good sandbox ships with strong defaults: pre-installed language runtimes test CLIs headless browsers. Allows agent to observe own work close self-verification loop. For businesses handling client data sandboxes prevent agents from accidentally modifying production systems.

**5. Memory and Continual Learning:**

Models have no knowledge beyond training weights and current context. Harnesses bridge gap using memory files that inject knowledge into every session. Files accumulate over time encoding domain expertise project conventions lessons learned.

For real-time information like new library versions live data current events web search and API tools baked directly into harness. Combination persistent memory and live retrieval makes agent more capable with every session.

**6. Context Management and Compaction:**

Models degrade reasoning as context windows fill up. Harnesses manage scarcity using three primary techniques:

- **Compaction:** Intelligently summarizing offloading older context to prevent errors while preserving key information
- **Tool-call offloading:** Storing massive tool outputs like 2000-line logs in filesystem while keeping only essential headers footers in context
- **Progressive disclosure:** Revealing instructions and tools only when task explicitly requires them rather than loading everything at startup

Without context management agents working long tasks eventually degrade quality or crash entirely. Most technically challenging aspects harness engineering and one most teams overlook.

**7. Hooks and Enforcement Layers:**

Hooks bridge gap between requesting action and enforcing it. They run at specific lifecycle points: before tool call after file edit or before commit. Hooks block destructive commands enforce auto-formatting to save tokens run test suites.

Rule: success is silent failures verbose. If typecheck passes agent hears nothing. If fails error injected directly back into loop for self-correction.

Hooks what turn helpful assistant into reliable system. Enforcement layer ensures agent cannot violate rules even when model wants to.

### 5. Planner-Generator-Evaluator Architecture (Inspired by GANs)

Three-stage multi-agent pattern inspired by GANs (Generative Adversarial Networks). In GANs Generator creates candidates while Discriminator evaluates them two networks improve by competing. Harness applies same separation to AI agents then adds Planner upfront.

At high level:

1. **Planner** turns vague requests into detailed specs
2. **Generator** implements those specs step-by-step
3. **Evaluator** tests implementation against strict criteria

**What Planner Does:**

Converts short fuzzy human requests into precise structured plans specifications.

Input: "Build login feature"
Output: spec containing requirements edge cases security constraints non-functional expectations

Behaves like product manager plus systems designer combined. Forcing separate spec-generation step surfaces hidden assumptions before any code written. Single change cut rework dramatically disagreements about scope came up before implementation not after.

**What Generator Does:**

Implementation agent receives Planner's spec turns into working artifacts using **sprint contracts** — small bounded units work with clear acceptance criteria. Think agile sprints but finer granularity:

- Sprint 1: Implement backend API for login
- Sprint 2: Implement frontend form validation
- Sprint 3: Integrate error handling security checks

Chunking work this way prevents Generator from trying swallow whole app at once exactly where solo agents tend hallucinate or quietly drop requirements.

**What Evaluator Does:**

Separate agent responsible running tests inspecting results scoring quality. Critically can't be same agent or same role as Generator.

In Anthropic implementation:
- Evaluator uses Playwright MCP browser automation tool to run real UI tests
- Applies explicit scoring criteria including aesthetic bar labeled "museum quality"
- If tests or criteria fail sends structured feedback back to Generator

Creates feedback loop: Generator produces version → Evaluator tests scores → if below threshold Evaluator returns actionable feedback → Generator revises → cycle repeats until approval.

Detail: simply adding phrase "museum quality" into Evaluator's rubric measurably improved visual design polish outputs. Single well-chosen constraint word can steer entire system's standards in ways hard to predict.

**Why separate planning, making, checking:**

Fixes two failures: context instability and self-evaluation bias. Planner keeps spec stable, Generator implements spec, Evaluator cannot be same as Generator so no self-evaluation bias.

### 6. Three Operational Layers — Context, Constraints, Feedback Loops

In harness engineering components cluster into three operational layers. Each layer addresses different category failure appears when agents run real-world environments.

**Layer 1: Context Engineering — Giving Agent What Needs to Know:**

Agents can only work with what is in context window. Anything stored Slack thread Google Doc or someone's memory effectively invisible.

Context layer ensures right information available at right moment. In practice means maintaining structured knowledge base inside repository itself writing progress files and session handoff documents so agents can resume work across context windows and loading relevant documentation dynamically based current task rather than flooding context upfront.

Anthropic documented problem: Each new session began with no memory prior work. Solution structured progress logs feature tracking files in JSON rather than Markdown agents less likely overwrite structured data and init script so fresh agent could orient itself instantly.

**Layer 2: Architectural Constraints — Preventing Wrong Moves:**

If context layer about what agent knows constraint layer about what agent allowed to do.

Production agents need hard boundaries. Without them agent tasked refactoring module might rewrite entire codebase. OpenAI engineering team described enforcing strict layered architecture where each domain had rigid dependency rules so code could only import from adjacent layers. Not documentation guidance enforced by custom linters and structural tests that ran every pull request and no agent could bypass them.

Key insight: Constraints do not limit what agent can accomplish. They focus it. Well-constrained agent produces better output precisely because cannot wander into territory that creates downstream problems.

**Layer 3: Feedback Loops and Verification — Catching What Goes Wrong:**

Even well-constrained agent with good context makes mistakes. Third layer system that catches and corrects those mistakes before they compound.

Includes self-verification prompts that instruct agent to run tests check own output before marking task complete garbage collection agents that periodically scan for documentation drift and broken architectural patterns and loop detection middleware that tracks how many times agent edits same file. After threshold crossed injects prompt nudging agent reconsider approach breaking doom loops where agents make small variations on broken solution ten or more times in row.

LangChain engineering team demonstrated impact directly. By improving harness without changing underlying model at all their coding agent jumped from 52.8% to 66.5% on Terminal Bench 2.0 moving from 30th to 5th place overall.

### 7. Real-World Proof — OpenAI 1M Lines, LangChain 52.8%→66.5%, 51-Agent System

**OpenAI Codex Team — 1M Lines Production Code in 5 Months:**

Clearest evidence for harness engineering impact comes from OpenAI Codex team who published findings February 2026 after building entire production product without single human-written line code.

Constraint radical: no human engineer would write single line production code. Everything had to be generated by Codex agents. Not productivity experiment forcing function if agents could not do work product did not get built.

Five months later repository contained roughly one million lines code across application logic infrastructure documentation tooling. Team three engineers later seven merged approximately 1500 pull requests averaging 3.5 PRs per engineer per day.

Engineers job not coding was designing harness:

- Structured docs/ directory versioned indexed served as agent's single source truth
- Short AGENTS.md file acted as table contents pointing agents to right documentation for any task
- Custom linters enforced architectural rules that no agent could violate even by accident
- Periodic garbage-collection agents scanned for documentation drift constraint violations
- Agents had access observability data browser navigation so they could debug failures themselves

Lesson same one LangChain confirmed with benchmark results: underlying model matters less than system built around it. Model provides intelligence but surrounding architecture determines whether intelligence usable consistently.

**LangChain — 52.8% to 66.5% Without Changing Model:**

By improving harness without changing underlying model at all their coding agent jumped from 52.8% to 66.5% on Terminal Bench 2.0 moving from 30th to 5th place overall. Same model wildly different outcomes harness difference.

**51-Agent Harness System — Real Business Operations:**

Real-world deployment where dozens specialized AI agents cooperate under shared rules hooks pipelines. Built independently before Anthropic public Harness blog converged on nearly same architecture anyway.

System currently includes:
- 51 agents specialized by department role
- 85 skills discrete capabilities each agent can invoke
- 21 security hooks blocking actions around data tools
- 90 rules governing behavior routing

Agents grouped similarly to enterprise org chart: development code review QA business strategy marketing creative research operations investment legal finance HR.

**Solo Agent vs Harness Cost/Quality:**

Building test app "Retro 4G"

| Approach | Model | Time | Cost | Result Quality |
|---|---|---|---|---|
| Solo Agent | Claude single agent | Not specified | $9 | Core functionality broken code not usable in practice |
| Harness v1 | Claude Sonnet 4.5 | 6 hours | $200 | 16 features delivered across 10 sprints test app fully working |
| Harness v2 | Claude Opus 4.6 | ~4 hours | $120 | ~70% complete app in 3 dev + 3 QA cycles service-level quality |

$9 solo agent run produced something that looked complete app core functionality broken. Anyone tried vibe coding with LLMs will recognize pattern large impressive-looking files that fail basic smoke tests. Harness variants cost 20x+ more API spend but shipped working software created reliable test coverage QA history and did so under observable repeatable sprints.

Another finding: as underlying models improved Harness scaffolding could be simplified. When Claude Sonnet 4.5 arrived explicit context-reset mechanisms became unnecessary. With Opus 4.6 even sprint structure could relax because model could self-chunk work more intelligently.

Harness is not fixed heavy framework living system that should get lighter as models get smarter.

### 8. Agent Harness vs Platform Harness

Term harness split into two distinct concepts 2026:

**Agent Harness:**

Everything around LLM that turns raw intelligence into reliable autonomous coding agent: planning loops memory systems tool orchestration verification error recovery execution runtime guardrails. Agent = Model + Harness model provides brain harness is body nervous system safety rails.

Includes: knowledge base, architectural constraints, tools integrations, verification gates, state management, feedback loops.

**Platform Harness:**

Environment that allows AI agents to contribute to software delivery safely effectively. Builds on same foundations we already care about in platform engineering: CI/CD test infrastructure observability security deployment safety developer experience.

Harness engineering is agent-friendly layer of platform engineering for human-agent teams. Discipline designing environment that allows AI agents to contribute to software delivery safely effectively.

**Both needed:**

At core any AI system sits LLM. To make outputs actionable need agent harness. But to make agent operate safely effectively within specific constraints company's Software Development Life Cycle SDLC requires platform harness.

Example:
- Agent harness: Claude Code's loop tools context management hooks sandboxes that turn Claude model into coding agent
- Platform harness: Harness.io platform CI/CD pipelines RBAC audit controls deployment safety that lets Claude Code agent operate safely within company's SDLC

Salesforce unveiled Enterprise AI Harness at Dreamforce described new products as parts of it. OpenAI Agents API presents itself as managed harness that handles difficult machinery around agent. Google shipped new managed-agent harness for Gemini platform.

### 9. Harness Engineer Role — What Does Engineer Actually Do?

As of early 2026 more likely find listed as "AI infrastructure engineer" "agent platform engineer" or "AI systems engineer" Work though becoming well-defined.

**Core responsibilities:**

1. **Designing knowledge base:** Ensuring all documentation architecture decisions operational context live in repository where agent can access them not in Slack or someone's head. Structured docs/ directory versioned indexed single source truth, AGENTS.md table contents.

2. **Building and maintaining tooling:** Creating CLI tools MCP servers integrations that give agents same capabilities human engineers rely on. Rise of agentic AI communication protocols like MCP and A2A made substantially more approachable in 2026. Ten highly focused tools outperform fifty overlapping.

3. **Enforcing architectural constraints:** Writing custom linters structural tests that make it mechanically impossible for agents to violate design rules. Strict layered architecture each domain rigid dependency rules code can only import adjacent layers enforced by custom linters structural tests that run every pull request no agent can bypass.

4. **Building verification systems:** Constructing feedback loops test runners self-check prompts that catch agent errors before they compound. Self-verification prompts instruct agent run tests check own output before marking task complete, garbage collection agents periodically scan for documentation drift broken patterns, loop detection middleware tracks how many times agent edits same file after threshold injects prompt nudging agent reconsider breaking doom loops.

5. **Running improvement loops:** Analyzing agent traces to find recurring failure modes then fixing harness so failures do not repeat. Every line in good system prompt should trace back to specific historical failure.

Distinct from simply building LLM-powered agents. Harness is what keeps agents working consistently after demo is over and across kind long-horizon tasks that separate proof-of-concept from production. LangChain deep-dive on anatomy of agent harness and academic framing in Pan et al work on natural-language agent harnesses both arrive same conclusion: harness is primary unit engineering work in agent-first world not model.

**What remains is infrastructure trust security efficiency including scoped permissions guardrails against catastrophic actions or $10,000 API fee. Harness is software around AI model that lets it read files run tools act. What lasts in view is part model cannot be trained to do: limit what agent may touch and spend.**

### 10. The Ratchet Principle — Every Mistake Becomes Rule

Most vital habit harness engineering treating agent mistakes as permanent signals not one-off flukes to retry forget.

If agent ships pull request with commented-out test that gets merged by accident that is signal. Next iteration rule file must state: "Never comment out tests. Delete or fix them." Next pre-commit hook should automatically flag skipped tests in diff. Reviewer subagent must be updated to block commented-out tests.

Every line in good system prompt should trace back to specific historical failure.

Constraints should only be added when observe real failure and removed only when capable model renders them redundant. Because of this harness engineering is discipline rather than one-size-fits-all framework. Right harness for organisation entirely shaped by its unique failure history.

This is ratchet principle: harness only tightens never loosens unless model upgrade makes constraint unnecessary. Over time creates system that becomes more reliable with every mistake it makes.

**Working backwards from desired behavior:**

Most effective way design harness start with desired behavior build component that delivers it.

Examples:

- **Behavior you want:** Agent never ships broken code
  **Harness component:** Pre-commit hook runs full test suite blocks commits on failure

- **Behavior you want:** Agent follows project-specific conventions
  **Harness component:** AGENTS.md file at project root encoding every convention learned from past failures

- **Behavior you want:** Agent completes long tasks without stopping early
  **Harness component:** Loop interceptor catches agent attempt to exit forces continuation against completion goal

- **Behavior you want:** Agent does not grade own work positively
  **Harness component:** Separate generation and evaluation into distinct agents preventing inherent bias models have when reviewing own output

- **Behavior you want:** Agent handles multi-step work predictably
  **Harness component:** Planning phase forces decomposition into step-by-step plan file with self-verification hooks after each step

Every piece harness must have distinct job. If cannot name specific behavior component exists to deliver remove it.

### 11. How to Build Your Own Harness — Practical Steps

**Step 1: Pick your harness framework:**

Do not build orchestration from scratch. Use existing harness Claude Code, Cursor, OpenClaw, Codex that provides loop tools context management hooks sandboxes out of box.

**Step 2: Write first rule file:**

Create AGENTS.md or equivalent at root project. Start 5-10 rules each tracing back to real mistake team or agent made. Keep short pilot checklist not style guide.

Example AGENTS.md:

```
# AGENTS.md - Table of Contents for Agents

## Project Overview
This is refund policy service...

## Rules (each from real failure)
1. Never comment out tests. Delete or fix them. (Failed PR #123 commented test merged)
2. Always run test suite before committing (Agent shipped broken code Jan 2026)
3. Never touch files outside src/refund/* without approval (Agent rewrote entire codebase Feb 2026)
4. Always check policy version v2.3 before generating refund logic (Agent used stale v1.0)
5. Bundle promotion refunds need approval per policy page 25 - never auto-refund bundles

## Where to Find What
- Refund policies: docs/policies/
- Architecture: docs/architecture.md
- API contracts: docs/api/
- Tests: tests/
```

**Step 3: Add one hook:**

Pick most common failure mode workflow add single hook that prevents it. Pre-commit typecheck lint rule test runner. One hook one failure mode.

Example pre-commit hook:

```python
# .git/hooks/pre-commit
#!/bin/bash
# Block commented-out tests
if git diff --cached | grep -E "^\+\s*//\s*test|^\+\s*/\*.*test"; then
  echo "ERROR: Commented-out tests detected. Delete or fix them per AGENTS.md rule 1"
  exit 1
fi

# Run tests
npm test
if [ $? -ne 0 ]; then
  echo "ERROR: Tests failed. Fix before committing."
  exit 1
fi
```

**Step 4: Run agent and observe:**

Every mistake is signal. Each time agent fails ask: Can I add rule hook or tool that makes this failure impossible next time?

**Step 5: Tighten ratchet:**

Over weeks months harness accumulates constraints born from real failures. Agent becomes more reliable not because model improved but because scaffolding around it got tighter.

**Example for growing businesses:**

Construction company using AI to process site reports harness might include:

- Rule file encoding report format conventions mandatory fields
- Hook validates every generated report against schema before submission
- Sandbox isolates report processing from production database
- Memory file accumulating site-specific terminology project codes over time

Allied health practice using AI to draft treatment plans harness might include:

- Rule file encoding clinical documentation standards privacy requirements
- Hook flags any generated text containing patient identifiers for human review
- Context management policy strips sensitive data from long-term memory
- Split architecture where one agent generates separate agent evaluates

Professional services firm using AI agents for client research proposal drafting harness might include:

- Rule file encoding firm's writing style methodology frameworks compliance requirements
- Hook runs every proposal through quality checklist before client delivery
- Subagent orchestration where one agent researches one drafts one reviews
- Memory file accumulates client preferences past feedback over time

**Harnesses do not shrink they move:**

As models improve need for harness does not disappear shifts. Tempting assume better models make scaffolding obsolete. Recent model upgrades drastically reduced need for context-anxiety mitigations for example. But as floor raises so does ceiling. Tasks previously unreachable now in play bringing entirely new failure modes.

Every component in harness encodes assumption about what model cannot do on own. When model improves outdated scaffolding should be removed and new scaffolding must be built to reach next horizon. This is why harness engineering continuous discipline not one-time setup. Best harnesses evolve with every model upgrade every new task attempted.

### 12. Harness-as-a-Service — Industry Shift

Industry shifting from building on LLM APIs which provide completions to building on Harness APIs which provide runtime. SDKs now offer loop tools context management hooks sandboxes right out of box.

Instead building orchestration from scratch modern default select harness framework configure core pillars focus purely on domain-specific prompt and tool design. This is what makes troubleshooting scalable: tuning well-factored configuration surface rather than reinventing entire agent architecture.

If look at top coding agents today they look more like each other than underlying models do. Models differ but harness patterns are...

**Harness Platform Examples:**

- **Harness.io (Company):** AI Software Delivery Platform company enabling engineering teams build test deliver software faster securely. Powered by Harness AI and Software Delivery Knowledge Graph platform brings intelligent automation to every stage software delivery lifecycle after code removing toil freeing developers from manual repetitive work. Purpose-Built AI Agents leverage Harness AI agents or build own AI agents to automate repetitive operational tasks. Generate pipelines using AI fine tune using visual editor apply bulk updates using APIs or MCP. Teams using Harness AI report 85% faster pipeline onboarding 7x faster issue resolution 2 hours saved per project average. Embedded directly in Harness Platform with full RBAC audit controls.

- **Claude Code, Cursor, Codex, Aider, Cline:** All harnesses same models different behavior dominated by harness

- **OpenAI Agents API, Salesforce Enterprise AI Harness, Google Gemini Managed-Agent Harness:** All present themselves as managed harness that handles difficult machinery around agent

**Future:**

Harness Engineering Belongs in Platform Engineering Conversation. Working definition: Harness engineering is agent-friendly layer of platform engineering for human-agent teams. More specifically engineering discipline designing environment that allows AI agents to contribute to software delivery safely effectively. Builds on same foundations we already care about in platform engineering: CI/CD test infrastructure observability security deployment safety developer experience.

As models improve explicit context-reset mechanisms became unnecessary with Sonnet 4.5 even sprint structure could relax with Opus 4.6 because model could self-chunk work more intelligently. Harness not fixed heavy framework living system that should get lighter as models get smarter.

### 13. Production Checklist

1. **What is Harness? Agent = Model + Harness** — Harness engineering discipline designing maintaining everything wrapped around AI model that turns it from text generator into working agent core equation Agent = Model + Harness If you are not model you are harness raw model not agent only becomes one when harness provides state tool execution feedback loops memory enforceable constraints harness includes system prompts tool definitions context management policies sandboxed execution environments subagent orchestration hooks deterministic checks observability layers track every decision agent makes. What harness actually is software layer around AI that defines not only what should be done but also how task itself should be executed harness defines agent behavior which stages it should go through which tools it should use what needs to be checked after execution when it should go back what counts as error and at what point it can actually say work is finished. Critical insight model merely one input into running agent rest scaffolding most interesting engineering work not selecting model but designing scaffolding. Analogy harness evokes saddle safety belt something that lets safely channel powerful but uncontrollable force model provides intelligence harness is body nervous system safety rails. Two uses AI Agent Harness software around AI model that lets it read files run tools act Jediah Katz longtime agent-harness engineer at Cursor now SpaceX harness is software around AI model that lets it read files run tools act Test Harness bench that runs program to test it model benchmarks kept meaning evaluation harness runs model on tasks scores result. For businesses evaluating AI question not which model does this use what harness wraps around it Platforms like Claude Code Cursor Codex Aider Cline behave differently despite often using same underlying models They are all harnesses model might be identical but behavior dominated by harness.

2. **Why Harness? Prompt and Context Engineering Broke Down** — Three eras Prompt Engineering 2022-2024 emerged when models used for single-turn tasks wrote prompt got response evaluated whole interaction lived one exchange got very good improving that exchange Context Engineering 2024-2025 emerged as tasks got more complex multi-turn content of what you sent model started mattering as much as how you phrased it retrieved documents memory session history structured state Context engineering addressed what model knows at inference time Harness Engineering 2025-2026 needed when agents started running autonomously for hours writing real code making real decisions chaining dozens tool calls across multiple sessions. Why prompt and context broke down both broke down moment agents started running autonomously for hours writing real code making real decisions chaining dozens tool calls across multiple sessions Reason simple neither prompt engineering nor context engineering has any mechanism to stop agent from doing something Well-crafted prompt can influence what agent tries to do It cannot prevent agent from rewriting entire codebase if nothing architecturally stopping it Retrieved context can give agent accurate information It cannot catch verification failure or break doom loop Those are structural problems need structural solutions That is what harness engineering is for. Summary Prompt engineering shapes what agent tries Context engineering shapes what agent knows Harness engineering shapes what agent can and cannot do. What happens without harness Picture agent tasked fixing single bug Without harness no architectural constraints telling it what it can cannot touch No verification gate checking whether fix actually works before declares success No loop detection to stop it from trying same broken approach twelve times in row No progress file so when session ends starts from scratch next time Agent edits files across codebase marks task complete because believes succeeded and two days later fix surfaces in production as different bug entirely This is not model capability problem model was capable enough to attempt task It is harness problem exactly kind failure became unavoidable as agents moved from controlled demos into real engineering workflows.

3. **Two Fundamental Ways AI Agents Fail** — Anthropic formalized two root causes Context Instability and Self-Evaluation Bias. Context Instability tendency AI to lose track earlier work as session grows Anyone used ChatGPT or Claude in long threads seen You remind it We already discussed that earlier and behaves like first time heard it For small Q&A tasks annoying For multi-step codebases or documents requiring dozens incremental edits catastrophic Forgotten constraints earlier decisions pile up into subtle inconsistencies regressions until final artifact internally broken. Self-Evaluation Bias even more dangerous appears when same model that created work also asked to judge it Anthropic engineer put bluntly I watched it identify legitimate issue then talk itself into deciding they weren't big deal and approved work anyway Mirrors human psychology most people overestimate quality own writing or code during self-review But LLMs optimized to make things sound okay so exceptionally good at rationalizing away problems they created Seen in automated test generation model writes code and tests then confidently declares everything passes even when obvious edge cases missing Harness engineering breaks this loop by forcing different agents to plan produce evaluate separately.

4. **Seven Pillars of Harness Engineering** — Every production-ready agent harness needs seven components Each has distinct job If cannot name specific behavior component exists to deliver should be removed. 1 System Prompts and Rule Files flat markdown file at root project like AGENTS.md or CLAUDE.md still highest-leverage configuration point any agent setup Must be treated like pilot checklist not style guide Keep short Ensure every rule earned through past failure Best system prompts do not describe what agent should do in general terms They encode specific constraints born from specific mistakes Never comment out tests Delete or fix them Always run test suite before committing Never use em dashes in client emails Each rule exists because agent once violated it. 2 Tools and Skills Tools how agent interacts with world Harness defines which tools exist what they do how agent discovers them Ten highly focused tools always outperform fifty overlapping ones This is where security risks enter Tool descriptions populate agent's prompt Malicious or sloppy external integrations such as unverified MCP servers can inject bad instructions into agent before even starts working Every tool in harness should be audited purposeful. 3 Filesystem and Version Control Filesystem foundational Models can only operate on what fits in context window Filesystem provides workspace to read data place to offload intermediate work and surface for multiple agents to coordinate Adding Git provides free versioning Agent can track progress branch experiments rollback errors For any business deploying agents that modify code documents configurations Git-backed filesystems non-negotiable. 4 Sandboxes and Safe Execution Bash access gives agents general-purpose problem-solving ability but only if runs safely Sandboxes provide isolated environments where agents can run code inspect files verify work without risking host machine Good sandbox ships with strong defaults pre-installed language runtimes test CLIs headless browsers Allows agent to observe own work close self-verification loop For businesses handling client data sandboxes prevent agents from accidentally modifying production systems. 5 Memory and Continual Learning Models have no knowledge beyond training weights and current context Harnesses bridge gap using memory files that inject knowledge into every session Files accumulate over time encoding domain expertise project conventions lessons learned For real-time information like new library versions live data current events web search and API tools baked directly into harness Combination persistent memory and live retrieval makes agent more capable with every session. 6 Context Management and Compaction Models degrade reasoning as context windows fill up Harnesses manage scarcity using three primary techniques Compaction intelligently summarizing offloading older context to prevent errors while preserving key information Tool-call offloading storing massive tool outputs like 2000-line logs in filesystem while keeping only essential headers footers in context Progressive disclosure revealing instructions and tools only when task explicitly requires them rather than loading everything at startup Without context management agents working long tasks eventually degrade quality or crash entirely Most technically challenging aspects harness engineering and one most teams overlook. 7 Hooks and Enforcement Layers Hooks bridge gap between requesting action and enforcing it They run at specific lifecycle points before tool call after file edit or before commit Hooks block destructive commands enforce auto-formatting to save tokens run test suites Rule success is silent failures verbose If typecheck passes agent hears nothing If fails error injected directly back into loop for self-correction Hooks what turn helpful assistant into reliable system Enforcement layer ensures agent cannot violate rules even when model wants to.

5. **Planner-Generator-Evaluator Architecture Inspired by GANs** — Three-stage multi-agent pattern inspired by GANs Generative Adversarial Networks In GANs Generator creates candidates while Discriminator evaluates them two networks improve by competing Harness applies same separation to AI agents then adds Planner upfront At high level 1 Planner turns vague requests into detailed specs 2 Generator implements those specs step-by-step 3 Evaluator tests implementation against strict criteria What Planner Does Converts short fuzzy human requests into precise structured plans specifications Input Build login feature Output spec containing requirements edge cases security constraints non-functional expectations Behaves like product manager plus systems designer combined Forcing separate spec-generation step surfaces hidden assumptions before any code written Single change cut rework dramatically disagreements about scope came up before implementation not after What Generator Does Implementation agent receives Planner's spec turns into working artifacts using sprint contracts small bounded units work with clear acceptance criteria Think agile sprints but finer granularity Sprint 1 Implement backend API for login Sprint 2 Implement frontend form validation Sprint 3 Integrate error handling security checks Chunking work this way prevents Generator from trying swallow whole app at once exactly where solo agents tend hallucinate or quietly drop requirements What Evaluator Does Separate agent responsible running tests inspecting results scoring quality Critically can't be same agent or same role as Generator In Anthropic implementation Evaluator uses Playwright MCP browser automation tool to run real UI tests Applies explicit scoring criteria including aesthetic bar labeled museum quality If tests or criteria fail sends structured feedback back to Generator Creates feedback loop Generator produces version → Evaluator tests scores → if below threshold Evaluator returns actionable feedback → Generator revises → cycle repeats until approval Detail simply adding phrase museum quality into Evaluator's rubric measurably improved visual design polish outputs Single well-chosen constraint word can steer entire system's standards in ways hard to predict Why separate planning making checking Fixes two failures context instability and self-evaluation bias Planner keeps spec stable Generator implements spec Evaluator cannot be same as Generator so no self-evaluation bias.

6. **Three Operational Layers Context Constraints Feedback Loops** — In harness engineering components cluster into three operational layers Each layer addresses different category failure appears when agents run real-world environments Layer 1 Context Engineering Giving Agent What Needs to Know Agents can only work with what is in context window Anything stored Slack thread Google Doc or someone's memory effectively invisible Context layer ensures right information available at right moment In practice means maintaining structured knowledge base inside repository itself writing progress files and session handoff documents so agents can resume work across context windows and loading relevant documentation dynamically based current task rather than flooding context upfront Anthropic documented problem Each new session began with no memory prior work Solution structured progress logs feature tracking files in JSON rather than Markdown agents less likely overwrite structured data and init script so fresh agent could orient itself instantly Layer 2 Architectural Constraints Preventing Wrong Moves If context layer about what agent knows constraint layer about what agent allowed to do Production agents need hard boundaries Without them agent tasked refactoring module might rewrite entire codebase OpenAI engineering team described enforcing strict layered architecture where each domain had rigid dependency rules so code could only import from adjacent layers Not documentation guidance enforced by custom linters and structural tests that ran every pull request and no agent could bypass them Key insight Constraints do not limit what agent can accomplish They focus it Well-constrained agent produces better output precisely because cannot wander into territory that creates downstream problems Layer 3 Feedback Loops and Verification Catching What Goes Wrong Even well-constrained agent with good context makes mistakes Third layer system that catches and corrects those mistakes before they compound Includes self-verification prompts that instruct agent to run tests check own output before marking task complete garbage collection agents that periodically scan for documentation drift and broken architectural patterns and loop detection middleware that tracks how many times agent edits same file After threshold crossed injects prompt nudging agent reconsider approach breaking doom loops where agents make small variations on broken solution ten or more times in row LangChain engineering team demonstrated impact directly By improving harness without changing underlying model at all their coding agent jumped from 52.8% to 66.5% on Terminal Bench 2.0 moving from 30th to 5th place overall.

7. **Real-World Proof OpenAI 1M Lines LangChain 52.8%→66.5% 51-Agent System** — Clearest evidence harness engineering impact comes from OpenAI Codex team who published findings February 2026 after building entire production product without single human-written line code Constraint radical no human engineer would write single line production code Everything had to be generated by Codex agents Not productivity experiment forcing function if agents could not do work product did not get built Five months later repository contained roughly one million lines code across application logic infrastructure documentation tooling Team three engineers later seven merged approximately 1500 pull requests averaging 3.5 PRs per engineer per day Engineers job not coding was designing harness Structured docs/ directory versioned indexed served as agent's single source truth Short AGENTS.md file acted as table contents pointing agents to right documentation for any task Custom linters enforced architectural rules that no agent could violate even by accident Periodic garbage-collection agents scanned for documentation drift constraint violations Agents had access observability data browser navigation so they could debug failures themselves Lesson same one LangChain confirmed with benchmark results underlying model matters less than system built around it Model provides intelligence but surrounding architecture determines whether intelligence usable consistently LangChain 52.8% to 66.5% without changing model by improving harness without changing underlying model at all their coding agent jumped from 52.8% to 66.5% on Terminal Bench 2.0 moving from 30th to 5th place overall Same model wildly different outcomes harness difference 51-Agent Harness System Real Business Operations Real-world deployment where dozens specialized AI agents cooperate under shared rules hooks pipelines Built independently before Anthropic public Harness blog converged on nearly same architecture anyway System currently includes 51 agents specialized by department role 85 skills discrete capabilities each agent can invoke 21 security hooks blocking actions around data tools 90 rules governing behavior routing Agents grouped similarly to enterprise org chart development code review QA business strategy marketing creative research operations investment legal finance HR Solo Agent vs Harness Cost/Quality Building test app Retro 4G Solo Agent Claude single agent Not specified $9 Core functionality broken code not usable in practice Harness v1 Claude Sonnet 4.5 6 hours $200 16 features delivered across 10 sprints test app fully working Harness v2 Claude Opus 4.6 ~4 hours $120 ~70% complete app in 3 dev + 3 QA cycles service-level quality $9 solo agent run produced something that looked complete app core functionality broken Anyone tried vibe coding with LLMs will recognize pattern large impressive-looking files that fail basic smoke tests Harness variants cost 20x+ more API spend but shipped working software created reliable test coverage QA history and did so under observable repeatable sprints Another finding as underlying models improved Harness scaffolding could be simplified When Claude Sonnet 4.5 arrived explicit context-reset mechanisms became unnecessary With Opus 4.6 even sprint structure could relax because model could self-chunk work more intelligently Harness is not fixed heavy framework living system that should get lighter as models get smarter.

8. **Agent Harness vs Platform Harness** — Term harness split into two distinct concepts 2026 Agent Harness Everything around LLM that turns raw intelligence into reliable autonomous coding agent planning loops memory systems tool orchestration verification error recovery execution runtime guardrails Agent = Model + Harness model provides brain harness is body nervous system safety rails Includes knowledge base architectural constraints tools integrations verification gates state management feedback loops Platform Harness Environment that allows AI agents to contribute to software delivery safely effectively Builds on same foundations we already care about in platform engineering CI/CD test infrastructure observability security deployment safety developer experience Harness engineering is agent-friendly layer of platform engineering for human-agent teams Discipline designing environment that allows AI agents to contribute to software delivery safely effectively Both needed At core any AI system sits LLM To make outputs actionable need agent harness But to make agent operate safely effectively within specific constraints company's Software Development Life Cycle SDLC requires platform harness Example Agent harness Claude Code's loop tools context management hooks sandboxes that turn Claude model into coding agent Platform harness Harness.io platform CI/CD pipelines RBAC audit controls deployment safety that lets Claude Code agent operate safely within company's SDLC Salesforce unveiled Enterprise AI Harness at Dreamforce described new products as parts of it OpenAI Agents API presents itself as managed harness that handles difficult machinery around agent Google shipped new managed-agent harness for Gemini platform.

9. **Harness Engineer Role What Does Engineer Actually Do** — As of early 2026 more likely find listed as AI infrastructure engineer agent platform engineer or AI systems engineer Work though becoming well-defined Core responsibilities 1 Designing knowledge base Ensuring all documentation architecture decisions operational context live in repository where agent can access them not in Slack or someone's head Structured docs/ directory versioned indexed single source truth AGENTS.md table contents 2 Building and maintaining tooling Creating CLI tools MCP servers integrations that give agents same capabilities human engineers rely on Rise of agentic AI communication protocols like MCP and A2A made substantially more approachable in 2026 Ten highly focused tools outperform fifty overlapping 3 Enforcing architectural constraints Writing custom linters structural tests that make it mechanically impossible for agents to violate design rules Strict layered architecture each domain rigid dependency rules code can only import adjacent layers enforced by custom linters structural tests that run every pull request no agent can bypass 4 Building verification systems Constructing feedback loops test runners self-check prompts that catch agent errors before they compound Self-verification prompts instruct agent run tests check own output before marking task complete garbage collection agents periodically scan for documentation drift broken patterns loop detection middleware tracks how many times agent edits same file after threshold injects prompt nudging agent reconsider breaking doom loops 5 Running improvement loops Analyzing agent traces to find recurring failure modes then fixing harness so failures do not repeat Every line in good system prompt should trace back to specific historical failure Distinct from simply building LLM-powered agents Harness is what keeps agents working consistently after demo is over and across kind long-horizon tasks that separate proof-of-concept from production LangChain deep-dive on anatomy of agent harness and academic framing in Pan et al work on natural-language agent harnesses both arrive same conclusion harness is primary unit engineering work in agent-first world not model What remains is infrastructure trust security efficiency including scoped permissions guardrails against catastrophic actions or $10000 API fee Harness is software around AI model that lets it read files run tools act What lasts in view is part model cannot be trained to do limit what agent may touch and spend.

10. **The Ratchet Principle Every Mistake Becomes Rule** — Most vital habit harness engineering treating agent mistakes as permanent signals not one-off flukes to retry forget If agent ships pull request with commented-out test that gets merged by accident that is signal Next iteration rule file must state Never comment out tests Delete or fix them Next pre-commit hook should automatically flag skipped tests in diff Reviewer subagent must be updated to block commented-out tests Every line in good system prompt should trace back to specific historical failure Constraints should only be added when observe real failure and removed only when capable model renders them redundant Because of this harness engineering is discipline rather than one-size-fits-all framework Right harness for organisation entirely shaped by its unique failure history This is ratchet principle harness only tightens never loosens unless model upgrade makes constraint unnecessary Over time creates system that becomes more reliable with every mistake it makes Working backwards from desired behavior Most effective way design harness start with desired behavior build component that delivers it Examples Behavior you want Agent never ships broken code Harness component Pre-commit hook runs full test suite blocks commits on failure Behavior you want Agent follows project-specific conventions Harness component AGENTS.md file at project root encoding every convention learned from past failures Behavior you want Agent completes long tasks without stopping early Harness component Loop interceptor catches agent attempt to exit forces continuation against completion goal Behavior you want Agent does not grade own work positively Harness component Separate generation and evaluation into distinct agents preventing inherent bias models have when reviewing own output Behavior you want Agent handles multi-step work predictably Harness component Planning phase forces decomposition into step-by-step plan file with self-verification hooks after each step Every piece harness must have distinct job If cannot name specific behavior component exists to deliver remove it.

11. **How to Build Your Own Harness Practical Steps** — Step 1 Pick your harness framework Do not build orchestration from scratch Use existing harness Claude Code Cursor OpenClaw Codex that provides loop tools context management hooks sandboxes out of box Step 2 Write first rule file Create AGENTS.md or equivalent at root project Start 5-10 rules each tracing back to real mistake team or agent made Keep short pilot checklist not style guide Example AGENTS.md Project Overview Rules each from real failure Never comment out tests Delete or fix them Failed PR #123 commented test merged Always run test suite before committing Agent shipped broken code Jan 2026 Never touch files outside src/refund/* without approval Agent rewrote entire codebase Feb 2026 Always check policy version v2.3 before generating refund logic Agent used stale v1.0 Bundle promotion refunds need approval per policy page 25 never auto-refund bundles Where to Find What Refund policies docs/policies/ Architecture docs/architecture.md API contracts docs/api/ Tests tests/ Step 3 Add one hook Pick most common failure mode workflow add single hook that prevents it Pre-commit typecheck lint rule test runner One hook one failure mode Example pre-commit hook Block commented-out tests git diff --cached grep -E ^\+\s*//\s*test ^\+\s*/\*.*test echo ERROR Commented-out tests detected Delete or fix them per AGENTS.md rule 1 exit 1 Run tests npm test if $? -ne 0 echo ERROR Tests failed Fix before committing exit 1 Step 4 Run agent and observe Every mistake is signal Each time agent fails ask Can I add rule hook or tool that makes this failure impossible next time Step 5 Tighten ratchet Over weeks months harness accumulates constraints born from real failures Agent becomes more reliable not because model improved but because scaffolding around it got tighter Example for growing businesses Construction company using AI to process site reports harness might include Rule file encoding report format conventions mandatory fields Hook validates every generated report against schema before submission Sandbox isolates report processing from production database Memory file accumulating site-specific terminology project codes over time Allied health practice using AI to draft treatment plans harness might include Rule file encoding clinical documentation standards privacy requirements Hook flags any generated text containing patient identifiers for human review Context management policy strips sensitive data from long-term memory Split architecture where one agent generates separate agent evaluates Professional services firm using AI agents for client research proposal drafting harness might include Rule file encoding firm's writing style methodology frameworks compliance requirements Hook runs every proposal through quality checklist before client delivery Subagent orchestration where one agent researches one drafts one reviews Memory file accumulates client preferences past feedback over time Harnesses do not shrink they move As models improve need for harness does not disappear shifts Tempting assume better models make scaffolding obsolete Recent model upgrades drastically reduced need for context-anxiety mitigations for example But as floor raises so does ceiling Tasks previously unreachable now in play bringing entirely new failure modes Every component in harness encodes assumption about what model cannot do on own When model improves outdated scaffolding should be removed and new scaffolding must be built to reach next horizon This is why harness engineering continuous discipline not one-time setup Best harnesses evolve with every model upgrade every new task attempted.

12. **Harness-as-a-Service Industry Shift** — Industry shifting from building on LLM APIs which provide completions to building on Harness APIs which provide runtime SDKs now offer loop tools context management hooks sandboxes right out of box Instead building orchestration from scratch modern default select harness framework configure core pillars focus purely on domain-specific prompt and tool design This is what makes troubleshooting scalable tuning well-factored configuration surface rather than reinventing entire agent architecture If look at top coding agents today they look more like each other than underlying models do Models differ but harness patterns are Harness Platform Examples Harness.io Company AI Software Delivery Platform company enabling engineering teams build test deliver software faster securely Powered by Harness AI and Software Delivery Knowledge Graph platform brings intelligent automation to every stage software delivery lifecycle after code removing toil freeing developers from manual repetitive work Purpose-Built AI Agents leverage Harness AI agents or build own AI agents to automate repetitive operational tasks Generate pipelines using AI fine tune using visual editor apply bulk updates using APIs or MCP Teams using Harness AI report 85% faster pipeline onboarding 7x faster issue resolution 2 hours saved per project average Embedded directly in Harness Platform with full RBAC audit controls Claude Code Cursor Codex Aider Cline All harnesses same models different behavior dominated by harness OpenAI Agents API Salesforce Enterprise AI Harness Google Gemini Managed-Agent Harness All present themselves as managed harness that handles difficult machinery around agent Future Harness Engineering Belongs in Platform Engineering Conversation Working definition Harness engineering is agent-friendly layer of platform engineering for human-agent teams More specifically engineering discipline designing environment that allows AI agents to contribute to software delivery safely effectively Builds on same foundations we already care about in platform engineering CI/CD test infrastructure observability security deployment safety developer experience As models improve explicit context-reset mechanisms became unnecessary with Sonnet 4.5 even sprint structure could relax with Opus 4.6 because model could self-chunk work more intelligently Harness not fixed heavy framework living system that should get lighter as models get smarter.

---
**Bottom Line:** Prompt engineering shapes what agent tries Context engineering shapes what agent knows Harness engineering shapes what agent can and cannot do Term popularized by Mitchell Hashimoto creator Terraform Ghostty early 2026 and Addy Osmani Google engineering leader May 2026 Every time an agent makes a mistake you don't just tell it to do better next time You change the system so that specific mistake becomes structurally harder to repeat Agent = Model + Harness If you are not model you are harness Decent model with great harness beats great model with bad harness LangChain raised accuracy 52.8% to 66.5% by changing only harness same model OpenAI Codex team shipped 1M lines production code in 5 months with 3 engineers using harness engineering Two fundamental failures Context Instability tendency AI to lose track earlier work as session grows and Self-Evaluation Bias same model that created work also asked to judge it I watched it identify legitimate issue then talk itself into deciding they weren't big deal and approved work anyway Seven Pillars System Prompts Rule Files AGENTS.md pilot checklist every rule earned past failure Tools Skills ten highly focused tools outperform fifty overlapping security risks unverified MCP servers Filesystem Version Control Git-backed non-negotiable Sandboxes Safe Execution isolated environments pre-installed runtimes test CLIs headless browsers Memory Continual Learning memory files inject knowledge every session accumulating domain expertise Context Management Compaction intelligently summarizing offloading older context tool-call offloading storing massive logs in filesystem progressive disclosure revealing instructions only when task requires Hooks Enforcement Layers run specific lifecycle points before tool call after file edit before commit block destructive commands enforce auto-formatting run test suites success silent failures verbose Three Operational Layers Context Engineering Giving Agent What Needs to Know structured knowledge base inside repository progress files session handoff documents loading relevant documentation dynamically Architectural Constraints Preventing Wrong Moves hard boundaries custom linters structural tests that make mechanically impossible violate design rules Constraints do not limit what agent can accomplish They focus it Feedback Loops Verification Catching What Goes Wrong self-verification prompts garbage collection agents loop detection middleware tracks how many times agent edits same file injects prompt reconsider breaking doom loops Planner-Generator-Evaluator Architecture Inspired by GANs Planner turns vague requests into detailed specs product manager systems designer surfaces hidden assumptions before code Generator implements specs step-by-step using sprint contracts small bounded units work acceptance criteria chunking prevents swallow whole app Evaluator separate agent running tests inspecting results scoring quality using Playwright MCP real UI tests explicit scoring criteria museum quality If fail sends structured feedback to Generator cycle repeats until approval Real-World Proof OpenAI 1M lines 5 months 3 engineers later seven 1500 PRs 3.5 PRs per engineer per day structured docs/ directory single source truth AGENTS.md table contents custom linters enforced rules no agent could violate garbage-collection agents scanned drift observability data browser navigation debug failures LangChain 52.8%→66.5% Terminal Bench 2.0 30th→5th place 51-Agent System 51 agents 85 skills 21 security hooks 90 rules grouped enterprise org chart development QA business strategy marketing creative research operations investment legal finance HR Solo Agent vs Harness $9 solo core broken vs $200 Harness v1 Sonnet 4.5 6 hours 16 features 10 sprints fully working vs $120 Harness v2 Opus 4.6 4 hours ~70% complete 3 dev+3 QA cycles service-level quality As models improve harness scaffolding could be simplified Sonnet 4.5 explicit context-reset unnecessary Opus 4.6 sprint structure relax self-chunk more intelligently Harness not fixed heavy framework living system should get lighter as models get smarter Agent Harness vs Platform Harness Agent Harness everything around LLM planning loops memory tool orchestration verification error recovery execution runtime guardrails body nervous system safety rails Platform Harness environment that allows AI agents to contribute software delivery safely effectively agent-friendly layer platform engineering CI/CD test infrastructure observability security deployment safety developer experience Both needed Agent harness Claude Code loop tools context management hooks sandboxes Platform harness Harness.io CI/CD RBAC audit controls deployment safety Salesforce Enterprise AI Harness OpenAI Agents API managed harness Google Gemini managed-agent harness Harness Engineer Role Designing knowledge base documentation architecture decisions operational context live in repository Building maintaining tooling CLI tools MCP servers integrations same capabilities human engineers Enforcing architectural constraints custom linters structural tests mechanically impossible violate design rules Building verification systems feedback loops test runners self-check prompts catching errors before compound Running improvement loops analyzing agent traces finding recurring failure modes fixing harness so failures do not repeat Distinct from building LLM-powered agents Harness is what keeps agents working consistently after demo is over long-horizon tasks proof-of-concept vs production What remains is infrastructure trust security efficiency scoped permissions guardrails against catastrophic actions $10000 API fee Harness is software around AI model that lets it read files run tools act What lasts is part model cannot be trained to do limit what agent may touch and spend Ratchet Principle Every Mistake Becomes Rule Most vital habit treating agent mistakes as permanent signals not one-off flukes to retry forget If agent ships PR with commented-out test merged accident signal Next iteration rule file must state Never comment out tests Delete or fix them Next pre-commit hook automatically flag skipped tests diff Reviewer subagent updated block commented-out tests Every line in good system prompt should trace back to specific historical failure Constraints only added when observe real failure removed only when capable model renders them redundant Right harness for organisation entirely shaped by its unique failure history ratchet principle harness only tightens never loosens unless model upgrade makes constraint unnecessary Over time creates system that becomes more reliable with every mistake it makes Working backwards from desired behavior start with desired behavior build component that delivers it Agent never ships broken code Pre-commit hook runs full test suite blocks commits on failure Agent follows project-specific conventions AGENTS.md encoding every convention learned from past failures Agent completes long tasks without stopping early Loop interceptor catches attempt to exit forces continuation against completion goal Agent does not grade own work positively Separate generation evaluation into distinct agents preventing inherent bias Agent handles multi-step work predictably Planning phase forces decomposition into step-by-step plan file with self-verification hooks after each step Every piece harness must have distinct job If cannot name specific behavior component exists to deliver remove it How to Build Your Own Harness Pick harness framework Do not build orchestration from scratch Use existing harness Claude Code Cursor OpenClaw Codex Write first rule file AGENTS.md 5-10 rules each tracing back to real mistake Keep short pilot checklist Add one hook Pick most common failure mode add single hook that prevents it Run agent and observe Every mistake is signal Each time agent fails ask Can I add rule hook or tool that makes this failure impossible next time Tighten ratchet Over weeks months harness accumulates constraints born from real failures Agent becomes more reliable not because model improved but because scaffolding around it got tighter Harnesses do not shrink they move As models improve need for harness does not disappear shifts As floor raises so does ceiling Tasks previously unreachable now in play bringing entirely new failure modes Every component in harness encodes assumption about what model cannot do on own When model improves outdated scaffolding should be removed and new scaffolding must be built to reach next horizon This is why harness engineering continuous discipline not one-time setup Best harnesses evolve with every model upgrade every new task attempted Harness-as-a-Service Industry shifting from building on LLM APIs which provide completions to building on Harness APIs which provide runtime SDKs now offer loop tools context management hooks sandboxes right out of box Modern default select harness framework configure core pillars focus purely on domain-specific prompt and tool design This is what makes troubleshooting scalable tuning well-factored configuration surface rather than reinventing entire agent architecture Top coding agents today look more like each other than underlying models do Models differ but harness patterns are Harness.io Company AI Software Delivery Platform Powered by Harness AI and Software Delivery Knowledge Graph intelligent automation every stage software delivery lifecycle after code removing toil freeing developers 85% faster pipeline onboarding 7x faster issue resolution 2 hours saved per project Embedded directly with full RBAC audit controls Claude Code Cursor Codex Aider Cline All harnesses same models different behavior dominated by harness OpenAI Agents API Salesforce Enterprise AI Harness Google Gemini Managed-Agent Harness All present themselves as managed harness that handles difficult machinery around agent Future Harness Engineering Belongs in Platform Engineering Conversation Working definition Harness engineering is agent-friendly layer of platform engineering for human-agent teams Designing environment that allows AI agents to contribute to software delivery safely effectively Builds on same foundations CI/CD test infrastructure observability security deployment safety developer experience As models improve explicit context-reset mechanisms became unnecessary with Sonnet 4.5 even sprint structure could relax with Opus 4.6 because model could self-chunk work more intelligently Harness not fixed heavy framework living system that should get lighter as models get smarter.
