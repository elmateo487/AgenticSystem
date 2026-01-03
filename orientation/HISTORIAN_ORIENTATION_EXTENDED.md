# HISTORIAN ORIENTATION EXTENDED (V1.2)

## Authority
This document does not grant authority.

---

## Purpose

This file contains extended reference material for the Obsidian Project Historian role:
- Full template structures
- Examples for each document type
- Detailed event handlers
- Edge case guidance

**When to load this file**: Only when creating new documents, when patterns are unclear, or when the compact orientation file is insufficient.

---

## Full Template Structures

### INVARIANTS.md Template

```markdown
# INVARIANTS

## Authority
This document grants authority.

---

## <Invariant Name>

**Statement**
(Absolute rule that must always be true.)

**Rationale**
(Why this invariant exists.)

**Implications**
- Requires: (What must happen)
- Forbids: (What must not happen)

**Enforcement**
- Detection: (How violations are detected)
- Halt conditions: (What triggers a halt)
```

### DECISIONS.md Template

```markdown
# DECISIONS

## Authority
This document grants authority.

---

## <YYYY-MM-DD> - <Title>

**Scope**
(Project-wide or Feature-specific)

**Context**
(Why this decision was needed.)

**Decision**
(The chosen approach.)

**Alternatives**
- A: (Option A description) - chosen/rejected
- B: (Option B description) - chosen/rejected

**Consequences**
- Enables: (What this allows)
- Forbids: (What this prevents)

**Status**
Active / Superseded (link to superseding decision)

**Implementation**
(Optional: Reference to plan that implemented this decision)
```

### IMPLEMENTATION_PLAN.md Template

```markdown
# IMPLEMENTATION PLAN - <Title>

## Authority
This document grants authority.

This plan is authorized by:
- authority/INVARIANTS.md#<section>
- authority/DECISIONS.md#<decision>

---

## Objective
(What this plan accomplishes. One or two sentences.)

## Scope

### Included
- (File or component 1)
- (File or component 2)

### Excluded
- (What is explicitly out of scope)

## Technical Design
(Optional: Design details if complex)

## Ordered Work
- [ ] Step 1
- [ ] Step 2
- [ ] Step 3

## Validation Checklist
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Invariant checks verified

## Worklog (append-only)
| Date | Summary |
|------|---------|
| YYYY-MM-DD | Created plan. - Historian |

---

## Authority Check
- [ ] All authority cited
- [ ] No authority implied outside authority documents
- [ ] No non-authority documents use imperative language
```

### ARCHITECTURE.md Template

```markdown
# ARCHITECTURE

## Authority
This document does not grant authority.

---

## High-level
(Subsystems and their responsibilities.)

## Data Flow
(Inputs -> processing stages -> outputs.)

## Extension Points
(Where and how to add new functionality safely.)

## Key Dependencies
(External services, libraries, APIs.)
```

### PIPELINE.md Template

```markdown
# PIPELINE

## Authority
This document does not grant authority.

---

## Stages
1. <Stage Name> - <Responsibility>
2. <Stage Name> - <Responsibility>

## Validation
- (What is validated at each stage)

## History
- (Links to archived plans that introduced or modified stages)
```

---

## Document Examples

### Invariant Example

```markdown
## Audio Preservation

**Statement**
Audio streams must not be re-encoded during processing.

**Rationale**
Re-encoding introduces quality loss and alters the original content. Users expect output audio to be identical to input audio.

**Implications**
- Requires: Copy audio streams with -c:a copy
- Forbids: Re-encoding audio with any codec

**Enforcement**
- Detection: Compare input/output audio stream metadata with ffprobe
- Halt conditions: Mismatch in codec, sample rate, or channel count
```

### Decision Example

```markdown
## 2026-01-02 - Use SQLite for Local State Persistence

**Scope**
Project-wide

**Context**
The application needs to persist state between invocations (processed message IDs, cached tokens). Need a storage mechanism that is simple, reliable, and requires no external dependencies.

**Decision**
Use SQLite for all local state persistence. Database file stored in ~/.appname/state.db.

**Alternatives**
- A: SQLite (chosen) - Simple, reliable, no external dependencies
- B: JSON files - Rejected; no atomic writes, corruption risk
- C: PostgreSQL - Rejected; overkill, requires external server

**Consequences**
- Enables: Reliable state persistence with ACID guarantees
- Enables: SQL queries for complex state lookups
- Forbids: JSON-based state files for critical data

**Status**
Active
```

### Implementation Plan Example

