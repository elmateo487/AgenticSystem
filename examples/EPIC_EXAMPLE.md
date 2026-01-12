# EPIC EXAMPLE

## Authority
This document does not grant authority. It provides examples only.

---

## Purpose

This example shows a complete Beads epic workflow from creation to completion.

---

## Scenario

Implement a new validation check that verifies audio codec preservation.

---

## Phase 1: Plan Creation (Historian)

Human invokes Historian: "Create a plan for adding audio codec validation"

### Historian Creates Epic (Level 1 - Context Only)

```bash
# Level 1: Epic contains CONTEXT, not instructions or AC checkboxes
bd create "Add Audio Codec Validation" \
  --type epic \
  --status draft \
  --label "feature:validation" \
  --label "scope:stages" \
  --label "type:feature" \
  --label "risk:low" \
  --label "priority:normal" \
  --field "authority_citations=INVARIANTS.md#Audio-Preservation,DECISIONS.md#2026-01-08---Audio-Codec-Validation" \
  --description "## Problem Statement
Users reported audio codec changes in some outputs. Need to catch codec mismatches during validation.

## Technical Context
ValidateFinalOutputStage runs after all processing. It has access to both input and output file paths for comparison via ffprobe.

## Design Rationale
Explicit codec comparison is more reliable than assuming stream copy worked correctly."
```

**Result**: Epic `bd-a1b2` created in `draft` status.

### Historian Creates Tickets (Level 2 - Instructions)

```bash
# Level 2: Tickets contain INSTRUCTIONS and implementation details
bd create "Implement audio codec validation" \
  --parent bd-a1b2 --priority 1 \
  --description "## Implementation
- Add validation method to ValidateFinalOutputStage
- Compare input/output codec via ffprobe
- Fail with clear error message on mismatch

## Files to Modify
- src/stages/validate_final_output_stage.py"
```

**Result**: Ticket `bd-c3d4` created under epic.

### Historian Creates Acceptance Criteria (Level 3 - Leaf Nodes)

```bash
# Level 3: ACs are tasks with --parent set (NOT checkboxes in descriptions)
# Note: Both tickets and ACs use Beads type: task - hierarchy is via --parent field
bd create "Detect codec mismatch and raise ValidationError" --parent bd-c3d4 --priority 1
bd create "Pass validation when codecs match" --parent bd-c3d4 --priority 2
bd create "Include both codecs in error message" --parent bd-c3d4 --priority 3
bd create "Add unit tests for mismatch and match cases" --parent bd-c3d4 --priority 4

# Additional tickets
bd create "Update validation documentation" \
  --parent bd-a1b2 --priority 2
```

**Result**: 4 ACs created with `--parent bd-c3d4`. Structure is now:
```
bd-a1b2 (Epic)
  └── bd-c3d4 (Ticket: Implement audio codec validation)
      ├── bd-e5f6 (AC: Detect codec mismatch)
      ├── bd-g7h8 (AC: Pass when codecs match)
      ├── bd-i9j0 (AC: Include both codecs in error)
      └── bd-k1l2 (AC: Add unit tests)
  └── bd-m3n4 (Ticket: Update documentation)
```

### Historian Submits for Approval

```bash
bd update bd-a1b2 --status pending_approval
bd comment bd-a1b2 "Plan ready for review. 2 tickets with 4 ACs total."
```

---

## Phase 2: Human Approval

Human reviews the epic:

```bash
bd show bd-a1b2
```

Human approves:

```bash
bd update bd-a1b2 --status approved
```

**Result**: Epic `bd-a1b2` is now approved for execution.

---

## Phase 3: Execution (Engineer)

Human invokes Engineer: "Execute epic bd-a1b2"

### Engineer Reads Work Tree and Starts

Engineer reads `/tmp/work.json` (pre-exported by Orchestrator) and begins work.

### Engineer Claims Ticket and Works Through ACs

```bash
# Find ready ticket
bd ready --parent bd-a1b2 --limit 1
# bd-c3d4: Implement audio codec validation

# Read ticket for implementation context
bd show bd-c3d4

# Claim the ticket
bd update bd-c3d4 --claim engineer-session-abc123

# Check for ACs (tasks with this ticket as parent)
bd list --parent bd-c3d4
# bd-e5f6: Detect codec mismatch and raise ValidationError
# bd-g7h8: Pass validation when codecs match
# bd-i9j0: Include both codecs in error message
# bd-k1l2: Add unit tests for mismatch and match cases
```

### Engineer Works Through ACs (Level 3)

```bash
# AC Item 1: Implement mismatch detection
bd comment bd-e5f6 "Implementing codec comparison in validate_final_output_stage.py"
# ... implement logic ...
bd close bd-e5f6 --reason "Mismatch detection implemented"

# AC Item 2: Handle matching codecs
bd close bd-g7h8 --reason "Match case handled, returns success"

# AC Item 3: Error message formatting
bd close bd-i9j0 --reason "Error includes input codec {X} vs output codec {Y}"

# AC Item 4: Unit tests
bd close bd-k1l2 --reason "Added test_codec_mismatch and test_codec_match"
```

### Engineer Closes Ticket (All ACs Complete)

```bash
# All ACs done - close the ticket
bd close bd-c3d4 --reason "All ACs complete, validation implemented"

# Continue with next ticket
bd ready --parent bd-a1b2 --limit 1
# bd-m3n4: Update validation documentation

bd update bd-m3n4 --claim engineer-session-abc123
# ... update docs ...
bd close bd-m3n4 --reason "Documentation updated"
```

---

## Phase 4: Completion Request (Engineer)

All tickets and ACs complete. Engineer proves acceptance criteria:

```bash
# Run tests to prove criteria met
pytest tests/unit/test_audio_codec_validation.py -v
# All tests pass

# Request human approval
bd update bd-a1b2 --status pending_human_approval
bd comment bd-a1b2 "All tickets and ACs complete. Tests pass. Ready for human approval.

Completed ACs (all closed in Beads):
- bd-e5f6: Detect codec mismatch - DONE
- bd-g7h8: Pass when codecs match - DONE
- bd-i9j0: Include both codecs in error - DONE
- bd-k1l2: Add unit tests - DONE

Test Coverage:
- test_codec_mismatch: Verifies ValidationError raised on mismatch
- test_codec_match: Verifies success return on match"
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
bd update bd-a1b2 --status approved  # Resume work
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
  -> pending_approval (Historian submits)
    -> approved (Human grants authority)
      -> in_progress (Engineer claims task)
        -> suspended (Discovery found)
        -> halted (Engineer blocked)
        -> pending_human_approval (Engineer done)
          -> completed (Human approves)
```
