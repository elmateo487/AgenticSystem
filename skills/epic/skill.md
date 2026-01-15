---
name: epic
description: Create a plan (epic) with tickets as children. Use for multi-step work that needs multiple tickets.
version: 1.0.0
context: fork
model: haiku
allowed-tools: Bash, Skill
---

# Epic Creation Skill

**An epic is:** A plan with tickets as children. Epics REQUIRE tickets - an epic without tickets is incomplete.

## Required Structure

- **Title**: Describes the overall goal
- **Description** with:
  - Context/Problem
  - Requirements
  - Authority citations (optional - cite INVARIANTS.md, DECISIONS.md when relevant)
- **Labels** including `type:epic`
- **Tickets as children** (labeled `type:ticket`)
  - Each ticket has its own AC children (labeled `type:ac`)
- **Dependencies** between tickets via `bd dep add`

## Lifecycle

draft → pending_approval → [human approves] → approved → in_progress → pending_human_approval → completed

## Workflow

### Phase 1: Create Epic Shell

```bash
EPIC_ID=$(bd create "Epic Title" \
  --label "type:epic" \
  --label "area:AREA" \
  --priority 2 \
  --description "## Context
Why this work is needed, what problem it solves.

## Requirements
What must be accomplished overall.

## Authority (optional)
Cite INVARIANTS.md#X or DECISIONS.md#Y if relevant." \
  2>&1 | grep -o 'safevision-[a-z0-9]*')

echo "Created epic: $EPIC_ID"
```

### Phase 2: Create Tickets Under Epic

Use the `/ticket` skill for each ticket, passing `--parent $EPIC_ID`:

```bash
# For each ticket needed, follow the ticket skill workflow:
# 1. Create ticket with --parent $EPIC_ID
# 2. Create 3-8 ACs as children of the ticket
# 3. Verify ACs exist

# Example for first ticket:
T1=$(bd create "First ticket title" \
  --parent $EPIC_ID \
  --label "type:ticket" \
  --priority 1 \
  --description "## Context
Why this ticket.

## Requirements
What this ticket accomplishes." \
  2>&1 | grep -o 'safevision-[a-z0-9.]*')

# Create ACs for T1 (use /ticket skill for full workflow)
bd create "AC description 1" --parent $T1 --label "type:ac" --priority 1
bd create "AC description 2" --parent $T1 --label "type:ac" --priority 2
bd create "AC description 3" --parent $T1 --label "type:ac" --priority 3

# Verify T1 has ACs
bd list --parent $T1

# Repeat for each ticket...
```

### Phase 3: Add Dependencies (if needed)

```bash
bd dep add $T2 $T1 --type blocks  # T1 blocks T2 (T1 must complete first)
```

### Phase 4: Verify Structure

```bash
bd show $EPIC_ID
# Verify all tickets listed as children

bd list --parent $T1
bd list --parent $T2
# Verify each ticket has AC children
```

### Phase 5: Submit for Approval

```bash
bd update $EPIC_ID --status pending_approval
bd comment $EPIC_ID "Created N tickets with M total ACs. Ready for review."
```

## Output Format

Report the created epic:
```
Created epic: safevision-XXX

Tickets:
1. safevision-XXX.1 - [title] (N ACs)
2. safevision-XXX.2 - [title] (N ACs)
...

Total: N tickets, M ACs

View with: bd show safevision-XXX
```

## Pre-Completion Checklist

Before reporting completion:
1. [ ] Epic exists with `type:epic` label
2. [ ] All tickets have `type:ticket` label
3. [ ] EACH ticket has AC children with `type:ac` label
4. [ ] Dependencies added where needed
5. [ ] Status set to pending_approval
