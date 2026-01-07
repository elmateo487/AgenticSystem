# SYSTEM V1.2 - Invocation-Only Agent Architecture

A governance framework for Claude Code that provides structured, auditable agent coordination.

## Setup

Clone to the canonical location on all machines:

```bash
git clone git@github.com:mklarson/system-v1.2.git ~/Developer/system-v1.2
```

## Usage

Reference from any project's CLAUDE.md:

```markdown
## System Documentation

```
~/Developer/system-v1.2/
├── orientation/           # Role-specific onboarding
├── agents/                # Full agent specifications
├── templates/             # Document templates
├── examples/              # Pattern examples
├── CHANGELOG.md           # Version history
└── INDEX.md               # Navigation
```
```

## Key Files

- `INDEX.md` - Navigation and structure overview
- `CHANGELOG.md` - Version history
- `orientation/` - Start here for agent orientation files
- `agents/` - Full agent specifications
- `templates/` - Document templates for projects
- `examples/` - Usage pattern examples
- `docs/` - Additional documentation

## Sync

Keep in sync across machines:

```bash
cd ~/Developer/system-v1.2
git pull
```

## Versioning

This repository tracks V1.2 of the system. The version is immutable once published; updates increment the version.
