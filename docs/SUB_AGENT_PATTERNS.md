# SUB-AGENT PATTERNS

## Authority
This document does not grant authority. It provides architectural guidance only.

---

## Purpose

This document describes patterns for using sub-agents (nested agent invocations) in SYSTEM V1.3 while maintaining efficiency and auditability.

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
  +-- Historian (scoped context)
  |     Returns: Beads convoy created, file written
  |
  +-- Engineer (scoped context)
        Returns: Tasks completed, tests passing
```

### Key Principles

1. **Each invocation is explicit**: No implicit agent chaining
2. **Each agent has scoped context**: Load only what that agent needs
3. **Parent receives condensed result**: Not full context
4. **Audit trail via Beads + files**: Inter-agent handoffs through Beads issues and files

---

## Pattern 1: Sequential Specialization

Use when different phases require different agent expertise.

### Example: Feature Implementation

```
Human: "Implement the new API endpoint"

Orchestrator:
  1. Invoke Historian to draft implementation plan
     Input: Feature requirements
     Output: Beads convoy bd-XYZ (status: pending_approval)

  2. Human approves plan
     bd update bd-XYZ --status approved --label authority:granted

  3. Invoke Engineer to execute plan
     Input: Convoy bd-XYZ
     Output: Code changes, tests, Beads comments

  4. Engineer requests completion approval
     bd update bd-XYZ --status pending_human_approval

  5. Human approves completion
     bd update bd-XYZ --status completed
```

### Token Efficiency

| Phase | Agent | Context Loaded | Est. Tokens |
|-------|-------|----------------|-------------|
| Planning | Historian | Orientation + authority | 2,000 |
| Execution | Engineer | Orientation + convoy + code | 5,000 |
| **Total** | | | **7,000** |

vs. Single Agent (everything): ~15,000-20,000 tokens

---

## Pattern 2: Parallel Analysis

Use when gathering information from multiple independent sources.

### Example: Context Gathering

```
Human: "What's the current state of the project?"

Orchestrator (parallel):
  1. Query Beads for convoy status
     bd list --type convoy --label "authority:granted"

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
  - Encounters test failure
  - Cannot resolve without modifying test or degrading implementation
  - Needs human decision

Engineer:
  1. HALT the convoy
     bd update bd-XYZ --status halted --label halted:test-conflict
     bd comment bd-XYZ "HALTED: test_X fails. Need guidance."

Orchestrator:
  2. Surface halt to human
  3. Wait for human decision
```

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

**Correct**: Historian writes to Beads/files, Engineer reads from Beads/files

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

### Anti-Pattern 4: Orchestrator Writes to Beads

**Wrong**: Orchestrator creates or updates Beads issues directly

```
Orchestrator:
  bd create "New task" --parent bd-XYZ  # VIOLATION
```

**Problem**: Violates Orchestrator boundary (dispatcher, not executor)

**Correct**: Orchestrator invokes Historian to create, Engineer to update

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
2. **Beads + file-based handoffs**: Inter-agent communication via Beads and files
3. **Scoped context loading**: Each agent loads only what it needs
4. **Clear task boundaries**: One clear objective per invocation
5. **Audit trail**: All actions traceable to Beads issues + files + invocation
6. **Skills for invocation**: Always use Skill tool, never manual Task prompts

---

## V1.3 Alignment

Sub-agent patterns preserve all SYSTEM V1.3 principles:

- **Invocation-only**: Each sub-agent invoked explicitly
- **Fresh context**: Each sub-agent loads current state
- **Auditability**: All handoffs via Beads issues and version-controlled files
- **Tests are sacrosanct**: Engineer halts rather than modifying tests
- **No autonomy**: Orchestrator dispatches, does not decide
