#!/usr/bin/env python3
"""
@SYPHON Threat & Risk Assessment with 3-5-7-9 Escalation System

Escalation based on @syphon threat & risk assessment:
- Level 3: Low escalation
- Level 5: Medium escalation
- Level 7: High escalation
- Level 9: Critical escalation (JHC)

#CUSTOMER #IMPACT is HIGHEST PRIORITY (top 3 at least)

Integrates with:
- @AIQ: AI Quorum for consensus decisions
- @JC: Jedi Council for medium-high escalation
- @JHC: Jedi High Council for critical escalation

Tags: #SYPHON #THREAT #RISK #ESCALATION #CUSTOMER #IMPACT @AIQ @JC @JHC @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONThreatRiskEscalation")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from lumina.syphon import SYPHONSystem
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("⚠️  SYPHON system not available")

# Import escalation systems
try:
    from jarvis_escalate_jedi_high_council import JARVISEscalateJediHighCouncil
    JHC_AVAILABLE = True
except ImportError:
    JHC_AVAILABLE = False
    logger.warning("⚠️  JHC escalation not available")

try:
    from aiq_fallback_decisioning import AIQFallbackDecisioning
    AIQ_AVAILABLE = True
except ImportError:
    AIQ_AVAILABLE = False
    logger.warning("⚠️  AIQ system not available")


class EscalationLevel(Enum):
    """3-5-7-9 Escalation Levels"""
    LEVEL_3 = 3  # Low escalation
    LEVEL_5 = 5  # Medium escalation
    LEVEL_7 = 7  # High escalation
    LEVEL_9 = 9  # Critical escalation (JHC)


class ThreatSeverity(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CustomerImpactLevel(Enum):
    """Customer impact levels - HIGHEST PRIORITY"""
    NONE = "none"  # No customer impact
    LOW = "low"  # Minor customer impact
    MEDIUM = "medium"  # Moderate customer impact
    HIGH = "high"  # Significant customer impact
    CRITICAL = "critical"  # Severe customer impact


@dataclass
class ThreatAssessment:
    """Threat assessment from @SYPHON"""
    threat_id: str
    threat_type: str
    severity: ThreatSeverity
    description: str
    detected_by: str = "@SYPHON"
    detected_at: datetime = field(default_factory=datetime.now)
    affected_systems: List[str] = field(default_factory=list)
    indicators: List[str] = field(default_factory=list)
    confidence: float = 0.0  # 0.0 to 1.0


@dataclass
class RiskAssessment:
    """Risk assessment from @SYPHON"""
    risk_id: str
    risk_type: str
    level: RiskLevel
    description: str
    detected_by: str = "@SYPHON"
    detected_at: datetime = field(default_factory=datetime.now)
    affected_systems: List[str] = field(default_factory=list)
    probability: float = 0.0  # 0.0 to 1.0
    impact: float = 0.0  # 0.0 to 1.0


@dataclass
class CustomerImpactAssessment:
    """Customer impact assessment - HIGHEST PRIORITY"""
    impact_id: str
    level: CustomerImpactLevel
    description: str
    affected_customers: int = 0
    affected_features: List[str] = field(default_factory=list)
    business_impact: str = ""
    detected_at: datetime = field(default_factory=datetime.now)
    urgency: str = "normal"  # normal, urgent, critical


@dataclass
class EscalationDecision:
    """Escalation decision based on threat/risk/customer impact"""
    escalation_level: EscalationLevel
    target: str  # @AIQ, @JC, @JHC
    reason: str
    threat_assessment: Optional[ThreatAssessment] = None
    risk_assessment: Optional[RiskAssessment] = None
    customer_impact: Optional[CustomerImpactAssessment] = None
    priority: int = 5  # 1-10, higher = more urgent
    requires_immediate_action: bool = False


class SYPHONThreatRiskEscalation:
    """
    @SYPHON Threat & Risk Assessment with 3-5-7-9 Escalation System

    #CUSTOMER #IMPACT is HIGHEST PRIORITY (top 3 at least)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON Threat & Risk Escalation System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_escalation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON system
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root=self.project_root)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON init error: {e}")

        # Initialize escalation systems
        self.jhc_escalator = None
        if JHC_AVAILABLE:
            try:
                self.jhc_escalator = JARVISEscalateJediHighCouncil(self.project_root)
                logger.info("✅ JHC escalation initialized")
            except Exception as e:
                logger.warning(f"⚠️  JHC escalation init error: {e}")

        self.aiq_system = None
        if AIQ_AVAILABLE:
            try:
                self.aiq_system = AIQFallbackDecisioning(self.project_root)
                logger.info("✅ AIQ system initialized")
            except Exception as e:
                logger.warning(f"⚠️  AIQ init error: {e}")

        logger.info("=" * 80)
        logger.info("🚨 @SYPHON THREAT & RISK ESCALATION SYSTEM")
        logger.info("   3-5-7-9 Escalation Levels")
        logger.info("   #CUSTOMER #IMPACT = HIGHEST PRIORITY (Top 3)")
        logger.info("=" * 80)

    def assess_and_escalate(
        self,
        context: Dict[str, Any],
        customer_impact: Optional[CustomerImpactAssessment] = None,
        threat_assessment: Optional[ThreatAssessment] = None,
        risk_assessment: Optional[RiskAssessment] = None
    ) -> EscalationDecision:
        """
        Assess threat/risk/customer impact and determine escalation level

        #CUSTOMER #IMPACT is HIGHEST PRIORITY (top 3 at least)

        Escalation Logic:
        - Level 3: Low threat/risk, low customer impact → @AIQ
        - Level 5: Medium threat/risk, medium customer impact → @JC
        - Level 7: High threat/risk, high customer impact → @JC (urgent)
        - Level 9: Critical threat/risk, critical customer impact → @JHC

        Priority Order:
        1. Customer Impact (HIGHEST PRIORITY - top 3)
        2. Threat Severity
        3. Risk Level
        """
        logger.info("=" * 80)
        logger.info("🔍 ASSESSING THREAT/RISK/CUSTOMER IMPACT")
        logger.info("=" * 80)

        # Step 1: Assess Customer Impact (HIGHEST PRIORITY)
        customer_impact_level = CustomerImpactLevel.NONE
        customer_priority = 0

        if customer_impact:
            customer_impact_level = customer_impact.level
            # Customer impact priority mapping (HIGHEST PRIORITY)
            customer_priority_map = {
                CustomerImpactLevel.CRITICAL: 10,  # Top priority
                CustomerImpactLevel.HIGH: 9,  # Top 3
                CustomerImpactLevel.MEDIUM: 7,  # Top 3
                CustomerImpactLevel.LOW: 4,
                CustomerImpactLevel.NONE: 1
            }
            customer_priority = customer_priority_map.get(customer_impact_level, 5)
            logger.info(f"   👥 CUSTOMER IMPACT: {customer_impact_level.value.upper()} (Priority: {customer_priority}/10)")
            logger.info(f"      Affected Customers: {customer_impact.affected_customers}")
            logger.info(f"      Business Impact: {customer_impact.business_impact}")

        # Step 2: Assess Threat
        threat_severity = ThreatSeverity.LOW
        threat_priority = 0

        if threat_assessment:
            threat_severity = threat_assessment.severity
            threat_priority_map = {
                ThreatSeverity.CRITICAL: 9,
                ThreatSeverity.HIGH: 7,
                ThreatSeverity.MEDIUM: 5,
                ThreatSeverity.LOW: 3
            }
            threat_priority = threat_priority_map.get(threat_severity, 5)
            logger.info(f"   ⚠️  THREAT: {threat_severity.value.upper()} (Priority: {threat_priority}/10)")
            logger.info(f"      Type: {threat_assessment.threat_type}")
            logger.info(f"      Confidence: {threat_assessment.confidence:.2f}")

        # Step 3: Assess Risk
        risk_level = RiskLevel.LOW
        risk_priority = 0

        if risk_assessment:
            risk_level = risk_assessment.level
            risk_priority_map = {
                RiskLevel.CRITICAL: 9,
                RiskLevel.HIGH: 7,
                RiskLevel.MEDIUM: 5,
                RiskLevel.LOW: 3
            }
            risk_priority = risk_priority_map.get(risk_level, 5)
            logger.info(f"   ⚠️  RISK: {risk_level.value.upper()} (Priority: {risk_priority}/10)")
            logger.info(f"      Type: {risk_assessment.risk_type}")
            logger.info(f"      Probability: {risk_assessment.probability:.2f}")
            logger.info(f"      Impact: {risk_assessment.impact:.2f}")

        # Step 4: Determine Overall Priority (Customer Impact weighted highest)
        # Customer Impact gets 50% weight (top priority), Threat 30%, Risk 20%
        overall_priority = (
            customer_priority * 0.5 +  # Customer Impact = 50% weight (HIGHEST)
            threat_priority * 0.3 +     # Threat = 30% weight
            risk_priority * 0.2          # Risk = 20% weight
        )

        logger.info("")
        logger.info(f"   📊 OVERALL PRIORITY: {overall_priority:.1f}/10")
        logger.info(f"      Customer Impact: {customer_priority} (50% weight)")
        logger.info(f"      Threat: {threat_priority} (30% weight)")
        logger.info(f"      Risk: {risk_priority} (20% weight)")
        logger.info("")

        # Step 5: Determine Escalation Level (3-5-7-9)
        escalation_level = EscalationLevel.LEVEL_3
        target = "@AIQ"
        reason = ""
        requires_immediate = False

        # Escalation logic with Customer Impact as primary driver
        if customer_impact_level == CustomerImpactLevel.CRITICAL or overall_priority >= 9.0:
            # Level 9: Critical - Direct to JHC
            escalation_level = EscalationLevel.LEVEL_9
            target = "@JHC"
            reason = "CRITICAL customer impact or overall priority >= 9.0 - Direct escalation to Jedi High Council"
            requires_immediate = True
        elif customer_impact_level == CustomerImpactLevel.HIGH or overall_priority >= 7.5:
            # Level 7: High - Urgent to JC
            escalation_level = EscalationLevel.LEVEL_7
            target = "@JC"
            reason = "HIGH customer impact or overall priority >= 7.5 - Urgent escalation to Jedi Council"
            requires_immediate = True
        elif customer_impact_level == CustomerImpactLevel.MEDIUM or overall_priority >= 5.5:
            # Level 5: Medium - Standard to JC
            escalation_level = EscalationLevel.LEVEL_5
            target = "@JC"
            reason = "MEDIUM customer impact or overall priority >= 5.5 - Standard escalation to Jedi Council"
        else:
            # Level 3: Low - AIQ consensus
            escalation_level = EscalationLevel.LEVEL_3
            target = "@AIQ"
            reason = "LOW customer impact or overall priority < 5.5 - AIQ consensus decision"

        logger.info("=" * 80)
        logger.info(f"🎯 ESCALATION DECISION: LEVEL {escalation_level.value}")
        logger.info(f"   Target: {target}")
        logger.info(f"   Reason: {reason}")
        logger.info(f"   Immediate Action: {'✅ YES' if requires_immediate else '❌ NO'}")
        logger.info("=" * 80)

        return EscalationDecision(
            escalation_level=escalation_level,
            target=target,
            reason=reason,
            threat_assessment=threat_assessment,
            risk_assessment=risk_assessment,
            customer_impact=customer_impact,
            priority=int(overall_priority),
            requires_immediate_action=requires_immediate
        )

    def execute_escalation(self, decision: EscalationDecision) -> Dict[str, Any]:
        """Execute escalation based on decision"""
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"🚀 EXECUTING ESCALATION: LEVEL {decision.escalation_level.value} → {decision.target}")
        logger.info("=" * 80)

        result = {
            "escalation_level": decision.escalation_level.value,
            "target": decision.target,
            "executed": False,
            "result": None
        }

        # Execute based on escalation level
        if decision.escalation_level == EscalationLevel.LEVEL_9:
            # Critical - JHC
            if self.jhc_escalator:
                try:
                    jhc_result = self.jhc_escalator.escalate(
                        title=f"CRITICAL: {decision.customer_impact.description if decision.customer_impact else 'Threat/Risk Escalation'}",
                        description=self._build_escalation_description(decision),
                        category="critical",
                        priority=decision.priority,
                        context={
                            "escalation_level": decision.escalation_level.value,
                            "customer_impact": decision.customer_impact.level.value if decision.customer_impact else "none",
                            "threat_severity": decision.threat_assessment.severity.value if decision.threat_assessment else "none",
                            "risk_level": decision.risk_assessment.level.value if decision.risk_assessment else "none"
                        }
                    )
                    result["executed"] = True
                    result["result"] = jhc_result
                    logger.info("   ✅ Escalated to @JHC")
                except Exception as e:
                    logger.error(f"   ❌ JHC escalation failed: {e}")
            else:
                logger.warning("   ⚠️  JHC escalator not available")

        elif decision.escalation_level == EscalationLevel.LEVEL_7:
            # High - JC (urgent)
            logger.info("   📤 Escalating to @JC (URGENT)")
            logger.info("   ⚠️  JC escalation not yet implemented - logging for manual review")
            result["executed"] = True
            result["result"] = {"status": "logged", "requires_manual_review": True}

        elif decision.escalation_level == EscalationLevel.LEVEL_5:
            # Medium - JC (standard)
            logger.info("   📤 Escalating to @JC (STANDARD)")
            logger.info("   ⚠️  JC escalation not yet implemented - logging for manual review")
            result["executed"] = True
            result["result"] = {"status": "logged", "requires_manual_review": True}

        elif decision.escalation_level == EscalationLevel.LEVEL_3:
            # Low - AIQ
            if self.aiq_system:
                try:
                    logger.info("   📤 Escalating to @AIQ for consensus")
                    # AIQ consensus decision
                    aiq_result = {
                        "status": "aiq_consensus",
                        "decision": "reviewed",
                        "requires_action": decision.requires_immediate_action
                    }
                    result["executed"] = True
                    result["result"] = aiq_result
                    logger.info("   ✅ @AIQ consensus decision made")
                except Exception as e:
                    logger.error(f"   ❌ AIQ escalation failed: {e}")
            else:
                logger.warning("   ⚠️  AIQ system not available")

        # Save escalation record
        self._save_escalation_record(decision, result)

        return result

    def _build_escalation_description(self, decision: EscalationDecision) -> str:
        """Build escalation description from decision"""
        parts = []

        if decision.customer_impact:
            parts.append(f"**CUSTOMER IMPACT (HIGHEST PRIORITY):** {decision.customer_impact.level.value.upper()}")
            parts.append(f"- Affected Customers: {decision.customer_impact.affected_customers}")
            parts.append(f"- Business Impact: {decision.customer_impact.business_impact}")
            parts.append(f"- Description: {decision.customer_impact.description}")
            parts.append("")

        if decision.threat_assessment:
            parts.append(f"**THREAT ASSESSMENT:** {decision.threat_assessment.severity.value.upper()}")
            parts.append(f"- Type: {decision.threat_assessment.threat_type}")
            parts.append(f"- Description: {decision.threat_assessment.description}")
            parts.append(f"- Confidence: {decision.threat_assessment.confidence:.2f}")
            parts.append("")

        if decision.risk_assessment:
            parts.append(f"**RISK ASSESSMENT:** {decision.risk_assessment.level.value.upper()}")
            parts.append(f"- Type: {decision.risk_assessment.risk_type}")
            parts.append(f"- Description: {decision.risk_assessment.description}")
            parts.append(f"- Probability: {decision.risk_assessment.probability:.2f}")
            parts.append(f"- Impact: {decision.risk_assessment.impact:.2f}")
            parts.append("")

        parts.append(f"**ESCALATION LEVEL:** {decision.escalation_level.value}")
        parts.append(f"**PRIORITY:** {decision.priority}/10")
        parts.append(f"**IMMEDIATE ACTION REQUIRED:** {'YES' if decision.requires_immediate_action else 'NO'}")

        return "\n".join(parts)

    def _save_escalation_record(self, decision: EscalationDecision, result: Dict[str, Any]):
        """Save escalation record"""
        record_file = self.data_dir / f"escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        record = {
            "timestamp": datetime.now().isoformat(),
            "escalation_level": decision.escalation_level.value,
            "target": decision.target,
            "priority": decision.priority,
            "reason": decision.reason,
            "customer_impact": {
                "level": decision.customer_impact.level.value if decision.customer_impact else None,
                "description": decision.customer_impact.description if decision.customer_impact else None,
                "affected_customers": decision.customer_impact.affected_customers if decision.customer_impact else 0
            },
            "threat_assessment": {
                "severity": decision.threat_assessment.severity.value if decision.threat_assessment else None,
                "type": decision.threat_assessment.threat_type if decision.threat_assessment else None
            },
            "risk_assessment": {
                "level": decision.risk_assessment.level.value if decision.risk_assessment else None,
                "type": decision.risk_assessment.risk_type if decision.risk_assessment else None
            },
            "result": result
        }

        try:
            with open(record_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, indent=2, default=str)
            logger.info(f"   💾 Escalation record saved: {record_file.name}")
        except Exception as e:
            logger.error(f"   ❌ Failed to save escalation record: {e}")


# Global instance
_global_escalation = None

def get_escalation_system() -> SYPHONThreatRiskEscalation:
    """Get global SYPHON Threat & Risk Escalation system instance"""
    global _global_escalation
    if _global_escalation is None:
        _global_escalation = SYPHONThreatRiskEscalation()
    return _global_escalation


if __name__ == "__main__":
    # Demo
    escalation = SYPHONThreatRiskEscalation()

    # Example: Critical customer impact
    customer_impact = CustomerImpactAssessment(
        impact_id="impact_001",
        level=CustomerImpactLevel.CRITICAL,
        description="Service outage affecting 1000+ customers",
        affected_customers=1000,
        affected_features=["authentication", "payment_processing"],
        business_impact="Revenue loss: $10K/hour",
        urgency="critical"
    )

    decision = escalation.assess_and_escalate(
        context={},
        customer_impact=customer_impact
    )

    result = escalation.execute_escalation(decision)

    print(f"\n✅ Escalation complete: Level {decision.escalation_level.value} → {decision.target}")
