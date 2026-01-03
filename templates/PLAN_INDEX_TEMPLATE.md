# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

## Template
Copy into a project and fill in. Do not edit templates in-place.

# PLAN INDEX

Generated: <YYYY-MM-DD>

## Authority
This document does not grant authority. It provides navigation only.

---

## Active Plans

| Plan | Objective | Status | Last Modified |
|------|-----------|--------|---------------|
| <plan_number>_<plan_name> | <Brief objective> | <In Progress/Ready> | <YYYY-MM-DD> |

## On-Hold Plans

| Plan | Reason | Since |
|------|--------|-------|
| <plan_number>_<plan_name> | <Why on hold> | <YYYY-MM-DD> |

(If none, write: "(none)")

## Recently Archived

| Plan | Completed | Outcome |
|------|-----------|---------|
| <plan_number>_<plan_name> | <YYYY-MM-DD> | <Success/Abandoned/Superseded> |

(Show last 5 archived plans)

---

## Plan Lifecycle

```
plans/active/     → In progress or ready for execution
plans/on-hold/    → Paused pending decisions/resources
plans/archive/    → Completed or abandoned
```

## Generation

This index can be generated via:

```bash
# Manual: Review plans directory and update index
ls plans/active/ plans/on-hold/ plans/archive/

# Or script-assisted (see PLAN_INDEX_GENERATION.md)
python scripts/generate_plan_index.py plans/ > plans/PLAN_INDEX.md
```

Regenerate when:
- New plan created
- Plan archived
- Plan moved to/from on-hold
- Plan status changes significantly
