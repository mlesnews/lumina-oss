#!/usr/bin/env python3
"""
Workflow Continuation Engine - PEAK Standard
                    -LUM THE MODERN

Implements exponential backoff and risk-based decision making for workflow roadblocks.
Prevents stopping at "NEXT ACTION" stages by implementing automated fallbacks and
risk assessment to determine when to proceed vs wait.

Root Cause Fix: We were stopping at user action requirements instead of implementing
intelligent continuation with exponential backoff and risk assessment.

Tags: #PEAK #WORKFLOW #CONTINUATION #EXPONENTIAL_BACKOFF #RISK_ASSESSMENT @JARVIS @SCOTTY
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import time
import json
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("WorkflowContinuation")


class RiskLevel(Enum):
    """Risk levels for workflow continuation"""
    NONE = "none"  # No risk, proceed immediately
    LOW = "low"  # Low risk, proceed with caution
    MEDIUM = "medium"  # Medium risk, use fallback
    HIGH = "high"  # High risk, wait for user action
    CRITICAL = "critical"  # Critical risk, must wait


class ActionType(Enum):
    """Types of actions that can block workflows"""
    USER_INPUT = "user_input"  # Requires user input
    CONFIGURATION = "configuration"  # Requires configuration
    EXTERNAL_SERVICE = "external_service"  # Requires external service
    PERMISSION = "permission"  # Requires permission
    RESOURCE = "resource"  # Requires resource availability


@dataclass
class WorkflowAction:
    """Represents a workflow action requirement"""
    action_id: str
    action_type: ActionType
    description: str
    required: bool = True
    risk_level: RiskLevel = RiskLevel.MEDIUM
    fallback_available: bool = False
    fallback_function: Optional[Callable] = None
    max_wait_seconds: int = 300  # 5 minutes default
    exponential_backoff: bool = True
    backoff_base: float = 2.0
    max_backoff_seconds: int = 60
    attempts: int = 0
    last_attempt: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowState:
    """Workflow state tracking"""
    workflow_id: str
    current_stage: str
    actions_required: List[WorkflowAction] = field(default_factory=list)
    actions_completed: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    risk_score: float = 0.0
    can_proceed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowContinuationEngine:
    """
    Workflow Continuation Engine with Exponential Backoff

    Prevents workflow stalls by:
    1. Assessing risk of proceeding without user action
    2. Implementing exponential backoff for retries
    3. Using automated fallbacks when risk is acceptable
    4. Escalating only when risk becomes untenable
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Risk thresholds
        self.risk_thresholds = {
            RiskLevel.NONE: 0.0,
            RiskLevel.LOW: 0.2,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0
        }

        logger.info("=" * 80)
        logger.info("🔄 WORKFLOW CONTINUATION ENGINE - PEAK STANDARD")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def assess_risk(self, action: WorkflowAction, workflow_state: WorkflowState) -> RiskLevel:
        """
        Assess risk of proceeding without user action

        Factors:
        - Action type (some are safer to proceed without)
        - Fallback availability
        - Time since last attempt
        - Number of attempts
        - Workflow criticality
        """
        risk_score = 0.0

        # Base risk by action type
        type_risk = {
            ActionType.USER_INPUT: 0.6,
            ActionType.CONFIGURATION: 0.4,
            ActionType.EXTERNAL_SERVICE: 0.3,
            ActionType.PERMISSION: 0.7,
            ActionType.RESOURCE: 0.5
        }
        risk_score += type_risk.get(action.action_type, 0.5)

        # Reduce risk if fallback available
        if action.fallback_available:
            risk_score *= 0.5

        # Increase risk with attempts (exponential backoff working)
        if action.attempts > 0:
            risk_score += min(0.3, action.attempts * 0.1)

        # Reduce risk if action is not required
        if not action.required:
            risk_score *= 0.3

        # Reduce risk if enough time has passed (exponential backoff)
        if action.last_attempt:
            time_since = (datetime.now() - action.last_attempt).total_seconds()
            if time_since > action.max_wait_seconds:
                risk_score *= 0.2  # Significantly reduce risk after max wait

        # Determine risk level
        for level, threshold in sorted(self.risk_thresholds.items(), key=lambda x: x[1], reverse=True):
            if risk_score >= threshold:
                return level

        return RiskLevel.NONE

    def calculate_backoff_delay(self, action: WorkflowAction) -> float:
        """Calculate exponential backoff delay"""
        if not action.exponential_backoff:
            return 1.0

        # Exponential backoff: base^attempts
        delay = action.backoff_base ** action.attempts

        # Cap at max backoff
        delay = min(delay, action.max_backoff_seconds)

        return delay

    def should_proceed(self, action: WorkflowAction, workflow_state: WorkflowState) -> tuple[bool, str]:
        """
        Determine if workflow should proceed without user action

        Returns: (should_proceed, reason)
        """
        # Assess current risk
        current_risk = self.assess_risk(action, workflow_state)

        # If risk is critical, must wait
        if current_risk == RiskLevel.CRITICAL:
            return False, f"Critical risk level - must wait for user action: {action.description}"

        # If risk is high and no fallback, wait
        if current_risk == RiskLevel.HIGH and not action.fallback_available:
            return False, f"High risk, no fallback - waiting for user action: {action.description}"

        # If risk is medium or lower, can proceed with fallback
        if current_risk in [RiskLevel.NONE, RiskLevel.LOW, RiskLevel.MEDIUM]:
            if action.fallback_available:
                return True, f"Proceeding with fallback (risk: {current_risk.value})"
            elif not action.required:
                return True, f"Proceeding - action not required (risk: {current_risk.value})"
            elif action.attempts == 0:
                # First attempt, try fallback if available
                return True, f"First attempt - trying fallback"

        # Check if max wait time exceeded
        if action.last_attempt:
            time_since = (datetime.now() - action.last_attempt).total_seconds()
            if time_since > action.max_wait_seconds:
                return True, f"Max wait time exceeded ({time_since:.0f}s) - proceeding with best effort"

        # Default: wait
        return False, f"Waiting for user action: {action.description}"

    def execute_fallback(self, action: WorkflowAction, workflow_state: WorkflowState) -> tuple[bool, Any]:
        """
        Execute fallback function if available

        Returns: (success, result)
        """
        if not action.fallback_available or not action.fallback_function:
            return False, None

        try:
            logger.info(f"🔄 Executing fallback for: {action.description}")
            result = action.fallback_function(workflow_state)
            action.attempts += 1
            action.last_attempt = datetime.now()
            return True, result
        except Exception as e:
            logger.error(f"❌ Fallback execution failed: {e}")
            action.attempts += 1
            action.last_attempt = datetime.now()
            return False, None

    def continue_workflow(self, workflow_state: WorkflowState) -> WorkflowState:
        """
        Continue workflow by processing pending actions

        Implements exponential backoff and risk-based decision making
        """
        logger.info(f"\n🔄 Continuing workflow: {workflow_state.workflow_id}")
        logger.info(f"   Current stage: {workflow_state.current_stage}")
        logger.info(f"   Actions required: {len(workflow_state.actions_required)}")

        # Process each action
        for action in workflow_state.actions_required[:]:  # Copy list to modify
            logger.info(f"\n   Processing action: {action.action_id}")
            logger.info(f"      Type: {action.action_type.value}")
            logger.info(f"      Description: {action.description}")
            logger.info(f"      Attempts: {action.attempts}")

            # Assess risk
            risk_level = self.assess_risk(action, workflow_state)
            logger.info(f"      Risk level: {risk_level.value}")

            # Determine if should proceed
            should_proceed, reason = self.should_proceed(action, workflow_state)
            logger.info(f"      Decision: {'✅ Proceed' if should_proceed else '⏸️  Wait'}")
            logger.info(f"      Reason: {reason}")

            if should_proceed:
                # Try fallback
                if action.fallback_available:
                    success, result = self.execute_fallback(action, workflow_state)
                    if success:
                        logger.info(f"      ✅ Fallback successful")
                        workflow_state.actions_completed.append(action.action_id)
                        workflow_state.actions_required.remove(action)
                        continue
                    else:
                        logger.warning(f"      ⚠️  Fallback failed, will retry with backoff")

                # Calculate backoff delay
                if action.exponential_backoff and action.attempts > 0:
                    delay = self.calculate_backoff_delay(action)
                    logger.info(f"      ⏳ Exponential backoff: {delay:.1f}s")
                    time.sleep(min(delay, 5))  # Cap at 5s for this execution

                # Mark attempt
                action.attempts += 1
                action.last_attempt = datetime.now()

            else:
                # Risk too high, must wait
                logger.warning(f"      ⚠️  Risk level {risk_level.value} - waiting for user action")
                if risk_level == RiskLevel.CRITICAL:
                    workflow_state.can_proceed = False
                    break

        # Update workflow state
        workflow_state.last_updated = datetime.now()
        workflow_state.risk_score = max(
            self.risk_thresholds[self.assess_risk(a, workflow_state)]
            for a in workflow_state.actions_required
        ) if workflow_state.actions_required else 0.0

        # Save state
        self.save_workflow_state(workflow_state)

        return workflow_state

    def save_workflow_state(self, workflow_state: WorkflowState):
        try:
            """Save workflow state to disk"""
            state_file = self.data_dir / f"{workflow_state.workflow_id}.json"
            with open(state_file, 'w') as f:
                json.dump({
                    "workflow_id": workflow_state.workflow_id,
                    "current_stage": workflow_state.current_stage,
                    "actions_required": [
                        {
                            "action_id": a.action_id,
                            "action_type": a.action_type.value,
                            "description": a.description,
                            "required": a.required,
                            "risk_level": a.risk_level.value,
                            "fallback_available": a.fallback_available,
                            "attempts": a.attempts,
                            "last_attempt": a.last_attempt.isoformat() if a.last_attempt else None,
                            "metadata": a.metadata
                        }
                        for a in workflow_state.actions_required
                    ],
                    "actions_completed": workflow_state.actions_completed,
                    "started_at": workflow_state.started_at.isoformat(),
                    "last_updated": workflow_state.last_updated.isoformat(),
                    "risk_score": workflow_state.risk_score,
                    "can_proceed": workflow_state.can_proceed,
                    "metadata": workflow_state.metadata
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in save_workflow_state: {e}", exc_info=True)
            raise
    def create_azure_endpoint_fallback(self) -> Callable:
        """Create fallback function for Azure endpoint configuration"""
        def fallback(workflow_state: WorkflowState) -> bool:
            """
            Fallback: Try to use default/test endpoint or proceed without Azure

            This allows workflow to continue even if Azure endpoint isn't configured
            """
            logger.info("🔄 Azure endpoint fallback: Using local-only mode")

            # Check if we can proceed with local models only
            from scripts.python.lumina_azure_ai_foundry_integration import (
                LuminaAzureAIFoundryIntegration
            )

            integration = LuminaAzureAIFoundryIntegration(self.project_root)
            local_models = integration.list_available_models()

            if len(local_models) > 0:
                logger.info(f"   ✅ {len(local_models)} local models available - proceeding without Azure")
                return True
            else:
                logger.warning("   ⚠️  No local models available - Azure endpoint required")
                return False

        return fallback


def create_azure_endpoint_action(engine: WorkflowContinuationEngine) -> WorkflowAction:
    """Create Azure endpoint configuration action with fallback"""
    return WorkflowAction(
        action_id="configure_azure_endpoint",
        action_type=ActionType.CONFIGURATION,
        description="Configure Azure AI Foundry project endpoint",
        required=False,  # Not required - can proceed with local models
        risk_level=RiskLevel.LOW,
        fallback_available=True,
        fallback_function=engine.create_azure_endpoint_fallback(),
        max_wait_seconds=60,  # Wait 1 minute max
        exponential_backoff=True,
        backoff_base=2.0,
        max_backoff_seconds=30,
        metadata={
            "configurable": True,
            "script": "scripts/python/configure_azure_foundry_endpoint.py",
            "can_proceed_without": True
        }
    )


def main():
    """Example usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Continuation Engine")
    parser.add_argument("--workflow-id", type=str, default="azure_foundry_integration", help="Workflow ID")
    parser.add_argument("--stage", type=str, default="production_deployment", help="Current stage")

    args = parser.parse_args()

    engine = WorkflowContinuationEngine()

    # Create workflow state with Azure endpoint action
    workflow_state = WorkflowState(
        workflow_id=args.workflow_id,
        current_stage=args.stage,
        actions_required=[create_azure_endpoint_action(engine)]
    )

    # Continue workflow
    updated_state = engine.continue_workflow(workflow_state)

    # Report results
    logger.info("\n" + "=" * 80)
    logger.info("📊 WORKFLOW CONTINUATION RESULTS")
    logger.info("=" * 80)
    logger.info(f"   Workflow: {updated_state.workflow_id}")
    logger.info(f"   Stage: {updated_state.current_stage}")
    logger.info(f"   Can Proceed: {'✅ YES' if updated_state.can_proceed else '⏸️  NO'}")
    logger.info(f"   Risk Score: {updated_state.risk_score:.2f}")
    logger.info(f"   Actions Remaining: {len(updated_state.actions_required)}")
    logger.info(f"   Actions Completed: {len(updated_state.actions_completed)}")
    logger.info("=" * 80)

    return 0 if updated_state.can_proceed else 1


if __name__ == "__main__":


    sys.exit(main())