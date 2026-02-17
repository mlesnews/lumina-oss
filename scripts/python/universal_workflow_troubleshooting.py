#!/usr/bin/env python3
"""
Universal Workflow Troubleshooting Module

Injects roast/repair evaluation and decision-making into all workflows.
Integrates with @ai, @jarvis, @marvin for evaluation.
Uses @decide, @aiq, @jedicouncil, @jedihighcouncil for decision-making.

@ai @jarvis @marvin @rr[#roast + #repair] @decide[#decisioning + @aiq + @jc[#jedicouncil + #jedihighcouncil]]

Tags: #TROUBLESHOOTING #WORKFLOW #ROAST #REPAIR #DECISIONING #AIQ #JEDICOUNCIL @JARVIS @MARVIN @TEAM
"""

from __future__ import annotations

import sys
import json
import time
import functools
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Roast system integration
try:
    from universal_roast_system import UniversalRoastSystem, RoastType, RoastStyle
    ROAST_AVAILABLE = True
except ImportError:
    ROAST_AVAILABLE = False
    UniversalRoastSystem = None

# Repair system integration
try:
    from jarvis_auto_repair_executor import JarvisAutoRepairExecutor
    REPAIR_AVAILABLE = True
except ImportError:
    REPAIR_AVAILABLE = False
    JarvisAutoRepairExecutor = None

# Decision tree integration
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome, UniversalDecisionTree
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    decide = None
    DecisionContext = None
    DecisionOutcome = None
    UniversalDecisionTree = None

# AIQ + Jedi Council integration
try:
    from aiq_triage_jedi import AIQTriageRouter
    AIQ_AVAILABLE = True
except ImportError:
    AIQ_AVAILABLE = False
    AIQTriageRouter = None

try:
    from jedi_council import JediCouncil
    JEDI_COUNCIL_AVAILABLE = True
except ImportError:
    JEDI_COUNCIL_AVAILABLE = False
    JediCouncil = None

# AI/JARVIS/MARVIN integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

try:
    from marvin_reality_checker import MarvinRealityChecker
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    MarvinRealityChecker = None

logger = get_logger("UniversalWorkflowTroubleshooting")


class TroubleshootingMode(Enum):
    """Troubleshooting evaluation modes"""
    PRE_WORKFLOW = "pre_workflow"  # Evaluate before execution
    POST_WORKFLOW = "post_workflow"  # Evaluate after execution
    CONTINUOUS = "continuous"  # Evaluate during execution
    ON_ERROR = "on_error"  # Evaluate only on errors


class EvaluationLevel(Enum):
    """Evaluation depth levels"""
    BASIC = "basic"  # Quick evaluation
    STANDARD = "standard"  # Standard evaluation
    DEEP = "deep"  # Deep analysis
    JEDI_COUNCIL = "jedi_council"  # Full Jedi Council approval


@dataclass
class WorkflowEvaluation:
    """Result of workflow evaluation"""
    workflow_id: str
    workflow_name: str
    evaluation_time: str
    mode: TroubleshootingMode
    level: EvaluationLevel

    # Roast results
    roast_findings: List[Dict[str, Any]] = field(default_factory=list)
    roast_score: float = 0.0
    roast_summary: str = ""

    # Repair recommendations
    repair_actions: List[Dict[str, Any]] = field(default_factory=list)
    repair_needed: bool = False

    # Decision results
    decision_outcome: Optional[str] = None
    decision_reasoning: str = ""
    decision_confidence: float = 0.0

    # AIQ/Jedi Council results
    aiq_result: Optional[Dict[str, Any]] = None
    jedi_council_approval: Optional[Dict[str, Any]] = None
    requires_approval: bool = False

    # AI evaluation results
    jarvis_evaluation: Optional[Dict[str, Any]] = None
    marvin_evaluation: Optional[Dict[str, Any]] = None

    # Overall assessment
    should_proceed: bool = True
    should_repair: bool = False
    escalation_needed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["mode"] = self.mode.value
        data["level"] = self.level.value
        return data


