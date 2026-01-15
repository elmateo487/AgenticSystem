#!/usr/bin/env python3
"""
Combined Claude Code hooks for Bash commands (PreToolUse and PostToolUse).

Combines:
1. Beads (bd) command validation and status propagation
2. System temp pollution detection for SafeVision
3. Auto-block on dependency creation

Exit codes:
  0 = Allow (command may proceed)
  2 = Block (command rejected with error message on stderr)
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


_HOOK_CWD = None  # Store cwd from stdin for bd commands
_PROJECT_ROOT = None  # Cached project root (parent of .beads)
_HOOK_EVENT = None  # PreToolUse or PostToolUse


def find_project_root(start_path: str) -> Optional[str]:
    """Search upward from start_path to find directory containing .beads with a database."""
    current = Path(start_path).resolve()
    while current != current.parent:
        beads_dir = current / ".beads"
        # Check for actual database (not just registry)
        if beads_dir.is_dir() and (
            (beads_dir / "beads.db").exists() or (beads_dir / "issues.jsonl").exists()
        ):
            return str(current)
        current = current.parent
    # Check root
    beads_dir = current / ".beads"
    if beads_dir.is_dir() and (
        (beads_dir / "beads.db").exists() or (beads_dir / "issues.jsonl").exists()
    ):
        return str(current)
    return None


def get_project_root() -> Optional[str]:
    """Get the project root (directory containing .beads)."""
    global _PROJECT_ROOT
    if _PROJECT_ROOT is not None:
        return _PROJECT_ROOT

    if _HOOK_CWD:
        _PROJECT_ROOT = find_project_root(_HOOK_CWD)

    return _PROJECT_ROOT


def get_command() -> str:
    """Extract the command from stdin JSON (Claude Code hook format)."""
    global _HOOK_CWD, _HOOK_EVENT
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            return ""
        data = json.loads(stdin_data)
        _HOOK_CWD = data.get("cwd")  # Capture cwd for bd commands
        _HOOK_EVENT = data.get("hook_event_name", "PreToolUse")
        return data.get("tool_input", {}).get("command", "")
    except Exception:
        return ""


# =============================================================================
# BEADS COMMAND VALIDATION
# =============================================================================


def has_type_label(command: str, type_name: str) -> bool:
    """Check if command has a label containing 'type:<type_name>'."""
    label_patterns = [
        rf'(?:--labels?|-l)\s+"[^"]*type:{type_name}[^"]*"',
        rf"(?:--labels?|-l)\s+'[^']*type:{type_name}[^']*'",
        rf"(?:--labels?|-l)\s+\S*type:{type_name}\S*",
    ]
    for pattern in label_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def has_any_type_label(command: str) -> Optional[str]:
    """Check if command has any type label. Returns the type if found, None otherwise."""
    for type_name in ["epic", "ticket", "ac", "research"]:
        if has_type_label(command, type_name):
            return type_name
    return None


def has_epic_label(command: str) -> bool:
    """Check if command has a label containing 'type:epic'."""
    return has_type_label(command, "epic")


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


def has_parent_flag(command: str) -> Optional[str]:
    """Check if command has --parent flag. Returns parent ID if found, None otherwise."""
    parent_patterns = [
        r'(?:--parent|-p)\s+"([^"]+)"',
        r"(?:--parent|-p)\s+'([^']+)'",
        r"(?:--parent|-p)\s+(\S+)",
    ]
    for pattern in parent_patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1)
    return None


def has_comment_flag(command: str) -> Optional[str]:
    """Check if command has a comment/message flag. Returns comment text if found."""
    patterns = [
        r'(?:--comment|-m|--message)\s+"([^"]+)"',
        r"(?:--comment|-m|--message)\s+'([^']+)'",
    ]
    for pattern in patterns:
        match = re.search(pattern, command)
        if match:
            return match.group(1)
    return None


def get_issue_status(issue_id: str) -> Optional[str]:
    """Get current status of an issue."""
    issue = get_issue_json(issue_id)
    return issue.get("status") if issue else None


def has_blocking_dependencies(issue_id: str) -> bool:
    """Check if issue has any blocking dependencies (something that blocks it)."""
    code, stdout, _ = run_bd_command(["dep", "list", issue_id, "--type", "blocks", "--json"])
    if code != 0 or not stdout.strip():
        return False
    try:
        deps = json.loads(stdout)
        return len(deps) > 0
    except:
        return False




def parse_issue_id_from_command(command: str, verb: str) -> Optional[str]:
    """Parse issue ID from a bd command like 'bd update ID ...' or 'bd close ID ...'."""
    # Remove the status/reason flags to find the bare issue ID
    cmd_clean = re.sub(r'(?:-s|--status)\s+\S+', '', command)
    cmd_clean = re.sub(r'(?:-r|--reason)\s+(?:"[^"]*"|\'[^\']*\'|\S+)', '', cmd_clean)
    cmd_clean = re.sub(r'(?:--comment|-m|--message)\s+(?:"[^"]*"|\'[^\']*\'|\S+)', '', cmd_clean)
    parts = cmd_clean.split()
    # Pattern: bd <verb> <issue_id> [other flags]
    for i, part in enumerate(parts):
        if i >= 2 and not part.startswith("-"):
            return part
    return None


def get_issue_type_label(issue_id: str) -> Optional[str]:
    """Get the type label of an issue (epic, ticket, ac, research)."""
    issue = get_issue_json(issue_id)
    if not issue:
        return None
    labels = issue.get("labels", [])
    for label in labels:
        if label.startswith("type:"):
            return label.replace("type:", "")
    return None


VALID_STATUSES = ["open", "in_progress", "blocked", "pending_approval"]

# Canonical close reason patterns
COMPLETION_REASONS = ["done", "fixed", "all acs complete", "all tickets complete"]
NON_COMPLETION_PREFIXES = ["won't implement", "wont implement", "duplicate", "out of scope"]


def is_valid_close_reason(reason: str) -> Tuple[bool, str]:
    """Check if close reason matches canonical patterns. Returns (is_valid, suggestion)."""
    if not reason:
        return False, ""

    reason_lower = reason.lower().strip()

    # Check completion reasons (exact match)
    if reason_lower in COMPLETION_REASONS:
        return True, ""

    # Check non-completion prefixes (must have explanation after)
    for prefix in NON_COMPLETION_PREFIXES:
        if reason_lower.startswith(prefix):
            # Check if there's content after the prefix
            rest = reason_lower[len(prefix):].strip(" -:")
            if rest:
                return True, ""
            else:
                return False, f'Non-completion reason needs explanation: "{prefix} - [why]"'

    return False, (
        "Use canonical close reason:\n"
        "  Completion: Done, Fixed, All ACs complete\n"
        "  Non-completion: Won't implement - [why], Duplicate - [of what], Out of scope - [why]"
    )


def check_bd_command_guard(command: str) -> Optional[str]:
    """Validate bd commands. Returns error message if blocked, None otherwise."""
    # Block: bd ready
    if re.match(r"^\s*bd\s+ready\b", command):
        return "BLOCKED: `bd ready` is not permitted\nOnly humans choose what work to execute next."

    # Block: bd delete without --hard --force, and require --cascade if has children
    if re.match(r"^\s*bd\s+delete\b", command):
        has_hard = "--hard" in command
        has_force = "--force" in command
        has_cascade = "--cascade" in command

        # Check required flags
        if not has_hard or not has_force:
            missing = []
            if not has_hard:
                missing.append("--hard")
            if not has_force:
                missing.append("--force")
            return f"BLOCKED: `bd delete` requires {' and '.join(missing)}\nUsage: bd delete $ISSUE_ID --hard --force --cascade"

        # Check for children - require --cascade if any exist
        if not has_cascade:
            issue_id = parse_issue_id_from_command(command, "delete")
            if issue_id:
                children = get_issue_children(issue_id)
                if children:
                    return (
                        f"BLOCKED: {issue_id} has {len(children)} children\n"
                        "Use --cascade to delete with all children:\n"
                        f"  bd delete {issue_id} --hard --force --cascade"
                    )

    # Block: bd update --status validations
    if re.match(r"^\s*bd\s+update\b", command):
        status_match = re.search(r"(?:-s|--status)\s+(\S+)", command)
        if status_match:
            new_status = status_match.group(1).lower()
            issue_id = parse_issue_id_from_command(command, "update")

            # Check 1: Valid status values only
            if new_status not in VALID_STATUSES:
                return (
                    f'BLOCKED: Invalid status "{new_status}"\n'
                    f'Valid statuses: {", ".join(VALID_STATUSES)}'
                )

            # Check 2: Can't block closed items
            if new_status == "blocked" and issue_id:
                current_status = get_issue_status(issue_id)
                if current_status == "closed":
                    return (
                        f"BLOCKED: Cannot block closed issue {issue_id}\n"
                        "Reopen the issue first if work needs to resume."
                    )

            # Check 3: Blocking requires a blocking dependency
            if new_status == "blocked" and issue_id:
                has_deps = has_blocking_dependencies(issue_id)
                if not has_deps:
                    return (
                        "BLOCKED: Setting status to blocked requires a blocking dependency\n"
                        f'First add the blocker: bd dep BLOCKER_ID --blocks {issue_id}\n'
                        f'Then: bd update {issue_id} --status blocked'
                    )

            # Check 4: Unblocking requires explanation
            if new_status in ("open", "in_progress") and issue_id:
                current_status = get_issue_status(issue_id)
                if current_status == "blocked":
                    has_comment = has_comment_flag(command)
                    if not has_comment:
                        return (
                            "BLOCKED: Unblocking requires explanation\n"
                            'Add --comment "how block was resolved" to the command\n'
                            'Example: bd update ID --status open --comment "ticket-123 completed"'
                        )

    # Block: bd close without --reason or with invalid reason
    if re.match(r"^\s*bd\s+close\b", command):
        # Try double-quoted reason first, then single-quoted, then unquoted
        reason_match = re.search(r'(?:-r|--reason)\s+"([^"]+)"', command)
        if not reason_match:
            reason_match = re.search(r"(?:-r|--reason)\s+'([^']+)'", command)
        if not reason_match:
            reason_match = re.search(r"(?:-r|--reason)\s+(\S+)", command)

        if not reason_match:
            return (
                'BLOCKED: `bd close` requires --reason\n'
                'Usage: bd close ISSUE_ID --reason "Done"\n'
                'Valid reasons: Done, Fixed, All ACs complete, Won\'t implement - [why], Duplicate - [of], Out of scope - [why]'
            )

        reason = reason_match.group(1)
        is_valid, suggestion = is_valid_close_reason(reason)
        if not is_valid:
            return f'BLOCKED: Invalid close reason "{reason}"\n{suggestion}'

    # Block: bd create validations
    if re.match(r"^\s*bd\s+create\b", command):
        # Check 1: Epic label requires --type epic
        if has_epic_label(command) and not has_epic_type(command):
            return 'BLOCKED: Epic creation misconfigured\nYou specified --label \'type:epic\' but did not set --type epic.\nUsage: bd create "Title" --label "type:epic" --type epic'

        # Check 2: Require type label (epic, ticket, ac, or research)
        type_label = has_any_type_label(command)
        if not type_label:
            return (
                'BLOCKED: `bd create` requires a type label\n'
                'Use one of: --label "type:epic", --label "type:ticket", --label "type:ac", --label "type:research"\n'
                'Example: bd create "Title" --label "type:ticket" --parent EPIC_ID'
            )

        # Check 3: AC must have --parent
        if type_label == "ac":
            parent_id = has_parent_flag(command)
            if not parent_id:
                return (
                    'BLOCKED: AC (type:ac) must have a parent ticket\n'
                    'Usage: bd create "AC title" --label "type:ac" --parent TICKET_ID'
                )

            # Check 4: AC parent must be a ticket, not an epic
            parent_type = get_issue_type_label(parent_id)
            if parent_type == "epic":
                return (
                    f'BLOCKED: AC cannot be child of epic ({parent_id})\n'
                    'ACs must be children of tickets, not epics.\n'
                    'Hierarchy: Epic → Ticket → AC'
                )

            # Check 5: AC parent cannot be another AC
            if parent_type == "ac":
                return (
                    f'BLOCKED: AC cannot be child of another AC ({parent_id})\n'
                    'ACs must be children of tickets.\n'
                    'Hierarchy: Epic → Ticket → AC'
                )

        # Check 6: Ticket parent (if specified) must be epic, not AC
        if type_label == "ticket":
            parent_id = has_parent_flag(command)
            if parent_id:
                parent_type = get_issue_type_label(parent_id)
                if parent_type == "ac":
                    return (
                        f'BLOCKED: Ticket cannot be child of AC ({parent_id})\n'
                        'Tickets must be children of epics.\n'
                        'Hierarchy: Epic → Ticket → AC'
                    )
                if parent_type == "ticket":
                    return (
                        f'BLOCKED: Ticket cannot be child of another ticket ({parent_id})\n'
                        'Tickets must be children of epics.\n'
                        'Hierarchy: Epic → Ticket → AC'
                    )

    return None


# =============================================================================
# BEADS STATUS PROPAGATION
# =============================================================================

COMPLETION_PATTERNS = ["done", "complete", "fixed", "resolved", "implemented", "all acs"]
NON_COMPLETION_PATTERNS = ["won't implement", "wont implement", "duplicate", "out of scope"]


def parse_bd_close(command: str) -> Tuple[Optional[str], Optional[str]]:
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


def parse_bd_update(command: str) -> Tuple[Optional[str], Optional[str]]:
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


def run_bd_command(args: list) -> Tuple[int, str, str]:
    """Run a bd command and return (returncode, stdout, stderr)."""
    try:
        # Run from project root so bd finds .beads naturally
        project_root = get_project_root()
        result = subprocess.run(
            ["bd"] + args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=project_root,
        )
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


def get_issue_children(issue_id: str) -> list:
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


def get_all_open_descendants(issue_id: str) -> list:
    """Get all open descendants of an issue (recursive)."""
    open_descendants = []
    for child in get_issue_children(issue_id):
        if child.get("status") != "closed":
            open_descendants.append(child)
        open_descendants.extend(get_all_open_descendants(child["id"]))
    return open_descendants


def get_siblings(issue_id: str) -> list:
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


def propagate_in_progress_up_chain(issue_id: str) -> list:
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


def propagate_blocked_up_chain(issue_id: str) -> list:
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


def propagate_unblock_up_chain(issue_id: str) -> list:
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


def cascade_close_descendants(issue_id: str, reason: str) -> list:
    """Close all open descendants with the same reason (depth-first)."""
    closed = []
    for child in get_issue_children(issue_id):
        closed.extend(cascade_close_descendants(child["id"], reason))
        if child.get("status") != "closed":
            if close_issue(child["id"], reason):
                closed.append(child["id"])
    return closed


def handle_bd_status_propagation(command: str) -> Optional[str]:
    """Handle status propagation for bd update and bd close commands. Returns block message or None."""
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
            return None

        if new_status == "blocked":
            updated = propagate_blocked_up_chain(update_id)
            if updated:
                print(f"PROPAGATE: Set {len(updated)} ancestors to blocked", file=sys.stderr)
                for pid in updated:
                    print(f"  ↑ {pid}", file=sys.stderr)
            return None

        if current_status == "blocked" and new_status in ("open", "in_progress"):
            updated = propagate_unblock_up_chain(update_id)
            if updated:
                print(f"PROPAGATE: Unblocked {len(updated)} ancestors", file=sys.stderr)
                for pid in updated:
                    print(f"  ↑ {pid}", file=sys.stderr)
            return None

    # Handle bd close
    issue_id, reason = parse_bd_close(command)
    if issue_id is None:
        return None

    open_descendants = get_all_open_descendants(issue_id)
    if not open_descendants:
        return None

    # Non-completion reason → cascade down
    if reason and is_non_completion_reason(reason):
        closed = cascade_close_descendants(issue_id, reason)
        if closed:
            print(f"CASCADE: Closed {len(closed)} descendants with reason: {reason}", file=sys.stderr)
            for cid in closed:
                print(f"  ✓ {cid}", file=sys.stderr)
        return None

    # Completion close with open descendants → BLOCK
    child_list = ", ".join(c["id"] for c in open_descendants[:5])
    if len(open_descendants) > 5:
        child_list += f" (+{len(open_descendants) - 5} more)"

    return f"BLOCKED: Cannot close {issue_id} - has {len(open_descendants)} open descendants\nOpen: {child_list}\nClose descendants first, or use non-completion reason."


# =============================================================================
# SYSTEM TEMP POLLUTION CHECK
# =============================================================================

SYSTEM_TEMP_PATTERNS = [
    r"/tmp(?:/|$)",
    r"/private/tmp(?:/|$)",
    r"/var(?:/|$)",
    r"/private/var(?:/|$)",
    r"/var/tmp(?:/|$)",
    r"/private/var/tmp(?:/|$)",
    r"/var/folders(?:/|$)",
    r"/private/var/folders(?:/|$)",
]

VIDEO_TOOLS = ["ffmpeg", "mkvmerge", "mkvextract", "dovi_tool", "x265", "hevc_nvenc"]
OUTPUT_FLAGS = ["-o", "--output", "-y"]

PYTHON_TEMP_PATTERNS = [
    r"tempfile\.mkdtemp\s*\(\s*\)",
    r"tempfile\.mkstemp\s*\(\s*\)",
    r"tempfile\.gettempdir\s*\(\s*\)",
    r"tempfile\.NamedTemporaryFile\s*\(\s*\)",
]

SAFEVISION_FILE_PATTERNS = [
    r"safevision", r"\.hevc", r"\.mkv", r"\.mp4", r"\.m4a",
    r"\.eac3", r"\.ac3", r"\.wav", r"dv_retime", r"clip_\d+",
    r"segment_\d+", r"frame_\d+",
]


def is_system_temp_path(path: str) -> bool:
    """Check if a path is in a system temp directory."""
    return any(re.search(p, path) for p in SYSTEM_TEMP_PATTERNS)


def is_safevision_related(command: str) -> bool:
    """Check if a command is SafeVision-related."""
    command_lower = command.lower()
    return any(re.search(p, command_lower) for p in SAFEVISION_FILE_PATTERNS)


def check_video_tool_output(command: str) -> Optional[str]:
    """Check if a video tool command writes to system temp."""
    if not any(tool in command for tool in VIDEO_TOOLS):
        return None

    words = command.split()
    for i, word in enumerate(words):
        if word in OUTPUT_FLAGS and i + 1 < len(words):
            next_word = words[i + 1]
            if is_system_temp_path(next_word):
                return next_word
        if is_system_temp_path(word) and word.endswith(('.mkv', '.mp4', '.hevc', '.m4a', '.eac3', '.ac3', '.wav')):
            return word
    return None


def check_python_temp_usage(command: str) -> Optional[str]:
    """Check if Python uses tempfile without dir parameter."""
    if "python" not in command and "tempfile" not in command:
        return None

    for pattern in PYTHON_TEMP_PATTERNS:
        match = re.search(pattern, command)
        if match and is_safevision_related(command):
            return match.group(0)
    return None


def check_system_temp(command: str) -> Optional[str]:
    """Check command for system temp violations. Returns error message or None."""
    if not command or not command.strip():
        return None

    violation = check_video_tool_output(command)
    if violation:
        return (
            f"BLOCKED: Command writes to system temp: {violation}\n"
            f"Use external drive: /Volumes/[DRIVE]/safevision_scratch/"
        )

    violation = check_python_temp_usage(command)
    if violation:
        return (
            f"BLOCKED: Python tempfile without dir=: {violation}\n"
            f"Use: tempfile.mkdtemp(dir='/Volumes/External/safevision_scratch/')"
        )

    return None


# =============================================================================
# POST-TOOL-USE: AUTO-ACTIONS AFTER COMMANDS
# =============================================================================


def parse_bd_dep_blocks(command: str) -> Optional[str]:
    """Parse 'bd dep X --blocks Y' command. Returns blocked issue ID (Y) or None."""
    if not re.match(r"^\s*bd\s+dep\b", command):
        return None
    # Match --blocks or -b flag
    blocks_match = re.search(r'(?:--blocks|-b)\s+(\S+)', command)
    if blocks_match:
        return blocks_match.group(1)
    return None


def is_delete_command(command: str) -> bool:
    """Check if command is 'bd delete'."""
    return bool(re.match(r"^\s*bd\s+delete\b", command))


def run_purge_cleanup():
    """Run cleanup after hard delete: compact to purge tombstones."""
    code, _, _ = run_bd_command(["admin", "compact", "--purge-tombstones"])
    if code == 0:
        print("AUTO: Purged tombstones", file=sys.stderr)


def handle_post_tool_use(command: str):
    """Handle PostToolUse events - auto-actions after commands complete."""
    # Auto-block when dependency created with --blocks
    blocked_id = parse_bd_dep_blocks(command)
    if blocked_id:
        # Check current status - only auto-block if not already blocked
        current_status = get_issue_status(blocked_id)
        if current_status and current_status != "blocked" and current_status != "closed":
            success = update_issue_status(blocked_id, "blocked")
            if success:
                print(f"AUTO: Set {blocked_id} to blocked (dependency created)", file=sys.stderr)

    # Auto-purge after delete (we require --hard via PreToolUse anyway)
    if is_delete_command(command):
        run_purge_cleanup()


# =============================================================================
# MAIN
# =============================================================================


def main():
    command = get_command()
    if not command:
        sys.exit(0)

    # PostToolUse: handle auto-actions after command completes
    if _HOOK_EVENT == "PostToolUse":
        if re.match(r"^\s*bd\s+", command):
            handle_post_tool_use(command)
        sys.exit(0)

    # PreToolUse: validation and guards
    # Check beads commands
    if re.match(r"^\s*bd\s+", command):
        # Command guard
        error = check_bd_command_guard(command)
        if error:
            print(error, file=sys.stderr)
            sys.exit(2)

        # Status propagation (may print info to stderr, may block)
        error = handle_bd_status_propagation(command)
        if error:
            print(error, file=sys.stderr)
            sys.exit(2)

    # Check system temp pollution
    error = check_system_temp(command)
    if error:
        print(error, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
