# SYSTEM V1.2 — Agent Invocation Protocol

## Authority
This document grants authority.

---

## Core Principle: Context, Not Instructions

**Invocations provide context. Agents determine actions.**

When invoking an agent, tell it:
- **What state** exists (which plan, what happened, where to look)
- **NOT what to do** (the agent reads its orientation to determine actions)

**Why This Matters**:
- Single source of truth: Responsibilities live in orientation files
- Consistency: Same event always triggers same response
- Auditability: Actions traceable to documentation, not ad-hoc instructions
- Reduced errors: No risk of forgetting steps

---

## V1.2 Fast Path

When invoking **any** agent, read ONE orientation file:

```
system/v1.2/orientation/<ROLE>_ORIENTATION.md
```

| Agent | Orientation File |
|-------|------------------|
| Obsidian Project Historian | `HISTORIAN_ORIENTATION.md` |
| Principal Software Engineer | `ENGINEER_ORIENTATION.md` |
| Notion Personal Assistant | `NOTION_ASSISTANT_ORIENTATION.md` |
| Orchestrator | `ORCHESTRATOR_ORIENTATION.md` |

---

## V1.2 Invocation Syntax

```
You are the [Agent Name] for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/[ROLE]_ORIENTATION.md

Context:
- Project: projects/[project]/
- [State description: what happened, what exists, what changed]

Halt and surface to the human if:
- Authority is missing or unclear
- Scope is ambiguous
- You encounter a halt condition
```

**Note**: The invocation does NOT tell the agent what to do. The agent determines its responsibilities from its orientation file.

---

## Tiered Loading Pattern

| Tier | What | When |
|------|------|------|
| Tier 1 | Orientation file | Always |
| Tier 2 | Templates, agent specs, examples | On demand |
| Tier 3 | AUTHORITY.md, active plan, authority docs | Project work |

---

## Agent Requirements

| Agent | Orientation | Additional (Tier 2/3) |
|-------|-------------|----------------------|
| Historian | `HISTORIAN_ORIENTATION.md` | Templates when creating documents |
| Engineer | `ENGINEER_ORIENTATION.md` | Active plan and authority docs |
| Notion Assistant | `NOTION_ASSISTANT_ORIENTATION.md` | authority/INVARIANTS.md |
| Orchestrator | `ORCHESTRATOR_ORIENTATION.md` | None (reads for context only) |

---

## Invocation Examples

### Correct: Context Only

```
Historian: Plan projects/notion-obligations/plans/active/001-initial-setup.md is complete.

Context: The Engineer has marked all checkboxes complete and tests pass.
```

### Incorrect: Provides Instructions

```
Historian: Plan 001 is complete.

Please do the following:
1. Verify all checkboxes are marked complete
2. Move the plan from active/ to archive/
3. Update DECISIONS.md if any new decisions were made
```

The Historian reads its orientation to determine what to do when a plan completes. The invoker does not specify steps.

> For more examples, see `examples/INVOCATION_PATTERNS_EXAMPLE.md`

---

## Verification

Before execution, an agent should answer:

1. What agent am I?
2. What are my boundaries?
3. What authority documents govern my work?
4. What plan am I executing (if applicable)?
5. What are my halt conditions?

If any answer is unclear, **halt and ask**.

---

## Violations

Failure to follow this protocol may result in:
- Agent operating outside defined constraints
- Authority violations
- Work that must be discarded and re-executed
