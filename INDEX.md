# SYSTEM V1.2 — Index

## Purpose
SYSTEM V1.2 introduces role-specific orientation files for faster agent onboarding while maintaining full operational fidelity.

## What's New in V1.2

**Orientation Files**: Single-file onboarding per agent role
- Reduces onboarding from ~3 minutes to <30 seconds
- Eliminates header duplication
- Consolidates essential context into one file per role

**Tiered Loading**: Read only what you need
- Tier 1: Compact orientation file (always)
- Tier 2: Extended orientation, full specs/templates (on demand)
- Tier 3: Project context (always for project work)

**Extended Orientation Files** (New in v1.2.1): Tier 2 reference material
- Full template structures
- Detailed examples
- Edge case guidance
- Event handler details

---

## Read Order (For Agents)

### V1.2 Fast Path (Recommended)

When invoking an agent, read ONE file:
1. `system/v1.2/orientation/<ROLE>_ORIENTATION.md`

| Role | Tier 1 (Always) | Tier 2 (On Demand) |
|------|-----------------|-------------------|
| Obsidian Project Historian | `HISTORIAN_ORIENTATION.md` | `HISTORIAN_ORIENTATION_EXTENDED.md` |
| Principal Software Engineer | `ENGINEER_ORIENTATION.md` | `ENGINEER_ORIENTATION_EXTENDED.md` |
| Notion Personal Assistant | `NOTION_ASSISTANT_ORIENTATION.md` | `NOTION_ASSISTANT_ORIENTATION_EXTENDED.md` |
| Orchestrator | `ORCHESTRATOR_ORIENTATION.md` | `ORCHESTRATOR_ORIENTATION_EXTENDED.md` |

Then read project context as specified in the orientation file.

### V1.2 Full Path (When Needed)

For complex situations or when constraints are unclear:
1. Tier 1 orientation file (always)
2. Tier 2 extended orientation: `orientation/<ROLE>_ORIENTATION_EXTENDED.md`
3. Full agent spec: `agents/<AGENT>_AGENT.md`
4. Full templates: `templates/*.md`
5. Examples: `examples/*.md`

---

## Directory Structure

```
system/v1.2/
├── INDEX.md                          # This file
├── CHANGELOG.md                      # Changes from V1.1
├── LLM_IMPLEMENTATION_ORIENTATION.md # System overview + efficiency guidance
├── orientation/                      # Role-specific onboarding
│   ├── HISTORIAN_ORIENTATION.md           # Tier 1 (compact)
│   ├── HISTORIAN_ORIENTATION_EXTENDED.md  # Tier 2 (templates, examples, changelog protocol)
│   ├── ENGINEER_ORIENTATION.md            # Tier 1 (compact)
│   ├── ENGINEER_ORIENTATION_EXTENDED.md   # Tier 2 (patterns, context-aware loading)
│   ├── NOTION_ASSISTANT_ORIENTATION.md    # Tier 1 (compact)
│   ├── NOTION_ASSISTANT_ORIENTATION_EXTENDED.md # Tier 2 (contract, examples)
│   ├── ORCHESTRATOR_ORIENTATION.md        # Tier 1 (compact)
│   └── ORCHESTRATOR_ORIENTATION_EXTENDED.md # Tier 2 (dispatch patterns)
├── docs/                             # Technical documentation
│   ├── PROMPT_CACHING.md             # Caching recommendations
│   ├── TOKEN_METRICS.md              # Token usage baselines
│   ├── AUTHORITY_SUMMARY_GENERATION.md # Summary generation guide
│   ├── PLAN_INDEX_GENERATION.md      # Plan index generation guide
│   └── SUB_AGENT_PATTERNS.md         # Sub-agent architecture patterns
├── agents/                           # Full agent specs (Tier 2)
├── templates/                        # Document templates (Tier 2)
│   ├── AUTHORITY_SUMMARY_TEMPLATE.md # Authority summary format
│   ├── PLAN_INDEX_TEMPLATE.md        # Plan index format
│   ├── AUTHORITY_CHANGELOG_TEMPLATE.md # Changelog format
│   ├── optional/                     # Optional tooling templates
│   │   └── OBSIDIAN_VAULT_SETUP.md   # Obsidian configuration (optional)
│   └── ... (other templates)
└── examples/                         # Pattern examples (Tier 2)
    ├── SUB_AGENT_EXAMPLES.md         # Sub-agent invocation examples
    └── ... (other examples)
```

---

## Canonical Artifacts

| Category | Location | Purpose |
|----------|----------|---------|
| Tier 1 Orientation | `orientation/*_ORIENTATION.md` | Fast agent onboarding |
| Tier 2 Orientation | `orientation/*_ORIENTATION_EXTENDED.md` | Templates, examples, details |
| Agent Specs | `agents/*.md` | Full constraints (Tier 2) |
| Templates | `templates/*.md` | Document creation |
| Examples | `examples/*.md` | Pattern reference |
| Technical Docs | `docs/*.md` | Caching, metrics, patterns |
| Changelog | `CHANGELOG.md` | Version history |

### Efficiency Artifacts

| Artifact | Location | Purpose |
|----------|----------|---------|
| Authority Summaries | `authority/*_SUMMARY.md` | Quick authority overview (~80% token reduction) |
| Authority Changelogs | `authority/*_CHANGELOG.md` | Delta-based authority loading |
| Plan Index | `plans/PLAN_INDEX.md` | Quick plan navigation |
| Token Metrics | `docs/TOKEN_METRICS.md` | Baseline measurements |
| Prompt Caching | `docs/PROMPT_CACHING.md` | Caching optimization guide |
| Sub-Agent Patterns | `docs/SUB_AGENT_PATTERNS.md` | Multi-agent architecture |

---

## Tiered Loading Protocol

### Tier 1 (Always Loaded)
- Compact orientation file (~75-120 lines)
- System constraints
- Core responsibilities
- Halt conditions
- Prohibited actions

### Tier 2 (Load On Demand)
- Extended orientation file (templates, examples)
- Full agent specifications
- Template files
- Example files

**When to load Tier 2**:
- Creating new documents (need templates)
- Patterns unclear (need examples)
- Constraints ambiguous (need full spec)

### Tier 3 (Project Context)
- `AUTHORITY.md` — Authority index
- `authority/INVARIANTS.md` — Constraints
- `authority/DECISIONS.md` — Design decisions
- `plans/active/<plan>.md` — Active implementation plan

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
3. Load extended files only when needed (Tier 2)

---

## Authority

This document does not grant authority. It provides navigation for the SYSTEM V1.2 specification.
