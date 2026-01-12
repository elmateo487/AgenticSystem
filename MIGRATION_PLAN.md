# V1.2 → V1.3 Migration Plan

## Decisions

### Removed from V1.3
| Item | Reason |
|------|--------|
| Notion Assistant (all files) | Not part of V1.3 scope |
| Extended orientation files | Consolidated into skills (~/.claude/skills/) |
| IMPLEMENTATION_PLAN_TEMPLATE.md | Replaced by Beads epic creation |
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
├── README.md                    # Entry point
├── INDEX.md                     # File index
├── CHANGELOG.md                 # Version history
│
├── templates/                   # Authority & architecture templates
│   ├── INVARIANTS_TEMPLATE.md       ✓
│   ├── DECISIONS_TEMPLATE.md        ✓
│   ├── ARCHITECTURE_TEMPLATE.md     ✓
│   ├── PIPELINE_TEMPLATE.md         ✓
│   └── AUTHORITY_CHANGELOG_TEMPLATE.md  ✓
│
├── docs/                        # Design documentation
│   ├── BEADS_INTEGRATION.md         ✓ (the V1.3 design doc)
│   ├── BEADS_INTEGRATION_AUDIT.md   ✓
│   └── SUB_AGENT_PATTERNS.md        ✓
│
└── examples/                    # Beads-based examples
    ├── EPIC_EXAMPLE.md              ✓
    ├── INVARIANTS_EXAMPLE.md        ✓
    └── DECISIONS_EXAMPLE.md         ✓

~/.claude/skills/               # Agent skills (global)
├── engineer/SKILL.md               ✓
├── historian/SKILL.md              ✓
└── orchestrator/SKILL.md           ✓
```

**Note**: orientation/ directory removed. Agent definitions consolidated into skills at ~/.claude/skills/.

---

## Ordered Work

### Phase 1: Foundation (Priority: High)
- [x] Create README.md - system overview and quick start
- [x] Create INDEX.md - file listing with descriptions

### Phase 2: Agent Specs (Priority: High)
- [x] Create agent skills at ~/.claude/skills/
- [x] Consolidate orientation content into skill files
- [x] Remove orientation/ directory

### Phase 3: Templates (Priority: Medium)
- [x] Copy templates/INVARIANTS_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/DECISIONS_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/ARCHITECTURE_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/PIPELINE_TEMPLATE.md - updated header to V1.3
- [x] Copy templates/AUTHORITY_CHANGELOG_TEMPLATE.md - updated header to V1.3

### Phase 4: Docs & Examples (Priority: Low)
- [x] Adapt docs/SUB_AGENT_PATTERNS.md for Beads
- [x] Create examples/EPIC_EXAMPLE.md - show Beads epic workflow
- [x] Copy examples/INVARIANTS_EXAMPLE.md
- [x] Copy examples/DECISIONS_EXAMPLE.md

### Phase 5: Finalize
- [x] Create CHANGELOG.md
- [x] Review all files for V1.2 references (appropriate references kept)
- [x] Commit to existing git repo (b7e40f6)

---

## File Count Summary

| Category | V1.2 | V1.3 | Delta |
|----------|------|------|-------|
| Skills | 0 | 3 | +3 (in ~/.claude/skills/) |
| Templates | 10 | 5 | -5 (removed plan/summary templates) |
| Docs | 5 | 3 | -2 (removed metrics/caching) |
| Examples | 6 | 3 | -3 (removed Notion + consolidated) |
| Root | 4 | 3 | -1 |
| **Total** | **37** | **14** | **-23** |

V1.3 is leaner by design. Beads epics handle what file-based plans used to do. Skills at ~/.claude/skills/ are the single source of truth for each agent.
