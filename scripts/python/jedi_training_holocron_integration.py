#!/usr/bin/env python3
"""
Jedi Temple Training Holocron Integration

Integrates workflow analytics/metrics into Jedi Temple training holocron.
Groups Master-Padawan educational units with workflow learning.

Tags: #JEDI_TEMPLE #MASTER_PADAWAN #WORKFLOW_ANALYTICS #HOLOCRON @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

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

logger = get_logger("JediTrainingHolocron")


class JediTrainingHolocron:
    """
    Jedi Temple Training Holocron

    Master-Padawan educational units with workflow analytics/metrics.
    Groups related information together in centralized storage.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Use centralized storage
        try:
            from centralized_holocron_storage import CentralizedHolocronStorage
            self.storage = CentralizedHolocronStorage(project_root=project_root)
        except ImportError:
            logger.error("❌ Centralized storage not available")
            self.storage = None
            return

        # Category for grouping
        self.category = "jedi_training"

        logger.info("=" * 80)
        logger.info("⚔️  JEDI TEMPLE TRAINING HOLOCRON")
        logger.info("=" * 80)
        logger.info("   Master-Padawan Educational Units")
        logger.info("   Workflow Analytics & Metrics")
        logger.info("   Centralized Storage")
        logger.info("=" * 80)

    def add_workflow_analytics(
        self,
        session_id: str,
        analytics: Dict[str, Any],
        metrics: Dict[str, Any]
    ):
        """
        Add workflow analytics and metrics to Jedi training holocron

        Groups with Master-Padawan educational units.
        """
        if not self.storage:
            logger.error("❌ Storage not available")
            return

        # Load existing training data
        training_data = self.storage.load_holocron_entry(
            self.category,
            "master_padawan_training"
        ) or {
            "master_padawan_units": [],
            "workflow_analytics": [],
            "metrics_history": []
        }

        # Add workflow analytics entry
        analytics_entry = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "analytics": analytics,
            "metrics": metrics,
            "type": "workflow_learning"
        }

        training_data["workflow_analytics"].append(analytics_entry)

        # Keep only last 100 entries (prevent bloat)
        if len(training_data["workflow_analytics"]) > 100:
            training_data["workflow_analytics"] = training_data["workflow_analytics"][-100:]

        # Save to centralized storage
        self.storage.save_holocron_entry(
            category=self.category,
            entry_name="master_padawan_training",
            data=training_data,
            update_index=True
        )

        logger.info(f"📊 Added workflow analytics for session: {session_id}")

    def add_master_padawan_unit(
        self,
        unit_id: str,
        unit_name: str,
        description: str,
        master_notes: str = "",
        padawan_notes: str = "",
        workflow_patterns: List[Dict[str, Any]] = None
    ):
        """
        Add Master-Padawan educational unit

        Groups with workflow analytics.
        """
        if not self.storage:
            logger.error("❌ Storage not available")
            return

        # Load existing training data
        training_data = self.storage.load_holocron_entry(
            self.category,
            "master_padawan_training"
        ) or {
            "master_padawan_units": [],
            "workflow_analytics": [],
            "metrics_history": []
        }

        # Add educational unit
        unit = {
            "unit_id": unit_id,
            "unit_name": unit_name,
            "description": description,
            "master_notes": master_notes,
            "padawan_notes": padawan_notes,
            "workflow_patterns": workflow_patterns or [],
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        # Check if unit exists, update if so
        existing_units = training_data.get("master_padawan_units", [])
        unit_index = next(
            (i for i, u in enumerate(existing_units) if u.get("unit_id") == unit_id),
            None
        )

        if unit_index is not None:
            existing_units[unit_index] = unit
            logger.info(f"📝 Updated Master-Padawan unit: {unit_name}")
        else:
            existing_units.append(unit)
            logger.info(f"➕ Added Master-Padawan unit: {unit_name}")

        training_data["master_padawan_units"] = existing_units

        # Save to centralized storage
        self.storage.save_holocron_entry(
            category=self.category,
            entry_name="master_padawan_training",
            data=training_data,
            update_index=True
        )

    def get_training_data(self) -> Optional[Dict[str, Any]]:
        """Get all training data (Master-Padawan units + workflow analytics)"""
        if not self.storage:
            return None

        return self.storage.load_holocron_entry(
            self.category,
            "master_padawan_training"
        )

    def integrate_workflow_tracker_analytics(self, workflow_tracker):
        """
        Integrate workflow tracker analytics into Jedi training holocron

        Automatically syncs workflow analytics/metrics.
        """
        if not self.storage or not workflow_tracker:
            return

        # Get workflow insights
        insights = workflow_tracker.get_workflow_insights()

        # Get recent events
        recent_events = workflow_tracker.focus_change_events[-10:]  # Last 10 events

        # Prepare analytics
        analytics = {
            "productivity_score": insights.get("productivity_score", 100.0),
            "total_interruptions": insights.get("total_interruptions", 0),
            "critical_interruptions": insights.get("critical_interruptions", 0),
            "recovery_rate": insights.get("recovery_rate", 0.0),
            "patterns_learned": insights.get("patterns_learned", 0)
        }

        metrics = {
            "focus_changes": len(recent_events),
            "average_recovery_time": insights.get("average_recovery_time", 0.0),
            "is_in_conversation": insights.get("is_in_conversation", True),
            "recent_events": [e.to_dict() for e in recent_events]
        }

        # Add to holocron
        session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.add_workflow_analytics(session_id, analytics, metrics)

        logger.info("🔄 Integrated workflow tracker analytics into Jedi training holocron")


def main():
    """Main entry point"""
    holocron = JediTrainingHolocron()

    # Example: Add workflow analytics
    from collaborative_workflow_tracker import CollaborativeWorkflowTracker
    tracker = CollaborativeWorkflowTracker()

    # Integrate analytics
    holocron.integrate_workflow_tracker_analytics(tracker)

    print("✅ Jedi training holocron integration complete")


if __name__ == "__main__":


    main()