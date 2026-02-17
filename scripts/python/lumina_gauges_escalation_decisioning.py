#!/usr/bin/env python3
"""
LUMINA Gauges Escalation & Decisioning System

#ESCALATION #DECISIONING #OPERATOR #ARTIFICIAL-INTELLIGENCE

Monitors gauge thresholds and triggers:
- Escalation when critical thresholds exceeded
- Decisioning for automated responses
- Operator alerts for manual intervention
- AI recommendations for optimization

Tags: #escalation #decisioning #operator #ai #monitoring
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from lumina_live_vehicle_gauges import LUMINALiveVehicleGauges, GaugeType, LayerType

logger = get_logger("LUMINAGaugesEscalationDecisioning")


class EscalationLevel(Enum):
    """Escalation levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DecisionType(Enum):
    """Decision types"""
    AUTOMATED = "automated"  # AI handles automatically
    OPERATOR = "operator"  # Requires operator intervention
    HYBRID = "hybrid"  # AI recommends, operator decides


@dataclass
class EscalationEvent:
    """Escalation event"""
    event_id: str
    layer: LayerType
    gauge_type: GaugeType
    current_value: float
    threshold_value: float
    escalation_level: EscalationLevel
    timestamp: datetime
    message: str
    recommended_action: str
    decision_type: DecisionType

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'event_id': self.event_id,
            'layer': self.layer.value,
            'gauge_type': self.gauge_type.value,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'escalation_level': self.escalation_level.value,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'recommended_action': self.recommended_action,
            'decision_type': self.decision_type.value
        }
        return result


