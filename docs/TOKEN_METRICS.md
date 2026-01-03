# TOKEN METRICS BASELINE

## Authority
This document does not grant authority. It provides measurement data only.

---

## Purpose

This document establishes baseline token usage metrics for SYSTEM V1.2 agent invocations, enabling measurement of efficiency improvements from tiered loading and prompt caching optimizations.

---

## Measurement Methodology

### Token Counting

Token estimates are calculated using:
- Anthropic's tokenizer (Claude models)
- Approximate ratio: ~4 characters per token for English text
- Markdown formatting adds ~10-15% overhead

### What's Measured

| Category | Includes |
|----------|----------|
| Orientation tokens | Role-specific orientation file |
| Authority tokens | INVARIANTS.md, DECISIONS.md |
| Plan tokens | Active implementation plan |
| Code context tokens | Referenced source files |

---

## Baseline Metrics (Before Tiered Loading)

### Orientation File Sizes

| File | Lines | Est. Tokens | Notes |
|------|-------|-------------|-------|
| HISTORIAN_ORIENTATION.md (v1.2.0) | 252 | ~2,000 | Pre-tiering |
| ENGINEER_ORIENTATION.md (v1.2.0) | 214 | ~1,700 | Pre-tiering |
| ORCHESTRATOR_ORIENTATION.md (v1.2.0) | 250 | ~2,000 | Pre-tiering |
| NOTION_ASSISTANT_ORIENTATION.md (v1.2.0) | 153 | ~1,200 | Pre-tiering |

### Full Invocation Token Estimates (Before Optimization)

| Agent | Orientation | Authority | Plan | Code | Total |
|-------|-------------|-----------|------|------|-------|
| Historian | 2,000 | 3,000 | 1,500 | 0 | 6,500-8,500 |
| Engineer | 1,700 | 3,000 | 2,000 | 5,000-15,000 | 11,700-21,700 |
| Orchestrator | 2,000 | 1,000 | 500 | 0 | 3,500-5,500 |
| Notion Assistant | 1,200 | 1,500 | 0 | 0 | 2,700-3,500 |

---

## Phase 1 Metrics (After Tiered Loading)

### Tiered Orientation File Sizes

| File | Lines | Est. Tokens | Reduction |
|------|-------|-------------|-----------|
| HISTORIAN_ORIENTATION.md (Tier 1) | 100 | ~800 | 60% |
| HISTORIAN_ORIENTATION_EXTENDED.md (Tier 2) | 280 | ~2,200 | N/A |
| ENGINEER_ORIENTATION.md (Tier 1) | 121 | ~950 | 44% |
| ENGINEER_ORIENTATION_EXTENDED.md (Tier 2) | 210 | ~1,650 | N/A |
| ORCHESTRATOR_ORIENTATION.md (Tier 1) | 110 | ~850 | 58% |
| ORCHESTRATOR_ORIENTATION_EXTENDED.md (Tier 2) | 200 | ~1,600 | N/A |
| NOTION_ASSISTANT_ORIENTATION.md (Tier 1) | 114 | ~900 | 25% |
| NOTION_ASSISTANT_ORIENTATION_EXTENDED.md (Tier 2) | 220 | ~1,750 | N/A |

### Tier 1 Only Invocation Estimates

| Agent | Tier 1 Orientation | Authority | Plan | Total (No Code) |
|-------|-------------------|-----------|------|-----------------|
| Historian | 800 | 3,000 | 1,500 | 5,300 |
| Engineer | 950 | 3,000 | 2,000 | 5,950 |
| Orchestrator | 850 | 1,000 | 500 | 2,350 |
| Notion Assistant | 900 | 1,500 | 0 | 2,400 |

### Token Reduction Summary (Phase 1)

| Agent | Before | After (Tier 1) | Reduction |
|-------|--------|----------------|-----------|
| Historian | 6,500-8,500 | 5,300 | 19-38% |
| Engineer | 11,700-21,700 | 5,950 + code | 15-50% |
| Orchestrator | 3,500-5,500 | 2,350 | 33-57% |
| Notion Assistant | 2,700-3,500 | 2,400 | 11-31% |

---

## Phase 2 Targets (Authority Summaries)

### Projected Authority Summary Sizes

| Document | Full Size | Summary Size | Reduction |
|----------|-----------|--------------|-----------|
| INVARIANTS.md | ~1,500 tokens | ~300 tokens | 80% |
| DECISIONS.md | ~5,000 tokens | ~500 tokens | 90% |

### Projected Invocation Estimates with Summaries

| Agent | Orientation | Auth Summary | Plan | Total |
|-------|-------------|--------------|------|-------|
| Historian | 800 | 800 | 1,500 | 3,100 |
| Engineer | 950 | 800 | 2,000 | 3,750 |
| Orchestrator | 850 | 300 | 500 | 1,650 |
| Notion Assistant | 900 | 300 | 0 | 1,200 |

---

## Cache Efficiency Estimates

### With Prompt Caching

Anthropic's prompt caching provides 90% cost reduction for cached content.

| Content Type | Cacheable | Cache Hit Rate |
|--------------|-----------|----------------|
| Tier 1 Orientation | Yes | 95%+ |
| Tier 2 Orientation | Yes (when loaded) | 80%+ |
| Authority Summaries | Yes | 90%+ |
| Full Authority | Yes | 70%+ |
| Active Plan | No (changes frequently) | 0% |
| Code Context | No (varies per task) | 10-30% |

### Effective Token Cost

With caching, effective cost = (cached tokens * 0.1) + uncached tokens

| Agent | Total Tokens | Cached | Uncached | Effective Cost |
|-------|--------------|--------|----------|----------------|
| Historian | 5,300 | 4,300 | 1,000 | 1,430 |
| Engineer | 5,950 | 4,950 | 1,000 | 1,495 |
| Orchestrator | 2,350 | 1,850 | 500 | 685 |
| Notion Assistant | 2,400 | 2,100 | 300 | 510 |

---

## Measurement Cadence

- Baseline established: 2026-01-03
- Phase 1 metrics: After tiered loading implementation
- Phase 2 metrics: After authority summary implementation
- Phase 3 metrics: After context-aware loading implementation

---

## V1.2 Alignment

Token optimization preserves all SYSTEM V1.2 principles:
- **Fresh context per invocation**: Caching is transparent; each invocation receives current state
- **Auditability**: All loaded content is version-controlled
- **Invocation-only**: No background processes or persistent memory
- **Documentation as source of truth**: Optimizations reduce token count, not content authority
