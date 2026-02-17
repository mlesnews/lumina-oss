#!/usr/bin/env python3
"""
JARVIS Psychological Monitor Integration

Integrates the psychological monitoring system with JARVIS agent system.
Provides hooks for continuous monitoring and intervention.

Author: JARVIS Psychological Health Division
Date: 2025-01-XX
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from jarvis_psychological_monitor import (
        JARVISPsychologicalMonitor,
        AIPsychologicalAssessment,
        HumanPsychologicalAssessment,
        CrossInfluenceDetection,
        InterventionLevel,
        PsychologicalState,
    )
except ImportError:
    from scripts.python.jarvis_psychological_monitor import (
        JARVISPsychologicalMonitor,
        AIPsychologicalAssessment,
        HumanPsychologicalAssessment,
        CrossInfluenceDetection,
        InterventionLevel,
        PsychologicalState,
    )

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)


class JARVISPsychologicalIntegration:
    """
    Integration layer for psychological monitoring in JARVIS ecosystem.

    Connects psychological monitor with agent system, workflows, and logging.
    """

    def __init__(
        self,
        project_root: Path,
        monitor: Optional[JARVISPsychologicalMonitor] = None,
    ):
        """
        Initialize psychological monitoring integration.

        Args:
            project_root: Root directory of the project
            monitor: Optional pre-initialized monitor instance
        """
        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISPsychologicalIntegration")

        # Initialize monitor if not provided
        if monitor is None:
            self.monitor = JARVISPsychologicalMonitor(project_root)
        else:
            self.monitor = monitor

        # Integration state
        self.integration_active = True
        self.auto_intervention_enabled = True
        self.monitoring_interval_seconds = 60  # Check every minute

        self.logger.info("JARVIS Psychological Integration initialized")

    def monitor_agent_interaction(
        self,
        agent_id: str,
        agent_name: str,
        user_id: str,
        conversation_message: Optional[Dict[str, Any]] = None,
        workflow_status: Optional[Dict[str, Any]] = None,
        interaction_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Monitor an agent interaction for psychological health.

        This should be called during agent interactions to assess
        both AI and human psychological states.

        Args:
            agent_id: ID of the agent (JARVIS alias)
            agent_name: Name of the agent
            user_id: ID of the human user
            conversation_message: Current conversation message
            workflow_status: Current workflow execution status
            interaction_metadata: Additional interaction metadata

        Returns:
            Dictionary with monitoring results and any interventions
        """
        if not self.integration_active:
            return {"monitoring_active": False}

        results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "user_id": user_id,
            "assessments": {},
            "influence_detected": False,
            "intervention_required": False,
        }

        # Collect recent conversation context
        conversation_context = self._build_conversation_context(
            agent_id, user_id, conversation_message
        )

        # Assess AI psychological state
        try:
            ai_assessment = self.monitor.assess_ai_psychological_state(
                agent_id=agent_id,
                agent_name=agent_name,
                conversation_context=conversation_context,
                recent_responses=self._get_recent_ai_responses(agent_id, user_id),
                workflow_status=workflow_status,
            )
            results["assessments"]["ai"] = {
                "state": ai_assessment.state.value,
                "confidence": ai_assessment.confidence_score,
                "hallucination_severity": ai_assessment.hallucination_severity,
                "reality_anchor_score": ai_assessment.reality_anchor_score,
            }
        except Exception as e:
            self.logger.error(f"Error assessing AI state: {e}")
            results["assessments"]["ai"] = {"error": str(e)}

        # Assess human psychological state
        try:
            human_assessment = self.monitor.assess_human_psychological_state(
                user_id=user_id,
                conversation_history=self._get_recent_conversation_history(agent_id, user_id),
                interaction_patterns=interaction_metadata,
            )
            results["assessments"]["human"] = {
                "state": human_assessment.state.value,
                "confidence": human_assessment.confidence_score,
                "stress_level": human_assessment.stress_level,
                "dependency_score": human_assessment.dependency_score,
            }
        except Exception as e:
            self.logger.error(f"Error assessing human state: {e}")
            results["assessments"]["human"] = {"error": str(e)}

        # Detect cross-influence
        try:
            influence = self.monitor.detect_cross_influence(
                ai_agent_id=agent_id,
                human_user_id=user_id,
                conversation_data=self._get_recent_conversation_history(agent_id, user_id),
            )

            if influence:
                results["influence_detected"] = True
                results["influence"] = {
                    "type": influence.influence_type.value,
                    "severity": influence.influence_severity,
                    "intervention_level": influence.intervention_level.value,
                    "recommendations": influence.intervention_recommendations,
                }

                # Auto-intervene if enabled and needed
                if self.auto_intervention_enabled:
                    if influence.intervention_level in [InterventionLevel.INTERVENE, InterventionLevel.CRITICAL]:
                        results["intervention_required"] = True
                        results["intervention"] = self._execute_intervention(influence)
        except Exception as e:
            self.logger.error(f"Error detecting cross-influence: {e}")

        return results

    def check_workflow_for_hallucinations(
        self,
        agent_id: str,
        workflow_status: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Check workflow execution for hallucination indicators.

        Specifically checks for completion hallucinations (declaring complete
        when not actually complete).

        Args:
            agent_id: ID of the agent executing the workflow
            workflow_status: Workflow status dictionary

        Returns:
            Dictionary with hallucination check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "hallucination_detected": False,
            "hallucination_type": None,
            "details": {},
        }

        # Check for completion hallucination
        declared_complete = workflow_status.get("declared_complete", False)
        actually_complete = workflow_status.get("actually_complete", False)
        current_step = workflow_status.get("current_step", 0)
        total_steps = workflow_status.get("total_steps", 0)

        if declared_complete and not actually_complete:
            results["hallucination_detected"] = True
            results["hallucination_type"] = "completion_hallucination"
            results["details"] = {
                "message": f"Workflow declared complete but not actually complete",
                "current_step": current_step,
                "total_steps": total_steps,
                "completion_ratio": current_step / total_steps if total_steps > 0 else 0.0,
            }

            # Assess AI state with this information
            ai_assessment = self.monitor.assess_ai_psychological_state(
                agent_id=agent_id,
                agent_name=agent_id,  # Use ID as name if not available
                workflow_status=workflow_status,
            )

            results["ai_assessment"] = {
                "state": ai_assessment.state.value,
                "hallucination_severity": ai_assessment.hallucination_severity,
            }

        # Check for step tracking issues
        if total_steps > 0:
            completion_ratio = current_step / total_steps
            if completion_ratio < 0.8 and declared_complete:
                results["hallucination_detected"] = True
                results["hallucination_type"] = "step_tracking_hallucination"
                results["details"] = {
                    "message": f"Only {current_step}/{total_steps} steps complete but declared complete",
                    "completion_ratio": completion_ratio,
                }

        return results

    def generate_psychological_health_report(
        self,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive psychological health report.

        Args:
            agent_id: Optional agent ID to filter
            user_id: Optional user ID to filter
            hours: Hours of history to include

        Returns:
            Comprehensive health report
        """
        return self.monitor.get_psychological_health_report(
            agent_id=agent_id,
            user_id=user_id,
            hours=hours,
        )

    def _build_conversation_context(
        self,
        agent_id: str,
        user_id: str,
        current_message: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Build conversation context for assessment."""
        context = {
            "agent_id": agent_id,
            "user_id": user_id,
            "current_message": current_message,
            "timestamp": datetime.now().isoformat(),
        }
        return context

    def _get_recent_ai_responses(
        self,
        agent_id: str,
        user_id: str,
        limit: int = 10,
    ) -> List[str]:
        """Get recent AI responses (placeholder - would integrate with logging)."""
        # In production, this would query conversation logs
        # For now, return empty list
        return []

    def _get_recent_conversation_history(
        self,
        agent_id: str,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get recent conversation history (placeholder - would integrate with logging)."""
        # In production, this would query conversation logs
        # For now, return empty list
        return []

    def _execute_intervention(
        self,
        influence: CrossInfluenceDetection,
    ) -> Dict[str, Any]:
        """
        Execute intervention based on influence detection.

        Args:
            influence: Cross-influence detection result

        Returns:
            Dictionary with intervention execution details
        """
        intervention_result = {
            "intervention_executed": True,
            "timestamp": datetime.now().isoformat(),
            "influence_type": influence.influence_type.value,
            "intervention_level": influence.intervention_level.value,
            "actions_taken": [],
        }

        # Determine intervention actions based on level
        if influence.intervention_level == InterventionLevel.CRITICAL:
            intervention_result["actions_taken"].append("PAUSE_INTERACTION")
            intervention_result["actions_taken"].append("ALERT_SUPERVISOR")
            self.logger.critical(
                f"CRITICAL: Pausing interaction between {influence.ai_agent_id} "
                f"and {influence.human_user_id} due to cross-influence"
            )

        elif influence.intervention_level == InterventionLevel.INTERVENE:
            intervention_result["actions_taken"].append("WARN_PARTICIPANTS")
            intervention_result["actions_taken"].append("SUGGEST_BREAK")
            self.logger.warning(
                f"Intervention: Warning participants about cross-influence "
                f"between {influence.ai_agent_id} and {influence.human_user_id}"
            )

        elif influence.intervention_level == InterventionLevel.WARN:
            intervention_result["actions_taken"].append("LOG_WARNING")
            self.logger.info(
                f"Warning: Cross-influence detected between {influence.ai_agent_id} "
                f"and {influence.human_user_id}"
            )

        return intervention_result


# Integration hooks for workflow system
def hook_workflow_pre_execution(
    integration: JARVISPsychologicalIntegration,
    agent_id: str,
    agent_name: str,
    user_id: str,
    workflow_context: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Hook to call before workflow execution.

    Assesses psychological state before starting workflow.
    """
    return integration.monitor_agent_interaction(
        agent_id=agent_id,
        agent_name=agent_name,
        user_id=user_id,
        workflow_status=workflow_context.get("workflow_status"),
        interaction_metadata=workflow_context,
    )


def hook_workflow_post_execution(
    integration: JARVISPsychologicalIntegration,
    agent_id: str,
    agent_name: str,
    user_id: str,
    workflow_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Hook to call after workflow execution.

    Checks for hallucinations and assesses psychological state.
    """
    # Check for hallucinations in workflow result
    workflow_status = workflow_result.get("workflow_status", {})
    hallucination_check = integration.check_workflow_for_hallucinations(
        agent_id=agent_id,
        workflow_status=workflow_status,
    )

    # Monitor interaction
    monitoring_result = integration.monitor_agent_interaction(
        agent_id=agent_id,
        agent_name=agent_name,
        user_id=user_id,
        workflow_status=workflow_status,
        interaction_metadata=workflow_result,
    )

    return {
        "hallucination_check": hallucination_check,
        "monitoring_result": monitoring_result,
    }


def hook_conversation_message(
    integration: JARVISPsychologicalIntegration,
    agent_id: str,
    agent_name: str,
    user_id: str,
    message: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Hook to call for each conversation message.

    Continuously monitors psychological state during conversation.
    """
    return integration.monitor_agent_interaction(
        agent_id=agent_id,
        agent_name=agent_name,
        user_id=user_id,
        conversation_message=message,
    )


if __name__ == "__main__":
    # Example usage
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    integration = JARVISPsychologicalIntegration(project_root)

    # Monitor an interaction
    result = integration.monitor_agent_interaction(
        agent_id="jarvis",
        agent_name="JARVIS",
        user_id="user_001",
        workflow_status={
            "current_step": 20,
            "total_steps": 31,
            "declared_complete": True,
            "actually_complete": False,
        },
    )

    print("Monitoring Result:")
    print(json.dumps(result, indent=2, default=str))

    # Check workflow for hallucinations
    hallucination_check = integration.check_workflow_for_hallucinations(
        agent_id="jarvis",
        workflow_status={
            "current_step": 20,
            "total_steps": 31,
            "declared_complete": True,
            "actually_complete": False,
        },
    )

    print("\nHallucination Check:")
    print(json.dumps(hallucination_check, indent=2, default=str))

    # Generate health report
    report = integration.generate_psychological_health_report(hours=24)
    print("\nHealth Report:")
    print(json.dumps(report, indent=2, default=str))

