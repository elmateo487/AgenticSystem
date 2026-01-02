# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

# IMPLEMENTATION PLAN — Example: Audio Metadata Parity

## Objective
Fail pipeline if output audio stream properties differ from input.

## Authority
- INVARIANTS.md#Audio-Preservation
- DECISIONS.md#ffprobe-stream-comparison

## Ordered Work
- [ ] Extract audio stream metadata
- [ ] Compare codec/channels/sample_rate
- [ ] Unit tests
- [ ] Integration fixtures

## Validation Checklist
- [ ] Tests pass
- [ ] Altered-audio fixture fails
