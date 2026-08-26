# ContextCompiler — Master Implementation Specification

## 1. Project Objective

Build an IDE-integrated, AST-aware context optimization system for LLM-based software engineering.

The system must solve the problem of excessive and irrelevant code context being sent to LLMs.

Given a developer query such as:

> "Why is JWT authentication failing after token expiration?"

the system must:

1. Understand the query.
2. Analyze the repository structure.
3. Parse source code using ASTs.
4. Extract functions, classes, methods, imports, calls, and relationships.
5. Build a code knowledge/dependency graph.
6. Perform semantic retrieval over code entities.
7. Combine semantic retrieval with AST and dependency relationships.
8. Rank candidate code entities.
9. Select context under a configurable token budget.
10. Produce an optimized context for the LLM.
11. Call the selected LLM provider.
12. Record a complete retrieval trace.
13. Visually explain how and why files/code entities were selected or rejected.
14. Report token usage and token reduction.

The system should be designed as a reusable context engine rather than a tightly coupled IDE extension.

---

# 2. Core Architecture

Implement the system using the following logical layers:

```text
IDE Extension
      |
      v
ContextCompiler API
      |
      +---------------- Query Analyzer
      |
      +---------------- Repository Indexer
      |                    |
      |                    +-- AST Parser
      |                    +-- Code Entity Extractor
      |
      +---------------- Vector Retrieval
      |
      +---------------- Dependency Graph
      |
      +---------------- Hybrid Reranker
      |
      +---------------- Context Optimizer
      |
      +---------------- Token Counter
      |
      +---------------- Trace/Event System
      |
      +---------------- LLM Provider
      |
      v
Optimized Answer
```

Keep these components modular and independently testable.

---

# 3. Initial Technology Choices

Use:

* TypeScript for the VS Code extension.
* Python for the initial analysis/retrieval backend if this provides faster development.
* Tree-sitter or equivalent robust parser technology for multi-language AST parsing.
* ChromaDB for the initial vector store.
* HNSW-compatible vector retrieval.
* A configurable embedding provider.
* A configurable LLM provider.
* NetworkX or an equivalent lightweight graph representation for the first dependency graph implementation.
* REST or another clearly defined local API between the VS Code extension and backend.

Do not introduce Neo4j, Kubernetes, Kafka, Redis, or other infrastructure unless a real requirement emerges.

Prioritize a simple local-first architecture.

---

# 4. Repository Structure

Create a clean monorepo approximately like:

```text
contextcompiler/
│
├── extension/
│   └── vscode/
│
├── backend/
│   ├── api/
│   ├── parser/
│   ├── indexer/
│   ├── retrieval/
│   ├── graph/
│   ├── ranking/
│   ├── optimizer/
│   ├── tracing/
│   ├── llm/
│   └── models/
│
├── storage/
│   ├── vector/
│   └── graph/
│
├── evaluation/
│
├── tests/
│
├── docs/
│
└── README.md
```

Keep the exact structure flexible when there is a strong engineering reason to change it, but preserve separation of concerns.

---

# 5. Phase 1 — Repository Indexing

Implement repository indexing.

Requirements:

* Detect supported source files.
* Ignore node_modules, .git, build directories, virtual environments, caches, and configurable ignored paths.
* Parse supported source files.
* Extract file metadata.
* Generate stable identifiers for code entities.
* Store source locations using file path, start line, end line, and entity type.

Initial Python entities:

```text
module
class
function
method
import
function call
```

Create a normalized internal representation.

Example:

```json
{
  "id": "auth.py::authenticate_user",
  "file": "auth.py",
  "type": "function",
  "name": "authenticate_user",
  "start_line": 20,
  "end_line": 45,
  "language": "python"
}
```

Make the model extensible for other languages.

---

# 6. Phase 2 — AST Relationship Extraction

Extract relationships such as:

```text
CALLS
IMPORTS
DEFINES
INHERITS
REFERENCES
```

For example:

```text
login()
  CALLS authenticate_user()

authenticate_user()
  CALLS UserRepository.find_user()

middleware.py
  CALLS validate_token()
```

Store relationships in a graph abstraction.

The graph implementation must be independent of the visualization layer.

---

# 7. Phase 3 — Semantic Code Retrieval

Create semantic embeddings for code entities.

Do not initially embed entire repositories as one document.

Prefer entity/chunk-level indexing.

