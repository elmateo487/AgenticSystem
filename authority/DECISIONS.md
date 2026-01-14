# DECISIONS

---

## 2026-01-13 - Issue Type Refactoring

### Problem

`task` type used for both stories and ACs makes hierarchy unclear.

### Decision

**Types:** epic, story, bug, ac, blocker

**Remove:** task, feature, chore

**Hierarchy:**
```
epic (≥3 stories) → story (≥3 ACs) → ac
bug (≥3 ACs) → ac
```

### Validation Rules

| Type | Parent | Children |
|------|--------|----------|
| epic | None | ≥3 stories |
| story | Epic (optional) | ≥3 ACs |
| bug | None (standalone) | ≥3 ACs |
| ac | Story or Bug | None |

### /bug Skill Template

```
Title: [Bug description]
Steps to Reproduce: [numbered steps]
Expected: [what should happen]
Actual: [what happens]

ACs (≥3):
- [ ] Regression test reproduces bug
- [ ] Fix implemented
- [ ] Regression test passes
```

### Migration

1. Add validation to beads
2. Rename /ticket → /story
3. Create /bug skill
4. Update skills: engineer, historian, epic
5. Update docs: replace "ticket" with "story"

### Authority

Effective immediately. New issues use new types. Existing issues migrated when touched.

---
