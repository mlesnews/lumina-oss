#!/usr/bin/env python3
"""
Blindspot Mirror System - Continuous Monitoring & Review
Like checking mirrors while driving - continuous blindspot detection and review

Tags: #BLINDSPOT #MIRROR #REVIEW #CONTINUOUS_MONITORING #REARVIEW #SIDE_MIRROR @MARVIN @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

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

logger = get_logger("BlindspotMirrorSystem")


@dataclass
class MirrorCheck:
    """Mirror check result (like checking mirrors while driving)"""
    check_id: str
    timestamp: str
    mirror_type: str  # "rearview", "side_left", "side_right", "all"
    blindspots_detected: List[str] = field(default_factory=list)
    status: str = "clear"  # "clear", "warning", "critical"
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MirrorReview:
    """Complete mirror review (all mirrors checked)"""
    review_id: str
    timestamp: str
    rearview_check: Optional[MirrorCheck] = None
    side_left_check: Optional[MirrorCheck] = None
    side_right_check: Optional[MirrorCheck] = None
    overall_status: str = "clear"
    blindspots_found: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BlindspotMirrorSystem:
    """
    Blindspot Mirror System

    Continuous monitoring and review - like checking mirrors while driving.
    Continuously checks for blindspots and provides ongoing visibility.
    """

    def __init__(self):
        """Initialize Blindspot Mirror System"""
        logger.info("=" * 80)
        logger.info("🪞 Blindspot Mirror System (Continuous Monitoring)")
        logger.info("=" * 80)

        self.project_root = project_root
        self.data_dir = project_root / "data" / "blindspot_mirrors"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Mirror check history
        self.history_file = self.data_dir / "mirror_history.json"
        self.history: List[MirrorReview] = []

        # Load history
        self._load_history()

        # Check intervals (like checking mirrors while driving)
        self.check_intervals = {
            "rearview": timedelta(seconds=5),  # Check rearview frequently
            "side_left": timedelta(seconds=10),  # Check side mirrors regularly
            "side_right": timedelta(seconds=10),
            "full_review": timedelta(minutes=1)  # Full review periodically
        }

        logger.info("✅ Blindspot Mirror System initialized")
        logger.info(f"   Historical reviews: {len(self.history)}")
        logger.info("   🪞 Continuous monitoring active (like checking mirrors)")

    def _load_history(self):
        """Load mirror check history"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = [MirrorReview(**r) for r in data]
            except Exception as e:
                logger.debug(f"   Could not load history: {e}")

    def _save_history(self):
        """Save mirror check history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump([asdict(r) for r in self.history], f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def check_rearview_mirror(self) -> MirrorCheck:
        """
        Check rearview mirror - look back at recent workflow executions

        Returns:
            MirrorCheck with recent blindspots
        """
        check_id = f"rearview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()

        logger.info("\n🪞 Checking Rearview Mirror (Recent History)...")

        blindspots = []
        details = {}

        # Check recent workflow executions
        recent_workflows = self._check_recent_workflows()
        if recent_workflows.get("failures", 0) > 0:
            blindspots.append("Recent workflow failures detected")
            details["recent_failures"] = recent_workflows["failures"]

        # Check for missing final steps
        missing_bda = self._check_missing_bda()
        if missing_bda:
            blindspots.append("Workflows missing @DOIT @BDA final step")
            details["missing_bda"] = missing_bda

        # Check for errors in logs
        recent_errors = self._check_recent_errors()
        if recent_errors:
            blindspots.append(f"Recent errors detected: {len(recent_errors)}")
            details["recent_errors"] = recent_errors[:5]  # Top 5

        # Determine status
        if blindspots:
            status = "critical" if any("missing" in bs.lower() for bs in blindspots) else "warning"
        else:
            status = "clear"

        check = MirrorCheck(
            check_id=check_id,
            timestamp=timestamp,
            mirror_type="rearview",
            blindspots_detected=blindspots,
            status=status,
            details=details
        )

        logger.info(f"   Status: {status.upper()}")
        if blindspots:
            logger.info(f"   Blindspots: {len(blindspots)}")
            for bs in blindspots:
                logger.info(f"     - {bs}")
        else:
            logger.info("   ✅ Clear - no blindspots detected")

        return check

    def check_side_left_mirror(self) -> MirrorCheck:
        """
        Check left side mirror - monitor current workflow execution

        Returns:
            MirrorCheck with current execution blindspots
        """
        check_id = f"side_left_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()

        logger.info("\n🪞 Checking Left Side Mirror (Current Execution)...")

        blindspots = []
        details = {}

        # Check for running workflows
        running_workflows = self._check_running_workflows()
        if running_workflows:
            details["running_workflows"] = running_workflows

        # Check for stuck processes
        stuck_processes = self._check_stuck_processes()
        if stuck_processes:
            blindspots.append("Stuck processes detected")
            details["stuck_processes"] = stuck_processes

        # Check resource usage
        resource_issues = self._check_resource_usage()
        if resource_issues:
            blindspots.append("Resource usage issues detected")
            details["resource_issues"] = resource_issues

        # Determine status
        status = "critical" if blindspots else "clear"

        check = MirrorCheck(
            check_id=check_id,
            timestamp=timestamp,
            mirror_type="side_left",
            blindspots_detected=blindspots,
            status=status,
            details=details
        )

        logger.info(f"   Status: {status.upper()}")
        if blindspots:
            logger.info(f"   Blindspots: {len(blindspots)}")
            for bs in blindspots:
                logger.info(f"     - {bs}")
        else:
            logger.info("   ✅ Clear - no blindspots detected")

        return check

    def check_side_right_mirror(self) -> MirrorCheck:
        """
        Check right side mirror - look ahead at upcoming workflows

        Returns:
            MirrorCheck with potential future blindspots
        """
        check_id = f"side_right_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()

        logger.info("\n🪞 Checking Right Side Mirror (Upcoming Workflows)...")

        blindspots = []
        details = {}

        # Check scheduled workflows
        scheduled_workflows = self._check_scheduled_workflows()
        if scheduled_workflows:
            details["scheduled_workflows"] = scheduled_workflows

        # Check for potential conflicts
        potential_conflicts = self._check_potential_conflicts()
        if potential_conflicts:
            blindspots.append("Potential workflow conflicts detected")
            details["conflicts"] = potential_conflicts

        # Check for resource availability
        resource_availability = self._check_resource_availability()
        if not resource_availability.get("sufficient", True):
            blindspots.append("Insufficient resources for upcoming workflows")
            details["resource_availability"] = resource_availability

        # Determine status
        status = "warning" if blindspots else "clear"

        check = MirrorCheck(
            check_id=check_id,
            timestamp=timestamp,
            mirror_type="side_right",
            blindspots_detected=blindspots,
            status=status,
            details=details
        )

        logger.info(f"   Status: {status.upper()}")
        if blindspots:
            logger.info(f"   Blindspots: {len(blindspots)}")
            for bs in blindspots:
                logger.info(f"     - {bs}")
        else:
            logger.info("   ✅ Clear - no blindspots detected")

        return check

    def full_mirror_review(self) -> MirrorReview:
        """
        Full mirror review - check all mirrors (rearview, left, right)

        Returns:
            MirrorReview with complete visibility
        """
        review_id = f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now().isoformat()

        logger.info("\n🪞 Full Mirror Review (All Mirrors)...")
        logger.info("   Checking rearview, left side, and right side mirrors...")

        # Check all mirrors
        rearview = self.check_rearview_mirror()
        side_left = self.check_side_left_mirror()
        side_right = self.check_side_right_mirror()

        # Collect all blindspots
        all_blindspots = []
        all_blindspots.extend(rearview.blindspots_detected)
        all_blindspots.extend(side_left.blindspots_detected)
        all_blindspots.extend(side_right.blindspots_detected)

        # Determine overall status
        statuses = [rearview.status, side_left.status, side_right.status]
        if "critical" in statuses:
            overall_status = "critical"
        elif "warning" in statuses:
            overall_status = "warning"
        else:
            overall_status = "clear"

        # Generate recommendations
        recommendations = self._generate_recommendations(all_blindspots)

        review = MirrorReview(
            review_id=review_id,
            timestamp=timestamp,
            rearview_check=rearview,
            side_left_check=side_left,
            side_right_check=side_right,
            overall_status=overall_status,
            blindspots_found=all_blindspots,
            recommendations=recommendations
        )

        # Save to history
        self.history.append(review)
        self._save_history()

        logger.info(f"\n✅ Full Mirror Review Complete")
        logger.info(f"   Overall Status: {overall_status.upper()}")
        logger.info(f"   Total Blindspots: {len(all_blindspots)}")
        logger.info(f"   Recommendations: {len(recommendations)}")

        return review

    def _check_recent_workflows(self) -> Dict[str, Any]:
        """Check recent workflow executions"""
        # Check intelligence processing reports
        intel_dir = project_root / "data" / "intelligence_processing"
        failures = 0
        total = 0

        if intel_dir.exists():
            for report_file in intel_dir.glob("*.json"):
                total += 1
                try:
                    with open(report_file, 'r') as f:
                        data = json.load(f)
                        # Check for errors or failures
                        if data.get("summary", {}).get("errors", 0) > 0:
                            failures += 1
                except:
                    pass

        return {
            "total": total,
            "failures": failures,
            "success_rate": (total - failures) / total if total > 0 else 1.0
        }

    def _check_missing_bda(self) -> List[str]:
        try:
            """Check for workflows missing @DOIT @BDA final step"""
            missing = []

            # Check intelligence processing
            intel_file = project_root / "scripts" / "python" / "intelligence_processing_analysis.py"
            if intel_file.exists():
                content = intel_file.read_text()
                if "DOITBDAFinalStep" not in content:
                    missing.append("intelligence_processing_analysis.py")

            # Check daily work cycle
            daily_file = project_root / "scripts" / "python" / "daily_work_cycle_complete.py"
            if daily_file.exists():
                content = daily_file.read_text()
                if "DOITBDAFinalStep" not in content:
                    missing.append("daily_work_cycle_complete.py")

            return missing

        except Exception as e:
            self.logger.error(f"Error in _check_missing_bda: {e}", exc_info=True)
            raise
    def _check_recent_errors(self) -> List[str]:
        try:
            """Check for recent errors in logs"""
            errors = []

            # Check log files (simplified - would need actual log parsing)
            log_dir = project_root / "logs"
            if log_dir.exists():
                # Check recent log files for errors
                # This is a placeholder - would need actual log parsing
                pass

            return errors

        except Exception as e:
            self.logger.error(f"Error in _check_recent_errors: {e}", exc_info=True)
            raise
    def _check_running_workflows(self) -> List[str]:
        """Check for currently running workflows"""
        # Placeholder - would check process list or workflow status
        return []

    def _check_stuck_processes(self) -> List[str]:
        """Check for stuck processes"""
        # Placeholder - would check for processes running too long
        return []

    def _check_resource_usage(self) -> Dict[str, Any]:
        """Check resource usage"""
        # Placeholder - would check CPU, memory, disk usage
        return {}

    def _check_scheduled_workflows(self) -> List[str]:
        """Check scheduled workflows"""
        # Check cron jobs
        cron_file = project_root / "data" / "nas_cron" / "cron_jobs.json"
        scheduled = []

        if cron_file.exists():
            try:
                with open(cron_file, 'r') as f:
                    data = json.load(f)
                    for job_id, job_data in data.items():
                        if job_data.get("enabled", False):
                            scheduled.append(job_id)
            except:
                pass

        return scheduled

    def _check_potential_conflicts(self) -> List[str]:
        """Check for potential workflow conflicts"""
        # Placeholder - would check for overlapping schedules, resource conflicts
        return []

    def _check_resource_availability(self) -> Dict[str, Any]:
        """Check resource availability for upcoming workflows"""
        # Placeholder - would check if resources are available
        return {"sufficient": True}

    def _generate_recommendations(self, blindspots: List[str]) -> List[str]:
        """Generate recommendations based on blindspots"""
        recommendations = []

        for blindspot in blindspots:
            if "missing @DOIT @BDA" in blindspot.lower():
                recommendations.append("Integrate @DOIT @BDA final step into affected workflows")
            elif "failures" in blindspot.lower():
                recommendations.append("Review and fix workflow failures")
            elif "errors" in blindspot.lower():
                recommendations.append("Investigate and resolve recent errors")
            elif "stuck" in blindspot.lower():
                recommendations.append("Restart or kill stuck processes")
            elif "resources" in blindspot.lower():
                recommendations.append("Allocate additional resources or optimize usage")
            elif "conflicts" in blindspot.lower():
                recommendations.append("Resolve workflow conflicts by adjusting schedules")

        # Remove duplicates
        return list(set(recommendations))

    def continuous_monitoring(self, interval_seconds: int = 60):
        """
        Continuous monitoring mode - continuously check mirrors

        Args:
            interval_seconds: Seconds between mirror checks
        """
        logger.info(f"\n🪞 Starting Continuous Mirror Monitoring")
        logger.info(f"   Check interval: {interval_seconds} seconds")
        logger.info("   (Like checking mirrors while driving)")

        import time

        try:
            while True:
                review = self.full_mirror_review()

                if review.overall_status != "clear":
                    logger.warning(f"\n⚠️  Blindspots detected! Status: {review.overall_status.upper()}")
                    for bs in review.blindspots_found:
                        logger.warning(f"   - {bs}")

                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("\n🛑 Continuous monitoring stopped")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description='Blindspot Mirror System')
        parser.add_argument('--rearview', action='store_true', help='Check rearview mirror')
        parser.add_argument('--side-left', action='store_true', help='Check left side mirror')
        parser.add_argument('--side-right', action='store_true', help='Check right side mirror')
        parser.add_argument('--full-review', action='store_true', help='Full mirror review (all mirrors)')
        parser.add_argument('--continuous', action='store_true', help='Continuous monitoring mode')
        parser.add_argument('--interval', type=int, default=60, help='Interval for continuous monitoring (seconds)')
        parser.add_argument('--json', action='store_true', help='Output as JSON')

        args = parser.parse_args()

        system = BlindspotMirrorSystem()

        if args.continuous:
            system.continuous_monitoring(interval_seconds=args.interval)

        elif args.full_review:
            review = system.full_mirror_review()
            if args.json:
                print(json.dumps(review.to_dict(), indent=2, default=str))

        elif args.rearview:
            check = system.check_rearview_mirror()
            if args.json:
                print(json.dumps(check.to_dict(), indent=2, default=str))

        elif args.side_left:
            check = system.check_side_left_mirror()
            if args.json:
                print(json.dumps(check.to_dict(), indent=2, default=str))

        elif args.side_right:
            check = system.check_side_right_mirror()
            if args.json:
                print(json.dumps(check.to_dict(), indent=2, default=str))

        else:
            # Default: full review
            review = system.full_mirror_review()
            if args.json:
                print(json.dumps(review.to_dict(), indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()