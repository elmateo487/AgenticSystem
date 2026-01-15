#!/usr/bin/env python3
"""
Claude Code PreToolUse hook for beads (bd) command management.

Combines:
1. Command validation (blocks dangerous/incorrect commands)
2. Status propagation (syncs status up/down hierarchy)

Exit codes:
  0 = Allow (command may proceed)
  2 = Block (command rejected with error message on stderr)
"""

import json
import os
import re
import subprocess
import sys
from typing import Optional


def get_command() -> str:
    """Extract the command from stdin JSON (Claude Code PreToolUse format)."""
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            return ""
        data = json.loads(stdin_data)
        return data.get("tool_input", {}).get("command", "")
    except Exception:
        return ""


# =============================================================================
# COMMAND VALIDATION
# =============================================================================


def has_epic_label(command: str) -> bool:
    """Check if command has a label containing 'type:epic'."""
    label_patterns = [
        r'(?:--labels?|-l)\s+"[^"]*type:epic[^"]*"',
        r"(?:--labels?|-l)\s+'[^']*type:epic[^']*'",
        r"(?:--labels?|-l)\s+\S*type:epic\S*",
    ]
    for pattern in label_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def has_epic_type(command: str) -> bool:
    """Check if command has --type epic or -t epic."""
    type_patterns = [
        r'(?:--type|-t)\s+"?epic"?(?:\s|$)',
        r"(?:--type|-t)\s+'?epic'?(?:\s|$)",
    ]
    for pattern in type_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def check_command_guard(command: str) -> bool:
    """Validate bd commands. Exits with code 2 if blocked."""
    # Block: bd ready
    if re.match(r"^\s*bd\s+ready\b", command):
        print("BLOCKED: `bd ready` is not permitted", file=sys.stderr)
        print("Only humans choose what work to execute next.", file=sys.stderr)
        sys.exit(2)

    # Block: bd delete without --hard --force
    if re.match(r"^\s*bd\s+delete\b", command):
        has_hard = "--hard" in command
        has_force = "--force" in command
        if not has_hard or not has_force:
            missing = []
            if not has_hard:
                missing.append("--hard")
            if not has_force:
                missing.append("--force")
            print(f"BLOCKED: `bd delete` requires {' and '.join(missing)}", file=sys.stderr)
            print("Usage: bd delete $ISSUE_ID --hard --force", file=sys.stderr)
            sys.exit(2)

    # Block: bd create with epic label but wrong/missing --type
    if re.match(r"^\s*bd\s+create\b", command):
        if has_epic_label(command) and not has_epic_type(command):
            print("BLOCKED: Epic creation misconfigured", file=sys.stderr)
            print("You specified --label 'type:epic' but did not set --type epic.", file=sys.stderr)
            print('Usage: bd create "Title" --label "type:epic" --type epic', file=sys.stderr)
            sys.exit(2)

    return False


# =============================================================================
# STATUS PROPAGATION HELPERS
# =============================================================================

COMPLETION_PATTERNS = ["done", "complete", "fixed", "resolved", "implemented", "all acs"]
NON_COMPLETION_PATTERNS = ["won't implement", "wont implement", "duplicate", "out of scope"]


def parse_bd_close(command: str) -> tuple[Optional[str], Optional[str]]:
    """Parse bd close command. Returns (issue_id, reason) or (None, None)."""
    if not re.match(r"^\s*bd\s+close\b", command):
        return None, None
    reason_match = re.search(r'(?:-r|--reason)\s+["\']([^"\']+)["\']', command)
    if not reason_match:
        reason_match = re.search(r"(?:-r|--reason)\s+(\S+)", command)
    reason = reason_match.group(1) if reason_match else None
    cmd_without_reason = re.sub(r'(?:-r|--reason)\s+(?:"[^"]*"|\'[^\']*\'|\S+)', "", command)
    parts = cmd_without_reason.split()
    issue_id = None
    for i, part in enumerate(parts):
        if i >= 2 and not part.startswith("-"):
            issue_id = part
            break
    return issue_id, reason


