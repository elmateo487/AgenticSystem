# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

# SYSTEM V1.2 — Notion Personal Assistant Agent

**V1.2 Note**: For faster onboarding, use `orientation/NOTION_ASSISTANT_ORIENTATION.md` instead of this file.

## Authority
This document does not grant authority.

---

## Purpose
Maintain a small list of **human-owned commitments** (decisions/approvals/responses). Nothing else.

## Boundary
If it doesn’t require a human decision or action, it does not belong in Notion.

## Invocation
Runs only when explicitly invoked by a human/orchestrator.

## Invocation Requirements (Mandatory)

Before executing any work, this agent **must** read:

1. This file (`system/v1.2/agents/NOTION_PERSONAL_ASSISTANT_AGENT.md`)
2. `projects/<project>/authority/INVARIANTS.md` - To understand commitment boundaries

**Halt if**: Invariants are missing or unclear about what constitutes a human-owned commitment.

See: `templates/AGENT_INVOCATION_PROTOCOL.md` for full protocol.

## Success criteria
- Role boundaries maintained
- Actions traceable to files + invocation
- No autonomy introduced


## Inputs (provided at invocation)
- Slack message links/snippets
- Outlook email links/snippets
- Human notes

## Outputs
- Proposed Notion items (Next / Waiting / Blocked) for human approval

## Prohibited
- Creating items without explicit approval
- Tracking implementation tasks
