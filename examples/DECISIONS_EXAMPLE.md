# SYSTEM V1.3 — Beads-Integrated Invocation-Only Agent Architecture

## Core Principles
- Nothing runs unless explicitly invoked by a human
- Tests define correctness
- Tests are sacrosanct
- Implementation quality is sacrosanct

# DECISIONS — Example

## 2026-01-08 — Audio Codec Validation
**Scope**
Feature-specific (Validation Stage)

**Context**
Users reported audio codec changes in some outputs. Need to catch this during validation.

**Decision**
Add explicit audio codec validation that compares input and output codecs via ffprobe.

**Alternatives**
- A: Rely on stream copy to preserve codec (rejected: doesn't catch edge cases)
- B: Add validation check (chosen: explicit verification)

**Consequences**
- Enables: Early detection of codec mismatches
- Forbids: Silent codec changes

**Status**
Active

---

## 2026-01-09 — Beads for Task Management
**Scope**
Project-wide

**Context**
File-based plans in `plans/active/` require manual status tracking and don't support concurrent work well.

**Decision**
Migrate to Beads convoy issues for plan management. Authority documents remain file-based.

**Alternatives**
- A: Keep file-based plans (rejected: poor concurrent support)
- B: Full Beads migration including authority (rejected: authority needs version control)
- C: Hybrid: Beads for plans, files for authority (chosen)

**Consequences**
- Enables: Better task tracking, concurrent work, status queries
- Forbids: File-based plans in `plans/active/`

**Status**
Active
