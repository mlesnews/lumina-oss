#!/usr/bin/env python3
"""
JARVIS Analytics Tracker
Tracks performance metrics and compares against baseline.

Tags: #JARVIS #ANALYTICS #METRICS #TRACKING @BASELINE
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAnalyticsTracker")

PROJECT_ROOT = script_dir.parent.parent
BASELINE_FILE = PROJECT_ROOT / "data" / "analytics" / "baseline_metrics.json"
METRICS_DIR = PROJECT_ROOT / "data" / "analytics" / "metrics"


@dataclass
class OperationMetrics:
    """Metrics for a single operation"""
    operation_id: str
    operation_type: str
    duration: float
    status: str
    errors: int
    warnings: int
    optimizations_applied: List[str]
    timestamp: str


@dataclass
class SessionMetrics:
    """Metrics for a complete session"""
    session_id: str
    total_duration: float
    operations: List[OperationMetrics]
    total_errors: int
    total_warnings: int
    success_rate: float
    timestamp: str


class JARVISAnalyticsTracker:
    """Track analytics and compare against baseline"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = PROJECT_ROOT
        self.project_root = Path(project_root)
        self.baseline_file = BASELINE_FILE
        self.metrics_dir = METRICS_DIR
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        self.baseline = self._load_baseline()

    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline metrics"""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load baseline: {e}")

        # Default baseline from 2026-01-12 session
        return {
            "session_id": "SESSION_20260112_051400",
            "baseline_date": "2026-01-12",
            "operations": {
                "all_systems_check": {
                    "duration": 13.0,
                    "status": "excellent"
                },
                "reboot_preparation": {
                    "duration": 4.0,
                    "status": "excellent"
                },
                "reboot_execution": {
                    "duration": 3.0,
                    "status": "excellent"
                }
            },
            "total_session_duration": 153.0,
            "success_rate": 100.0,
            "error_rate": 0.0,
            "optimizations": [
                "parallel_checks",
                "lazy_state_saving",
                "smart_process_detection",
                "incremental_tracking",
                "metadata_first_reporting"
            ]
        }

    def track_operation(self, operation_type: str, duration: float,
                       status: str = "ok", errors: int = 0,
                       warnings: int = 0, optimizations: List[str] = None) -> OperationMetrics:
        """Track a single operation"""
        operation_id = f"OP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        metrics = OperationMetrics(
            operation_id=operation_id,
            operation_type=operation_type,
            duration=duration,
            status=status,
            errors=errors,
            warnings=warnings,
            optimizations_applied=optimizations or [],
            timestamp=datetime.now().isoformat()
        )

        return metrics

    def compare_to_baseline(self, operation_type: str, duration: float) -> Dict[str, Any]:
        """Compare operation to baseline"""
        baseline_ops = self.baseline.get("operations", {})
        baseline_op = baseline_ops.get(operation_type, {})
        baseline_duration = baseline_op.get("duration", 0)

        if baseline_duration == 0:
            return {
                "comparison": "no_baseline",
                "baseline_duration": 0,
                "current_duration": duration,
                "variance": 0,
                "improvement_percent": 0
            }

        variance = duration - baseline_duration
        improvement_percent = ((baseline_duration - duration) / baseline_duration) * 100

        if improvement_percent > 5:
            comparison = "improved"
            status_icon = "✅"
        elif improvement_percent < -20:
            comparison = "regressed"
            status_icon = "❌"
        else:
            comparison = "maintained"
            status_icon = "➡️"

        return {
            "comparison": comparison,
            "status_icon": status_icon,
            "baseline_duration": baseline_duration,
            "current_duration": duration,
            "variance": variance,
            "improvement_percent": improvement_percent,
            "baseline_status": baseline_op.get("status", "unknown")
        }

    def track_session(self, operations: List[OperationMetrics]) -> SessionMetrics:
        """Track a complete session"""
        session_id = f"SESSION_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        total_duration = sum(op.duration for op in operations)
        total_errors = sum(op.errors for op in operations)
        total_warnings = sum(op.warnings for op in operations)

        # Calculate success rate
        successful_ops = len([op for op in operations if op.status == "ok"])
        success_rate = (successful_ops / len(operations) * 100) if operations else 0

        metrics = SessionMetrics(
            session_id=session_id,
            total_duration=total_duration,
            operations=operations,
            total_errors=total_errors,
            total_warnings=total_warnings,
            success_rate=success_rate,
            timestamp=datetime.now().isoformat()
        )

        # Save session metrics
        self._save_session_metrics(metrics)

        return metrics

    def _save_session_metrics(self, metrics: SessionMetrics):
        try:
            """Save session metrics to file"""
            metrics_file = self.metrics_dir / f"{metrics.session_id}.json"

            data = {
                "session_id": metrics.session_id,
                "timestamp": metrics.timestamp,
                "total_duration": metrics.total_duration,
                "total_errors": metrics.total_errors,
                "total_warnings": metrics.total_warnings,
                "success_rate": metrics.success_rate,
                "operations": [asdict(op) for op in metrics.operations],
                "baseline_comparison": self._compare_session_to_baseline(metrics)
            }

            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Session metrics saved to {metrics_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_session_metrics: {e}", exc_info=True)
            raise
    def _compare_session_to_baseline(self, metrics: SessionMetrics) -> Dict[str, Any]:
        """Compare entire session to baseline"""
        baseline_duration = self.baseline.get("total_session_duration", 0)
        baseline_success = self.baseline.get("success_rate", 100.0)

        duration_variance = metrics.total_duration - baseline_duration
        duration_improvement = ((baseline_duration - metrics.total_duration) / baseline_duration * 100) if baseline_duration > 0 else 0

        success_variance = metrics.success_rate - baseline_success
        success_improvement = metrics.success_rate - baseline_success

        return {
            "duration": {
                "baseline": baseline_duration,
                "current": metrics.total_duration,
                "variance": duration_variance,
                "improvement_percent": duration_improvement
            },
            "success_rate": {
                "baseline": baseline_success,
                "current": metrics.success_rate,
                "variance": success_variance,
                "improvement_percent": success_improvement
            }
        }

    def generate_analytics_report(self, session_metrics: SessionMetrics) -> str:
        """Generate human-readable analytics report"""
        lines = []
        lines.append("="*80)
        lines.append("📊 JARVIS ANALYTICS REPORT")
        lines.append("="*80)
        lines.append("")
        lines.append(f"**Session ID:** {session_metrics.session_id}")
        lines.append(f"**Timestamp:** {session_metrics.timestamp}")
        lines.append("")
        lines.append("## 📈 Performance Metrics")
        lines.append("")

        # Compare each operation to baseline
        for op in session_metrics.operations:
            comparison = self.compare_to_baseline(op.operation_type, op.duration)
            lines.append(f"### {op.operation_type.replace('_', ' ').title()}")
            lines.append(f"- **Duration:** {op.duration:.2f}s")
            lines.append(f"- **Baseline:** {comparison['baseline_duration']:.2f}s")
            lines.append(f"- **Variance:** {comparison['variance']:+.2f}s ({comparison['improvement_percent']:+.1f}%)")
            lines.append(f"- **Status:** {comparison['status_icon']} {comparison['comparison'].upper()}")
            lines.append("")

        # Session summary
        session_comparison = self._compare_session_to_baseline(session_metrics)
        lines.append("## 📊 Session Summary")
        lines.append("")
        lines.append(f"- **Total Duration:** {session_metrics.total_duration:.2f}s")
        lines.append(f"- **Baseline Duration:** {session_comparison['duration']['baseline']:.2f}s")
        lines.append(f"- **Improvement:** {session_comparison['duration']['improvement_percent']:+.1f}%")
        lines.append(f"- **Success Rate:** {session_metrics.success_rate:.1f}%")
        lines.append(f"- **Errors:** {session_metrics.total_errors}")
        lines.append(f"- **Warnings:** {session_metrics.total_warnings}")
        lines.append("")

        return "\n".join(lines)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Analytics Tracker")
        parser.add_argument('--baseline', action='store_true', help='Show baseline metrics')
        parser.add_argument('--track', type=str, help='Track operation (type,duration,status)')
        parser.add_argument('--compare', type=str, help='Compare operation to baseline (type,duration)')

        args = parser.parse_args()

        tracker = JARVISAnalyticsTracker()

        if args.baseline:
            print("📊 Baseline Metrics:")
            print(json.dumps(tracker.baseline, indent=2))

        elif args.track:
            parts = args.track.split(',')
            if len(parts) >= 2:
                op_type = parts[0]
                duration = float(parts[1])
                status = parts[2] if len(parts) > 2 else "ok"
                metrics = tracker.track_operation(op_type, duration, status)
                comparison = tracker.compare_to_baseline(op_type, duration)
                print(f"✅ Tracked: {op_type} ({duration:.2f}s)")
                print(f"   Comparison: {comparison['status_icon']} {comparison['comparison']} ({comparison['improvement_percent']:+.1f}%)")

        elif args.compare:
            parts = args.compare.split(',')
            if len(parts) >= 2:
                op_type = parts[0]
                duration = float(parts[1])
                comparison = tracker.compare_to_baseline(op_type, duration)
                print(f"📊 Comparison for {op_type}:")
                print(f"   Baseline: {comparison['baseline_duration']:.2f}s")
                print(f"   Current: {comparison['current_duration']:.2f}s")
                print(f"   Variance: {comparison['variance']:+.2f}s")
                print(f"   Status: {comparison['status_icon']} {comparison['comparison'].upper()}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()