# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

# INVARIANTS — Example

## Audio Preservation
**Statement**
Audio must not be re-encoded.

**Enforcement**
Compare input/output audio stream metadata with ffprobe; fail closed on mismatch.