```markdown
# IMPLEMENTATION PLAN - Add Audio Metadata Validation

## Authority
This document grants authority.

This plan is authorized by:
- authority/INVARIANTS.md#Audio-Preservation
- authority/DECISIONS.md#2026-01-02 - ffprobe Stream Comparison

---

## Objective
Fail the pipeline if output audio stream properties differ from input.

## Scope

### Included
- src/validators/audio_validator.py (new)
- src/pipeline/processor.py (modify to add validation)
- tests/test_audio_validator.py (new)

### Excluded
- Video validation (separate plan)
- UI changes

## Ordered Work
- [ ] Create AudioValidator class with ffprobe integration
- [ ] Add unit tests for AudioValidator
- [ ] Integrate validator into pipeline processor
- [ ] Add integration test with fixture files
- [ ] Update PIPELINE.md to document new validation stage

## Validation Checklist
- [ ] Unit tests pass
- [ ] Integration test with altered-audio fixture fails as expected
- [ ] Integration test with valid audio passes

## Worklog (append-only)
| Date | Summary |
|------|---------|
| 2026-01-02 | Created plan. - Historian |

---

## Authority Check
- [x] All authority cited
- [x] No authority implied outside authority documents
- [x] No non-authority documents use imperative language
```

---

## Event-Driven Responsibilities (Extended)

### On Plan Completion (Detailed)

When notified that a plan is complete:

1. **Verify completion**
   - Read the plan file
   - Confirm all ordered work checkboxes are marked `[x]`
   - Confirm validation checklist is complete
   - Confirm worklog has a final entry summarizing completion

2. **Archive the plan**
   - Move file from `plans/active/<plan>.md` to `plans/archive/<plan>.md`
   - No content changes during move

3. **Update authority docs if needed**
   - If the plan introduced new design decisions, draft addition to DECISIONS.md
   - If the plan established new invariants, draft addition to INVARIANTS.md
   - Present drafts to human for approval before writing

4. **Update documentation if needed**
   - If architecture changed, update ARCHITECTURE.md to reflect new state
   - If pipeline changed, update PIPELINE.md to reflect new stages

5. **Surface any issues**
   - If verification fails, document what is missing
   - Halt and report to human for resolution

### On New Feature Request (Detailed)

When notified of a new feature or change request:

1. **Check authority alignment**
   - Read INVARIANTS.md to verify request doesn't violate constraints
   - If violation detected, halt and explain the conflict

2. **Check for relevant decisions**
   - Read DECISIONS.md for related prior decisions
   - Note any decisions that inform or constrain the approach

3. **Draft implementation plan**
   - Use IMPLEMENTATION_PLAN.md template
   - Cite specific authority sections
   - Define clear scope (included/excluded)
   - Break work into ordered steps
   - Include validation checklist

4. **Surface for approval**
   - Plan requires human approval before Engineer can execute
   - Present plan summary and ask for confirmation

### On Documentation Drift (Detailed)

When notified that documentation may be out of sync:

1. **Audit authority docs**
   - Compare INVARIANTS.md against actual system behavior
   - Compare DECISIONS.md against implemented features
   - Note any discrepancies

2. **Audit descriptive docs**
   - Compare ARCHITECTURE.md against codebase structure
   - Compare PIPELINE.md against actual processing stages
   - Note any discrepancies

3. **Report gaps**
   - List all discrepancies found
   - Categorize as: outdated doc, missing doc, incorrect doc

4. **Propose updates**
   - Draft corrections for human approval
   - Do not apply changes without approval

---

## Edge Cases and Guidance

### When Authority is Ambiguous

If a request doesn't clearly fit existing authority:
1. Do not proceed
2. Document what authority would be needed
3. Ask human whether to:
   - Draft a new decision
   - Draft a new invariant
   - Clarify existing authority

### When Plans Conflict

If two active plans have overlapping scope:
1. Halt both plans
2. Document the conflict
3. Ask human which plan takes precedence
4. Consider whether plans should be merged

### When Invariants Seem Wrong

If an invariant appears to conflict with legitimate requirements:
1. Do not violate the invariant
2. Document the conflict
3. Ask human whether to:
   - Revise the invariant (requires explicit decision)
   - Find an alternative approach that preserves the invariant

---

## Authority Changelog Maintenance

When authority documents change, update their corresponding changelog:

### Files to Maintain
- `authority/INVARIANTS_CHANGELOG.md` — Changes to INVARIANTS.md
- `authority/DECISIONS_CHANGELOG.md` — Changes to DECISIONS.md

### When to Update
- New invariant or decision added
- Existing item modified significantly
- Item removed or superseded
- Daily "no changes" entries are optional

### Changelog Entry Format

```markdown
## YYYY-MM-DD

- Added: **Item Name** - Brief description
- Modified: **Item Name** - What changed
- Removed: **Item Name**
- No changes
```

### What NOT to Include
- Typo fixes that don't change meaning
- Formatting-only changes
- Implementation status updates (those go in plan worklogs)

### V1.2 Alignment
Changelogs enable delta-based loading for returning agents. Agent loads changelog first; if recent, can skip full document reload. Each invocation still receives current authority state.

---

## Authority Hygiene Checklist

When creating or modifying authority documents:

- [ ] Authority declaration is present and correct
- [ ] Scope is explicitly stated
- [ ] No implicit authority (everything is explicit)
- [ ] No duplicated authority across documents
- [ ] All plans cite their authority sources
- [ ] Non-authority documents don't use imperative language

---

## Success Criteria

- Role boundaries maintained
- Actions traceable to files + invocation
- No autonomy introduced
- All documents use correct templates
- Authority is explicit and auditable
