#!/usr/bin/env python3
"""
PostToolUse Hook: Secrets Redactor

Scans tool output for leaked secrets (API keys, tokens, private keys, JWTs)
and warns Claude Code to avoid repeating them. Last line of defense after
PreToolUse guards.

Maintains an audit trail of all secret-adjacent operations.

Install: Register as PostToolUse for Bash, Read, Grep, WebFetch, WebSearch.
Output: ~/logs/security/secrets_audit.jsonl
"""

import json
import re
import sys
import time
from pathlib import Path

AUDIT_DIR = Path.home() / "logs" / "security"
AUDIT_LOG = AUDIT_DIR / "secrets_audit.jsonl"

# -- Patterns that indicate a leaked secret in output --
SECRET_PATTERNS = [
    # GitHub tokens
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub PAT'),
    (r'gho_[A-Za-z0-9]{36}', 'GitHub OAuth'),
    (r'ghs_[A-Za-z0-9]{36}', 'GitHub Server Token'),

    # AI provider keys
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI API Key'),
    (r'sk-ant-api\d{2}-[A-Za-z0-9_-]{80,}', 'Anthropic API Key'),
    (r'hf_[a-zA-Z0-9]{34,}', 'HuggingFace Token'),

    # Slack tokens
    (r'xoxb-[A-Za-z0-9-]{50,}', 'Slack Bot Token'),
    (r'xoxp-[A-Za-z0-9-]{50,}', 'Slack User Token'),

    # Cloud provider keys
    (r'AKIA[A-Z0-9]{16}', 'AWS Access Key'),
    (r'pcsk_[a-zA-Z0-9_-]{40,}', 'Pinecone Key'),

    # Auth tokens
    (r'eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]+', 'JWT Token'),
    (r'Bearer\s+[A-Za-z0-9+/=_.-]{30,}', 'Bearer Token'),

    # Private keys
    (r'-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+|DSA\s+)?PRIVATE\s+KEY-----', 'Private Key'),

    # Connection strings with embedded passwords
    (r'(?:mysql|postgres|mongodb|redis)://\w+:[^@\s]{6,}@', 'DB Connection String'),

    # Structured data with secrets
    (r'"password"\s*:\s*"[^"]{6,}"', 'Password in JSON'),
    (r'"secret"\s*:\s*"[^"]{6,}"', 'Secret in JSON'),
    (r'"token"\s*:\s*"[A-Za-z0-9+/=_-]{20,}"', 'Token in JSON'),
    (r'"api_key"\s*:\s*"[^"]{10,}"', 'API Key in JSON'),
]

# -- Known false positives --
FALSE_POSITIVE_PATTERNS = [
    r'sha256:[a-f0-9]{64}',            # Docker/OCI image digests
    r'SHA256:[A-Za-z0-9+/]{43}=',      # SSH host key fingerprints
    r'commit\s+[a-f0-9]{40}',          # Git commit hashes
    r'ssh-(ed25519|rsa)\s+AAAA',       # SSH public keys (not private)
    r'-----BEGIN\s+CERTIFICATE-----',   # Public certs (not private keys)
]


def audit_log(event_type: str, details: dict):
    """Append to forensic audit trail."""
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "iso": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "event": event_type,
            "details": details,
        }
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def scan_output(output_text: str) -> list[tuple[str, str]]:
    """Scan for leaked secrets. Returns list of (pattern_name, preview)."""
    findings = []
    seen_types: set[str] = set()
    for pattern, name in SECRET_PATTERNS:
        if name in seen_types:
            continue
        for m in re.finditer(pattern, output_text, re.IGNORECASE):
            # Check false positives in surrounding context
            ctx_start = max(0, m.start() - 100)
            ctx_end = min(len(output_text), m.end() + 100)
            context = output_text[ctx_start:ctx_end]
            if any(re.search(fp, context, re.IGNORECASE) for fp in FALSE_POSITIVE_PATTERNS):
                continue
            preview = m.group(0)[:8] + "..." if len(m.group(0)) > 8 else m.group(0)
            findings.append((name, preview))
            seen_types.add(name)
            break
    return findings


def main():
    try:
        hook_data = json.loads(sys.stdin.read())
        tool_name = hook_data.get("tool_name", "")
        tool_output = hook_data.get("tool_output", "")

        output_str = str(tool_output) if tool_output else ""
        if not output_str:
            sys.exit(0)

        findings = scan_output(output_str)
        if findings:
            audit_log("SECRET_LEAK_DETECTED", {
                "tool": tool_name,
                "findings": [(name, preview) for name, preview in findings[:5]],
                "severity": "CRITICAL",
            })
            names = ", ".join(set(name for name, _ in findings))
            print(
                f"WARNING: Secret detected in output! Types: {names}. "
                f"DO NOT repeat this output. Logged to audit trail.",
                file=sys.stderr,
            )

    except Exception as e:
        audit_log("hook_error", {"error": str(e)})

    sys.exit(0)


if __name__ == "__main__":
    main()