def parse_bd_update(command: str) -> tuple[Optional[str], Optional[str]]:
    """Parse bd update command. Returns (issue_id, status) or (None, None)."""
    if not re.match(r"^\s*bd\s+update\b", command):
        return None, None
    status_match = re.search(r"(?:-s|--status)\s+(\S+)", command)
    if not status_match:
        return None, None
    status = status_match.group(1)
    cmd_without_status = re.sub(r"(?:-s|--status)\s+\S+", "", command)
    parts = cmd_without_status.split()
    issue_id = None
    for i, part in enumerate(parts):
        if i >= 2 and not part.startswith("-"):
            issue_id = part
            break
    return issue_id, status


def run_bd_command(args: list[str]) -> tuple[int, str, str]:
    """Run a bd command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(["bd"] + args, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def get_issue_json(issue_id: str) -> Optional[dict]:
    """Get issue data as dict."""
    code, stdout, _ = run_bd_command(["show", issue_id, "--json"])
    if code != 0 or not stdout.strip():
        return None
    try:
        data = json.loads(stdout)
        return data[0] if isinstance(data, list) else data
    except:
        return None


def get_issue_children(issue_id: str) -> list[dict]:
    """Get direct children of an issue."""
    code, stdout, _ = run_bd_command(["list", "--parent", issue_id, "--json"])
    if code != 0 or not stdout.strip():
        return []
    try:
        return json.loads(stdout)
    except:
        return []


def get_issue_parent(issue_id: str) -> Optional[dict]:
    """Get the parent of an issue, if any."""
    issue = get_issue_json(issue_id)
    if not issue or not issue.get("parent"):
        return None
    return get_issue_json(issue["parent"])


def update_issue_status(issue_id: str, status: str) -> bool:
    """Update an issue's status."""
    code, _, _ = run_bd_command(["update", issue_id, "--status", status])
    return code == 0


def close_issue(issue_id: str, reason: str) -> bool:
    """Close a single issue with the given reason."""
    code, _, _ = run_bd_command(["close", issue_id, "--reason", reason])
    return code == 0


def get_all_open_descendants(issue_id: str) -> list[dict]:
    """Get all open descendants of an issue (recursive)."""
    open_descendants = []
    for child in get_issue_children(issue_id):
        if child.get("status") != "closed":
            open_descendants.append(child)
        open_descendants.extend(get_all_open_descendants(child["id"]))
    return open_descendants


def get_siblings(issue_id: str) -> list[dict]:
    """Get siblings of an issue (other children of same parent)."""
    parent = get_issue_parent(issue_id)
    if not parent:
        return []
    children = get_issue_children(parent.get("id"))
    return [c for c in children if c.get("id") != issue_id]


def any_sibling_blocked(issue_id: str) -> bool:
    """Check if any sibling of the issue is blocked."""
    return any(s.get("status") == "blocked" for s in get_siblings(issue_id))


def is_non_completion_reason(reason: str) -> bool:
    if not reason:
        return False
    reason_lower = reason.lower()
    return any(p in reason_lower for p in NON_COMPLETION_PATTERNS)


def is_completion_reason(reason: str) -> bool:
    if not reason:
        return True
    reason_lower = reason.lower()
    return any(p in reason_lower for p in COMPLETION_PATTERNS)


# =============================================================================
# STATUS PROPAGATION
# =============================================================================


def propagate_in_progress_up_chain(issue_id: str) -> list[str]:
    """Propagate in_progress status up the parent chain."""
    updated = []
    current_id = issue_id
    while True:
        parent = get_issue_parent(current_id)
        if not parent:
            break
        parent_id = parent.get("id")
        parent_status = parent.get("status")
        if parent_status in ("blocked", "closed"):
            break
        if parent_status == "open":
            if update_issue_status(parent_id, "in_progress"):
                updated.append(parent_id)
        current_id = parent_id
    return updated


