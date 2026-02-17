#!/usr/bin/env python3
"""
Cursor IDE Performance Fix
Address heap-stack issues and bottlenecks

Tags: #CURSOR-IDE #PERFORMANCE #HEAP-STACK #BOTTLENECK #FIX
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIDEPerformanceFix")


class CursorIDEPerformanceFix:
    """
    Cursor IDE Performance Fix

    Addresses:
    - Heap-stack issues (Windows "not responding" popups)
    - NAS migration incomplete/partial status bottleneck
    - Storage bottlenecks
    - Performance optimization
    """

    def __init__(self, project_root: Path):
        """Initialize performance fix"""
        self.project_root = project_root
        self.logger = logger

        # Performance issues
        self.issues = {
            "heap_stack": {
                "symptom": "Windows 'not responding' popups",
                "cause": "Near edge of heap-stack",
                "status": "detected"
            },
            "nas_migration": {
                "symptom": "Incomplete/partial migration",
                "cause": "Storage NAS migration incomplete",
                "status": "bottleneck"
            },
            "storage": {
                "symptom": "Storage bottlenecks",
                "cause": "NAS migration incomplete",
                "status": "bottleneck"
            }
        }

        self.logger.info("🔧 Cursor IDE Performance Fix initialized")
        self.logger.info("   Addressing heap-stack and NAS migration bottlenecks")

    def diagnose_performance_issues(self) -> Dict[str, Any]:
        """Diagnose performance issues"""
        self.logger.info("🔍 Diagnosing performance issues...")

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "bottlenecks": [],
            "recommendations": []
        }

        # Check NAS migration status
        nas_status = self._check_nas_migration_status()
        if nas_status.get("incomplete"):
            diagnosis["bottlenecks"].append({
                "type": "nas_migration",
                "severity": "high",
                "description": "NAS migration incomplete/partial",
                "impact": "Storage bottlenecks, heap-stack pressure"
            })
            diagnosis["recommendations"].append({
                "priority": "high",
                "action": "Complete NAS migration",
                "details": "Resume and complete NAS migration to free up local storage"
            })

        # Check heap-stack indicators
        heap_stack_indicators = self._check_heap_stack_indicators()
        if heap_stack_indicators.get("near_limit"):
            diagnosis["issues"].append({
                "type": "heap_stack",
                "severity": "high",
                "description": "Near edge of heap-stack",
                "symptom": "Windows 'not responding' popups"
            })
            diagnosis["recommendations"].append({
                "priority": "critical",
                "action": "Reduce memory pressure",
                "details": "Complete NAS migration, optimize storage, reduce active processes"
            })

        return diagnosis

    def _check_nas_migration_status(self) -> Dict[str, Any]:
        """Check NAS migration status"""
        try:
            from nas_migration_status import NASMigrationStatus
            status_checker = NASMigrationStatus(self.project_root)
            status = status_checker.get_comprehensive_status()

            # Check if migration is incomplete
            migration_plan = status.get("migration_plan", {})
            doit_execution = status.get("doit_execution", {})
            nas_accessible = status.get("nas_accessibility", {})

            incomplete = False
            if migration_plan.get("available"):
                steps = migration_plan.get("steps", [])
                for step in steps:
                    if step.get("status") not in ["COMPLETED", "SKIPPED"]:
                        incomplete = True
                        break

            if doit_execution.get("available") and not doit_execution.get("executed"):
                incomplete = True

            return {
                "incomplete": incomplete,
                "nas_accessible": nas_accessible.get("accessible", False),
                "migration_plan": migration_plan,
                "doit_execution": doit_execution
            }
        except Exception as e:
            self.logger.warning(f"⚠️  Could not check NAS migration status: {e}")
            return {"incomplete": True, "error": str(e)}

    def _check_heap_stack_indicators(self) -> Dict[str, Any]:
        """Check heap-stack indicators"""
        # Check for large files, active processes, memory usage indicators
        indicators = {
            "near_limit": False,
            "indicators": []
        }

        # Check for large data directories
        data_dir = self.project_root / "data"
        if data_dir.exists():
            large_dirs = []
            for subdir in data_dir.iterdir():
                if subdir.is_dir():
                    try:
                        size = sum(f.stat().st_size for f in subdir.rglob('*') if f.is_file())
                        size_gb = size / (1024**3)
                        if size_gb > 1.0:  # More than 1GB
                            large_dirs.append({
                                "path": str(subdir),
                                "size_gb": size_gb
                            })
                    except Exception:
                        pass

            if large_dirs:
                indicators["near_limit"] = True
                indicators["indicators"].append({
                    "type": "large_data_directories",
                    "count": len(large_dirs),
                    "directories": large_dirs
                })

        return indicators

    def fix_nas_migration_bottleneck(self) -> Dict[str, Any]:
        """Fix NAS migration bottleneck"""
        self.logger.info("🔧 Fixing NAS migration bottleneck...")

        try:
            from resume_nas_migration_initiative import NASMigrationInitiative

            initiative = NASMigrationInitiative(project_root=self.project_root)

            # Check status first
            lumina_path = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")
            migration_info = initiative.check_migration_status(lumina_path)

            if migration_info.get("status"):
                status = migration_info["status"]
                if status.migration_status in ["interrupted", "partial", "incomplete"]:
                    self.logger.info("🔄 Resuming incomplete migration...")
                    success = initiative.resume_migration_initiative(lumina_path, dry_run=False)

                    return {
                        "success": success,
                        "action": "resumed_migration",
                        "status": status.migration_status,
                        "target": str(migration_info.get("target", "unknown"))
                    }
                elif status.migration_status == "complete":
                    return {
                        "success": True,
                        "action": "already_complete",
                        "status": "complete"
                    }
            else:
                # Status unknown - try to resume anyway
                self.logger.info("🔄 Migration status unknown - attempting to resume...")
                success = initiative.resume_migration_initiative(lumina_path, dry_run=False)

                return {
                    "success": success,
                    "action": "resumed_unknown_status",
                    "note": "Migration status was unknown, attempted resume"
                }
        except Exception as e:
            self.logger.error(f"❌ Error fixing NAS migration: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage to reduce heap-stack pressure"""
        self.logger.info("🔧 Optimizing storage...")

        optimizations = {
            "completed": [],
            "failed": [],
            "space_freed_gb": 0.0
        }

        # Optimization 1: Clean up temporary files
        try:
            temp_dirs = [
                self.project_root / "data" / "temp",
                self.project_root / "data" / "cache",
                self.project_root / "__pycache__"
            ]

            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    try:
                        size_before = sum(f.stat().st_size for f in temp_dir.rglob('*') if f.is_file())
                        # Clean old files (older than 7 days)
                        cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
                        cleaned = 0
                        for f in temp_dir.rglob('*'):
                            if f.is_file() and f.stat().st_mtime < cutoff:
                                try:
                                    size = f.stat().st_size
                                    f.unlink()
                                    cleaned += size
                                except Exception:
                                    pass

                        if cleaned > 0:
                            optimizations["space_freed_gb"] += cleaned / (1024**3)
                            optimizations["completed"].append(f"Cleaned {temp_dir.name}")
                    except Exception as e:
                        optimizations["failed"].append(f"Failed to clean {temp_dir.name}: {e}")
        except Exception as e:
            self.logger.warning(f"⚠️  Storage optimization error: {e}")

        return optimizations

    def apply_fixes(self) -> Dict[str, Any]:
        """Apply all performance fixes"""
        self.logger.info("🚀 Applying performance fixes...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "diagnosis": {},
            "fixes_applied": [],
            "results": {}
        }

        # Step 1: Diagnose
        diagnosis = self.diagnose_performance_issues()
        results["diagnosis"] = diagnosis

        # Step 2: Fix NAS migration bottleneck
        if any(b.get("type") == "nas_migration" for b in diagnosis.get("bottlenecks", [])):
            self.logger.info("🔧 Fixing NAS migration bottleneck...")
            nas_fix = self.fix_nas_migration_bottleneck()
            results["fixes_applied"].append("nas_migration")
            results["results"]["nas_migration"] = nas_fix

        # Step 3: Optimize storage
        self.logger.info("🔧 Optimizing storage...")
        storage_opt = self.optimize_storage()
        results["fixes_applied"].append("storage_optimization")
        results["results"]["storage_optimization"] = storage_opt

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Performance Fix")
        parser.add_argument("--diagnose", action="store_true", help="Diagnose performance issues")
        parser.add_argument("--fix", action="store_true", help="Apply fixes")
        parser.add_argument("--nas", action="store_true", help="Fix NAS migration bottleneck")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        fixer = CursorIDEPerformanceFix(project_root)

        if args.diagnose:
            diagnosis = fixer.diagnose_performance_issues()
            print("\n🔍 PERFORMANCE DIAGNOSIS:")
            print(json.dumps(diagnosis, indent=2, default=str))

        elif args.fix:
            results = fixer.apply_fixes()
            print("\n🔧 FIXES APPLIED:")
            print(json.dumps(results, indent=2, default=str))

        elif args.nas:
            nas_fix = fixer.fix_nas_migration_bottleneck()
            print("\n🔧 NAS MIGRATION FIX:")
            print(json.dumps(nas_fix, indent=2, default=str))

        else:
            print("Usage:")
            print("  --diagnose  : Diagnose performance issues")
            print("  --fix       : Apply all fixes")
            print("  --nas       : Fix NAS migration bottleneck")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()