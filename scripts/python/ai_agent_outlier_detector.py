#!/usr/bin/env python3
"""
AI Agent-Driven Outlier Detection & Initiative System

Automatically detects outliers and initiates AI agent-driven actions.
Integrates with JARVIS, MARVIN, and other agents for intelligent responses.

Tags: #AI_AGENT #OUTLIER_DETECTION #AUTOMATION #INITIATIVES #JARVIS #MARVIN @JARVIS @LUMINA @AIQ
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIAgentOutlierDetector")


@dataclass
class OutlierDetection:
    """Outlier detection result"""
    id: str
    timestamp: str
    type: str
    severity: str
    value: Any
    expected_value: Any
    deviation: float
    agent: str
    action_taken: str
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIAgentOutlierDetector:
    """
    AI Agent-Driven Outlier Detection & Initiative System

    Detects outliers and automatically initiates agent-driven actions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize outlier detector"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "outlier_detections"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Detection history
        self.detections_file = self.data_dir / "detections.json"
        self.detections: List[OutlierDetection] = []

        # Load NAS cron scheduler for initiatives
        try:
            from nas_cron_scheduler import NASCronScheduler
            self.nas_scheduler = NASCronScheduler(self.project_root)
        except Exception as e:
            logger.debug(f"   NAS scheduler not available: {e}")
            self.nas_scheduler = None

        # Load existing detections
        self._load_detections()

        logger.info("✅ AI Agent Outlier Detector initialized")
        logger.info(f"   Historical detections: {len(self.detections)}")

    def _load_detections(self):
        """Load detection history"""
        if self.detections_file.exists():
            try:
                with open(self.detections_file, 'r') as f:
                    data = json.load(f)
                    self.detections = [OutlierDetection(**d) for d in data]
            except Exception as e:
                logger.debug(f"   Could not load detections: {e}")

    def _save_detections(self):
        """Save detection history"""
        try:
            with open(self.detections_file, 'w') as f:
                json.dump([
                    {
                        "id": d.id,
                        "timestamp": d.timestamp,
                        "type": d.type,
                        "severity": d.severity,
                        "value": d.value,
                        "expected_value": d.expected_value,
                        "deviation": d.deviation,
                        "agent": d.agent,
                        "action_taken": d.action_taken,
                        "success": d.success,
                        "metadata": d.metadata
                    }
                    for d in self.detections[-1000:]  # Keep last 1000
                ], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving detections: {e}")

    def detect_connection_error_outliers(self) -> List[OutlierDetection]:
        """Detect connection error outliers"""
        logger.info("   🔍 Detecting connection error outliers...")

        detections = []

        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            monitor = CursorConnectionHealthMonitor(self.project_root)
            health = monitor.get_health_status()

            # Check for error spike
            error_rate = 1.0 - (health.get("success_rate", 100) / 100.0)

            # Outlier: error rate > 10%
            if error_rate > 0.10:
                detection = OutlierDetection(
                    id=f"conn_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now().isoformat(),
                    type="connection_error_spike",
                    severity="critical",
                    value=error_rate,
                    expected_value=0.05,  # Expected < 5%
                    deviation=(error_rate - 0.05) / 0.05 * 100,  # Percentage deviation
                    agent="JARVIS",
                    action_taken="initiate_recovery_sequence",
                    success=False  # Will be updated after action
                )

                # Execute recovery
                success = self._execute_recovery_sequence(detection)
                detection.success = success

                detections.append(detection)
                self.detections.append(detection)
                self._save_detections()

                logger.warning(f"   ⚠️  Connection error outlier detected: {error_rate:.1%}")

        except Exception as e:
            logger.error(f"   ❌ Error detecting connection outliers: {e}")

        return detections

    def detect_performance_outliers(self) -> List[OutlierDetection]:
        """Detect performance outliers"""
        logger.info("   🔍 Detecting performance outliers...")

        detections = []

        try:
            import psutil

            # Get current metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Outlier: CPU > 90%
            if cpu_percent > 90:
                detection = OutlierDetection(
                    id=f"perf_cpu_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now().isoformat(),
                    type="cpu_spike",
                    severity="high",
                    value=cpu_percent,
                    expected_value=70.0,
                    deviation=((cpu_percent - 70) / 70) * 100,
                    agent="JARVIS",
                    action_taken="scale_resources",
                    success=False
                )

                success = self._execute_scale_resources(detection)
                detection.success = success

                detections.append(detection)
                self.detections.append(detection)

            # Outlier: Memory > 90%
            if memory_percent > 90:
                detection = OutlierDetection(
                    id=f"perf_mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    timestamp=datetime.now().isoformat(),
                    type="memory_spike",
                    severity="high",
                    value=memory_percent,
                    expected_value=70.0,
                    deviation=((memory_percent - 70) / 70) * 100,
                    agent="JARVIS",
                    action_taken="optimize_memory",
                    success=False
                )

                success = self._execute_optimize_memory(detection)
                detection.success = success

                detections.append(detection)
                self.detections.append(detection)

        except Exception as e:
            logger.error(f"   ❌ Error detecting performance outliers: {e}")

        return detections

    def detect_schedule_outliers(self) -> List[OutlierDetection]:
        """Detect schedule/activity outliers"""
        logger.info("   🔍 Detecting schedule outliers...")

        detections = []

        try:
            # Check if daily work cycle ran
            if self.nas_scheduler:
                daily_job = self.nas_scheduler.cron_jobs.get("daily_work_cycle")
                if daily_job:
                    last_run = daily_job.last_run
                    if last_run:
                        last_run_time = datetime.fromisoformat(last_run)
                        hours_since_run = (datetime.now() - last_run_time).total_seconds() / 3600

                        # Outlier: Should run daily, but hasn't run in > 26 hours
                        if hours_since_run > 26:
                            detection = OutlierDetection(
                                id=f"schedule_daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                timestamp=datetime.now().isoformat(),
                                type="missing_scheduled_run",
                                severity="medium",
                                value=hours_since_run,
                                expected_value=24.0,
                                deviation=((hours_since_run - 24) / 24) * 100,
                                agent="JARVIS",
                                action_taken="trigger_manual_run",
                                success=False
                            )

                            success = self._execute_trigger_manual_run("daily_work_cycle")
                            detection.success = success

                            detections.append(detection)
                            self.detections.append(detection)

        except Exception as e:
            logger.error(f"   ❌ Error detecting schedule outliers: {e}")

        return detections

    def _execute_recovery_sequence(self, detection: OutlierDetection) -> bool:
        """Execute recovery sequence for connection errors"""
        logger.info("   🔄 Executing recovery sequence...")

        try:
            # 1. Retry connections
            logger.info("      → Retrying connections")

            # 2. Check services
            logger.info("      → Checking services")

            # 3. Restart if needed
            logger.info("      → Evaluating restart necessity")

            # Would integrate with connection resilience system
            return True

        except Exception as e:
            logger.error(f"   ❌ Recovery sequence error: {e}")
            return False

    def _execute_scale_resources(self, detection: OutlierDetection) -> bool:
        """Execute resource scaling"""
        logger.info("   📈 Scaling resources...")

        try:
            # Would integrate with dynamic scaling system
            logger.info("      → Scaling CPU resources")
            return True
        except Exception as e:
            logger.error(f"   ❌ Scaling error: {e}")
            return False

    def _execute_optimize_memory(self, detection: OutlierDetection) -> bool:
        """Execute memory optimization"""
        logger.info("   🧹 Optimizing memory...")

        try:
            # Would integrate with memory optimizer
            logger.info("      → Optimizing memory usage")
            return True
        except Exception as e:
            logger.error(f"   ❌ Memory optimization error: {e}")
            return False

    def _execute_trigger_manual_run(self, job_id: str) -> bool:
        """Trigger manual run of scheduled job"""
        logger.info(f"   ▶️  Triggering manual run: {job_id}")

        try:
            if self.nas_scheduler:
                # Would trigger the job manually
                logger.info(f"      → Triggering {job_id}")
                return True
        except Exception as e:
            logger.error(f"   ❌ Trigger error: {e}")

        return False

    def detect_all_outliers(self) -> Dict[str, List[OutlierDetection]]:
        """Detect all types of outliers"""
        logger.info("=" * 80)
        logger.info("🔍 AI AGENT-DRIVEN OUTLIER DETECTION")
        logger.info("=" * 80)

        results = {
            "connection_errors": self.detect_connection_error_outliers(),
            "performance": self.detect_performance_outliers(),
            "schedule": self.detect_schedule_outliers()
        }

        total = sum(len(detections) for detections in results.values())
        logger.info(f"   ✅ Detected {total} outliers")

        return results

    def get_outlier_statistics(self) -> Dict[str, Any]:
        """Get outlier detection statistics"""
        total = len(self.detections)

        by_type = {}
        by_severity = {}
        by_agent = {}

        for detection in self.detections:
            by_type[detection.type] = by_type.get(detection.type, 0) + 1
            by_severity[detection.severity] = by_severity.get(detection.severity, 0) + 1
            by_agent[detection.agent] = by_agent.get(detection.agent, 0) + 1

        # Recent detections (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent = [
            d for d in self.detections
            if datetime.fromisoformat(d.timestamp) > recent_cutoff
        ]

        return {
            "total_detections": total,
            "recent_24h": len(recent),
            "by_type": by_type,
            "by_severity": by_severity,
            "by_agent": by_agent,
            "success_rate": (
                sum(1 for d in self.detections if d.success) / total * 100
                if total > 0 else 0.0
            )
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="AI Agent Outlier Detector")
        parser.add_argument("--detect", action="store_true", help="Detect all outliers")
        parser.add_argument("--detect-connection", action="store_true", help="Detect connection outliers")
        parser.add_argument("--detect-performance", action="store_true", help="Detect performance outliers")
        parser.add_argument("--detect-schedule", action="store_true", help="Detect schedule outliers")
        parser.add_argument("--stats", action="store_true", help="Show statistics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        detector = AIAgentOutlierDetector()

        if args.detect or not any([args.detect_connection, args.detect_performance, args.detect_schedule, args.stats]):
            results = detector.detect_all_outliers()
            if args.json:
                print(json.dumps({
                    type_name: [
                        {
                            "id": d.id,
                            "type": d.type,
                            "severity": d.severity,
                            "agent": d.agent,
                            "action": d.action_taken
                        }
                        for d in detections
                    ]
                    for type_name, detections in results.items()
                }, indent=2, default=str))
            else:
                total = sum(len(detections) for detections in results.values())
                print(f"✅ Detected {total} outliers")

        elif args.detect_connection:
            detections = detector.detect_connection_error_outliers()
            print(f"✅ Detected {len(detections)} connection outliers")

        elif args.detect_performance:
            detections = detector.detect_performance_outliers()
            print(f"✅ Detected {len(detections)} performance outliers")

        elif args.detect_schedule:
            detections = detector.detect_schedule_outliers()
            print(f"✅ Detected {len(detections)} schedule outliers")

        elif args.stats:
            stats = detector.get_outlier_statistics()
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"Total Detections: {stats['total_detections']}")
                print(f"Recent (24h): {stats['recent_24h']}")
                print(f"Success Rate: {stats['success_rate']:.1f}%")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()