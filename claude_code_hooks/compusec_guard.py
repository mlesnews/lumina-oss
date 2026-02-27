#!/usr/bin/env python3
"""
PreToolUse Hook: COMPUSEC Guard — Secret Leak Prevention

Blocks commands that would expose secrets in CLI arguments, process listings,
or tool output. Checks Bash commands, Write operations, and Edit operations.

Install: Copy to ~/.claude/hooks/ and register in settings.json as PreToolUse.

Exit codes:
    0 = approve (no secrets detected)
    2 = block (secret exposure detected)
"""

import sys
import json
import re

# Patterns that indicate secrets being exposed in CLI args
DANGEROUS_PATTERNS = [
    # Direct password/token in command line args
    r'--passwd[= ]\S+',
    r'--password[= ]\S+',
    r'api[_-]?key[= ]\S+',
    r'token[= ][A-Za-z0-9+/=_-]{20,}',
    r"token[= ]['\"][A-Za-z0-9+/=_-]{10,}",

    # Piping vault secrets to display commands
    r'az keyvault secret show.*\|\s*(echo|cat|printf|od|xxd|hexdump)',
    r'az keyvault secret show.*--query\s+value.*-o\s+tsv(?!.*\|)',

    # Direct echo of secret variables
    r'echo\s+["\']?\$\w*(PASS|SECRET|TOKEN|KEY|CRED)\w*',

    # Clipboard reads without safe pipe target
    r'Get-Clipboard(?!.*\|\s*(az\s+keyvault|Out-Null|Set-Content|wc\b))',
    r'xclip\s+-o(?!.*\|\s*az)',
    r'pbpaste(?!.*\|\s*az)',

    # Temp file secret storage
    r'>\s*/tmp/\.(secret|api_key|token|password|cred)',
]

# Commands that safely handle secrets (allowlist)
SAFE_PATTERNS = [
    r'az keyvault secret show.*\|\s*python3?\s+-c.*print.*len',
    r'az keyvault secret show.*\|\s*wc\s+-c',
    r'\$\(az keyvault.*\)',
    r'Get-Clipboard.*\|\s*az\s+keyvault\s+secret\s+set',
]

# Content patterns that indicate actual secrets
SECRET_CONTENT_PATTERNS = [
    r'-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----',
    r'AKIA[A-Z0-9]{16}',
    r'sk-ant-api\d{2}-',
    r'sk-[A-Za-z0-9]{20,}',
    r'ghp_[A-Za-z0-9]{30,}',
    r'ghu_[A-Za-z0-9]{30,}',
    r'ghs_[A-Za-z0-9]{30,}',
    r'xoxb-[A-Za-z0-9-]+',
    r'hf_[a-zA-Z0-9]{34,}',
    r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+',
]


def strip_heredoc_content(command):
    """Remove heredoc body so patterns inside string literals don't false-positive."""
    return re.sub(
        r"<<\s*['\"]?(\w+)['\"]?\s*\n.*?\n\1\b",
        "<HEREDOC_REDACTED>",
        command,
        flags=re.DOTALL,
    )


def check_command(command):
    """Check if a bash command would expose secrets."""
    sanitized = strip_heredoc_content(command)
    violations = []
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, sanitized, re.IGNORECASE):
            is_safe = any(re.search(s, sanitized, re.IGNORECASE) for s in SAFE_PATTERNS)
            if not is_safe:
                violations.append(pattern)
    return violations


def check_write(file_path, content=""):
    """Check if a write would persist secrets to disk."""
    violations = []
    for pattern in SECRET_CONTENT_PATTERNS:
        if re.search(pattern, content[:5000]):
            violations.append(f"secret content: {pattern}")
    return violations


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
        tool_name = hook_data.get("tool_name", "")
        tool_input = hook_data.get("tool_input", {})

        if tool_name == "Bash":
            command = tool_input.get("command", "")
            violations = check_command(command)
            if violations:
                reason = f"COMPUSEC BLOCKED: Command would expose secrets. Use stdin pipes to vault instead."
                print(reason, file=sys.stderr)
                sys.exit(2)

        elif tool_name in ("Write", "Edit"):
            content = tool_input.get("content", "") or tool_input.get("new_string", "")
            violations = check_write(tool_input.get("file_path", ""), content)
            if violations:
                print("COMPUSEC BLOCKED: Content contains secrets.", file=sys.stderr)
                sys.exit(2)

        sys.exit(0)

    except Exception as e:
        print(f"COMPUSEC HOOK ERROR: {e}. Blocking out of caution.", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
