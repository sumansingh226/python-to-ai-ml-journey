# Trees in Agentic AI: Search Trees, Decision Trees, and Execution Trees
## How Agents Explore, Plan, and Decide Using Tree Structures

> **Core Thesis:** Trees are how agents think beyond linear chains. A chain is one path Thought->Action->Observation. A tree explores multiple paths, evaluates them, backtracks, and picks the best. Tree-of-Thought, MCTS, and execution trees turn agents from greedy next-step predictors into planners that search, just like chess engines. Result: 20-40% better success on complex reasoning, coding, and multi-step tasks.

### Table of Contents
1. [Why Trees? Chain vs Tree](#1-why-trees-chain-vs-tree)
2. [Type 1: Tree-of-Thought (ToT) - Reasoning Tree](#2-type-1-tree-of-thought-tot---reasoning-tree)
3. [Type 2: Monte Carlo Tree Search (MCTS) for Agents](#3-type-2-monte-carlo-tree-search-mcts-for-agents)
4. [Type 3: Decision Trees / Behavior Trees for Control](#4-type-3-decision-trees--behavior-trees-for-control)
5. [Type 4: Execution Trees / Task Trees (DAG is a Tree)](#5-type-4-execution-trees--task-trees-dag-is-a-tree)
6. [Type 5: Conversation Trees / Branching Context](#6-type-5-conversation-trees--branching-context)
7. [Type 6: Knowledge Trees / Hierarchical Memory](#7-type-6-knowledge-trees--hierarchical-memory)
8. [Implementation Blueprint](#8-implementation-blueprint)
9. [When to Use Chain vs Tree vs Graph](#9-when-to-use-chain-vs-tree-vs-graph)
10. [Production Checklist](#10-production-checklist)

---

### 1. Why Trees? Chain vs Tree

**Chain (ReAct):** Linear Thought->Action->Observation->Thought... One path, greedy. If first Thought wrong, entire trajectory fails. No backtracking.

```
Chain:
Thought: Check order status
Action: get_order_status(ORD-123)
Observation: $120 delivered
Thought: Refund $120
Action: refund_order(ORD-123, 120) -> fails trust_score required
Failed - no backtrack
```

**Tree:** Explore multiple Thoughts at each step, evaluate, pick best path, backtrack if needed.

```
Tree at step 2:
Root: Order $120 delivered
  |
  +-> Branch A Thought: Refund directly -> Action refund_order -> fails trust_score required (score: 2/10)
  +-> Branch B Thought: Check policy first -> Action get_policy -> <500 auto, trust>80 (score: 8/10)
  +-> Branch C Thought: Check trust first -> Action get_trust_score -> 85 (score: 9/10) <- Best

Pick Branch C, then from C explore next step:
  C -> Branch C1: Refund now -> success (score 10/10) -> Pick C1

Result: Success via search, not greedy.
```

**Why trees better:**
- Complex tasks have multiple valid approaches, chain picks first, tree explores 3-5 and picks best
- Enables backtracking - if branch fails, try other branch (chain cannot)
- Evaluates intermediate steps (is this Thought promising?)
- 20-40% better on Game of 24, coding, math, complex refunds

**Cost:** Tree explores 3x more paths = 3x LLM calls = 3x cost vs chain. Worth for high-value tasks ($500+ refund, coding) but not for simple FAQ.

### 2. Type 1: Tree-of-Thought (ToT) - Reasoning Tree

From Yao et al. 2023 Tree-of-Thoughts paper - extends Chain-of-Thought by branching.

**How it works:**

1. Generate 3-5 Thoughts at each step (branching factor k=3)
2. Evaluate each Thought with value function (LLM as evaluator scores 1-10)
3. Search via BFS or DFS, keep best b branches (beam width b=2)
4. Backtrack if dead end
5. Pick path with highest final score

**Pseudocode:**

```python
def tree_of_thought(query, branching_factor=3, beam_width=2, max_depth=5):
    # Root
    root = Node(thought="Start", score=0, depth=0)
    frontier = [root] # BFS frontier
    
    for depth in range(max_depth):
        candidates = []
        for node in frontier:
            # Generate k thoughts from this node
            thoughts = llm.generate(f"Query: {query}\nHistory: {node.path()}\nGenerate {branching_factor} different next thoughts", n=branching_factor, temperature=0.7)
            for thought in thoughts:
                # Evaluate thought
                score = llm.generate(f"Query: {query}\nHistory: {node.path()}\nThought: {thought}\nRate this thought 1-10 for progressing to answer", temperature=0.0)
                score = parse_score(score) # e.g., 8/10
                child = Node(thought=thought, parent=node, score=score, depth=depth+1)
                candidates.append(child)
        
        # Keep top beam_width candidates
        candidates.sort(key=lambda x: x.score, reverse=True)
        frontier = candidates[:beam_width]
        
        # Check if any candidate is done
        for node in frontier:
            if is_done(node.thought):
                return node.path() # Best path
    
    # Return best path from frontier
    frontier.sort(key=lambda x: x.score, reverse=True)
    return frontier[0].path()

# Example for refund
# Depth 0: Root "Refund ORD-12345"
# Depth 1 candidates:
#   Thought A: "Refund directly" score 3/10
#   Thought B: "Check policy first" score 8/10
#   Thought C: "Check trust first" score 9/10
# Keep top 2: B (8) and C (9)
# Depth 2 from B and C:
#   From B: "Policy says <500 auto if trust>80" score 9, "Check trust" score 9
#   From C: "Trust 85 >80, check policy" score 9, "Refund now" score 7
# Keep top 2: Both score 9
# Depth 3: Refund -> success score 10 -> done
```

**BFS vs DFS:**

- BFS: Explore all nodes at depth d, then depth d+1. Good for shallow trees where best path near root.
- DFS: Explore one branch deep, backtrack if fails. Good for deep trees where need to go deep to find solution (coding).

**Evaluation function:**

- LLM as evaluator: Prompt "Rate this thought 1-10 for progressing to answer"
- Can also use tool output: If action returns success, score 10; if error, score 2
- Can use heuristic: If thought mentions checking required fields (trust_score, policy) before refund, score higher

**Pros:**
- 20-40% better than Chain-of-Thought on Game of 24, creative writing, math
- Enables backtracking
- Evaluates intermediate steps, not just final answer

**Cons:**
- 3-5x cost (k=3 branching * depth 5 = 15 LLM calls vs 5 for chain)
- Evaluation can be noisy — LLM evaluator may score wrong
- Needs tuning branching_factor and beam_width

**When to use:** Complex reasoning tasks where first thought often wrong — math, coding, complex policy checks with multiple dependencies. For refund example, ToT helps when policy has multiple conditions.

**Cost:** k=3, depth=5, beam=2: ~15 LLM calls vs 5 for chain = 3x cost. For high-value task $500+ refund, worth 20% more success.

### 3. Type 2: Monte Carlo Tree Search (MCTS) for Agents

MCTS = ToT + simulation + backpropagation. Used in AlphaGo, now in agents for coding and planning.

**4 steps:**

1. **Selection:** Traverse tree from root to leaf using UCT (Upper Confidence Bound) balancing exploration vs exploitation
2. **Expansion:** Generate new child nodes (thoughts) from leaf
3. **Simulation:** From new node, simulate random rollout to terminal (or use LLM to estimate value)
4. **Backpropagation:** Propagate value back to root, update visit counts and scores

**Pseudocode:**

```python
class MCTSNode:
    def __init__(self, thought, parent=None):
        self.thought = thought
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0

def uct_score(node, parent_visits, c=1.4):
    if node.visits == 0:
        return float('inf') # Explore unvisited
    exploitation = node.value / node.visits
    exploration = c * math.sqrt(math.log(parent_visits) / node.visits)
    return exploitation + exploration

def mcts_search(query, iterations=50):
    root = MCTSNode(thought="Start")
    
    for i in range(iterations):
        # 1. Selection: Traverse to leaf using UCT
        node = root
        while node.children:
            node = max(node.children, key=lambda c: uct_score(c, node.visits))
        
        # 2. Expansion: Generate k children from leaf
        if not is_done(node.thought) and node.visits > 0: # Expand only visited nodes
            thoughts = llm.generate(f"Query: {query}\nHistory: {node.path()}\nGenerate 3 next thoughts", n=3, temperature=0.7)
            for thought in thoughts:
                child = MCTSNode(thought=thought, parent=node)
                node.children.append(child)
            node = random.choice(node.children) # Pick one child to simulate
        
        # 3. Simulation: Rollout from node to terminal using fast LLM or heuristic
        rollout_path = [node.thought]
        current = node.thought
        for _ in range(5): # Rollout depth 5
            if is_done(current):
                break
            next_thought = llm.generate(f"Query: {query}\nHistory: {rollout_path}\nNext thought (fast)", temperature=0.7)
            rollout_path.append(next_thought)
            current = next_thought
        
        # Evaluate rollout final state
        final_score = llm.generate(f"Query: {query}\nPath: {rollout_path}\nRate final answer 1-10", temperature=0.0)
        value = parse_score(final_score) / 10.0 # Normalize 0-1
        
        # 4. Backpropagation: Update value and visits back to root
        while node:
            node.visits += 1
            node.value += value
            node = node.parent
    
    # Pick best child of root with highest average value
    best = max(root.children, key=lambda c: c.value / c.visits if c.visits>0 else 0)
    return best.path()
```

**Pros:**
- Balances exploration (try new branches) vs exploitation (use known good branches) via UCT
- Simulation estimates long-term value, not just immediate thought score
- Works well for coding, game playing, planning where need lookahead

**Cons:**
- Even more expensive than ToT: iterations=50 * rollout depth 5 = 250 LLM calls vs 15 for ToT
- Needs tuning c parameter, iterations
- Simulation can be noisy

**When to use:** Very complex tasks requiring lookahead — coding (generate code, simulate execution, evaluate), game playing, complex multi-step planning with dependencies. For refund, overkill — ToT sufficient.

**Cost:** iterations=50, depth=5: 250 LLM calls vs 5 chain = 50x cost. Only for very high-value tasks (code generation $100 value).

### 4. Type 3: Decision Trees / Behavior Trees for Control

**What:** Hard-coded tree for agent control flow, not LLM-generated thoughts. Each node is a condition or action.

**Behavior Tree (from game AI):**

```
Root (Selector - tries children until one succeeds)
  |
  +-> Sequence (Check if refund allowed)
  |     |
  |     +-> Condition: order_exists? (if no, fail)
  |     +-> Condition: amount <500? (if no, go to approval)
  |     +-> Condition: trust_score >80? (if no, go to approval)
  |     +-> Action: refund_order
  |
  +-> Sequence (Request approval)
        |
        +-> Action: serialize_state waiting_approval
        +-> Action: send_webhook
```

**Implementation:**

```python
class BTNode:
    def tick(self, state): # Returns SUCCESS, FAILURE, RUNNING
        pass

class Condition(BTNode):
    def __init__(self, check_fn):
        self.check_fn = check_fn
    def tick(self, state):
        return SUCCESS if self.check_fn(state) else FAILURE

class Action(BTNode):
    def __init__(self, action_fn):
        self.action_fn = action_fn
    def tick(self, state):
        result = self.action_fn(state)
        return SUCCESS if result else FAILURE

class Sequence(BTNode): # And - all children must succeed
    def __init__(self, children):
        self.children = children
    def tick(self, state):
        for child in self.children:
            status = child.tick(state)
            if status != SUCCESS:
                return status
        return SUCCESS

class Selector(BTNode): # Or - try children until one succeeds
    def __init__(self, children):
        self.children = children
    def tick(self, state):
        for child in self.children:
            status = child.tick(state)
            if status == SUCCESS:
                return SUCCESS
        return FAILURE

# Build refund behavior tree
refund_tree = Selector([
    Sequence([
        Condition(lambda s: order_exists(s.order_id)),
        Condition(lambda s: s.amount < 500),
        Condition(lambda s: s.trust_score > 80),
        Action(lambda s: refund_order(s.order_id, s.amount))
    ]),
    Sequence([
        Action(lambda s: request_approval(s)),
        Action(lambda s: notify_user("Waiting approval"))
    ])
])

# Execute
status = refund_tree.tick(state)
```

**Pros:**
- Deterministic, auditable, no LLM hallucination for control flow
- Fast (no LLM calls for control)
- Easy to debug
- Good for policy enforcement (if amount>500 then approval else auto)

**Cons:**
- Hard-coded, not flexible — need to code tree for each task
- Doesn't handle novel situations

**When to use:** ALWAYS for policy enforcement and high-risk control flow — amount checks, PII checks, delete operations. Use behavior tree for deterministic part, LLM for reasoning part. This is mandatory for SOC2, EU AI Act.

**Hybrid:** Behavior tree for control (if amount>500 then approval), LLM for reasoning (what is trust_score?).

### 5. Type 4: Execution Trees / Task Trees (DAG is a Tree)

**What:** Represent task decomposition as tree — root is main goal, children are sub-goals, leaves are tool calls.

```
Root: Process refund for ORD-12345
  |
  +-> Sub-goal 1: Get order info
  |     |
  |     +-> Tool: get_order_status(ORD-12345) -> $120
  |
  +-> Sub-goal 2: Check policy
  |     |
  |     +-> Tool: get_policy(v2.3) -> <500 auto
  |
  +-> Sub-goal 3: Check trust
  |     |
  |     +-> Tool: get_trust_score(user) -> 85
  |
  +-> Sub-goal 4: Refund (depends on 1,2,3)
  |     |
  |     +-> Tool: refund_order(ORD-12345, 120)
  |
  +-> Sub-goal 5: Notify (depends on 4)
        |
        +-> Tool: send_email(user, "Refund $120")
```

**This is a tree (actually DAG because sub-goal 4 depends on 1,2,3 — multiple parents — so it's DAG, but often called task tree).**

**Implementation with planning loop:**

```python
def build_task_tree(user_goal):
    # LLM decomposes goal into sub-goals with dependencies
    plan = llm.generate(f"Goal: {user_goal}\nDecompose into sub-goals with dependencies as JSON tree: {{goal, sub_goals: [{{id, goal, dependencies: [id], tool: {{name, args}}}}]}}", schema=TaskTreeSchema, temperature=0.4)
    return plan

def execute_task_tree(task_tree):
    completed = {}
    # Topological sort by dependencies
    sorted_tasks = topological_sort(task_tree.sub_goals)
    
    for task in sorted_tasks:
        # Check dependencies completed
        if not all(dep in completed for dep in task.dependencies):
            raise Exception(f"Dependency not met for {task.id}")
        
        # Execute task (ReAct loop for each sub-goal)
        result = react_loop(task.goal, max_steps=5)
        completed[task.id] = result
    
    return completed
```

**Pros:**
- Clear decomposition — easy to see which sub-goal failed
- Enables parallel execution — sub-goals 1,2,3 have no dependencies, can run parallel (multi-agent)
- Optimal scheduling via topological sort

**Cons:**
- Need to define tree via LLM planning — planning can be wrong
- More complex than linear chain

**When to use:** Complex tasks with 5+ steps and dependencies — use for multi-agent orchestration.

### 6. Type 5: Conversation Trees / Branching Context

**What:** Conversation is not linear — it branches. User asks follow-up, agent clarifies, etc. Conversation tree stores branching with parent pointers.

```
User: "Refund ORD-123"
  |
Agent: "Order $120, refund?"
  |
User: "Yes, but also check my other order ORD-456" -> branches from root
  |
Agent: Need to handle two orders — creates two branches
  |
  Branch 1: ORD-123 refund -> success
  Branch 2: ORD-456 status -> $500 -> needs approval -> waiting
```

**Implementation:**

```python
class ConversationNode:
    def __init__(self, id, parent_id, role, content, branch_id):
        self.id = id
        self.parent_id = parent_id
        self.role = role
        self.content = content
        self.branch_id = branch_id

# Store in Postgres
# CREATE TABLE conversation_tree (id TEXT PRIMARY KEY, parent_id TEXT, task_id TEXT, branch_id TEXT, role TEXT, content TEXT, timestamp TIMESTAMPTZ)
```

**Pros:**
- Handles non-linear conversations — follow-ups, clarifications, parallel sub-tasks
- Enables undo — revert to parent node

**Cons:**
- More complex than linear history array

**When to use:** Complex conversations with branching, multi-tasking, or need undo.

### 7. Type 6: Knowledge Trees / Hierarchical Memory

**What:** Hierarchical organization of knowledge — root is broad topic, children are sub-topics, leaves are facts.

```
Root: Company Knowledge
  |
  +-> Team: Analytics
  |     |
  |     +-> Members: Alice, Bob, Carol
  |     +-> Projects: Feature X, Feature Z
  |     +-> Policies: Refund policy <500 auto
  |
  +-> Product: Feature X
        |
        +-> Built by: Team Y
        +-> Amount: $120
        +-> Status: Delivered
```

**This is Knowledge Graph as tree (hierarchical), not general graph.**

**Implementation:**

```python
# Hierarchical memory with parent pointers
class KnowledgeNode:
    def __init__(self, id, type, properties, parent_id=None):
        self.id = id
        self.type = type
        self.properties = properties
        self.parent_id = parent_id
        self.children = []

# Store in Postgres with ltree extension for hierarchical queries
# CREATE TABLE knowledge_tree (id TEXT PRIMARY KEY, type TEXT, properties JSONB, parent_id TEXT, path LTREE);
# path = Company.Analytics.TeamY for hierarchical query: SELECT * FROM knowledge_tree WHERE path <@ 'Company.Analytics'
```

**Pros:**
- Hierarchical — easy to query sub-tree (all knowledge under Analytics team)
- Efficient for broad queries

**Cons:**
- Less flexible than graph — tree is hierarchical, graph can have arbitrary relationships (e.g., Alice manages Team Y and also built Feature X — two parents, not tree)

**When to use:** When knowledge is naturally hierarchical — org chart, product categories, file system.

**vs Knowledge Graph:** Tree is subset of graph — tree has one parent per node (hierarchical), graph has multiple parents and arbitrary edges. Use tree when hierarchy matters, graph when relationships arbitrary.

### 8. Implementation Blueprint

**Tree-of-Thought with LangGraph:**

```python
from langgraph.graph import StateGraph

class ToTState(TypedDict):
    query: str
    thoughts: list
    scores: list
    depth: int

def generate_thoughts(state: ToTState):
    thoughts = llm.generate(f"Query: {state['query']}\nHistory: {state['thoughts']}\nGenerate 3 thoughts", n=3, temperature=0.7)
    return {"thoughts": state["thoughts"] + thoughts}

def evaluate_thoughts(state: ToTState):
    scores = []
    for thought in state["thoughts"][-3:]: # Last 3 generated
        score = llm.generate(f"Query: {state['query']}\nThought: {thought}\nRate 1-10", temperature=0.0)
        scores.append(parse_score(score))
    return {"scores": state["scores"] + scores}

def should_continue(state: ToTState):
    if max(state["scores"]) > 8 or state["depth"] > 5:
        return "end"
    else:
        return "generate"

workflow = StateGraph(ToTState)
workflow.add_node("generate", generate_thoughts)
workflow.add_node("evaluate", evaluate_thoughts)
workflow.set_entry_point("generate")
workflow.add_edge("generate", "evaluate")
workflow.add_conditional_edges("evaluate", should_continue, {"generate": "generate", "end": END})
app = workflow.compile()
result = app.invoke({"query": "Refund ORD-12345", "thoughts": [], "scores": [], "depth": 0})
```

**MCTS for coding:**

```python
# For coding task, use MCTS with code execution as simulation
def mcts_code_generation(task):
    root = MCTSNode(thought="Start code")
    for i in range(50):
        node = select_uct(root)
        if node.visits>0:
            children = generate_code_variants(node.thought, k=3)
            for child_code in children:
                child = MCTSNode(thought=child_code, parent=node)
                node.children.append(child)
            node = random.choice(node.children)
        
        # Simulation: Execute code, get test results
        test_result = execute_code(node.thought)
        value = 1.0 if test_result.passed else 0.0
        
        # Backprop
        while node:
            node.visits += 1
            node.value += value
            node = node.parent
    
    best = max(root.children, key=lambda c: c.value/c.visits)
    return best.thought
```

### 9. When to Use Chain vs Tree vs Graph

| Structure | Cost | Success | When to Use |
| :--- | :--- | :--- | :--- |
| **Chain (ReAct)** | 1x (5 LLM calls) | 70% | Simple tasks, FAQ, single tool call |
| **Tree (ToT)** | 3x (15 calls) | 85-90% (+15-20%) | Complex reasoning, math, coding, multi-condition policy |
| **Tree (MCTS)** | 50x (250 calls) | 90-95% (+20-25%) | Very complex: code generation, game playing, planning with lookahead |
| **Graph (GraphRAG)** | 3x query, 100x build | 85% multi-hop vs 60% vector | Multi-hop QA, knowledge base with relationships |
| **Behavior Tree** | 0.1x (no LLM for control) | 99% deterministic | Policy enforcement, high-risk control flow (amount>500 then approval) |

**Decision:**

- Simple FAQ: Chain (ReAct)
- Complex reasoning with multiple valid approaches: Tree-of-Thought (k=3, beam=2)
- Very complex with lookahead (coding, game): MCTS (iterations=50)
- Multi-hop QA over KB: Graph (GraphRAG)
- Policy enforcement: Behavior Tree (deterministic) + Chain/Tree for reasoning part

**Hybrid: Use all together**

```
Root: Behavior Tree for control (if amount>500 then approval else auto)
  |
  +-> Sub-goal: Check policy -> Use GraphRAG to retrieve policy (graph traversal)
  +-> Sub-goal: Decide approach -> Use Tree-of-Thought to explore 3 approaches, pick best
  +-> Sub-goal: Execute -> Chain (ReAct loop) for tool calls
```

### 10. Production Checklist

1. **Chain is default** — Start with ReAct chain (Thought->Action->Observation loop), measure success rate. If <80% on complex tasks, add tree.
2. **Tree-of-Thought for complex reasoning** — Generate k=3 thoughts at each step, evaluate with LLM scorer 1-10, keep beam_width=2 best, BFS or DFS, max depth 5. Cost 3x chain, +15-20% success.
3. **MCTS for very complex** — Selection via UCT (exploration vs exploitation), expansion k=3, simulation via rollout or code execution, backpropagation value. iterations=50, cost 50x chain, +20-25% success. Only for coding, game playing.
4. **Behavior Trees for policy enforcement** — Deterministic tree with Sequence (And) and Selector (Or) nodes, Conditions and Actions, no LLM for control flow. Mandatory for high-risk: amount>500, PII, delete. Hybrid with LLM for reasoning.
5. **Execution Trees / Task Trees for decomposition** — Decompose goal into sub-goals with dependencies as tree/DAG, topological sort, execute ready tasks parallel (multi-agent). Clear which sub-goal failed.
6. **Conversation Trees for branching** — Store conversation as tree with parent_id + branch_id, not linear array. Handles follow-ups, multi-tasking, undo.
7. **Knowledge Trees for hierarchical memory** — Hierarchical org chart, product categories, file system. Use Postgres ltree for hierarchical queries. Tree is subset of graph (one parent per node), graph has multiple parents arbitrary edges.
8. **When to use what** — Simple FAQ: Chain, Complex reasoning: ToT (3x cost, +20% success), Very complex: MCTS (50x cost, +25% success), Multi-hop QA: GraphRAG (3x query cost, +25% multi-hop), Policy enforcement: Behavior Tree (deterministic, 0.1x cost)
9. **Cost control** — Tree explores 3x more paths = 3x cost. Set max depth 5, beam width 2, branching factor 3 to bound cost. MCTS iterations 50 only for high-value tasks ($100+ value).
10. **Observability** — Log tree: thoughts generated, scores, path chosen, backtracks, depth, cost. Alert if tree depth >10 or cost >$1.00 (possible infinite branching).

---
**Bottom Line:** Chains are linear one path greedy, trees explore multiple paths, evaluate, backtrack, pick best. Tree-of-Thought: Generate k=3 thoughts each step, evaluate 1-10 with LLM, keep beam_width=2 best, BFS/DFS, max depth 5, cost 3x chain, +15-20% success on complex reasoning. MCTS: Selection via UCT, expansion, simulation rollout, backpropagation, iterations 50, cost 50x chain, +20-25% success for coding/game. Behavior Trees: Deterministic control flow with Sequence (And) and Selector (Or), Conditions and Actions, no LLM for control, mandatory for policy enforcement high-risk. Execution Trees: Task decomposition as tree/DAG with dependencies, topological sort, parallel execution. Conversation Trees: Branching context with parent_id branch_id, handles follow-ups. Knowledge Trees: Hierarchical memory with one parent per node, vs graph multiple parents arbitrary edges. Use chain default, tree for complex reasoning, MCTS for very complex, graph for multi-hop QA, behavior tree for policy enforcement. Hybrid use all together: Behavior tree for control, GraphRAG for retrieval, ToT for decision, chain for execution.

