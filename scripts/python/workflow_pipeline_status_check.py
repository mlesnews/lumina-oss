#!/usr/bin/env python3
"""
Workflow Pipeline Status Check

Comprehensive status check of all workflow pipeline systems:
- @DOIT Workflow with @5W1H
- SYPHON + Agents + VAs + @asks Unified System
- Daily Source Sweeps (NAS KRON SCHEDULER)
- SYPHON Imports of Daily Sources
- Workflow Flow Rate Calculator
- IDE Footer Flow Rate Display
- Content Creation Engine
- Building Blocks + @PEAK + Jedi Archive Organizer

Tags: #STATUS #WORKFLOW #PIPELINE #MONITORING @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
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

logger = get_logger("WorkflowPipelineStatus")


class WorkflowPipelineStatusCheck:
    """
    Workflow Pipeline Status Check

    Comprehensive status check of all workflow pipeline systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow pipeline status checker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        logger.info("✅ Workflow Pipeline Status Check initialized")

    def check_all_systems(self) -> Dict[str, Any]:
        """Check status of all workflow pipeline systems"""
        logger.info("="*80)
        logger.info("📊 WORKFLOW PIPELINE STATUS CHECK")
        logger.info("="*80)

        status = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "overall_status": "unknown",
            "summary": {}
        }

        # 1. @DOIT Workflow with @5W1H
        status["systems"]["doit_5w1h_workflow"] = self._check_doit_5w1h_workflow()

        # 2. SYPHON + Agents + VAs + @asks Unified System
        status["systems"]["syphon_agents_asks_unified"] = self._check_syphon_agents_asks_unified()

        # 3. Daily Source Sweeps (NAS KRON SCHEDULER)
        status["systems"]["daily_source_sweeps"] = self._check_daily_source_sweeps()

        # 4. SYPHON Imports of Daily Sources
        status["systems"]["syphon_imports"] = self._check_syphon_imports()

        # 5. Workflow Flow Rate Calculator
        status["systems"]["workflow_flow_rate"] = self._check_workflow_flow_rate()

        # 6. IDE Footer Flow Rate Display
        status["systems"]["ide_footer_display"] = self._check_ide_footer_display()

        # 7. Content Creation Engine
        status["systems"]["content_creation"] = self._check_content_creation()

        # 8. Building Blocks + @PEAK + Jedi Archive
        status["systems"]["building_blocks_peak_jedi"] = self._check_building_blocks_peak_jedi()

        # Calculate overall status
        status["overall_status"] = self._calculate_overall_status(status["systems"])

        # Generate summary
        status["summary"] = self._generate_summary(status["systems"])

        logger.info("="*80)
        logger.info(f"✅ Status Check Complete - Overall: {status['overall_status']}")
        logger.info("="*80)

        return status

    def _check_doit_5w1h_workflow(self) -> Dict[str, Any]:
        """Check @DOIT Workflow with @5W1H status"""
        try:
            from doit_5w1h_workflow import DOIT5W1HWorkflow

            workflow = DOIT5W1HWorkflow(project_root=self.project_root)

            # Check for recent workflow results
            workflow_dir = self.data_dir / "doit_workflows"
            recent_results = list(workflow_dir.glob("doit_*.json")) if workflow_dir.exists() else []
            latest_result = max(recent_results, key=lambda p: p.stat().st_mtime) if recent_results else None

            return {
                "status": "operational",
                "available": True,
                "recent_workflows": len(recent_results),
                "latest_workflow": latest_result.name if latest_result else None,
                "framework": "@DOIT + @5W1H (ORDER 66)"
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_syphon_agents_asks_unified(self) -> Dict[str, Any]:
        """Check SYPHON + Agents + VAs + @asks Unified System status"""
        try:
            from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem

            system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
            system_status = system.get_system_status()

            return {
                "status": "operational" if system_status.get("syphon_available") else "partial",
                "available": True,
                "syphon_available": system_status.get("syphon_available", False),
                "asks_available": system_status.get("asks_available", False),
                "agents_tracked": system_status.get("agents_tracked", 0),
                "running": system_status.get("running", False)
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_daily_source_sweeps(self) -> Dict[str, Any]:
        """Check Daily Source Sweeps status"""
        try:
            sweeps_dir = self.data_dir / "daily_source_sweeps"
            if sweeps_dir.exists():
                execution_files = list(sweeps_dir.glob("execution_*.json"))
                peak_mcp_files = list(sweeps_dir.glob("peak_mcp_execution_*.json"))
                latest_execution = max(execution_files + peak_mcp_files, key=lambda p: p.stat().st_mtime) if (execution_files or peak_mcp_files) else None

                return {
                    "status": "operational",
                    "available": True,
                    "total_executions": len(execution_files) + len(peak_mcp_files),
                    "latest_execution": latest_execution.name if latest_execution else None,
                    "nas_kron_scheduler": "configured"
                }
            else:
                return {
                    "status": "not_configured",
                    "available": False
                }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_syphon_imports(self) -> Dict[str, Any]:
        """Check SYPHON Imports status"""
        try:
            syphon_imports_dir = self.data_dir / "syphon" / "imported_sources"
            if syphon_imports_dir.exists():
                import_files = list(syphon_imports_dir.glob("import_result_*.json"))
                latest_import = max(import_files, key=lambda p: p.stat().st_mtime) if import_files else None

                # Check latest import result
                total_items = 0
                if latest_import:
                    try:
                        with open(latest_import, 'r', encoding='utf-8') as f:
                            import_data = json.load(f)
                            total_items = import_data.get("total_items_imported", 0)
                    except:
                        pass

                return {
                    "status": "operational",
                    "available": True,
                    "total_imports": len(import_files),
                    "latest_import": latest_import.name if latest_import else None,
                    "total_items_imported": total_items
                }
            else:
                return {
                    "status": "not_configured",
                    "available": False
                }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_workflow_flow_rate(self) -> Dict[str, Any]:
        """Check Workflow Flow Rate Calculator status"""
        try:
            from workflow_flow_rate_calculator import WorkflowFlowRateCalculator

            calculator = WorkflowFlowRateCalculator(project_root=self.project_root)
            stats = calculator.calculate_flow_rate()

            return {
                "status": "operational",
                "available": True,
                "current_flow_rate": stats.current_flow_rate,
                "peak_flow_rate": stats.peak_flow_rate,
                "efficiency": stats.efficiency,
                "active_workflows": stats.active_workflows
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_ide_footer_display(self) -> Dict[str, Any]:
        """Check IDE Footer Flow Rate Display status"""
        try:
            from ide_footer_flow_rate_display import IDEFooterFlowRateDisplay

            display = IDEFooterFlowRateDisplay(project_root=self.project_root)
            stats = display.get_stats()

            return {
                "status": "operational",
                "available": True,
                "display_active": stats is not None,
                "current_flow_rate": stats.get("current_flow_rate", 0) if stats else 0
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_content_creation(self) -> Dict[str, Any]:
        """Check Content Creation Engine status"""
        try:
            from content_creation_engine import ContentCreationEngine

            engine = ContentCreationEngine(project_root=self.project_root)

            # Check for created content
            content_dir = self.data_dir / "content_creation"
            books = list(content_dir.glob("book_*.json")) if content_dir.exists() else []

            return {
                "status": "operational",
                "available": True,
                "books_created": len(books)
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _check_building_blocks_peak_jedi(self) -> Dict[str, Any]:
        """Check Building Blocks + @PEAK + Jedi Archive status"""
        try:
            from building_blocks_peak_jedi_organizer import BuildingBlocksPeakJediOrganizer

            organizer = BuildingBlocksPeakJediOrganizer(project_root=self.project_root)

            # Check for catalog entries
            holocron_dir = self.data_dir / "holocron"
            catalog_files = list(holocron_dir.rglob("catalog_*.json")) if holocron_dir.exists() else []

            return {
                "status": "operational",
                "available": True,
                "catalog_entries": len(catalog_files)
            }
        except Exception as e:
            return {
                "status": "error",
                "available": False,
                "error": str(e)
            }

    def _calculate_overall_status(self, systems: Dict[str, Dict[str, Any]]) -> str:
        """Calculate overall pipeline status"""
        operational = sum(1 for s in systems.values() if s.get("status") == "operational")
        partial = sum(1 for s in systems.values() if s.get("status") == "partial")
        errors = sum(1 for s in systems.values() if s.get("status") == "error")
        total = len(systems)

        if operational == total:
            return "✅ FULLY OPERATIONAL"
        elif operational + partial == total:
            return "⚠️  OPERATIONAL (PARTIAL)"
        elif operational > total / 2:
            return "⚠️  MOSTLY OPERATIONAL"
        elif errors > 0:
            return "❌ ERRORS DETECTED"
        else:
            return "⚠️  NEEDS ATTENTION"

    def _generate_summary(self, systems: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        operational_count = sum(1 for s in systems.values() if s.get("status") == "operational")
        total_count = len(systems)

        return {
            "total_systems": total_count,
            "operational_systems": operational_count,
            "operational_percentage": (operational_count / total_count * 100) if total_count > 0 else 0,
            "systems_by_status": {
                "operational": operational_count,
                "partial": sum(1 for s in systems.values() if s.get("status") == "partial"),
                "error": sum(1 for s in systems.values() if s.get("status") == "error"),
                "not_configured": sum(1 for s in systems.values() if s.get("status") == "not_configured")
            }
        }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 WORKFLOW PIPELINE STATUS CHECK")
    print("="*80 + "\n")

    status_checker = WorkflowPipelineStatusCheck()
    status = status_checker.check_all_systems()

    print("\n" + "="*80)
    print("📊 WORKFLOW PIPELINE STATUS REPORT")
    print("="*80)
    print(f"Timestamp: {status['timestamp']}")
    print(f"Overall Status: {status['overall_status']}")
    print(f"\nSummary:")
    summary = status['summary']
    print(f"  Total Systems: {summary['total_systems']}")
    print(f"  Operational: {summary['operational_systems']} ({summary['operational_percentage']:.1f}%)")
    print(f"  Status Breakdown:")
    for status_type, count in summary['systems_by_status'].items():
        if count > 0:
            print(f"    {status_type}: {count}")

    print(f"\nSystem Details:")
    for system_name, system_status in status['systems'].items():
        status_icon = "✅" if system_status.get("status") == "operational" else "⚠️" if system_status.get("status") == "partial" else "❌"
        print(f"  {status_icon} {system_name.replace('_', ' ').title()}: {system_status.get('status', 'unknown')}")
        if system_status.get("available"):
            # Show key metrics
            if "recent_workflows" in system_status:
                print(f"      Recent Workflows: {system_status['recent_workflows']}")
            if "agents_tracked" in system_status:
                print(f"      Agents Tracked: {system_status['agents_tracked']}")
            if "total_executions" in system_status:
                print(f"      Total Executions: {system_status['total_executions']}")
            if "total_items_imported" in system_status:
                print(f"      Items Imported: {system_status['total_items_imported']}")
            if "current_flow_rate" in system_status:
                print(f"      Flow Rate: {system_status['current_flow_rate']:.2f} workflows/s")
            if "peak_flow_rate" in system_status:
                print(f"      Peak Flow Rate: {system_status['peak_flow_rate']:.2f} workflows/s")

    print("\n✅ Status Check Complete")
    print("="*80 + "\n")
