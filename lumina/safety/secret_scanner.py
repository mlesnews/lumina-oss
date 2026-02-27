"""
Regex-based secret detection.

Scans text for patterns that match API keys, tokens, passwords, private keys,
and other credential formats. Used by CI/CD, pre-commit hooks, and the
COMPUSEC guard hook to prevent secret leakage.

Pattern extracted from production: compusec_guard.py

Example:
    scanner = SecretScanner()
    findings = scanner.scan("export API_KEY=sk-ant-api03-abc123xyz")
    for f in findings:
        print(f"FOUND: {f['pattern_name']} at position {f['start']}")

    # Scan a file
    findings = scanner.scan_file(Path("config.yaml"))
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


# Secret patterns: (name, regex, description)
DEFAULT_PATTERNS = [
    ("aws_access_key", r"AKIA[A-Z0-9]{16}", "AWS Access Key ID"),
    ("anthropic_key", r"sk-ant-api\d{2}-[A-Za-z0-9_-]{20,}", "Anthropic API Key"),
    ("openai_key", r"sk-[A-Za-z0-9]{20,}", "OpenAI-style API Key"),
    ("github_pat", r"ghp_[A-Za-z0-9]{30,}", "GitHub Personal Access Token"),
    ("github_user_token", r"ghu_[A-Za-z0-9]{30,}", "GitHub User Token"),
    ("github_server_token", r"ghs_[A-Za-z0-9]{30,}", "GitHub Server Token"),
    ("slack_token", r"xoxb-[A-Za-z0-9-]+", "Slack Bot Token"),
    ("huggingface_token", r"hf_[a-zA-Z0-9]{34,}", "Hugging Face Token"),
    ("pinecone_key", r"pcsk_[a-zA-Z0-9_-]{40,}", "Pinecone API Key"),
    ("jwt_token", r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+", "JWT Token"),
    ("private_key", r"-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----", "Private Key"),
    ("bearer_token", r"Bearer\s+[A-Za-z0-9+/=_.-]{20,}", "Bearer Token"),
    ("generic_secret", r"(?:password|secret|token|api_key)\s*[:=]\s*['\"][A-Za-z0-9+/=_-]{20,}", "Generic Secret Assignment"),
]


class SecretScanner:
    """
    Scans text for secret/credential patterns.

    Args:
        patterns: List of (name, regex, description) tuples.
            Defaults to common API key and token patterns.
        extra_patterns: Additional patterns to append to defaults.
    """

    def __init__(
        self,
        patterns: Optional[List[tuple]] = None,
        extra_patterns: Optional[List[tuple]] = None,
    ):
        raw = patterns if patterns is not None else list(DEFAULT_PATTERNS)
        if extra_patterns:
            raw.extend(extra_patterns)
        self._patterns = [
            (name, re.compile(regex, re.IGNORECASE), desc)
            for name, regex, desc in raw
        ]

    def scan(self, text: str) -> List[Dict]:
        """
        Scan text for secret patterns.

        Args:
            text: The text to scan.

        Returns:
            List of finding dicts with keys:
            pattern_name, description, match, start, end.
        """
        findings = []
        for name, compiled, desc in self._patterns:
            for match in compiled.finditer(text):
                findings.append({
                    "pattern_name": name,
                    "description": desc,
                    "match": self._redact(match.group()),
                    "start": match.start(),
                    "end": match.end(),
                })
        return findings

    def scan_file(self, path: Path, max_bytes: int = 1_000_000) -> List[Dict]:
        """
        Scan a file for secret patterns.

        Args:
            path: File path to scan.
            max_bytes: Maximum bytes to read (default 1MB).

        Returns:
            List of findings (same format as scan()).
        """
        try:
            content = path.read_text(errors="replace")[:max_bytes]
            findings = self.scan(content)
            for f in findings:
                f["file"] = str(path)
            return findings
        except OSError:
            return []

    def has_secrets(self, text: str) -> bool:
        """Quick check: does the text contain any secret patterns?"""
        return len(self.scan(text)) > 0

    @staticmethod
    def _redact(value: str, visible: int = 6) -> str:
        """Redact a matched secret, showing only first N chars."""
        if len(value) <= visible:
            return "***"
        return value[:visible] + "***"
