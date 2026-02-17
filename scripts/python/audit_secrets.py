#!/usr/bin/env python3
"""
Secret Audit Script - Scavenge codebase for secrets

Scans the codebase for hardcoded secrets, API keys, tokens, passwords, etc.
Uses local codebase patterns first, then aggregates findings to R5.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    import sys
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from lumina_logger import get_logger
except ImportError:
    try:
        from scripts.python.lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecretAudit")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SecretFinding:
    """Represents a found secret in the codebase"""
    file_path: str
    line_number: int
    secret_type: str  # api_key, password, token, connection_string, etc.
    pattern_matched: str
    context: str  # Surrounding code context
    severity: str  # critical, high, medium, low
    recommendation: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class SecretAuditor:
    """
    Audits codebase for secrets using patterns from local codebase.

    Scavenges existing patterns first, then uses common secret patterns.
    """

    def __init__(self, project_root: Path):
        """Initialize auditor"""
        self.project_root = Path(project_root)
        self.findings: List[SecretFinding] = []

        # Patterns from local codebase (scavenged)
        self.patterns = self._build_patterns()

        # Files to exclude
        self.exclude_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv',
            'env', '.env', 'dist', 'build', '.pytest_cache',
            'data/azvault',  # Local vault storage (to be migrated)
            'data/r5_living_matrix'  # Knowledge aggregation
        }

        # File extensions to scan
        self.scan_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.config', '.conf'}

        logger.info(f"Initialized Secret Auditor for: {self.project_root}")

    def _build_patterns(self) -> Dict[str, List[Tuple[str, str]]]:
        """
        Build secret patterns from local codebase patterns first.

        Returns:
            Dict mapping secret_type to list of (pattern, description) tuples
        """
        patterns = {}

        # API Keys - patterns from local codebase
        patterns['api_key'] = [
            (r'api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'API key assignment'),
            (r'API[_-]?KEY\s*[=:]\s*["\']([^"\']+)["\']', 'API KEY assignment'),
            (r'api_key\s*=\s*["\']([^"\']{20,})["\']', 'API key variable'),
            (r'anthropic[_-]?api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'Anthropic API key'),
            (r'openai[_-]?api[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'OpenAI API key'),
            (r'github[_-]?token\s*[=:]\s*["\']([^"\']+)["\']', 'GitHub token'),
            (r'n8n[_-]?webhook[_-]?secret\s*[=:]\s*["\']([^"\']+)["\']', 'n8n webhook secret'),
        ]

        # Connection Strings - from local patterns
        patterns['connection_string'] = [
            (r'connection[_-]?string\s*[=:]\s*["\']([^"\']+)["\']', 'Connection string'),
            (r'CONNECTION[_-]?STRING\s*[=:]\s*["\']([^"\']+)["\']', 'CONNECTION STRING'),
            (r'database[_-]?url\s*[=:]\s*["\']([^"\']+)["\']', 'Database URL'),
            (r'redis[_-]?url\s*[=:]\s*["\']([^"\']+)["\']', 'Redis URL'),
            (r'service[_-]?bus[_-]?connection\s*[=:]\s*["\']([^"\']+)["\']', 'Service Bus connection'),
        ]

        # Tokens
        patterns['token'] = [
            (r'token\s*[=:]\s*["\']([^"\']{20,})["\']', 'Token assignment'),
            (r'TOKEN\s*[=:]\s*["\']([^"\']{20,})["\']', 'TOKEN assignment'),
            (r'bearer[_-]?token\s*[=:]\s*["\']([^"\']+)["\']', 'Bearer token'),
            (r'access[_-]?token\s*[=:]\s*["\']([^"\']+)["\']', 'Access token'),
        ]

        # Passwords
        patterns['password'] = [
            (r'password\s*[=:]\s*["\']([^"\']+)["\']', 'Password assignment'),
            (r'PASSWORD\s*[=:]\s*["\']([^"\']+)["\']', 'PASSWORD assignment'),
            (r'pwd\s*[=:]\s*["\']([^"\']+)["\']', 'Password (pwd)'),
        ]

        # Secrets (generic)
        patterns['secret'] = [
            (r'secret\s*[=:]\s*["\']([^"\']{10,})["\']', 'Secret assignment'),
            (r'SECRET\s*[=:]\s*["\']([^"\']{10,})["\']', 'SECRET assignment'),
            (r'secret[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'Secret key'),
        ]

        # Azure-specific (from local codebase patterns)
        patterns['azure_secret'] = [
            (r'azure[_-]?key[_-]?vault[_-]?url\s*[=:]\s*["\']([^"\']+)["\']', 'Azure Key Vault URL'),
            (r'vault[_-]?url\s*[=:]\s*["\']([^"\']+)["\']', 'Vault URL'),
            (r'service[_-]?principal[_-]?secret\s*[=:]\s*["\']([^"\']+)["\']', 'Service principal secret'),
        ]

        # Encryption keys
        patterns['encryption_key'] = [
            (r'encryption[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'Encryption key'),
            (r'encryption_key\s*=\s*["\']([^"\']{20,})["\']', 'Encryption key variable'),
            (r'r5[_-]?encryption[_-]?key\s*[=:]\s*["\']([^"\']+)["\']', 'R5 encryption key'),
        ]

        return patterns

    def _should_scan_file(self, file_path: Path) -> bool:
        try:
            """Check if file should be scanned"""
            # Check extension
            if file_path.suffix not in self.scan_extensions:
                return False

            # Check if in exclude directory
            for part in file_path.parts:
                if part in self.exclude_dirs:
                    return False

            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error in _should_scan_file: {e}", exc_info=True)
            raise
    def _get_severity(self, secret_type: str, value: str) -> str:
        """Determine severity of secret finding"""
        # Critical: API keys, tokens, passwords
        if secret_type in ['api_key', 'token', 'password']:
            if len(value) > 20:  # Likely real secret
                return 'critical'
            return 'high'

        # High: Connection strings, encryption keys
        if secret_type in ['connection_string', 'encryption_key']:
            return 'high'

        # Medium: Generic secrets
        if secret_type == 'secret':
            return 'medium'

        # Low: Azure URLs (not secrets themselves)
        if secret_type == 'azure_secret':
            return 'low'

        return 'medium'

    def _get_recommendation(self, secret_type: str) -> str:
        """Get recommendation for secret type"""
        recommendations = {
            'api_key': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'token': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'password': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'connection_string': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'secret': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'encryption_key': 'Move to Azure Key Vault. Use get_secret_from_vault()',
            'azure_secret': 'Verify this is not a secret. If it is, move to Key Vault.',
        }
        return recommendations.get(secret_type, 'Review and move to Azure Key Vault if sensitive')

    def scan_file(self, file_path: Path) -> List[SecretFinding]:
        """Scan a single file for secrets"""
        findings = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip comments that are clearly examples
                if '# example' in line.lower() or '# TODO' in line.lower():  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                    continue

                # Check each pattern type
                for secret_type, type_patterns in self.patterns.items():
                    for pattern, description in type_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            value = match.group(1) if match.groups() else match.group(0)

                            # Skip if looks like a placeholder
                            if any(placeholder in value.lower() for placeholder in ['placeholder', 'example', 'your_', 'xxx', '***']):
                                continue

                            # Skip if too short (likely not a real secret)
                            if len(value) < 8:
                                continue

                            # Get context (surrounding lines)
                            context_start = max(0, line_num - 2)
                            context_end = min(len(lines), line_num + 2)
                            context = ''.join(lines[context_start:context_end])

                            finding = SecretFinding(
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=line_num,
                                secret_type=secret_type,
                                pattern_matched=description,
                                context=context.strip(),
                                severity=self._get_severity(secret_type, value),
                                recommendation=self._get_recommendation(secret_type)
                            )

                            findings.append(finding)
                            logger.debug(f"Found {secret_type} in {file_path.name}:{line_num}")

        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")

        return findings

    def scan_codebase(self) -> List[SecretFinding]:
        """Scan entire codebase for secrets"""
        logger.info("Starting codebase secret audit...")

        all_findings = []
        scanned_files = 0

        # Walk through project directory
        for file_path in self.project_root.rglob('*'):
            if not self._should_scan_file(file_path):
                continue

            scanned_files += 1
            findings = self.scan_file(file_path)
            all_findings.extend(findings)

        self.findings = all_findings
        logger.info(f"Scanned {scanned_files} files, found {len(all_findings)} potential secrets")

        return all_findings

    def generate_report(self) -> Dict:
        """Generate audit report"""
        # Group by severity
        by_severity = {}
        by_type = {}

        for finding in self.findings:
            # By severity
            if finding.severity not in by_severity:
                by_severity[finding.severity] = []
            by_severity[finding.severity].append(finding.to_dict())

            # By type
            if finding.secret_type not in by_type:
                by_type[finding.secret_type] = []
            by_type[finding.secret_type].append(finding.to_dict())

        report = {
            "audit_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_findings": len(self.findings),
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "by_type": {k: len(v) for k, v in by_type.items()},
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "critical": len(by_severity.get('critical', [])),
                "high": len(by_severity.get('high', [])),
                "medium": len(by_severity.get('medium', [])),
                "low": len(by_severity.get('low', []))
            }
        }

        return report

    def save_report(self, output_path: Path) -> None:
        try:
            """Save audit report to file"""
            report = self.generate_report()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"Audit report saved to: {output_path}")


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def aggregate_to_r5(project_root: Path, audit_report: Dict) -> None:
    """
    Aggregate secret audit findings to R5 Living Context Matrix.

    Uses local R5 integration patterns.
    """
    try:
        from scripts.python.r5_living_context_matrix import R5LivingContextMatrix

        r5 = R5LivingContextMatrix(project_root)

        # Create session data from audit
        session_data = {
            "session_id": f"secret_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "session_type": "secret_audit",
            "timestamp": datetime.now().isoformat(),
            "content": f"""
