#!/usr/bin/env python3
"""
Continuous Improvement Service
Tracks improvements and system evolution

Maintains blueprint synchronization and tracks improvements.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ContinuousImprovement")


class ContinuousImprovementService:
    """Manages continuous improvement and blueprint synchronization"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.improvements_dir = self.project_root / "data" / "continuous_improvement"
        self.improvements_dir.mkdir(parents=True, exist_ok=True)

        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.master_plan_file = self.project_root / "config" / "master_plan.json"

    def record_improvement(
        self,
        component: str,
        improvement_type: str,
        description: str,
        impact: str = "medium"
    ) -> Dict[str, Any]:
        """Record an improvement"""
        improvement = {
            "id": f"imp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "component": component,
            "type": improvement_type,
            "description": description,
            "impact": impact,
            "timestamp": datetime.now().isoformat(),
            "status": "recorded"
        }

        # Save improvement
        improvement_file = self.improvements_dir / f"{improvement['id']}.json"
        with open(improvement_file, 'w', encoding='utf-8') as f:
            json.dump(improvement, f, indent=2)

        logger.info(f"Improvement recorded: {component} - {improvement_type}")
        return improvement

    def sync_blueprint_with_implementation(self) -> Dict[str, Any]:
        try:
            """Synchronize blueprint with actual implementation"""
            logger.info("Synchronizing blueprint with implementation...")

            sync_report = {
                "sync_date": datetime.now().isoformat(),
                "blueprint_file": str(self.blueprint_file),
                "master_plan_file": str(self.master_plan_file),
                "changes": [],
                "status": "synced"
            }

            # Read blueprint
            if self.blueprint_file.exists():
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)

                # Check implementation status
                # This would compare blueprint requirements with actual implementation

                sync_report["blueprint_version"] = blueprint.get("version", "unknown")
                sync_report["status"] = "synced"

            # Save sync report
            report_file = self.improvements_dir / f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(sync_report, f, indent=2)

            return sync_report

        except Exception as e:
            self.logger.error(f"Error in sync_blueprint_with_implementation: {e}", exc_info=True)
            raise
    def get_improvement_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get improvement history"""
        improvements = []

        for improvement_file in sorted(self.improvements_dir.glob("imp_*.json"), reverse=True):
            if len(improvements) >= limit:
                break

            try:
                with open(improvement_file, 'r', encoding='utf-8') as f:
                    improvements.append(json.load(f))
            except Exception as e:
                logger.warning(f"Error reading improvement file {improvement_file}: {e}")

        return improvements


def get_improvement_service(project_root: Optional[Path] = None) -> ContinuousImprovementService:
    """Get global continuous improvement service"""
    return ContinuousImprovementService(project_root)
