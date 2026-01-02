# SYSTEM V1.2 — Changelog

## V1.2.1 (2026-01-01) — Audit Remediation

**Problem Solved**: Language-level ambiguities in V1.2 documents risked authority confusion and chat-based scope bleed between agents.

**Changes**:

### Issue 1: Orchestrator Language Implies Selection Authority
- Added constraint block to `agents/ORCHESTRATOR_AGENT.md` Boundary section
- Added constraint block to `orientation/ORCHESTRATOR_ORIENTATION.md` Your Role section
- Explicitly states: "The orchestrator does not choose plans, priorities, or next steps. It only invokes roles using artifacts explicitly designated by the human."

### Issue 2: Historian Orientation Implies Plan Ownership
- Added constraint block to `orientation/HISTORIAN_ORIENTATION.md` Your Role section
- Explicitly states: "The Historian may draft or modify implementation plans only when explicitly invoked to do so. Plan existence does not imply execution readiness or permission."

### Issue 3: Engineer Contract Missing Explicit Chat Reliance Prohibition
- Added clause to `agents/PRINCIPAL_SOFTWARE_ENGINEER_AGENT.md` Input Source Constraint section
- Explicitly states: "The Engineer must treat prior chat output as non-authoritative commentary. Only repository artifacts and explicitly provided file paths may be used as execution inputs."

### Issue 4: Missing Authority Headers in Orientation Documents
- Added `## Authority: This document does not grant authority.` to:
  - `orientation/ORCHESTRATOR_ORIENTATION.md`
  - `orientation/ENGINEER_ORIENTATION.md`
  - `orientation/HISTORIAN_ORIENTATION.md`
  - `orientation/NOTION_ASSISTANT_ORIENTATION.md`

### Issue 5: Obsidian Template Risks Tool-Coupling
- Updated authority header in `templates/OBSIDIAN_VAULT_SETUP.md` to include:
  - "Note: Obsidian is a recommended documentation interface, not a system requirement."
  - "All authority derives from repository files, not tooling."

**Affected Files**:
| File | Change |
|------|--------|
| `agents/ORCHESTRATOR_AGENT.md` | Added no-selection-authority constraint |
| `agents/PRINCIPAL_SOFTWARE_ENGINEER_AGENT.md` | Added chat reliance prohibition |
| `orientation/ORCHESTRATOR_ORIENTATION.md` | Added authority header + no-selection constraint |
| `orientation/ENGINEER_ORIENTATION.md` | Added authority header |
| `orientation/HISTORIAN_ORIENTATION.md` | Added authority header + invocation gate |
| `orientation/NOTION_ASSISTANT_ORIENTATION.md` | Added authority header |
| `templates/OBSIDIAN_VAULT_SETUP.md` | Added tool-coupling clarification |

---

## V1.2 (2026-01-01T18:00:00Z)

### Artifact Boundary Rules

**Problem Solved**: When agents communicate through the Orchestrator, conversation history could leak context between agents. For example, if the Historian provided recommendations in chat without writing to files, and the Engineer was invoked in the same session, the Engineer might act on chat-only output. This turned the Orchestrator into an implicit context broker.

**Solution**: Two complementary rules that formalize the artifact boundary between agents.

#### Historian Output Rule
- **Rule**: "Outputs must land in files"
- Historian outputs not written to files are non-existent for other agents
- Valid targets: `docs/*`, `authority/*` (if authorized), `plans/active/*`
- Chat-only recommendations are not valid handoff artifacts

#### Engineer Input Rule
- **Rule**: "Engineer reads from files only"
- Valid sources: authority docs + active plan + referenced code paths
- Prior conversation output is explicitly excluded
- Invocation must include: "Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths."

