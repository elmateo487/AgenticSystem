# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

# SYSTEM V1.2 — LLM Implementation Orientation

## What you are building
You are implementing signal ingestion + human-invoked workflows.
You are not building an autonomous assistant.

## Invocation rule
All actions occur only when explicitly invoked by a human.

## Prohibited
No polling loops, no background watchers, no self-scheduling, no silent state changes.

## Outputs
- Proposed Notion commitments (copy/paste ready)
- Documentation updates (Historian only, when invoked)
- Code + tests (Engineer only, when invoked)

## Agent Invocation Protocol (Mandatory)

Before any agent executes work, it **must** read its orientation file.

**V1.2 Fast Path**: Read one orientation file per role:
- `system/v1.2/orientation/<ROLE>_ORIENTATION.md`

See: `templates/AGENT_INVOCATION_PROTOCOL.md` for full protocol.

**Key requirement**: When invoking an agent (including subagents), the invocation prompt must explicitly instruct the agent to read:
1. Its orientation file (`orientation/<ROLE>_ORIENTATION.md`)
2. Relevant project authority files
3. The active plan (if executing)

Agents that execute without reading their orientation are operating blind and may violate SYSTEM V1.2 constraints.
