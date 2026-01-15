#!/usr/bin/env python3
"""
Claude Code PreToolUse hook to detect system temp pollution.

Blocks commands that would create SafeVision-related temp files in system
directories (/tmp, /private/tmp, /var, /private/var).

Exit codes:
  0 = Allow (command may proceed)
  2 = Block (message on stderr)
"""

import json
import re
import sys
from typing import Optional, Tuple

# System temp paths that should not be used for SafeVision files
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

# Video processing tools that create large temp files
VIDEO_TOOLS = ["ffmpeg", "mkvmerge", "mkvextract", "dovi_tool", "x265", "hevc_nvenc"]

# Output file flags for video tools
OUTPUT_FLAGS = ["-o", "--output", "-y"]

# Python patterns that might create temp files
PYTHON_TEMP_PATTERNS = [
    r"tempfile\.mkdtemp\s*\(\s*\)",
    r"tempfile\.mkstemp\s*\(\s*\)",
    r"tempfile\.gettempdir\s*\(\s*\)",
    r"tempfile\.NamedTemporaryFile\s*\(\s*\)",
]

# SafeVision-related file patterns
SAFEVISION_FILE_PATTERNS = [
    r"safevision", r"\.hevc", r"\.mkv", r"\.mp4", r"\.m4a",
    r"\.eac3", r"\.ac3", r"\.wav", r"dv_retime", r"clip_\d+",
    r"segment_\d+", r"frame_\d+",
]


def get_command() -> str:
    """Extract command from stdin JSON."""
    try:
        data = json.loads(sys.stdin.read())
        return data.get("tool_input", {}).get("command", "")
    except:
        return ""


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


def check_command(command: str) -> Tuple[bool, str]:
    """Check command for violations. Returns (should_block, message)."""
    if not command or not command.strip():
        return False, ""

    violation = check_video_tool_output(command)
    if violation:
        return True, (
            f"BLOCKED: Command writes to system temp: {violation}\n"
            f"Use external drive: /Volumes/[DRIVE]/safevision_scratch/"
        )

    violation = check_python_temp_usage(command)
    if violation:
        return True, (
            f"BLOCKED: Python tempfile without dir=: {violation}\n"
            f"Use: tempfile.mkdtemp(dir='/Volumes/External/safevision_scratch/')"
        )

    return False, ""


def main():
    command = get_command()

    # Debug: log what command was received
    with open("/tmp/check_system_temp_debug.log", "a") as f:
        f.write(f"Command received: {repr(command)}\n")

    should_block, message = check_command(command)

    if should_block:
        print(message, file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