class LUMINAGaugesEscalationDecisioning:
    """
    LUMINA Gauges Escalation & Decisioning System

    Monitors gauges and triggers escalation/decisioning
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize escalation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "escalation_decisioning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.gauges = LUMINALiveVehicleGauges(project_root)

        # Thresholds
        self.thresholds = {
            EscalationLevel.WARNING: 70.0,  # 70% triggers warning
            EscalationLevel.CRITICAL: 85.0,  # 85% triggers critical
            EscalationLevel.EMERGENCY: 95.0  # 95% triggers emergency
        }

        # Escalation history
        self.escalation_history: List[EscalationEvent] = []

        logger.info("=" * 80)
        logger.info("🚨 LUMINA GAUGES ESCALATION & DECISIONING SYSTEM")
        logger.info("=" * 80)
        logger.info("   #ESCALATION #DECISIONING #OPERATOR #ARTIFICIAL-INTELLIGENCE")
        logger.info("=" * 80)
        logger.info("")

    def check_escalations(self) -> List[EscalationEvent]:
        """Check all gauges for escalation conditions"""
        events = []

        # Update gauges first
        self.gauges.update_all_gauges()

        # Check each layer
        for layer, layer_state in self.gauges.layer_states.items():
            for gauge_name, gauge in layer_state.gauges.items():
                # Determine escalation level
                escalation_level = self._determine_escalation_level(gauge.percentage)

                if escalation_level != EscalationLevel.INFO:
                    event = self._create_escalation_event(
                        layer=layer,
                        gauge_type=gauge.gauge_type,
                        current_value=gauge.value,
                        percentage=gauge.percentage,
                        escalation_level=escalation_level
                    )
                    events.append(event)

        # Store events
        self.escalation_history.extend(events)

        return events

    def _determine_escalation_level(self, percentage: float) -> EscalationLevel:
        """Determine escalation level from percentage"""
        if percentage >= self.thresholds[EscalationLevel.EMERGENCY]:
            return EscalationLevel.EMERGENCY
        elif percentage >= self.thresholds[EscalationLevel.CRITICAL]:
            return EscalationLevel.CRITICAL
        elif percentage >= self.thresholds[EscalationLevel.WARNING]:
            return EscalationLevel.WARNING
        return EscalationLevel.INFO

    def _create_escalation_event(
        self,
        layer: LayerType,
        gauge_type: GaugeType,
        current_value: float,
        percentage: float,
        escalation_level: EscalationLevel
    ) -> EscalationEvent:
        """Create escalation event"""
        event_id = f"escalation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine decision type
        if escalation_level == EscalationLevel.EMERGENCY:
            decision_type = DecisionType.OPERATOR  # Emergency requires operator
        elif escalation_level == EscalationLevel.CRITICAL:
            decision_type = DecisionType.HYBRID  # Critical: AI recommends, operator decides
        else:
            decision_type = DecisionType.AUTOMATED  # Warning: AI can handle

        # Generate message and recommendation
        message = f"{layer.value.upper()} {gauge_type.value.upper()} at {percentage:.1f}% ({escalation_level.value.upper()})"
        recommended_action = self._generate_recommendation(layer, gauge_type, percentage, escalation_level)

        return EscalationEvent(
            event_id=event_id,
            layer=layer,
            gauge_type=gauge_type,
            current_value=current_value,
            threshold_value=self.thresholds.get(escalation_level, 0.0),
            escalation_level=escalation_level,
            timestamp=datetime.now(),
            message=message,
            recommended_action=recommended_action,
            decision_type=decision_type
        )

    def _generate_recommendation(
        self,
        layer: LayerType,
        gauge_type: GaugeType,
        percentage: float,
        escalation_level: EscalationLevel
    ) -> str:
        """Generate AI recommendation"""
        recommendations = {
            (LayerType.MEMORY, GaugeType.FUEL): "Consider freeing memory or scaling up resources",
            (LayerType.CPU, GaugeType.RPM): "Reduce CPU load or add processing capacity",
            (LayerType.STORAGE, GaugeType.WEIGHT): "Clean up storage or expand capacity",
            (LayerType.NETWORK, GaugeType.INTENSITY): "Optimize network traffic or increase bandwidth",
            (LayerType.SYSTEM, GaugeType.TEMPERATURE): "Reduce system load or improve cooling",
            (LayerType.WORKFLOW, GaugeType.SPEEDOMETER): "Optimize workflows or reduce concurrent operations",
            (LayerType.AI, GaugeType.INTENSITY): "Throttle AI requests or scale AI infrastructure"
        }

        key = (layer, gauge_type)
        base_recommendation = recommendations.get(key, "Monitor and optimize system resources")

        if escalation_level == EscalationLevel.EMERGENCY:
            return f"🚨 EMERGENCY: {base_recommendation} - IMMEDIATE ACTION REQUIRED"
        elif escalation_level == EscalationLevel.CRITICAL:
            return f"⚠️  CRITICAL: {base_recommendation} - Action needed soon"
        else:
            return f"ℹ️  WARNING: {base_recommendation} - Monitor closely"

    def get_operator_alerts(self) -> List[EscalationEvent]:
        """Get alerts requiring operator intervention"""
        return [
            e for e in self.escalation_history[-100:]  # Last 100 events
            if e.decision_type in [DecisionType.OPERATOR, DecisionType.HYBRID]
        ]

    def get_ai_recommendations(self) -> List[EscalationEvent]:
        """Get events where AI can take automated action"""
        return [
            e for e in self.escalation_history[-100:]
            if e.decision_type == DecisionType.AUTOMATED
        ]

    def print_escalation_report(self):
        """Print escalation report"""
        events = self.check_escalations()

        print("\n" + "=" * 80)
        print("🚨 ESCALATION & DECISIONING REPORT")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Events Detected: {len(events)}")
        print("")

        if events:
            # Group by escalation level
            by_level = {}
            for event in events:
                level = event.escalation_level.value
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(event)

            for level in ["emergency", "critical", "warning"]:
                if level in by_level:
                    print(f"🚨 {level.upper()}: {len(by_level[level])} events")
                    print("-" * 80)
                    for event in by_level[level]:
                        print(f"   {event.message}")
                        print(f"   Action: {event.recommended_action}")
                        print(f"   Decision: {event.decision_type.value}")
                        print("")
        else:
            print("✅ No escalations - All systems normal")
            print("")

        # Operator alerts
        operator_alerts = self.get_operator_alerts()
        if operator_alerts:
            print("👤 OPERATOR ALERTS:")
            print("-" * 80)
            for alert in operator_alerts[:5]:  # Top 5
                print(f"   {alert.message}")
                print(f"   Recommendation: {alert.recommended_action}")
                print("")

        # AI recommendations
        ai_recommendations = self.get_ai_recommendations()
        if ai_recommendations:
            print("🤖 AI RECOMMENDATIONS:")
            print("-" * 80)
            for rec in ai_recommendations[:5]:  # Top 5
                print(f"   {rec.message}")
                print(f"   Action: {rec.recommended_action}")
                print("")

        print("=" * 80)
        print("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Gauges Escalation & Decisioning")
    parser.add_argument('--check', action='store_true', help='Check for escalations')
    parser.add_argument('--report', action='store_true', help='Print escalation report')
    parser.add_argument('--operator-alerts', action='store_true', help='Show operator alerts')
    parser.add_argument('--ai-recommendations', action='store_true', help='Show AI recommendations')

    args = parser.parse_args()

    escalation = LUMINAGaugesEscalationDecisioning()

    if args.check or args.report:
        escalation.print_escalation_report()

    elif args.operator_alerts:
        alerts = escalation.get_operator_alerts()
        print(f"\n👤 OPERATOR ALERTS: {len(alerts)}")
        for alert in alerts[:10]:
            print(f"   {alert.message}")
            print(f"   {alert.recommended_action}")
            print("")

    elif args.ai_recommendations:
        recommendations = escalation.get_ai_recommendations()
        print(f"\n🤖 AI RECOMMENDATIONS: {len(recommendations)}")
        for rec in recommendations[:10]:
            print(f"   {rec.message}")
            print(f"   {rec.recommended_action}")
            print("")

    else:
        print("\n" + "=" * 80)
        print("🚨 LUMINA GAUGES ESCALATION & DECISIONING")
        print("=" * 80)
        print("   Use --check or --report to check escalations")
        print("   Use --operator-alerts to show operator alerts")
        print("   Use --ai-recommendations to show AI recommendations")
        print("=" * 80)
        print("")


if __name__ == "__main__":


    main()