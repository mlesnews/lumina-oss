#!/usr/bin/env python3
"""
MARVIN & HK-47 Security Audit System
Aggressive internal and external security sweeps

@marvin: Internal Security Officer - Monitors codebase, configs, secrets
@hk-47: External Security Officer - Monitors digital presence, exposure

Author: <COMPANY_NAME> LLC
Date: 2025-01-28
Status: 🔴 CRITICAL SECURITY AUDIT
"""

import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SecurityAudit")


class SecurityLevel(Enum):
    """Security threat levels"""
    CRITICAL = "critical"  # Immediate action required
    HIGH = "high"  # Action required within 24 hours
    MEDIUM = "medium"  # Action required within 1 week
    LOW = "low"  # Monitor and review


@dataclass
class SecurityFinding:
    """Security finding from audit"""
    finding_id: str
    timestamp: datetime
    level: SecurityLevel
    category: str  # secret_exposure, key_vault, service_bus, config_security, etc.
    location: str
    description: str
    evidence: str
    recommendation: str
    fixed: bool = False
    fixed_date: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat(),
            "fixed_date": self.fixed_date.isoformat() if self.fixed_date else None,
            "level": self.level.value
        }


class MarvinInternalAuditor:
    """
    @marvin: Internal Security Officer
    Aggressively scans codebase, configs, and secrets
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.findings: List[SecurityFinding] = []

        # Aggressive patterns for secret detection
        self.secret_patterns = {
            'api_key': [
                r'api[_-]?key\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'API[_-]?KEY\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'sk-[a-zA-Z0-9]{20,}',
                r'AIza[0-9A-Za-z-_]{35}',
            ],
            'password': [
                r'password\s*[=:]\s*["\']([^"\']+)["\']',
                r'PASSWORD\s*[=:]\s*["\']([^"\']+)["\']',
                r'pwd\s*[=:]\s*["\']([^"\']+)["\']',
            ],
            'token': [
                r'token\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'TOKEN\s*[=:]\s*["\']([^"\']{20,})["\']',
                r'bearer\s+([a-zA-Z0-9\-_]{20,})',
                r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{32}',
            ],
            'connection_string': [
                r'connection[_-]?string\s*[=:]\s*["\']([^"\']+)["\']',
                r'CONNECTION[_-]?STRING\s*[=:]\s*["\']([^"\']+)["\']',
                r'(mongodb|postgresql|mysql|redis)://[^\s"\']+',
            ],
            'secret': [
                r'secret\s*[=:]\s*["\']([^"\']{10,})["\']',
                r'SECRET\s*[=:]\s*["\']([^"\']{10,})["\']',
            ],
        }

        # Files to scan aggressively
        self.scan_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.config', '.conf', '.txt', '.md'}

        # Directories to exclude
        self.exclude_dirs = {
            '.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env',
            'dist', 'build', '.pytest_cache', '.mypy_cache'
        }

        logger.info(f"🔴 MARVIN Internal Security Auditor initialized for: {self.project_root}")

    def audit_secrets_in_code(self) -> List[SecurityFinding]:
        """Aggressively scan for secrets in code"""
        findings = []
        scanned_files = 0

        logger.info("🔍 MARVIN: Scanning codebase for exposed secrets...")

        for file_path in self.project_root.rglob('*'):
            if not self._should_scan(file_path):
                continue

            scanned_files += 1
            file_findings = self._scan_file_for_secrets(file_path)
            findings.extend(file_findings)

        logger.warning(f"🔴 MARVIN: Scanned {scanned_files} files, found {len(findings)} potential secret exposures")
        return findings

    def audit_key_vault_usage(self) -> List[SecurityFinding]:
        """Verify Azure Key Vault is actually being used"""
        findings = []

        logger.info("🔍 MARVIN: Verifying Azure Key Vault implementation...")

        # Check if Key Vault client exists
        key_vault_file = self.project_root / "scripts" / "python" / "azure_service_bus_integration.py"
        if not key_vault_file.exists():
            findings.append(SecurityFinding(
                finding_id=f"kv-001-{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                level=SecurityLevel.CRITICAL,
                category="key_vault",
                location="azure_service_bus_integration.py",
                description="Azure Key Vault integration file not found",
                evidence="File does not exist",
                recommendation="Create Azure Key Vault integration module"
            ))
            return findings

        # Check for actual usage of Key Vault
        key_vault_usage = []
        secret_retrieval_patterns = [
            r'get_secret\s*\(',
            r'SecretClient\s*\(',
            r'AzureKeyVaultClient\s*\(',
            r'key_vault\.get',
            r'vault_client\.get',
        ]

        # Scan Python files for Key Vault usage
        for py_file in self.project_root.rglob('*.py'):
            if not self._should_scan(py_file):
                continue

            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Check if file has secrets but doesn't use Key Vault
                has_secrets = any(
                    re.search(pattern, content, re.IGNORECASE)
                    for patterns in self.secret_patterns.values()
                    for pattern in patterns
                )

                uses_key_vault = any(
                    re.search(pattern, content, re.IGNORECASE)
                    for pattern in secret_retrieval_patterns
                )

                if has_secrets and not uses_key_vault:
                    findings.append(SecurityFinding(
                        finding_id=f"kv-002-{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        level=SecurityLevel.CRITICAL,
                        category="key_vault",
                        location=str(py_file.relative_to(self.project_root)),
                        description="File contains secrets but does not use Azure Key Vault",
                        evidence=f"Found secret patterns but no Key Vault usage",
                        recommendation="Migrate secrets to Azure Key Vault and update code to retrieve from vault"
                    ))
            except Exception as e:
                logger.debug(f"Error scanning {py_file}: {e}")

        logger.warning(f"🔴 MARVIN: Found {len(findings)} Key Vault compliance issues")
        return findings

    def audit_service_bus_usage(self) -> List[SecurityFinding]:
        """Verify Azure Service Bus is actually being used"""
        findings = []

        logger.info("🔍 MARVIN: Verifying Azure Service Bus implementation...")

        # Check if Service Bus client exists
        service_bus_file = self.project_root / "scripts" / "python" / "azure_service_bus_integration.py"
        if not service_bus_file.exists():
            findings.append(SecurityFinding(
                finding_id=f"sb-001-{datetime.now().timestamp()}",
                timestamp=datetime.now(),
                level=SecurityLevel.CRITICAL,
                category="service_bus",
                location="azure_service_bus_integration.py",
                description="Azure Service Bus integration file not found",
                evidence="File does not exist",
                recommendation="Create Azure Service Bus integration module"
            ))
            return findings

        # Check for actual usage
        service_bus_patterns = [
            r'ServiceBusClient\s*\(',
            r'publish_to_topic\s*\(',
            r'subscribe_to_topic\s*\(',
            r'send_message\s*\(',
        ]

        # Find components that should use Service Bus but don't
        critical_components = [
            'jarvis', 'lumina', 'r5', 'droid', 'helpdesk', 'workflow'
        ]

        for py_file in self.project_root.rglob('*.py'):
            if not self._should_scan(py_file):
                continue

            file_name_lower = py_file.name.lower()
            if any(component in file_name_lower for component in critical_components):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')

                    # Check if it makes direct calls (should use Service Bus)
                    has_direct_calls = re.search(r'def\s+\w+\(.*\)\s*:', content)
                    uses_service_bus = any(
                        re.search(pattern, content, re.IGNORECASE)
                        for pattern in service_bus_patterns
                    )

                    if has_direct_calls and not uses_service_bus:
                        findings.append(SecurityFinding(
                            finding_id=f"sb-002-{datetime.now().timestamp()}",
                            timestamp=datetime.now(),
                            level=SecurityLevel.HIGH,
                            category="service_bus",
                            location=str(py_file.relative_to(self.project_root)),
                            description="Component should use Azure Service Bus for async communication",
                            evidence="Component makes direct calls instead of using Service Bus",
                            recommendation="Refactor to use Azure Service Bus for all async communication"
                        ))
                except Exception as e:
                    logger.debug(f"Error scanning {py_file}: {e}")

        logger.warning(f"🔴 MARVIN: Found {len(findings)} Service Bus compliance issues")
        return findings

    def audit_config_files(self) -> List[SecurityFinding]:
        """Audit config files for exposed secrets"""
        findings = []

        logger.info("🔍 MARVIN: Auditing configuration files...")

        config_files = [
            self.project_root / ".env",
            self.project_root / ".env.local",
            self.project_root / "config" / "llm_api_keys.json",
        ]

        for config_file in config_files:
            if not config_file.exists():
                continue

            try:
                content = config_file.read_text(encoding='utf-8', errors='ignore')

                for secret_type, patterns in self.secret_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            value = match.group(1) if match.groups() else match.group(0)

                            # Skip placeholders
                            if any(p in value.lower() for p in ['placeholder', 'example', 'your_', 'xxx']):
                                continue

                            findings.append(SecurityFinding(
                                finding_id=f"config-{secret_type}-{datetime.now().timestamp()}",
                                timestamp=datetime.now(),
                                level=SecurityLevel.CRITICAL,
                                category="config_security",
                                location=str(config_file.relative_to(self.project_root)),
                                description=f"Secret found in config file: {secret_type}",
                                evidence=f"Pattern matched: {pattern}",
                                recommendation="MOVE TO AZURE KEY VAULT IMMEDIATELY"
                            ))
            except Exception as e:
                logger.warning(f"Error reading {config_file}: {e}")

        logger.warning(f"🔴 MARVIN: Found {len(findings)} secrets in config files")
        return findings

    def _should_scan(self, file_path: Path) -> bool:
        try:
            """Check if file should be scanned"""
            if file_path.suffix not in self.scan_extensions:
                return False

            for part in file_path.parts:
                if part in self.exclude_dirs:
                    return False

            return file_path.exists() and file_path.is_file()

        except Exception as e:
            self.logger.error(f"Error in _should_scan: {e}", exc_info=True)
            raise
    def _scan_file_for_secrets(self, file_path: Path) -> List[SecurityFinding]:
        """Scan a single file for secrets"""
        findings = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Skip comments with examples
                if '# example' in line.lower() or '# TODO' in line.lower() or 'placeholder' in line.lower():  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                    continue

                for secret_type, patterns in self.secret_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            value = match.group(1) if match.groups() else match.group(0)

                            # Skip placeholders
                            if any(p in value.lower() for p in ['placeholder', 'example', 'your_', 'xxx', '***']):
                                continue

                            # Skip if too short
                            if len(value) < 8:
                                continue

                            findings.append(SecurityFinding(
                                finding_id=f"{secret_type}-{file_path.stem}-{line_num}-{datetime.now().timestamp()}",
                                timestamp=datetime.now(),
                                level=SecurityLevel.CRITICAL,
                                category="secret_exposure",
                                location=f"{file_path.relative_to(self.project_root)}:{line_num}",
                                description=f"Potential {secret_type} exposure in code",
                                evidence=line.strip()[:100],
                                recommendation="MOVE TO AZURE KEY VAULT IMMEDIATELY"
                            ))
        except Exception as e:
            logger.debug(f"Error scanning {file_path}: {e}")

        return findings

    def run_full_audit(self) -> List[SecurityFinding]:
        """Run complete internal security audit"""
        logger.info("=" * 80)
        logger.info("🔴 MARVIN INTERNAL SECURITY AUDIT - AGGRESSIVE SCAN")
        logger.info("=" * 80)

        all_findings = []

        # 1. Scan for secrets in code
        all_findings.extend(self.audit_secrets_in_code())

        # 2. Verify Key Vault usage
        all_findings.extend(self.audit_key_vault_usage())

        # 3. Verify Service Bus usage
        all_findings.extend(self.audit_service_bus_usage())

        # 4. Audit config files
        all_findings.extend(self.audit_config_files())

        self.findings = all_findings

        logger.warning(f"🔴 MARVIN AUDIT COMPLETE: {len(all_findings)} security findings")

        return all_findings


class HK47ExternalAuditor:
    """
    @hk-47: External Security Officer
    Monitors digital presence and external exposure
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.findings: List[SecurityFinding] = []

        logger.info(f"🔴 HK-47 External Security Auditor initialized")

    def audit_git_exposure(self) -> List[SecurityFinding]:
        """Check if secrets are exposed in git history"""
        findings = []

        logger.info("🔍 HK-47: Checking git history for exposed secrets...")

        # This would require git commands - placeholder for now
        # In production, would run: git log --all --full-history --source -- "*" | grep -i "api_key\|password\|secret"

        findings.append(SecurityFinding(
            finding_id=f"git-001-{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            level=SecurityLevel.HIGH,
            category="git_security",
            location=".git",
            description="Git history may contain exposed secrets",
            evidence="Manual review required",
            recommendation="Run: git log --all --full-history --source -- '*.*' | grep -iE 'api_key|password|secret|token'"
        ))

        return findings

    def audit_public_repos(self) -> List[SecurityFinding]:
        """Check if project is in public repositories"""
        findings = []

        logger.info("🔍 HK-47: Checking for public repository exposure...")

        # Check for .git directory
        git_dir = self.project_root / ".git"
        if git_dir.exists():
            # Check for remote URLs
            try:
                git_config = git_dir / "config"
                if git_config.exists():
                    content = git_config.read_text(encoding='utf-8', errors='ignore')
                    if 'github.com' in content or 'gitlab.com' in content:
                        findings.append(SecurityFinding(
                            finding_id=f"repo-001-{datetime.now().timestamp()}",
                            timestamp=datetime.now(),
                            level=SecurityLevel.HIGH,
                            category="repository_security",
                            location=".git/config",
                            description="Project may be in public repository",
                            evidence="Git remote found",
                            recommendation="Verify repository is private. Check for exposed secrets in commits."
                        ))
            except Exception as e:
                logger.debug(f"Error checking git config: {e}")

        return findings

    def run_full_audit(self) -> List[SecurityFinding]:
        """Run complete external security audit"""
        logger.info("=" * 80)
        logger.info("🔴 HK-47 EXTERNAL SECURITY AUDIT")
        logger.info("=" * 80)

        all_findings = []

        # 1. Check git exposure
        all_findings.extend(self.audit_git_exposure())

        # 2. Check public repos
        all_findings.extend(self.audit_public_repos())

        self.findings = all_findings

        logger.warning(f"🔴 HK-47 AUDIT COMPLETE: {len(all_findings)} external security findings")

        return all_findings


