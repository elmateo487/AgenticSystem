# AUTHORITY SUMMARY GENERATION

## Authority
This document does not grant authority. It provides technical guidance only.

---

## Purpose

This document describes how to generate authority summary files (INVARIANTS_SUMMARY.md, DECISIONS_SUMMARY.md) for efficient token loading while maintaining auditability.

---

## Design Principles

1. **Deterministic**: Same input always produces same output
2. **Committed Artifacts**: Summaries are version-controlled, not runtime-generated
3. **Non-Authoritative**: Summaries never grant authority; full documents required for that
4. **Manual Trigger**: Human explicitly invokes generation after source changes

---

## Generation Approach

### Recommended: Manual Generation with Template

For most projects, manual generation following the template is sufficient and most auditable:

1. Read full authority document
2. Extract key information per template
3. Write summary file
4. Commit as artifact

**Template**: `system/v1.2/templates/AUTHORITY_SUMMARY_TEMPLATE.md`

### Alternative: Script-Assisted Generation

For projects with frequently changing authority documents, a generation script can help:

```python
#!/usr/bin/env python3
"""
generate_authority_summary.py

Usage: python generate_authority_summary.py <source_file> <output_file>

Generates a summary of an authority document.
Output is deterministic and suitable for version control.
"""

import sys
import re
import hashlib
from datetime import date
from pathlib import Path

def generate_invariants_summary(source_path: Path) -> str:
    """Generate summary for INVARIANTS.md"""
    content = source_path.read_text()

    # Extract invariant names and statements
    invariants = []
    for match in re.finditer(r'## ([^\n]+)\n\n\*\*Statement\*\*\n([^\n]+)', content):
        name = match.group(1)
        statement = match.group(2)
        invariants.append((name, statement))

    # Build summary
    today = date.today().isoformat()
    file_hash = hashlib.sha256(content.encode()).hexdigest()[:12]

    summary = f"""# INVARIANTS SUMMARY

Generated: {today} | Source: INVARIANTS.md (sha256: {file_hash})

## Authority
This document does not grant authority. Load full INVARIANTS.md for authority.

## Active Invariants

"""
    for i, (name, statement) in enumerate(invariants, 1):
        summary += f"{i}. **{name}** - {statement}\n\n"

    summary += """---

## When to Load Full Document

Load full INVARIANTS.md when:
- Implementing new features (need enforcement details)
- Validating code changes (need halt conditions)
- Drafting new invariants (need full template structure)
"""
    return summary


def generate_decisions_summary(source_path: Path) -> str:
    """Generate summary for DECISIONS.md"""
    content = source_path.read_text()

    # Extract decision headers
    decisions = []
    for match in re.finditer(r'## (\d{4}-\d{2}-\d{2}) . ([^\n]+)\n', content):
        date_str = match.group(1)
        title = match.group(2)
        decisions.append((date_str, title))

    # Build summary
    today = date.today().isoformat()
    file_hash = hashlib.sha256(content.encode()).hexdigest()[:12]

    summary = f"""# DECISIONS SUMMARY

Generated: {today} | Source: DECISIONS.md (sha256: {file_hash})

## Authority
This document does not grant authority. Load full DECISIONS.md for authority.

## Active Decisions

| Date | Decision |
|------|----------|
"""
    for date_str, title in decisions:
        summary += f"| {date_str} | {title} |\n"

    summary += """
---

## When to Load Full Document

Load full DECISIONS.md when:
- Implementing features (need full context and consequences)
- Evaluating alternatives (need rejected options)
- Drafting new decisions (need full template structure)
"""
    return summary


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_authority_summary.py <source_file> <output_file>")
        sys.exit(1)

    source_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if "INVARIANTS" in source_path.name.upper():
        summary = generate_invariants_summary(source_path)
    elif "DECISIONS" in source_path.name.upper():
        summary = generate_decisions_summary(source_path)
    else:
        print(f"Unknown document type: {source_path.name}")
        sys.exit(1)

    output_path.write_text(summary)
    print(f"Generated: {output_path}")
```

---

## Usage Examples

### Manual Generation

```bash
# 1. Review source document
cat authority/INVARIANTS.md

# 2. Create/update summary following template
# (Use editor or invoke Historian agent)

# 3. Commit
git add authority/INVARIANTS_SUMMARY.md
git commit -m "Update INVARIANTS_SUMMARY.md"
```

### Script-Assisted Generation

```bash
# Generate INVARIANTS summary
python scripts/generate_authority_summary.py \
    authority/INVARIANTS.md \
    authority/INVARIANTS_SUMMARY.md

# Generate DECISIONS summary
python scripts/generate_authority_summary.py \
    authority/DECISIONS.md \
    authority/DECISIONS_SUMMARY.md

# Review and commit
git diff authority/*_SUMMARY.md
git add authority/*_SUMMARY.md
git commit -m "Regenerate authority summaries"
```

---

## Validation

After generation, verify:

1. **Authority declaration present**: "This document does not grant authority"
2. **Source reference present**: Includes source file name
3. **Hash matches** (if using script): sha256 of source matches summary header
4. **All items included**: Summary lists all invariants/decisions from source
5. **Committed**: Summary is version-controlled

---

## When to Regenerate

Regenerate summaries when:

- Authority document is modified
- New invariant or decision is added
- Existing invariant or decision is removed or superseded
- Significant rewording that changes meaning

Do NOT regenerate for:
- Formatting changes only
- Typo fixes that don't change meaning
- Implementation status updates

---

## V1.2 Alignment

This approach preserves all SYSTEM V1.2 principles:

- **Fresh context**: Summaries are files, loaded fresh each invocation
- **Auditability**: Summaries are version-controlled artifacts
- **No runtime generation**: Summaries generated via explicit human invocation
- **Documentation as source of truth**: Summaries reference (never replace) authority docs
