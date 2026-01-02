# INVOCATION PATTERNS — Correct vs Incorrect Examples

## Authority
This document does not grant authority.

---

## Purpose

This document provides concrete examples of correct and incorrect agent invocation patterns. Use these as reference when invoking agents.

**Core Principle**: Invocations provide context, not instructions. Agents determine their actions from their orientation files and authority documents.

---

## Historian Invocations

### Plan Completion

**INCORRECT** (instructions in invocation):
```
Historian: Plan 001 is complete.

Do the following:
1. Verify all checkboxes are marked complete
2. Move the plan from active/ to archive/
3. Update DECISIONS.md if any new decisions were made
4. Update ARCHITECTURE.md to reflect the new module structure
5. Create a completion summary in the worklog
```

**CORRECT** (context only):
```
You are the Obsidian Project Historian for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/HISTORIAN_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Plan: plans/active/001-initial-setup.md
- State: Engineer has completed execution, all tests pass

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Historian's orientation file defines what to do when a plan completes. The invoker only needs to provide the plan location and state.

---

### New Feature Request

**INCORRECT** (instructions in invocation):
```
Historian: We need OAuth support.

Create a plan with:
- Clear objective
- Authority citations
- Ordered work items with checkboxes
- Validation checklist
- Empty worklog
```

**CORRECT** (context only):
```
You are the Obsidian Project Historian for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/HISTORIAN_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Request: Add OAuth support for Notion API authentication
- Relevant authority: DECISIONS.md#2026-01-01-authentication-strategy

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Historian knows from its orientation that plans must use the template, cite authority, include ordered work, etc.

---

### Authority Audit

**INCORRECT** (instructions in invocation):
```
Historian: Check if our docs are up to date.

Please:
1. Compare INVARIANTS.md against the codebase
2. Compare DECISIONS.md against what we actually built
3. Update ARCHITECTURE.md if needed
4. List any gaps you find
```

**CORRECT** (context only):
```
You are the Obsidian Project Historian for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/HISTORIAN_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Request: Documentation audit - implementation has evolved since initial docs
- Last known update: ARCHITECTURE.md updated 2025-12-15

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Historian's orientation defines documentation drift responsibilities.

---

## Engineer Invocations

### Plan Execution

**INCORRECT** (instructions in invocation):
```
Engineer: Execute plan 001.

Remember to:
1. Read the plan first
2. Verify authority citations exist
3. Execute each step in order
4. Run tests after each step
5. Update checkboxes as you go
6. Add worklog entries
```

**CORRECT** (context only):
```
You are the Principal Software Engineer for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/ENGINEER_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Plan to execute: plans/active/001-initial-setup.md

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Engineer's orientation file specifies the complete execution contract.

---

### Continue Execution

**INCORRECT** (instructions in invocation):
```
Engineer: Continue from where you left off on plan 001.

You were on step 3. Please:
1. Continue with step 3
2. Then do steps 4 and 5
3. Run the full test suite
4. Mark everything complete
```

**CORRECT** (context only):
```
You are the Principal Software Engineer for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/ENGINEER_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Plan: plans/active/001-initial-setup.md
- State: Steps 1-2 complete per worklog, step 3 in progress

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Engineer reads the plan to see what's checked, reads the worklog to understand state, and continues accordingly.

---

### Test Failure Recovery

**INCORRECT** (instructions in invocation):
```
Engineer: Tests failed on the last run.

Please:
1. Look at the test output
2. Figure out what's wrong
3. Fix the issue
4. Re-run tests
5. If they pass, continue with the plan
```

**CORRECT** (context only):
```
You are the Principal Software Engineer for SYSTEM V1.2.

Read your orientation file:
- system/v1.2/orientation/ENGINEER_ORIENTATION.md

Context:
- Project: projects/notion-obligations/
- Plan: plans/active/001-initial-setup.md
- State: Test failure during step 3, see worklog for details

Ignore prior conversation output. Use only: authority docs + the active plan + referenced code paths.

Working directory: /Users/dev/projects/notion-obligations
```

**Why correct**: The Engineer's orientation defines test failure handling. The worklog contains the failure details.

---

## Anti-Patterns to Avoid

### 1. Summarizing Files

**BAD**: Reading files and summarizing them in the invocation prompt.
```
Engineer: Here's what AUTHORITY.md says: [500 words]. Here's the plan: [300 words]. Now execute step 3.
```

**GOOD**: Let the agent read the files directly.
```
Context:
- Project: projects/notion-obligations/
- Plan: plans/active/001-initial-setup.md
- Execute: Step 3
```

### 2. Restating Constraints

**BAD**: Restating agent constraints from the spec.
```
Engineer: Remember you must halt if tests fail. You must update worklogs. You must verify authority.
```

**GOOD**: The agent reads its own constraints.
```
Read your orientation file:
- system/v1.2/orientation/ENGINEER_ORIENTATION.md
```

### 3. Providing Task Lists

**BAD**: Telling the agent exactly what to do.
```
Historian: Please:
1. Check invariants
2. Update decisions
3. Archive plan
4. Update architecture
```

**GOOD**: Describe the state, let the agent determine actions.
```
Context:
- State: Plan execution complete, tests pass
```

### 4. Implicit State

**BAD**: Assuming the agent remembers prior conversation.
```
Engineer: Continue where we left off.
```

**GOOD**: Explicit state in the context.
```
Context:
- State: Steps 1-3 complete per plan checkboxes, step 4 next
```

---

## Quick Reference: What to Include

| Include in Invocation | Do NOT Include |
|-----------------------|----------------|
| Agent identity | Task lists |
| Orientation file path | File contents/summaries |
| Project path | Constraint restatements |
| Plan path (if applicable) | Execution instructions |
| State description | What agent should do |
| Working directory | How agent should do it |

---

## The Test: Can You Remove Instructions?

When drafting an invocation, ask: "If I removed all the imperative sentences, would the agent still know what to do?"

If yes: The invocation is correct.
If no: You're providing instructions, not context. Revise.
