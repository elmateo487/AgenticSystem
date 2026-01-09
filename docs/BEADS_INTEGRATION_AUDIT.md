# BEADS_INTEGRATION.md Audit Report

**Document**: `/Users/minimatt/Developer/system-v1.3/docs/BEADS_INTEGRATION.md`
**Auditor**: Historian (SYSTEM V1.2)
**Date**: 2026-01-09
**Lines Reviewed**: 720

---

## Resolution Status (2026-01-09)

| Issue | Status | Resolution |
|-------|--------|------------|
| CRITICAL-01 | **RESOLVED** | Clarified suspension as "safety mechanism" that halts work, not authority action |
| CRITICAL-02 | **RESOLVED** | Removed auto-close; added `pending_human_approval` state. Engineer must prove criteria with tests before requesting human approval. |
| V1.2 Gap (Tests) | **RESOLVED** | Added dedicated "Test Integrity" section + core principle |
| MEDIUM-01 | **RESOLVED** | Added `rejected` and `abandoned` states to State Definitions |

**Key change for CRITICAL-02**: The completion flow is now:
1. Engineer completes all tasks
2. Engineer writes/runs tests to prove acceptance criteria
3. Engineer moves convoy to `pending_human_approval`
4. Human reviews and approves → `completed`

**Test Integrity additions**:
- New dedicated section (## Test Integrity) establishing tests as sacrosanct
- **Two prohibited responses**: modifying tests OR worsening implementation
- Prohibited actions table (disable, loosen, bypass, gut, skip, mock, degrade, hack)
- HALT protocol for two scenarios: test seems wrong OR implementation would degrade
- Only humans can authorize test modifications or architectural compromises
- Reinforced in Engineer workflow, completion flow, and core principles
- Fourth core principle: "Implementation quality is sacrosanct"

---

## Executive Summary

The BEADS_INTEGRATION.md document provides comprehensive guidance for integrating Beads as the task management layer in SYSTEM V1.3. The document generally preserves V1.2 core principles but contains several issues requiring attention:

- **Critical Issues**: 2 (V1.2 intent breaches) — **RESOLVED**
- **Medium Issues**: 7 (Inconsistencies and clarification needed)
- **Low Issues**: 5 (Minor clarifications)

---

## Category 1: V1.2 Intent Breaches

### CRITICAL-01: Automatic Authority Suspension Bypasses Human Decision

**Location**: Lines 139-153, 110-111

**Issue**: The document states authority is "automatically suspended" by the system when certain triggers occur (description edited, new task added, needs_triage child exists, citation invalid). Line 110-111 explicitly states:

```
| `approved`/`in_progress` | `suspended` | Mutation detected | Beads (auto) |
```

**V1.2 Violation**: V1.2 establishes that "Nothing runs unless explicitly invoked by a human" and "Documentation is the source of truth for authority." Automatic authority changes represent autonomous system action affecting the authority model without human invocation.

**Severity**: CRITICAL

**Recommendation**:
1. Replace automatic suspension with automatic FLAGGING for human review
2. Reword to: "When mutation detected, system PROPOSES suspension; human must confirm"
3. Alternative: Keep automatic suspension but require it be treated as a safety mechanism that still requires human acknowledgment before work resumes (which the document partially addresses)

**Mitigation Note**: The document does require human re-approval to restore authority (line 431), which partially addresses this concern. However, the automatic removal of `authority:granted` is still autonomous action affecting authority state.

---

### CRITICAL-02: Convoy Auto-Close Represents Autonomous State Change

**Location**: Lines 112, 439

**Issue**:
- Line 112: `| in_progress | completed | All children closed | Beads (auto, convoy) |`
- Line 439: "Convoy auto-closes (Beads convoy behavior)"

**V1.2 Violation**: The automatic closure of a plan (convoy) based on child task completion is autonomous system behavior that changes authoritative state without explicit human invocation.

**Severity**: CRITICAL

**Recommendation**:
1. Replace auto-close with human confirmation: "When all tasks closed, convoy moves to `pending_completion` state; human must explicitly close"
2. Or document this as acceptable Beads behavior that does not affect authority (since authority:granted label remains)
3. Clarify whether auto-close removes authority or is purely an organizational state change

---

## Category 2: Internal Inconsistencies

### MEDIUM-01: Conflicting Status Terminology

**Location**: Lines 92-99 vs Lines 665-666

**Issue**: The State Definitions table uses lowercase states (`draft`, `pending_approval`, `approved`, etc.) but the Human Commands Reference uses different values:

- Line 665: `bd update <id> --status approved`
- Line 666: `bd update <id> --status rejected`

The state `rejected` is not defined in the State Definitions table (lines 92-99). The diagram shows `REJECTED / ABANDONED` but the table only shows:
- `draft`, `pending_approval`, `approved`, `in_progress`, `suspended`, `completed`

**Severity**: MEDIUM

**Recommendation**: Add `rejected` and `abandoned` to the State Definitions table, including their labels and meanings.

---

### MEDIUM-02: Inconsistent Task Status Values

**Location**: Lines 381, 509, 681-683, 701

**Issue**: Multiple status values are used for tasks without clear definition:
- Line 381: `--status needs_triage`
- Line 509: `--status ready`
- Line 681: `--status ready`
- Line 682: `--status in_progress`
- Line 683: `--status done`
- Line 701: `--status done`

The document provides State Definitions only for convoy issues (lines 92-99), not for task issues. What are the valid task statuses?

**Severity**: MEDIUM

**Recommendation**: Add a "Task State Definitions" section parallel to the convoy states, defining valid task statuses and their meanings.

---

### MEDIUM-03: Duplicate Workflow Documentation

**Location**: Lines 292-411 ("Agent Workflows") overlaps significantly with Lines 653-702 ("Human Commands Reference")

**Issue**: The same workflows are described twice with slightly different details:
- Agent Workflows section describes what each agent does
- Human Commands Reference includes a "Command Flow Example" that duplicates this

This creates maintenance burden and risk of divergence.

**Severity**: MEDIUM

**Recommendation**: Consolidate into a single "Workflows" section, or clearly differentiate purposes (e.g., "Agent Workflows" for agent behavior, "Command Reference" purely for command syntax without workflow narrative).

---

### MEDIUM-04: Conflicting Claim Syntax

**Location**: Lines 398, 629, 681

**Issue**: Different claim syntaxes shown:
- Line 398: `bd update bd-c3d4 --claim engineer-session-123`
- Line 629: "Atomic claiming (`--claim`)"
- Line 681: `bd update <id> --status in_progress --claim`

Is `--claim` a flag that requires a session ID, or is it a standalone flag? Line 398 suggests an argument is required; line 681 suggests it's a flag.

**Severity**: MEDIUM

**Recommendation**: Clarify the exact `--claim` syntax. If it requires an identifier, document the format (e.g., `--claim <agent-type>-<session-id>`).

---

### MEDIUM-05: Authority Verification Steps Missing from Engineer Workflow

**Location**: Lines 370-411 (Engineer section)

**Issue**: The Engineer workflow (lines 381-390) shows:
```
3. Verify authority (check convoy labels + citations)
```

But the detailed verification steps from lines 158-164 are not referenced:
```
1. Get task's parent convoy
2. Check convoy has label: authority:granted
3. Check no children have status: needs_triage
4. Check all authority_citations resolve to existing sections
5. If any check fails: HALT and report
```

The workflow summary is less rigorous than the detailed specification.

**Severity**: MEDIUM

**Recommendation**: In the Engineer Workflow section, explicitly reference the full verification procedure: "See 'Authority Verification (Engineer)' section above" or inline the complete checklist.

---

### MEDIUM-06: Historian Role Boundary Expansion

**Location**: Lines 313-333, Line 323

**Issue**: Line 323 states Historian should "Research problem (read code, understand scope)" before creating a plan.

**V1.2 Reference**: HISTORIAN_ORIENTATION.md states the Historian "does not execute code" but does not explicitly prohibit reading code.

However, the V1.2 Historian responsibilities focus on:
- Authority docs (INVARIANTS.md, DECISIONS.md)
- Non-authority docs (ARCHITECTURE.md, PIPELINE.md)
- Plans

"Reading code to understand scope" is a new responsibility not present in V1.2.

**Severity**: MEDIUM

**Recommendation**:
1. If this is intentional V1.3 expansion, document it explicitly as a change from V1.2
2. Consider whether this should be an Orchestrator responsibility (providing context to Historian) rather than Historian reading code directly
3. Clarify scope: which files can Historian read? Only source code, or also tests/configs?

---

### MEDIUM-07: Missing Orchestrator Dispatch Criteria for Beads

**Location**: Lines 296-309 (Orchestrator section)

**Issue**: The Orchestrator section describes what the Orchestrator does NOT do (auto-discover via `bd ready`, create issues, execute code) but lacks positive guidance on:
- How Orchestrator determines which plan to invoke Engineer for
- How Orchestrator queries Beads to understand current state
- Whether Orchestrator can run `bd list` or `bd show` commands

V1.2 ORCHESTRATOR_ORIENTATION.md permits "Read files (for context)" - does this extend to `bd show` commands?

**Severity**: MEDIUM

**Recommendation**: Add explicit guidance on what Beads commands Orchestrator may use for read-only context gathering (e.g., `bd list`, `bd show`), and what commands are prohibited (e.g., `bd create`, `bd update`).

---

## Category 3: Clarification Needed

### LOW-01: Undefined "Mutation" Term

**Location**: Lines 85, 110, 139-146, 479

**Issue**: The term "mutation" is used repeatedly but never precisely defined. Lines 143-146 list specific mutation triggers, but "mutation" as a concept is not defined.

**Severity**: LOW

**Recommendation**: Add a definition: "Mutation: Any change to a convoy issue's description, tasks, or authority citations after approval has been granted."

---

### LOW-02: Authority Citations Format Unclear

**Location**: Lines 133-134, 247-248

**Issue**: The citation format uses Markdown heading anchor syntax:
```
authority_citations=INVARIANTS.md#Section-Name,DECISIONS.md#2026-01-01---Decision-Title
```

Questions not addressed:
- How are multi-word section names formatted? (hyphens replacing spaces?)
- What about special characters in section names?
- Is validation case-sensitive?

**Severity**: LOW

**Recommendation**: Add a subsection "Citation Format Specification" documenting:
- Exact anchor generation rules
- Case sensitivity
- Special character handling
- Example citations for complex section names

---

### LOW-03: Archive Naming Convention Incomplete

**Location**: Lines 443-449

**Issue**: Archive files use `YYYY-MM-DD-convoy-title.md` format, but:
- How is "convoy-title" derived from the actual title? (slugification rules)
- What happens with duplicate dates?
- Who performs the export - Historian or Engineer?

**Severity**: LOW

**Recommendation**: Specify:
1. Slugification rules (lowercase, hyphen-separated, special char removal)
2. Collision handling (append `-2`, `-3`, etc.)
3. Responsible agent (likely Historian)

---

### LOW-04: Discovery Limit Undefined

**Location**: Line 564

**Issue**: "Limit discovery creation per task. If too many discoveries, halt and escalate."

What is "too many"? No threshold is provided.

**Severity**: LOW

**Recommendation**: Either:
1. Define a specific threshold (e.g., "3 discoveries per task")
2. Remove the guidance and let human judgment apply
3. Make it configurable per-project

---

### LOW-05: Beads Version Requirement Verification

**Location**: Lines 625-630

**Issue**: Document requires "Beads v0.42.0+" but provides no verification command or guidance on what happens if an older version is used.

**Severity**: LOW

**Recommendation**: Add:
```bash
# Verify Beads version
bd version  # Must be >= 0.42.0
```

And describe behavior with older versions (features unavailable, errors expected, etc.).

---

## Category 4: V1.2 Alignment Verification

The following V1.2 principles are correctly preserved:

| V1.2 Principle | V1.3 Alignment | Evidence |
|----------------|----------------|----------|
| Human invocation only | Preserved | Line 9: "Nothing runs unless explicitly invoked by a human" |
| Documentation as authority source | Preserved | Authority layer remains in files (lines 18-24) |
| Plans define execution scope | Preserved | Convoy issues serve same function |
| Tests define correctness | Not mentioned | **Gap**: Add statement about tests |
| Historian boundary (no code execution) | Preserved | Lines 313-320 show no code execution |
| Engineer boundary (executes plans) | Preserved | Lines 370-411 |
| Orchestrator as dispatcher | Preserved | Lines 296-309 |

**Gap Identified**: V1.2 system constraint "Tests define correctness" is not mentioned in BEADS_INTEGRATION.md. This should be added to the document.

---

## Recommended Actions by Priority

### Immediate (Before V1.3 Deployment)

1. **CRITICAL-01**: Clarify automatic suspension as safety mechanism requiring human acknowledgment
2. **CRITICAL-02**: Clarify auto-close behavior and its relationship to authority
3. **MEDIUM-02**: Add task state definitions

### Before Finalizing Document

4. **MEDIUM-01**: Add rejected/abandoned states
5. **MEDIUM-04**: Clarify --claim syntax
6. **MEDIUM-05**: Reference full authority verification in Engineer workflow
7. **MEDIUM-07**: Add Orchestrator Beads command permissions

### Nice to Have

8. **MEDIUM-03**: Consolidate duplicate workflow sections
9. **MEDIUM-06**: Clarify/document Historian code reading expansion
10. **LOW-01** through **LOW-05**: Address clarification items
11. Add "Tests define correctness" to document

---

## Appendix: Reference Document Checksums

Documents referenced during this audit:
- HISTORIAN_ORIENTATION.md (V1.2): 104 lines
- ORCHESTRATOR_ORIENTATION.md (V1.2): 178 lines
- ENGINEER_ORIENTATION.md (V1.2): 126 lines
- BEADS_INTEGRATION.md (V1.3): 720 lines

---

*Audit completed by Historian agent per SYSTEM V1.2 role boundaries. This audit does not execute code, prioritize work, or create authority. Findings require human review and decision.*