def generate_security_report(
    marvin_findings: List[SecurityFinding],
    hk47_findings: List[SecurityFinding],
    output_path: Path
) -> Dict:
    """Generate comprehensive security report"""

    all_findings = marvin_findings + hk47_findings

    # Group by level
    by_level = {}
    by_category = {}

    for finding in all_findings:
        level = finding.level.value
        if level not in by_level:
            by_level[level] = []
        by_level[level].append(finding.to_dict())

        category = finding.category
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(finding.to_dict())

    report = {
        "audit_date": datetime.now().isoformat(),
        "auditor": "@marvin (Internal) + @hk-47 (External)",
        "summary": {
            "total_findings": len(all_findings),
            "critical": len(by_level.get('critical', [])),
            "high": len(by_level.get('high', [])),
            "medium": len(by_level.get('medium', [])),
            "low": len(by_level.get('low', [])),
        },
        "by_level": {k: len(v) for k, v in by_level.items()},
        "by_category": {k: len(v) for k, v in by_category.items()},
        "marvin_findings": len(marvin_findings),
        "hk47_findings": len(hk47_findings),
        "findings": [f.to_dict() for f in all_findings],
        "critical_actions_required": [
            f.to_dict() for f in all_findings if f.level == SecurityLevel.CRITICAL
        ]
    }

    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.warning(f"🔴 Security report saved to: {output_path}")

    return report


