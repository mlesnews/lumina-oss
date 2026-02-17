#!/usr/bin/env python3
"""
Development Effectiveness Analyzer

Cross-references idle time (@IDLETIME) with development time to analyze
effectiveness patterns and improve ETA calculations for workflows.

Tags: #EFFECTIVENESS #ANALYTICS #IDLETIME #DEVELOPMENT_TIME #ETAs @JARVIS @LUMINA
"""

import sys
import json
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
    from idle_time_tracker import IdleTimeTracker
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    IdleTimeTracker = None

logger = get_logger("DevelopmentEffectivenessAnalyzer")


class DevelopmentEffectivenessAnalyzer:
    """
    Development Effectiveness Analyzer

    Analyzes development effectiveness by comparing:
    - Development time (WakaTime, Cursor IDE)
    - Idle time (@IDLETIME - screen sleep events)
    - Effectiveness patterns
    - ETA improvements
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize effectiveness analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "effectiveness"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.idle_tracker = IdleTimeTracker(project_root) if IdleTimeTracker else None

        logger.info("✅ Development Effectiveness Analyzer initialized")

    def get_wakatime_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get WakaTime data for date

        Args:
            date: Date (YYYY-MM-DD) or None for today

        Returns:
            WakaTime data
        """
        # TODO: Integrate with WakaTime API or local data  # [ADDRESSED]  # [ADDRESSED]
        # For now, return placeholder
        return {
            "date": date or datetime.now().strftime('%Y-%m-%d'),
            "total_seconds": 0,
            "total_hours": 0,
            "languages": {},
            "projects": {}
        }

    def get_cursor_ide_data(self, date: Optional[str] = None) -> Dict[str, Any]:
        try:
            """
            Get Cursor IDE development history data

            Args:
                date: Date (YYYY-MM-DD) or None for today

            Returns:
                Cursor IDE data
            """
            # TODO: Integrate with Cursor IDE development history  # [ADDRESSED]  # [ADDRESSED]
            # Check data/cursor_ide_features/ or similar
            cursor_data_dir = self.project_root / "data" / "cursor_ide_features"

            if cursor_data_dir.exists():
                # Look for date-specific files
                date_str = date or datetime.now().strftime('%Y-%m-%d')
                # Implementation would search for relevant files
                pass

            return {
                "date": date or datetime.now().strftime('%Y-%m-%d'),
                "total_seconds": 0,
                "total_hours": 0,
                "features_used": [],
                "sessions": []
            }

        except Exception as e:
            self.logger.error(f"Error in get_cursor_ide_data: {e}", exc_info=True)
            raise
    def analyze_effectiveness(
        self,
        date: Optional[str] = None,
        wakatime_data: Optional[Dict[str, Any]] = None,
        cursor_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze development effectiveness

        Args:
            date: Date to analyze
            wakatime_data: WakaTime data (if None, will fetch)
            cursor_data: Cursor IDE data (if None, will fetch)

        Returns:
            Effectiveness analysis
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        # Get data
        if wakatime_data is None:
            wakatime_data = self.get_wakatime_data(date)
        if cursor_data is None:
            cursor_data = self.get_cursor_ide_data(date)

        # Get idle time
        idle_summary = self.idle_tracker.get_daily_summary(date) if self.idle_tracker else {}

        # Calculate development time
        dev_time_seconds = max(
            wakatime_data.get("total_seconds", 0),
            cursor_data.get("total_seconds", 0)
        )

        # Compare with idle time
        if self.idle_tracker:
            comparison = self.idle_tracker.compare_with_development_time(dev_time_seconds, date)
        else:
            comparison = {
                "development_time_seconds": dev_time_seconds,
                "idle_time_seconds": 0,
                "effectiveness_ratio": float('inf')
            }

        # Calculate effectiveness metrics
        analysis = {
            "date": date,
            "development_time": {
                "seconds": dev_time_seconds,
                "hours": dev_time_seconds / 3600,
                "wakatime_seconds": wakatime_data.get("total_seconds", 0),
                "cursor_ide_seconds": cursor_data.get("total_seconds", 0)
            },
            "idle_time": {
                "seconds": idle_summary.get("total_idle_seconds", 0),
                "hours": idle_summary.get("total_idle_hours", 0),
                "sessions": idle_summary.get("idle_sessions_count", 0)
            },
            "effectiveness": {
                "development_percentage": comparison.get("development_percentage", 0),
                "idle_percentage": comparison.get("idle_percentage", 0),
                "effectiveness_ratio": comparison.get("effectiveness_ratio", 0),
                "total_time_hours": comparison.get("total_time_hours", 0)
            },
            "insights": self._generate_insights(comparison, dev_time_seconds, idle_summary),
            "recommendations": self._generate_recommendations(comparison, dev_time_seconds, idle_summary)
        }

        return analysis

    def _generate_insights(
        self,
        comparison: Dict[str, Any],
        dev_time: float,
        idle_summary: Dict[str, Any]
    ) -> List[str]:
        """Generate insights from analysis"""
        insights = []

        effectiveness_ratio = comparison.get("effectiveness_ratio", 0)
        dev_percentage = comparison.get("development_percentage", 0)

        if effectiveness_ratio > 2.0:
            insights.append("High effectiveness: Development time significantly exceeds idle time")
        elif effectiveness_ratio > 1.0:
            insights.append("Good effectiveness: Development time exceeds idle time")
        elif effectiveness_ratio > 0.5:
            insights.append("Moderate effectiveness: Development and idle time are balanced")
        else:
            insights.append("Low effectiveness: Idle time exceeds development time - consider optimizing workflow")

        if dev_percentage > 70:
            insights.append("High development focus: Over 70% of time spent in active development")
        elif dev_percentage > 50:
            insights.append("Balanced focus: Development and idle time are well balanced")
        else:
            insights.append("Low development focus: Less than 50% of time in active development")

        avg_idle = idle_summary.get("average_idle_duration_minutes", 0)
        if avg_idle > 60:
            insights.append(f"Long idle periods: Average idle duration is {avg_idle:.1f} minutes - may indicate breaks or distractions")
        elif avg_idle > 30:
            insights.append(f"Moderate idle periods: Average idle duration is {avg_idle:.1f} minutes")
        else:
            insights.append(f"Short idle periods: Average idle duration is {avg_idle:.1f} minutes - good focus")

        return insights

    def _generate_recommendations(
        self,
        comparison: Dict[str, Any],
        dev_time: float,
        idle_summary: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        effectiveness_ratio = comparison.get("effectiveness_ratio", 0)
        dev_percentage = comparison.get("development_percentage", 0)

        if effectiveness_ratio < 1.0:
            recommendations.append("Consider reducing idle time by setting shorter screen saver timeout during active work")
            recommendations.append("Review workflow to identify and minimize distractions")

        if dev_percentage < 50:
            recommendations.append("Increase development focus time - consider time-blocking techniques")
            recommendations.append("Track and minimize context switching")

        avg_idle = idle_summary.get("average_idle_duration_minutes", 0)
        if avg_idle > 60:
            recommendations.append("Long idle periods detected - consider using dynamic screen saver timeout based on activity")
            recommendations.append("Review idle patterns to identify optimal work times")

        return recommendations

    def calculate_workflow_eta(
        self,
        workflow_complexity: str,
        historical_days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate ETA for workflow based on historical effectiveness

        Args:
            workflow_complexity: low, medium, high
            historical_days: Number of days to analyze

        Returns:
            ETA calculation with effectiveness adjustments
        """
        # Get historical data
        historical_analyses = []
        for i in range(historical_days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            analysis = self.analyze_effectiveness(date)
            historical_analyses.append(analysis)

        # Calculate average effectiveness
        avg_effectiveness_ratio = sum(
            a["effectiveness"]["effectiveness_ratio"]
            for a in historical_analyses
            if a["effectiveness"]["effectiveness_ratio"] != float('inf')
        ) / len(historical_analyses) if historical_analyses else 1.0

        # Get ETA from idle tracker
        if self.idle_tracker:
            base_eta = self.idle_tracker.calculate_eta(workflow_complexity)
        else:
            base_eta = {
                "estimated_minutes": 60,
                "estimated_hours": 1.0
            }

        # Adjust for effectiveness
        effectiveness_adjustment = 1.0 / avg_effectiveness_ratio if avg_effectiveness_ratio > 0 else 1.0

        adjusted_minutes = base_eta.get("estimated_minutes", 60) * effectiveness_adjustment

        eta = {
            "workflow_complexity": workflow_complexity,
            "base_eta_minutes": base_eta.get("estimated_minutes", 60),
            "base_eta_hours": base_eta.get("estimated_hours", 1.0),
            "effectiveness_adjustment": effectiveness_adjustment,
            "adjusted_eta_minutes": adjusted_minutes,
            "adjusted_eta_hours": adjusted_minutes / 60,
            "historical_effectiveness_ratio": avg_effectiveness_ratio,
            "historical_days_analyzed": historical_days,
            "factors": {
                "idle_time_patterns": base_eta.get("factors", {}),
                "development_effectiveness": avg_effectiveness_ratio
            }
        }

        return eta


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Development Effectiveness Analyzer")
    parser.add_argument("--analyze", help="Analyze effectiveness for date (YYYY-MM-DD)")
    parser.add_argument("--calculate-workflow-eta", choices=["low", "medium", "high"], help="Calculate workflow ETA")
    parser.add_argument("--historical-days", type=int, default=7, help="Days of history to analyze")

    args = parser.parse_args()

    analyzer = DevelopmentEffectivenessAnalyzer()

    if args.analyze:
        analysis = analyzer.analyze_effectiveness(args.analyze)
        print("\n📊 Development Effectiveness Analysis\n")
        print(f"Date: {analysis['date']}")
        print(f"\nDevelopment Time: {analysis['development_time']['hours']:.2f} hours")
        print(f"Idle Time: {analysis['idle_time']['hours']:.2f} hours")
        print(f"Effectiveness Ratio: {analysis['effectiveness']['effectiveness_ratio']:.2f}")
        print(f"\nInsights:")
        for insight in analysis['insights']:
            print(f"  • {insight}")
        print(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  • {rec}")
    elif args.calculate_workflow_eta:
        eta = analyzer.calculate_workflow_eta(args.calculate_workflow_eta, args.historical_days)
        print("\n⏱️  Workflow ETA Calculation\n")
        print(f"Complexity: {eta['workflow_complexity']}")
        print(f"Base ETA: {eta['base_eta_hours']:.2f} hours")
        print(f"Adjusted ETA: {eta['adjusted_eta_hours']:.2f} hours")
        print(f"Effectiveness Adjustment: {eta['effectiveness_adjustment']:.2f}x")
        print(f"Historical Effectiveness: {eta['historical_effectiveness_ratio']:.2f}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())