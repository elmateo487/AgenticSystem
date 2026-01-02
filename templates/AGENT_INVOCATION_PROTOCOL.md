# SYSTEM V1.2 — Agent Invocation Protocol

## Authority
This document grants authority.

---

## Purpose

This protocol ensures that agents always operate within their defined constraints by requiring them to read their specification files before execution.

**V1.2 Update**: Introduces orientation files for faster onboarding with tiered loading.

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

When invoking an agent (whether in main context or as a subagent), the invocation prompt should include:

```
You are the [Agent Name] for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/[ROLE]_ORIENTATION.md

Then read project context:
- projects/[project]/AUTHORITY.md
- projects/[project]/plans/active/[plan].md (if executing)

Execute: [task description]

Halt and surface to the human if:
- Authority is missing or unclear
- Plan scope is ambiguous
- Tests fail or are missing
```

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

- **v1.2**: Added orientation files and tiered loading pattern for faster onboarding
- **v1.1**: Initial protocol creation to address agents executing without reading their spec files
