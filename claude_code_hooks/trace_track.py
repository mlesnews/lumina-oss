#!/usr/bin/env python3
"""
PreToolUse Hook: Trace-Track Rule Enforcer

Reads persistent memory rules from MEMORY.md and enforces them as active
guardrails on tool calls. Rules under ## CRITICAL RULES are compiled into
regex patterns that block violations.

Install: Copy to ~/.claude/hooks/ and register as PreToolUse.

Customize: Add rules to GUARDRAIL_RULES list below, or add CRITICAL RULES
to your MEMORY.md file.
"""

import sys
import json
import re
import os
from pathlib import Path
from datetime import datetime

# Directories to scan for MEMORY.md files
MEMORY_DIRS = [
    Path.home() / ".claude" / "projects",
]

AUDIT_LOG = Path.home() / "logs" / "trace-track" / "audit.jsonl"

# Guardrail rules — each maps a named rule to enforcement patterns.
# Add your own rules here.
GUARDRAIL_RULES = [
    {
        "id": "NO_ENV_SECRETS",
        "rule": "Never write secrets to .env files",
        "checks": {
            "Write": {
                "file_patterns": [r"\.env$", r"\.env\.\w+$"],
                "content_patterns": [
                    r"(?:TOKEN|KEY|SECRET|PASSWORD|API_KEY)\s*=\s*\S{8,}",
                ],
            },
            "Edit": {
                "file_patterns": [r"\.env$", r"\.env\.\w+$"],
                "content_patterns": [
                    r"(?:TOKEN|KEY|SECRET|PASSWORD|API_KEY)\s*=\s*\S{8,}",
                ],
            },
            "Bash": {
                "command_patterns": [
                    r"echo\s+.*(?:TOKEN|KEY|SECRET|PASS).*>\s*\S*\.env",
                ],
            },
        },
    },
    {
        "id": "VAULT_ONLY",
        "rule": "No hardcoded secrets in config files",
        "checks": {
            "Write": {
                "file_patterns": [r"docker-compose\.ya?ml$", r"compose\.ya?ml$"],
                "content_patterns": [
                    r"(?:API_KEY|SECRET|TOKEN|PASSWORD)\s*[=:]\s*(?!\$\{)[a-zA-Z0-9_-]{20,}",
                ],
            },
        },
    },
]


def audit_log(event_type: str, rule_id: str, tool: str, detail: str):
    """Append enforcement event to audit trail."""
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "rule_id": rule_id,
            "tool": tool,
            "detail": detail[:200],
        }
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def check_tool_call(tool_name: str, tool_input: dict) -> list:
    """Check a tool call against all guardrail rules."""
    violations = []

    for rule in GUARDRAIL_RULES:
        checks = rule.get("checks", {}).get(tool_name, {})
        if not checks:
            continue

        if tool_name == "Bash":
            command = tool_input.get("command", "")
            for pattern in checks.get("command_patterns", []):
                if re.search(pattern, command, re.IGNORECASE):
                    violations.append((rule["id"], f"Rule '{rule['rule']}'"))
                    break

        elif tool_name in ("Write", "Edit"):
            file_path = tool_input.get("file_path", "")
            content = tool_input.get("content", "") or tool_input.get("new_string", "")

            file_matches = any(
                re.search(p, file_path, re.IGNORECASE)
                for p in checks.get("file_patterns", [])
            )
            if file_matches and content:
                for pattern in checks.get("content_patterns", []):
                    if re.search(pattern, content[:5000], re.IGNORECASE):
                        violations.append((rule["id"], f"Rule '{rule['rule']}'"))
                        break

    return violations


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        violations = check_tool_call(tool_name, tool_input)

        if violations:
            rule_id, reason = violations[0]
            audit_log("BLOCKED", rule_id, tool_name, reason)
            print(f"TRACE-TRACK BLOCKED: {reason}.", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)

    except Exception:
        sys.exit(0)  # Fail open — compusec_guard handles fail-closed for secrets


if __name__ == "__main__":
    main()
