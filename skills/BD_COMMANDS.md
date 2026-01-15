# Beads CLI Command Reference

## Hook-Enforced Rules

All rules below are enforced by PreToolUse hooks. Violations are **blocked**.

### Blocked Commands

| Command | Why Blocked |
|---------|-------------|
| `bd ready` | Humans choose work, not agents |
| `bd delete X` | Must use `bd delete X --hard --force` |
| `bd create "Title"` | Must include type label |
| `bd create --label "type:ac"` | AC must have `--parent TICKET_ID` |
| `bd create --label "type:epic"` | Must also include `--type epic` |
| `bd update --status blocked` | Must have blocking dependency (use `bd dep X --blocks Y` instead) |
| `bd update CLOSED --status blocked` | Can't block closed issues |
| `bd update BLOCKED --status open` | Must have `--comment "how resolved"` |
| `bd close X` | Must include `--reason "..."` |

### Hierarchy Enforcement

```
Epic (type:epic)
  └── Ticket (type:ticket) ← parent must be Epic
        └── AC (type:ac) ← parent must be Ticket
```

| Attempt | Result |
|---------|--------|
| AC under Epic | ❌ BLOCKED |
| AC under AC | ❌ BLOCKED |
| Ticket under Ticket | ❌ BLOCKED |
| Ticket under AC | ❌ BLOCKED |
| AC under Ticket | ✅ Allowed |
| Ticket under Epic | ✅ Allowed |

### Valid Statuses

Only these values accepted for `bd update --status`:

| Status | Meaning |
|--------|---------|
| `open` | Ready to work |
| `in_progress` | Currently being worked |
| `blocked` | Waiting on dependency |
| `pending_approval` | Awaiting human review |

### Blocked Status Rules

| Action | Requirement |
|--------|-------------|
| Block an issue | Just create dependency - status auto-updates |
| Block closed issue | ❌ BLOCKED - can't block already-closed items |
| Unblock an issue | Requires `--comment "how resolved"` |

```bash
# Blocking (one command - auto-sets status)
bd dep safevision-abc --blocks $ID       # Creates dep AND sets $ID to blocked

# Unblocking (comment required)
bd update $ID --status open --comment "safevision-abc completed"
```

### Dependency Commands

```bash
bd dep BLOCKER --blocks BLOCKED          # Create blocking relationship (auto-sets BLOCKED to blocked status)
bd dep list $ID --type blocks            # What blocks this issue?
bd dep list $ID --direction up           # What does this issue block?
bd dep tree $ID                          # Full dependency tree
bd dep remove BLOCKED BLOCKER            # Remove dependency
```

**Note:** `bd dep X --blocks Y` automatically sets Y's status to `blocked` via PostToolUse hook.

### Valid Close Reasons

`bd close` requires `--reason` with canonical wording:

**Completion** (exact match, case-insensitive):
- `Done` - Work completed successfully
- `Fixed` - Bug was fixed
- `All ACs complete` - All acceptance criteria met
- `All tickets complete` - All child tickets closed

**Non-completion** (prefix + explanation required):
- `Won't implement - [why]` - Decision not to do the work
- `Duplicate - [of what]` - Already covered elsewhere
- `Out of scope - [why]` - Not part of this work

Non-completion format: `PREFIX - EXPLANATION` where explanation cannot be empty.

```bash
# Valid
--reason "Won't implement - not needed for MVP"
--reason "Duplicate - see ticket-123"
--reason "Out of scope - belongs in phase 2"

# Invalid (missing explanation)
--reason "Won't implement"      # ❌ needs "- [why]"
--reason "Duplicate"            # ❌ needs "- [ref]"
--reason "Out of scope"         # ❌ needs "- [why]"

# Invalid (wrong wording)
--reason "Completed"            # ❌ use "Done"
--reason "finished"             # ❌ use "Done"
--reason "wontfix"              # ❌ use "Won't implement - [why]"
```

### Auto-Propagation (Hook-Triggered)

| Trigger | Auto-Action |
|---------|-------------|
| `--status in_progress` | Ancestors → in_progress |
| `--status blocked` | Ancestors → blocked |
| `--status open` (was blocked) | Ancestors → open (if no siblings blocked) |
| `--reason "Won't implement..."` | Descendants auto-closed |
| `--reason "Done"` | BLOCKED if open children exist |

---

## Quick Reference

### Create

```bash
# Epic (root level)
bd create "Title" --label "type:epic" --type epic --description "..."

# Ticket (under epic)
bd create "Title" --label "type:ticket" --parent $EPIC_ID --description "..."

# AC (under ticket)
bd create "Title" --label "type:ac" --parent $TICKET_ID

# Research (standalone)
bd create "Title" --label "type:research"
```

### Update Status

```bash
bd update $ID --status in_progress   # Start work (propagates up)
bd update $ID --status blocked       # Block (propagates up)
bd update $ID --status open          # Unblock
bd update $ID --status pending_approval
```

### Close

```bash
# Completion (children must be closed first)
bd close $ID --reason "Done"
bd close $ID --reason "Fixed"
bd close $ID --reason "All ACs complete"

# Non-completion (cascades to descendants)
bd close $ID --reason "Won't implement - not needed for MVP"
bd close $ID --reason "Duplicate - see ticket-123"
bd close $ID --reason "Out of scope - belongs in phase 2"
```

### Delete

```bash
bd delete $ID --hard --force   # Both flags required
```

### Query

```bash
bd show $ID                    # Details
bd show $ID --json             # JSON output
bd list --type epic            # List epics
bd list --label "type:ticket"  # List tickets
bd list --parent $ID           # List children
bd dep tree $ID                # Dependency tree
```

---

## Agent Permissions

| Command | Orchestrator | Engineer | Historian |
|---------|:------------:|:--------:|:---------:|
| `bd show/list` | ✓ | ✓ | ✓ |
| `bd create` | - | blocker only | ✓ |
| `bd update --status` | - | ✓ | ✓ |
| `bd close` | human-directed | ✓ | - |
| `bd delete` | human-directed | - | - |

---

## Labels

```bash
# Type (required)
type:epic, type:ticket, type:ac, type:research

# Area
area:pipeline, area:services, area:gui, area:cli

# Priority: P1 (critical) → P5 (backlog)
```
