# SYSTEM V1.3

**Beads-Integrated Invocation-Only Agent Architecture**

## Overview

SYSTEM V1.3 is an agent coordination framework where:
- **Nothing runs unless explicitly invoked by a human**
- **Tests define correctness**
- **Tests are sacrosanct**
- **Implementation quality is sacrosanct**

V1.3 integrates Beads for task management, replacing file-based plans with convoy issues.

## Quick Start

### 1. Understand the Agents

| Agent | Purpose | Invocation |
|-------|---------|------------|
| **Orchestrator** | Dispatches work to other agents | Main Claude instance |
| **Historian** | Creates plans (convoys), maintains authority docs | `/historian` skill |
| **Engineer** | Executes approved plans, writes code | `/engineer` skill |

### 2. Authority Model

Authority lives in **files**, not Beads:

```
project/
  authority/
    INVARIANTS.md    # Non-negotiable constraints
    DECISIONS.md     # Design decisions with rationale
```

Plans live in **Beads** as convoy issues that cite authority documents.

### 3. Typical Workflow

```
Human: "Create a plan for feature X"
  Orchestrator invokes Historian
  Historian creates convoy in Beads (status: draft, then pending_approval)

Human reviews and approves:
  bd update bd-XYZ --status approved --label authority:granted
Human: "Execute plan X"
  Orchestrator invokes Engineer
  Engineer verifies authority, claims tasks, executes, proves criteria
  Engineer moves convoy to pending_human_approval

Human reviews and completes:
  bd update bd-XYZ --status completed
```

## Key Concepts

### Convoys and Tasks

- **Convoy**: A plan (parent issue) with authority citations
- **Tasks**: Child issues under a convoy
- **Authority**: Granted via `authority:granted` label by humans only

### States

| State | Meaning |
|-------|---------|
| `draft` | Plan being created |
| `pending_approval` | Awaiting human review |
| `approved` | Human granted authority |
| `in_progress` | Work underway |
| `suspended` | Authority revoked (mutation detected) |
| `halted` | Engineer blocked, needs guidance |
| `pending_human_approval` | Work done, awaiting human sign-off |
| `completed` | Human approved completion |

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/BEADS_INTEGRATION.md` | Full V1.3 design specification |
| `orientation/*.md` | Agent quick-reference guides |
| `agents/*.md` | Full agent specifications |
| `templates/*.md` | Authority document templates |

## Requirements

- Beads v0.42.0+
- Claude Code with `/historian` and `/engineer` skills configured

## Migration from V1.2

V1.3 replaces file-based plans (`plans/active/*.md`) with Beads convoys. Authority documents remain file-based. See `MIGRATION_PLAN.md` for details.

