# SYSTEM V1.3 — Beads-Integrated Invocation-Only Agent Architecture

## Core Principles
- Nothing runs unless explicitly invoked by a human
- Tests define correctness
- Tests are sacrosanct
- Implementation quality is sacrosanct

# INVARIANTS — Example

## Audio Preservation
**Statement**
Audio must not be re-encoded.

**Rationale**
Re-encoding audio introduces quality loss and increases processing time. The original audio codec and bitrate must be preserved in the output.

**Implications**
- Requires: Stream copy for audio (`-c:a copy`)
- Forbids: Audio transcoding, sample rate conversion

**Enforcement**
- Detection: Compare input/output audio stream metadata with ffprobe
- Halt conditions: Codec mismatch, bitrate deviation > 1%

---

## Frame-Exact Cutting
**Statement**
Video cuts must be frame-exact with no content leakage.

**Rationale**
Content filtering requires precise cuts. GOP boundary issues can cause unwanted frames to appear in output.

**Implications**
- Requires: Keyframe-aware cutting, RASL gap handling
- Forbids: Approximate cuts, GOP leakage

**Enforcement**
- Detection: Perceptual hash validation of cut boundaries
- Halt conditions: Curated frames found in clean output
