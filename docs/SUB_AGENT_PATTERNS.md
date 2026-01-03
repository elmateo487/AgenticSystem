# SUB-AGENT PATTERNS

## Authority
This document does not grant authority. It provides architectural guidance only.

---

## Purpose

This document describes patterns for using sub-agents (nested agent invocations) in SYSTEM V1.2 while maintaining efficiency and auditability.

---

## When to Use Sub-Agents

### Good Use Cases

1. **Complex multi-phase work**: Plan requires both documentation and code changes
2. **Specialized expertise**: Different phases need different agent capabilities
3. **Parallel analysis**: Gather context from multiple sources simultaneously

### When NOT to Use Sub-Agents

1. **Simple tasks**: Single-phase work that one agent can complete
2. **Token overhead**: Sub-agent invocation has fixed cost (~500-1000 tokens each)
3. **Context sharing**: Information would need to pass through Orchestrator

---

## Sub-Agent Architecture

```
Orchestrator (minimal context)
  |
  +-- Agent A (scoped context)
  |     Returns: Condensed result
  |
  +-- Agent B (scoped context)
        Returns: Condensed result
```

### Key Principles

1. **Each invocation is explicit**: No implicit agent chaining
2. **Each agent has scoped context**: Load only what that agent needs
3. **Parent receives condensed result**: Not full context
4. **Audit trail via files**: Inter-agent handoffs through files, not conversation

---

## Pattern 1: Sequential Specialization

Use when different phases require different agent expertise.

### Example: Feature Implementation

```
Human: "Implement the new API endpoint"

Orchestrator:
  1. Invoke Historian to draft implementation plan
     Input: Feature requirements
     Output: plans/active/new_api_endpoint.md

  2. Human approves plan

  3. Invoke Engineer to execute plan
     Input: plans/active/new_api_endpoint.md
     Output: Code changes, tests, worklog updates

  4. Invoke Historian to archive plan
     Input: Completed plan
     Output: Plan moved to archive, docs updated
```

### Token Efficiency

| Phase | Agent | Context Loaded | Est. Tokens |
|-------|-------|----------------|-------------|
| Planning | Historian | Orientation + authority | 2,000 |
| Execution | Engineer | Orientation + plan + code | 5,000 |
| Archival | Historian | Orientation + plan | 1,500 |
| **Total** | | | **8,500** |

vs. Single Agent (everything): ~15,000-20,000 tokens

---

## Pattern 2: Parallel Analysis

Use when gathering information from multiple independent sources.

### Example: Context Gathering

```
Human: "What's the current state of the project?"

Orchestrator (parallel):
  1. Invoke Historian to summarize authority state
     Input: authority/
     Output: Summary of invariants and decisions

  2. Invoke Engineer to summarize code state (read-only)
     Input: src/, tests/
     Output: Summary of implementation status

Orchestrator:
  3. Synthesize results for human
```

### Token Efficiency

Each agent loads only its relevant context. Results are summarized before returning to Orchestrator.

---

## Pattern 3: Scoped Delegation

Use when part of a task requires specialized handling.

### Example: Halt Escalation

```
Engineer executing plan:
  - Encounters blocking condition
  - Cannot resolve within authority
  - Needs human decision

Engineer:
  1. Document blocker in worklog
  2. Request Orchestrator invoke Notion Assistant

Orchestrator:
  3. Invoke Notion Assistant
     Input: Blocker description
     Output: Proposed Notion commitment

---

## Anti-Patterns

### Anti-Pattern 1: Context Relay

**Wrong**: Orchestrator reads files, summarizes, passes to agent

```
Orchestrator:
  - Reads INVARIANTS.md (1,500 tokens)
  - Reads DECISIONS.md (5,000 tokens)
  - Summarizes in prompt to Engineer (2,000 tokens)
Engineer:
  - Receives summary
  - Reads INVARIANTS.md again anyway
  - Reads DECISIONS.md again anyway
```

**Problem**: Double token usage, summary may misrepresent

**Correct**: Orchestrator invokes with minimal prompt, agent reads files directly

### Anti-Pattern 2: Implicit Context Sharing

**Wrong**: Historian provides recommendations in chat, Engineer reads chat

```
Historian (in conversation):
  "I recommend using approach X because..."
Engineer (in same conversation):
  - Reads chat history
  - Acts on Historian's recommendation
```

**Problem**: Violates artifact boundary rules, no audit trail

**Correct**: Historian writes to files, Engineer reads from files

### Anti-Pattern 3: Micro-Invocation

**Wrong**: Multiple sub-agent calls for trivial tasks

```
Orchestrator:
  1. Invoke Historian to check INVARIANTS.md
  2. Invoke Historian to check DECISIONS.md
  3. Invoke Historian to draft one paragraph
```

**Problem**: Each invocation has ~500-1000 token overhead

**Correct**: Single invocation with clear scope

---

## Invocation Overhead

Each sub-agent invocation has fixed costs:

| Component | Est. Tokens |
|-----------|-------------|
| Agent identity prompt | ~50 |
| Orientation file (Tier 1) | ~800-1000 |
| Task description | ~50-100 |
| Response formatting | ~100-200 |
| **Minimum per invocation** | **~1,000-1,350** |

Use sub-agents when: Task scope justifies overhead
Avoid sub-agents when: Task can be done in current context

---

## Best Practices

1. **Minimal invocation prompts**: Agent reads its own spec
2. **File-based handoffs**: Inter-agent communication via files
3. **Scoped context loading**: Each agent loads only what it needs
4. **Clear task boundaries**: One clear objective per invocation
5. **Audit trail**: All actions traceable to files + invocation

---

## V1.2 Alignment

Sub-agent patterns preserve all SYSTEM V1.2 principles:

- **Invocation-only**: Each sub-agent invoked explicitly
- **Fresh context**: Each sub-agent loads current state
- **Auditability**: All handoffs via version-controlled files
- **Documentation as source of truth**: Agents read from files, not conversation
- **No autonomy**: Orchestrator dispatches, does not decide