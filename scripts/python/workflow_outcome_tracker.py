#!/usr/bin/env python3
"""
Workflow Outcome Tracker

Tracks workflow outcomes and integrates with Lumina Data Mining Feedback Loop.
Records outcomes for all workflow executions to enable OTS (Outcomes of Intent) analysis.

@WORKFLOW @OUTCOME_TRACKING @LUMINA @FEEDBACK_LOOP
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowOutcomeTracker")


@dataclass
class WorkflowOutcome:
    """Outcome of a workflow execution"""
    outcome_id: str
    workflow_name: str
    execution_id: str
    intent_id: Optional[str] = None  # Links to original intent
    success: bool = False
    outcome_type: str = "unknown"  # success, failure, partial, deviation
    outcome_text: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    workflow_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class WorkflowOutcomeTracker:
    """
    Tracks workflow outcomes for integration with Lumina Data Mining Feedback Loop

    Automatically records outcomes for all workflow executions to enable:
    - OTS (Outcomes of Intent) analysis
    - Progressive scaling measurement
    - Feedback loop improvements
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("WorkflowOutcomeTracker")

        # Outcome storage
        self.outcomes_dir = self.project_root / "data" / "workflow_outcomes"
        self.outcomes_dir.mkdir(parents=True, exist_ok=True)

        # Integration with data mining
        try:
            from lumina_data_mining_feedback_loop import LuminaDataMiner
            self.data_miner = LuminaDataMiner(project_root)
        except ImportError:
            self.data_miner = None
            self.logger.warning("LuminaDataMiner not available - outcomes will be saved but not integrated")

    def track_outcome(self, 
                     workflow_name: str,
                     execution_id: str,
                     success: bool,
                     outcome_text: str = "",
                     intent_id: Optional[str] = None,
                     metrics: Optional[Dict[str, float]] = None,
                     duration_seconds: float = 0.0,
                     workflow_data: Optional[Dict[str, Any]] = None) -> WorkflowOutcome:
        """
        Track a workflow outcome

        Args:
            workflow_name: Name of the workflow
            execution_id: Execution ID
            success: Whether workflow succeeded
            outcome_text: Description of outcome
            intent_id: ID of original intent (if linked to @ASK)
            metrics: Performance metrics
            duration_seconds: Execution duration
            workflow_data: Full workflow execution data

        Returns:
            WorkflowOutcome object
        """
        # Determine outcome type
        if success:
            outcome_type = "success"
        else:
            outcome_type = "failure"

        # Extract intent_id from workflow_data if not provided
        if not intent_id and workflow_data:
            intent_id = workflow_data.get('intent_id') or workflow_data.get('ask_id')

        outcome = WorkflowOutcome(
            outcome_id=f"workflow_{execution_id}_{datetime.now().timestamp()}",
            workflow_name=workflow_name,
            execution_id=execution_id,
            intent_id=intent_id,
            success=success,
            outcome_type=outcome_type,
            outcome_text=outcome_text,
            metrics=metrics or {},
            duration_seconds=duration_seconds,
            timestamp=datetime.now(),
            workflow_data=workflow_data or {}
        )

        # Save outcome
        self._save_outcome(outcome)

        # Integrate with data miner if available
        if self.data_miner:
            try:
                self._integrate_with_data_miner(outcome)
            except Exception as e:
                self.logger.warning(f"Could not integrate with data miner: {e}")

        self.logger.info(f"✅ Tracked outcome: {workflow_name}/{execution_id} - {outcome_type}")
        return outcome

    def _save_outcome(self, outcome: WorkflowOutcome) -> None:
        """Save outcome to disk"""
        outcome_file = self.outcomes_dir / f"{outcome.outcome_id}.json"

        try:
            with open(outcome_file, 'w') as f:
                json.dump(outcome.to_dict(), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving outcome: {e}")

    def _integrate_with_data_miner(self, outcome: WorkflowOutcome) -> None:
        """Integrate outcome with Lumina Data Mining system"""
        if not self.data_miner:
            return

        # Convert to Outcome format expected by data miner
        from lumina_data_mining_feedback_loop import Outcome

        data_miner_outcome = Outcome(
            outcome_id=outcome.outcome_id,
            intent_id=outcome.intent_id or "unknown",
            outcome_type=outcome.outcome_type,
            outcome_text=outcome.outcome_text or str(outcome.workflow_data),
            metrics=outcome.metrics,
            timestamp=outcome.timestamp,
            implementation_details={
                'workflow_name': outcome.workflow_name,
                'execution_id': outcome.execution_id,
                'duration_seconds': outcome.duration_seconds,
                **outcome.workflow_data
            }
        )

        # Add to data miner outcomes
        self.data_miner.outcomes.append(data_miner_outcome)
        self.data_miner._save_mined_data()

        # Try to create/update OTS entries
        if outcome.intent_id and outcome.intent_id != "unknown":
            try:
                # Find matching intent
                matching_intents = [i for i in self.data_miner.intents if i.intent_id == outcome.intent_id]
                if matching_intents:
                    # Create OTS entry
                    from lumina_data_mining_feedback_loop import OutcomeOfIntent, Intent
                    intent = matching_intents[0]

                    alignment_score = self.data_miner._calculate_alignment_score(intent, data_miner_outcome)
                    deviation_analysis = self.data_miner._analyze_deviation(intent, data_miner_outcome)
                    scaling_factor = self.data_miner._calculate_scaling_factor(intent, data_miner_outcome)
                    improvement_metrics = self.data_miner._calculate_improvement_metrics(intent, data_miner_outcome)

                    ots = OutcomeOfIntent(
                        ots_id=f"ots_{outcome.outcome_id}_{datetime.now().timestamp()}",
                        intent=intent,
                        outcome=data_miner_outcome,
                        alignment_score=alignment_score,
                        deviation_analysis=deviation_analysis,
                        scaling_factor=scaling_factor,
                        improvement_metrics=improvement_metrics
                    )

                    # Add if not already exists
                    existing = [o for o in self.data_miner.ots_list 
                               if o.intent.intent_id == intent.intent_id and o.outcome and o.outcome.outcome_id == data_miner_outcome.outcome_id]
                    if not existing:
                        self.data_miner.ots_list.append(ots)
                        self.data_miner._save_mined_data()
                        self.logger.info(f"✅ Created OTS entry for {intent.intent_id}")
            except Exception as e:
                self.logger.warning(f"Could not create OTS entry: {e}")

    def track_from_workflow_result(self, workflow_result: Dict[str, Any]) -> Optional[WorkflowOutcome]:
        """
        Track outcome from a workflow execution result dictionary

        Args:
            workflow_result: Result dictionary from workflow execution

        Returns:
            WorkflowOutcome if successfully tracked
        """
        try:
            workflow_name = workflow_result.get('workflow_name', workflow_result.get('name', 'unknown'))
            execution_id = workflow_result.get('execution_id', workflow_result.get('id', f"exec_{datetime.now().timestamp()}"))
            success = workflow_result.get('success', workflow_result.get('status') == 'completed')

            # Extract outcome text
            outcome_text = (
                workflow_result.get('outcome_text') or
                workflow_result.get('result') or
                workflow_result.get('message') or
                str(workflow_result.get('final_status', 'completed' if success else 'failed'))
            )

            # Extract metrics
            metrics = workflow_result.get('metrics', {})
            if 'duration' in workflow_result:
                metrics['duration'] = workflow_result['duration']
            if 'execution_time' in workflow_result:
                metrics['execution_time'] = workflow_result['execution_time']

            # Extract duration
            duration = workflow_result.get('duration_seconds') or workflow_result.get('execution_time', 0.0)

            return self.track_outcome(
                workflow_name=workflow_name,
                execution_id=execution_id,
                success=success,
                outcome_text=outcome_text,
                intent_id=workflow_result.get('intent_id'),
                metrics=metrics,
                duration_seconds=duration,
                workflow_data=workflow_result
            )
        except Exception as e:
            self.logger.error(f"Error tracking workflow result: {e}")
            return None


# Global instance for easy access
_global_tracker: Optional[WorkflowOutcomeTracker] = None

def get_outcome_tracker(project_root: Optional[Path] = None) -> WorkflowOutcomeTracker:
    """Get or create global outcome tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = WorkflowOutcomeTracker(project_root)
    return _global_tracker
