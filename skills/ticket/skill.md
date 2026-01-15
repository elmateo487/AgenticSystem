---
name: ticket
description: Create a well-formed ticket (task/issue) with acceptance criteria as children. Use for any work item that needs tracking.
version: 1.0.0
context: fork
model: haiku
allowed-tools: Bash
---

# Ticket Creation Skill

**A ticket is:** A description with acceptance criteria as children. Tickets REQUIRE ACs (3-8 children). Tickets can be standalone or children of an epic (via `--parent`).

Note: Ticket, task, and issue are synonymous.

## Required Structure

- **Title**: Concise, action-oriented
- **Description** with:
  - Context/Problem
  - Requirements
  - Authority citations (optional - cite INVARIANTS.md, DECISIONS.md when relevant)
- **Labels** including `type:ticket`
- **Priority** (P0-P4)
- **Acceptance criteria as child issues** (labeled `type:ac`)

## Workflow

### Step 1: Create the Ticket

```bash
TICKET_ID=$(bd create "Ticket Title" \
  --label "type:ticket" \
  --label "area:AREA" \
  --priority 2 \
  --description "## Context
Why this is needed, what problem it solves.

## Requirements
What must be accomplished.

## Authority (optional)
Cite INVARIANTS.md#X or DECISIONS.md#Y if relevant." \
  2>&1 | grep -o 'safevision-[a-z0-9]*')

echo "Created ticket: $TICKET_ID"
```

### Step 2: Create Acceptance Criteria as Children (MANDATORY)

Each AC must be:
- **Specific**: Clear what to do
- **Testable**: Can verify completion
- **Atomic**: Single action
- **Imperative**: Starts with verb

## Test Requirements (Include in ACs)

**For new features and code:**
- **Unit tests (70-80%)**: Required for all new public functions/methods. Mock dependencies. Target 80% line coverage.
- **Integration tests (15-25%)**: Required for cross-component interactions. Mock external services.
- **E2E tests (5-10%)**: Required for critical user paths only.

**For bugs:**
- **P0/P1**: Must include regression test proving the fix prevents recurrence.
- **P2/P3**: Unit test covering the fixed case is sufficient.

Always include a test AC when creating feature or bug tickets.

```bash
bd create "AC description 1" --parent $TICKET_ID --label "type:ac" --priority 1
bd create "AC description 2" --parent $TICKET_ID --label "type:ac" --priority 2
bd create "AC description 3" --parent $TICKET_ID --label "type:ac" --priority 3
# Add more as needed (typically 3-8 ACs)
```

### Step 3: Verify Structure

```bash
bd show $TICKET_ID
# Confirm children are listed
```

## Output Format

Report the created ticket:
```
Created ticket: safevision-XXX
- Title: [title]
- ACs: N children created

View with: bd show safevision-XXX
```

## Exception: Research Tickets

Pure investigation tickets may skip ACs:

```bash
bd create "Research X" \
  --label "type:ticket" \
  --label "type:research" \
  --description "## Objective
What to find out.

## Deliverables
- Research document at docs/research/X.md"
```
