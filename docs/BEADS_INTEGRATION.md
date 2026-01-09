# SYSTEM V1.3 - Beads Integration

> Task management for AI agents using Beads as the single source of truth for plans.

## Overview

SYSTEM V1.3 integrates [Beads](https://github.com/steveyegge/beads) as its task management layer. Plans are Beads convoy issues. Tasks are child issues. Authority is enforced via labels and citations to authority documents.

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
│  Convoy Issue = Plan                                            │
│    - description: Objective, Design, Scope, Criteria            │
│    - authority_citations: ["INVARIANTS.md#Section", ...]        │
│    - labels: authority:granted, scope:*, risk:*                 │
│    └── Child Issues = Tasks                                     │
│        - Flat structure (no sub-tasks)                          │
│        - Dependencies via bd dep add                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ on archive
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     ARCHIVE LAYER (files)                        │
│  plans/archive/*.md                                             │
│  - Exported via: bd show <convoy> --format markdown             │
│  - Historical reference only                                    │
│  - Created when convoy closes                                   │
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

| State | Labels | Meaning |
|-------|--------|---------|
| `draft` | `authority:pending` | Historian is creating the plan |
| `pending_approval` | `authority:pending` | Ready for human review |
| `approved` | `authority:granted` | Human approved, tasks can be claimed |
| `in_progress` | `authority:granted` | At least one task claimed |
| `suspended` | `authority:suspended` | Safety halt (system-triggered) - mutation detected, authority revoked |
| `halted` | `authority:granted`, `halted:*` | Engineer halt - cannot proceed without human guidance, authority intact |
| `pending_human_approval` | `authority:granted` | Engineer proved criteria met, awaiting human sign-off |
| `completed` | `authority:granted`, `archived` | Human approved completion, plan closed |
| `rejected` | - | Human rejected the plan |
| `abandoned` | - | Plan discontinued before completion |

**Note on `suspended`**: Suspension is a **safety mechanism**, not an authority action. It does not grant authority to do anything—it revokes the ability to proceed until human review. This preserves V1.2's principle that humans control all authority grants.

### Transitions

| From | To | Trigger | Actor |
|------|-----|---------|-------|
| - | `draft` | `bd create --type convoy` | Historian |
| `draft` | `pending_approval` | `bd update --status pending_approval` | Historian |
| `pending_approval` | `approved` | `bd update --status approved --label authority:granted` | Human |
| `pending_approval` | `draft` | `bd update --status draft` (changes requested) | Human |
| `pending_approval` | `rejected` | `bd update --status rejected` | Human |
| `approved` | `in_progress` | First task claimed | Engineer |
| `approved`/`in_progress` | `suspended` | Mutation detected (safety halt) | System |
| `approved`/`in_progress` | `halted` | Engineer cannot proceed | Engineer |
| `suspended` | `approved` | `bd update --label authority:granted` | Human |
| `halted` | `in_progress` | Human provides guidance, Engineer resumes | Human |
| `in_progress` | `pending_human_approval` | All tasks done, tests pass | Engineer |
| `pending_human_approval` | `completed` | Human approves | Human |
| `pending_human_approval` | `suspended` | Human rejects or finds issues | Human |
| `in_progress`/`approved` | `abandoned` | `bd update --status abandoned` | Human |

---

## Authority Model

### Authority Grant

Authority is represented by the `authority:granted` label on a convoy issue.

**Requirements for authority:granted**:
1. Convoy has `authority_citations` field with valid citations
2. All cited sections exist in authority files
3. Human explicitly added the label

### Authority Citations

Convoy issues must cite their authority:

```bash
bd create "Feature X Implementation" \
  --type convoy \
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
1. System removes `authority:granted` label
2. System adds `authority:suspended` label
3. System adds comment explaining trigger
4. **All work halts** - no tasks can be claimed or executed
5. Human must review and explicitly re-approve to resume

### Authority Verification (Engineer)

Before executing any task:

```
1. Get task's parent convoy
2. Check convoy has label: authority:granted
3. Check no children have status: needs_triage
4. Check all authority_citations resolve to existing sections
5. If any check fails: HALT and report
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
2. **Move convoy to `halted` status with label**:
   ```bash
   # If test seems wrong:
   bd update bd-CONVOY --status halted --label "halted:test-conflict"
   bd comment bd-CONVOY "HALTED: test_X fails. Test expects Y but implementation does Z. Need guidance on which is correct."

   # If implementation would need to worsen:
   bd update bd-CONVOY --status halted --label "halted:arch-degradation"
   bd comment bd-CONVOY "HALTED: test_X fails. Can only pass by [describe hack/degradation]. Need guidance on approach."
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
   bd update bd-CONVOY --status in_progress
   bd comment bd-CONVOY "Guidance: [decision]. Resume work."
   ```

**Only humans can authorize test modifications or architectural compromises.**

---

## Linking and Relationships

### Dependency Types

Beads supports four dependency types:

| Type | Command | Meaning | Use Case |
|------|---------|---------|----------|
| `parent-child` | `--parent bd-xyz` | Hierarchical containment | Convoy → Tasks |
| `blocks` | `bd dep add A B --type blocks` | A must close before B starts | Task ordering |
| `related` | `bd dep add A B --type related` | Informational link | Cross-references |
| `discovered-from` | `--discovered-from bd-xyz` | Issue originated from task | Discovery tracking |

### Cross-Plan Dependencies

Plans can depend on other plans:

```bash
# Task in Plan A blocks on Plan B completing
bd dep add bd-PLAN-A-TASK bd-PLAN-B-CONVOY --type blocks

# Task in Plan A blocks on specific task in Plan B
bd dep add bd-PLAN-A-TASK bd-PLAN-B-TASK --type blocks
```

**Rules**:
- Cross-plan deps use the same `blocks` type
- Authority verification follows the dependency chain
- If blocked-on plan loses authority, blocking task cannot proceed

### Relationship Queries

```bash
# Find all tasks blocked by a convoy
bd dep tree bd-CONVOY

# Find what blocks a specific task
bd show bd-TASK --json | jq '.blocked_by'

# Find all related issues
bd list --related-to bd-ISSUE
```

---

## Label Taxonomy

### Required Labels (Convoy)

Every convoy (plan) **must** have these labels:

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
| `authority:pending` | Historian | Awaiting approval |
| `authority:granted` | Human | Approved for execution |
| `authority:suspended` | System | Authority revoked - plan mutated, needs re-approval |
| `halted:test-conflict` | Engineer | Blocked: test expects behavior implementation cannot provide |
| `halted:arch-degradation` | Engineer | Blocked: test can only pass by worsening implementation |
| `archived` | System | Plan completed and exported |

**Note**: `halted:*` labels do NOT revoke authority. The plan is still valid; Engineer just needs guidance.

### Example Convoy Creation

```bash
bd create "Fix RASL Hybrid Seek Bug" \
  --type convoy \
  --status draft \
  --label "authority:pending" \
  --label "feature:rasl-repair" \
  --label "scope:services" \
  --label "type:bugfix" \
  --label "risk:medium" \
  --label "priority:high" \
  --field "authority_citations=INVARIANTS.md#DV-Frame-Exact,DECISIONS.md#Hybrid-Cutting" \
  --description "..."
```

### Task Labels

Tasks (children of convoy) **do not** have required labels. They inherit context from their parent convoy.

Optional task labels:
- `blocked` - Manually mark as blocked (in addition to dep-based blocking)
- `wontfix` - Marked as won't implement

### Label Validation

Historian **must** verify before submitting for approval:
1. All required label prefixes present on convoy
2. Values are from allowed set
3. `authority:pending` label set

Engineer **must** verify before claiming:
1. Parent convoy has `authority:granted`
2. No `authority:suspended` label

### Querying by Labels

```bash
# Find all plans for a feature
bd list --type convoy --label "feature:rasl-repair"

# Find high-priority bugfixes
bd list --type convoy --label "type:bugfix" --label "priority:high"

# Find approved plans ready for work
bd list --type convoy --label "authority:granted"

# Find suspended plans needing attention
bd list --type convoy --label "authority:suspended"

# Find all work in a scope area
bd list --type convoy --label "scope:services"
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

**Role**: Create and maintain plans (convoy issues) in Beads.

**Commands used**:
- `bd create` - Create convoy and task issues
- `bd update` - Move to pending_approval
- `bd comment` - Add worklog entries
- `bd show` - Export to markdown on archive

**Workflow**:
```
1. Research problem (read code, understand scope)
2. Create convoy issue with:
   - Title
   - Description (objective, design, scope, criteria)
   - authority_citations field
   - authority:pending label
3. Create task issues as children
4. Add dependencies between tasks (bd dep add)
5. Move convoy to pending_approval
6. Wait for human approval
```

**Example**:
```bash
# Create plan (convoy)
bd create "RASL Hybrid Seek Fix" \
  --type convoy \
  --status draft \
  --label "authority:pending" \
  --field "authority_citations=INVARIANTS.md#DV-Frame-Exact,DECISIONS.md#Hybrid-Cutting" \
  --description "## Objective
Fix the hybrid seeking bug...

## Technical Design
Replace FFmpeg hybrid seek with mkvmerge...

## Scope
- Included: video_repair_service.py
- Excluded: GUI

## Acceptance Criteria
- No nudity at clean 6775s
- Frame count validation passes"

# Create tasks
bd create "Create test fixture" --parent bd-CONVOY --priority 1
bd create "Implement mkvmerge extraction" --parent bd-CONVOY --priority 2
bd create "Validate with test case" --parent bd-CONVOY --priority 3

# Add dependencies
bd dep add bd-TASK2 bd-TASK1 --type blocks
bd dep add bd-TASK3 bd-TASK2 --type blocks

# Submit for approval
bd update bd-CONVOY --status pending_approval
```

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
2. bd ready --parent bd-CONVOY --limit 1
3. Verify authority (check convoy labels + citations)
4. bd update bd-TASK --claim engineer-id
5. Execute the work
6. If discovery: bd create --status needs_triage --discovered-from bd-TASK
7. bd close bd-TASK --reason "Completed"
8. When ALL tasks done:
   a. Write new tests or run existing tests to prove acceptance criteria
   b. If tests pass: bd update bd-CONVOY --status pending_human_approval
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
3. **Authority suspended** on convoy (automatic)
4. **Work pauses** until human triages

**Human triage options**:
- Add to current plan: `bd update bd-NEW --parent bd-CONVOY --status approved`
- Create new plan: Historian creates separate convoy
- Dismiss: `bd close bd-NEW --reason "Not needed"`
- Workaround: `bd close bd-NEW --reason "Workaround: ..."`

After triage, if no `needs_triage` children remain:
- Human re-approves: `bd update bd-CONVOY --label authority:granted`

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
   bd update bd-CONVOY --status pending_human_approval
   bd comment bd-CONVOY "All tasks complete. Tests pass. Ready for human approval."
   ```

**Test Integrity Rule**: Tests may NOT be disabled, loosened, bypassed, gutted, or skipped to make them pass. If a test cannot pass with the current implementation, the Engineer must HALT and request human guidance.

**Step 2: Human approves completion**

Human reviews Engineer's work and either:
```bash
# Approve - plan is complete
bd update bd-CONVOY --status completed

# Reject - needs more work
bd update bd-CONVOY --status suspended --label authority:suspended
bd comment bd-CONVOY "Issues found: [describe problems]"
```

**Step 3: Archive (after completion)**

1. **Export to archive**: `bd show bd-CONVOY --format markdown > plans/archive/convoy-title.md`
2. **Add archived label**: `bd update bd-CONVOY --label archived`

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
bd update bd-CONVOY --status halted --label "halted:test-conflict"
bd comment bd-CONVOY "HALTED: Test X fails. Test expects A but implementation does B. Requesting guidance."

# Implementation would need to worsen - move to halted status:
bd update bd-CONVOY --status halted --label "halted:arch-degradation"
bd comment bd-CONVOY "HALTED: Test X fails. Can only pass by [describe degradation]. Requesting guidance on approach."
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
bd show bd-CONVOY --json | jq '.fields.authority_citations'

# 2. Human decides:
#    a) Update authority doc to restore section
#    b) Update convoy with new valid citation
bd update bd-CONVOY --field "authority_citations=INVARIANTS.md#New-Section"

# 3. Re-approve
bd update bd-CONVOY --label "authority:granted"
```

#### Authority Suspended Mid-Execution

**Trigger**: Plan mutates while Engineer is working (new task added, description changed, needs_triage child).

**Detection**: Engineer's next `bd ready` or claim attempt fails authority check.

**Recovery**:
```bash
# 1. Engineer halts current work (don't commit incomplete changes)

# 2. Identify suspension reason
bd show bd-CONVOY  # Check for authority:suspended, needs_triage children

# 3. Human reviews and either:
#    a) Approves the mutation
bd update bd-CONVOY --label "authority:granted"
#    b) Reverts the mutation
bd update bd-CONVOY --description "original description..."
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

# 5. Wait for human to resolve authority issue
# 6. Re-claim when authority:granted restored
```

### Human Interaction Failures

#### Plan Never Approved

**Trigger**: Historian submits plan, human doesn't respond.

**Detection**: Plan sits in `pending_approval` for extended period.

**Recovery**:
```bash
# Option 1: Human approves
bd update bd-CONVOY --status approved --label "authority:granted"

# Option 2: Human requests changes
bd comment bd-CONVOY "Need to clarify scope for X"
bd update bd-CONVOY --status draft

# Option 3: Human rejects
bd close bd-CONVOY --reason "Not needed / out of scope"
```

**Prevention**: Orchestrator can surface stale pending_approval convoys:
```bash
bd list --type convoy --status pending_approval
```

#### Discoveries Never Triaged

**Trigger**: Engineer discovers issues, human doesn't triage them.

**Detection**: Authority suspended, `needs_triage` children accumulate.

**Recovery**:
```bash
# 1. List untriaged discoveries
bd list --status needs_triage --parent bd-CONVOY

# 2. For each, human decides:
#    a) Add to plan
bd update bd-DISCOVERY --status approved
#    b) Defer to new plan
bd update bd-DISCOVERY --parent ""  # Remove from this convoy
#    c) Dismiss
bd close bd-DISCOVERY --reason "Won't fix / duplicate / not needed"

# 3. Once all triaged, restore authority
bd update bd-CONVOY --label "authority:granted"
```

**Prevention**: Limit discovery creation per task. If too many discoveries, halt and escalate.

#### Human Modifies Authority Docs After Approval

**Trigger**: INVARIANTS.md or DECISIONS.md changed after plan approved.

**Detection**: Next authority verification fails (citation invalid).

**Impact**: All plans citing modified sections become suspended.

**Recovery**:
```bash
# 1. Identify affected plans
bd list --type convoy --label "authority:granted" | while read id; do
  # Check each plan's citations
  bd show $id --json | jq '.fields.authority_citations'
done

# 2. For each affected plan:
#    a) Update citation to new section name
#    b) Or acknowledge the authority doc change invalidates the plan

# 3. Re-approve valid plans
bd update bd-CONVOY --label "authority:granted"
```

**Prevention**: Authority docs should be changed rarely. Consider requiring plan review before authority doc changes.

### Recovery Commands Reference

| Situation | Command |
|-----------|---------|
| Check why suspended | `bd show bd-CONVOY` |
| List needs_triage | `bd list --status needs_triage --parent bd-CONVOY` |
| Restore authority | `bd update bd-CONVOY --label "authority:granted"` |
| Unclaim task | `bd update bd-TASK --status ready --assignee ""` |
| Close discovery | `bd close bd-DISCOVERY --reason "..."` |
| List stale plans | `bd list --type convoy --status pending_approval` |

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
- Convoy issues (auto-close when children done)
- Atomic claiming (`--claim`)
- State management

---

## Migration from V1.2

Projects migrating from V1.2 markdown plans:

1. **Keep authority files** - No change to INVARIANTS.md, DECISIONS.md
2. **Initialize Beads** - `bd init --prefix project`
3. **Import active plans** - Create convoy issues from existing plans/active/*.md
4. **Archive old plans** - Move plans/active/*.md to plans/archive/ (historical reference)
5. **Update CLAUDE.md** - Reference V1.3 orientation

**Active plan migration**:
```bash
# For each active plan, create convoy + tasks in Beads
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
| `bd comment <id> "..."` | Add comment | Providing feedback, notes |
| `bd dep tree <id>` | View dependency graph | Understanding blockers |

### Orchestrator-Invoked Commands

These commands are invoked by agents (Historian, Engineer) on behalf of the human:

| Command | Purpose | Which Agent |
|---------|---------|-------------|
| `bd create --type convoy ...` | Create new plan | Historian |
| `bd create --parent <convoy> ...` | Create task under plan | Historian |
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
        └── Historian: bd create --type convoy "Feature X plan"
        └── Historian: bd create --parent bd-001 "Task 1"
        └── Historian: bd create --parent bd-001 "Task 2"
        └── Historian: bd update bd-001 --status pending_approval
Human: "Looks good, approved"
    └── Human: bd update bd-001 --status approved --label authority:granted
Human: "Execute the plan"
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
| Plan storage | Markdown files | Beads convoy issues |
| Task tracking | Checkboxes | Beads child issues |
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