def main():
    try:
        """Main execution - Run aggressive security audit"""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent

        print("=" * 80)
        print("🔴 MARVIN & HK-47 AGGRESSIVE SECURITY AUDIT")
        print("=" * 80)
        print(f"Project Root: {project_root}\n")

        # Run MARVIN internal audit
        marvin = MarvinInternalAuditor(project_root)
        marvin_findings = marvin.run_full_audit()

        # Run HK-47 external audit
        hk47 = HK47ExternalAuditor(project_root)
        hk47_findings = hk47.run_full_audit()

        # Generate report
        report_path = project_root / "data" / "security_audit_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report = generate_security_report(marvin_findings, hk47_findings, report_path)

        # Print summary
        print("\n" + "=" * 80)
        print("🔴 SECURITY AUDIT SUMMARY")
        print("=" * 80)
        print(f"Total Findings: {report['summary']['total_findings']}")
        print(f"  🔴 CRITICAL: {report['summary']['critical']}")
        print(f"  🟠 HIGH: {report['summary']['high']}")
        print(f"  🟡 MEDIUM: {report['summary']['medium']}")
        print(f"  🟢 LOW: {report['summary']['low']}")
        print(f"\n@marvin (Internal): {report['marvin_findings']} findings")
        print(f"@hk-47 (External): {report['hk47_findings']} findings")
        print(f"\nReport saved to: {report_path}")

        if report['summary']['critical'] > 0:
            print("\n" + "=" * 80)
            print("🔴 CRITICAL ACTIONS REQUIRED IMMEDIATELY")
            print("=" * 80)
            for finding in report['critical_actions_required']:
                print(f"\n🔴 {finding['category'].upper()}: {finding['description']}")
                print(f"   Location: {finding['location']}")
                print(f"   Recommendation: {finding['recommendation']}")

        print("\n" + "=" * 80)
        print("AUDIT COMPLETE")
        print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()