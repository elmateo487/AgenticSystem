# PROMPT CACHING RECOMMENDATIONS

## Authority
This document does not grant authority. It provides technical guidance only.

---

## Purpose

This document provides recommendations for structuring agent invocations to optimize for Anthropic's prompt caching, which provides 90% token cost reduction for cached content. Prompt caching is platform-level and transparent to agents, preserving full auditability.

---

## How Prompt Caching Works

Anthropic's prompt caching caches the prefix of prompts. Content that appears first in the prompt is more likely to be cached and reused across invocations. To maximize cache efficiency:

1. **Stable content first**: Load content that rarely changes at the beginning
2. **Dynamic content last**: Load content that changes frequently at the end
3. **Consistent ordering**: Use the same ordering across invocations for same-role agents

---

## Recommended Cache Breakpoint Structure

```
[Cache Breakpoint 1] System orientation (stable)
    - Role-specific orientation file
    - System constraints
    - Core responsibilities

[Cache Breakpoint 2] Authority documents (changes infrequently)
    - INVARIANTS.md (or INVARIANTS_SUMMARY.md)
    - DECISIONS.md (or DECISIONS_SUMMARY.md)

[Cache Breakpoint 3] Role-specific orientation (stable)
    - Halt conditions
    - Prohibited actions
    - Templates (if needed)

[No Cache] Active plan content (changes frequently)
    - Implementation plan
    - Referenced code paths
    - Dynamic context
```

---

## Loading Order by Agent Type

### Historian Invocation

| Order | Content | Cache Status | Tokens (est.) |
|-------|---------|--------------|---------------|
| 1 | HISTORIAN_ORIENTATION.md | Cached | ~500 |
| 2 | authority/INVARIANTS.md | Cached | ~300 |
| 3 | authority/DECISIONS.md | Cached | ~500 |
| 4 | Active plan (if executing) | Not cached | Variable |

### Engineer Invocation

| Order | Content | Cache Status | Tokens (est.) |
|-------|---------|--------------|---------------|
| 1 | ENGINEER_ORIENTATION.md | Cached | ~500 |
| 2 | authority/INVARIANTS.md | Cached | ~300 |
| 3 | authority/DECISIONS.md | Cached | ~500 |
| 4 | Active plan | Not cached | ~1000-2000 |
| 5 | Referenced code paths | Not cached | Variable |

### Orchestrator Invocation

| Order | Content | Cache Status | Tokens (est.) |
|-------|---------|--------------|---------------|
| 1 | ORCHESTRATOR_ORIENTATION.md | Cached | ~400 |
| 2 | Project AUTHORITY.md | Cached | ~100 |
| 3 | Plan index (if available) | Cached | ~200 |
| 4 | Task-specific context | Not cached | Variable |

### Notion Assistant Invocation

| Order | Content | Cache Status | Tokens (est.) |
|-------|---------|--------------|---------------|
| 1 | NOTION_ASSISTANT_ORIENTATION.md | Cached | ~300 |
| 2 | authority/INVARIANTS.md | Cached | ~300 |
| 3 | Input signals | Not cached | Variable |

---

## Implementation Guidance

### For Claude Code Configuration

When configuring Claude Code prompts, structure them as follows:

```
# System Context (cached across invocations)
[Include orientation file path reference]

# Project Context (cached within project work)
[Include authority document references]

# Task Context (not cached, changes per invocation)
[Include active plan and specific task details]
```

### For Orchestrator Invocations

When the Orchestrator invokes subagents, use minimal prompts:

**Good (cache-efficient):**
```
You are the Principal Software Engineer.

Task: Execute step 3 of the active plan.

Project: projects/notion-obligations/
```

The Engineer will load its own orientation file (cached) and read the plan (not cached).

**Bad (cache-inefficient):**
```
You are the Principal Software Engineer. Here are your constraints:
[400 words of constraints that are already in the orientation file]

Here is the plan:
[2000 words of plan content]

Here are the authority documents:
[1000 words of authority content]

Now execute step 3.
```

This duplicates cached content in the task-specific section, preventing caching.

---

## Tiered Loading for Cache Optimization

### Tier 1: Always Cached

- Orientation files (role-specific, ~50-75 lines each)
- System constraints (4 non-negotiables)
- Core responsibilities
- Halt conditions
- Prohibited actions

### Tier 2: Conditionally Loaded

Load only when needed to avoid cache dilution:

- Extended orientation files (templates, examples)
- Full agent specifications
- Full authority documents (vs. summaries)

### Tier 3: Never Cached

- Active plan content
- Referenced source code
- Dynamic task context

---

## Measuring Cache Efficiency

### Baseline Token Estimates (Before Optimization)

| Agent | Invocation Tokens | Cached Potential |
|-------|-------------------|------------------|
| Historian | 15,000-25,000 | 60-70% |
| Engineer | 25,000-40,000 | 40-50% |
| Orchestrator | 10,000-15,000 | 70-80% |
| Notion Assistant | 5,000-8,000 | 50-60% |

### Target Token Estimates (After Optimization)

| Agent | Phase 1 Target | Phase 2 Target |
|-------|----------------|----------------|
| Historian | 8,000-12,000 | 4,000-6,000 |
| Engineer | 12,000-20,000 | 6,000-10,000 |
| Orchestrator | 5,000-8,000 | 3,000-5,000 |
| Notion Assistant | 3,000-5,000 | 2,000-3,000 |

---

## V1.2 Alignment

Prompt caching optimizations preserve all SYSTEM V1.2 principles:

- **Fresh context per invocation**: Each invocation receives current state (caching is transparent)
- **Auditability**: All cached content is version-controlled
- **Invocation-only**: No background processes or persistent memory
- **Documentation as source of truth**: Cached content is documentation
