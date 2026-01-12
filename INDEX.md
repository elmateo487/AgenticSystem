# SYSTEM V1.3 Index

## Root Files

| File | Description |
|------|-------------|
| `README.md` | System overview and quick start |
| `INDEX.md` | This file - complete file listing |
| `MIGRATION_PLAN.md` | V1.2 to V1.3 migration plan |
| `CHANGELOG.md` | Version history (TODO) |

## Agent Skills

Agent definitions are consolidated into skills at `~/.claude/skills/`:

| Skill | Purpose |
|-------|---------|
| `/engineer` | Execute approved plans (code, tests, implementation) |
| `/historian` | Create plans (Beads epics), maintain authority documents |
| `/orchestrator` | Re-orient when context is lost |

## Documentation

| File | Lines | Description |
|------|-------|-------------|
| `docs/BEADS_INTEGRATION.md` | ~900 | V1.3 design specification - Beads integration |
| `docs/BEADS_INTEGRATION_AUDIT.md` | ~370 | Audit of BEADS_INTEGRATION.md |
| `docs/SUB_AGENT_PATTERNS.md` | 245 | Subagent coordination patterns |

## Templates

Templates for project authority documents.

| File | Lines | Description |
|------|-------|-------------|
| `templates/INVARIANTS_TEMPLATE.md` | 32 | Non-negotiable constraints template |
| `templates/DECISIONS_TEMPLATE.md` | 38 | Design decisions template |
| `templates/ARCHITECTURE_TEMPLATE.md` | 29 | Architecture documentation template |
| `templates/PIPELINE_TEMPLATE.md` | 26 | Pipeline documentation template |
| `templates/AUTHORITY_CHANGELOG_TEMPLATE.md` | 49 | Authority change log template |

## Examples

| File | Lines | Description |
|------|-------|-------------|
| `examples/EPIC_EXAMPLE.md` | 258 | Complete Beads epic workflow example |
| `examples/INVARIANTS_EXAMPLE.md` | 41 | Example INVARIANTS.md |
| `examples/DECISIONS_EXAMPLE.md` | 54 | Example DECISIONS.md |

## Status

| Category | Complete | TODO |
|----------|----------|------|
| Root | 3 | 1 |
| Skills | 3 | 0 |
| Docs | 3 | 0 |
| Templates | 5 | 0 |
| Examples | 3 | 0 |
| **Total** | **17** | **1** |
