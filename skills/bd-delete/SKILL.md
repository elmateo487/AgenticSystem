---
name: bd-delete
description: "Delete beads issue with all children. Usage: /bd-delete sv-XXX"
version: 1.2.0
context: inline
allowed-tools: Bash
---

# Delete Beads Issue

Permanently deletes a beads issue and all children, preventing git history resurrection.

## Usage

```
/bd-delete <BEAD_ID>
```

## Execution

Run these commands in sequence:

```bash
# 1. Hard delete with cascade (also cleans JSONL)
bd delete <BEAD_ID> --cascade --force --hard

# 2. Purge tombstones
bd admin compact --purge-tombstones

# 3. Rebuild DB from clean JSONL (prevents git resurrection)
rm .beads/beads.db
bd import -i .beads/issues.jsonl --no-git-history

# 4. Sync
bd sync
```

## Why This Works

- `--hard` immediately deletes from both DB and JSONL (no tombstone)
- `--cascade` deletes all children
- `--purge-tombstones` removes any remaining soft deletes from prior operations
- `rm beads.db` + `--no-git-history` prevents resurrecting from git commits
- Fresh DB import ensures clean state

## Notes

- The `--hard` flag handles JSONL cleanup automatically - no manual grep needed
- Ignore daemon warnings; commands still execute in direct mode

## Verify

```bash
bd show <BEAD_ID>  # Should return "not found"
bd list --json | jq 'length'  # Confirm count
```
