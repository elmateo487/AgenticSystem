---
name: hook-test
description: "Test if frontmatter hooks fire with correct stdin/stderr format"
version: 2.0.0
context: fork
allowed-tools: Bash, Read
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "python3 /Users/minimatt/.claude/skills/hook-test/hook-script.py"
---

# Hook Test Skill (v2)

Testing frontmatter hooks with correct stdin JSON / stderr output format.

Run a bash command and check if you see "FRONTMATTER_HOOK_FIRED" in the output.
