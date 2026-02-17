#!/usr/bin/env python3
"""
Factory Processing Status Check

Check if the "factory" is actually processing and reproducing workflows:
- Are workflows executing?
- Are outputs being produced?
- Is the factory operational and generating results?

Tags: #FACTORY #PROCESSING #REPRODUCING #WORKFLOW #STATUS @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FactoryProcessingStatus")


class FactoryProcessingStatus:
    """
    Factory Processing Status Check

    Verifies if the factory is actually processing and reproducing workflows
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize factory status checker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        logger.info("✅ Factory Processing Status Check initialized")

    def check_factory_status(self) -> Dict[str, Any]:
        """Check if factory is processing and reproducing"""
        logger.info("="*80)
        logger.info("🏭 FACTORY PROCESSING STATUS CHECK")
        logger.info("="*80)

        status = {
            "timestamp": datetime.now().isoformat(),
            "factory_operational": False,
            "processing_active": False,
            "reproducing_outputs": False,
            "workflows_executed": 0,
            "outputs_produced": 0,
            "recent_activity": {},
            "issues": []
        }

        # Check @DOIT workflow executions
        doit_status = self._check_doit_executions()
        status["recent_activity"]["doit_workflows"] = doit_status
        if doit_status["executions_found"] > 0:
            status["processing_active"] = True
            status["workflows_executed"] += doit_status["executions_found"]
            status["outputs_produced"] += doit_status["outputs_produced"]

        # Check SYPHON imports
        syphon_status = self._check_syphon_imports()
        status["recent_activity"]["syphon_imports"] = syphon_status
        if syphon_status["imports_found"] > 0:
            status["processing_active"] = True
            status["outputs_produced"] += syphon_status["items_imported"]

        # Check daily source sweeps
        sweeps_status = self._check_daily_sweeps()
        status["recent_activity"]["daily_sweeps"] = sweeps_status
        if sweeps_status["executions_found"] > 0:
            status["processing_active"] = True
            status["workflows_executed"] += sweeps_status["executions_found"]

        # Check content creation outputs
        content_status = self._check_content_outputs()
        status["recent_activity"]["content_creation"] = content_status
        if content_status["outputs_found"] > 0:
            status["reproducing_outputs"] = True
            status["outputs_produced"] += content_status["outputs_found"]

        # Check building blocks/jedi archive outputs
        archive_status = self._check_archive_outputs()
        status["recent_activity"]["jedi_archive"] = archive_status
        if archive_status["catalog_entries"] > 0:
            status["reproducing_outputs"] = True
            status["outputs_produced"] += archive_status["catalog_entries"]

        # Determine factory operational status
        # Factory is operational if it's processing AND producing outputs (even if not all output types)
        status["factory_operational"] = (
            status["processing_active"] and 
            status["outputs_produced"] > 0
        )

        # Check for issues
        if not status["processing_active"]:
            status["issues"].append("No active processing detected")
        if status["outputs_produced"] == 0:
            status["issues"].append("No outputs being produced")
        if status["workflows_executed"] == 0:
            status["issues"].append("No workflows executed recently")
        if not status["reproducing_outputs"]:
            status["issues"].append("Content creation outputs idle (books/docuseries not being generated)")

        logger.info("="*80)
        if status["factory_operational"]:
            logger.info("✅ FACTORY IS OPERATIONAL - Processing and Reproducing")
        else:
            logger.info("⚠️  FACTORY STATUS: Needs Attention")
        logger.info("="*80)

        return status

    def _check_doit_executions(self) -> Dict[str, Any]:
        """Check @DOIT workflow executions"""
        workflow_dir = self.data_dir / "doit_workflows"
        if not workflow_dir.exists():
            return {
                "executions_found": 0,
                "outputs_produced": 0,
                "latest_execution": None,
                "status": "not_configured"
            }

        execution_files = list(workflow_dir.glob("doit_*.json"))
        recent_executions = []

        for exec_file in execution_files:
            try:
                with open(exec_file, 'r', encoding='utf-8') as f:
                    exec_data = json.load(f)
                    executed = exec_data.get("executed", False)
                    if executed:
                        recent_executions.append({
                            "file": exec_file.name,
                            "timestamp": exec_data.get("timestamp"),
                            "task": exec_data.get("task_description", "unknown"),
                            "executed": executed
                        })
            except:
                pass

        latest = max(recent_executions, key=lambda x: x.get("timestamp", "")) if recent_executions else None

        return {
            "executions_found": len(recent_executions),
            "outputs_produced": len(recent_executions),  # Each execution produces a result
            "latest_execution": latest["file"] if latest else None,
            "latest_task": latest["task"] if latest else None,
            "status": "operational" if recent_executions else "idle"
        }

    def _check_syphon_imports(self) -> Dict[str, Any]:
        """Check SYPHON imports"""
        imports_dir = self.data_dir / "syphon" / "imported_sources"
        if not imports_dir.exists():
            return {
                "imports_found": 0,
                "items_imported": 0,
                "latest_import": None,
                "status": "not_configured"
            }

        import_files = list(imports_dir.glob("import_result_*.json"))
        total_items = 0
        latest_import = None

        for import_file in import_files:
            try:
                with open(import_file, 'r', encoding='utf-8') as f:
                    import_data = json.load(f)
                    items = import_data.get("total_items_imported", 0)
                    total_items += items
                    if not latest_import or import_file.stat().st_mtime > latest_import.stat().st_mtime:
                        latest_import = import_file
            except:
                pass

        return {
            "imports_found": len(import_files),
            "items_imported": total_items,
            "latest_import": latest_import.name if latest_import else None,
            "status": "operational" if import_files else "idle"
        }

    def _check_daily_sweeps(self) -> Dict[str, Any]:
        try:
            """Check daily source sweeps"""
            sweeps_dir = self.data_dir / "daily_source_sweeps"
            if not sweeps_dir.exists():
                return {
                    "executions_found": 0,
                    "latest_execution": None,
                    "status": "not_configured"
                }

            execution_files = list(sweeps_dir.glob("execution_*.json")) + list(sweeps_dir.glob("peak_mcp_execution_*.json"))
            latest = max(execution_files, key=lambda p: p.stat().st_mtime) if execution_files else None

            return {
                "executions_found": len(execution_files),
                "latest_execution": latest.name if latest else None,
                "status": "operational" if execution_files else "idle"
            }

        except Exception as e:
            self.logger.error(f"Error in _check_daily_sweeps: {e}", exc_info=True)
            raise
    def _check_content_outputs(self) -> Dict[str, Any]:
        try:
            """Check content creation outputs"""
            content_dir = self.data_dir / "content_creation"
            if not content_dir.exists():
                return {
                    "outputs_found": 0,
                    "books_created": 0,
                    "status": "not_configured"
                }

            books = list(content_dir.glob("book_*.json"))
            docuseries = list(content_dir.glob("docuseries_*.json"))

            return {
                "outputs_found": len(books) + len(docuseries),
                "books_created": len(books),
                "docuseries_created": len(docuseries),
                "status": "operational" if (books or docuseries) else "idle"
            }

        except Exception as e:
            self.logger.error(f"Error in _check_content_outputs: {e}", exc_info=True)
            raise
    def _check_archive_outputs(self) -> Dict[str, Any]:
        try:
            """Check Jedi Archive outputs"""
            holocron_dir = self.data_dir / "holocron"
            if not holocron_dir.exists():
                return {
                    "catalog_entries": 0,
                    "status": "not_configured"
                }

            catalog_files = list(holocron_dir.rglob("catalog_*.json"))

            return {
                "catalog_entries": len(catalog_files),
                "status": "operational" if catalog_files else "idle"
            }


        except Exception as e:
            self.logger.error(f"Error in _check_archive_outputs: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🏭 FACTORY PROCESSING STATUS CHECK")
    print("="*80 + "\n")

    checker = FactoryProcessingStatus()
    status = checker.check_factory_status()

    print("\n" + "="*80)
    print("🏭 FACTORY STATUS REPORT")
    print("="*80)
    print(f"Timestamp: {status['timestamp']}")
    print(f"\nFactory Operational: {'✅ YES' if status['factory_operational'] else '❌ NO'}")
    print(f"Processing Active: {'✅ YES' if status['processing_active'] else '❌ NO'}")
    print(f"Reproducing Outputs: {'✅ YES' if status['reproducing_outputs'] else '❌ NO'}")
    print(f"\nMetrics:")
    print(f"  Workflows Executed: {status['workflows_executed']}")
    print(f"  Outputs Produced: {status['outputs_produced']}")

    print(f"\nRecent Activity:")
    for activity_type, activity_data in status['recent_activity'].items():
        print(f"  {activity_type.replace('_', ' ').title()}:")
        for key, value in activity_data.items():
            if key != "status":
                print(f"    {key}: {value}")
        print(f"    Status: {activity_data.get('status', 'unknown')}")

    if status.get('issues'):
        print(f"\n⚠️  Issues Detected: {len(status['issues'])}")
        for issue in status['issues']:
            print(f"    - {issue}")

    print("\n" + "="*80)
    if status['factory_operational']:
        print("✅ FACTORY IS OPERATIONAL - Processing and Reproducing")
    else:
        print("⚠️  FACTORY NEEDS ATTENTION")
    print("="*80 + "\n")
