# PLAN INDEX GENERATION

## Authority
This document does not grant authority. It provides technical guidance only.

---

## Purpose

This document describes how to generate and maintain a PLAN_INDEX.md file that provides a quick overview of all plans without loading each plan file.

---

## Design Principles

1. **Committed Artifact**: Index is version-controlled, not runtime-generated
2. **Manual Trigger**: Human explicitly invokes generation/update
3. **Non-Authoritative**: Index navigates to plans but doesn't grant authority
4. **Lightweight**: Quick to scan without parsing all plan files

---

## Generation Approach

### Recommended: Manual Update

For most projects, manually updating the index is sufficient:

```bash
# 1. Check plan directories
ls plans/active/
ls plans/on-hold/
ls plans/archive/

# 2. Open each new/changed plan and extract objective
head -20 plans/active/027_*.md

# 3. Update PLAN_INDEX.md
# (Use editor or invoke Historian agent)

# 4. Commit
git add plans/PLAN_INDEX.md
git commit -m "Update plan index"
```

### Alternative: Script-Assisted Generation

```python
#!/usr/bin/env python3
"""
generate_plan_index.py

Usage: python generate_plan_index.py <plans_directory>

Generates a PLAN_INDEX.md from plan files.
Extracts objective from each plan's ## Objective section.
"""

import sys
import re
from pathlib import Path
from datetime import date

def extract_plan_info(plan_path: Path) -> dict:
    """Extract objective and status from a plan file."""
    content = plan_path.read_text()

    # Extract objective (first line after ## Objective)
    obj_match = re.search(r'## Objective\n+([^\n]+)', content)
    objective = obj_match.group(1) if obj_match else "No objective found"

    # Determine status from checkboxes
    checkboxes = re.findall(r'- \[([ x])\]', content)
    if not checkboxes:
        status = "Ready"
    elif all(c == 'x' for c in checkboxes):
        status = "Complete"
    elif any(c == 'x' for c in checkboxes):
        status = "In Progress"
    else:
        status = "Ready"

    # Get last modified from git or file mtime
    mtime = plan_path.stat().st_mtime
    last_modified = date.fromtimestamp(mtime).isoformat()

    return {
        "name": plan_path.stem,
        "objective": objective[:60] + "..." if len(objective) > 60 else objective,
        "status": status,
        "last_modified": last_modified
    }


def generate_index(plans_dir: Path) -> str:
    """Generate PLAN_INDEX.md content."""
    today = date.today().isoformat()

    active_plans = []
    onhold_plans = []
    archived_plans = []

    # Scan directories
    active_dir = plans_dir / "active"
    onhold_dir = plans_dir / "on-hold"
    archive_dir = plans_dir / "archive"

    if active_dir.exists():
        for f in sorted(active_dir.glob("*.md")):
            if f.name != "README.md":
                active_plans.append(extract_plan_info(f))

    if onhold_dir.exists():
        for f in sorted(onhold_dir.glob("*.md")):
            if f.name != "README.md":
                onhold_plans.append(extract_plan_info(f))

    if archive_dir.exists():
        for f in sorted(archive_dir.glob("*.md"), reverse=True)[:5]:
            if f.name != "README.md":
                archived_plans.append(extract_plan_info(f))

    # Build output
    output = f"""# PLAN INDEX

Generated: {today}

## Authority
This document does not grant authority. It provides navigation only.

---

## Active Plans

| Plan | Objective | Status | Last Modified |
|------|-----------|--------|---------------|
"""
    for p in active_plans:
        output += f"| {p['name']} | {p['objective']} | {p['status']} | {p['last_modified']} |\n"

    output += """
## On-Hold Plans

| Plan | Reason | Since |
|------|--------|-------|
"""
    if onhold_plans:
        for p in onhold_plans:
            output += f"| {p['name']} | (see plan) | {p['last_modified']} |\n"
    else:
        output += "(none)\n"

    output += """
## Recently Archived

| Plan | Completed | Outcome |
|------|-----------|---------|
"""
    for p in archived_plans:
        output += f"| {p['name']} | {p['last_modified']} | (see plan) |\n"

    output += """
---

## Plan Lifecycle

```
plans/active/     -> In progress or ready for execution
plans/on-hold/    -> Paused pending decisions/resources
plans/archive/    -> Completed or abandoned
```
"""
    return output


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_plan_index.py <plans_directory>")
        sys.exit(1)

    plans_dir = Path(sys.argv[1])
    if not plans_dir.exists():
        print(f"Directory not found: {plans_dir}")
        sys.exit(1)

    print(generate_index(plans_dir))
```

---

## Usage

### Manual Update

```bash
# After creating/archiving a plan
vim plans/PLAN_INDEX.md
# Update the appropriate table
git add plans/PLAN_INDEX.md
git commit -m "Update plan index"
```

### Script-Assisted

```bash
# Generate to stdout
python scripts/generate_plan_index.py plans/

# Generate to file
python scripts/generate_plan_index.py plans/ > plans/PLAN_INDEX.md

# Review and commit
git diff plans/PLAN_INDEX.md
git add plans/PLAN_INDEX.md
git commit -m "Regenerate plan index"
```

---

## When to Update

Update the plan index when:

- New plan created in `plans/active/`
- Plan moved to `plans/on-hold/`
- Plan moved to `plans/archive/`
- Plan status changes significantly (Ready -> In Progress)

---

## Token Efficiency

Loading PLAN_INDEX.md (~50-100 tokens) is much cheaper than loading all active plans (~2000-5000 tokens per plan). This enables:

1. Orchestrator scans index to understand project state
2. Agent loads only the specific plan needed
3. Reduces context window usage by 80-90% for plan discovery

---

## V1.2 Alignment

This approach preserves all SYSTEM V1.2 principles:

- **Fresh context**: Index is a file, loaded fresh each invocation
- **Auditability**: Index is version-controlled
- **No runtime generation**: Index updated via explicit human invocation
- **Plans grant authority**: Index navigates, plans authorize
