#!/usr/bin/env python3
"""
Mantra Evolution & Static State Tracker

Tracks workflow mantras and their evolution to static states.
When a mantra reaches 100% utilization or maximum effectiveness for a situation,
it becomes STATIC - meaning optimization is complete.

Current Best Workflow Enhancement: Memory Gap Prevention System

All mantras will become static at some stage due to:
- 100% utilization reached
- Capped at maximum for particular situation(s)
- Optimization complete

Tags: #mantras #workflow #static_state #evolution #optimization #100_percent
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from prevent_memory_gap_automation import MemoryGapPrevention

logger = get_logger("MantraEvolutionTracker")


class MantraState(Enum):
    """Mantra state in evolution"""
    ACTIVE = "active"  # Currently being applied
    OPTIMIZING = "optimizing"  # In process of improvement
    STATIC = "static"  # Reached 100% or maximum - optimization complete
    OBSOLETE = "obsolete"  # Replaced by better mantra


class UtilizationLevel(Enum):
    """Utilization level"""
    LOW = "low"  # 0-25%
    MEDIUM = "medium"  # 26-50%
    HIGH = "high"  # 51-75%
    VERY_HIGH = "very_high"  # 76-99%
    MAXIMUM = "maximum"  # 100% or capped


@dataclass
class MantraEvolution:
    """Mantra evolution tracking"""
    mantra_id: str
    mantra: str
    stage: str  # development, it_testing, etc.
    state: MantraState
    utilization_percentage: float  # 0-100
    utilization_level: UtilizationLevel
    reached_static_date: Optional[datetime] = None
    static_reason: str = ""  # Why it became static
    max_cap_reached: bool = False
    situations: List[str] = field(default_factory=list)  # Situations where it applies
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['state'] = self.state.value
        result['utilization_level'] = self.utilization_level.value
        if self.reached_static_date:
            result['reached_static_date'] = self.reached_static_date.isoformat()
        result['created_at'] = self.created_at.isoformat()
        result['last_updated'] = self.last_updated.isoformat()
        return result


class MantraEvolutionTracker:
    """
    Mantra Evolution & Static State Tracker

    Tracks when mantras reach static state (100% utilization or maximum cap).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize mantra evolution tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "mantra_evolution"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tracker_file = self.data_dir / "mantra_evolution.json"
        self.mantras: Dict[str, MantraEvolution] = {}

        # Load existing tracking data
        self.load_tracker()

        # Initialize with current mantras
        self._initialize_current_mantras()

        logger.info("=" * 80)
        logger.info("📈 MANTRA EVOLUTION & STATIC STATE TRACKER")
        logger.info("=" * 80)
        logger.info("   Principle: All mantras become static at 100% utilization")
        logger.info("   Best Enhancement: Memory Gap Prevention System")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_current_mantras(self):
        """Initialize tracking for current mantras"""
        # Development Mantra
        if "document_document_document" not in self.mantras:
            self.mantras["document_document_document"] = MantraEvolution(
                mantra_id="document_document_document",
                mantra="DOCUMENT, DOCUMENT, DOCUMENT",
                stage="development",
                state=MantraState.ACTIVE,
                utilization_percentage=50.0,  # Current logging compliance
                utilization_level=UtilizationLevel.MEDIUM,
                situations=["code_development", "logging", "documentation"],
                metrics={
                    "logging_compliance": 50.0,
                    "files_compliant": 651,
                    "files_total": 1302
                }
            )

        # IT/Testing Mantra
        if "delegate_delegate_delegate" not in self.mantras:
            self.mantras["delegate_delegate_delegate"] = MantraEvolution(
                mantra_id="delegate_delegate_delegate",
                mantra="DELEGATE, DELEGATE, DELEGATE",
                stage="it_testing",
                state=MantraState.ACTIVE,
                utilization_percentage=0.0,  # Just implemented
                utilization_level=UtilizationLevel.LOW,
                situations=["automation", "testing", "system_delegation"],
                metrics={
                    "automation_count": 0,
                    "delegated_tasks": 0
                }
            )

        # Memory Gap Prevention (Current Best Enhancement)
        if "memory_gap_prevention" not in self.mantras:
            self.mantras["memory_gap_prevention"] = MantraEvolution(
                mantra_id="memory_gap_prevention",
                mantra="Prevent Memory Gaps - Check Before Storing",
                stage="it_testing",
                state=MantraState.ACTIVE,
                utilization_percentage=100.0,  # Fully implemented and working
                utilization_level=UtilizationLevel.MAXIMUM,
                situations=["memory_storage", "duplicate_prevention", "DRY_principle"],
                metrics={
                    "prevention_success_rate": 100.0,
                    "duplicates_prevented": 1,  # Already prevented one
                    "system_status": "operational"
                },
                static_reason="Fully implemented and operational - prevents all duplicate memory storage",
                max_cap_reached=True
            )

    def update_utilization(
        self,
        mantra_id: str,
        utilization_percentage: float,
        metrics: Optional[Dict[str, Any]] = None
    ):
        """Update mantra utilization percentage"""
        if mantra_id not in self.mantras:
            logger.warning(f"Mantra {mantra_id} not found")
            return

        mantra = self.mantras[mantra_id]
        mantra.utilization_percentage = utilization_percentage
        mantra.last_updated = datetime.now()

        # Update utilization level
        if utilization_percentage >= 100.0:
            mantra.utilization_level = UtilizationLevel.MAXIMUM
            mantra.state = MantraState.STATIC
            if not mantra.reached_static_date:
                mantra.reached_static_date = datetime.now()
                mantra.static_reason = "Reached 100% utilization"
                mantra.max_cap_reached = True
                logger.info(f"🎯 Mantra {mantra_id} reached STATIC state at 100%")
        elif utilization_percentage >= 76.0:
            mantra.utilization_level = UtilizationLevel.VERY_HIGH
        elif utilization_percentage >= 51.0:
            mantra.utilization_level = UtilizationLevel.HIGH
        elif utilization_percentage >= 26.0:
            mantra.utilization_level = UtilizationLevel.MEDIUM
        else:
            mantra.utilization_level = UtilizationLevel.LOW

        # Update metrics
        if metrics:
            mantra.metrics.update(metrics)

        logger.info(f"📊 Updated {mantra_id}: {utilization_percentage:.1f}% ({mantra.utilization_level.value})")

    def mark_static(
        self,
        mantra_id: str,
        reason: str,
        max_cap: bool = True
    ):
        """Manually mark mantra as static"""
        if mantra_id not in self.mantras:
            logger.warning(f"Mantra {mantra_id} not found")
            return

        mantra = self.mantras[mantra_id]
        mantra.state = MantraState.STATIC
        mantra.static_reason = reason
        mantra.max_cap_reached = max_cap
        mantra.utilization_level = UtilizationLevel.MAXIMUM
        mantra.utilization_percentage = 100.0
        if not mantra.reached_static_date:
            mantra.reached_static_date = datetime.now()
        mantra.last_updated = datetime.now()

        logger.info(f"✅ Mantra {mantra_id} marked as STATIC")
        logger.info(f"   Reason: {reason}")

    def get_static_mantras(self) -> List[MantraEvolution]:
        """Get all mantras in static state"""
        return [m for m in self.mantras.values() if m.state == MantraState.STATIC]

    def get_active_mantras(self) -> List[MantraEvolution]:
        """Get all active mantras"""
        return [m for m in self.mantras.values() if m.state == MantraState.ACTIVE]

    def get_best_enhancement(self) -> Optional[MantraEvolution]:
        """Get current best workflow enhancement"""
        # Find mantra with highest utilization that's not static
        active = self.get_active_mantras()
        if not active:
            return None

        # Or return the memory gap prevention if it exists
        if "memory_gap_prevention" in self.mantras:
            return self.mantras["memory_gap_prevention"]

        # Otherwise, highest utilization active mantra
        return max(active, key=lambda m: m.utilization_percentage)

    def save_tracker(self):
        try:
            """Save tracker data to file"""
            tracker_data = {
                "last_updated": datetime.now().isoformat(),
                "total_mantras": len(self.mantras),
                "static_count": len(self.get_static_mantras()),
                "active_count": len(self.get_active_mantras()),
                "mantras": {k: v.to_dict() for k, v in self.mantras.items()}
            }

            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2, default=str)

            logger.info(f"💾 Saved mantra evolution tracker: {len(self.mantras)} mantras")

        except Exception as e:
            self.logger.error(f"Error in save_tracker: {e}", exc_info=True)
            raise
    def load_tracker(self):
        """Load tracker data from file"""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    tracker_data = json.load(f)

                for mantra_id, mantra_data in tracker_data.get('mantras', {}).items():
                    evolution = MantraEvolution(
                        mantra_id=mantra_data['mantra_id'],
                        mantra=mantra_data['mantra'],
                        stage=mantra_data['stage'],
                        state=MantraState(mantra_data['state']),
                        utilization_percentage=mantra_data['utilization_percentage'],
                        utilization_level=UtilizationLevel(mantra_data['utilization_level']),
                        static_reason=mantra_data.get('static_reason', ''),
                        max_cap_reached=mantra_data.get('max_cap_reached', False),
                        situations=mantra_data.get('situations', []),
                        metrics=mantra_data.get('metrics', {})
                    )
                    if mantra_data.get('reached_static_date'):
                        evolution.reached_static_date = datetime.fromisoformat(mantra_data['reached_static_date'])
                    if mantra_data.get('created_at'):
                        evolution.created_at = datetime.fromisoformat(mantra_data['created_at'])
                    if mantra_data.get('last_updated'):
                        evolution.last_updated = datetime.fromisoformat(mantra_data['last_updated'])

                    self.mantras[mantra_id] = evolution

                logger.info(f"📂 Loaded {len(self.mantras)} mantras from tracker")
            except Exception as e:
                logger.debug(f"Could not load tracker: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate mantra evolution report"""
        static_mantras = self.get_static_mantras()
        active_mantras = self.get_active_mantras()
        best_enhancement = self.get_best_enhancement()

        report = {
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_mantras": len(self.mantras),
                "static_count": len(static_mantras),
                "active_count": len(active_mantras),
                "best_enhancement": best_enhancement.mantra if best_enhancement else None
            },
            "static_mantras": [m.to_dict() for m in static_mantras],
            "active_mantras": [m.to_dict() for m in active_mantras],
            "all_mantras": [m.to_dict() for m in self.mantras.values()]
        }

        return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Mantra Evolution & Static State Tracker")
        parser.add_argument('--update', nargs=3, metavar=('MANTRA_ID', 'UTILIZATION', 'METRICS_JSON'),
                           help='Update mantra utilization (metrics as JSON string)')
        parser.add_argument('--mark-static', nargs=2, metavar=('MANTRA_ID', 'REASON'),
                           help='Mark mantra as static')
        parser.add_argument('--report', action='store_true', help='Generate report')
        parser.add_argument('--save', action='store_true', help='Save tracker')

        args = parser.parse_args()

        tracker = MantraEvolutionTracker()

        if args.update:
            mantra_id, utilization_str, metrics_json = args.update
            utilization = float(utilization_str)
            metrics = json.loads(metrics_json) if metrics_json else {}
            tracker.update_utilization(mantra_id, utilization, metrics)
            if args.save:
                tracker.save_tracker()

        elif args.mark_static:
            mantra_id, reason = args.mark_static
            tracker.mark_static(mantra_id, reason)
            if args.save:
                tracker.save_tracker()

        elif args.report:
            report = tracker.generate_report()
            print("\n" + "=" * 80)
            print("📈 MANTRA EVOLUTION REPORT")
            print("=" * 80)
            print(f"Total Mantras: {report['summary']['total_mantras']}")
            print(f"Static (100%): {report['summary']['static_count']}")
            print(f"Active: {report['summary']['active_count']}")
            print(f"Best Enhancement: {report['summary']['best_enhancement']}")
            print("")

            if report['static_mantras']:
                print("🎯 STATIC MANTRAS (100% Utilization):")
                print("-" * 80)
                for mantra in report['static_mantras']:
                    print(f"  {mantra['mantra']}")
                    print(f"    Stage: {mantra['stage']}")
                    print(f"    Utilization: {mantra['utilization_percentage']:.1f}%")
                    print(f"    Reason: {mantra['static_reason']}")
                    if mantra.get('reached_static_date'):
                        print(f"    Reached Static: {mantra['reached_static_date']}")
                    print("")

            if report['active_mantras']:
                print("📊 ACTIVE MANTRAS:")
                print("-" * 80)
                for mantra in sorted(report['active_mantras'], key=lambda x: x['utilization_percentage'], reverse=True):
                    print(f"  {mantra['mantra']}")
                    print(f"    Stage: {mantra['stage']}")
                    print(f"    Utilization: {mantra['utilization_percentage']:.1f}% ({mantra['utilization_level']})")
                    print("")

            print("=" * 80)
            print("")

        else:
            # Default: show summary
            report = tracker.generate_report()
            print("\n" + "=" * 80)
            print("📈 MANTRA EVOLUTION & STATIC STATE TRACKER")
            print("=" * 80)
            print(f"Total Mantras: {report['summary']['total_mantras']}")
            print(f"Static (100%): {report['summary']['static_count']}")
            print(f"Active: {report['summary']['active_count']}")
            print(f"Best Enhancement: {report['summary']['best_enhancement']}")
            print("")
            print("Principle: All mantras become static at 100% utilization or maximum cap")
            print("")

        if args.save:
            tracker.save_tracker()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()