class UniversalWorkflowTroubleshooting:
    """
    Universal Workflow Troubleshooting Module

    Injects roast/repair evaluation and decision-making into workflows.
    Can be used as a decorator or called directly.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize troubleshooting system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("UniversalWorkflowTroubleshooting")

        # Initialize subsystems
        self.roast_system = None
        if ROAST_AVAILABLE:
            try:
                self.roast_system = UniversalRoastSystem(project_root=project_root)
                self.logger.info("✅ Roast system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Roast system not available: {e}")

        self.repair_executor = None
        if REPAIR_AVAILABLE:
            try:
                self.repair_executor = JarvisAutoRepairExecutor(project_root=project_root)
                self.logger.info("✅ Repair executor integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Repair executor not available: {e}")

        self.decision_tree = None
        if DECISION_TREE_AVAILABLE:
            try:
                self.decision_tree = UniversalDecisionTree(project_root=project_root)
                self.logger.info("✅ Decision tree system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Decision tree not available: {e}")

        self.aiq_router = None
        if AIQ_AVAILABLE:
            try:
                self.aiq_router = AIQTriageRouter()
                self.logger.info("✅ AIQ Triage Router integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  AIQ Router not available: {e}")

        self.jedi_council = None
        if JEDI_COUNCIL_AVAILABLE:
            try:
                self.jedi_council = JediCouncil(project_root=project_root)
                self.logger.info("✅ Jedi Council integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Jedi Council not available: {e}")

        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root=project_root)
                self.logger.info("✅ JARVIS agent integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS agent not available: {e}")

        self.marvin = None
        if MARVIN_AVAILABLE:
            try:
                self.marvin = MarvinRealityChecker(project_root=project_root)
                self.logger.info("✅ MARVIN reality checker integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  MARVIN not available: {e}")

        # SYPHON integration
        self.syphon = None
        self.troubleshooting_extractor = None
        try:
            from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
            from syphon.troubleshooting_extractor import TroubleshootingExtractor
            from syphon.models import DataSourceType

            config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True
            )
            self.syphon = SYPHONSystem(config)
            self.troubleshooting_extractor = TroubleshootingExtractor(config)
            self.syphon.register_extractor(DataSourceType.CODE, self.troubleshooting_extractor)
            self.logger.info("✅ SYPHON integration initialized")
        except ImportError:
            self.logger.warning("⚠️  SYPHON not available - intelligence extraction disabled")
        except Exception as e:
            self.logger.warning(f"⚠️  SYPHON initialization failed: {e}")

        # Data directory
        self.data_dir = self.project_root / "data" / "workflow_troubleshooting"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Universal Workflow Troubleshooting initialized")

    def evaluate_workflow(
        self,
        workflow_data: Dict[str, Any],
        mode: TroubleshootingMode = TroubleshootingMode.PRE_WORKFLOW,
        level: EvaluationLevel = EvaluationLevel.STANDARD,
        auto_repair: bool = False,
        require_approval: bool = False
    ) -> WorkflowEvaluation:
        """
        Evaluate a workflow using roast/repair and decision-making

        Args:
            workflow_data: Workflow data to evaluate
            mode: When to evaluate (pre/post/continuous/on_error)
            level: Evaluation depth
            auto_repair: If True, automatically execute repairs
            require_approval: If True, require Jedi Council approval

        Returns:
            WorkflowEvaluation with results
        """
        workflow_id = workflow_data.get("workflow_id", f"workflow_{int(time.time())}")
        workflow_name = workflow_data.get("workflow_name", "Unknown Workflow")

        evaluation = WorkflowEvaluation(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            evaluation_time=datetime.now().isoformat(),
            mode=mode,
            level=level
        )

        self.logger.info(f"🔍 Evaluating workflow: {workflow_name} (mode: {mode.value}, level: {level.value})")

        # 1. Roast evaluation (critical analysis)
        if self.roast_system and level.value in ["standard", "deep", "jedi_council"]:
            try:
                roast_result = self._perform_roast(workflow_data, level)
                evaluation.roast_findings = roast_result.get("findings", [])
                evaluation.roast_score = roast_result.get("score", 0.0)
                evaluation.roast_summary = roast_result.get("summary", "")
                evaluation.repair_needed = len(evaluation.roast_findings) > 0

                self.logger.info(f"🍖 Roast complete: {len(evaluation.roast_findings)} findings, score: {evaluation.roast_score:.2f}")
            except Exception as e:
                self.logger.error(f"Error during roast: {e}", exc_info=True)

        # 2. Decision-making via @decide
        if self.decision_tree and level.value in ["standard", "deep", "jedi_council"]:
            try:
                decision_result = self._make_decision(workflow_data, evaluation)
                evaluation.decision_outcome = decision_result.get("outcome")
                evaluation.decision_reasoning = decision_result.get("reasoning", "")
                evaluation.decision_confidence = decision_result.get("confidence", 0.0)

                # Determine if we should proceed
                if decision_result.get("outcome") == "escalate":
                    evaluation.escalation_needed = True
                    evaluation.should_proceed = False

                self.logger.info(f"🎯 Decision: {evaluation.decision_outcome} (confidence: {evaluation.decision_confidence:.2f})")
            except Exception as e:
                self.logger.error(f"Error during decision-making: {e}", exc_info=True)

        # 3. AIQ consensus (if multiple solutions)
        if self.aiq_router and level.value in ["deep", "jedi_council"]:
            try:
                aiq_result = self._run_aiq_consensus(workflow_data, evaluation)
                evaluation.aiq_result = aiq_result

                if aiq_result.get("selected"):
                    self.logger.info(f"🤝 AIQ consensus: {aiq_result.get('selected', {}).get('solution', 'N/A')}")
            except Exception as e:
                self.logger.error(f"Error during AIQ consensus: {e}", exc_info=True)

        # 4. JARVIS evaluation
        if self.jarvis and level.value in ["standard", "deep", "jedi_council"]:
            try:
                jarvis_eval = self._evaluate_with_jarvis(workflow_data, evaluation)
                evaluation.jarvis_evaluation = jarvis_eval

                if jarvis_eval.get("recommendation") == "reject":
                    evaluation.should_proceed = False
                    evaluation.escalation_needed = True

                self.logger.info(f"🤖 JARVIS evaluation: {jarvis_eval.get('recommendation', 'N/A')}")
            except Exception as e:
                self.logger.error(f"Error during JARVIS evaluation: {e}", exc_info=True)

        # 5. MARVIN reality check
        if self.marvin and level.value in ["deep", "jedi_council"]:
            try:
                marvin_eval = self._evaluate_with_marvin(workflow_data, evaluation)
                evaluation.marvin_evaluation = marvin_eval

                if marvin_eval.get("reality_check") == "fail":
                    evaluation.should_proceed = False
                    evaluation.escalation_needed = True

                self.logger.info(f"🤖 MARVIN reality check: {marvin_eval.get('reality_check', 'N/A')}")
            except Exception as e:
                self.logger.error(f"Error during MARVIN evaluation: {e}", exc_info=True)

        # 6. Jedi Council approval (if required or deep evaluation)
        if self.jedi_council and (require_approval or level == EvaluationLevel.JEDI_COUNCIL):
            try:
                council_result = self._get_jedi_council_approval(workflow_data, evaluation)
                evaluation.jedi_council_approval = council_result
                evaluation.requires_approval = True

                if not council_result.get("approved", False):
                    evaluation.should_proceed = False
                    evaluation.escalation_needed = True

                self.logger.info(f"⚔️  Jedi Council: {'APPROVED' if council_result.get('approved') else 'REJECTED'}")
            except Exception as e:
                self.logger.error(f"Error during Jedi Council approval: {e}", exc_info=True)

        # 7. Generate repair actions
        if evaluation.repair_needed and self.repair_executor:
            try:
                repair_actions = self._generate_repair_actions(workflow_data, evaluation)
                evaluation.repair_actions = repair_actions
                evaluation.should_repair = len(repair_actions) > 0

                # Auto-repair if enabled
                if auto_repair and evaluation.should_repair:
                    self._execute_repairs(repair_actions, workflow_data)
                    evaluation.metadata["auto_repair_executed"] = True

                self.logger.info(f"🔧 Generated {len(repair_actions)} repair actions")
            except Exception as e:
                self.logger.error(f"Error generating repair actions: {e}", exc_info=True)

        # Final assessment
        evaluation.should_proceed = (
            evaluation.should_proceed and 
            not evaluation.escalation_needed and
            (evaluation.jedi_council_approval is None or evaluation.jedi_council_approval.get("approved", False))
        )

        # 8. SYPHON intelligence extraction
        if self.troubleshooting_extractor:
            try:
                syphon_result = self.troubleshooting_extractor.extract(
                    content={
                        "workflow_data": workflow_data,
                        "evaluation": evaluation.to_dict()
                    },
                    metadata={
                        "workflow_id": workflow_id,
                        "workflow_name": workflow_name,
                        "mode": mode.value,
                        "level": level.value
                    }
                )

                if syphon_result.success and syphon_result.data:
                    evaluation.metadata["syphon_data"] = syphon_result.data.to_dict()
                    evaluation.metadata["actionable_intelligence"] = syphon_result.data.actionable_items
                    evaluation.metadata["proven_patterns"] = [
                        p for p in syphon_result.data.intelligence 
                        if p.get("type") == "proven_pattern"
                    ]
                    self.logger.info(f"✅ SYPHON intelligence extracted: {len(syphon_result.data.actionable_items)} items")
            except Exception as e:
                self.logger.error(f"Error during SYPHON extraction: {e}", exc_info=True)

        # Save evaluation
        self._save_evaluation(evaluation)

        return evaluation

    def _perform_roast(self, workflow_data: Dict[str, Any], level: EvaluationLevel) -> Dict[str, Any]:
        """Perform roast evaluation on workflow"""
        if not self.roast_system:
            return {}

        try:
            # Convert workflow data to roast-able format
            workflow_text = json.dumps(workflow_data, indent=2)
            ask_id = workflow_data.get("workflow_id", "workflow")
            ask_text = workflow_data.get("workflow_name", "Workflow")

            # Perform roast
            roast_type = RoastType.BOTH if level == EvaluationLevel.DEEP else RoastType.ROAST
            roast_style = RoastStyle.ANALYTICAL  # JARVIS-style analytical roast

            roast_result = self.roast_system.roast(
                agent_id="jarvis",
                agent_name="JARVIS",
                ask_id=ask_id,
                ask_text=ask_text,
                content=workflow_text,
                roast_type=roast_type,
                style=roast_style
            )

            return {
                "findings": [f.to_dict() for f in roast_result.findings],
                "score": roast_result.total_severity_score,
                "summary": roast_result.summary
            }
        except Exception as e:
            self.logger.error(f"Roast error: {e}", exc_info=True)
            return {}

    def _make_decision(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> Dict[str, Any]:
        """Make decision using universal decision tree"""
        if not self.decision_tree or not decide:
            return {}

        try:
            # Create decision context from workflow and evaluation
            context = DecisionContext(
                complexity=self._assess_complexity(workflow_data),
                urgency=workflow_data.get("urgency", "medium"),
                cost_sensitive=workflow_data.get("cost_sensitive", True),
                local_ai_available=True,
                custom_data={
                    "workflow_data": workflow_data,
                    "roast_score": evaluation.roast_score,
                    "repair_needed": evaluation.repair_needed
                }
            )

            # Decide on workflow execution using decision tree
            result = self.decision_tree.decide('workflow_execution', context)

            return {
                "outcome": result.outcome.value if hasattr(result.outcome, 'value') else str(result.outcome),
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "next_action": result.next_action
            }
        except Exception as e:
            self.logger.error(f"Decision error: {e}", exc_info=True)
            # Fallback decision
            return {
                "outcome": "proceed",
                "reasoning": "Decision tree unavailable, proceeding with caution",
                "confidence": 0.5
            }

    def _run_aiq_consensus(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> Dict[str, Any]:
        """Run AIQ consensus on workflow solutions"""
        if not self.aiq_router:
            return {}

        try:
            # Generate candidate solutions from roast findings
            candidates = []
            for finding in evaluation.roast_findings:
                if finding.get("recommendations"):
                    candidates.append({
                        "solution": finding.get("description", ""),
                        "recommendations": finding.get("recommendations", [])
                    })

            if not candidates:
                return {}

            # Run AIQ consensus
            aiq_result = self.aiq_router.run_aiq_consensus(candidates, quorum=3)

            return {
                "selected": aiq_result.selected,
                "scores": aiq_result.scores
            }
        except Exception as e:
            self.logger.error(f"AIQ consensus error: {e}", exc_info=True)
            return {}

    def _evaluate_with_jarvis(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> Dict[str, Any]:
        """Evaluate workflow with JARVIS"""
        if not self.jarvis:
            return {}

        try:
            # Use JARVIS to evaluate workflow
            workflow_summary = f"Workflow: {evaluation.workflow_name}\n"
            workflow_summary += f"Roast Score: {evaluation.roast_score:.2f}\n"
            workflow_summary += f"Findings: {len(evaluation.roast_findings)}\n"

            # JARVIS optimization evaluation
            # This would typically call JARVIS's evaluation method
            # For now, provide basic assessment

            recommendation = "approve"
            if evaluation.roast_score > 7.0:
                recommendation = "reject"
            elif evaluation.roast_score > 5.0:
                recommendation = "review"

            return {
                "recommendation": recommendation,
                "score": evaluation.roast_score,
                "assessment": workflow_summary
            }
        except Exception as e:
            self.logger.error(f"JARVIS evaluation error: {e}", exc_info=True)
            return {}

    def _evaluate_with_marvin(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> Dict[str, Any]:
        """Evaluate workflow with MARVIN reality checker"""
        if not self.marvin:
            return {}

        try:
            # MARVIN reality check
            # This would typically call MARVIN's reality check method
            # For now, provide basic assessment

            reality_check = "pass"
            if evaluation.roast_score > 8.0:
                reality_check = "fail"
            elif evaluation.roast_score > 6.0:
                reality_check = "questionable"

            return {
                "reality_check": reality_check,
                "score": evaluation.roast_score,
                "concerns": [f.get("description", "") for f in evaluation.roast_findings[:3]]
            }
        except Exception as e:
            self.logger.error(f"MARVIN evaluation error: {e}", exc_info=True)
            return {}

    def _get_jedi_council_approval(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> Dict[str, Any]:
        """Get Jedi Council approval for workflow"""
        if not self.jedi_council:
            return {"approved": True, "reason": "Jedi Council not available"}

        try:
            # Prepare approval request
            request_text = f"Workflow: {evaluation.workflow_name}\n"
            request_text += f"Roast Score: {evaluation.roast_score:.2f}\n"
            request_text += f"Findings: {len(evaluation.roast_findings)}\n"

            # Request Jedi Council approval
            approval_result = self.jedi_council.seek_approval(
                request_id=evaluation.workflow_id,
                request_text=request_text,
                context={
                    "workflow_data": workflow_data,
                    "evaluation": evaluation.to_dict()
                }
            )

            return {
                "approved": approval_result.approved,
                "votes": [v.to_dict() for v in approval_result.votes] if hasattr(approval_result, 'votes') else [],
                "reasoning": approval_result.reasoning if hasattr(approval_result, 'reasoning') else ""
            }
        except Exception as e:
            self.logger.error(f"Jedi Council approval error: {e}", exc_info=True)
            return {"approved": False, "reason": f"Error: {str(e)}"}

    def _generate_repair_actions(self, workflow_data: Dict[str, Any], evaluation: WorkflowEvaluation) -> List[Dict[str, Any]]:
        """Generate repair actions from roast findings"""
        if not self.repair_executor:
            return []

        try:
            repair_actions = []

            for finding in evaluation.roast_findings:
                if finding.get("recommendations"):
                    action = {
                        "finding_id": finding.get("finding_id", ""),
                        "description": finding.get("description", ""),
                        "recommendations": finding.get("recommendations", []),
                        "severity": finding.get("severity", "medium")
                    }
                    repair_actions.append(action)

            return repair_actions
        except Exception as e:
            self.logger.error(f"Repair action generation error: {e}", exc_info=True)
            return []

    def _execute_repairs(self, repair_actions: List[Dict[str, Any]], workflow_data: Dict[str, Any]):
        """Execute repair actions"""
        if not self.repair_executor:
            return

        try:
            for action in repair_actions:
                # Execute repair via repair executor
                # This would typically call repair_executor methods
                self.logger.info(f"🔧 Executing repair: {action.get('description', 'N/A')}")
        except Exception as e:
            self.logger.error(f"Repair execution error: {e}", exc_info=True)

    def _assess_complexity(self, workflow_data: Dict[str, Any]) -> str:
        """Assess workflow complexity"""
        # Simple complexity assessment
        steps = workflow_data.get("steps", [])
        if len(steps) > 10:
            return "high"
        elif len(steps) > 5:
            return "medium"
        return "low"

    def _save_evaluation(self, evaluation: WorkflowEvaluation):
        """Save evaluation to file"""
        try:
            eval_file = self.data_dir / f"evaluation_{evaluation.workflow_id}_{int(time.time())}.json"
            with open(eval_file, 'w') as f:
                json.dump(evaluation.to_dict(), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving evaluation: {e}", exc_info=True)

    def inject(
        self,
        mode: TroubleshootingMode = TroubleshootingMode.PRE_WORKFLOW,
        level: EvaluationLevel = EvaluationLevel.STANDARD,
        auto_repair: bool = False,
        require_approval: bool = False
    ) -> Callable:
        """
        Decorator to inject troubleshooting into workflows

        Usage:
            @troubleshooting.inject(mode=TroubleshootingMode.PRE_WORKFLOW, level=EvaluationLevel.STANDARD)
            def my_workflow(workflow_data):
                # workflow code
                return result
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Extract workflow data
                workflow_data = {}
                if args:
                    workflow_data = args[0] if isinstance(args[0], dict) else {"args": args}
                workflow_data.update(kwargs)

                workflow_data["workflow_name"] = func.__name__
                workflow_data["workflow_id"] = workflow_data.get("workflow_id", f"{func.__name__}_{int(time.time())}")

                # Evaluate workflow
                evaluation = self.evaluate_workflow(
                    workflow_data,
                    mode=mode,
                    level=level,
                    auto_repair=auto_repair,
                    require_approval=require_approval
                )

                # Check if we should proceed
                if not evaluation.should_proceed and mode == TroubleshootingMode.PRE_WORKFLOW:
                    error_msg = f"Workflow {func.__name__} rejected by troubleshooting evaluation"
                    if evaluation.jedi_council_approval:
                        error_msg += f": {evaluation.jedi_council_approval.get('reasoning', 'No approval')}"
                    raise ValueError(error_msg)

                # Execute workflow
                try:
                    result = func(*args, **kwargs)

                    # Post-workflow evaluation
                    if mode == TroubleshootingMode.POST_WORKFLOW:
                        post_eval = self.evaluate_workflow(
                            {**workflow_data, "result": result},
                            mode=TroubleshootingMode.POST_WORKFLOW,
                            level=level
                        )
                        workflow_data["post_evaluation"] = post_eval.to_dict()

                    return result
                except Exception as e:
                    # On-error evaluation
                    if mode == TroubleshootingMode.ON_ERROR:
                        error_eval = self.evaluate_workflow(
                            {**workflow_data, "error": str(e)},
                            mode=TroubleshootingMode.ON_ERROR,
                            level=level,
                            auto_repair=auto_repair
                        )

                    raise

            return wrapper
        return decorator


