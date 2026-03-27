#!/usr/bin/env bash
# PreToolUse Hook: Security pattern check before code writing
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)
echo "$INPUT" | python3 "$(dirname "$0")/pre_tool_security.py"