Metadata must include:

```text
entity_id
file
language
entity_type
name
start_line
end_line
```

Implement:

```text
index()
search(query, top_k)
delete()
update()
```

Support incremental indexing where possible.

Do not re-index unchanged files unnecessarily.

---

# 8. Phase 4 — Hybrid Retrieval

Implement a hybrid retrieval pipeline.

Input:

```text
user_query
repository
```

Output:

```text
ranked_candidate_entities
```

Combine:

1. Semantic similarity.
2. Lexical relevance.
3. AST structural relevance.
4. Dependency relevance.

Use a configurable scoring function.

Conceptually:

```text
final_score =
    semantic_weight * semantic_score
    + lexical_weight * lexical_score
    + ast_weight * ast_score
    + dependency_weight * dependency_score
```

Keep the weights configurable.

Do not claim that the chosen weights are optimal.

Create tests for each scoring component independently.

---

# 9. Phase 5 — Dependency Expansion

After initial semantic retrieval:

1. Select high-confidence candidates.
2. Traverse relevant dependency relationships.
3. Retrieve callers/callees/import relationships.
4. Add structurally relevant entities.
5. Re-rank the expanded candidate set.

Support configurable graph traversal depth.

Example:

```text
depth = 0
Only directly retrieved entity.

depth = 1
Direct callers/callees.

depth = 2
Second-level dependencies.
```

Do not blindly retrieve the entire connected component.

---

# 10. Phase 6 — Context Optimizer

Implement a token-budget-aware context optimizer.

Input:

```text
candidate_entities
token_budget
user_query
```

Output:

```text
selected_context
```

Each candidate should contain:

```text
entity
token_count
semantic_score
ast_score
dependency_score
final_score
```

The optimizer must maximize contextual usefulness subject to a token budget.

Conceptually:

```text
maximize contextual relevance

subject to:

sum(selected_entity_tokens) <= token_budget
```

Start with a deterministic greedy strategy.

Then design the optimizer so more sophisticated strategies can be evaluated later.

Do not prematurely introduce machine learning for this component.

---

# 11. Phase 7 — Context Compression

Implement optional context compression.

Compression must never modify the user's source code.

The compressed representation may contain:

* signatures
* relevant function bodies
* relevant classes
* dependency metadata
* selected comments/docstrings
* concise structural summaries

Support configurable modes:

```text
full
balanced
compressed
```

Always preserve source locations so the UI can navigate back to the original source.

---

# 12. Phase 8 — Token Accounting

Implement reliable token accounting.

Track:

```text
original candidate tokens
selected context tokens
compressed context tokens
final prompt tokens
LLM output tokens
total tokens
estimated cost
```

The system must expose:

```text
token_reduction_percentage
```

Never fabricate token counts.

Use the tokenizer appropriate to the selected LLM where possible.

---

# 13. Phase 9 — Retrieval Trace

Create a structured event system.

Events should include:

```text
query_received
query_analyzed
repository_scan_started
repository_scan_completed
semantic_search_started
candidate_retrieved
ast_relationship_found
dependency_expansion_started
candidate_reranked
candidate_rejected
candidate_selected
context_compressed
context_budget_applied
llm_request_started
llm_request_completed
```

Every event should contain enough metadata to explain the decision.

Example:

```json
{
  "event": "candidate_selected",
  "entity_id": "jwt.py::validate_token",
  "semantic_score": 0.89,
  "ast_score": 0.96,
  "dependency_score": 0.94,
  "final_score": 0.93,
  "token_count": 520,
  "reason": "Direct dependency of middleware authentication flow"
}
```

Do not expose sensitive source contents in logs by default.

---

# 14. Phase 10 — Explainability

For every selected entity, support:

```text
Why was this selected?
```

Possible explanations:

```text
High semantic similarity
Direct dependency
Called by a selected function
Imported by a selected module
Matches query terminology
Required to resolve a dependency
Fits remaining token budget
```

For rejected entities support:

```text
Why was this rejected?
```

Possible explanations:

```text
Low relevance
Duplicate information
Outside token budget
Weak dependency relationship
Low semantic similarity
```

The explanation must be derived from actual retrieval metadata.

Never generate a fictional explanation with an LLM.

---

# 15. Phase 11 — Visualization

Build a VS Code Context Trace panel.

The visualization should contain:

## Query section

