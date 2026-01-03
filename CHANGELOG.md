# SYSTEM V1.2 — Changelog

> **This file is the authoritative source for SYSTEM V1.2 version history.**
> All other documents should reference "SYSTEM V1.2" (major version) without patch numbers.

---

## V1.2.3 (2026-01-02) — Plan On Hold Status

**Summary**: Introduced `plans/on-hold/` directory for plans paused pending decisions, resources, or dependencies. Engineers cannot execute on-hold plans; only Historian can move plans to/from on-hold.

**Plan Lifecycle**:
| Status | Location | Actionable |
|--------|----------|------------|
| Draft/Ready/In Progress | `plans/active/` | Yes (when Ready) |
| On Hold | `plans/on-hold/` | No |
| Complete/Abandoned | `plans/archive/` | No |

---

## V1.2.2 (2026-01-02) — Authority Path Correction

**Summary**: Fixed authority document paths. Agents were looking for `INVARIANTS.md` and `DECISIONS.md` at project root instead of `authority/` subdirectory.

**Fix**: All references now correctly point to `authority/INVARIANTS.md` and `authority/DECISIONS.md`.

---

## V1.2.1 (2026-01-01) — Audit Remediation

**Summary**: Fixed language-level ambiguities that risked authority confusion and chat-based scope bleed.

**Key Fixes**:
- Orchestrator explicitly cannot choose plans/priorities (dispatch only)
- Historian explicitly cannot self-invoke plan creation
- Engineer explicitly cannot use prior chat output as input
- All orientation documents now include authority headers

---

## V1.2 (2026-01-01) — Role-Specific Orientation Files

### What Changed

**Problem**: Agent onboarding took ~3 minutes reading 4-6 files (~586 lines) with duplicated headers.

**Solution**: Created consolidated orientation files—one file per role with all essential context.

### Orientation Files

| Role | File | Lines |
|------|------|-------|
| Orchestrator | `orientation/ORCHESTRATOR_ORIENTATION.md` | ~100 |
| Historian | `orientation/HISTORIAN_ORIENTATION.md` | ~120 |
| Engineer | `orientation/ENGINEER_ORIENTATION.md` | ~110 |
| Notion Assistant | `orientation/NOTION_ASSISTANT_ORIENTATION.md` | ~100 |

### Tiered Loading Pattern

- **Tier 1** (Always): Orientation file only (<10 seconds)
- **Tier 2** (On Demand): Full templates, agent specs, examples
- **Tier 3** (Project Context): AUTHORITY.md, active plan, authority docs

### Artifact Boundary Rules

Two rules prevent context leakage between agents:

1. **Historian Output Rule**: Outputs must land in files. Chat-only recommendations are non-existent for other agents.

2. **Engineer Input Rule**: Engineer reads from files only. Prior conversation output is explicitly excluded.

### Performance

| Metric | V1.1 | V1.2 | Improvement |
|--------|------|------|-------------|
| Files to read | 4-6 | 1 | 75-83% reduction |
| Total lines | ~586 | ~120 | ~80% reduction |
| Time to operational | ~3 min | <30 sec | ~85% faster |

### Backward Compatibility

V1.2 is fully backward compatible with V1.1. Agents invoked with V1.1 protocol continue to work.

---

## Previous Versions

- **V1.1**: See `system/v1.1/CHANGELOG.md`
- **V1**: Initial release at `system/v1/`
