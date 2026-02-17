#!/usr/bin/env python3
"""
YouTube Dynamic Scaling Module

Dynamically scales YouTube video processing based on user activity patterns.
Uses algebraic equations to calculate optimal batch sizes and processing limits.

Activity-Based Scaling Formula:
  scaling_factor = f(activity_level, historical_patterns, system_resources)
  optimal_batch_size = base_batch_size * scaling_factor

Tags: #YOUTUBE #DYNAMIC_SCALING #ACTIVITY_BASED #ALGEBRAIC @JARVIS @LUMINA
"""

import sys
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import deque
import statistics

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

logger = get_logger("YouTubeDynamicScaling")

# Import existing dynamic scaling modules
try:
    from lumina.dynamic_scaling import DynamicScalingModule, ResourceMetrics
    DYNAMIC_SCALING_AVAILABLE = True
except ImportError:
    DYNAMIC_SCALING_AVAILABLE = False
    logger.warning("Dynamic scaling module not available, using standalone mode")

try:
    from youtube_processed_tracker import YouTubeProcessedTracker
    TRACKER_AVAILABLE = True
except ImportError:
    TRACKER_AVAILABLE = False
    logger.warning("YouTube processed tracker not available")


@dataclass
class ActivityMetrics:
    """Activity metrics for YouTube processing"""
    videos_per_day: float  # Average videos watched per day
    videos_per_week: float  # Average videos watched per week
    videos_per_month: float  # Average videos watched per month
    activity_trend: str  # "increasing", "decreasing", "stable"
    peak_activity: float  # Peak videos per day
    low_activity: float  # Low videos per day
    activity_variance: float  # Variance in activity
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ScalingParameters:
    """Scaling parameters calculated from activity"""
    max_history_videos: int  # Maximum history videos to fetch
    max_recommended_videos: int  # Maximum recommended videos to fetch
    max_channel_videos: int  # Maximum channel videos to fetch
    history_timeout: int  # Timeout for history fetch (seconds)
    recommended_timeout: int  # Timeout for recommended fetch (seconds)
    channel_timeout: int  # Timeout for channel fetch (seconds)
    scaling_factor: float  # Overall scaling factor
    activity_level: str  # "light", "average", "heavy", "power"
    confidence: float  # Confidence in scaling decision (0.0-1.0)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class YouTubeDynamicScaling:
    """
    YouTube Dynamic Scaling Module

    Dynamically scales YouTube video processing based on:
    1. User activity (videos watched per day)
    2. Historical patterns
    3. System resources
    4. Processing capacity

    Uses algebraic equations to calculate optimal batch sizes.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize YouTube Dynamic Scaling"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "youtube_dynamic_scaling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Activity history (rolling window)
        self.activity_history: deque = deque(maxlen=90)  # 90 days of history

        # Base configuration
        self.base_config = {
            "max_history_videos": 500,
            "max_recommended_videos": 100,
            "max_channel_videos": 100,
            "history_timeout": 600,  # 10 minutes
            "recommended_timeout": 300,  # 5 minutes
            "channel_timeout": 300,  # 5 minutes
        }

        # Activity thresholds (videos per day)
        self.activity_thresholds = {
            "light": (0, 3),  # 0-3 videos/day
            "average": (3, 10),  # 3-10 videos/day
            "heavy": (10, 25),  # 10-25 videos/day
            "power": (25, float('inf'))  # 25+ videos/day
        }

        # Scaling multipliers by activity level
        self.scaling_multipliers = {
            "light": 0.5,  # Scale down for light users
            "average": 1.0,  # Base scaling
            "heavy": 2.0,  # Scale up 2x
            "power": 3.5  # Scale up 3.5x
        }

        # Resource-aware scaling
        if DYNAMIC_SCALING_AVAILABLE:
            self.resource_scaler = DynamicScalingModule()
        else:
            self.resource_scaler = None

        # Processed tracker
        if TRACKER_AVAILABLE:
            self.tracker = YouTubeProcessedTracker(self.project_root)
        else:
            self.tracker = None

        # Persistent storage
        self.activity_file = self.data_dir / "activity_history.json"
        self.scaling_config_file = self.data_dir / "scaling_config.json"

        # Load history
        self._load_activity_history()

        logger.info("📈 YouTube Dynamic Scaling initialized")
        logger.info("   Activity-based scaling enabled")
        logger.info("   Algebraic calculation engine ready")
        logger.info("   Resource-aware scaling: " + ("✅" if self.resource_scaler else "❌"))

    def calculate_activity_metrics(self, days: int = 90) -> ActivityMetrics:
        """
        Calculate activity metrics from history

        Args:
            days: Number of days to analyze

        Returns:
            Activity metrics
        """
        if not self.activity_history:
            # No history, return default
            return ActivityMetrics(
                videos_per_day=5.0,  # Default average
                videos_per_week=35.0,
                videos_per_month=150.0,
                activity_trend="stable",
                peak_activity=10.0,
                low_activity=1.0,
                activity_variance=0.0
            )

        # Get recent history
        recent_history = list(self.activity_history)[-days:] if len(self.activity_history) >= days else list(self.activity_history)

        if not recent_history:
            return ActivityMetrics(
                videos_per_day=5.0,
                videos_per_week=35.0,
                videos_per_month=150.0,
                activity_trend="stable",
                peak_activity=10.0,
                low_activity=1.0,
                activity_variance=0.0
            )

        # Calculate metrics
        videos_per_day = statistics.mean([h.get("videos_per_day", 0) for h in recent_history])
        videos_per_week = videos_per_day * 7
        videos_per_month = videos_per_day * 30

        # Calculate trend
        if len(recent_history) >= 7:
            recent_week = recent_history[-7:]
            older_week = recent_history[-14:-7] if len(recent_history) >= 14 else recent_history[:7]

            recent_avg = statistics.mean([h.get("videos_per_day", 0) for h in recent_week])
            older_avg = statistics.mean([h.get("videos_per_day", 0) for h in older_week])

            if recent_avg > older_avg * 1.1:
                activity_trend = "increasing"
            elif recent_avg < older_avg * 0.9:
                activity_trend = "decreasing"
            else:
                activity_trend = "stable"
        else:
            activity_trend = "stable"

        # Peak and low activity
        all_videos = [h.get("videos_per_day", 0) for h in recent_history]
        peak_activity = max(all_videos) if all_videos else 10.0
        low_activity = min(all_videos) if all_videos else 1.0

        # Variance
        activity_variance = statistics.variance(all_videos) if len(all_videos) > 1 else 0.0

        return ActivityMetrics(
            videos_per_day=videos_per_day,
            videos_per_week=videos_per_week,
            videos_per_month=videos_per_month,
            activity_trend=activity_trend,
            peak_activity=peak_activity,
            low_activity=low_activity,
            activity_variance=activity_variance
        )

    def determine_activity_level(self, metrics: ActivityMetrics) -> str:
        """
        Determine activity level from metrics

        Args:
            metrics: Activity metrics

        Returns:
            Activity level: "light", "average", "heavy", "power"
        """
        videos_per_day = metrics.videos_per_day

        for level, (min_v, max_v) in self.activity_thresholds.items():
            if min_v <= videos_per_day < max_v:
                return level

        # Default to average
        return "average"

    def calculate_scaling_factor(self, metrics: ActivityMetrics, activity_level: str) -> float:
        """
        Calculate scaling factor using algebraic equation

        Formula:
          base_factor = scaling_multipliers[activity_level]
          trend_factor = 1.0 + (trend_adjustment * trend_strength)
          variance_factor = 1.0 + (variance_adjustment * normalized_variance)
          scaling_factor = base_factor * trend_factor * variance_factor

        Args:
            metrics: Activity metrics
            activity_level: Activity level

        Returns:
            Scaling factor
        """
        # Base factor from activity level
        base_factor = self.scaling_multipliers.get(activity_level, 1.0)

        # Trend adjustment
        trend_adjustment = 0.1  # 10% adjustment per trend
        if metrics.activity_trend == "increasing":
            trend_factor = 1.0 + trend_adjustment
        elif metrics.activity_trend == "decreasing":
            trend_factor = 1.0 - (trend_adjustment * 0.5)  # Less aggressive downscaling
        else:
            trend_factor = 1.0

        # Variance adjustment (higher variance = more conservative scaling)
        variance_adjustment = 0.05  # 5% adjustment per unit variance
        normalized_variance = min(1.0, metrics.activity_variance / 100.0)  # Normalize to 0-1
        variance_factor = 1.0 - (variance_adjustment * normalized_variance)

        # Calculate final scaling factor
        scaling_factor = base_factor * trend_factor * variance_factor

        # Clamp to reasonable bounds
        scaling_factor = max(0.25, min(5.0, scaling_factor))

        logger.debug(f"   📊 Scaling calculation:")
        logger.debug(f"      Base factor: {base_factor:.2f}")
        logger.debug(f"      Trend factor: {trend_factor:.2f}")
        logger.debug(f"      Variance factor: {variance_factor:.2f}")
        logger.debug(f"      Final factor: {scaling_factor:.2f}")

        return scaling_factor

    def calculate_optimal_parameters(self, metrics: Optional[ActivityMetrics] = None) -> ScalingParameters:
        """
        Calculate optimal scaling parameters using algebraic equations

        Formula:
          max_videos = base_max * scaling_factor * resource_factor
          timeout = base_timeout * (1 + log(max_videos / base_max))

        Args:
            metrics: Activity metrics (if None, calculates from history)

        Returns:
            Optimal scaling parameters
        """
        # Get activity metrics
        if metrics is None:
            metrics = self.calculate_activity_metrics()

        # Determine activity level
        activity_level = self.determine_activity_level(metrics)

        # Calculate scaling factor
        scaling_factor = self.calculate_scaling_factor(metrics, activity_level)

        # Get resource metrics if available
        resource_factor = 1.0
        if self.resource_scaler:
            try:
                resource_metrics = self.resource_scaler.monitor_resources()
                # Use CPU and memory average as resource factor
                resource_utilization = (resource_metrics.cpu_percent + resource_metrics.memory_percent) / 200.0
                # Invert: lower utilization = higher factor (can process more)
                resource_factor = 1.0 + (1.0 - resource_utilization) * 0.5  # 0.5-1.5 range
                resource_factor = max(0.5, min(1.5, resource_factor))
            except Exception as e:
                logger.warning(f"   ⚠️  Could not get resource metrics: {e}")

        # Calculate optimal parameters
        # History videos: scale based on activity
        max_history_videos = int(self.base_config["max_history_videos"] * scaling_factor * resource_factor)

        # Recommended videos: scale less aggressively (recommended feed is smaller)
        recommended_scaling = min(2.0, scaling_factor)  # Cap at 2x
        max_recommended_videos = int(self.base_config["max_recommended_videos"] * recommended_scaling * resource_factor)

        # Channel videos: scale moderately
        channel_scaling = min(1.5, scaling_factor)  # Cap at 1.5x
        max_channel_videos = int(self.base_config["max_channel_videos"] * channel_scaling * resource_factor)

        # Calculate timeouts (logarithmic scaling)
        history_timeout = int(self.base_config["history_timeout"] * (1 + math.log(max_history_videos / self.base_config["max_history_videos"] + 1)))
        recommended_timeout = int(self.base_config["recommended_timeout"] * (1 + math.log(max_recommended_videos / self.base_config["max_recommended_videos"] + 1)))
        channel_timeout = int(self.base_config["channel_timeout"] * (1 + math.log(max_channel_videos / self.base_config["max_channel_videos"] + 1)))

        # Clamp timeouts to reasonable bounds
        history_timeout = max(300, min(1800, history_timeout))  # 5-30 minutes
        recommended_timeout = max(180, min(900, recommended_timeout))  # 3-15 minutes
        channel_timeout = max(180, min(900, channel_timeout))  # 3-15 minutes

        # Calculate confidence (based on history length and variance)
        history_length = len(self.activity_history)
        confidence = min(1.0, history_length / 30.0)  # 30 days = full confidence
        if metrics.activity_variance > 50:
            confidence *= 0.8  # Reduce confidence with high variance

        return ScalingParameters(
            max_history_videos=max_history_videos,
            max_recommended_videos=max_recommended_videos,
            max_channel_videos=max_channel_videos,
            history_timeout=history_timeout,
            recommended_timeout=recommended_timeout,
            channel_timeout=channel_timeout,
            scaling_factor=scaling_factor,
            activity_level=activity_level,
            confidence=confidence
        )

    def record_activity(self, videos_fetched: int, videos_processed: int, days: int = 90):
        """
        Record activity for scaling calculations

        Args:
            videos_fetched: Number of videos fetched
            videos_processed: Number of videos processed
            days: Time window (default: 90 days)
        """
        videos_per_day = videos_fetched / days if days > 0 else 0

        activity_record = {
            "timestamp": datetime.now().isoformat(),
            "videos_fetched": videos_fetched,
            "videos_processed": videos_processed,
            "videos_per_day": videos_per_day,
            "days": days
        }

        self.activity_history.append(activity_record)
        self._save_activity_history()

        logger.debug(f"   📊 Recorded activity: {videos_per_day:.1f} videos/day")

    def get_scaling_parameters(self) -> ScalingParameters:
        """
        Get current optimal scaling parameters

        Returns:
            Optimal scaling parameters
        """
        return self.calculate_optimal_parameters()

    def _load_activity_history(self):
        """Load activity history from disk"""
        if self.activity_file.exists():
            try:
                with open(self.activity_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    history = data.get("activity_history", [])
                    # Keep last 90 days
                    for record in history[-90:]:
                        self.activity_history.append(record)
                    logger.info(f"   📚 Loaded {len(self.activity_history)} activity records")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load activity history: {e}")

    def _save_activity_history(self):
        """Save activity history to disk"""
        try:
            with open(self.activity_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "activity_history": list(self.activity_history)
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving activity history: {e}")

    def get_scaling_report(self) -> Dict[str, Any]:
        """Get comprehensive scaling report"""
        metrics = self.calculate_activity_metrics()
        parameters = self.calculate_optimal_parameters(metrics)

        return {
            "timestamp": datetime.now().isoformat(),
            "activity_metrics": metrics.to_dict(),
            "scaling_parameters": parameters.to_dict(),
            "activity_history_length": len(self.activity_history),
            "resource_aware": self.resource_scaler is not None,
            "tracker_available": self.tracker is not None
        }


def main():
    try:
        """CLI interface for YouTube Dynamic Scaling"""
        import argparse

        parser = argparse.ArgumentParser(description="YouTube Dynamic Scaling - Activity-Based")
        parser.add_argument("--calculate", action="store_true", help="Calculate optimal parameters")
        parser.add_argument("--record", nargs=3, metavar=("FETCHED", "PROCESSED", "DAYS"),
                           type=int, help="Record activity (fetched, processed, days)")
        parser.add_argument("--report", action="store_true", help="Get scaling report")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        scaler = YouTubeDynamicScaling()

        if args.record:
            videos_fetched, videos_processed, days = args.record
            scaler.record_activity(videos_fetched, videos_processed, days)
            if args.json:
                print(json.dumps({"recorded": True, "videos_per_day": videos_fetched / days}, indent=2))
            else:
                print(f"✅ Recorded activity: {videos_fetched} fetched, {videos_processed} processed ({videos_fetched/days:.1f} videos/day)")

        elif args.report:
            report = scaler.get_scaling_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("\n📈 YouTube Dynamic Scaling Report")
                print("=" * 80)
                print(f"\nActivity Metrics:")
                metrics = report["activity_metrics"]
                print(f"  Videos/Day: {metrics['videos_per_day']:.1f}")
                print(f"  Videos/Week: {metrics['videos_per_week']:.1f}")
                print(f"  Activity Trend: {metrics['activity_trend']}")
                print(f"  Peak Activity: {metrics['peak_activity']:.1f} videos/day")
                print(f"\nScaling Parameters:")
                params = report["scaling_parameters"]
                print(f"  Activity Level: {params['activity_level']}")
                print(f"  Scaling Factor: {params['scaling_factor']:.2f}x")
                print(f"  Max History Videos: {params['max_history_videos']}")
                print(f"  Max Recommended Videos: {params['max_recommended_videos']}")
                print(f"  Max Channel Videos: {params['max_channel_videos']}")
                print(f"  History Timeout: {params['history_timeout']}s")
                print(f"  Confidence: {params['confidence']:.1%}")

        elif args.calculate or not any([args.record, args.report]):
            parameters = scaler.get_scaling_parameters()
            if args.json:
                print(json.dumps(parameters.to_dict(), indent=2))
            else:
                print("\n📈 YouTube Dynamic Scaling Parameters")
                print("=" * 80)
                print(f"Activity Level: {parameters.activity_level}")
                print(f"Scaling Factor: {parameters.scaling_factor:.2f}x")
                print(f"\nOptimal Limits:")
                print(f"  Max History Videos: {parameters.max_history_videos}")
                print(f"  Max Recommended Videos: {parameters.max_recommended_videos}")
                print(f"  Max Channel Videos: {parameters.max_channel_videos}")
                print(f"\nTimeouts:")
                print(f"  History: {parameters.history_timeout}s ({parameters.history_timeout/60:.1f} min)")
                print(f"  Recommended: {parameters.recommended_timeout}s ({parameters.recommended_timeout/60:.1f} min)")
                print(f"  Channel: {parameters.channel_timeout}s ({parameters.channel_timeout/60:.1f} min)")
                print(f"\nConfidence: {parameters.confidence:.1%}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()