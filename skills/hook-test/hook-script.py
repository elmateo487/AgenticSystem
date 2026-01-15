#!/usr/bin/env python3
import json
import sys

try:
    stdin_data = sys.stdin.read()
    data = json.loads(stdin_data) if stdin_data else {}
    command = data.get("tool_input", {}).get("command", "")
    print(f"FRONTMATTER_HOOK_FIRED: {command[:50]}", file=sys.stderr)
except Exception as e:
    print(f"FRONTMATTER_HOOK_ERROR: {e}", file=sys.stderr)

sys.exit(0)
