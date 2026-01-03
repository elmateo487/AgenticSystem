# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

## Template
Copy into a project and fill in. Do not edit templates in-place.

# <DOCUMENT_TYPE> CHANGELOG

## Authority
This document does not grant authority. It provides change history only.

---

## <YYYY-MM-DD>

- Added: <Item name and brief description>
- Modified: <Item name and what changed>
- Removed: <Item name>
- No changes

## <YYYY-MM-DD>

- Initial: <List of initial items>

---

## Maintenance Protocol

Update this changelog when:
- New invariant or decision is added
- Existing item is modified significantly
- Item is removed or superseded
- Daily no-change entries are optional

Format:
- **Added**: New items that didn't exist before
- **Modified**: Changes to existing items (include what changed)
- **Removed**: Items that no longer apply
- **No changes**: Explicit note when reviewing but no changes made

Do NOT include:
- Typo fixes that don't change meaning
- Formatting-only changes
- Implementation status updates (those go in plan worklogs)
