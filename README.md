# SYSTEM V1.3

**Beads-Integrated Invocation-Only Agent Architecture**

## Overview

SYSTEM V1.3 is an agent coordination framework where:
- **Nothing runs unless explicitly invoked by a human**
- **Tests define correctness**
- **Tests are sacrosanct**
- **Implementation quality is sacrosanct**

V1.3 integrates Beads for task management, replacing file-based plans with epic issues.

## Quick Start

### 1. Understand the Agents

| Agent | Purpose | Invocation |
|-------|---------|------------|
| **Orchestrator** | Dispatches work to other agents | Main Claude instance |
| **Historian** | Creates plans (epics), maintains authority docs | `/historian` skill |
| **Engineer** | Executes plans, writes code | `/engineer` skill |

### 2. Authority Model

**Human invocation is the authority.** When you invoke an agent, that is the authorization.

Authority documents live in files:

```
project/
  authority/
    INVARIANTS.md    # Non-negotiable constraints
    DECISIONS.md     # Design decisions with rationale
```

Plans live in **Beads** as epic issues that cite authority documents.

### 3. Typical Workflow

```
Human: "Create a plan for feature X"
  Orchestrator invokes Historian
  Historian creates epic in Beads

Human: "Execute plan X"
  Orchestrator invokes Engineer
  Engineer executes tasks, proves criteria
```

## Documentation

| Document | Purpose |
|----------|---------|
| `docs/BEADS_INTEGRATION.md` | Full V1.3 design specification |
| `~/.claude/skills/` | Agent skills (engineer, historian, orchestrator) |
| `templates/*.md` | Authority document templates |

## Requirements

- Beads v0.42.0+
- Claude Code with `/historian` and `/engineer` skills configured

## Migration from V1.2

V1.3 replaces file-based plans (`plans/active/*.md`) with Beads epics. Authority documents remain file-based. See `MIGRATION_PLAN.md` for details.
