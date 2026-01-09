# CONVOY EXAMPLE

## Authority
This document does not grant authority. It provides examples only.

---

## Purpose

This example shows a complete Beads convoy workflow from creation to completion.

---

## Scenario

Implement a new validation check that verifies audio codec preservation.

---

## Phase 1: Plan Creation (Historian)

Human invokes Historian: "Create a plan for adding audio codec validation"

### Historian Creates Convoy

```bash
bd create "Add Audio Codec Validation" \
  --type convoy \
  --status draft \
  --label "authority:pending" \
  --label "feature:validation" \
  --label "scope:stages" \
  --label "type:feature" \
  --label "risk:low" \
  --label "priority:normal" \
  --field "authority_citations=INVARIANTS.md#Audio-Preservation,DECISIONS.md#2026-01-08---Audio-Codec-Validation" \
  --description "## Objective
Add a validation check that verifies the output audio codec matches the input.

## Technical Design
- Add new validation to ValidateFinalOutputStage
- Compare input/output codec via ffprobe
- Fail with clear error message on mismatch

## Scope
- Included: Audio codec validation logic, tests
- Excluded: Video codec validation (separate plan)

## Acceptance Criteria
- [ ] Validation detects codec mismatch
- [ ] Validation passes when codecs match
- [ ] Error message includes both codecs
- [ ] Unit tests cover both cases"
```

**Result**: Convoy `bd-a1b2` created in `draft` status.

### Historian Creates Tasks

```bash
bd create "Add audio codec validation to ValidateFinalOutputStage" \
  --parent bd-a1b2 --priority 1

bd create "Write unit tests for audio codec validation" \
  --parent bd-a1b2 --priority 2

bd create "Update validation documentation" \
  --parent bd-a1b2 --priority 3
```

### Historian Submits for Approval

```bash
bd update bd-a1b2 --status pending_approval
bd comment bd-a1b2 "Plan ready for review. 3 tasks created."
```

---

## Phase 2: Human Approval

Human reviews the convoy:

```bash
bd show bd-a1b2
```

Human approves:

```bash
bd update bd-a1b2 --status approved --label authority:granted
```

**Result**: Convoy `bd-a1b2` now has `authority:granted` label.

---

## Phase 3: Execution (Engineer)

Human invokes Engineer: "Execute convoy bd-a1b2"

### Engineer Verifies Authority

```bash
# 1. Check convoy has authority:granted
bd show bd-a1b2 --json | jq '.labels'
# ["authority:granted", "feature:validation", ...]

# 2. Check no suspended label
# (none present)

# 3. Check no needs_triage children
bd list --parent bd-a1b2 --status needs_triage
# (empty)

# 4. Check authority citations resolve
# INVARIANTS.md#Audio-Preservation exists ✓
# DECISIONS.md#2026-01-08---Audio-Codec-Validation exists ✓
```

### Engineer Claims First Task

```bash
bd ready --parent bd-a1b2 --limit 1
# bd-c3d4: Add audio codec validation to ValidateFinalOutputStage

bd update bd-c3d4 --claim engineer-session-abc123
```

### Engineer Executes Task

1. Reads existing validation code
2. Adds audio codec validation logic
3. Runs existing tests to ensure no regression

```bash
bd comment bd-c3d4 "Added validation logic to validate_final_output_stage.py"
```

### Engineer Closes Task

```bash
bd close bd-c3d4 --reason "Implementation complete"
```

### Engineer Continues with Remaining Tasks

```bash
# Task 2: Write tests
bd ready --parent bd-a1b2 --limit 1
bd update bd-e5f6 --claim engineer-session-abc123
# ... write tests ...
bd close bd-e5f6 --reason "Unit tests added, all passing"

# Task 3: Update docs
bd ready --parent bd-a1b2 --limit 1
bd update bd-g7h8 --claim engineer-session-abc123
# ... update docs ...
bd close bd-g7h8 --reason "Documentation updated"
```

---

## Phase 4: Completion Request (Engineer)

All tasks complete. Engineer proves acceptance criteria:

```bash
# Run tests to prove criteria met
pytest tests/unit/test_audio_codec_validation.py -v
# All tests pass

# Request human approval
bd update bd-a1b2 --status pending_human_approval
bd comment bd-a1b2 "All tasks complete. Tests pass. Ready for human approval.

Acceptance Criteria Status:
- [x] Validation detects codec mismatch (test_codec_mismatch)
- [x] Validation passes when codecs match (test_codec_match)
- [x] Error message includes both codecs (verified in test)
- [x] Unit tests cover both cases (2 tests added)"
```

---

## Phase 5: Human Completion

Human reviews:

```bash
bd show bd-a1b2
# Review tasks, comments, test results
```

Human approves completion:

```bash
bd update bd-a1b2 --status completed
```

---

## Alternative: Discovery During Execution

If Engineer finds unexpected work:

```bash
# Engineer discovers edge case not in plan
bd create "Handle AAC-LC vs AAC-HE codec variants" \
  --type blocker \
  --status needs_triage \
  --discovered-from bd-c3d4

# This automatically suspends authority on bd-a1b2
# Engineer HALTS and waits for human to triage
```

Human triages:

```bash
# Option A: Add to current plan
bd update bd-i9j0 --parent bd-a1b2 --status ready

# Option B: Create separate plan
bd update bd-i9j0 --status deferred
bd update bd-a1b2 --label authority:granted  # Restore authority
```

---

## Alternative: HALT on Test Conflict

If Engineer cannot pass tests without violating principles:

```bash
bd update bd-a1b2 --status halted --label halted:test-conflict
bd comment bd-a1b2 "HALTED: test_codec_validation expects AAC output but source is FLAC.
Cannot preserve codec AND pass test. Need guidance:
1. Update test to expect FLAC?
2. Change requirement to allow transcoding?"
```

Human decides and Engineer resumes.

---

## Summary: State Transitions

```
draft
  → pending_approval (Historian submits)
    → approved (Human grants authority)
      → in_progress (Engineer claims task)
        → suspended (Discovery found)
        → halted (Engineer blocked)
        → pending_human_approval (Engineer done)
          → completed (Human approves)
```
