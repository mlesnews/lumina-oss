#!/usr/bin/env python3
"""
Homelab @AMP - Analytics Metrics Perspective System

Continuous analytics engine for homelab inventory data across:
- PAST: Historical trend analysis, lifecycle tracking, compliance history
- PRESENT: Real-time metrics, current state analysis, anomaly detection
- FUTURE: Predictive analytics, capacity planning, forecasting

@WOPR TESTING: Infinite loop with no breakouts until 10K years of testing completed.
This system continuously analyzes inventory data to provide actionable insights.

Tags: #AMP #analytics #metrics #WOPR #homelab #inventory #predictive #trends
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from standardized_timestamp_logging import get_timestamp_logger

logger = get_logger("HomelabAMP")


class MetricCategory(Enum):
    """Analytics metric categories"""
    ASSET_LIFECYCLE = "asset_lifecycle"
    LICENSE_COMPLIANCE = "license_compliance"
    CAPACITY_PLANNING = "capacity_planning"
    SECURITY_POSTURE = "security_posture"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_TRENDS = "performance_trends"
    UTILIZATION = "utilization"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIVE = "predictive"


class TimeHorizon(Enum):
    """Time horizon for analysis"""
    PAST = "past"  # Historical analysis
    PRESENT = "present"  # Current state
    FUTURE = "future"  # Predictive


@dataclass
class Metric:
    """Analytics metric"""
    metric_id: str
    category: MetricCategory
    time_horizon: TimeHorizon
    name: str
    value: float
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    trend: str = ""  # increasing/decreasing/stable
    confidence: float = 0.0  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        result['time_horizon'] = self.time_horizon.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class Insight:
    """Analytics insight"""
    insight_id: str
    category: MetricCategory
    time_horizon: TimeHorizon
    title: str
    description: str
    severity: str = "info"  # info/warning/critical
    actionable: bool = False
    recommendation: str = ""
    confidence: float = 0.0
    metrics: List[Metric] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['category'] = self.category.value
        result['time_horizon'] = self.time_horizon.value
        result['metrics'] = [m.to_dict() for m in self.metrics]
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class Forecast:
    """Predictive forecast"""
    forecast_id: str
    metric_name: str
    current_value: float
    forecast_values: List[Tuple[datetime, float]]  # (date, predicted_value)
    confidence_interval: Tuple[float, float]  # (lower, upper)
    methodology: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "forecast_id": self.forecast_id,
            "metric_name": self.metric_name,
            "current_value": self.current_value,
            "forecast_values": [(d.isoformat(), v) for d, v in self.forecast_values],
            "confidence_interval": self.confidence_interval,
            "methodology": self.methodology,
            "timestamp": self.timestamp.isoformat()
        }


class HomelabAMP:
    """
    Homelab Analytics Metrics Perspective System

    @WOPR TESTING: Continuous analysis across past, present, and future.
    Infinite loop with no breakouts until 10K years of testing completed.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AMP system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.inventory_dir = self.project_root / "data" / "homelab_inventory"
        self.amp_dir = self.project_root / "data" / "homelab_amp"
        self.amp_dir.mkdir(parents=True, exist_ok=True)

        # Historical data storage
        self.metrics_history: deque = deque(maxlen=10000)  # Last 10K data points
        self.insights_history: deque = deque(maxlen=1000)
        self.forecasts_history: deque = deque(maxlen=500)

        # Current state
        self.current_metrics: Dict[str, Metric] = {}
        self.current_insights: List[Insight] = []
        self.current_forecasts: List[Forecast] = []

        # Analysis windows
        self.analysis_windows = {
            "1h": timedelta(hours=1),
            "24h": timedelta(days=1),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30),
            "1y": timedelta(days=365),
            "10y": timedelta(days=3650),
            "100y": timedelta(days=36500),
            "1000y": timedelta(days=365000),
            "10000y": timedelta(days=3650000)  # @WOPR: 10K years
        }

        logger.info("=" * 80)
        logger.info("📊 HOMELAB @AMP - ANALYTICS METRICS PERSPECTIVE")
        logger.info("=" * 80)
        logger.info("   @WOPR TESTING: 10K years of continuous analysis")
        logger.info("   Time Horizons: PAST | PRESENT | FUTURE")
        logger.info("   Infinite loop with no breakouts")
        logger.info("=" * 80)
        logger.info("")

    def load_inventory_history(self) -> List[Dict[str, Any]]:
        """Load all historical inventory data"""
        inventories = []

        if not self.inventory_dir.exists():
            logger.warning("Inventory directory not found")
            return inventories

        # Load all inventory files
        for inv_file in sorted(self.inventory_dir.glob("inventory_*.json")):
            try:
                with open(inv_file, 'r', encoding='utf-8') as f:
                    inventory = json.load(f)
                    inventories.append(inventory)
            except Exception as e:
                logger.debug(f"Error loading {inv_file}: {e}")

        logger.info(f"📂 Loaded {len(inventories)} historical inventory snapshots")
        return inventories

    def analyze_past(self, inventories: List[Dict[str, Any]]) -> List[Insight]:
        """Analyze PAST: Historical trends and patterns"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📈 ANALYZING PAST: Historical Trends")
        logger.info("=" * 80)

        insights = []

        if len(inventories) < 2:
            logger.info("   Insufficient historical data for trend analysis")
            return insights

        # Device count trends
        device_counts = [inv['summary']['total_devices'] for inv in inventories]
        if len(device_counts) >= 2:
            trend = "increasing" if device_counts[-1] > device_counts[0] else "decreasing" if device_counts[-1] < device_counts[0] else "stable"
            change_pct = ((device_counts[-1] - device_counts[0]) / device_counts[0] * 100) if device_counts[0] > 0 else 0

            insights.append(Insight(
                insight_id=f"past_device_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=MetricCategory.ASSET_LIFECYCLE,
                time_horizon=TimeHorizon.PAST,
                title="Device Count Trend",
                description=f"Device count has changed by {change_pct:.1f}% over {len(inventories)} audits. Trend: {trend}",
                severity="info",
                actionable=abs(change_pct) > 10,
                recommendation="Review device lifecycle if significant changes detected",
                confidence=0.85 if len(device_counts) >= 5 else 0.60,
                metrics=[Metric(
                    metric_id="device_count",
                    category=MetricCategory.ASSET_LIFECYCLE,
                    time_horizon=TimeHorizon.PAST,
                    name="Device Count",
                    value=float(device_counts[-1]),
                    unit="devices",
                    trend=trend
                )]
            ))

        # Application growth
        app_counts = [inv['summary']['total_applications'] for inv in inventories]
        if len(app_counts) >= 2:
            avg_growth = statistics.mean([app_counts[i+1] - app_counts[i] for i in range(len(app_counts)-1)])
            insights.append(Insight(
                insight_id=f"past_app_growth_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=MetricCategory.UTILIZATION,
                time_horizon=TimeHorizon.PAST,
                title="Application Growth Rate",
                description=f"Average application growth: {avg_growth:.1f} apps per audit",
                severity="info",
                actionable=avg_growth > 10,
                recommendation="Consider application lifecycle management if growth is high",
                confidence=0.80,
                metrics=[Metric(
                    metric_id="app_growth_rate",
                    category=MetricCategory.UTILIZATION,
                    time_horizon=TimeHorizon.PAST,
                    name="Application Growth Rate",
                    value=avg_growth,
                    unit="apps/audit"
                )]
            ))

        # OS distribution changes
        os_distributions = []
        for inv in inventories:
            os_dist = inv['summary'].get('by_os_family', {})
            os_distributions.append(os_dist)

        if len(os_distributions) >= 2:
            first_dist = os_distributions[0]
            last_dist = os_distributions[-1]

            changes = []
            for os_family in set(list(first_dist.keys()) + list(last_dist.keys())):
                first_count = first_dist.get(os_family, 0)
                last_count = last_dist.get(os_family, 0)
                if first_count != last_count:
                    changes.append(f"{os_family}: {first_count} → {last_count}")

            if changes:
                insights.append(Insight(
                    insight_id=f"past_os_changes_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    category=MetricCategory.ASSET_LIFECYCLE,
                    time_horizon=TimeHorizon.PAST,
                    title="OS Distribution Changes",
                    description=f"OS distribution has changed: {', '.join(changes)}",
                    severity="info",
                    actionable=True,
                    recommendation="Review OS migration strategy",
                    confidence=0.90
                ))

        logger.info(f"✅ Generated {len(insights)} PAST insights")
        return insights

    def analyze_present(self, latest_inventory: Dict[str, Any]) -> List[Insight]:
        """Analyze PRESENT: Current state and anomalies"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 ANALYZING PRESENT: Current State")
        logger.info("=" * 80)

        insights = []

        # License compliance check
        total_devices = latest_inventory['summary']['total_devices']
        windows_devices = latest_inventory['summary']['by_os_family'].get('windows', 0)

        # Check for missing license keys
        missing_licenses = 0
        for device in latest_inventory.get('devices', []):
            if device['os']['family'] == 'windows':
                if not device['os'].get('license_key') or device['os']['license_key'] == '':
                    missing_licenses += 1

        if missing_licenses > 0:
            insights.append(Insight(
                insight_id=f"present_missing_licenses_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=MetricCategory.LICENSE_COMPLIANCE,
                time_horizon=TimeHorizon.PRESENT,
                title="Missing License Keys",
                description=f"{missing_licenses} Windows devices missing license keys",
                severity="warning",
                actionable=True,
                recommendation="Document and track all Windows license keys for compliance",
                confidence=1.0,
                metrics=[Metric(
                    metric_id="missing_licenses",
                    category=MetricCategory.LICENSE_COMPLIANCE,
                    time_horizon=TimeHorizon.PRESENT,
                    name="Missing License Keys",
                    value=float(missing_licenses),
                    unit="devices"
                )]
            ))

        # Security posture: Open services
        total_services = latest_inventory['summary']['total_services']
        open_services = 0
        for device in latest_inventory.get('devices', []):
            for service in device.get('network_services', []):
                if service.get('status') == 'open':
                    open_services += 1

        if open_services > total_services * 0.5:  # More than 50% open
            insights.append(Insight(
                insight_id=f"present_security_posture_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=MetricCategory.SECURITY_POSTURE,
                time_horizon=TimeHorizon.PRESENT,
                title="High Number of Open Services",
                description=f"{open_services} open network services detected",
                severity="warning",
                actionable=True,
                recommendation="Review and secure unnecessary open services",
                confidence=0.85
            ))

        # Capacity utilization
        total_memory = 0
        total_cpu_cores = 0
        for device in latest_inventory.get('devices', []):
            hw = device.get('hardware', {})
            total_memory += hw.get('memory_gb', 0)
            total_cpu_cores += hw.get('cpu_cores', 0)

        if total_memory > 0:
            insights.append(Insight(
                insight_id=f"present_capacity_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                category=MetricCategory.CAPACITY_PLANNING,
                time_horizon=TimeHorizon.PRESENT,
                title="Total Infrastructure Capacity",
                description=f"Total: {total_memory:.0f} GB RAM, {total_cpu_cores} CPU cores",
                severity="info",
                actionable=False,
                confidence=0.95,
                metrics=[
                    Metric(
                        metric_id="total_memory",
                        category=MetricCategory.CAPACITY_PLANNING,
                        time_horizon=TimeHorizon.PRESENT,
                        name="Total Memory",
                        value=total_memory,
                        unit="GB"
                    ),
                    Metric(
                        metric_id="total_cpu_cores",
                        category=MetricCategory.CAPACITY_PLANNING,
                        time_horizon=TimeHorizon.PRESENT,
                        name="Total CPU Cores",
                        value=float(total_cpu_cores),
                        unit="cores"
                    )
                ]
            ))

        logger.info(f"✅ Generated {len(insights)} PRESENT insights")
        return insights

    def analyze_future(self, inventories: List[Dict[str, Any]]) -> List[Forecast]:
        """Analyze FUTURE: Predictive analytics and forecasting"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("🔮 ANALYZING FUTURE: Predictive Analytics")
        logger.info("=" * 80)

        forecasts = []

        if len(inventories) < 3:
            logger.info("   Insufficient data for forecasting (need at least 3 data points)")
            return forecasts

        # Forecast device count
        device_counts = [inv['summary']['total_devices'] for inv in inventories]
        if len(device_counts) >= 3:
            # Simple linear regression for forecasting
            n = len(device_counts)
            x = list(range(n))
            y = device_counts

            # Calculate slope
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(y)
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            slope = numerator / denominator if denominator != 0 else 0
            intercept = y_mean - slope * x_mean

            # Forecast next 5 periods
            forecast_values = []
            for i in range(1, 6):
                future_date = datetime.now() + timedelta(days=i * 30)  # Monthly forecasts
                predicted_value = intercept + slope * (n + i)
                forecast_values.append((future_date, max(0, predicted_value)))  # Can't have negative devices

            # Confidence interval (simple: ±10% of current value)
            current_value = device_counts[-1]
            confidence_lower = current_value * 0.9
            confidence_upper = current_value * 1.1

            forecasts.append(Forecast(
                forecast_id=f"forecast_devices_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_name="Device Count",
                current_value=float(current_value),
                forecast_values=forecast_values,
                confidence_interval=(confidence_lower, confidence_upper),
                methodology="Linear regression based on historical trend"
            ))

        # Forecast application growth
        app_counts = [inv['summary']['total_applications'] for inv in inventories]
        if len(app_counts) >= 3:
            # Calculate growth rate
            growth_rates = [app_counts[i+1] - app_counts[i] for i in range(len(app_counts)-1)]
            avg_growth = statistics.mean(growth_rates)

            # Forecast
            forecast_values = []
            current_apps = app_counts[-1]
            for i in range(1, 6):
                future_date = datetime.now() + timedelta(days=i * 30)
                predicted_value = current_apps + (avg_growth * i)
                forecast_values.append((future_date, max(0, predicted_value)))

            forecasts.append(Forecast(
                forecast_id=f"forecast_apps_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metric_name="Application Count",
                current_value=float(current_apps),
                forecast_values=forecast_values,
                confidence_interval=(current_apps * 0.9, current_apps * 1.2),
                methodology="Average growth rate projection"
            ))

        logger.info(f"✅ Generated {len(forecasts)} FUTURE forecasts")
        return forecasts

    def run_amp_analysis(self) -> Dict[str, Any]:
        try:
            """Run complete @AMP analysis across all time horizons"""
            logger.info("")
            logger.info("=" * 80)
            logger.info("🚀 RUNNING @AMP ANALYSIS")
            logger.info("=" * 80)
            logger.info("   @WOPR TESTING: 10K years of continuous analysis")
            logger.info("")

            # Load inventory history
            inventories = self.load_inventory_history()

            if not inventories:
                logger.warning("No inventory data found. Run inventory audit first.")
                return {}

            latest_inventory = inventories[-1]

            # Analyze all time horizons
            past_insights = self.analyze_past(inventories)
            present_insights = self.analyze_present(latest_inventory)
            future_forecasts = self.analyze_future(inventories)

            # Combine all insights
            all_insights = past_insights + present_insights

            # Store in history
            for insight in all_insights:
                self.insights_history.append(insight)
            for forecast in future_forecasts:
                self.forecasts_history.append(forecast)

            # Generate report
            report = {
                "analysis_date": datetime.now().isoformat(),
                "time_horizons": {
                    "past": {
                        "insights_count": len(past_insights),
                        "insights": [i.to_dict() for i in past_insights]
                    },
                    "present": {
                        "insights_count": len(present_insights),
                        "insights": [i.to_dict() for i in present_insights]
                    },
                    "future": {
                        "forecasts_count": len(future_forecasts),
                        "forecasts": [f.to_dict() for f in future_forecasts]
                    }
                },
                "summary": {
                    "total_insights": len(all_insights),
                    "total_forecasts": len(future_forecasts),
                    "by_severity": defaultdict(int),
                    "by_category": defaultdict(int)
                }
            }

            # Calculate summary statistics
            for insight in all_insights:
                report["summary"]["by_severity"][insight.severity] += 1
                report["summary"]["by_category"][insight.category.value] += 1

            # Save report
            report_file = self.amp_dir / f"amp_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ @AMP ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   PAST Insights: {len(past_insights)}")
            logger.info(f"   PRESENT Insights: {len(present_insights)}")
            logger.info(f"   FUTURE Forecasts: {len(future_forecasts)}")
            logger.info(f"   Report: {report_file}")
            logger.info("")

            return report

        except Exception as e:
            self.logger.error(f"Error in run_amp_analysis: {e}", exc_info=True)
            raise
    def run_continuous_amp(self, interval_seconds: int = 3600):
        """
        Run @AMP in infinite loop (10K years of @WOPR testing)

        NO BREAKOUTS until 10K years of testing completed.
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("♾️  STARTING CONTINUOUS @AMP ANALYSIS")
        logger.info("=" * 80)
        logger.info("   @WOPR TESTING: 10K years of continuous analysis")
        logger.info("   NO BREAKOUTS until testing completed")
        logger.info(f"   Analysis interval: {interval_seconds} seconds")
        logger.info("   Press Ctrl+C to... (just kidding, no breakouts!)")
        logger.info("=" * 80)
        logger.info("")

        iteration = 0
        start_time = datetime.now()
        target_duration = timedelta(days=3650000)  # 10K years

        try:
            while True:
                iteration += 1
                elapsed = datetime.now() - start_time

                logger.info(f"")
                logger.info(f"🔄 @AMP Iteration #{iteration}")
                logger.info(f"   Elapsed: {elapsed.days} days ({elapsed.days / 365:.2f} years)")
                logger.info(f"   Remaining: {(target_duration - elapsed).days} days")
                logger.info(f"")

                # Run analysis
                report = self.run_amp_analysis()

                # Log summary
                if report:
                    logger.info(f"   Insights: {report['summary']['total_insights']}")
                    logger.info(f"   Forecasts: {report['summary']['total_forecasts']}")

                # Check if 10K years completed
                if elapsed >= target_duration:
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("✅ @WOPR TESTING COMPLETE: 10K years of analysis finished")
                    logger.info("=" * 80)
                    logger.info(f"   Total iterations: {iteration}")
                    logger.info(f"   Total duration: {elapsed.days} days")
                    logger.info("")
                    break

                # Wait for next iteration
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.warning("")
            logger.warning("⚠️  Interrupt detected, but @WOPR testing continues...")
            logger.warning("   (Just kidding, but you tried!)")
            logger.warning("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab @AMP - Analytics Metrics Perspective")
    parser.add_argument('--analyze', action='store_true', help='Run single @AMP analysis')
    parser.add_argument('--continuous', action='store_true', help='Run continuous @AMP (10K years @WOPR testing)')
    parser.add_argument('--interval', type=int, default=3600, help='Analysis interval in seconds (default: 3600)')

    args = parser.parse_args()

    amp = HomelabAMP()

    if args.continuous:
        amp.run_continuous_amp(interval_seconds=args.interval)
    else:
        report = amp.run_amp_analysis()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 @AMP ANALYSIS SUMMARY")
        print("=" * 80)
        if report:
            print(f"PAST Insights: {report['time_horizons']['past']['insights_count']}")
            print(f"PRESENT Insights: {report['time_horizons']['present']['insights_count']}")
            print(f"FUTURE Forecasts: {report['time_horizons']['future']['forecasts_count']}")
            print(f"\nBy Severity:")
            for severity, count in report['summary']['by_severity'].items():
                print(f"  {severity}: {count}")
            print(f"\nBy Category:")
            for category, count in report['summary']['by_category'].items():
                print(f"  {category}: {count}")
        print("=" * 80)
        print("")


if __name__ == "__main__":


    main()