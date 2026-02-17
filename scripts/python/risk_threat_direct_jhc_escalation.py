#!/usr/bin/env python3
"""
Risk & Threat Direct JHC Escalation System

When @risk and @threat warrant skipping normal @jc (Jedi Council) 
and escalating directly to @jhc (Jedi High Council).

Tags: #RISK #THREAT #ESCALATION #JEDI_COUNCIL #JEDI_HIGH_COUNCIL @JARVIS @JHC @JC @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("RiskThreatDirectJHCEscalation")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RiskThreatDirectJHCEscalation")

# Import R5 Living Context Matrix
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    logger.warning("R5 Living Context Matrix not available")

# Import Universal Decision Tree
try:
    from universal_decision_tree import UniversalDecisionTree, DecisionContext, DecisionOutcome, decide
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    UniversalDecisionTree = None
    DecisionContext = None
    DecisionOutcome = None
    decide = None
    logger.warning("Universal Decision Tree not available")

# Import workflow systems (optional - may have import issues)
try:
    from master_workflow_orchestrator import MasterWorkflowOrchestrator
    WORKFLOW_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    WORKFLOW_AVAILABLE = False
    MasterWorkflowOrchestrator = None
    # Don't log warning on import - workflow is optional


class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EXISTENTIAL = "existential"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"
    EXISTENTIAL = "existential"


class ThreatType(Enum):
    """Threat types"""
    SECURITY = "security"
    DATA_BREACH = "data_breach"
    SYSTEM_FAILURE = "system_failure"
    FINANCIAL = "financial"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    EXISTENTIAL = "existential"
    CYBER = "cyber"
    PHYSICAL = "physical"
    INTELLIGENCE = "intelligence"


class EscalationPath(Enum):
    """Escalation paths"""
    NORMAL_JC = "normal_jc"  # Normal Jedi Council escalation
    DIRECT_JHC = "direct_jhc"  # Direct to Jedi High Council (skip JC)
    EMERGENCY_JHC = "emergency_jhc"  # Emergency direct to JHC


@dataclass
class RiskAssessment:
    """Risk assessment"""
    risk_id: str
    risk_level: RiskLevel
    risk_type: str
    description: str
    impact: str  # low, medium, high, critical, existential
    probability: float  # 0.0 to 1.0
    affected_systems: List[str] = field(default_factory=list)
    mitigation_required: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ThreatAssessment:
    """Threat assessment"""
    threat_id: str
    threat_type: ThreatType
    severity: ThreatSeverity
    description: str
    source: str  # internal, external, unknown
    affected_systems: List[str] = field(default_factory=list)
    immediate_action_required: bool = False
    law_enforcement_required: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class EscalationDecision:
    """Escalation decision"""
    decision_id: str
    escalation_path: EscalationPath
    skip_jc: bool
    direct_jhc: bool
    reasoning: str
    risk_factors: List[str] = field(default_factory=list)
    threat_factors: List[str] = field(default_factory=list)
    urgency: str = "high"  # low, medium, high, critical, emergency
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class RiskThreatDirectJHCEscalation:
    """
    Risk & Threat Direct JHC Escalation System

    Determines when @risk and @threat warrant skipping normal @jc
    and escalating directly to @jhc.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "risk_threat_escalation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize R5 Living Context Matrix
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                logger.info("✅ R5 Living Context Matrix initialized")
            except Exception as e:
                logger.warning(f"R5 initialization failed: {e}")
                self.r5 = None
        else:
            self.r5 = None

        # Initialize Universal Decision Tree
        if DECISIONING_AVAILABLE:
            try:
                self.decision_tree = UniversalDecisionTree(project_root)
                logger.info("✅ Universal Decision Tree initialized")
            except Exception as e:
                logger.warning(f"Decision Tree initialization failed: {e}")
                self.decision_tree = None
        else:
            self.decision_tree = None

        # Initialize Workflow Orchestrator
        if WORKFLOW_AVAILABLE:
            try:
                self.workflow_orchestrator = MasterWorkflowOrchestrator(project_root)
                logger.info("✅ Master Workflow Orchestrator initialized")
            except Exception as e:
                logger.warning(f"Workflow Orchestrator initialization failed: {e}")
                self.workflow_orchestrator = None
        else:
            self.workflow_orchestrator = None

        # Direct JHC escalation criteria
        self.direct_jhc_criteria = {
            "risk_levels": [
                RiskLevel.CRITICAL,
                RiskLevel.EXISTENTIAL
            ],
            "threat_severity": [
                ThreatSeverity.CRITICAL,
                ThreatSeverity.EXISTENTIAL
            ],
            "threat_types": [
                ThreatType.EXISTENTIAL,
                ThreatType.SECURITY,
                ThreatType.DATA_BREACH,
                ThreatType.INTELLIGENCE
            ],
            "risk_impact": ["critical", "existential"],
            "immediate_action_required": True,
            "law_enforcement_required": True,
            "system_failure": True,
            "financial_critical": True,
            "legal_critical": True,
            "reputational_critical": True
        }

        # Emergency JHC escalation criteria (even more urgent)
        self.emergency_jhc_criteria = {
            "risk_levels": [RiskLevel.EXISTENTIAL],
            "threat_severity": [ThreatSeverity.EXISTENTIAL],
            "threat_types": [ThreatType.EXISTENTIAL],
            "multiple_critical_threats": True,
            "cascading_failures": True,
            "active_breach": True,
            "immediate_danger": True
        }

        logger.info("="*80)
        logger.info("🚨 RISK & THREAT DIRECT JHC ESCALATION SYSTEM")
        logger.info("="*80)
        logger.info("")
        logger.info("   Determines when to skip @jc and escalate directly to @jhc")
        logger.info("")
        logger.info("   Integrations:")
        if self.r5:
            logger.info("   ✅ @r5 - R5 Living Context Matrix")
        if self.decision_tree:
            logger.info("   ✅ #decisioning - Universal Decision Tree")
        if self.workflow_orchestrator:
            logger.info("   ✅ @workflows - Master Workflow Orchestrator")
        logger.info("")

    def assess_and_escalate(
        self,
        risk_assessment: Optional[RiskAssessment] = None,
        threat_assessment: Optional[ThreatAssessment] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> EscalationDecision:
        """
        Assess risk/threat and determine escalation path

        Args:
            risk_assessment: Risk assessment
            threat_assessment: Threat assessment
            context: Additional context

        Returns:
            Escalation decision
        """
        if context is None:
            context = {}

        decision_id = f"escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Consult R5 for context-aware recommendations
        r5_recommendation = None
        if self.r5:
            try:
                r5_recommendation = self._consult_r5(risk_assessment, threat_assessment, context)
            except Exception as e:
                logger.warning(f"R5 consultation failed: {e}")

        # Consult decision tree for escalation decision
        decisioning_result = None
        if self.decision_tree:
            try:
                decisioning_result = self._consult_decision_tree(risk_assessment, threat_assessment, context)
            except Exception as e:
                logger.warning(f"Decision tree consultation failed: {e}")

        # Consult workflows for workflow-based escalation
        workflow_recommendation = None
        if self.workflow_orchestrator:
            try:
                workflow_recommendation = self._consult_workflows(risk_assessment, threat_assessment, context)
            except Exception as e:
                logger.warning(f"Workflow consultation failed: {e}")

        # Determine escalation path (with R5, decisioning, and workflow input)
        escalation_path, skip_jc, direct_jhc, reasoning, risk_factors, threat_factors, urgency = \
            self._determine_escalation_path(
                risk_assessment, 
                threat_assessment, 
                context,
                r5_recommendation=r5_recommendation,
                decisioning_result=decisioning_result,
                workflow_recommendation=workflow_recommendation
            )

        decision = EscalationDecision(
            decision_id=decision_id,
            escalation_path=escalation_path,
            skip_jc=skip_jc,
            direct_jhc=direct_jhc,
            reasoning=reasoning,
            risk_factors=risk_factors,
            threat_factors=threat_factors,
            urgency=urgency
        )

        # Log decision
        logger.info("="*80)
        logger.info("🚨 ESCALATION DECISION")
        logger.info("="*80)
        logger.info(f"   Decision ID: {decision_id}")
        logger.info(f"   Escalation Path: {escalation_path.value.upper()}")
        logger.info(f"   Skip JC: {skip_jc}")
        logger.info(f"   Direct JHC: {direct_jhc}")
        logger.info(f"   Urgency: {urgency.upper()}")
        logger.info("")
        logger.info(f"   Reasoning: {reasoning}")
        logger.info("")

        if risk_factors:
            logger.info("   Risk Factors:")
            for factor in risk_factors:
                logger.info(f"   - {factor}")
            logger.info("")

        if threat_factors:
            logger.info("   Threat Factors:")
            for factor in threat_factors:
                logger.info(f"   - {factor}")
            logger.info("")

        # Save decision
        decision_file = self.data_dir / f"{decision_id}.json"
        with open(decision_file, 'w', encoding='utf-8') as f:
            json.dump({
                "decision_id": decision.decision_id,
                "escalation_path": decision.escalation_path.value,
                "skip_jc": decision.skip_jc,
                "direct_jhc": decision.direct_jhc,
                "reasoning": decision.reasoning,
                "risk_factors": decision.risk_factors,
                "threat_factors": decision.threat_factors,
                "urgency": decision.urgency,
                "timestamp": decision.timestamp,
                "risk_assessment": {
                    "risk_id": risk_assessment.risk_id,
                    "risk_level": risk_assessment.risk_level.value,
                    "risk_type": risk_assessment.risk_type,
                    "description": risk_assessment.description,
                    "impact": risk_assessment.impact,
                    "probability": risk_assessment.probability
                } if risk_assessment else None,
                "threat_assessment": {
                    "threat_id": threat_assessment.threat_id,
                    "threat_type": threat_assessment.threat_type.value,
                    "severity": threat_assessment.severity.value,
                    "description": threat_assessment.description,
                    "source": threat_assessment.source,
                    "immediate_action_required": threat_assessment.immediate_action_required,
                    "law_enforcement_required": threat_assessment.law_enforcement_required
                } if threat_assessment else None
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"   💾 Decision saved: {decision_file}")
        logger.info("="*80)
        logger.info("")

        return decision

    def _consult_r5(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Consult R5 Living Context Matrix for context-aware escalation recommendations

        Returns:
            R5 recommendation dict with escalation advice
        """
        if not self.r5:
            return None

        try:
            # Create context for R5
            r5_context = {
                "risk_level": risk_assessment.risk_level.value if risk_assessment else None,
                "threat_severity": threat_assessment.severity.value if threat_assessment else None,
                "threat_type": threat_assessment.threat_type.value if threat_assessment else None,
                "escalation_type": "risk_threat_direct_jhc",
                **context
            }

            # Ingest escalation context into R5
            session_data = {
                "session_id": f"escalation_r5_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "content": f"Risk/Threat Escalation: {r5_context}",
                "metadata": {
                    "type": "escalation_consultation",
                    "risk_assessment": risk_assessment.risk_id if risk_assessment else None,
                    "threat_assessment": threat_assessment.threat_id if threat_assessment else None
                }
            }

            session_id = self.r5.ingest_session(session_data)

            # Get R5 recommendation (simplified - in real implementation, would query R5 matrix)
            recommendation = {
                "session_id": session_id,
                "recommendation": "escalate_direct_jhc" if (
                    (risk_assessment and risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXISTENTIAL]) or
                    (threat_assessment and threat_assessment.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXISTENTIAL])
                ) else "normal_escalation",
                "confidence": 0.85,
                "reasoning": "R5 context-aware analysis"
            }

            logger.info(f"   📊 R5 Recommendation: {recommendation['recommendation']}")

            return recommendation

        except Exception as e:
            logger.error(f"R5 consultation error: {e}")
            return None

    def _consult_decision_tree(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Consult Universal Decision Tree for escalation decision

        Returns:
            Decision tree result
        """
        if not self.decision_tree or not DecisionContext:
            return None

        try:
            # Create decision context
            decision_context = DecisionContext(
                urgency="critical" if (
                    (risk_assessment and risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXISTENTIAL]) or
                    (threat_assessment and threat_assessment.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXISTENTIAL])
                ) else "high",
                complexity="high" if (
                    (risk_assessment and risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXISTENTIAL]) or
                    (threat_assessment and threat_assessment.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXISTENTIAL])
                ) else "medium",
                custom_data={
                    "risk_level": risk_assessment.risk_level.value if risk_assessment else None,
                    "threat_severity": threat_assessment.severity.value if threat_assessment else None,
                    "threat_type": threat_assessment.threat_type.value if threat_assessment else None,
                    "risk_impact": risk_assessment.impact if risk_assessment else None,
                    "risk_probability": risk_assessment.probability if risk_assessment else None,
                    "immediate_action_required": threat_assessment.immediate_action_required if threat_assessment else False,
                    "law_enforcement_required": threat_assessment.law_enforcement_required if threat_assessment else False,
                    **context
                }
            )

            # Use risk_threat_escalation decision tree
            tree_name = "risk_threat_escalation"
            if tree_name not in self.decision_tree.trees:
                # Create the tree if it doesn't exist (should be in config, but fallback)
                logger.warning(f"Decision tree '{tree_name}' not found, using fallback logic")
                # Fallback to direct assessment
                if (risk_assessment and risk_assessment.risk_level == RiskLevel.EXISTENTIAL) or \
                   (threat_assessment and threat_assessment.severity == ThreatSeverity.EXISTENTIAL):
                    return {
                        "outcome": "escalate",
                        "reasoning": "Existential risk/threat detected",
                        "confidence": 0.95,
                        "next_action": "emergency_jhc"
                    }
                elif (risk_assessment and risk_assessment.risk_level == RiskLevel.CRITICAL) or \
                     (threat_assessment and threat_assessment.severity == ThreatSeverity.CRITICAL):
                    return {
                        "outcome": "escalate",
                        "reasoning": "Critical risk/threat detected",
                        "confidence": 0.9,
                        "next_action": "direct_jhc"
                    }
                else:
                    return {
                        "outcome": "skip",
                        "reasoning": "Normal escalation path",
                        "confidence": 0.85,
                        "next_action": "normal_jc"
                    }

            # Add R5 and workflow recommendations to context
            decision_context.custom_data.update({
                "r5_recommendation": r5_recommendation.get("recommendation") if r5_recommendation else None,
                "workflow_recommendation": workflow_recommendation.get("recommendation") if workflow_recommendation else None,
                "workflow_priority": workflow_recommendation.get("priority") if workflow_recommendation else None
            })

            result = self.decision_tree.decide(tree_name, decision_context)

            # Map decision outcome to escalation metadata
            if result.outcome == DecisionOutcome.ESCALATE:
                # Check metadata for escalation path
                escalation_metadata = result.metadata.get("escalation_path", "direct_jhc")
                decision_context.custom_data["decisioning_outcome"] = escalation_metadata
            else:
                decision_context.custom_data["decisioning_outcome"] = result.outcome.value

            logger.info(f"   🌳 Decision Tree: {result.outcome.value} (confidence: {result.confidence:.2f})")

            return {
                "outcome": result.outcome.value,
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "next_action": result.next_action
            }

        except Exception as e:
            logger.error(f"Decision tree consultation error: {e}")
            return None

    def _consult_workflows(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Consult workflow orchestrator for workflow-based escalation

        Returns:
            Workflow recommendation
        """
        if not self.workflow_orchestrator:
            return None

        try:
            # Check if escalation workflow exists
            workflow_context = {
                "risk_assessment": risk_assessment.risk_id if risk_assessment else None,
                "threat_assessment": threat_assessment.threat_id if threat_assessment else None,
                "escalation_type": "risk_threat_direct_jhc",
                **context
            }

            # In real implementation, would query workflow orchestrator for escalation workflows
            recommendation = {
                "workflow_available": True,
                "workflow_type": "escalation",
                "recommendation": "execute_escalation_workflow",
                "priority": "high" if (
                    (risk_assessment and risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXISTENTIAL]) or
                    (threat_assessment and threat_assessment.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXISTENTIAL])
                ) else "medium"
            }

            logger.info(f"   🔄 Workflow Recommendation: {recommendation['recommendation']}")

            return recommendation

        except Exception as e:
            logger.error(f"Workflow consultation error: {e}")
            return None

    def _determine_escalation_path(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any],
        r5_recommendation: Optional[Dict[str, Any]] = None,
        decisioning_result: Optional[Dict[str, Any]] = None,
        workflow_recommendation: Optional[Dict[str, Any]] = None
    ) -> Tuple[EscalationPath, bool, bool, str, List[str], List[str], str]:
        """
        Determine escalation path based on risk and threat

        Args:
            risk_assessment: Risk assessment
            threat_assessment: Threat assessment
            context: Additional context
            r5_recommendation: R5 recommendation
            decisioning_result: Decision tree result
            workflow_recommendation: Workflow recommendation

        Returns:
            (escalation_path, skip_jc, direct_jhc, reasoning, risk_factors, threat_factors, urgency)
        """
        risk_factors = []
        threat_factors = []
        urgency = "medium"

        # Incorporate R5 recommendation
        if r5_recommendation:
            if r5_recommendation.get("recommendation") == "escalate_direct_jhc":
                risk_factors.append(f"R5 recommends direct JHC escalation (confidence: {r5_recommendation.get('confidence', 0.0):.2f})")

        # Incorporate decision tree result
        if decisioning_result:
            outcome = decisioning_result.get("outcome")
            if outcome == "escalate" or outcome in ["escalate", "direct_jhc", "emergency_jhc"]:
                risk_factors.append(f"#decisioning recommends escalation: {decisioning_result.get('reasoning', 'N/A')} (confidence: {decisioning_result.get('confidence', 0.0):.2f})")
                # Use decision tree metadata if available
                if decisioning_result.get("metadata"):
                    escalation_metadata = decisioning_result.get("metadata", {})
                    if escalation_metadata.get("escalation_path"):
                        # Override escalation path based on decision tree
                        escalation_path_override = escalation_metadata.get("escalation_path")
                        if escalation_path_override == "emergency_jhc":
                            return (
                                EscalationPath.EMERGENCY_JHC,
                                True,
                                True,
                                f"EMERGENCY: {decisioning_result.get('reasoning', 'Decision tree recommends emergency JHC')}",
                                risk_factors,
                                threat_factors,
                                "emergency"
                            )
                        elif escalation_path_override == "direct_jhc":
                            return (
                                EscalationPath.DIRECT_JHC,
                                True,
                                True,
                                f"CRITICAL: {decisioning_result.get('reasoning', 'Decision tree recommends direct JHC')}",
                                risk_factors,
                                threat_factors,
                                "critical"
                            )

        # Incorporate workflow recommendation
        if workflow_recommendation:
            if workflow_recommendation.get("recommendation") == "execute_escalation_workflow":
                risk_factors.append(f"Workflow orchestrator recommends escalation workflow (priority: {workflow_recommendation.get('priority', 'medium')})")

        # Check for emergency JHC escalation (highest priority)
        if self._check_emergency_jhc(risk_assessment, threat_assessment, context):
            urgency = "emergency"
            return (
                EscalationPath.EMERGENCY_JHC,
                True,  # skip_jc
                True,  # direct_jhc
                "EMERGENCY: Existential risk/threat detected. Immediate direct escalation to Jedi High Council required. Normal Jedi Council escalation bypassed due to critical urgency.",
                risk_factors,
                threat_factors,
                urgency
            )

        # Check for direct JHC escalation
        if self._check_direct_jhc(risk_assessment, threat_assessment, context):
            urgency = "critical"
            return (
                EscalationPath.DIRECT_JHC,
                True,  # skip_jc
                True,  # direct_jhc
                "CRITICAL: Risk/threat level warrants direct escalation to Jedi High Council. Normal Jedi Council escalation bypassed.",
                risk_factors,
                threat_factors,
                urgency
            )

        # Normal JC escalation
        urgency = "high"
        return (
            EscalationPath.NORMAL_JC,
            False,  # skip_jc
            False,  # direct_jhc
            "Standard escalation: Proceed through normal Jedi Council process. Risk/threat levels do not warrant direct JHC escalation.",
            risk_factors,
            threat_factors,
            urgency
        )

    def _check_emergency_jhc(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any]
    ) -> bool:
        """Check if emergency JHC escalation is warranted"""
        # Existential risk
        if risk_assessment and risk_assessment.risk_level == RiskLevel.EXISTENTIAL:
            return True

        # Existential threat
        if threat_assessment and threat_assessment.severity == ThreatSeverity.EXISTENTIAL:
            return True

        # Existential threat type
        if threat_assessment and threat_assessment.threat_type == ThreatType.EXISTENTIAL:
            return True

        # Multiple critical threats
        if context.get("multiple_critical_threats", False):
            return True

        # Cascading failures
        if context.get("cascading_failures", False):
            return True

        # Active breach
        if context.get("active_breach", False):
            return True

        # Immediate danger
        if context.get("immediate_danger", False):
            return True

        return False

    def _check_direct_jhc(
        self,
        risk_assessment: Optional[RiskAssessment],
        threat_assessment: Optional[ThreatAssessment],
        context: Dict[str, Any]
    ) -> bool:
        """Check if direct JHC escalation is warranted"""
        # Critical or existential risk level
        if risk_assessment:
            if risk_assessment.risk_level in [RiskLevel.CRITICAL, RiskLevel.EXISTENTIAL]:
                return True
            if risk_assessment.impact in ["critical", "existential"]:
                return True
            if risk_assessment.probability >= 0.8:  # High probability
                return True

        # Critical or existential threat severity
        if threat_assessment:
            if threat_assessment.severity in [ThreatSeverity.CRITICAL, ThreatSeverity.EXISTENTIAL]:
                return True

            # Critical threat types
            if threat_assessment.threat_type in [
                ThreatType.EXISTENTIAL,
                ThreatType.SECURITY,
                ThreatType.DATA_BREACH,
                ThreatType.INTELLIGENCE
            ]:
                return True

            # Immediate action required
            if threat_assessment.immediate_action_required:
                return True

            # Law enforcement required
            if threat_assessment.law_enforcement_required:
                return True

        # Context-based checks
        if context.get("system_failure", False):
            return True

        if context.get("financial_critical", False):
            return True

        if context.get("legal_critical", False):
            return True

        if context.get("reputational_critical", False):
            return True

        # Combined risk + threat
        if risk_assessment and threat_assessment:
            if (risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] and
                threat_assessment.severity in [ThreatSeverity.SEVERE, ThreatSeverity.CRITICAL]):
                return True

        return False

    def create_risk_assessment(
        self,
        risk_level: RiskLevel,
        risk_type: str,
        description: str,
        impact: str,
        probability: float,
        affected_systems: Optional[List[str]] = None
    ) -> RiskAssessment:
        """Create a risk assessment"""
        if affected_systems is None:
            affected_systems = []

        return RiskAssessment(
            risk_id=f"risk_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            risk_level=risk_level,
            risk_type=risk_type,
            description=description,
            impact=impact,
            probability=probability,
            affected_systems=affected_systems
        )

    def create_threat_assessment(
        self,
        threat_type: ThreatType,
        severity: ThreatSeverity,
        description: str,
        source: str,
        affected_systems: Optional[List[str]] = None,
        immediate_action_required: bool = False,
        law_enforcement_required: bool = False
    ) -> ThreatAssessment:
        """Create a threat assessment"""
        if affected_systems is None:
            affected_systems = []

        return ThreatAssessment(
            threat_id=f"threat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            threat_type=threat_type,
            severity=severity,
            description=description,
            source=source,
            affected_systems=affected_systems,
            immediate_action_required=immediate_action_required,
            law_enforcement_required=law_enforcement_required
        )


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Risk & Threat Direct JHC Escalation")
        parser.add_argument("--risk-level", choices=["low", "medium", "high", "critical", "existential"],
                           help="Risk level")
        parser.add_argument("--threat-severity", choices=["minor", "moderate", "severe", "critical", "existential"],
                           help="Threat severity")
        parser.add_argument("--threat-type", choices=[t.value for t in ThreatType],
                           help="Threat type")
        parser.add_argument("--immediate-action", action="store_true",
                           help="Immediate action required")
        parser.add_argument("--law-enforcement", action="store_true",
                           help="Law enforcement required")
        parser.add_argument("--test", action="store_true",
                           help="Run test scenarios")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        escalation_system = RiskThreatDirectJHCEscalation(project_root)

        if args.test:
            # Test scenarios
            logger.info("🧪 Running test scenarios...")
            logger.info("")

            # Test 1: Critical risk - should direct JHC
            logger.info("Test 1: Critical Risk")
            risk = escalation_system.create_risk_assessment(
                risk_level=RiskLevel.CRITICAL,
                risk_type="system_failure",
                description="Critical system failure risk",
                impact="critical",
                probability=0.9
            )
            decision = escalation_system.assess_and_escalate(risk_assessment=risk)
            logger.info("")

            # Test 2: Existential threat - should emergency JHC
            logger.info("Test 2: Existential Threat")
            threat = escalation_system.create_threat_assessment(
                threat_type=ThreatType.EXISTENTIAL,
                severity=ThreatSeverity.EXISTENTIAL,
                description="Existential threat detected",
                source="external",
                immediate_action_required=True
            )
            decision = escalation_system.assess_and_escalate(threat_assessment=threat)
            logger.info("")

            # Test 3: Normal risk - should normal JC
            logger.info("Test 3: Normal Risk")
            risk = escalation_system.create_risk_assessment(
                risk_level=RiskLevel.MEDIUM,
                risk_type="operational",
                description="Medium operational risk",
                impact="medium",
                probability=0.4
            )
            decision = escalation_system.assess_and_escalate(risk_assessment=risk)
            logger.info("")

        elif args.risk_level or args.threat_severity:
            # Create assessments from args
            risk_assessment = None
            threat_assessment = None

            if args.risk_level:
                risk_assessment = escalation_system.create_risk_assessment(
                    risk_level=RiskLevel[args.risk_level.upper()],
                    risk_type="assessed",
                    description="Risk assessment from command line",
                    impact=args.risk_level,
                    probability=0.7 if args.risk_level in ["high", "critical", "existential"] else 0.4
                )

            if args.threat_severity:
                threat_type = ThreatType[args.threat_type.upper()] if args.threat_type else ThreatType.SECURITY
                threat_assessment = escalation_system.create_threat_assessment(
                    threat_type=threat_type,
                    severity=ThreatSeverity[args.threat_severity.upper()],
                    description="Threat assessment from command line",
                    source="unknown",
                    immediate_action_required=args.immediate_action,
                    law_enforcement_required=args.law_enforcement
                )

            context = {}
            if args.immediate_action:
                context["immediate_danger"] = True
            if args.law_enforcement:
                context["law_enforcement_required"] = True

            decision = escalation_system.assess_and_escalate(
                risk_assessment=risk_assessment,
                threat_assessment=threat_assessment,
                context=context
            )
        else:
            logger.info("Use --test for test scenarios or provide --risk-level/--threat-severity")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())