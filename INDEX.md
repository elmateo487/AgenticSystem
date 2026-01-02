# SYSTEM V1.2 — Index

## Purpose
SYSTEM V1.2 introduces role-specific orientation files for faster agent onboarding while maintaining full operational fidelity.

## What's New in V1.2

**Orientation Files**: Single-file onboarding per agent role
- Reduces onboarding from ~3 minutes to <30 seconds
- Eliminates header duplication
- Consolidates essential context into one file per role

**Tiered Loading**: Read only what you need
- Tier 1: Orientation file (always)
- Tier 2: Full specs/templates (on demand)
- Tier 3: Project context (always for project work)

---

## Read Order (For Agents)

### V1.2 Fast Path (Recommended)

When invoking an agent, read ONE file:
1. `system/v1.2/orientation/<ROLE>_ORIENTATION.md`

| Role | Orientation File |
|------|------------------|
| Obsidian Project Historian | `HISTORIAN_ORIENTATION.md` |
| Principal Software Engineer | `ENGINEER_ORIENTATION.md` |
| Notion Personal Assistant | `NOTION_ASSISTANT_ORIENTATION.md` |
| Orchestrator | `ORCHESTRATOR_ORIENTATION.md` |

Then read project context as specified in the orientation file.

### V1.2 Full Path (When Needed)

For complex situations or when constraints are unclear:
1. Orientation file (always)
2. Full agent spec: `agents/<AGENT>_AGENT.md`
3. Full templates: `templates/*.md`
4. Examples: `examples/*.md`

---

## Directory Structure

```
system/v1.2/
├── INDEX.md                          # This file
├── CHANGELOG.md                      # Changes from V1.1
├── LLM_IMPLEMENTATION_ORIENTATION.md # System overview
├── orientation/                      # NEW: Role-specific onboarding
│   ├── HISTORIAN_ORIENTATION.md
│   ├── ENGINEER_ORIENTATION.md
│   ├── NOTION_ASSISTANT_ORIENTATION.md
│   └── ORCHESTRATOR_ORIENTATION.md
├── agents/                           # Full agent specs (Tier 2)
├── templates/                        # Document templates (Tier 2)
└── examples/                         # Pattern examples (Tier 2)
```

---

## Canonical Artifacts

| Category | Location | Purpose |
|----------|----------|---------|
| Orientation | `orientation/*.md` | Fast agent onboarding |
| Agent Specs | `agents/*.md` | Full constraints (Tier 2) |
| Templates | `templates/*.md` | Document creation |
| Examples | `examples/*.md` | Pattern reference |
| Changelog | `CHANGELOG.md` | Version history |

---

## Versioning

- V1.1 is immutable and remains at `system/v1.1/`
- V1.2 adds orientation files; does not remove V1.1 content
- Future versions: `system/v1.3/`, `system/v2/`, etc.

---

## Upgrade Path from V1.1

V1.2 is backward compatible. Agents invoked with V1.1 protocol will still work.

To use V1.2 optimized onboarding:
1. Update invocation prompts to reference `system/v1.2/orientation/<ROLE>_ORIENTATION.md`
2. Use tiered loading as specified in orientation files

---

## Authority

This document does not grant authority. It provides navigation for the SYSTEM V1.2 specification.
