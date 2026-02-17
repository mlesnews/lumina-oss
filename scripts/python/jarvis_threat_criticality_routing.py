#!/usr/bin/env python3
"""
JARVIS Threat & Criticality-Based Routing - Lumina-Wide
                    -LUM THE MODERN

Routes decisions across ALL of Lumina's AI infrastructure based on threat, criticality, severity, intensity, temperature, and other metrics.

Lumina Ecosystem:
- ULTRON (Local, KAIJU, KUBE)
- Iron Legion (7 Mark nodes on KAIJU_NO_8)
- MILLENNIUM_FALCON (laptop failover cluster)
- Any other Lumina clusters/nodes

Routing Logic:
- Low Priority: JARVIS solves solo (no cluster routing)
- Medium Priority: JARVIS solves solo OR engages agents/clusters
- High/Critical Priority: Requires 3-5-7-9 escalation based on metrics

Metrics Tracked Over Time:
- Criticality
- Threat Level
- Severity
- Intensity
- Temperature
- Other custom metrics

Tags: #DECISIONING_SYSTEM #THREAT #CRITICALITY #ROUTING #LUMINA #ULTRON #IRON_LEGION #METRICS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("JARVISThreatRouting")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISThreatRouting")

# Import SYPHON escalation
try:
    from scripts.python.syphon_threat_risk_escalation import (
        SYPHONThreatRiskEscalation,
        CustomerImpactAssessment,
        CustomerImpactLevel,
        ThreatAssessment,
        ThreatSeverity,
        RiskAssessment,
        RiskLevel,
        EscalationLevel,
        get_escalation_system
    )
    ESCALATION_AVAILABLE = True
except ImportError:
    ESCALATION_AVAILABLE = False
    logger.warning("⚠️  SYPHON escalation not available")

# Import decisioning engine
try:
    from scripts.python.lumina_decisioning_engine import LuminaDecisioningEngine
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    logger.warning("⚠️  Decisioning engine not available")


class PriorityLevel(Enum):
    """Priority levels for routing"""
    LOW = "low"  # JARVIS solves solo
    MEDIUM = "medium"  # JARVIS solves solo OR engages agents
    HIGH = "high"  # Requires escalation (3-5-7-9)
    CRITICAL = "critical"  # Requires escalation (3-5-7-9)


class RoutingAction(Enum):
    """Routing actions"""
    JARVIS_SOLO = "jarvis_solo"  # JARVIS handles alone
    JARVIS_WITH_AGENTS = "jarvis_with_agents"  # JARVIS + agents
    IRON_LEGION = "iron_legion"  # Route to Iron Legion
    ESCALATION_3 = "escalation_3"  # Level 3 escalation
    ESCALATION_5 = "escalation_5"  # Level 5 escalation
    ESCALATION_7 = "escalation_7"  # Level 7 escalation
    ESCALATION_9 = "escalation_9"  # Level 9 escalation


@dataclass
class ThreatMetrics:
    """Threat and criticality metrics"""
    criticality: float = 0.0  # 0.0 to 1.0
    threat_level: float = 0.0  # 0.0 to 1.0
    severity: float = 0.0  # 0.0 to 1.0
    intensity: float = 0.0  # 0.0 to 1.0
    temperature: float = 0.0  # 0.0 to 1.0 (urgency/heat)
    customer_impact: float = 0.0  # 0.0 to 1.0
    risk_score: float = 0.0  # 0.0 to 1.0
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingDecision:
    """Routing decision with metrics"""
    decision_id: str
    priority: PriorityLevel
    routing: "RoutingAction"
    target_cluster: Optional[str] = None  # ULTRON, Iron Legion, etc.
    target_node: Optional[str] = None  # Mark I-VII, specific node
    target_endpoint: Optional[str] = None  # Full endpoint URL
    escalation_level: Optional[EscalationLevel] = None
    metrics: ThreatMetrics = field(default_factory=ThreatMetrics)
    reasoning: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class JARVISThreatCriticalityRouter:
    """
    JARVIS Threat & Criticality-Based Router - Lumina-Wide

    Routes decisions across ALL of Lumina's AI infrastructure:
    - ULTRON (Local, KAIJU, KUBE)
    - Iron Legion (7 Mark nodes)
    - MILLENNIUM_FALCON (laptop failover)
    - Any other Lumina clusters

    Routes based on threat, criticality, and other metrics.
    Tracks metrics over time for analysis.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize router"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.data_dir = self.project_root / "data" / "jarvis_routing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config_file = self.config_dir / "jarvis_threat_routing_config.json"
        self.config = self._load_config()

        # Initialize systems
        self.escalation_system = None
        if ESCALATION_AVAILABLE:
            try:
                self.escalation_system = get_escalation_system()
                logger.info("✅ SYPHON escalation system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Escalation init error: {e}")

        self.decisioning_engine = None
        if DECISIONING_AVAILABLE:
            try:
                self.decisioning_engine = LuminaDecisioningEngine(self.project_root)
                logger.info("✅ Decisioning engine initialized")
            except Exception as e:
                logger.warning(f"⚠️  Decisioning init error: {e}")

        # Metrics history
        self.metrics_history: List[ThreatMetrics] = []
        self.routing_history: List[RoutingDecision] = []
        self.history_file = self.data_dir / "routing_history.jsonl"
        self.metrics_file = self.data_dir / "metrics_history.jsonl"

        logger.info("=" * 80)
        logger.info("🛡️  JARVIS THREAT & CRITICALITY ROUTER - LUMINA-WIDE")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   Routing Logic:")
        logger.info("   - Low Priority: JARVIS solves solo")
        logger.info("   - Medium Priority: JARVIS solves solo OR engages agents/clusters")
        logger.info("   - High/Critical: Requires 3-5-7-9 escalation")
        logger.info("")
        logger.info("   Clusters: ULTRON, Iron Legion, MILLENNIUM_FALCON, etc.")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "routing_thresholds": {
                "low_max": 0.3,  # Metrics < 0.3 = Low priority
                "medium_max": 0.6,  # Metrics 0.3-0.6 = Medium priority
                "high_max": 0.8,  # Metrics 0.6-0.8 = High priority
                "critical_min": 0.8  # Metrics >= 0.8 = Critical priority
            },
            "cluster_routing": {
                "low": None,  # JARVIS solo
                "medium": {
                    "clusters": ["ultron_local", "millennium_falcon"],
                    "nodes": ["mark_iii", "mark_vii"]  # Quick/fallback
                },
                "high": {
                    "clusters": ["ultron_kube", "iron_legion"],
                    "nodes": ["mark_ii", "mark_iv", "mark_v"]  # General/balanced/reasoning
                },
                "critical": {
                    "clusters": ["ultron_cluster", "iron_legion"],
                    "nodes": ["mark_i", "mark_vi"]  # Code expert / complex expert
                }
            },
            "escalation_mapping": {
                "level_3": {
                    "clusters": ["ultron_local"],
                    "nodes": ["mark_iii", "mark_vii"]  # AIQ consensus
                },
                "level_5": {
                    "clusters": ["ultron_kube", "iron_legion"],
                    "nodes": ["mark_ii", "mark_iv"]  # JC standard
                },
                "level_7": {
                    "clusters": ["ultron_cluster", "iron_legion", "azure_foundry"],
                    "nodes": ["mark_i", "mark_v"]  # JC urgent
                },
                "level_9": {
                    "clusters": ["ultron_cluster", "iron_legion", "azure_foundry"],
                    "nodes": ["mark_vi"]  # JHC critical
                }
            },
            "cluster_endpoints": {
                "ultron_local": "http://localhost:11434",
                "ultron_kube": "http://localhost:11435",
                "ultron_cluster": "http://localhost:11436",
                "iron_legion": "http://<NAS_IP>:3000",
                "iron_legion_mark_i": "http://<NAS_IP>:3001",
                "iron_legion_mark_ii": "http://<NAS_IP>:3002",
                "iron_legion_mark_iii": "http://<NAS_IP>:3003",
                "iron_legion_mark_iv": "http://<NAS_IP>:3004",
                "iron_legion_mark_v": "http://<NAS_IP>:3005",
                "iron_legion_mark_vi": "http://<NAS_IP>:3006",
                "iron_legion_mark_vii": "http://<NAS_IP>:3007",
                "millennium_falcon": "http://localhost:11436",
                "azure_foundry": "https://api.foundry.azure.com",
                "azure_foundry_gpt4": "https://api.foundry.azure.com/models/gpt-4",
                "azure_foundry_gpt35": "https://api.foundry.azure.com/models/gpt-3.5-turbo"
            },
            "azure_foundry": {
                "enabled": True,
                "routing_enabled": True,
                "cost_threshold": 0.10,
                "latency_threshold_ms": 2000,
                "prefer_local": True,
                "fallback_to_azure": True
            },
            "metrics_weights": {
                "criticality": 0.25,
                "threat_level": 0.20,
                "severity": 0.15,
                "intensity": 0.10,
                "temperature": 0.10,
                "customer_impact": 0.15,  # Higher weight
                "risk_score": 0.05
            },
            "track_metrics_over_time": True,
            "metrics_retention_days": 90
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️  Error loading config: {e}, using defaults")

        return default_config

    def assess_metrics(
        self,
        criticality: Optional[float] = None,
        threat_level: Optional[float] = None,
        severity: Optional[float] = None,
        intensity: Optional[float] = None,
        temperature: Optional[float] = None,
        customer_impact: Optional[float] = None,
        risk_score: Optional[float] = None,
        custom_metrics: Optional[Dict[str, float]] = None,
        customer_impact_obj: Optional[CustomerImpactAssessment] = None,
        threat_assessment: Optional[ThreatAssessment] = None,
        risk_assessment: Optional[RiskAssessment] = None
    ) -> ThreatMetrics:
        """
        Assess threat and criticality metrics

        Can accept direct values or assessment objects
        """
        metrics = ThreatMetrics()

        # Map assessment objects to metrics if provided
        if customer_impact_obj:
            impact_map = {
                CustomerImpactLevel.NONE: 0.0,
                CustomerImpactLevel.LOW: 0.25,
                CustomerImpactLevel.MEDIUM: 0.5,
                CustomerImpactLevel.HIGH: 0.75,
                CustomerImpactLevel.CRITICAL: 1.0
            }
            metrics.customer_impact = impact_map.get(customer_impact_obj.level, 0.0)

        if threat_assessment:
            severity_map = {
                ThreatSeverity.LOW: 0.25,
                ThreatSeverity.MEDIUM: 0.5,
                ThreatSeverity.HIGH: 0.75,
                ThreatSeverity.CRITICAL: 1.0
            }
            metrics.threat_level = severity_map.get(threat_assessment.severity, 0.0)
            metrics.severity = threat_assessment.confidence

        if risk_assessment:
            risk_map = {
                RiskLevel.LOW: 0.25,
                RiskLevel.MEDIUM: 0.5,
                RiskLevel.HIGH: 0.75,
                RiskLevel.CRITICAL: 1.0
            }
            metrics.risk_score = risk_map.get(risk_assessment.level, 0.0)
            metrics.intensity = risk_assessment.impact

        # Override with direct values if provided
        if criticality is not None:
            metrics.criticality = max(0.0, min(1.0, criticality))
        if threat_level is not None:
            metrics.threat_level = max(0.0, min(1.0, threat_level))
        if severity is not None:
            metrics.severity = max(0.0, min(1.0, severity))
        if intensity is not None:
            metrics.intensity = max(0.0, min(1.0, intensity))
        if temperature is not None:
            metrics.temperature = max(0.0, min(1.0, temperature))
        if customer_impact is not None:
            metrics.customer_impact = max(0.0, min(1.0, customer_impact))
        if risk_score is not None:
            metrics.risk_score = max(0.0, min(1.0, risk_score))
        if custom_metrics:
            metrics.custom_metrics = custom_metrics

        # Save metrics to history
        if self.config["track_metrics_over_time"]:
            self.metrics_history.append(metrics)
            self._save_metrics(metrics)

        return metrics

    def calculate_priority(self, metrics: ThreatMetrics) -> PriorityLevel:
        """Calculate priority level from metrics"""
        weights = self.config["metrics_weights"]

        # Calculate weighted score
        weighted_score = (
            metrics.criticality * weights["criticality"] +
            metrics.threat_level * weights["threat_level"] +
            metrics.severity * weights["severity"] +
            metrics.intensity * weights["intensity"] +
            metrics.temperature * weights["temperature"] +
            metrics.customer_impact * weights["customer_impact"] +
            metrics.risk_score * weights["risk_score"]
        )

        # Add custom metrics if any
        if metrics.custom_metrics:
            custom_weight = 0.05 / len(metrics.custom_metrics)  # Distribute 5% among custom metrics
            for value in metrics.custom_metrics.values():
                weighted_score += value * custom_weight

        # Determine priority
        thresholds = self.config["routing_thresholds"]

        if weighted_score >= thresholds["critical_min"]:
            return PriorityLevel.CRITICAL
        elif weighted_score >= thresholds["high_max"]:
            return PriorityLevel.HIGH
        elif weighted_score >= thresholds["medium_max"]:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    def route_decision(
        self,
        metrics: ThreatMetrics,
        context: Optional[Dict[str, Any]] = None,
        customer_impact_obj: Optional[CustomerImpactAssessment] = None,
        threat_assessment: Optional[ThreatAssessment] = None,
        risk_assessment: Optional[RiskAssessment] = None
    ) -> RoutingDecision:
        """
        Route decision based on threat, criticality, and metrics

        Returns routing decision with target Mark node or escalation level
        """
        logger.info("=" * 80)
        logger.info("🔍 ASSESSING ROUTING DECISION")
        logger.info("=" * 80)

        # Calculate priority
        priority = self.calculate_priority(metrics)
        logger.info(f"   Priority: {priority.value.upper()}")
        logger.info(f"   Metrics:")
        logger.info(f"      Criticality: {metrics.criticality:.2f}")
        logger.info(f"      Threat Level: {metrics.threat_level:.2f}")
        logger.info(f"      Severity: {metrics.severity:.2f}")
        logger.info(f"      Intensity: {metrics.intensity:.2f}")
        logger.info(f"      Temperature: {metrics.temperature:.2f}")
        logger.info(f"      Customer Impact: {metrics.customer_impact:.2f}")
        logger.info(f"      Risk Score: {metrics.risk_score:.2f}")

        # Determine routing
        routing = None
        target_mark = None
        escalation_level = None
        reasoning = ""

        if priority == PriorityLevel.LOW:
            # Low Priority: JARVIS solves solo
            routing = RoutingAction.JARVIS_SOLO
            target_cluster = None
            target_node = None
            target_endpoint = None
            reasoning = "Low priority - JARVIS handles solo"
            logger.info("   🎯 Routing: JARVIS SOLO")

        elif priority == PriorityLevel.MEDIUM:
            # Medium Priority: JARVIS solves solo OR engages agents
            # Choose based on complexity or agent availability
            if metrics.intensity > 0.5 or metrics.temperature > 0.5:
                # Higher intensity/temperature = engage agents/clusters
                routing = RoutingAction.JARVIS_WITH_AGENTS
                medium_config = self.config["cluster_routing"]["medium"]
                cluster_options = medium_config.get("clusters", [])
                node_options = medium_config.get("nodes", [])

                # Select cluster and node
                target_cluster = cluster_options[0] if cluster_options else None
                target_node = node_options[0] if node_options else None

                # Get endpoint
                if target_cluster:
                    target_endpoint = self.config["cluster_endpoints"].get(target_cluster)
                elif target_node:
                    endpoint_key = f"iron_legion_{target_node}"
                    target_endpoint = self.config["cluster_endpoints"].get(endpoint_key)

                reasoning = f"Medium priority with higher intensity/temperature - JARVIS with {target_cluster or target_node}"
                logger.info(f"   🎯 Routing: JARVIS WITH AGENTS → {target_cluster or target_node}")
            else:
                # Lower intensity = JARVIS solo
                routing = RoutingAction.JARVIS_SOLO
                target_cluster = None
                target_node = None
                target_endpoint = None
                reasoning = "Medium priority - JARVIS handles solo"
                logger.info("   🎯 Routing: JARVIS SOLO")

        else:
            # High/Critical Priority: Requires 3-5-7-9 escalation
            if self.escalation_system:
                # Use SYPHON escalation
                escalation_decision = self.escalation_system.assess_and_escalate(
                    context=context or {},
                    customer_impact=customer_impact_obj,
                    threat_assessment=threat_assessment,
                    risk_assessment=risk_assessment
                )

                escalation_level = escalation_decision.escalation_level

                # Map escalation level to routing
                level_key = f"level_{escalation_level.value}"
                escalation_config = self.config["escalation_mapping"].get(level_key, {})

                cluster_options = escalation_config.get("clusters", [])
                node_options = escalation_config.get("nodes", [])

                # Select cluster and node
                target_cluster = cluster_options[0] if cluster_options else None
                target_node = node_options[0] if node_options else None

                # Get endpoint
                if target_cluster:
                    target_endpoint = self.config["cluster_endpoints"].get(target_cluster)
                elif target_node:
                    endpoint_key = f"iron_legion_{target_node}"
                    target_endpoint = self.config["cluster_endpoints"].get(endpoint_key)

                # Set routing action
                if escalation_level == EscalationLevel.LEVEL_9:
                    routing = RoutingAction.ESCALATION_9
                    reasoning = f"Level 9 escalation (CRITICAL) → {target_cluster or target_node}"
                    logger.info(f"   🚨 Routing: ESCALATION 9 → {target_cluster or target_node}")
                elif escalation_level == EscalationLevel.LEVEL_7:
                    routing = RoutingAction.ESCALATION_7
                    reasoning = f"Level 7 escalation (HIGH) → {target_cluster or target_node}"
                    logger.info(f"   🚨 Routing: ESCALATION 7 → {target_cluster or target_node}")
                elif escalation_level == EscalationLevel.LEVEL_5:
                    routing = RoutingAction.ESCALATION_5
                    reasoning = f"Level 5 escalation (MEDIUM) → {target_cluster or target_node}"
                    logger.info(f"   🚨 Routing: ESCALATION 5 → {target_cluster or target_node}")
                else:  # LEVEL_3
                    routing = RoutingAction.ESCALATION_3
                    reasoning = f"Level 3 escalation (LOW) → {target_cluster or target_node}"
                    logger.info(f"   🚨 Routing: ESCALATION 3 → {target_cluster or target_node}")
            else:
                # Fallback: Route to high-priority clusters/nodes
                routing = RoutingAction.IRON_LEGION
                priority_key = "critical" if priority == PriorityLevel.CRITICAL else "high"
                priority_config = self.config["cluster_routing"].get(priority_key, {})

                cluster_options = priority_config.get("clusters", [])
                node_options = priority_config.get("nodes", [])

                target_cluster = cluster_options[0] if cluster_options else None
                target_node = node_options[0] if node_options else None

                # Get endpoint
                if target_cluster:
                    target_endpoint = self.config["cluster_endpoints"].get(target_cluster)
                elif target_node:
                    endpoint_key = f"iron_legion_{target_node}"
                    target_endpoint = self.config["cluster_endpoints"].get(endpoint_key)

                reasoning = f"{priority.value.upper()} priority - Route to {target_cluster or target_node}"
                logger.info(f"   🎯 Routing: {target_cluster or target_node}")

        # Create routing decision
        decision = RoutingDecision(
            decision_id=f"route_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            priority=priority,
            routing=routing,
            target_cluster=target_cluster,
            target_node=target_node,
            target_endpoint=target_endpoint,
            escalation_level=escalation_level,
            metrics=metrics,
            reasoning=reasoning
        )

        # Save to history
        self.routing_history.append(decision)
        self._save_routing_decision(decision)

        logger.info("=" * 80)

        return decision

    def _save_metrics(self, metrics: ThreatMetrics):
        """Save metrics to history"""
        try:
            metrics_dict = asdict(metrics)
            metrics_dict["timestamp"] = metrics.timestamp.isoformat()

            with open(self.metrics_file, 'a') as f:
                f.write(json.dumps(metrics_dict, default=str) + '\n')
        except Exception as e:
            logger.warning(f"⚠️  Error saving metrics: {e}")

    def _save_routing_decision(self, decision: RoutingDecision):
        """Save routing decision to history"""
        try:
            decision_dict = asdict(decision)
            decision_dict["priority"] = decision.priority.value
            decision_dict["routing"] = decision.routing.value
            decision_dict["timestamp"] = decision.timestamp.isoformat()
            if decision.escalation_level:
                decision_dict["escalation_level"] = decision.escalation_level.value

            with open(self.history_file, 'a') as f:
                f.write(json.dumps(decision_dict, default=str) + '\n')
        except Exception as e:
            logger.warning(f"⚠️  Error saving routing decision: {e}")

    def get_metrics_over_time(
        self,
        days: int = 7,
        metric_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get metrics over time for analysis"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # Load from file if needed
        if not self.metrics_history:
            self._load_metrics_history()

        filtered = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_date
        ]

        if metric_name:
            return [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "value": getattr(m, metric_name, 0.0)
                }
                for m in filtered
            ]

        return [asdict(m) for m in filtered]


def main():
    """Main function"""
    router = JARVISThreatCriticalityRouter()

    # Example: Assess and route
    metrics = router.assess_metrics(
        criticality=0.7,
        threat_level=0.6,
        severity=0.5,
        intensity=0.4,
        temperature=0.3,
        customer_impact=0.8,
        risk_score=0.5
    )

    decision = router.route_decision(metrics)

    logger.info(f"\n✅ Routing Decision: {decision.routing.value}")
    logger.info(f"   Target Cluster: {decision.target_cluster}")
    logger.info(f"   Target Node: {decision.target_node}")
    logger.info(f"   Endpoint: {decision.target_endpoint}")
    logger.info(f"   Reasoning: {decision.reasoning}")

    return 0


if __name__ == "__main__":


    sys.exit(main())