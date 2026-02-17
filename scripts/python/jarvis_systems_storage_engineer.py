#!/usr/bin/env python3
"""
JARVIS Systems Storage Engineer

Manages system storage, disk space, NAS migration, and storage optimization.
Coordinates with disk space manager, NAS migration manager, and storage systems.

Tags: #STORAGE #SYSTEM-HEALTH #NAS-MIGRATION @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_disk_space_manager import JARVISDiskSpaceManager
    from jarvis_nas_migration_manager import JARVISNASMigrationManager
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JARVISDiskSpaceManager = None
    JARVISNASMigrationManager = None

logger = get_logger("JARVISStorageEngineer")


class JARVISSystemsStorageEngineer:
    """
    JARVIS Systems Storage Engineer

    Manages all aspects of system storage:
    - Disk space monitoring and management
    - NAS migration and network drive mapping
    - Storage optimization
    - Data lifecycle management
    - Storage capacity planning
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Initialize storage management systems
        self.disk_manager = None
        self.nas_manager = None

        if JARVISDiskSpaceManager:
            try:
                self.disk_manager = JARVISDiskSpaceManager(project_root)
                self.logger.info("✅ Disk Space Manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Disk Space Manager not available: {e}")

        if JARVISNASMigrationManager:
            try:
                self.nas_manager = JARVISNASMigrationManager(project_root)
                self.logger.info("✅ NAS Migration Manager initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  NAS Migration Manager not available: {e}")

        self.logger.info("✅ JARVIS Systems Storage Engineer initialized")

    def get_storage_health_report(self) -> Dict[str, Any]:
        """Get comprehensive storage health report"""
        self.logger.info("📊 Generating storage health report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "disk_space": {},
            "nas_status": {},
            "network_drives": {},
            "migration_status": {},
            "recommendations": [],
            "critical": False
        }

        # Disk space analysis
        if self.disk_manager:
            disk_report = self.disk_manager.generate_report()
            report["disk_space"] = disk_report.get("disk_usage", {})
            report["critical"] = disk_report.get("critical", False)

            # Add recommendations
            for rec in disk_report.get("recommendations", []):
                report["recommendations"].append({
                    "source": "disk_space",
                    "priority": rec.get("priority", "MEDIUM"),
                    "action": rec.get("action", ""),
                    "details": rec.get("details", "")
                })

        # NAS and network drives status
        if self.nas_manager:
            # Get network drive mappings
            drive_config = self.nas_manager.get_network_drive_mappings()
            report["network_drives"] = {
                "configured": len(drive_config.get("mappings", [])),
                "mappings": drive_config.get("mappings", [])
            }

            # Get migration plan
            try:
                migration_plan = self.nas_manager.create_migration_plan()
                report["migration_status"] = {
                    "candidates_gb": migration_plan.get("estimated_space_freed_gb", 0),
                    "steps": migration_plan.get("steps", [])
                }
            except Exception as e:
                self.logger.warning(f"⚠️  Could not get migration plan: {e}")

        return report

    def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage across the system"""
        self.logger.info("🔧 Optimizing storage...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "disk_cleanup": {},
            "nas_migration": {},
            "space_freed_gb": 0.0,
            "errors": []
        }

        # Clean up disk space
        if self.disk_manager:
            try:
                cleanup_result = self.disk_manager.cleanup_docker(
                    prune_images=True,
                    prune_build_cache=True
                )
                results["disk_cleanup"] = cleanup_result
                results["space_freed_gb"] += cleanup_result.get("space_freed_gb", 0.0)
            except Exception as e:
                results["errors"].append(f"Disk cleanup error: {str(e)}")

        # Execute NAS migration (dry run first)
        if self.nas_manager:
            try:
                migration_result = self.nas_manager.execute_migration_plan(dry_run=True)
                results["nas_migration"] = migration_result
            except Exception as e:
                results["errors"].append(f"NAS migration error: {str(e)}")

        return results

    def manage_storage_capacity(self) -> Dict[str, Any]:
        """Manage storage capacity and plan for growth"""
        self.logger.info("📈 Managing storage capacity...")

        capacity_plan = {
            "timestamp": datetime.now().isoformat(),
            "current_usage": {},
            "projected_growth": {},
            "recommendations": []
        }

        if self.disk_manager:
            disk_usage = self.disk_manager.get_disk_usage("C:")
            capacity_plan["current_usage"] = disk_usage

            # Calculate projections
            percent_free = disk_usage.get("percent_free", 0)
            free_gb = disk_usage.get("free_gb", 0)

            if percent_free < 10:
                capacity_plan["recommendations"].append({
                    "priority": "CRITICAL",
                    "action": "Immediate storage expansion or cleanup required",
                    "details": f"Only {percent_free:.1f}% free space remaining"
                })
            elif percent_free < 20:
                capacity_plan["recommendations"].append({
                    "priority": "HIGH",
                    "action": "Plan for storage expansion or migration",
                    "details": f"{percent_free:.1f}% free space - approaching critical threshold"
                })

        return capacity_plan


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="JARVIS Systems Storage Engineer")
        parser.add_argument("--health", action="store_true", help="Get storage health report")
        parser.add_argument("--optimize", action="store_true", help="Optimize storage")
        parser.add_argument("--capacity", action="store_true", help="Manage storage capacity")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        engineer = JARVISSystemsStorageEngineer(project_root)

        if args.health:
            report = engineer.get_storage_health_report()
            print(json.dumps(report, indent=2, default=str))

        elif args.optimize:
            results = engineer.optimize_storage()
            print(json.dumps(results, indent=2, default=str))

        elif args.capacity:
            plan = engineer.manage_storage_capacity()
            print(json.dumps(plan, indent=2, default=str))

        else:
            # Default: health report
            report = engineer.get_storage_health_report()
            print(json.dumps(report, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()