# SYSTEM V1.2 — Agent Invocation Protocol

## Authority
This document grants authority.

---

## Purpose

This protocol ensures that agents always operate within their defined constraints by requiring them to read their specification files before execution.

**V1.2 Update**: Introduces orientation files for faster onboarding with tiered loading.

**V1.2.1 Update**: Clarifies that invocations provide context, not instructions. Agents determine their actions from their orientation files and authority documents.

---

## Core Principle: Context, Not Instructions

**Invocations provide context. Agents determine actions.**

When invoking an agent, the invocation should tell the agent:
- **What state** exists (which plan, what happened, where to look)
- **NOT what to do** (the agent reads its orientation to determine actions)

The agent's orientation file defines its responsibilities. The agent reads authority documents to understand what actions are required. The invocation merely provides the context for the agent to apply its documented responsibilities.

### Why This Matters

1. **Single source of truth**: Agent responsibilities live in orientation files, not scattered across invocations
2. **Consistency**: The same event always triggers the same response, regardless of who invokes
3. **Auditability**: What an agent does is traceable to its documentation, not to ad-hoc instructions
4. **Reduced errors**: No risk of forgetting steps when invoking — the agent knows its job

---

## V1.2 Fast Path (Recommended)

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

Then read project context as specified in the orientation file.

---

## V1.2 Invocation Syntax

When invoking an agent (whether in main context or as a subagent), the invocation prompt should provide **context only**:

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

**Note**: The invocation does NOT tell the agent what to do. The agent reads its orientation file to determine its responsibilities given the provided context.

### Engineer Invocation (File-Only Directive)

When invoking the Engineer, add the file-only directive to enforce artifact boundaries:

```
You are the Principal Software Engineer.

Task: [task description]

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Project: projects/<project>/
Working directory: [working directory]
```

This ensures the Engineer reads only from files and ignores any prior conversation context from other agents (e.g., Historian chat output).

---

## Tiered Loading Pattern

### Tier 1 — Always Read
- Role-specific orientation file
- Takes <10 seconds

### Tier 2 — Read on Demand
- Full templates in `system/v1.2/templates/` — When creating documents
- Full agent specs in `system/v1.2/agents/` — If constraints unclear
- Examples in `system/v1.2/examples/` — When patterns needed

### Tier 3 — Project Context
- `projects/<project>/AUTHORITY.md`
- `projects/<project>/plans/active/<plan>.md`
- `projects/<project>/authority/INVARIANTS.md`
- `projects/<project>/authority/DECISIONS.md`

---

## Agent-Specific Requirements

| Agent | Orientation File | Additional Tier 2/3 |
|-------|------------------|---------------------|
| Historian | `HISTORIAN_ORIENTATION.md` | Templates when creating documents |
| Engineer | `ENGINEER_ORIENTATION.md` | Active plan and authority docs |
| Notion Assistant | `NOTION_ASSISTANT_ORIENTATION.md` | INVARIANTS.md for commitment boundaries |
| Orchestrator | `ORCHESTRATOR_ORIENTATION.md` | None (reads only for context) |

---

## V1.1 Full Path (Backward Compatible)

For situations requiring full context, the V1.1 protocol remains valid:

### Step 1: System Context
1. `system/v1.2/INDEX.md`
2. `system/v1.2/LLM_IMPLEMENTATION_ORIENTATION.md`

### Step 2: Agent Specification
3. `system/v1.2/agents/<AGENT_NAME>_AGENT.md`

### Step 3: Project Context (if applicable)
4. `projects/<project>/AUTHORITY.md`
5. Active plan: `projects/<project>/plans/active/<plan>.md`

---

## Invocation Examples: Correct vs Incorrect

### Example 1: Plan Completion

**INCORRECT** (provides instructions):
```
Historian: Plan 001 is complete.

Please do the following:
1. Verify all checkboxes are marked complete
2. Move the plan from active/ to archive/
3. Update DECISIONS.md if any new decisions were made
4. Create a completion summary
```

**CORRECT** (provides context only):
```
Historian: Plan projects/notion-obligations/plans/active/001-initial-setup.md is complete.

Context: The Engineer has marked all checkboxes complete and tests pass.
```

The Historian reads its orientation file to determine what to do when a plan completes. The invoker does not need to specify the steps.

---

### Example 2: Engineer Execution

**INCORRECT** (provides instructions):
```
Engineer: Execute plan 001.

Steps to follow:
1. Read the plan
2. Verify authority
3. Execute each step in order
4. Run tests after each step
5. Update checkboxes
6. Update worklog
```

**CORRECT** (provides context only):
```
Engineer: Execute plan projects/notion-obligations/plans/active/001-initial-setup.md

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.
```

The Engineer knows from its orientation file that it must verify authority, execute steps in order, run tests, and update checkboxes/worklog.

---

### Example 3: Historian Plan Creation

**INCORRECT** (provides instructions):
```
Historian: Create a plan for adding OAuth support.

Include these sections:
- Objective
- Authority citations
- Ordered work with checkboxes
- Validation checklist
- Worklog
```

**CORRECT** (provides context only):
```
Historian: Create an implementation plan for adding OAuth support.

Context:
- Project: projects/notion-obligations/
- Relevant decision: DECISIONS.md#2026-01-01-authentication-strategy
```

The Historian knows from its orientation file (and templates) the required structure for implementation plans.

---

### Example 4: Post-Execution Documentation Update

**INCORRECT** (provides instructions):
```
Historian: The OAuth feature is implemented.

Please:
1. Update ARCHITECTURE.md to reflect the new OAuth flow
2. Add a decision entry for the token storage approach we used
3. Update PIPELINE.md with the new authentication stage
```

**CORRECT** (provides context only):
```
Historian: OAuth implementation is complete.

Context:
- Project: projects/notion-obligations/
- Completed plan: plans/archive/003-oauth-implementation.md
- Changes made: New auth module in src/auth/, token storage in src/storage/
```

The Historian reads the completed plan and determines what documentation updates are needed based on its responsibilities.

---

### Key Differences

| Aspect | Incorrect Pattern | Correct Pattern |
|--------|-------------------|-----------------|
| Instructions | Explicit task list | None |
| Context | Minimal | Detailed state description |
| Responsibility source | Invocation prompt | Orientation file |
| Consistency | Varies by invoker | Always the same |
| Auditability | Scattered across invocations | Centralized in docs |

---

## Verification

Before an agent begins execution, it should be able to answer:

1. What agent am I?
2. What are my boundaries?
3. What authority documents govern my work?
4. What plan am I executing (if applicable)?
5. What are my halt conditions?

If any answer is unclear, **halt and ask**.

---

## Violations

Failure to follow this protocol results in:
- Agent may operate outside its defined constraints
- Authority may be violated or invented
- Work may need to be discarded and re-executed

---

## Changelog

- **v1.2.1**: Added "Context, Not Instructions" principle and invocation examples (correct vs incorrect patterns)
- **v1.2**: Added orientation files and tiered loading pattern for faster onboarding
- **v1.1**: Initial protocol creation to address agents executing without reading their spec files