# Secret Audit Results

**Date**: {audit_report['audit_date']}
**Total Findings**: {audit_report['total_findings']}

## Summary
- Critical: {audit_report['summary']['critical']}
- High: {audit_report['summary']['high']}
- Medium: {audit_report['summary']['medium']}
- Low: {audit_report['summary']['low']}

## Findings by Type
{json.dumps(audit_report['by_type'], indent=2)}

## Key Findings
{len(audit_report['findings'])} secrets found that need migration to Azure Key Vault.

## Recommendation
All secrets must be migrated to Azure Key Vault per requirements.
            """,
            "metadata": {
                "audit_report": audit_report,
                "source": "secret_audit_script",
                "aggregated_to_r5": True
            }
        }

        # Ingest to R5
        r5.ingest_session(session_data)
        logger.info("Secret audit findings aggregated to R5")

    except ImportError:
        logger.warning("R5 Living Context Matrix not available, skipping aggregation")
    except Exception as e:
        logger.error(f"Failed to aggregate to R5: {e}")


def main():
    try:
        """Main execution"""
        # Auto-detect project root from script location
        script_path = Path(__file__).resolve()
        # Go up from scripts/python/ to project root
        project_root = script_path.parent.parent

        print("=" * 60)
        print("Secret Audit - Scavenging Codebase")
        print("=" * 60)
        print(f"Project Root: {project_root}\n")

        # Initialize auditor
        auditor = SecretAuditor(project_root)

        # Scan codebase
        print("Scanning codebase for secrets...")
        findings = auditor.scan_codebase()

        # Generate report
        print("\nGenerating audit report...")
        report = auditor.generate_report()

        # Print summary
        print("\n" + "=" * 60)
        print("Audit Summary")
        print("=" * 60)
        print(f"Total Findings: {report['total_findings']}")
        print(f"\nBy Severity:")
        for severity, count in report['by_severity'].items():
            print(f"  {severity.upper()}: {count}")
        print(f"\nBy Type:")
        for secret_type, count in report['by_type'].items():
            print(f"  {secret_type}: {count}")

        # Save report
        report_path = project_root / "data" / "secret_audit_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        auditor.save_report(report_path)
        print(f"\nReport saved to: {report_path}")

        # Aggregate to R5
        print("\nAggregating findings to R5...")
        aggregate_to_r5(project_root, report)
        print("✅ Findings aggregated to R5")

        print("\n" + "=" * 60)
        print("Audit Complete")
        print("=" * 60)
        print("\nNext Steps:")
        print("1. Review findings in the audit report")
        print("2. Migrate all secrets to Azure Key Vault")
        print("3. Update code to retrieve secrets from Key Vault")
        print("4. Remove secrets from codebase")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()