Display the developer's query.

## Pipeline section

Visualize:

```text
Query
 ↓
Semantic Retrieval
 ↓
AST Analysis
 ↓
Dependency Expansion
 ↓
Hybrid Ranking
 ↓
Context Optimization
 ↓
LLM
```

## Candidate section

Display:

```text
File/entity
semantic score
AST score
dependency score
final score
token count
selection status
```

## Dependency graph

Display relevant code entities and relationships.

Use visual states:

```text
candidate
selected
rejected
dependency
```

Do not rely exclusively on color. Include text/status indicators for accessibility.

## Decision details

Clicking a node must display:

```text
Entity
File
Lines
Scores
Token count
Selection status
Reason
```

## Token summary

Display:

```text
Original context
Optimized context
Tokens saved
Reduction %
```

---

# 16. Phase 12 — VS Code Integration

Create commands:

```text
ContextCompiler: Ask AI
ContextCompiler: Explain Selection
ContextCompiler: Show Context Trace
ContextCompiler: Re-index Repository
ContextCompiler: Configure Token Budget
```

The user should be able to select code and ask a question.

Support:

```text
current selection
current file
repository
```

as context scopes.

Do not send the repository to the LLM automatically.

---

# 17. Phase 13 — LLM Provider Abstraction

Create:

```text
LLMProvider
```

with methods similar to:

```text
generate()
stream()
estimate_cost()
```

Support at least one provider initially.

Design the interface so other providers can be added without changing retrieval code.

The LLM must receive only the optimized context.

---

# 18. Phase 14 — Evaluation Framework

Create a benchmark framework.

Each benchmark case should contain:

```text
repository
question
expected relevant files/entities
expected answer characteristics
```

Compare:

```text
Full Context
Naive Vector RAG
AST Retrieval
Hybrid Retrieval
Hybrid + Token Optimization
```

Measure:

```text
retrieval precision
retrieval recall
MRR
nDCG
input tokens
output tokens
token reduction
latency
cost
answer correctness
code correctness
```

Create machine-readable experiment results.

Do not hard-code expected performance.

---

# 19. Phase 15 — Research Experiments

The project should eventually test these hypotheses:

### H1

AST-aware retrieval reduces irrelevant code context compared with semantic-only RAG.

### H2

Combining semantic similarity with dependency relationships improves retrieval quality.

### H3

Token-budget-aware context selection reduces LLM input tokens while maintaining or improving answer quality.

### H4

Retrieval trace visualization improves developer understanding of AI context selection.

Design experiments to validate or reject these hypotheses.

Do not assume the hypotheses are true.

---

# 20. Engineering Requirements

Follow these rules throughout implementation:

* Strong typing.
* Modular architecture.
* Unit tests for core algorithms.
* Integration tests for retrieval.
* Deterministic components wherever possible.
* Structured logging.
* Configuration through environment/config files.
* No hard-coded API keys.
* No unnecessary external services.
* No repository source code sent externally unless explicitly required by the configured LLM/embedding provider.
* Make privacy behavior clear to users.
* Handle malformed source files gracefully.
* Handle unsupported languages gracefully.
* Handle empty repositories.
* Handle very large repositories.
* Support incremental indexing.
* Cache embeddings.
* Avoid unnecessary LLM calls.
* Do not use an LLM when deterministic AST analysis can solve the problem.
* Keep the visualization separate from retrieval logic.

---

# 21. Implementation Strategy

Do not implement all phases simultaneously.

Implement one phase at a time.

After each phase:

1. Compile the project.
2. Run tests.
3. Add missing tests.
4. Demonstrate the feature.
5. Update documentation.
6. Record architectural decisions.
7. Only then continue to the next phase.

At every stage, preserve working functionality.

Do not rewrite working components unnecessarily.

---

# 22. First Deliverable

Start ONLY with:

```text
Phase 1:
Repository setup
+
basic indexing
+
AST entity extraction
+
normalized entity model
+
unit tests
```

Do not implement:

* LLM integration
* vector database
* dependency graph
* visualization
* token optimization

until the initial indexing layer is working and tested.

At the end of Phase 1, provide:

1. Repository structure.
2. Implementation summary.
3. Files created.
4. How to run it.
5. Tests written.
6. Example AST/entity output.
7. Known limitations.
8. Recommended next phase.

Then wait for approval before implementing the next phase.
