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

# <DOCUMENT_TYPE> SUMMARY

Generated: <YYYY-MM-DD> | Source: <SOURCE_FILE> (sha256: <HASH>)

## Authority
This document does not grant authority. Load full <SOURCE_FILE> for authority.

## Summary

<Brief overview of document contents>

## Active Items

<List of active invariants/decisions with one-line descriptions>

1. <Item Name> — <Brief description>
2. <Item Name> — <Brief description>
3. <Item Name> — <Brief description>

## Last Modified

- <YYYY-MM-DD>: <Change description>

---

## Generation Instructions

This summary is generated deterministically from the source document. To regenerate:

```bash
# Example generation command (project-specific implementation)
python scripts/generate_authority_summary.py <source_file> <output_file>
```

**Rules**:
1. Summary is a committed artifact (auditable)
2. Summary must reference source document hash
3. Summary does not grant authority
4. Regenerate manually after source changes
