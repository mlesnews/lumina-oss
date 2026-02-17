#!/usr/bin/env python3
"""
Cluster Configuration Validation Tool

Validates configuration consistency across all configuration files using the
cluster_endpoint_registry.json as the single source of truth.

Tags: #VALIDATION #CONFIGURATION #CLUSTER #SSOT @JARVIS @LUMINA
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("validate_cluster_config")


@dataclass
class ValidationIssue:
    """Represents a configuration validation issue"""

    severity: str  # "error", "warning", "info"
    category: str  # "endpoint", "format", "consistency", "health"
    file_path: str
    issue: str
    expected: Optional[str] = None
    actual: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Results of configuration validation"""

    valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    endpoints_checked: int = 0
    endpoints_healthy: int = 0
    endpoints_unhealthy: int = 0
    endpoints_unknown: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ClusterConfigValidator:
    """Validates cluster configuration consistency"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / "config" / "cluster_endpoint_registry.json"
        self.registry: Dict[str, Any] = {}
        self.issues: List[ValidationIssue] = []

    def load_registry(self) -> bool:
        """Load the endpoint registry (SSOT)"""
        try:
            if not self.registry_path.exists():
                self.issues.append(
                    ValidationIssue(
                        severity="error",
                        category="endpoint",
                        file_path=str(self.registry_path),
                        issue="Endpoint registry not found",
                        fix_suggestion="Create config/cluster_endpoint_registry.json",
                    )
                )
                return False

            with open(self.registry_path, encoding="utf-8") as f:
                self.registry = json.load(f)
            return True
        except Exception as e:
            self.issues.append(
                ValidationIssue(
                    severity="error",
                    category="format",
                    file_path=str(self.registry_path),
                    issue=f"Failed to load registry: {e}",
                    fix_suggestion="Check JSON syntax and file permissions",
                )
            )
            return False

    def validate_url_format(self, url: str) -> bool:
        """Validate URL format"""
        pattern = r"^https?://[\w\.-]+(:\d+)?(/.*)?$"
        return bool(re.match(pattern, url))

    def check_endpoint_health(
        self, endpoint_id: str, endpoint: Dict[str, Any]
    ) -> Tuple[str, Optional[str]]:
        """Check endpoint health status"""
        health_check = endpoint.get("health_check")
        if not health_check:
            return "unknown", "No health check URL defined"

        try:
            response = requests.get(health_check, timeout=5)
            if response.status_code == 200:
                return "operational", None
            else:
                return "degraded", f"HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "offline", "Connection timeout"
        except requests.exceptions.ConnectionError:
            return "offline", "Connection refused"
        except Exception as e:
            return "unknown", str(e)

    def validate_endpoint_registry(self) -> List[ValidationIssue]:
        """Validate endpoint registry structure"""
        issues = []

        if "endpoints" not in self.registry:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="format",
                    file_path=str(self.registry_path),
                    issue="Missing 'endpoints' section in registry",
                )
            )
            return issues

        required_fields = ["id", "name", "type", "url", "health_check"]

        for endpoint_id, endpoint in self.registry["endpoints"].items():
            # Check required fields
            for field in required_fields:
                if field not in endpoint:
                    issues.append(
                        ValidationIssue(
                            severity="error",
                            category="format",
                            file_path=str(self.registry_path),
                            issue=f"Endpoint '{endpoint_id}' missing required field: {field}",
                            expected=field,
                            fix_suggestion=f"Add '{field}' field to endpoint configuration",
                        )
                    )

            # Validate URL format
            url = endpoint.get("url", "")
            if url and not self.validate_url_format(url):
                issues.append(
                    ValidationIssue(
                        severity="error",
                        category="format",
                        file_path=str(self.registry_path),
                        issue=f"Endpoint '{endpoint_id}' has invalid URL format: {url}",
                        actual=url,
                        fix_suggestion="Use format: http://hostname:port or https://hostname:port",
                    )
                )

            # Validate status value
            status = endpoint.get("status", "unknown")
            valid_statuses = ["operational", "degraded", "offline", "unknown", "maintenance"]
            if status not in valid_statuses:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="format",
                        file_path=str(self.registry_path),
                        issue=f"Endpoint '{endpoint_id}' has invalid status: {status}",
                        actual=status,
                        expected=", ".join(valid_statuses),
                        fix_suggestion=f"Set status to one of: {', '.join(valid_statuses)}",
                    )
                )

        return issues

    def validate_cursor_settings(self) -> List[ValidationIssue]:
        """Validate Cursor IDE settings against registry"""
        issues = []

        # Find Cursor settings file
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    category="consistency",
                    file_path="Cursor settings",
                    issue="APPDATA environment variable not set, cannot validate Cursor settings",
                )
            )
            return issues

        cursor_settings_path = Path(appdata) / "Cursor" / "User" / "settings.json"
        if not cursor_settings_path.exists():
            issues.append(
                ValidationIssue(
                    severity="info",
                    category="consistency",
                    file_path=str(cursor_settings_path),
                    issue="Cursor settings file not found (may not be installed)",
                )
            )
            return issues

        try:
            with open(cursor_settings_path, encoding="utf-8") as f:
                cursor_settings = json.load(f)
        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="format",
                    file_path=str(cursor_settings_path),
                    issue=f"Failed to load Cursor settings: {e}",
                )
            )
            return issues

        # Check custom models sections
        sections = [
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.agent.customModels",
        ]

        registry_endpoints = self.registry.get("endpoints", {})

        for section_key in sections:
            models = cursor_settings.get(section_key, [])
            for model in models:
                api_base = model.get("apiBase", "")
                name = model.get("name", "")

                # Check if endpoint matches registry
                found_match = False
                for endpoint_id, endpoint in registry_endpoints.items():
                    endpoint_url = endpoint.get("url", "")
                    if api_base.startswith(endpoint_url) or endpoint_url in api_base:
                        found_match = True
                        break

                if api_base and not found_match:
                    issues.append(
                        ValidationIssue(
                            severity="warning",
                            category="consistency",
                            file_path=str(cursor_settings_path),
                            issue=f"Model '{name}' in {section_key} uses endpoint '{api_base}' not found in registry",
                            actual=api_base,
                            fix_suggestion="Update endpoint to match registry or add to registry",
                        )
                    )

                # Check required flags for local models
                if api_base and ("localhost" in api_base or "127.0.0.1" in api_base):
                    local_only = model.get("localOnly", False)
                    skip_provider = model.get("skipProviderSelection", False)

                    if not local_only:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                category="consistency",
                                file_path=str(cursor_settings_path),
                                issue=f"Model '{name}' uses localhost endpoint but 'localOnly' is not set",
                                fix_suggestion="Set 'localOnly': true for local endpoints",
                            )
                        )

                    if not skip_provider:
                        issues.append(
                            ValidationIssue(
                                severity="warning",
                                category="consistency",
                                file_path=str(cursor_settings_path),
                                issue=f"Model '{name}' uses localhost endpoint but 'skipProviderSelection' is not set",
                                fix_suggestion="Set 'skipProviderSelection': true to bypass IDE validation",
                            )
                        )

        return issues

    def validate_cluster_config(self) -> List[ValidationIssue]:
        """Validate cluster configuration file"""
        issues = []

        cluster_config_path = self.project_root / "config" / "cursor_ultron_model_config.json"
        if not cluster_config_path.exists():
            issues.append(
                ValidationIssue(
                    severity="info",
                    category="consistency",
                    file_path=str(cluster_config_path),
                    issue="Cluster config file not found",
                )
            )
            return issues

        try:
            with open(cluster_config_path, encoding="utf-8") as f:
                cluster_config = json.load(f)
        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity="error",
                    category="format",
                    file_path=str(cluster_config_path),
                    issue=f"Failed to load cluster config: {e}",
                )
            )
            return issues

        # Check endpoints match registry
        registry_endpoints = self.registry.get("endpoints", {})
        config_endpoints = cluster_config.get("endpoints", {})

        for endpoint_key, endpoint_config in config_endpoints.items():
            config_url = endpoint_config.get("url", "")

            # Find matching registry endpoint
            found_match = False
            for endpoint_id, registry_endpoint in registry_endpoints.items():
                registry_url = registry_endpoint.get("url", "")
                if config_url == registry_url or config_url.startswith(registry_url):
                    found_match = True
                    break

            if not found_match:
                issues.append(
                    ValidationIssue(
                        severity="warning",
                        category="consistency",
                        file_path=str(cluster_config_path),
                        issue=f"Endpoint '{endpoint_key}' with URL '{config_url}' not found in registry",
                        actual=config_url,
                        fix_suggestion="Update endpoint URL to match registry or add to registry",
                    )
                )

        return issues

    def check_all_endpoints_health(self) -> Dict[str, Tuple[str, Optional[str]]]:
        """Check health of all endpoints"""
        health_results = {}
        endpoints = self.registry.get("endpoints", {})

        for endpoint_id, endpoint in endpoints.items():
            status, message = self.check_endpoint_health(endpoint_id, endpoint)
            health_results[endpoint_id] = (status, message)

            # Update registry status if different
            current_status = endpoint.get("status", "unknown")
            if status != current_status:
                self.issues.append(
                    ValidationIssue(
                        severity="info" if status == "operational" else "warning",
                        category="health",
                        file_path=str(self.registry_path),
                        issue=f"Endpoint '{endpoint_id}' status changed: {current_status} → {status}",
                        actual=current_status,
                        expected=status,
                        fix_suggestion=f"Update registry status to '{status}'",
                    )
                )

        return health_results

    def validate_all(self, check_health: bool = True) -> ValidationResult:
        """Run all validation checks"""
        self.issues = []

        # Load registry
        if not self.load_registry():
            return ValidationResult(valid=False, issues=self.issues)

        # Validate registry structure
        self.issues.extend(self.validate_endpoint_registry())

        # Validate Cursor settings
        self.issues.extend(self.validate_cursor_settings())

        # Validate cluster config
        self.issues.extend(self.validate_cluster_config())

        # Check endpoint health
        health_results = {}
        if check_health:
            health_results = self.check_all_endpoints_health()

        # Count health statuses
        endpoints_checked = len(health_results)
        endpoints_healthy = sum(
            1 for status, _ in health_results.values() if status == "operational"
        )
        endpoints_unhealthy = sum(
            1 for status, _ in health_results.values() if status in ["degraded", "offline"]
        )
        endpoints_unknown = sum(1 for status, _ in health_results.values() if status == "unknown")

        # Determine if valid (no errors)
        has_errors = any(issue.severity == "error" for issue in self.issues)

        return ValidationResult(
            valid=not has_errors,
            issues=self.issues,
            endpoints_checked=endpoints_checked,
            endpoints_healthy=endpoints_healthy,
            endpoints_unhealthy=endpoints_unhealthy,
            endpoints_unknown=endpoints_unknown,
        )

    def print_report(self, result: ValidationResult):
        """Print validation report"""
        print("=" * 80)
        print("CLUSTER CONFIGURATION VALIDATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {result.timestamp}")
        print(f"Valid: {'✅ YES' if result.valid else '❌ NO'}")
        print()

        print("Endpoint Health Summary:")
        print(f"  Checked: {result.endpoints_checked}")
        print(f"  ✅ Healthy: {result.endpoints_healthy}")
        print(f"  ⚠️  Unhealthy: {result.endpoints_unhealthy}")
        print(f"  ❓ Unknown: {result.endpoints_unknown}")
        print()

        if result.issues:
            print(f"Issues Found: {len(result.issues)}")
            print()

            # Group by severity
            errors = [i for i in result.issues if i.severity == "error"]
            warnings = [i for i in result.issues if i.severity == "warning"]
            infos = [i for i in result.issues if i.severity == "info"]

            if errors:
                print("❌ ERRORS:")
                for issue in errors:
                    print(f"  [{issue.category}] {issue.file_path}")
                    print(f"    {issue.issue}")
                    if issue.expected:
                        print(f"    Expected: {issue.expected}")
                    if issue.actual:
                        print(f"    Actual: {issue.actual}")
                    if issue.fix_suggestion:
                        print(f"    Fix: {issue.fix_suggestion}")
                    print()

            if warnings:
                print("⚠️  WARNINGS:")
                for issue in warnings:
                    print(f"  [{issue.category}] {issue.file_path}")
                    print(f"    {issue.issue}")
                    if issue.fix_suggestion:
                        print(f"    Fix: {issue.fix_suggestion}")
                    print()

            if infos:
                print("ℹ️  INFO:")
                for issue in infos:
                    print(f"  [{issue.category}] {issue.file_path}")
                    print(f"    {issue.issue}")
                    print()
        else:
            print("✅ No issues found!")

        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate cluster configuration consistency")
    parser.add_argument(
        "--no-health-check", action="store_true", help="Skip endpoint health checks"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = ClusterConfigValidator(project_root)
    result = validator.validate_all(check_health=not args.no_health_check)

    if args.json:
        # Output as JSON
        output = {
            "valid": result.valid,
            "timestamp": result.timestamp,
            "endpoints_checked": result.endpoints_checked,
            "endpoints_healthy": result.endpoints_healthy,
            "endpoints_unhealthy": result.endpoints_unhealthy,
            "endpoints_unknown": result.endpoints_unknown,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file_path": issue.file_path,
                    "issue": issue.issue,
                    "expected": issue.expected,
                    "actual": issue.actual,
                    "fix_suggestion": issue.fix_suggestion,
                }
                for issue in result.issues
            ],
        }
        print(json.dumps(output, indent=2))
    else:
        validator.print_report(result)

    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
