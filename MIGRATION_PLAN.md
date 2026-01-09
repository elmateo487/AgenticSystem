# V1.2 → V1.3 Migration Plan

## Decisions

### Removed from V1.3
| Item | Reason |
|------|--------|
| Notion Assistant (all files) | Not part of V1.3 scope |
| Extended orientation files | Consolidated into main orientations + BEADS_INTEGRATION.md |
| IMPLEMENTATION_PLAN_TEMPLATE.md | Replaced by Beads convoy creation |
| PLAN_INDEX_TEMPLATE.md | Plans are now Beads queries, not index files |
| PLAN_INDEX_GENERATION.md | Same reason |
| AUTHORITY_SUMMARY_TEMPLATE.md | Over-engineering; read full docs |
| AUTHORITY_SUMMARY_GENERATION.md | Same reason |
| TOKEN_METRICS.md | Implementation detail, not system design |
| PROMPT_CACHING.md | Implementation detail, not system design |
| OBSIDIAN_VAULT_SETUP.md | Obsidian-specific, not relevant |

### Renamed
| V1.2 Name | V1.3 Name |
|-----------|-----------|
| OBSIDIAN_PROJECT_HISTORIAN_AGENT.md | HISTORIAN_AGENT.md |
| PRINCIPAL_SOFTWARE_ENGINEER_AGENT.md | ENGINEER_AGENT.md |
| ORCHESTRATOR_AGENT.md | ORCHESTRATOR_AGENT.md (unchanged) |

### Kept As-Is (copy with minor updates)
| File | Notes |
|------|-------|
| INVARIANTS_TEMPLATE.md | Authority still file-based |
| DECISIONS_TEMPLATE.md | Authority still file-based |
| ARCHITECTURE_TEMPLATE.md | Still relevant |
| PIPELINE_TEMPLATE.md | Still relevant |
| AUTHORITY_CHANGELOG_TEMPLATE.md | Still relevant |

### Adapted for Beads
| V1.2 File | V1.3 Adaptation |
|-----------|-----------------|
| SUB_AGENT_PATTERNS.md | Update for Beads context |
| AGENT_INVOCATION_PROTOCOL.md | Merge into BEADS_INTEGRATION.md or drop |
| Examples (non-Notion) | Create Beads-based examples |

---

## V1.3 Target Structure

```
system-v1.3/
├── README.md                    # NEW - entry point
├── INDEX.md                     # NEW - file index
├── CHANGELOG.md                 # NEW - version history
│
├── orientation/                 # Agent quick-reference (DONE)
│   ├── HISTORIAN_ORIENTATION.md     ✓
│   ├── ENGINEER_ORIENTATION.md      ✓
│   └── ORCHESTRATOR_ORIENTATION.md  ✓
│
├── agents/                      # Full agent specifications
│   ├── HISTORIAN_AGENT.md           TODO - adapt from V1.2
│   ├── ENGINEER_AGENT.md            TODO - adapt from V1.2
│   └── ORCHESTRATOR_AGENT.md        TODO - adapt from V1.2
│
├── templates/                   # Authority & architecture templates
│   ├── INVARIANTS_TEMPLATE.md       TODO - copy from V1.2
│   ├── DECISIONS_TEMPLATE.md        TODO - copy from V1.2
│   ├── ARCHITECTURE_TEMPLATE.md     TODO - copy from V1.2
│   ├── PIPELINE_TEMPLATE.md         TODO - copy from V1.2
│   └── AUTHORITY_CHANGELOG_TEMPLATE.md  TODO - copy from V1.2
│
├── docs/                        # Design documentation
│   ├── BEADS_INTEGRATION.md         ✓ (the V1.3 design doc)
│   ├── BEADS_INTEGRATION_AUDIT.md   ✓
│   └── SUB_AGENT_PATTERNS.md        TODO - adapt from V1.2
│
└── examples/                    # Beads-based examples
    ├── CONVOY_EXAMPLE.md            TODO - NEW for V1.3
    ├── INVARIANTS_EXAMPLE.md        TODO - copy from V1.2
    └── DECISIONS_EXAMPLE.md         TODO - copy from V1.2
```

---

## Ordered Work

### Phase 1: Foundation (Priority: High)
- [x] Create orientation files (DONE)
- [x] Create README.md - system overview and quick start
- [x] Create INDEX.md - file listing with descriptions

### Phase 2: Agent Specs (Priority: High)
- [x] Create agents/HISTORIAN_AGENT.md - adapt from V1.2, remove Obsidian references
- [x] Create agents/ENGINEER_AGENT.md - adapt from V1.2, add Test Integrity, Beads commands
- [x] Create agents/ORCHESTRATOR_AGENT.md - adapt from V1.2, add Beads read-only commands

### Phase 3: Templates (Priority: Medium)
- [x] Copy templates/INVARIANTS_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/DECISIONS_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/ARCHITECTURE_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/PIPELINE_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/AUTHORITY_CHANGELOG_TEMPLATE.md - updated header to V1.3

### Phase 4: Docs & Examples (Priority: Low)
- [x] Adapt docs/SUB_AGENT_PATTERNS.md for Beads
- [x] Create examples/CONVOY_EXAMPLE.md - show Beads convoy workflow
- [x] Copy examples/INVARIANTS_EXAMPLE.md
- [x] Copy examples/DECISIONS_EXAMPLE.md

### Phase 5: Finalize
- [ ] Create CHANGELOG.md
- [ ] Review all files for V1.2 references
- [ ] Initialize git repo and commit

---

## File Count Summary

| Category | V1.2 | V1.3 | Delta |
|----------|------|------|-------|
| Orientation | 8 | 3 | -5 (removed extended + Notion) |
| Agents | 4 | 3 | -1 (removed Notion) |
| Templates | 10 | 5 | -5 (removed plan/summary templates) |
| Docs | 5 | 3 | -2 (removed metrics/caching) |
| Examples | 6 | 3 | -3 (removed Notion + consolidated) |
| Root | 4 | 3 | -1 |
| **Total** | **37** | **20** | **-17** |

V1.3 is leaner by design. Beads handles what file-based plans used to do.
