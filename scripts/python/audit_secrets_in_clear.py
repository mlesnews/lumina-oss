#!/usr/bin/env python3
"""
Audit Secrets in the Clear

Scans the project for any API keys or secrets that might be exposed
in plaintext. Reports findings and recommends Azure Key Vault migration.

NO SECRETS IN THE CLEAR! 🔐

Tags: #SECURITY #AUDIT #AZURE_KEY_VAULT @JARVIS @TEAM
"""

import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AuditSecretsInClear")


@dataclass
class SecretFinding:
    """A potential secret found in the codebase"""
    file_path: str
    line_number: int
    pattern_matched: str
    snippet: str  # Masked snippet
    severity: str  # high, medium, low
    recommendation: str


# Patterns to detect potential secrets
SECRET_PATTERNS = [
    # API Keys
    (r'sk-[a-zA-Z0-9]{20,}', 'OpenAI API Key', 'high'),
    (r'sk-ant-[a-zA-Z0-9]{20,}', 'Anthropic API Key', 'high'),
    (r'AIza[a-zA-Z0-9_-]{35}', 'Google API Key', 'high'),
    (r'xai-[a-zA-Z0-9]{20,}', 'xAI API Key', 'high'),
    (r'waka_[a-zA-Z0-9-]{36}', 'WakaTime API Key', 'high'),
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token', 'high'),
    (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token', 'high'),
    (r'glpat-[a-zA-Z0-9_-]{20,}', 'GitLab Personal Access Token', 'high'),

    # Azure
    (r'[a-zA-Z0-9+/]{86}==', 'Azure Storage Key (possible)', 'medium'),

    # AWS
    (r'AKIA[A-Z0-9]{16}', 'AWS Access Key ID', 'high'),
    (r'[a-zA-Z0-9/+=]{40}', 'AWS Secret Key (possible)', 'low'),

    # Generic patterns
    (r'api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Generic API Key', 'medium'),
    (r'secret[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Secret Key', 'high'),
    (r'password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'Password', 'high'),
    (r'token["\']?\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}["\']', 'Token', 'medium'),

    # Private keys
    (r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', 'Private Key', 'high'),
    (r'-----BEGIN CERTIFICATE-----', 'Certificate', 'medium'),
]

# Files/directories to skip
SKIP_PATTERNS = [
    '*.encrypted',
    '*.log',
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    '*.pyc',
    '*.backup',
]

# Known safe patterns (false positives)
SAFE_PATTERNS = [
    r'\$\{[A-Z_]+\}',  # Environment variable references like ${API_KEY}
    r'%[A-Z_]+%',  # Windows env vars like %API_KEY%
    r'os\.environ',  # Python env access
    r'vault_url',  # Vault URLs
    r'secret_name',  # Secret name references (not actual secrets)
    r'api_key_secret',  # Secret name references
    r'fallback_env_var',  # Env var name references
    r'=\{\{\$json\.',  # n8n template expressions like ={{$json.password}}
    r'\{\{.*\}\}',  # n8n/Jinja2 template variables
    r'password.*\}\}',  # Template password references
]


class SecretsAuditor:
    """Audit codebase for secrets in the clear"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.findings: List[SecretFinding] = []

        logger.info("✅ Secrets Auditor initialized")

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        path_str = str(file_path)

        for pattern in SKIP_PATTERNS:
            if pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True

        return False

    def _is_safe_pattern(self, line: str) -> bool:
        """Check if the line contains a known safe pattern"""
        for pattern in SAFE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def _mask_secret(self, text: str, pattern: str) -> str:
        """Mask the secret in the text"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            secret = match.group()
            if len(secret) > 10:
                masked = secret[:6] + "..." + secret[-4:]
            else:
                masked = secret[:3] + "***"
            return text.replace(secret, masked)
        return text

    def scan_file(self, file_path: Path) -> List[SecretFinding]:
        """Scan a single file for secrets"""
        findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            logger.debug(f"Could not read {file_path}: {e}")
            return findings

        for line_num, line in enumerate(lines, 1):
            # Skip if it's a known safe pattern
            if self._is_safe_pattern(line):
                continue

            for pattern, name, severity in SECRET_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    # Mask the secret before storing
                    masked_line = self._mask_secret(line.strip(), pattern)

                    finding = SecretFinding(
                        file_path=str(file_path.relative_to(self.project_root)),
                        line_number=line_num,
                        pattern_matched=name,
                        snippet=masked_line[:100] + "..." if len(masked_line) > 100 else masked_line,
                        severity=severity,
                        recommendation=f"Move to Azure Key Vault (jarvis-lumina)"
                    )
                    findings.append(finding)

        return findings

    def audit_directory(self, directory: Optional[Path] = None) -> Dict[str, Any]:
        """Audit entire directory for secrets"""
        if directory is None:
            directory = self.project_root

        logger.info("="*80)
        logger.info("🔐 AUDITING FOR SECRETS IN THE CLEAR")
        logger.info("="*80)
        logger.info(f"📁 Scanning: {directory}")

        self.findings = []
        files_scanned = 0

        # Scan all files
        for file_path in directory.rglob('*'):
            if file_path.is_file() and not self._should_skip_file(file_path):
                files_scanned += 1
                file_findings = self.scan_file(file_path)
                self.findings.extend(file_findings)

        # Group by severity
        high_severity = [f for f in self.findings if f.severity == 'high']
        medium_severity = [f for f in self.findings if f.severity == 'medium']
        low_severity = [f for f in self.findings if f.severity == 'low']

        result = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "directory_scanned": str(directory),
            "files_scanned": files_scanned,
            "total_findings": len(self.findings),
            "high_severity": len(high_severity),
            "medium_severity": len(medium_severity),
            "low_severity": len(low_severity),
            "findings": [
                {
                    "file": f.file_path,
                    "line": f.line_number,
                    "type": f.pattern_matched,
                    "severity": f.severity,
                    "snippet": f.snippet,
                    "recommendation": f.recommendation
                }
                for f in self.findings
            ],
            "recommendation": "All secrets should be stored in Azure Key Vault (jarvis-lumina.vault.azure.net)"
        }

        logger.info(f"📊 Files scanned: {files_scanned}")
        logger.info(f"🔍 Findings: {len(self.findings)}")
        logger.info(f"   🔴 High: {len(high_severity)}")
        logger.info(f"   🟡 Medium: {len(medium_severity)}")
        logger.info(f"   🟢 Low: {len(low_severity)}")
        logger.info("="*80)

        return result

    def print_report(self, result: Dict[str, Any]):
        """Print formatted report"""
        print("\n" + "="*80)
        print("🔐 SECRETS AUDIT REPORT")
        print("="*80)
        print(f"\nDirectory: {result['directory_scanned']}")
        print(f"Files Scanned: {result['files_scanned']}")
        print(f"Total Findings: {result['total_findings']}")
        print(f"  🔴 High Severity: {result['high_severity']}")
        print(f"  🟡 Medium Severity: {result['medium_severity']}")
        print(f"  🟢 Low Severity: {result['low_severity']}")

        if result['findings']:
            print("\n" + "-"*80)
            print("FINDINGS:")
            print("-"*80)

            for f in result['findings']:
                severity_icon = "🔴" if f['severity'] == 'high' else ("🟡" if f['severity'] == 'medium' else "🟢")
                print(f"\n{severity_icon} {f['type']} ({f['severity'].upper()})")
                print(f"   File: {f['file']}:{f['line']}")
                print(f"   Snippet: {f['snippet']}")
                print(f"   Action: {f['recommendation']}")
        else:
            print("\n✅ NO SECRETS IN THE CLEAR FOUND!")

        print("\n" + "="*80)
        print("RECOMMENDATIONS:")
        print("="*80)
        print("""
1. Store ALL API keys in Azure Key Vault
   - Vault: https://jarvis-lumina.vault.azure.net/

2. Use environment variables populated from vault
   - Run set_wakatime_env.py at startup
   - Never hardcode secrets

3. Use ${VAR_NAME} or %VAR_NAME% placeholders in config files

4. Files ending in .encrypted are already secure

5. Run this audit regularly:
   python scripts/python/audit_secrets_in_clear.py
""")
        print("="*80)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Audit for Secrets in the Clear")
        parser.add_argument('--directory', type=Path, help='Directory to audit')
        parser.add_argument('--json', action='store_true', help='Output as JSON')
        parser.add_argument('--config-only', action='store_true', help='Only scan config directory')

        args = parser.parse_args()

        auditor = SecretsAuditor()

        if args.config_only:
            directory = auditor.project_root / "config"
        else:
            directory = args.directory

        result = auditor.audit_directory(directory)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            auditor.print_report(result)

        # Return exit code based on high severity findings
        return 1 if result['high_severity'] > 0 else 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())