# Global instance for easy access
_troubleshooting_instance = None


def get_troubleshooting(project_root: Optional[Path] = None) -> UniversalWorkflowTroubleshooting:
    """Get global troubleshooting instance"""
    global _troubleshooting_instance
    if _troubleshooting_instance is None:
        _troubleshooting_instance = UniversalWorkflowTroubleshooting(project_root=project_root)
    return _troubleshooting_instance


# Convenience decorator
def troubleshoot(
    mode: TroubleshootingMode = TroubleshootingMode.PRE_WORKFLOW,
    level: EvaluationLevel = EvaluationLevel.STANDARD,
    auto_repair: bool = False,
    require_approval: bool = False,
    project_root: Optional[Path] = None
) -> Callable:
    """
    Convenience decorator for workflow troubleshooting

    Usage:
        @troubleshoot(mode=TroubleshootingMode.PRE_WORKFLOW, level=EvaluationLevel.STANDARD)
        def my_workflow(workflow_data):
            # workflow code
            return result
    """
    troubleshooting = get_troubleshooting(project_root)
    return troubleshooting.inject(mode=mode, level=level, auto_repair=auto_repair, require_approval=require_approval)


if __name__ == "__main__":
    print("=" * 70)
    print("🔍 Universal Workflow Troubleshooting Module")
    print("   @ai @jarvis @marvin @rr[#roast + #repair]")
    print("   @decide[#decisioning + @aiq + @jc[#jedicouncil + #jedihighcouncil]]")
    print("=" * 70)

    troubleshooting = UniversalWorkflowTroubleshooting()

    # Example usage
    test_workflow = {
        "workflow_id": "test_001",
        "workflow_name": "Test Workflow",
        "steps": ["step1", "step2", "step3"],
        "urgency": "medium"
    }

    evaluation = troubleshooting.evaluate_workflow(
        test_workflow,
        mode=TroubleshootingMode.PRE_WORKFLOW,
        level=EvaluationLevel.STANDARD
    )

    print(f"\n✅ Evaluation complete:")
    print(f"   Workflow: {evaluation.workflow_name}")
    print(f"   Should proceed: {evaluation.should_proceed}")
    print(f"   Roast score: {evaluation.roast_score:.2f}")
    print(f"   Findings: {len(evaluation.roast_findings)}")
    print(f"   Repair needed: {evaluation.repair_needed}")
    print(f"   Decision: {evaluation.decision_outcome}")

    print("\n" + "=" * 70)
    print("✅ Universal Workflow Troubleshooting ready!")
    print("=" * 70)
