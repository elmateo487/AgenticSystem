# CHANGELOG

## [1.3.0] - 2026-01-09

### Added
- **Beads Integration**: Plans now use Beads epic issues instead of markdown files
- **Test Integrity**: New core principle - tests are sacrosanct, implementation quality is sacrosanct
- **HALT Protocol**: Engineers halt and escalate when tests cannot pass without compromise
- **Epic workflow**: draft → pending_approval → approved → in_progress → pending_human_approval → completed
- **Authority states**: suspended (system-triggered), halted (engineer-triggered)
- **Discovery issues**: Surface out-of-scope work without blocking execution

### Changed
- Renamed "Obsidian Project Historian" to "Historian Agent"
- Renamed "Principal Software Engineer" to "Engineer Agent"
- Core principles expanded from 4 to 4 (tests are sacrosanct, implementation quality is sacrosanct)
- Authority documents remain file-based; only plans migrated to Beads
- Worklog entries now use Beads comments instead of markdown tables

### Removed
- Notion Assistant (all related files)
- Orientation files (consolidated into skills at ~/.claude/skills/)
- File-based plan templates (replaced by Beads epic structure)
- Plan index generation (replaced by Beads queries)
- Authority summary templates (over-engineering removed)

### Migration
- File count reduced from 37 to 20 (47% reduction)
- See `MIGRATION_PLAN.md` for detailed migration guidance
- See `docs/BEADS_INTEGRATION.md` for full V1.3 specification

---

## [1.2.0] - 2026-01-06

### Added
- Initial V1.2 release
- Invocation-only agent architecture
- File-based plans in `plans/active/`
- Historian, Engineer, Orchestrator, Notion Assistant agents
- Authority documents (INVARIANTS.md, DECISIONS.md)
- Templates for all document types
