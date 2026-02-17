#!/usr/bin/env python3
"""
Unified Cluster Configuration Manager

Centralized configuration management system that:
- Maintains single source of truth
- Detects configuration drift
- Auto-fixes inconsistencies
- Synchronizes across all config files

Tags: #CONFIGURATION #MANAGEMENT #SSOT #AUTOMATION @JARVIS @LUMINA
"""

import json
import os
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("cluster_config_manager")


@dataclass
class ConfigDrift:
    """Represents configuration drift"""

    file_path: str
    field: str
    expected_value: Any
    actual_value: Any
    severity: str  # "error", "warning", "info"
    fix_applied: bool = False


class ClusterConfigManager:
    """Unified configuration manager"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / "config" / "cluster_endpoint_registry.json"
        self.registry: Dict[str, Any] = {}
        self.drift_detected: List[ConfigDrift] = []

    def load_registry(self) -> bool:
        """Load endpoint registry (SSOT)"""
        try:
            if not self.registry_path.exists():
                logger.error("Registry not found")
                return False

            with open(self.registry_path, encoding="utf-8") as f:
                self.registry = json.load(f)
            return True
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            return False

    def detect_drift(self) -> List[ConfigDrift]:
        """Detect configuration drift across all config files"""
        self.drift_detected = []

        if not self.load_registry():
            return self.drift_detected

        # Check Cursor settings
        self._check_cursor_settings()

        # Check cluster config
        self._check_cluster_config()

        # Check environment config
        self._check_environment_config()

        return self.drift_detected

    def _check_cursor_settings(self):
        """Check Cursor IDE settings for drift"""
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            return

        cursor_settings_path = Path(appdata) / "Cursor" / "User" / "settings.json"
        if not cursor_settings_path.exists():
            return

        try:
            with open(cursor_settings_path, encoding="utf-8") as f:
                cursor_settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Cursor settings: {e}")
            return

        registry_endpoints = self.registry.get("endpoints", {})
        sections = [
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.agent.customModels",
        ]

        for section_key in sections:
            models = cursor_settings.get(section_key, [])
            for model in models:
                api_base = model.get("apiBase", "")
                name = model.get("name", "")

                # Find matching registry endpoint
                matching_endpoint = None
                for endpoint_id, endpoint in registry_endpoints.items():
                    endpoint_url = endpoint.get("url", "")
                    if api_base.startswith(endpoint_url) or endpoint_url in api_base:
                        matching_endpoint = endpoint
                        break

                if matching_endpoint:
                    # Check for drift
                    expected_local_only = (
                        True
                        if "localhost" in api_base
                        else matching_endpoint.get("localOnly", False)
                    )
                    actual_local_only = model.get("localOnly", False)

                    if expected_local_only != actual_local_only:
                        self.drift_detected.append(
                            ConfigDrift(
                                file_path=str(cursor_settings_path),
                                field=f"{section_key}.{name}.localOnly",
                                expected_value=expected_local_only,
                                actual_value=actual_local_only,
                                severity="warning",
                            )
                        )

    def _check_cluster_config(self):
        """Check cluster configuration for drift"""
        cluster_config_path = self.project_root / "config" / "cursor_ultron_model_config.json"
        if not cluster_config_path.exists():
            return

        try:
            with open(cluster_config_path, encoding="utf-8") as f:
                cluster_config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cluster config: {e}")
            return

        registry_endpoints = self.registry.get("endpoints", {})
        config_endpoints = cluster_config.get("endpoints", {})

        for endpoint_key, endpoint_config in config_endpoints.items():
            config_url = endpoint_config.get("url", "")

            # Find matching registry endpoint
            matching_endpoint = None
            for endpoint_id, endpoint in registry_endpoints.items():
                registry_url = endpoint.get("url", "")
                if config_url == registry_url or config_url.startswith(registry_url):
                    matching_endpoint = endpoint
                    break

            if matching_endpoint:
                # Check status drift
                expected_status = matching_endpoint.get("status", "unknown")
                actual_status = endpoint_config.get("status", "unknown")

                if expected_status != actual_status:
                    self.drift_detected.append(
                        ConfigDrift(
                            file_path=str(cluster_config_path),
                            field=f"endpoints.{endpoint_key}.status",
                            expected_value=expected_status,
                            actual_value=actual_status,
                            severity="info",
                        )
                    )

    def _check_environment_config(self):
        """Check environment configuration for drift"""
        env_config_path = self.project_root / "config" / "homelab_ai_ecosystem.json"
        if not env_config_path.exists():
            return

        try:
            with open(env_config_path, encoding="utf-8") as f:
                env_config = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load environment config: {e}")
            return

        # Check for endpoint references that don't match registry
        # (Implementation depends on structure of environment config)
        pass

    def fix_drift(self, dry_run: bool = False) -> Tuple[int, int]:
        """Fix detected configuration drift"""
        fixed = 0
        failed = 0

        for drift in self.drift_detected:
            if drift.fix_applied:
                continue

            try:
                if not dry_run:
                    success = self._apply_fix(drift)
                    if success:
                        drift.fix_applied = True
                        fixed += 1
                    else:
                        failed += 1
                else:
                    fixed += 1  # Count as would-be fixed in dry run
            except Exception as e:
                logger.error(f"Failed to fix drift in {drift.file_path}: {e}")
                failed += 1

        return fixed, failed

    def _apply_fix(self, drift: ConfigDrift) -> bool:
        """Apply fix for a single drift"""
        file_path = Path(drift.file_path)

        if not file_path.exists():
            return False

        # Backup file
        backup_path = file_path.with_suffix(".json.backup")
        if not backup_path.exists():
            shutil.copy2(file_path, backup_path)

        try:
            with open(file_path, encoding="utf-8") as f:
                config = json.load(f)

            # Apply fix based on field path
            field_parts = drift.field.split(".")
            current = config

            # Navigate to field
            for part in field_parts[:-1]:
                if part not in current:
                    return False
                current = current[part]

            # Set value
            field_name = field_parts[-1]
            current[field_name] = drift.expected_value

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"Fixed drift in {drift.file_path}: {drift.field}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply fix: {e}")
            return False

    def sync_all_configs(self, dry_run: bool = False) -> Dict[str, Any]:
        """Synchronize all config files with registry"""
        results = {"drift_detected": 0, "drift_fixed": 0, "drift_failed": 0, "files_updated": []}

        # Detect drift
        drift_list = self.detect_drift()
        results["drift_detected"] = len(drift_list)

        # Fix drift
        if not dry_run:
            fixed, failed = self.fix_drift(dry_run=False)
            results["drift_fixed"] = fixed
            results["drift_failed"] = failed

            # Collect updated files
            updated_files = set()
            for drift in drift_list:
                if drift.fix_applied:
                    updated_files.add(drift.file_path)
            results["files_updated"] = list(updated_files)
        else:
            fixed, failed = self.fix_drift(dry_run=True)
            results["drift_fixed"] = fixed
            results["drift_failed"] = failed

        return results

    def print_report(self, results: Dict[str, Any]):
        """Print synchronization report"""
        print("=" * 80)
        print("CLUSTER CONFIGURATION SYNCHRONIZATION REPORT")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()

        print(f"Drift Detected: {results['drift_detected']}")
        print(f"Drift Fixed: {results['drift_fixed']}")
        print(f"Drift Failed: {results['drift_failed']}")

        if results["files_updated"]:
            print(f"\nFiles Updated: {len(results['files_updated'])}")
            for file_path in results["files_updated"]:
                print(f"  ✅ {file_path}")

        if self.drift_detected:
            print("\nDrift Details:")
            for drift in self.drift_detected:
                status = "✅ Fixed" if drift.fix_applied else "⏳ Pending"
                print(f"  [{drift.severity.upper()}] {drift.file_path}")
                print(f"    Field: {drift.field}")
                print(f"    Expected: {drift.expected_value}")
                print(f"    Actual: {drift.actual_value}")
                print(f"    Status: {status}")
                print()

        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified cluster configuration manager")
    parser.add_argument("--detect-drift", action="store_true", help="Detect configuration drift")
    parser.add_argument("--fix-drift", action="store_true", help="Fix detected drift")
    parser.add_argument("--sync", action="store_true", help="Synchronize all configs with registry")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be changed without making changes"
    )

    args = parser.parse_args()

    manager = ClusterConfigManager(project_root)

    if args.detect_drift or args.fix_drift or args.sync:
        if args.sync:
            results = manager.sync_all_configs(dry_run=args.dry_run)
            manager.print_report(results)
        elif args.fix_drift:
            drift_list = manager.detect_drift()
            fixed, failed = manager.fix_drift(dry_run=args.dry_run)
            print(f"Fixed: {fixed}, Failed: {failed}")
        else:
            drift_list = manager.detect_drift()
            print(f"Drift detected: {len(drift_list)}")
            for drift in drift_list:
                print(f"  [{drift.severity}] {drift.file_path}: {drift.field}")
    else:
        # Default: sync
        results = manager.sync_all_configs(dry_run=args.dry_run)
        manager.print_report(results)


if __name__ == "__main__":
    main()