#### Affected Files
| File | Change |
|------|--------|
| `orientation/HISTORIAN_ORIENTATION.md` | Added "Output File Requirement" section |
| `orientation/ENGINEER_ORIENTATION.md` | Added "Input Source Constraint" section |
| `orientation/ORCHESTRATOR_ORIENTATION.md` | Added "Engineer Invocation Template" with file-only directive |
| `agents/OBSIDIAN_PROJECT_HISTORIAN_AGENT.md` | Added output file requirement, updated prohibited actions |
| `agents/PRINCIPAL_SOFTWARE_ENGINEER_AGENT.md` | Added input source constraint section |
| `agents/ORCHESTRATOR_AGENT.md` | Added Engineer invocation template |
| `templates/AGENT_INVOCATION_PROTOCOL.md` | Added Engineer file-only invocation syntax |

#### Rationale
- Keeps Orchestrator as a pure dispatcher (no implicit context brokering)
- All inter-agent communication is auditable via files
- Prevents autonomy creep through conversation history leakage

---

### Role-Specific Orientation Files

**Problem Solved**: Agent onboarding took ~3 minutes due to reading multiple files with duplicated headers.

**Solution**: Created consolidated orientation files that contain all essential context for each role in a single file.

#### New Files

| File | Purpose | Lines |
|------|---------|-------|
| `orientation/HISTORIAN_ORIENTATION.md` | All Historian context | ~120 |
| `orientation/ENGINEER_ORIENTATION.md` | All Engineer context | ~110 |
| `orientation/NOTION_ASSISTANT_ORIENTATION.md` | All Notion Assistant context | ~100 |
| `orientation/ORCHESTRATOR_ORIENTATION.md` | All Orchestrator context | ~100 |

#### Performance Improvement

| Metric | V1.1 | V1.2 | Improvement |
|--------|------|------|-------------|
| Files to read | 4-6 | 1 | 75-83% reduction |
| Total lines | ~586 | ~120 | ~80% reduction |
| Duplicated headers | ~108 lines | 0 | 100% elimination |
| Time to operational | ~3 min | <30 sec | ~85% faster |

### Tiered Loading Pattern

**New Pattern**: Agents read only what they need, when they need it.

**Tier 1 — Always Read**
- Role-specific orientation file
- Takes <10 seconds

**Tier 2 — Read on Demand**
- Full templates (only when creating documents)
- Full agent specs (only if constraints are unclear)
- Examples (only if patterns needed)

**Tier 3 — Project Context**
- AUTHORITY.md
- Active plan
- Authority documents

### What's Preserved

All V1.1 content is preserved in V1.2:
- Full agent specs in `agents/`
- All templates in `templates/`
- All examples in `examples/`
- `LLM_IMPLEMENTATION_ORIENTATION.md`
- `AGENT_INVOCATION_PROTOCOL.md`

V1.2 **adds** orientation files; it does not remove or modify V1.1 content.

### Updated Files

**AGENT_INVOCATION_PROTOCOL.md**
- Added V1.2 fast path invocation pattern
- Orientation file as primary onboarding mechanism
- Tiered loading instructions

**INDEX.md**
- New V1.2-specific read order
- Orientation file references
- Directory structure update

### Fidelity Validation

V1.2 orientation files preserve all constraints from V1.1. Tested scenarios:

| Constraint | V1.1 | V1.2 | Status |
|------------|------|------|--------|
| Role boundaries | Agent spec | Orientation | Preserved |
| Halt conditions | Agent spec | Orientation | Preserved |
| Template requirements | Templates | Orientation + Templates | Preserved |
| Authority hygiene | Agent spec | Orientation | Preserved |
| Prohibited actions | Agent spec | Orientation | Preserved |

### Backward Compatibility

V1.2 is fully backward compatible with V1.1:
- Agents invoked with V1.1 protocol continue to work
- Full agent specs remain available
- Templates unchanged
- Examples unchanged

To upgrade: Update invocation prompts to reference `system/v1.2/orientation/` instead of reading multiple V1.1 files.

---

## V1.1 (2026-01-01T09:00:00Z)

See `system/v1.1/CHANGELOG.md` for V1.1 changes from V1.

---

## V1 (Initial)

Initial release. See `system/v1/` for original specification.
