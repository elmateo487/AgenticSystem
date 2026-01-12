# SYSTEM V1.3 - Beads Integration

> Task management for AI agents using Beads as the single source of truth for plans.

## Overview

SYSTEM V1.3 integrates [Beads](https://github.com/steveyegge/beads) as its task management layer. Plans are Beads issues with type `epic`. Tickets and ACs are issues with type `task` that have a parent field set. Human invocation is the authority - when you invoke an agent, that is the authorization.

**Beads Types**: `epic`, `task`, `blocker` (three distinct types - epics are NOT tasks)

**Parent-Child Relationships**: Tasks with a `--parent` field set, not special "child" types

**Core Principle**: Nothing runs unless explicitly invoked by a human. Beads provides structure; humans provide authorization.

**Key difference from V1.2**: Plans live in Beads, not markdown files. Authority model preserved.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHORITY LAYER (files)                      │
│  authority/INVARIANTS.md    authority/DECISIONS.md              │
│  - Source of truth for constraints and decisions                │
│  - Human-maintained, rarely changes                             │
│  - Beads issues cite these by path                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ cited by (field)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BEADS LAYER (database)                       │
│  .beads/project.db (local)  +  .beads/beads.jsonl (git)        │
│                                                                 │
│  Epic (type: epic) = Plan                                     │
│    - description: Objective, Design, Scope, Criteria            │
│    - authority_citations: ["INVARIANTS.md#Section", ...]        │
│    - labels: scope:*, risk:*, feature:*, type:*                 │
│    └── Tickets (type: task, with --parent bd-EPIC)              │
│        └── ACs (type: task, with --parent bd-TICKET)            │
│        - Dependencies via bd dep add                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ on archive
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ARCHIVE LAYER (files)                        │
│  plans/archive/*.md                                             │
│  - Exported via: bd show <epic> --format markdown             │
│  - Historical reference only                                    │
│  - Created when epic closes                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
project/
├── .beads/
│   ├── project.db        # SQLite database (gitignored)
│   └── beads.jsonl       # Git-committed state (synced)
├── authority/
│   ├── INVARIANTS.md     # Immutable constraints
│   └── DECISIONS.md      # Design decisions with rationale
├── plans/
│   └── archive/          # Exported completed plans (markdown)
├── CLAUDE.md             # Project guidance
└── ... (source code)
```

**Note**: No `plans/active/` directory. Active plans live only in Beads.

---

## Plan Lifecycle

### States

```
DRAFT ──► PENDING_APPROVAL ──► APPROVED ──► IN_PROGRESS ──► PENDING_HUMAN_APPROVAL ──► COMPLETED
  │              │                 │              │                   │
  │              │                 │              ├──► SUSPENDED ◄────┘
  │              │                 │              │       │
  │              │                 │              │       │ (system-triggered)
  │              │                 │              │       │
  │              │                 │              └──► HALTED
  │              │                 │                      │
  │              │                 └──────────────────────┘ (engineer-triggered)
  │              │
  └──────────────┴──► REJECTED / ABANDONED
```

**Key distinction**:
- `SUSPENDED` = System-triggered (mutation detected) - **authority revoked**, plan validity in question
- `HALTED` = Engineer-triggered (cannot proceed) - **authority intact**, plan valid but needs guidance

### State Definitions

| State | Meaning |
|-------|---------|
| `draft` | Historian is creating the plan |
| `pending_approval` | Ready for human review |
| `approved` | Human approved, tasks can be claimed |
| `in_progress` | At least one task claimed |
| `suspended` | Safety halt - work paused |
| `halted` | Engineer halt - needs human guidance |
| `pending_human_approval` | Engineer proved criteria met, awaiting human sign-off |
| `completed` | Human approved completion |
| `rejected` | Human rejected the plan |
| `abandoned` | Plan discontinued before completion |

**Note**: Human invocation is the authority. When you invoke an agent (e.g., `/engineer`), that is the authorization to proceed.

### Transitions

| From | To | Trigger | Actor |
|------|-----|---------|-------|
| - | `draft` | `bd create --type epic` | Historian |
| `draft` | `pending_approval` | `bd update --status pending_approval` | Historian |
| `pending_approval` | `approved` | `bd update --status approved` | Human |
| `pending_approval` | `draft` | `bd update --status draft` (changes requested) | Human |
| `pending_approval` | `rejected` | `bd update --status rejected` | Human |
| `approved` | `in_progress` | First task claimed | Engineer |
| `approved`/`in_progress` | `suspended` | Mutation detected (safety halt) | System |
| `approved`/`in_progress` | `halted` | Engineer cannot proceed | Engineer |
| `suspended` | `approved` | `bd update --status approved` | Human |
| `halted` | `in_progress` | Human provides guidance, Engineer resumes | Human |
| `in_progress` | `pending_human_approval` | All tasks done, tests pass | Engineer |
| `pending_human_approval` | `completed` | Human approves | Human |
| `pending_human_approval` | `suspended` | Human rejects or finds issues | Human |
| `in_progress`/`approved` | `abandoned` | `bd update --status abandoned` | Human |

---

## Authority Model

### Human Invocation is Authority

**Human invocation is the authority.** When you invoke an agent (e.g., `/engineer`), that is the authorization to proceed.

There are no authority labels. The act of invocation by a human grants authority for that specific work.

### Authority Citations

Epic issues must cite their authority:

```bash
bd create "Feature X Implementation" \
  --type epic \
  --field "authority_citations=INVARIANTS.md#Section-Name,DECISIONS.md#2026-01-01---Decision-Title"
```

### Authority Suspension (Safety Mechanism)

Suspension is a **safety halt**, not an authority action. It does not grant permission to do anything—it blocks all work until a human reviews the situation. This preserves V1.2's principle that only humans control authority.

**Automatic suspension triggers**:

| Trigger | Reason |
|---------|--------|
| Description edited | Plan changed without re-approval |
| New task added | Scope expanded without approval |
| `needs_triage` child exists | Unaddressed discovery |
| Citation becomes invalid | Authority file section removed/renamed |

**What happens on suspension**:
1. Epic status changes to `suspended`
2. System adds comment explaining trigger
3. **All work halts** - no tasks can be claimed or executed
4. Human must review and explicitly re-approve to resume

### Starting Work (Engineer)

When invoked by a human, the Engineer:

```
1. Reads /tmp/work.json (pre-exported by Orchestrator)
2. Reads authority docs if they exist
3. Begins work on specified ticket/epic
```

---

## Test Integrity

Tests define correctness. This is a V1.2 principle that V1.3 preserves and strengthens.

### Principle

The implementation must satisfy the tests—never the reverse. If tests fail, the Engineer must fix the implementation **properly** or halt for human guidance.

**Two prohibited responses to failing tests**:
1. Modifying the test to make it pass
2. Worsening the implementation to make it pass

If the only way to pass a test is to make an architectural decision that degrades the codebase—adding hacks, introducing technical debt, bypassing good patterns, or making the code worse—the Engineer must HALT and request guidance. A passing test achieved through a worse implementation is not a success.

### What Engineer May Do

- **Write new tests** to validate acceptance criteria not covered by existing tests
- **Run existing tests** to prove criteria are met
- **Fix implementation** when tests reveal bugs
- **Add test coverage** for edge cases discovered during implementation

### Prohibited Actions

The following actions violate test integrity and are **never permitted** without human authorization:

| Action | Why Prohibited |
|--------|----------------|
| Disabling tests | Hides failures instead of fixing them |
| Loosening assertions | Changes the definition of correctness |
| Bypassing test execution | Skips proof of correctness |
| Removing/gutting test content | Destroys institutional knowledge |
| Skipping via markers or flags | Same as disabling |
| Mocking away tested behavior | Removes the actual check |
| Degrading implementation to pass | Trades code quality for green tests |
| Adding hacks/workarounds to pass | Technical debt is not a fix |

### When to HALT

Engineer must HALT and request human guidance when:

1. **Test cannot pass without modifying it** - The test expects behavior the implementation cannot provide
2. **Test can only pass by worsening the implementation** - Passing requires hacks, technical debt, or architectural degradation

**HALT procedure**:

1. **Stop immediately** - Do not proceed with either a test change or a bad implementation
2. **Move epic to `halted` status with label**:
   ```bash
   # If test seems wrong:
   bd update bd-EPIC --status halted --label "halted:test-conflict"
   bd comment bd-EPIC "HALTED: test_X fails. Test expects Y but implementation does Z. Need guidance on which is correct."

   # If implementation would need to worsen:
   bd update bd-EPIC --status halted --label "halted:arch-degradation"
   bd comment bd-EPIC "HALTED: test_X fails. Can only pass by [describe hack/degradation]. Need guidance on approach."
   ```
3. **Wait for human decision** - Human can discover halted plans via:
   ```bash
   bd list --status halted
   ```
4. **Human resolves** by:
   - Clarifying that the test is wrong (authorizes test change)
   - Clarifying that implementation approach is wrong (Engineer revises properly)
   - Authorizing the architectural trade-off (if justified)
   - Adjusting acceptance criteria (plan scope change)
5. **Human resumes work**:
   ```bash
   bd update bd-EPIC --status in_progress
   bd comment bd-EPIC "Guidance: [decision]. Resume work."
   ```

**Only humans can authorize test modifications or architectural compromises.**

---

## Linking and Relationships

### Dependency Types

Beads supports four dependency types:

| Type | Command | Meaning | Use Case |
|------|---------|---------|----------|
| `parent-child` | `--parent bd-xyz` | Hierarchical containment | Epic → Tasks |
| `blocks` | `bd dep add A B --type blocks` | A must close before B starts | Task ordering |
| `related` | `bd dep add A B --type related` | Informational link | Cross-references |
| `discovered-from` | `--discovered-from bd-xyz` | Issue originated from task | Discovery tracking |

### Cross-Plan Dependencies

Plans can depend on other plans:

```bash
# Task in Plan A blocks on Plan B completing
bd dep add bd-PLAN-A-TASK bd-PLAN-B-EPIC --type blocks

# Task in Plan A blocks on specific task in Plan B
bd dep add bd-PLAN-A-TASK bd-PLAN-B-TASK --type blocks
```

**Rules**:
- Cross-plan deps use the same `blocks` type
- Authority verification follows the dependency chain
- If blocked-on plan loses authority, blocking task cannot proceed

### Relationship Queries

```bash
# Find all tasks blocked by a epic
bd dep tree bd-EPIC

# Find what blocks a specific task
bd show bd-TASK --json | jq '.blocked_by'

# Find all related issues
bd list --related-to bd-ISSUE
```

---

## Label Taxonomy

### Required Labels (Epic)

Every epic (plan) **must** have these labels:

| Prefix | Values | Description |
|--------|--------|-------------|
| `feature:` | Project-specific | Feature/epic grouping (e.g., `feature:rasl-repair`) |
| `scope:` | `services`, `stages`, `gui`, `pipeline`, `tests`, `docs` | Codebase area affected |
| `type:` | `feature`, `bugfix`, `refactor`, `docs`, `research` | Type of work |
| `risk:` | `low`, `medium`, `high`, `critical` | Risk assessment |
| `priority:` | `critical`, `high`, `normal`, `low` | Execution priority |

### System Labels (Managed by System)

| Label | Set By | Meaning |
|-------|--------|---------|
| `halted:test-conflict` | Engineer | Blocked: test expects behavior implementation cannot provide |
| `halted:arch-degradation` | Engineer | Blocked: test can only pass by worsening implementation |
| `archived` | System | Plan completed and exported |

**Note**: `halted:*` labels indicate Engineer needs guidance but plan is still valid.

### Example Epic Creation

```bash
bd create "Fix RASL Hybrid Seek Bug" \
  --type epic \
  --status draft \
   \
  --label "feature:rasl-repair" \
  --label "scope:services" \
  --label "type:bugfix" \
  --label "risk:medium" \
  --label "priority:high" \
  --field "authority_citations=INVARIANTS.md#DV-Frame-Exact,DECISIONS.md#Hybrid-Cutting" \
  --description "..."
```

### Task Labels

Tasks (children of epic) **do not** have required labels. They inherit context from their parent epic.

Optional task labels:
- `blocked` - Manually mark as blocked (in addition to dep-based blocking)
- `wontfix` - Marked as won't implement

### Label Validation

Historian **must** verify before submitting for approval:
1. All required label prefixes present on epic
2. Values are from allowed set

Engineer works when invoked by human - no label verification needed.

### Querying by Labels

```bash
# Find all plans for a feature
bd list --type epic --label "feature:rasl-repair"

# Find high-priority bugfixes
bd list --type epic --label "type:bugfix" --label "priority:high"

# Find approved plans ready for work
bd list --type epic 
# Find suspended plans needing attention
bd list --type epic --label "authority:suspended"

# Find all work in a scope area
bd list --type epic --label "scope:services"
```

---

## Agent Workflows

### Orchestrator

**Role**: Dispatch work to Historian or Engineer based on human requests.

**Does NOT**:
- Auto-discover work via `bd ready`
- Create issues directly
- Execute code

**Workflow**:
```
Human: "Create a plan for feature X"
  └─► Orchestrator invokes Historian
Human: "Execute plan X"
  └─► Orchestrator invokes Engineer
```

### Historian

**Role**: Create and maintain plans (epic issues) in Beads.

**Commands used**:
- `bd create` - Create epic and task issues
- `bd update` - Move to pending_approval
- `bd comment` - Add worklog entries
- `bd show` - Export to markdown on archive

**Workflow**:
```
1. Research problem (read code, understand scope)
2. Create epic issue with:
   - Title
   - Description (objective, design, scope, criteria)
   - Required labels (feature, scope, type, risk, priority)
3. Create task issues as children
4. Add dependencies between tasks (bd dep add)
5. Move epic to pending_approval
6. Wait for human approval
```

**Example** (3-level hierarchy):
```bash
# Level 1: Create epic with CONTEXT only (no AC checkboxes)
bd create "RASL Hybrid Seek Fix" \
  --type epic \
  --status draft \
   \
  --field "authority_citations=INVARIANTS.md#DV-Frame-Exact,DECISIONS.md#Hybrid-Cutting" \
  --description "## Problem Statement
Hybrid seeking bug causes frame leakage at cut boundaries.

## Technical Context
FFmpeg hybrid seek has known issues with certain codecs.
mkvmerge provides more reliable extraction.

## Design Rationale
Replace FFmpeg with mkvmerge for extraction phase."

# Level 2: Create tickets with INSTRUCTIONS
bd create "Implement mkvmerge extraction" --parent bd-EPIC --priority 1 \
  --description "## Implementation
- Replace FFmpeg extraction with mkvmerge
- Update video_repair_service.py

## Files to Modify
- src/services/video_repair_service.py"

# Level 3: Create ACs as tasks with --parent (NOT checkboxes in descriptions)
bd create "No curated frames in clean output at 6775s" --parent bd-TICKET1 --priority 1
bd create "Frame count validation passes" --parent bd-TICKET1 --priority 2
bd create "Add unit tests for edge cases" --parent bd-TICKET1 --priority 3

bd create "Create test fixture" --parent bd-EPIC --priority 2
bd create "Validate with full test suite" --parent bd-EPIC --priority 3

# Add dependencies between tickets
bd dep add bd-TICKET2 bd-TICKET1 --type blocks
bd dep add bd-TICKET3 bd-TICKET2 --type blocks

# Submit for approval
bd update bd-EPIC --status pending_approval
```

**3-Level Hierarchy Rule**:
| Level | Beads Type | Contains | Has Children |
|-------|------------|----------|--------------|
| 1 | `epic` | Problem context, rationale | Yes (tickets) |
| 2 | `task` | Implementation details | Yes (ACs) |
| 3 | `task` | Single actionable task | **No** (leaf node) |

**Note**: Both tickets (level 2) and ACs (level 3) use Beads type `task`. The hierarchy is created via the `--parent` field, not via different types.

**Rule**: Acceptance Criteria (level 3) are leaf nodes - no further nesting, no checkboxes in descriptions.

### Engineer

**Role**: Execute tasks within approved plans. Prove acceptance criteria before completion.

**Commands used**:
- `bd ready` - Find next unblocked task (when directed by human)
- `bd update --claim` - Atomically claim a task
- `bd update --status pending_human_approval` - Request completion approval (after tests pass)
- `bd comment` - Log progress
- `bd create` - Surface discovered work (goes to needs_triage)
- `bd close` - Complete tasks

**Workflow**:
```
1. Human says "work on plan X" or "what's next?"
2. bd ready --parent bd-EPIC --limit 1
3. Verify authority (check epic labels + citations)
4. bd update bd-TASK --claim engineer-id
5. Execute the work
6. If discovery: bd create --status needs_triage --discovered-from bd-TASK
7. bd close bd-TASK --reason "Completed"
8. When ALL tasks done:
   a. Write new tests or run existing tests to prove acceptance criteria
   b. If tests pass: bd update bd-EPIC --status pending_human_approval
   c. If tests fail: Fix implementation (NOT the tests) or HALT for human
```

**Test Integrity**: Tests may NOT be disabled, loosened, bypassed, gutted, or skipped. Implementation may NOT be degraded or hacked to pass tests. If a test cannot pass properly, HALT and escalate to human.

**Example**:
```bash
# Find ready work
bd ready --parent bd-a1b2 --json --limit 1

# Claim task
bd update bd-c3d4 --claim engineer-session-123

# Log progress
bd comment bd-c3d4 "Extracted test fixture, starting implementation"

# Discover new work (goes to needs_triage, suspends authority)
bd create "Found: mkvmerge version requirement" \
  --type blocker \
  --status needs_triage \
  --discovered-from bd-c3d4

# Complete task
bd close bd-c3d4 --reason "Test fixture created at tests/fixtures/"

# When all tasks done - prove criteria and request approval
bd comment bd-a1b2 "All tasks complete. Running acceptance tests..."
# (write new tests or run existing tests)

# If tests PASS:
bd update bd-a1b2 --status pending_human_approval
bd comment bd-a1b2 "Tests pass. Ready for human approval."

# If tests FAIL and can fix implementation:
# Fix the implementation, re-run tests, then request approval

# If tests FAIL and cannot fix without modifying test - HALT:
bd update bd-a1b2 --status halted --label "halted:test-conflict"
bd comment bd-a1b2 "HALTED: test_frame_count fails. Implementation produces 1847 frames, test expects 1850. Cannot proceed without guidance."

# If tests FAIL and can only pass by worsening implementation - HALT:
bd update bd-a1b2 --status halted --label "halted:arch-degradation"
bd comment bd-a1b2 "HALTED: test_sync fails. Can only pass by adding 500ms sleep hack. This would degrade performance. Need guidance."

# DO NOT: disable test, loosen assertion, skip test, mock the check, add hacks, degrade architecture
```

---

## Discovery Handling

When an Engineer discovers new work during execution:

1. **Create issue** with `--status needs_triage`
2. **Link** to source task with `--discovered-from`
3. **Authority suspended** on epic (automatic)
4. **Work pauses** until human triages

**Human triage options**:
- Add to current plan: `bd update bd-NEW --parent bd-EPIC --status approved`
- Create new plan: Historian creates separate epic
- Dismiss: `bd close bd-NEW --reason "Not needed"`
- Workaround: `bd close bd-NEW --reason "Workaround: ..."`

After triage, if no `needs_triage` children remain:
- Human re-approves: `bd update bd-EPIC --status approved`

---

## Plan Completion

Plan completion is a two-step process: **Engineer proves criteria**, then **Human approves**.

### Completion Flow

**Step 1: Engineer proves acceptance criteria (all tasks done)**

When all tasks are complete, Engineer must:
1. Write new tests or run existing tests that validate the plan's acceptance criteria
2. Verify deliverables match the plan's scope
3. Confirm no regressions or unintended changes
4. Move to pending_human_approval:
   ```bash
   bd update bd-EPIC --status pending_human_approval
   bd comment bd-EPIC "All tasks complete. Tests pass. Ready for human approval."
   ```

**Test Integrity Rule**: Tests may NOT be disabled, loosened, bypassed, gutted, or skipped to make them pass. If a test cannot pass with the current implementation, the Engineer must HALT and request human guidance.

**Step 2: Human approves completion**

Human reviews Engineer's work and either:
```bash
# Approve - plan is complete
bd update bd-EPIC --status completed

# Reject - needs more work
bd update bd-EPIC --status suspended --label authority:suspended
bd comment bd-EPIC "Issues found: [describe problems]"
```

**Step 3: Archive (after completion)**

1. **Export to archive**: `bd show bd-EPIC --format markdown > plans/archive/epic-title.md`
2. **Add archived label**: `bd update bd-EPIC --label archived`

### Test Failure During Completion

If tests fail when Engineer attempts to prove criteria:
- Engineer does NOT move to `pending_human_approval`
- Engineer must fix issues and re-run tests
- If fix is out of scope, Engineer creates discovery issue (`--status needs_triage`)

**Critical**: Engineer must **HALT immediately** and escalate to human when:
- A test cannot pass without modifying the test itself
- A test can only pass by degrading the implementation (hacks, workarounds, technical debt)

```bash
# Test seems wrong - move to halted status:
bd update bd-EPIC --status halted --label "halted:test-conflict"
bd comment bd-EPIC "HALTED: Test X fails. Test expects A but implementation does B. Requesting guidance."

# Implementation would need to worsen - move to halted status:
bd update bd-EPIC --status halted --label "halted:arch-degradation"
bd comment bd-EPIC "HALTED: Test X fails. Can only pass by [describe degradation]. Requesting guidance on approach."
```

**Human discovers halted plans**: `bd list --status halted`

**Prohibited actions**:
- Disabling the failing test
- Loosening test assertions to make them pass
- Bypassing test execution
- Removing or "gutting" test content
- Skipping tests via markers or flags
- Mocking away the behavior being tested
- Adding hacks or workarounds to make tests pass
- Degrading architecture or code quality to satisfy tests

These actions violate the principle that tests define correctness. The implementation must satisfy the tests **properly**, not through compromise.

**Archive file structure**:
```
plans/archive/
├── 2026-01-09-rasl-hybrid-seek-fix.md
├── 2026-01-08-storage-location-audit.md
└── ...
```

**Key principle**: Engineer must prove acceptance criteria are met with passing tests before requesting human approval. Human provides final sign-off.

---

## Failure Modes and Recovery

### Authority Failures

#### Citation Becomes Invalid

**Trigger**: Human edits INVARIANTS.md or DECISIONS.md, removing/renaming a cited section.

**Detection**: Engineer runs authority verification before claiming task.

**Recovery**:
```bash
# 1. Identify invalid citation
bd show bd-EPIC --json | jq '.fields.authority_citations'

# 2. Human decides:
#    a) Update authority doc to restore section
#    b) Update epic with new valid citation
bd update bd-EPIC --field "authority_citations=INVARIANTS.md#New-Section"

# 3. Re-approve
bd update bd-EPIC ```

#### Authority Suspended Mid-Execution

**Trigger**: Plan mutates while Engineer is working (new task added, description changed, needs_triage child).

**Detection**: Engineer's next `bd ready` or claim attempt fails authority check.

**Recovery**:
```bash
# 1. Engineer halts current work (don't commit incomplete changes)

# 2. Identify suspension reason
bd show bd-EPIC  # Check for authority:suspended, needs_triage children

# 3. Human reviews and either:
#    a) Approves the mutation
bd update bd-EPIC #    b) Reverts the mutation
bd update bd-EPIC --description "original description..."
bd close bd-NEW-TASK --reason "Rejected"
```

#### Task Claimed but Authority Lost

**Trigger**: Engineer claims task, then authority suspended before completion.

**Recovery**:
```bash
# 1. Engineer must stop work immediately
# 2. Do NOT close the task
# 3. Do NOT commit changes

# 4. Unclaim the task (return to ready pool)
bd update bd-TASK --status ready --assignee ""

# 5. Wait for human to resolve issue
# 6. Re-claim when human re-invokes
```

### Human Interaction Failures

#### Plan Never Approved

**Trigger**: Historian submits plan, human doesn't respond.

**Detection**: Plan sits in `pending_approval` for extended period.

**Recovery**:
```bash
# Option 1: Human approves
bd update bd-EPIC --status approved 
# Option 2: Human requests changes
bd comment bd-EPIC "Need to clarify scope for X"
bd update bd-EPIC --status draft

# Option 3: Human rejects
bd close bd-EPIC --reason "Not needed / out of scope"
```

**Prevention**: Orchestrator can surface stale pending_approval epics:
```bash
bd list --type epic --status pending_approval
```

#### Discoveries Never Triaged

**Trigger**: Engineer discovers issues, human doesn't triage them.

**Detection**: Authority suspended, `needs_triage` children accumulate.

**Recovery**:
```bash
# 1. List untriaged discoveries
bd list --status needs_triage --parent bd-EPIC

# 2. For each, human decides:
#    a) Add to plan
bd update bd-DISCOVERY --status approved
#    b) Defer to new plan
bd update bd-DISCOVERY --parent ""  # Remove from this epic
#    c) Dismiss
bd close bd-DISCOVERY --reason "Won't fix / duplicate / not needed"

# 3. Once all triaged, restore authority
bd update bd-EPIC ```

**Prevention**: Limit discovery creation per task. If too many discoveries, halt and escalate.

#### Human Modifies Authority Docs After Approval

**Trigger**: INVARIANTS.md or DECISIONS.md changed after plan approved.

**Detection**: Next authority verification fails (citation invalid).

**Impact**: All plans citing modified sections become suspended.

**Recovery**:
```bash
# 1. Identify affected plans
bd list --type epic --status approved | while read id; do
  # Check each plan's citations
  bd show $id --json | jq '.fields.authority_citations'
done

# 2. For each affected plan:
#    a) Update citation to new section name
#    b) Or acknowledge the authority doc change invalidates the plan

# 3. Re-approve valid plans
bd update bd-EPIC --status approved
```

**Prevention**: Authority docs should be changed rarely. Consider requiring plan review before authority doc changes.

### Recovery Commands Reference

| Situation | Command |
|-----------|---------|
| Check why suspended | `bd show bd-EPIC` |
| List needs_triage | `bd list --status needs_triage --parent bd-EPIC` |
| Resume work | `bd update bd-EPIC --status approved` |
| Unclaim task | `bd update bd-TASK --status ready --assignee ""` |
| Close discovery | `bd close bd-DISCOVERY --reason "..."` |
| List stale plans | `bd list --type epic --status pending_approval` |

---

## Beads Setup

### Initialize Beads in a project

```bash
cd /path/to/project
bd init --prefix projectname --quiet
```

This creates:
- `.beads/projectname.db` - SQLite database
- `.beads/beads.jsonl` - Git-synced state
- Git hooks for auto-sync

### .gitignore

```
.beads/*.db
```

### Required Beads version

V1.3 requires Beads v0.42.0+ for:
- Epic issues (auto-close when children done)
- Atomic claiming (`--claim`)
- State management

---

## Migration from V1.2

Projects migrating from V1.2 markdown plans:

1. **Keep authority files** - No change to INVARIANTS.md, DECISIONS.md
2. **Initialize Beads** - `bd init --prefix project`
3. **Import active plans** - Create epic issues from existing plans/active/*.md
4. **Archive old plans** - Move plans/active/*.md to plans/archive/ (historical reference)
5. **Update CLAUDE.md** - Reference V1.3 skills

**Active plan migration**:
```bash
# For each active plan, create epic + tasks in Beads
# Then archive the markdown file
mv plans/active/PLAN-X.md plans/archive/migrated-PLAN-X.md
```

---

## Human Commands Reference

Commands are split between those humans invoke directly and those the orchestrator invokes on their behalf.

### Human Direct Commands

These commands are executed by the human directly in terminal:

| Command | Purpose | When Used |
|---------|---------|-----------|
| `bd show <id>` | View issue details | Reviewing plan/task status |
| `bd list [filters]` | List issues | Finding work, checking status |
| `bd list --status halted` | Find halted plans needing guidance | Discovering blocked work |
| `bd update <id> --status approved` | Approve plan for execution | After reviewing plan |
| `bd update <id> --status completed` | Approve plan completion | After Engineer proves criteria |
| `bd update <id> --status in_progress` | Resume halted plan | After providing guidance |
| `bd update <id> --status rejected` | Reject plan | Plan needs revision |
| `bd close <id> --reason "..."` | Close issue | Dismissing discoveries, completing work |
| `bd close $(bd list --parent <epic> --json \| jq -r '.[].id') <epic> --reason "..."` | Close epic AND all children | Closing entire plan (beads does not cascade) |
| `bd comment <id> "..."` | Add comment | Providing feedback, notes |
| `bd dep tree <id>` | View dependency graph | Understanding blockers |

### Orchestrator-Invoked Commands

These commands are invoked by agents (Historian, Engineer) on behalf of the human:

| Command | Purpose | Which Agent |
|---------|---------|-------------|
| `bd create --type epic ...` | Create new plan | Historian |
| `bd create --parent <epic> ...` | Create task under plan | Historian |
| `bd dep add <from> <to> --type blocks` | Add dependency | Historian |
| `bd update <id> --status ready` | Mark task ready for work | Historian |
| `bd update <id> --status in_progress --claim` | Claim and start work | Engineer |
| `bd update <id> --status done` | Complete task | Engineer |
| `bd update <id> --status halted --label "halted:*"` | HALT - cannot proceed without guidance | Engineer |
| `bd update <id> --status pending_human_approval` | Request completion approval (tests pass) | Engineer |
| `bd update <id> --status needs_triage` | Flag discovery for human | Engineer |

### Command Flow Example

```
Human: "Plan a new feature for X"
    └── Orchestrator invokes Historian
        └── Historian: bd create --type epic "Feature X plan"
        └── Historian: bd create --parent bd-001 "Task 1"
        └── Historian: bd create --parent bd-001 "Task 2"
        └── Historian: bd update bd-001 --status pending_approval
Human: "Looks good, approved"
    └── Human: bd update bd-001 --status approved Human: "Execute the plan"
    └── Orchestrator invokes Engineer
        └── Engineer: bd ready --parent bd-001
        └── Engineer: bd update bd-002 --status in_progress --claim
        └── Engineer: (executes work)
        └── Engineer: bd update bd-002 --status done
        └── Engineer: (all tasks done, runs tests to prove criteria met)
        └── Engineer: bd update bd-001 --status pending_human_approval
Human: (reviews Engineer's work)
    └── Human: bd update bd-001 --status completed
```

---

## Summary

| Concept | V1.2 | V1.3 |
|---------|------|------|
| Plan storage | Markdown files | Beads epic issues |
| Task tracking | Checkboxes | Beads tasks (type: task with --parent) |
| Authority grant | Text in file | Label on issue |
| Progress | Worklog in file | Comments on issue |
| Dependencies | Implicit ordering | Explicit `bd dep add` |
| Discovery | Update plan file | `--status needs_triage` |
| Plan completion | Human moves file | Engineer proves with tests → Human approves |
| Archive | Move file | Export + label |
| Multi-agent | Manual coordination | Atomic claiming |
| Suspension | N/A | Safety halt (not authority) |

**Core principles unchanged**:
- Nothing runs unless explicitly invoked by a human
- Tests define correctness—Engineer must prove criteria before human approval
- Tests are sacrosanct—they cannot be disabled, loosened, bypassed, gutted, or skipped
- Implementation quality is sacrosanct—code cannot be degraded or hacked to pass tests
