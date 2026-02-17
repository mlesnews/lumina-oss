#!/usr/bin/env python3
"""
JARVIS SYPHON Performance Net Gains Analysis
SYPHONs systems for perfect percentage net gains and sustainable profit margins

@JARVIS @SYPHON @PERFORMANCE @NETGAINS @PROFIT @MARGINS @SCALING
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSyphonPerformance")


@dataclass
class PerformanceMetric:
    """Performance metric"""
    metric_name: str
    current_value: float
    baseline_value: float
    net_gain_percent: float
    category: str  # cpu, memory, workflow, financial, etc.
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "baseline_value": self.baseline_value,
            "net_gain_percent": self.net_gain_percent,
            "category": self.category,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ScalingRecommendation:
    """Hardware/software scaling recommendation"""
    recommendation_id: str
    type: str  # hardware, software, hybrid
    description: str
    estimated_cost: float
    estimated_gain_percent: float
    roi_months: float
    sustainability_score: float  # 0-1
    priority: str  # low, medium, high, critical

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "type": self.type,
            "description": self.description,
            "estimated_cost": self.estimated_cost,
            "estimated_gain_percent": self.estimated_gain_percent,
            "roi_months": self.roi_months,
            "sustainability_score": self.sustainability_score,
            "priority": self.priority
        }


@dataclass
class ProfitMarginAnalysis:
    """Profit margin analysis"""
    analysis_id: str
    current_margin_percent: float
    target_margin_percent: float
    gap_percent: float
    sustainability_level: str  # low, medium, high, optimal
    recommendations: List[ScalingRecommendation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "analysis_id": self.analysis_id,
            "current_margin_percent": self.current_margin_percent,
            "target_margin_percent": self.target_margin_percent,
            "gap_percent": self.gap_percent,
            "sustainability_level": self.sustainability_level,
            "recommendations": [r.to_dict() for r in self.recommendations]
        }


class JARVISSyphonPerformanceNetGains:
    """
    SYPHON Performance Net Gains Analysis System

    SYPHONs systems to extract:
    - Performance percentage net gains
    - Hardware/software scaling opportunities
    - Sustainable profit margin analysis
    - ROI calculations
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON performance analysis"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "syphon_performance"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("🔍 JARVIS SYPHON PERFORMANCE NET GAINS")
        logger.info("   Extracting Perfect Percentage Net Gains")
        logger.info("   Analyzing Hardware/Software Scaling")
        logger.info("   Formulating Sustainable Profit Margins")
        logger.info("=" * 70)
        logger.info("")

    def syphon_performance_metrics(self) -> List[PerformanceMetric]:
        """SYPHON performance metrics from various systems"""
        logger.info("🔍 SYPHONING PERFORMANCE METRICS...")
        logger.info("")

        metrics = []

        # 1. CPU/Workflow Performance
        logger.info("1. CPU/WORKFLOW PERFORMANCE")
        logger.info("-" * 70)
        try:
            cpu_status_file = self.project_root / "data" / "workflow_cpu" / "cpu_status_*.json"
            cpu_files = list(self.project_root.glob("data/workflow_cpu/cpu_status_*.json"))
            if cpu_files:
                latest_cpu = sorted(cpu_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                with open(latest_cpu, 'r') as f:
                    cpu_data = json.load(f)

                active_cores = cpu_data.get("active_cores", 0)
                max_cores = cpu_data.get("max_cores", 4)
                utilization = (active_cores / max_cores * 100) if max_cores > 0 else 0

                # Baseline: 4 cores at 75% = 3 effective cores
                baseline_utilization = 75.0
                net_gain = ((utilization - baseline_utilization) / baseline_utilization * 100) if baseline_utilization > 0 else 0

                metrics.append(PerformanceMetric(
                    metric_name="CPU Utilization",
                    current_value=utilization,
                    baseline_value=baseline_utilization,
                    net_gain_percent=net_gain,
                    category="cpu"
                ))

                logger.info(f"   CPU Utilization: {utilization:.1f}% (Baseline: {baseline_utilization:.1f}%)")
                logger.info(f"   Net Gain: {net_gain:+.1f}%")
        except Exception as e:
            logger.warning(f"   ⚠️  Error SYPHONing CPU metrics: {e}")

        # 2. Workflow Execution Performance
        logger.info("")
        logger.info("2. WORKFLOW EXECUTION PERFORMANCE")
        logger.info("-" * 70)
        try:
            ask_chain_files = list(self.project_root.glob("data/ask_chaining/ask_chain_execution_*.json"))
            if ask_chain_files:
                latest_chain = sorted(ask_chain_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                with open(latest_chain, 'r') as f:
                    chain_data = json.load(f)

                success_count = chain_data.get("success_count", 0)
                failed_count = chain_data.get("failed_count", 0)
                total = success_count + failed_count
                success_rate = (success_count / total * 100) if total > 0 else 0

                # Baseline: 80% success rate
                baseline_success = 80.0
                net_gain = ((success_rate - baseline_success) / baseline_success * 100) if baseline_success > 0 else 0

                metrics.append(PerformanceMetric(
                    metric_name="Workflow Success Rate",
                    current_value=success_rate,
                    baseline_value=baseline_success,
                    net_gain_percent=net_gain,
                    category="workflow"
                ))

                logger.info(f"   Success Rate: {success_rate:.1f}% (Baseline: {baseline_success:.1f}%)")
                logger.info(f"   Net Gain: {net_gain:+.1f}%")
        except Exception as e:
            logger.warning(f"   ⚠️  Error SYPHONing workflow metrics: {e}")

        # 3. System Validation Performance
        logger.info("")
        logger.info("3. SYSTEM VALIDATION PERFORMANCE")
        logger.info("-" * 70)
        try:
            validation_files = list(self.project_root.glob("data/system_validation/deep_validation_*.json"))
            if validation_files:
                latest_validation = sorted(validation_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
                with open(latest_validation, 'r') as f:
                    validation_data = json.load(f)

                summary = validation_data.get("summary", {})
                pass_rate_str = summary.get("pass_rate", "0%")
                pass_rate = float(pass_rate_str.rstrip("%"))

                # Baseline: 85% pass rate
                baseline_pass = 85.0
                net_gain = ((pass_rate - baseline_pass) / baseline_pass * 100) if baseline_pass > 0 else 0

                metrics.append(PerformanceMetric(
                    metric_name="System Validation Pass Rate",
                    current_value=pass_rate,
                    baseline_value=baseline_pass,
                    net_gain_percent=net_gain,
                    category="validation"
                ))

                logger.info(f"   Pass Rate: {pass_rate:.1f}% (Baseline: {baseline_pass:.1f}%)")
                logger.info(f"   Net Gain: {net_gain:+.1f}%")
        except Exception as e:
            logger.warning(f"   ⚠️  Error SYPHONing validation metrics: {e}")

        logger.info("")
        logger.info(f"✅ Extracted {len(metrics)} performance metrics")

        return metrics

    def analyze_scaling_opportunities(self, metrics: List[PerformanceMetric]) -> List[ScalingRecommendation]:
        """Analyze hardware/software scaling opportunities"""
        logger.info("")
        logger.info("🔍 ANALYZING SCALING OPPORTUNITIES...")
        logger.info("")

        recommendations = []

        # Analyze CPU metrics
        cpu_metrics = [m for m in metrics if m.category == "cpu"]
        if cpu_metrics:
            cpu_metric = cpu_metrics[0]
            if cpu_metric.current_value > 90:  # High utilization
                recommendations.append(ScalingRecommendation(
                    recommendation_id="scaling_001",
                    type="hardware",
                    description="Upgrade to 8-core CPU for 2x workflow capacity",
                    estimated_cost=500.0,
                    estimated_gain_percent=100.0,  # Double capacity
                    roi_months=6.0,
                    sustainability_score=0.8,
                    priority="high"
                ))

                recommendations.append(ScalingRecommendation(
                    recommendation_id="scaling_002",
                    type="software",
                    description="Optimize workflow execution with async batching",
                    estimated_cost=0.0,  # Software optimization
                    estimated_gain_percent=25.0,
                    roi_months=0.0,  # Immediate
                    sustainability_score=0.9,
                    priority="medium"
                ))

        # Analyze workflow metrics
        workflow_metrics = [m for m in metrics if m.category == "workflow"]
        if workflow_metrics:
            workflow_metric = workflow_metrics[0]
            if workflow_metric.net_gain_percent < 0:  # Below baseline
                recommendations.append(ScalingRecommendation(
                    recommendation_id="scaling_003",
                    type="hybrid",
                    description="Implement workflow retry logic + better error handling",
                    estimated_cost=200.0,
                    estimated_gain_percent=15.0,
                    roi_months=3.0,
                    sustainability_score=0.85,
                    priority="high"
                ))

        # Analyze validation metrics
        validation_metrics = [m for m in metrics if m.category == "validation"]
        if validation_metrics:
            validation_metric = validation_metrics[0]
            if validation_metric.current_value < 95:  # Below 95%
                recommendations.append(ScalingRecommendation(
                    recommendation_id="scaling_004",
                    type="software",
                    description="Automated syntax fixer + validation pre-checks",
                    estimated_cost=100.0,
                    estimated_gain_percent=8.0,  # Get to 100%
                    roi_months=2.0,
                    sustainability_score=0.9,
                    priority="medium"
                ))

        # General scaling recommendations
        recommendations.append(ScalingRecommendation(
            recommendation_id="scaling_005",
            type="hybrid",
            description="Add GPU acceleration for AI/ML workflows (if applicable)",
            estimated_cost=1500.0,
            estimated_gain_percent=200.0,  # 3x for AI workloads
            roi_months=12.0,
            sustainability_score=0.7,
            priority="low"
        ))

        logger.info(f"✅ Identified {len(recommendations)} scaling opportunities")

        return recommendations

    def calculate_profit_margins(self, metrics: List[PerformanceMetric], 
                                recommendations: List[ScalingRecommendation]) -> ProfitMarginAnalysis:
        """Calculate sustainable profit margins"""
        logger.info("")
        logger.info("💰 CALCULATING PROFIT MARGINS...")
        logger.info("")

        # Calculate current efficiency (weighted average of net gains)
        if metrics:
            avg_net_gain = sum(m.net_gain_percent for m in metrics) / len(metrics)
        else:
            avg_net_gain = 0.0

        # Estimate current margin based on efficiency
        # Higher efficiency = higher margin potential
        current_margin = 20.0 + (avg_net_gain * 0.5)  # Base 20% + efficiency bonus
        current_margin = max(10.0, min(50.0, current_margin))  # Clamp 10-50%

        # Target margin (sustainable)
        target_margin = 35.0  # Industry standard for SaaS/tech

        gap = target_margin - current_margin

        # Determine sustainability
        if current_margin >= 30.0:
            sustainability = "optimal"
        elif current_margin >= 25.0:
            sustainability = "high"
        elif current_margin >= 20.0:
            sustainability = "medium"
        else:
            sustainability = "low"

        # Filter recommendations by ROI and sustainability
        sustainable_recommendations = [
            r for r in recommendations
            if r.sustainability_score >= 0.7 and r.roi_months <= 12
        ]

        # Sort by priority and ROI
        sustainable_recommendations.sort(
            key=lambda x: (
                {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(x.priority, 0),
                -x.estimated_gain_percent / max(x.roi_months, 0.1)  # Gain per month
            ),
            reverse=True
        )

        analysis = ProfitMarginAnalysis(
            analysis_id=f"profit_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            current_margin_percent=current_margin,
            target_margin_percent=target_margin,
            gap_percent=gap,
            sustainability_level=sustainability,
            recommendations=sustainable_recommendations[:5]  # Top 5
        )

        logger.info(f"   Current Margin: {current_margin:.1f}%")
        logger.info(f"   Target Margin: {target_margin:.1f}%")
        logger.info(f"   Gap: {gap:+.1f}%")
        logger.info(f"   Sustainability: {sustainability.upper()}")
        logger.info(f"   Top Recommendations: {len(analysis.recommendations)}")

        return analysis

    def generate_performance_report(self) -> Dict[str, Any]:
        try:
            """Generate complete performance report"""
            logger.info("")
            logger.info("=" * 70)
            logger.info("📊 GENERATING PERFORMANCE REPORT")
            logger.info("=" * 70)
            logger.info("")

            # SYPHON metrics
            metrics = self.syphon_performance_metrics()

            # Analyze scaling
            recommendations = self.analyze_scaling_opportunities(metrics)

            # Calculate margins
            profit_analysis = self.calculate_profit_margins(metrics, recommendations)

            # Generate report
            report = {
                "report_id": f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "generated_at": datetime.now().isoformat(),
                "metrics": [m.to_dict() for m in metrics],
                "scaling_recommendations": [r.to_dict() for r in recommendations],
                "profit_analysis": profit_analysis.to_dict(),
                "summary": {
                    "total_metrics": len(metrics),
                    "avg_net_gain": sum(m.net_gain_percent for m in metrics) / len(metrics) if metrics else 0.0,
                    "total_recommendations": len(recommendations),
                    "sustainable_recommendations": len(profit_analysis.recommendations),
                    "current_margin": profit_analysis.current_margin_percent,
                    "target_margin": profit_analysis.target_margin_percent,
                    "sustainability": profit_analysis.sustainability_level
                }
            }

            # Save report
            filename = self.output_dir / f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info("")
            logger.info("=" * 70)
            logger.info("📊 PERFORMANCE REPORT SUMMARY")
            logger.info("=" * 70)
            logger.info(f"Metrics Analyzed: {report['summary']['total_metrics']}")
            logger.info(f"Average Net Gain: {report['summary']['avg_net_gain']:+.1f}%")
            logger.info(f"Scaling Opportunities: {report['summary']['total_recommendations']}")
            logger.info(f"Sustainable Recommendations: {report['summary']['sustainable_recommendations']}")
            logger.info(f"Current Margin: {report['summary']['current_margin']:.1f}%")
            logger.info(f"Target Margin: {report['summary']['target_margin']:.1f}%")
            logger.info(f"Sustainability: {report['summary']['sustainability'].upper()}")
            logger.info("")
            logger.info(f"✅ Report saved: {filename}")
            logger.info("=" * 70)

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_performance_report: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    print("=" * 70)
    print("🔍 JARVIS SYPHON PERFORMANCE NET GAINS")
    print("   Extracting Perfect Percentage Net Gains")
    print("   Analyzing Hardware/Software Scaling")
    print("   Formulating Sustainable Profit Margins")
    print("=" * 70)
    print()

    analyzer = JARVISSyphonPerformanceNetGains()
    report = analyzer.generate_performance_report()

    print()
    print("=" * 70)
    print("✅ PERFORMANCE ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":


    main()