def propagate_blocked_up_chain(issue_id: str) -> list[str]:
    """Propagate blocked status up the parent chain."""
    updated = []
    current_id = issue_id
    while True:
        parent = get_issue_parent(current_id)
        if not parent:
            break
        parent_id = parent.get("id")
        if parent.get("status") != "blocked":
            if update_issue_status(parent_id, "blocked"):
                updated.append(parent_id)
        current_id = parent_id
    return updated


def propagate_unblock_up_chain(issue_id: str) -> list[str]:
    """Propagate unblock up the chain if no siblings are blocked."""
    updated = []
    current_id = issue_id
    while True:
        if any_sibling_blocked(current_id):
            break
        parent = get_issue_parent(current_id)
        if not parent:
            break
        parent_id = parent.get("id")
        if parent.get("status") == "blocked":
            if update_issue_status(parent_id, "open"):
                updated.append(parent_id)
                current_id = parent_id
            else:
                break
        else:
            break
    return updated


def cascade_close_descendants(issue_id: str, reason: str) -> list[str]:
    """Close all open descendants with the same reason (depth-first)."""
    closed = []
    for child in get_issue_children(issue_id):
        closed.extend(cascade_close_descendants(child["id"], reason))
        if child.get("status") != "closed":
            if close_issue(child["id"], reason):
                closed.append(child["id"])
    return closed


def handle_status_propagation(command: str):
    """Handle status propagation for bd update and bd close commands."""
    # Handle bd update --status
    update_id, new_status = parse_bd_update(command)
    if update_id and new_status:
        issue = get_issue_json(update_id)
        current_status = issue.get("status") if issue else None

        if new_status == "in_progress":
            updated = propagate_in_progress_up_chain(update_id)
            if updated:
                print(f"PROPAGATE: Set {len(updated)} ancestors to in_progress", file=sys.stderr)
                for pid in updated:
                    print(f"  ↑ {pid}", file=sys.stderr)
            return

        if new_status == "blocked":
            updated = propagate_blocked_up_chain(update_id)
            if updated:
                print(f"PROPAGATE: Set {len(updated)} ancestors to blocked", file=sys.stderr)
                for pid in updated:
                    print(f"  ↑ {pid}", file=sys.stderr)
            return

        if current_status == "blocked" and new_status in ("open", "in_progress"):
            updated = propagate_unblock_up_chain(update_id)
            if updated:
                print(f"PROPAGATE: Unblocked {len(updated)} ancestors", file=sys.stderr)
                for pid in updated:
                    print(f"  ↑ {pid}", file=sys.stderr)
            return

    # Handle bd close
    issue_id, reason = parse_bd_close(command)
    if issue_id is None:
        return

    open_descendants = get_all_open_descendants(issue_id)
    if not open_descendants:
        return

    # Non-completion reason → cascade down
    if reason and is_non_completion_reason(reason):
        closed = cascade_close_descendants(issue_id, reason)
        if closed:
            print(f"CASCADE: Closed {len(closed)} descendants with reason: {reason}", file=sys.stderr)
            for cid in closed:
                print(f"  ✓ {cid}", file=sys.stderr)
        return

    # Completion close with open descendants → BLOCK
    child_list = ", ".join(c["id"] for c in open_descendants[:5])
    if len(open_descendants) > 5:
        child_list += f" (+{len(open_descendants) - 5} more)"

    print(f"BLOCKED: Cannot close {issue_id} - has {len(open_descendants)} open descendants", file=sys.stderr)
    print(f"Open: {child_list}", file=sys.stderr)
    print("Close descendants first, or use non-completion reason.", file=sys.stderr)
    sys.exit(2)


# =============================================================================
# MAIN
# =============================================================================


def main():
    command = get_command()
    if not re.match(r"^\s*bd\s+", command):
        sys.exit(0)
    check_command_guard(command)
    handle_status_propagation(command)
    sys.exit(0)


if __name__ == "__main__":
    main()
