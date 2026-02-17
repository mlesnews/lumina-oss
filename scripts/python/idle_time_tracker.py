#!/usr/bin/env python3
"""
Idle Time Tracker (@IDLETIME)

Tracks idle time by monitoring screen sleep events. When screen goes to sleep,
it indicates the user has gone idle. This is cross-referenced with development
time to calculate accurate ETAs and analyze effectiveness.

Tags: #IDLETIME #SCREEN_SLEEP #ETAs #EFFECTIVENESS #ANALYTICS @JARVIS @LUMINA
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
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

logger = get_logger("IdleTimeTracker")


class IdleTimeTracker:
    """
    Idle Time Tracker

    Tracks idle time by monitoring screen sleep events.
    Cross-references with development time for ETAs and effectiveness analysis.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize idle time tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "idle_time"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tracking_file = self.data_dir / "idle_time_tracking.json"
        self.daily_file = self.data_dir / f"idle_time_{datetime.now().strftime('%Y%m%d')}.json"

        self.tracking_data = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "idle_sessions": [],
            "daily_summary": {},
            "metadata": {
                "description": "Tracks idle time when screen goes to sleep",
                "purpose": "Compare with development time for ETAs and effectiveness analysis"
            }
        }

        self._load_tracking_data()
        logger.info("✅ Idle Time Tracker initialized")

    def _load_tracking_data(self):
        """Load tracking data"""
        try:
            if self.tracking_file.exists():
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    self.tracking_data = json.load(f)
                logger.info(f"   ✅ Loaded {len(self.tracking_data.get('idle_sessions', []))} idle sessions")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not load tracking data: {e}")

    def _save_tracking_data(self):
        """Save tracking data"""
        try:
            self.tracking_data["last_updated"] = datetime.now().isoformat()
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.tracking_data, f, indent=2, ensure_ascii=False)

            # Also save daily file
            today = datetime.now().strftime('%Y%m%d')
            daily_data = {
                "date": datetime.now().strftime('%Y-%m-%d'),
                "idle_sessions": [
                    s for s in self.tracking_data.get("idle_sessions", [])
                    if s.get("date") == datetime.now().strftime('%Y-%m-%d')
                ],
                "summary": self._calculate_daily_summary()
            }

            daily_file = self.data_dir / f"idle_time_{today}.json"
            with open(daily_file, 'w', encoding='utf-8') as f:
                json.dump(daily_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving tracking data: {e}")

    def record_idle_start(self, context: Optional[Dict[str, Any]] = None):
        """
        Record when idle period starts (screen goes to sleep)

        Args:
            context: Additional context about the idle period
        """
        idle_session = {
            "id": f"idle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "idle_start": datetime.now().isoformat(),
            "idle_end": None,
            "duration_seconds": None,
            "context": context or {},
            "metadata": {
                "trigger": "screen_sleep",
                "tracked_by": "idle_time_tracker"
            }
        }

        if "idle_sessions" not in self.tracking_data:
            self.tracking_data["idle_sessions"] = []

        self.tracking_data["idle_sessions"].append(idle_session)
        self._save_tracking_data()

        logger.info(f"   ✅ Idle session started: {idle_session['id']}")

        return idle_session["id"]

    def record_idle_end(self, session_id: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Record when idle period ends (screen wakes up)

        Args:
            session_id: Session ID to end (if None, ends most recent)
            context: Additional context
        """
        if session_id is None:
            # Find most recent idle session without an end time
            for session in reversed(self.tracking_data.get("idle_sessions", [])):
                if session.get("idle_end") is None:
                    session_id = session["id"]
                    break

        if session_id is None:
            logger.warning("   ⚠️  No active idle session found")
            return None

        # Find and update session
        for session in self.tracking_data.get("idle_sessions", []):
            if session["id"] == session_id:
                session["idle_end"] = datetime.now().isoformat()

                # Calculate duration
                start_time = datetime.fromisoformat(session["idle_start"])
                end_time = datetime.fromisoformat(session["idle_end"])
                duration = (end_time - start_time).total_seconds()
                session["duration_seconds"] = duration
                session["duration_minutes"] = duration / 60
                session["duration_hours"] = duration / 3600

                if context:
                    session["context"].update(context)

                self._save_tracking_data()

                logger.info(f"   ✅ Idle session ended: {session_id}")
                logger.info(f"      Duration: {session['duration_minutes']:.2f} minutes")

                return session

        logger.warning(f"   ⚠️  Session not found: {session_id}")
        return None

    def _calculate_daily_summary(self) -> Dict[str, Any]:
        """Calculate daily summary"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_sessions = [
            s for s in self.tracking_data.get("idle_sessions", [])
            if s.get("date") == today
        ]

        total_idle_seconds = sum(
            s.get("duration_seconds", 0) for s in today_sessions
            if s.get("duration_seconds") is not None
        )

        active_sessions = [s for s in today_sessions if s.get("idle_end") is None]

        summary = {
            "date": today,
            "total_idle_seconds": total_idle_seconds,
            "total_idle_minutes": total_idle_seconds / 60,
            "total_idle_hours": total_idle_seconds / 3600,
            "idle_sessions_count": len(today_sessions),
            "active_idle_sessions": len(active_sessions),
            "average_idle_duration_minutes": (
                total_idle_seconds / len(today_sessions) / 60
                if today_sessions else 0
            )
        }

        return summary

    def get_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get daily summary"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        return self._calculate_daily_summary()

    def compare_with_development_time(
        self,
        development_time_seconds: float,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare idle time with development time

        Args:
            development_time_seconds: Total development time in seconds
            date: Date to compare (if None, uses today)

        Returns:
            Comparison metrics
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        summary = self.get_daily_summary(date)
        idle_time_seconds = summary.get("total_idle_seconds", 0)

        total_time = development_time_seconds + idle_time_seconds

        comparison = {
            "date": date,
            "development_time_seconds": development_time_seconds,
            "development_time_hours": development_time_seconds / 3600,
            "idle_time_seconds": idle_time_seconds,
            "idle_time_hours": idle_time_seconds / 3600,
            "total_time_seconds": total_time,
            "total_time_hours": total_time / 3600,
            "development_percentage": (
                (development_time_seconds / total_time * 100) if total_time > 0 else 0
            ),
            "idle_percentage": (
                (idle_time_seconds / total_time * 100) if total_time > 0 else 0
            ),
            "effectiveness_ratio": (
                development_time_seconds / idle_time_seconds
                if idle_time_seconds > 0 else float('inf')
            )
        }

        return comparison

    def calculate_eta(
        self,
        task_complexity: str,
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculate ETA for a task based on idle time patterns

        Args:
            task_complexity: Task complexity (low, medium, high)
            historical_data: Historical development vs idle time data

        Returns:
            ETA calculation
        """
        # Get recent idle patterns
        recent_sessions = self.tracking_data.get("idle_sessions", [])[-30:]  # Last 30 sessions

        avg_idle_duration = sum(
            s.get("duration_minutes", 0) for s in recent_sessions
            if s.get("duration_minutes") is not None
        ) / len(recent_sessions) if recent_sessions else 0

        # Complexity multipliers
        complexity_multipliers = {
            "low": 1.0,
            "medium": 1.5,
            "high": 2.5
        }

        base_eta_minutes = 60  # Base 1 hour
        complexity_multiplier = complexity_multipliers.get(task_complexity, 1.5)

        # Adjust for idle time patterns
        idle_adjustment = 1.0 + (avg_idle_duration / 60) * 0.1  # 10% per hour of average idle

        estimated_minutes = base_eta_minutes * complexity_multiplier * idle_adjustment

        eta = {
            "task_complexity": task_complexity,
            "base_eta_minutes": base_eta_minutes,
            "complexity_multiplier": complexity_multiplier,
            "idle_adjustment": idle_adjustment,
            "estimated_minutes": estimated_minutes,
            "estimated_hours": estimated_minutes / 60,
            "factors": {
                "average_idle_duration_minutes": avg_idle_duration,
                "historical_sessions_analyzed": len(recent_sessions)
            }
        }

        return eta


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Idle Time Tracker")
    parser.add_argument("--idle-start", action="store_true", help="Record idle start (screen sleep)")
    parser.add_argument("--idle-end", action="store_true", help="Record idle end (screen wake)")
    parser.add_argument("--summary", action="store_true", help="Show daily summary")
    parser.add_argument("--compare", type=float, help="Compare with development time (seconds)")
    parser.add_argument("--calculate-eta", choices=["low", "medium", "high"], help="Calculate ETA for task complexity")

    args = parser.parse_args()

    tracker = IdleTimeTracker()

    if args.idle_start:
        session_id = tracker.record_idle_start()
        print(f"✅ Idle session started: {session_id}")
    elif args.idle_end:
        session = tracker.record_idle_end()
        if session:
            print(f"✅ Idle session ended: {session['id']}")
            print(f"   Duration: {session['duration_minutes']:.2f} minutes")
    elif args.summary:
        summary = tracker.get_daily_summary()
        print("\n📊 Daily Idle Time Summary\n")
        print(f"Date: {summary['date']}")
        print(f"Total Idle Time: {summary['total_idle_hours']:.2f} hours ({summary['total_idle_minutes']:.2f} minutes)")
        print(f"Idle Sessions: {summary['idle_sessions_count']}")
        print(f"Active Sessions: {summary['active_idle_sessions']}")
        print(f"Average Duration: {summary['average_idle_duration_minutes']:.2f} minutes")
    elif args.compare:
        comparison = tracker.compare_with_development_time(args.compare)
        print("\n📊 Development vs Idle Time Comparison\n")
        print(f"Development Time: {comparison['development_time_hours']:.2f} hours")
        print(f"Idle Time: {comparison['idle_time_hours']:.2f} hours")
        print(f"Total Time: {comparison['total_time_hours']:.2f} hours")
        print(f"Development %: {comparison['development_percentage']:.1f}%")
        print(f"Idle %: {comparison['idle_percentage']:.1f}%")
        print(f"Effectiveness Ratio: {comparison['effectiveness_ratio']:.2f}")
    elif args.calculate_eta:
        eta = tracker.calculate_eta(args.calculate_eta)
        print("\n⏱️  ETA Calculation\n")
        print(f"Task Complexity: {eta['task_complexity']}")
        print(f"Estimated Time: {eta['estimated_hours']:.2f} hours ({eta['estimated_minutes']:.2f} minutes)")
        print(f"Factors:")
        print(f"  Base ETA: {eta['base_eta_minutes']} minutes")
        print(f"  Complexity Multiplier: {eta['complexity_multiplier']}x")
        print(f"  Idle Adjustment: {eta['idle_adjustment']:.2f}x")
        print(f"  Average Idle Duration: {eta['factors']['average_idle_duration_minutes']:.2f} minutes")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())