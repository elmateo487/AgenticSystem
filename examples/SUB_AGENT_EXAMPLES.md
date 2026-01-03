# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

# SUB-AGENT INVOCATION EXAMPLES

## Authority
This document does not grant authority. It provides pattern examples only.

---

## Example 1: Feature Implementation Flow

Human requests a new feature. Orchestrator coordinates multiple agents.

### Step 1: Human Request

```
Human: "I need to add a VIP list feature for obligation classification"
```

### Step 2: Orchestrator Invokes Historian

```
You are the Obsidian Project Historian.

Task: Draft an implementation plan for adding VIP list to obligation classification.

Project: projects/notion-obligations/
```

Historian produces: `plans/active/vip_list.md`

### Step 3: Human Approves Plan

```
Human: "Plan looks good. Execute it."
```

### Step 4: Orchestrator Invokes Engineer

```
You are the Principal Software Engineer.

Task: Execute the implementation plan at plans/active/vip_list.md.

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Project: projects/notion-obligations/
```

Engineer executes plan, updates checkboxes and worklog.

### Step 5: Orchestrator Invokes Historian to Archive

```
You are the Obsidian Project Historian.

Task: Archive the completed plan vip_list.md.

Project: projects/notion-obligations/
```

Historian moves plan to archive, updates any affected docs.

---

## Example 2: Halt Escalation

Engineer encounters a blocking condition requiring human decision.

### Step 1: Engineer Halts

```
Engineer (during execution):
  "I've encountered a decision point not covered by authority.
   The classifier could use approach A or approach B.
   This requires human decision. Halting and updating worklog."

   Worklog entry:
   | 2026-01-03 | Halted at step 3: Approach A vs B needs human decision. - Engineer |
```

### Step 2: Orchestrator Invokes Notion Assistant

```
You are the Notion Personal Assistant.

Task: Propose a Notion commitment for the blocking decision between Approach A and Approach B for classifier implementation.

Project: projects/notion-obligations/
```

### Step 3: Notion Assistant Output

```
## [Next] Decide on classifier approach

**Context**: Engineer implementing VIP list feature needs decision on approach A vs B.

**Required Action**: Review both approaches and select one.

**Link**: plans/active/vip_list.md (Step 3)

**Due**: Before continuing implementation
```

### Step 4: Human Decides

Human reviews Notion item, makes decision, and records in DECISIONS.md via Historian.

### Step 5: Orchestrator Resumes Engineer

```
You are the Principal Software Engineer.

Task: Resume execution of plans/active/vip_list.md starting from step 3.

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Project: projects/notion-obligations/
```

---

## Example 3: Context Gathering

Human asks about project state. Multiple agents gather information in parallel.

### Step 1: Human Request

```
Human: "What's the current state of the notion-obligations project?"
```

### Step 2: Orchestrator Invokes Historian (Authority Analysis)

```
You are the Obsidian Project Historian.

Task: Summarize the current authority state (active invariants, recent decisions).

Project: projects/notion-obligations/
```

### Step 3: Orchestrator Checks Plan Index

Orchestrator reads `plans/PLAN_INDEX.md` directly (no agent needed for simple file read).

### Step 4: Orchestrator Synthesizes

```
Orchestrator to Human:

## Project State: notion-obligations

### Authority
- 3 active invariants (Human-Owned Processing, Source Traceability, Invocation-Only)
- 18 active decisions
- Last authority change: 2026-01-02

### Plans
- 10 active plans
- 1 on-hold plan
- Current: 027_agent_invocation_efficiency (In Progress)

### Recent Activity
- Phase 1 of efficiency improvements completed
- VIP list feature implemented
```

---

## Example 4: Documentation Update

After code changes, documentation needs updating.

### Step 1: Engineer Completes Plan

```
Engineer:
  "Plan complete. All checkboxes marked. Worklog updated.
   Note: ARCHITECTURE.md may need updating to reflect new module structure."
```

### Step 2: Orchestrator Invokes Historian

```
You are the Obsidian Project Historian.

Task: Update ARCHITECTURE.md to reflect the new VIP module structure added in plan vip_list.md.

Project: projects/notion-obligations/
```

### Step 3: Historian Updates Docs

Historian reads the plan and code, updates ARCHITECTURE.md appropriately.

---

## Token Efficiency Comparison

### Without Sub-Agent Pattern (Monolithic)

Single agent loads everything:
- Orientation: 2,000 tokens
- All authority: 6,500 tokens
- All plans: 10,000 tokens
- All code: 15,000 tokens
- **Total: ~33,500 tokens**

### With Sub-Agent Pattern

| Invocation | Agent | Tokens |
|------------|-------|--------|
| Plan draft | Historian | 3,000 |
| Execution | Engineer | 8,000 |
| Archive | Historian | 1,500 |
| **Total** | | **12,500** |

**Savings: ~63%**

---

## See Also

- `docs/SUB_AGENT_PATTERNS.md` — Pattern documentation
- `docs/PROMPT_CACHING.md` — Caching recommendations
- `docs/TOKEN_METRICS.md` — Token measurements
