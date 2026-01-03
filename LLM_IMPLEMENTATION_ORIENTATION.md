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

---

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

---

## Efficiency Optimizations

### Tiered Loading

Load only what you need to minimize token consumption:

| Tier | What | When |
|------|------|------|
| Tier 1 | Compact orientation file | Always |
| Tier 2 | Extended orientation, summaries | On demand |
| Tier 3 | Full authority, active plan | For execution |

### Summary Files

Use summary files for quick context gathering:

| File | Purpose | Tokens |
|------|---------|--------|
| `authority/INVARIANTS_SUMMARY.md` | Quick invariant list | ~300 |
| `authority/DECISIONS_SUMMARY.md` | Quick decision list | ~500 |
| `plans/PLAN_INDEX.md` | Quick plan navigation | ~200 |

Load full documents only when summary is insufficient.

### Prompt Caching

Structure invocations for optimal caching:

1. **Stable content first**: Orientation files (cached)
2. **Authority next**: Summaries or full docs (cached)
3. **Dynamic content last**: Active plan, code (not cached)

See: `docs/PROMPT_CACHING.md` for detailed recommendations.

### Minimal Agent Invocation

When invoking subagents, use minimal prompts:

```
You are the [Agent Name].

Task: [One sentence describing intent]

Project: projects/<project>/
```

Agents read their own specs. Do not duplicate constraints in prompts.

---

## File Structure

```
system/v1.2/
├── orientation/           # Tier 1 + Tier 2 orientation files
│   ├── *_ORIENTATION.md        # Tier 1 (compact, ~100 lines)
│   └── *_ORIENTATION_EXTENDED.md # Tier 2 (templates, examples)
├── docs/                  # Technical documentation
│   ├── PROMPT_CACHING.md       # Caching recommendations
│   ├── TOKEN_METRICS.md        # Token usage baselines
│   └── *_GENERATION.md         # Generation scripts
├── templates/             # Document templates
└── examples/              # Pattern examples
```

---

## See Also

- `INDEX.md` — Full system navigation
- `docs/TOKEN_METRICS.md` — Token usage measurements
- `docs/PROMPT_CACHING.md` — Caching optimization
