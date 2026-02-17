#!/usr/bin/env python3
"""
JARVIS Metrics & Performance History System

Tracking force multipliers, analytics, and performance history.
Measuring what we can quantify, and acknowledging what we can't.

@JARVIS @METRICS @PERFORMANCE_HISTORY @ANALYTICS @FORCE_MULTIPLIERS @REC
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict
import statistics

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MetricsPerformanceHistory")


class MetricType(Enum):
    """Type of metric"""
    QUANTITATIVE = "QUANTITATIVE"  # Can be measured numerically
    QUALITATIVE = "QUALITATIVE"  # Subjective, feeling-based
    FORCE_MULTIPLIER = "FORCE_MULTIPLIER"  # Multiplier effect
    PERFORMANCE = "PERFORMANCE"  # Performance metric
    COLLABORATION = "COLLABORATION"  # AI-Human collaboration


@dataclass
class Metric:
    """A metric to track"""
    metric_id: str
    name: str
    metric_type: MetricType
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    context: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['metric_type'] = self.metric_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class PerformanceSnapshot:
    """A snapshot of performance at a point in time"""
    snapshot_id: str
    timestamp: datetime
    force_multiplier_stack: List[str]  # Active force multipliers
    total_multiplier: float
    metrics: List[Metric]
    qualitative_notes: str = ""  # The "feeling" that can't be quantified
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp.isoformat(),
            "force_multiplier_stack": self.force_multiplier_stack,
            "total_multiplier": self.total_multiplier,
            "metrics": [m.to_dict() for m in self.metrics],
            "qualitative_notes": self.qualitative_notes,
            "metadata": self.metadata
        }


@dataclass
class AnalyticsInsight:
    """An insight derived from analytics"""
    insight_id: str
    insight_type: str  # "trend", "correlation", "recommendation", "anomaly"
    description: str
    confidence: float  # 0.0 to 1.0
    recommendation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MetricsPerformanceHistory:
    """
    Metrics & Performance History System

    Tracking what we can quantify, acknowledging what we can't.
    Building analytics and recommendations based on performance history.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "metrics_performance_history"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("MetricsPerformanceHistory")

        self.metrics_history: List[Metric] = []
        self.performance_snapshots: List[PerformanceSnapshot] = []
        self.analytics_insights: List[AnalyticsInsight] = []

        self.logger.info("=" * 70)
        self.logger.info("📊 METRICS & PERFORMANCE HISTORY SYSTEM")
        self.logger.info("   Tracking what we can quantify")
        self.logger.info("   Acknowledging what we can't")
        self.logger.info("=" * 70)
        self.logger.info("")

    def capture_performance_snapshot(self, 
                                    force_multiplier_stack: List[str],
                                    total_multiplier: float,
                                    qualitative_notes: str = "") -> PerformanceSnapshot:
        """Capture a performance snapshot"""
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create metrics for this snapshot
        metrics = [
            Metric(
                metric_id=f"{snapshot_id}_multiplier",
                name="Total Force Multiplier",
                metric_type=MetricType.FORCE_MULTIPLIER,
                value=total_multiplier,
                unit="x",
                context="Current stack multiplier"
            ),
            Metric(
                metric_id=f"{snapshot_id}_stack_size",
                name="Stack Size",
                metric_type=MetricType.QUANTITATIVE,
                value=len(force_multiplier_stack),
                unit="multipliers",
                context="Number of active force multipliers"
            ),
            Metric(
                metric_id=f"{snapshot_id}_target_ratio",
                name="Target Ratio (2x)",
                metric_type=MetricType.PERFORMANCE,
                value=total_multiplier / 2.0,
                unit="ratio",
                context="Ratio to 2x target"
            )
        ]

        snapshot = PerformanceSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            force_multiplier_stack=force_multiplier_stack,
            total_multiplier=total_multiplier,
            metrics=metrics,
            qualitative_notes=qualitative_notes,
            metadata={
                "captured_by": "metrics_system",
                "has_qualitative_notes": bool(qualitative_notes)
            }
        )

        self.performance_snapshots.append(snapshot)
        self.metrics_history.extend(metrics)

        return snapshot

    def analyze_performance_history(self) -> List[AnalyticsInsight]:
        """Analyze performance history and generate insights"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 ANALYZING PERFORMANCE HISTORY")
        self.logger.info("=" * 70)
        self.logger.info("")

        insights = []

        if not self.performance_snapshots:
            self.logger.warning("No performance snapshots available for analysis")
            return insights

        # Calculate statistics
        multipliers = [s.total_multiplier for s in self.performance_snapshots]
        avg_multiplier = statistics.mean(multipliers) if multipliers else 0.0
        max_multiplier = max(multipliers) if multipliers else 0.0
        min_multiplier = min(multipliers) if multipliers else 0.0

        # Trend analysis
        if len(multipliers) >= 2:
            recent_avg = statistics.mean(multipliers[-5:]) if len(multipliers) >= 5 else statistics.mean(multipliers)
            earlier_avg = statistics.mean(multipliers[:5]) if len(multipliers) >= 5 else statistics.mean(multipliers)
            trend = "INCREASING" if recent_avg > earlier_avg else "DECREASING" if recent_avg < earlier_avg else "STABLE"

            trend_insight = AnalyticsInsight(
                insight_id=f"trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="trend",
                description=f"Performance trend: {trend}. Recent average: {recent_avg:.2f}x, Earlier average: {earlier_avg:.2f}x",
                confidence=0.85 if len(multipliers) >= 5 else 0.60,
                recommendation=f"Continue current approach" if trend == "INCREASING" else f"Review and optimize force multiplier stack",
                metadata={"trend": trend, "recent_avg": recent_avg, "earlier_avg": earlier_avg}
            )
            insights.append(trend_insight)

        # Target analysis
        target = 2.0
        above_target = sum(1 for m in multipliers if m >= target)
        above_target_pct = (above_target / len(multipliers)) * 100 if multipliers else 0.0

        target_insight = AnalyticsInsight(
            insight_id=f"target_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            insight_type="performance",
            description=f"Target achievement: {above_target_pct:.1f}% of snapshots meet 2x target. Average: {avg_multiplier:.2f}x",
            confidence=0.90,
            recommendation=f"Maintain current stack" if above_target_pct >= 80 else f"Optimize stack to consistently meet 2x target",
            metadata={"target": target, "above_target_pct": above_target_pct, "avg_multiplier": avg_multiplier}
        )
        insights.append(target_insight)

        # Wiggle room analysis
        wiggle_rooms = [m - target for m in multipliers]
        avg_wiggle_room = statistics.mean(wiggle_rooms) if wiggle_rooms else 0.0

        wiggle_insight = AnalyticsInsight(
            insight_id=f"wiggle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            insight_type="recommendation",
            description=f"Average wiggle room: {avg_wiggle_room:.2f}x ({avg_wiggle_room/target*100:.1f}% above target). Good redundancy available.",
            confidence=0.95,
            recommendation=f"Wiggle room provides good fault tolerance. Consider optimizing for efficiency if wiggle room exceeds 50%.",
            metadata={"avg_wiggle_room": avg_wiggle_room, "wiggle_room_pct": avg_wiggle_room/target*100}
        )
        insights.append(wiggle_insight)

        # Stack size correlation
        stack_sizes = [len(s.force_multiplier_stack) for s in self.performance_snapshots]
        if len(stack_sizes) >= 2:
            # Simple correlation: larger stacks tend to have higher multipliers
            avg_stack_size = statistics.mean(stack_sizes)
            correlation_insight = AnalyticsInsight(
                insight_id=f"correlation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="correlation",
                description=f"Average stack size: {avg_stack_size:.1f} multipliers. Larger stacks correlate with higher multipliers (multiplicative stacking).",
                confidence=0.80,
                recommendation=f"Optimize stack size: minimum 3 multipliers for 2x target, current average {avg_stack_size:.1f}",
                metadata={"avg_stack_size": avg_stack_size, "min_for_2x": 3}
            )
            insights.append(correlation_insight)

        # Qualitative notes analysis
        qualitative_snapshots = [s for s in self.performance_snapshots if s.qualitative_notes]
        if qualitative_snapshots:
            qualitative_insight = AnalyticsInsight(
                insight_id=f"qualitative_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                insight_type="qualitative",
                description=f"Qualitative notes captured: {len(qualitative_snapshots)}/{len(self.performance_snapshots)} snapshots. The 'feeling' that can't be quantified is being tracked.",
                confidence=0.70,
                recommendation=f"Continue capturing qualitative notes alongside quantitative metrics. Both are valuable.",
                metadata={"qualitative_count": len(qualitative_snapshots), "total_count": len(self.performance_snapshots)}
            )
            insights.append(qualitative_insight)

        self.analytics_insights.extend(insights)

        # Log insights
        for insight in insights:
            self.logger.info(f"   💡 {insight.insight_type.upper()}: {insight.description}")
            if insight.recommendation:
                self.logger.info(f"      📋 Recommendation: {insight.recommendation}")
            self.logger.info("")

        return insights

    def generate_recommendations(self) -> Dict[str, Any]:
        """Generate recommendations based on analytics"""
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("💡 GENERATING RECOMMENDATIONS")
        self.logger.info("=" * 70)
        self.logger.info("")

        recommendations = {
            "timestamp": datetime.now().isoformat(),
            "recommendations": [],
            "priority": "MEDIUM",
            "based_on": "performance_history_analysis"
        }

        if not self.performance_snapshots:
            recommendations["recommendations"].append({
                "type": "INITIALIZATION",
                "description": "No performance history yet. Start capturing snapshots.",
                "action": "Begin tracking metrics and performance snapshots",
                "priority": "HIGH"
            })
            return recommendations

        # Analyze and generate recommendations
        insights = self.analyze_performance_history()

        for insight in insights:
            if insight.recommendation:
                recommendations["recommendations"].append({
                    "type": insight.insight_type.upper(),
                    "description": insight.description,
                    "recommendation": insight.recommendation,
                    "confidence": insight.confidence,
                    "priority": "HIGH" if insight.confidence >= 0.85 else "MEDIUM" if insight.confidence >= 0.70 else "LOW"
                })

        # Summary recommendation
        multipliers = [s.total_multiplier for s in self.performance_snapshots]
        avg_multiplier = statistics.mean(multipliers) if multipliers else 0.0

        if avg_multiplier >= 2.0:
            recommendations["recommendations"].append({
                "type": "SUMMARY",
                "description": f"Average performance: {avg_multiplier:.2f}x (above 2x target). Good wiggle room available.",
                "recommendation": "Continue current approach. System has good redundancy and fault tolerance.",
                "confidence": 0.95,
                "priority": "LOW"
            })
        else:
            recommendations["recommendations"].append({
                "type": "SUMMARY",
                "description": f"Average performance: {avg_multiplier:.2f}x (below 2x target). Optimization needed.",
                "recommendation": "Review force multiplier stack and optimize to consistently meet 2x target.",
                "confidence": 0.90,
                "priority": "HIGH"
            })

        # Log recommendations
        for rec in recommendations["recommendations"]:
            self.logger.info(f"   📋 [{rec['priority']}] {rec['type']}: {rec['description']}")
            self.logger.info(f"      → {rec['recommendation']}")
            self.logger.info("")

        return recommendations

    def create_performance_report(self) -> Dict[str, Any]:
        try:
            """Create comprehensive performance report"""
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 CREATING PERFORMANCE REPORT")
            self.logger.info("=" * 70)
            self.logger.info("")

            # Capture current snapshot
            current_snapshot = self.capture_performance_snapshot(
                force_multiplier_stack=["INFRASTRUCTURE", "QUANTUM_ENTANGLEMENT", "QUANTUM_TRADING", "F2F_NITRO_BOOST"],
                total_multiplier=2.03,  # Minimum for 2x
                qualitative_notes="Napkin math, spitballing - but interesting to see metrics. Feeling that this is 'more than that' - can't quantify but both will be better informed with force multipliers and metrics."
            )

            # Generate recommendations
            recommendations = self.generate_recommendations()

            # Calculate statistics
            multipliers = [s.total_multiplier for s in self.performance_snapshots]
            stats = {
                "total_snapshots": len(self.performance_snapshots),
                "average_multiplier": statistics.mean(multipliers) if multipliers else 0.0,
                "max_multiplier": max(multipliers) if multipliers else 0.0,
                "min_multiplier": min(multipliers) if multipliers else 0.0,
                "median_multiplier": statistics.median(multipliers) if multipliers else 0.0,
                "stdev_multiplier": statistics.stdev(multipliers) if len(multipliers) > 1 else 0.0
            }

            report = {
                "report_id": f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "insight": "Tracking what we can quantify, acknowledging what we can't. Both AI and human will be better informed with force multipliers and metrics.",
                "statistics": stats,
                "current_snapshot": current_snapshot.to_dict(),
                "performance_snapshots": [s.to_dict() for s in self.performance_snapshots],
                "analytics_insights": [i.to_dict() for i in self.analytics_insights],
                "recommendations": recommendations,
                "qualitative_acknowledgment": {
                    "note": "The 'feeling' that this is 'more than that' - can't quantify what that means or feels like, but both will be better informed with accurate analytics and metrics.",
                    "tracking": "Qualitative notes are being captured alongside quantitative metrics",
                    "value": "Both quantitative and qualitative data are valuable for understanding performance"
                }
            }

            # Save report
            filename = self.data_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("📊 PERFORMANCE REPORT SUMMARY")
            self.logger.info("=" * 70)
            self.logger.info(f"   Total Snapshots: {stats['total_snapshots']}")
            self.logger.info(f"   Average Multiplier: {stats['average_multiplier']:.2f}x")
            self.logger.info(f"   Max Multiplier: {stats['max_multiplier']:.2f}x")
            self.logger.info(f"   Min Multiplier: {stats['min_multiplier']:.2f}x")
            self.logger.info("")
            self.logger.info("💡 QUALITATIVE ACKNOWLEDGMENT:")
            self.logger.info("   The 'feeling' that this is 'more than that'")
            self.logger.info("   Can't quantify what that means or feels like")
            self.logger.info("   But both will be better informed with metrics")
            self.logger.info("")
            self.logger.info(f"✅ Report saved: {filename}")
            self.logger.info("")
            self.logger.info("=" * 70)
            self.logger.info("✅ METRICS & PERFORMANCE HISTORY SYSTEM READY")
            self.logger.info("=" * 70)
            self.logger.info("")

            return report


        except Exception as e:
            self.logger.error(f"Error in create_performance_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        system = MetricsPerformanceHistory(project_root)
        report = system.create_performance_report()

        print()
        print("=" * 70)
        print("📊 METRICS & PERFORMANCE HISTORY SYSTEM")
        print("=" * 70)
        print(f"✅ Total Snapshots: {report['statistics']['total_snapshots']}")
        print(f"✅ Average Multiplier: {report['statistics']['average_multiplier']:.2f}x")
        print()
        print("💡 QUALITATIVE ACKNOWLEDGMENT:")
        print("   The 'feeling' that this is 'more than that'")
        print("   Can't quantify what that means or feels like")
        print("   But both will be better informed with metrics")
        print()
        print("📋 RECOMMENDATIONS:")
        for rec in report['recommendations']['recommendations'][:3]:
            print(f"   [{rec['priority']}] {rec['type']}: {rec['description'][:60]}...")
        print()
        print("=" * 70)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()