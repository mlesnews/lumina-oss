#!/usr/bin/env python3
"""
Temporal Pattern Recognition - Time-Based Predictive Analysis

This system analyzes temporal patterns across master sessions to predict workflow
success/failure based on time-based behavioral patterns. It recognizes cycles,
seasonal trends, and temporal correlations that affect system performance.

Key Capabilities:
1. Cyclical Pattern Detection - Identify recurring patterns over time
2. Seasonal Trend Analysis - Recognize seasonal variations in performance
3. Time-Based Correlations - Find relationships between time factors and outcomes
4. Predictive Forecasting - Forecast future performance based on temporal patterns
5. Peak Performance Prediction - Identify optimal times for operations
6. Temporal Anomaly Detection - Detect unusual temporal behavior
"""

import json
import math
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import numpy as np
from collections import defaultdict, Counter
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from psychohistory_engine import PsychohistoryEngine
    PSYCHOHISTORY_AVAILABLE = True
except ImportError:
    PSYCHOHISTORY_AVAILABLE = False

try:
    from seldon_psychohistory_math import SeldonPsychohistoryMath
    SELDON_MATH_AVAILABLE = True
except ImportError:
    SELDON_MATH_AVAILABLE = False

try:
    from master_session_manager import MasterSessionManager
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False


class TemporalPatternType(Enum):
    """Types of temporal patterns"""
    HOURLY_CYCLE = "hourly_cycle"          # Patterns repeating every hour
    DAILY_CYCLE = "daily_cycle"            # Daily patterns
    WEEKLY_CYCLE = "weekly_cycle"          # Weekly patterns
    MONTHLY_CYCLE = "monthly_cycle"        # Monthly patterns
    SEASONAL_TREND = "seasonal_trend"      # Seasonal variations
    LONG_TERM_TREND = "long_term_trend"    # Long-term trends
    IRREGULAR_SPIKE = "irregular_spike"    # Irregular but recurring spikes
    TEMPORAL_CORRELATION = "temporal_correlation"  # Time-based correlations


class TimeResolution(Enum):
    """Time resolution for analysis"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


@dataclass
class TemporalPattern:
    """A detected temporal pattern"""
    pattern_id: str
    pattern_type: TemporalPatternType
    description: str
    time_resolution: TimeResolution
    cycle_length: int  # Length of cycle in time units
    strength: float  # Pattern strength (0.0 to 1.0)
    confidence: float  # Statistical confidence (0.0 to 1.0)
    peak_times: List[int]  # Peak times within cycle (in time units)
    trough_times: List[int]  # Trough times within cycle
    affected_metrics: List[str]  # Metrics affected by this pattern
    predictive_accuracy: float  # How well this predicts future behavior
    discovered_at: datetime = field(default_factory=datetime.now)
    last_validated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["pattern_type"] = self.pattern_type.value
        data["time_resolution"] = self.time_resolution.value
        data["discovered_at"] = self.discovered_at.isoformat()
        if self.last_validated:
            data["last_validated"] = self.last_validated.isoformat()
        return data

    def predict_value(self, target_time: datetime, base_value: float = 1.0) -> float:
        """Predict value at target time based on this pattern"""
        # Convert target time to cycle position
        cycle_position = self._get_cycle_position(target_time)

        # Find closest peak/trough
        closest_peak_distance = min(abs(cycle_position - peak) for peak in self.peak_times) if self.peak_times else self.cycle_length
        closest_trough_distance = min(abs(cycle_position - trough) for trough in self.trough_times) if self.trough_times else self.cycle_length

        # Calculate multiplicative factor
        if closest_peak_distance <= 1:  # Within 1 unit of peak
            factor = 1.0 + (self.strength * 0.5)  # +50% at peak
        elif closest_trough_distance <= 1:  # Within 1 unit of trough
            factor = 1.0 - (self.strength * 0.3)  # -30% at trough
        else:
            factor = 1.0  # Baseline

        return base_value * factor

    def _get_cycle_position(self, target_time: datetime) -> int:
        """Get position within cycle for target time"""
        if self.time_resolution == TimeResolution.HOUR:
            # Position within day (0-23)
            return target_time.hour
        elif self.time_resolution == TimeResolution.DAY:
            # Day of week (0-6)
            return target_time.weekday()
        elif self.time_resolution == TimeResolution.WEEK:
            # Week of month (0-3)
            return target_time.day // 7
        elif self.time_resolution == TimeResolution.MONTH:
            # Month of year (0-11)
            return target_time.month - 1
        else:
            # Default to hour
            return target_time.hour


@dataclass
class TemporalForecast:
    """A temporal forecast based on patterns"""
    forecast_id: str
    target_metric: str
    forecast_time: datetime
    predicted_value: float
    confidence_interval: Tuple[float, float]
    contributing_patterns: List[str]  # Pattern IDs that contributed
    forecast_horizon: int  # hours into future
    accuracy_estimate: float  # Estimated accuracy (0.0 to 1.0)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["forecast_time"] = self.forecast_time.isoformat()
        data["generated_at"] = self.generated_at.isoformat()
        return data


@dataclass
class TimeSeriesData:
    """Time series data for analysis"""
    metric_name: str
    timestamps: List[datetime]
    values: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamps"] = [ts.isoformat() for ts in self.timestamps]
        return data

    def add_data_point(self, timestamp: datetime, value: float):
        """Add a data point to the time series"""
        self.timestamps.append(timestamp)
        self.values.append(value)

    def get_recent_data(self, hours: int = 24) -> Tuple[List[datetime], List[float]]:
        """Get data from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_indices = [i for i, ts in enumerate(self.timestamps) if ts >= cutoff_time]

        return (
            [self.timestamps[i] for i in recent_indices],
            [self.values[i] for i in recent_indices]
        )


class TemporalPatternRecognition:
    """
    Temporal Pattern Recognition System

    Analyzes time-based patterns to predict workflow success/failure and
    optimize system performance based on temporal behavior.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data" / "temporal_patterns"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.time_series_dir = self.data_dir / "time_series"
        self.time_series_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.patterns_file = self.data_dir / "temporal_patterns.json"
        self.forecasts_file = self.data_dir / "temporal_forecasts.json"
        self.time_series_file = self.data_dir / "time_series_data.json"

        # State
        self.temporal_patterns: Dict[str, TemporalPattern] = {}
        self.temporal_forecasts: Dict[str, TemporalForecast] = {}
        self.time_series_data: Dict[str, TimeSeriesData] = {}

        # Analysis parameters
        self.min_data_points = 24  # Minimum data points for analysis
        self.confidence_threshold = 0.6  # Minimum confidence for patterns
        self.forecast_horizon_hours = 24  # How far to forecast

        # Integration
        self.psychohistory_engine = None
        self.seldon_math = None
        self.master_session_manager = None

        if PSYCHOHISTORY_AVAILABLE:
            try:
                self.psychohistory_engine = PsychohistoryEngine(project_root=self.project_root)
                self.logger.info("✅ Psychohistory Engine integrated")
            except Exception as e:
                self.logger.warning(f"Psychohistory Engine integration failed: {e}")

        if SELDON_MATH_AVAILABLE:
            try:
                self.seldon_math = SeldonPsychohistoryMath(project_root=self.project_root)
                self.logger.info("✅ Seldon Mathematics integrated")
            except Exception as e:
                self.logger.warning(f"Seldon Mathematics integration failed: {e}")

        if MASTER_SESSION_AVAILABLE:
            try:
                self.master_session_manager = MasterSessionManager(project_root=self.project_root)
                self.logger.info("✅ Master Session Manager integrated")
            except Exception as e:
                self.logger.warning(f"Master Session Manager integration failed: {e}")

        self.logger = get_logger("TemporalPatternRecognition")
        self._load_state()
        self._initialize_time_series()

    def _load_state(self):
        """Load temporal pattern recognition state"""
        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    for pattern_id, pattern_data in patterns_data.items():
                        pattern_data["pattern_type"] = TemporalPatternType(pattern_data["pattern_type"])
                        pattern_data["time_resolution"] = TimeResolution(pattern_data["time_resolution"])
                        pattern_data["discovered_at"] = datetime.fromisoformat(pattern_data["discovered_at"])
                        if pattern_data.get("last_validated"):
                            pattern_data["last_validated"] = datetime.fromisoformat(pattern_data["last_validated"])
                        self.temporal_patterns[pattern_id] = TemporalPattern(**pattern_data)
            except Exception as e:
                self.logger.warning(f"Could not load patterns: {e}")

        # Load forecasts
        if self.forecasts_file.exists():
            try:
                with open(self.forecasts_file, 'r', encoding='utf-8') as f:
                    forecasts_data = json.load(f)
                    for forecast_id, forecast_data in forecasts_data.items():
                        forecast_data["forecast_time"] = datetime.fromisoformat(forecast_data["forecast_time"])
                        forecast_data["generated_at"] = datetime.fromisoformat(forecast_data["generated_at"])
                        self.temporal_forecasts[forecast_id] = TemporalForecast(**forecast_data)
            except Exception as e:
                self.logger.warning(f"Could not load forecasts: {e}")

        # Load time series
        if self.time_series_file.exists():
            try:
                with open(self.time_series_file, 'r', encoding='utf-8') as f:
                    ts_data = json.load(f)
                    for metric_name, data in ts_data.items():
                        data["timestamps"] = [datetime.fromisoformat(ts) for ts in data["timestamps"]]
                        self.time_series_data[metric_name] = TimeSeriesData(**data)
            except Exception as e:
                self.logger.warning(f"Could not load time series: {e}")

    def _save_state(self):
        try:
            """Save temporal pattern recognition state"""
            # Save patterns
            patterns_data = {pid: pattern.to_dict() for pid, pattern in self.temporal_patterns.items()}
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)

            # Save forecasts
            forecasts_data = {fid: forecast.to_dict() for fid, forecast in self.temporal_forecasts.items()}
            with open(self.forecasts_file, 'w', encoding='utf-8') as f:
                json.dump(forecasts_data, f, indent=2, ensure_ascii=False)

            # Save time series
            ts_data = {name: ts.to_dict() for name, ts in self.time_series_data.items()}
            with open(self.time_series_file, 'w', encoding='utf-8') as f:
                json.dump(ts_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def _initialize_time_series(self):
        """Initialize core time series metrics"""
        core_metrics = [
            "workflow_success_rate",
            "session_activity_level",
            "system_health_score",
            "resource_utilization_cpu",
            "resource_utilization_memory",
            "agent_spawn_rate",
            "error_rate",
            "response_time"
        ]

        for metric in core_metrics:
            if metric not in self.time_series_data:
                self.time_series_data[metric] = TimeSeriesData(
                    metric_name=metric,
                    timestamps=[],
                    values=[],
                    metadata={"description": f"Time series data for {metric}"}
                )

        self._save_state()

    def collect_temporal_data(self):
        """
        Collect temporal data from integrated systems

        This gathers time-stamped data from all integrated components.
        """
        self.logger.debug("📊 Collecting temporal data...")

        current_time = datetime.now()

        # Collect from psychohistory engine
        if self.psychohistory_engine:
            try:
                status = self.psychohistory_engine.get_psychohistory_status()
                if "prediction_accuracy" in status:
                    self.time_series_data["workflow_success_rate"].add_data_point(
                        current_time, status["prediction_accuracy"]
                    )
            except Exception as e:
                self.logger.debug(f"Could not collect psychohistory data: {e}")

        # Collect from Seldon mathematics
        if self.seldon_math:
            try:
                math_status = self.seldon_math.get_mathematical_status()
                if "overall_accuracy" in math_status:
                    self.time_series_data["system_health_score"].add_data_point(
                        current_time, math_status["overall_accuracy"]
                    )
            except Exception as e:
                self.logger.debug(f"Could not collect Seldon math data: {e}")

        # Collect from master session manager
        if self.master_session_manager:
            try:
                session_summary = self.master_session_manager.get_master_session_summary()
                if "error" not in session_summary:
                    activity_level = session_summary.get("chat_entries", 0) / 100.0  # Normalize
                    self.time_series_data["session_activity_level"].add_data_point(
                        current_time, min(activity_level, 1.0)
                    )
            except Exception as e:
                self.logger.debug(f"Could not collect session data: {e}")

        # Simulate additional metrics (would come from real monitoring)
        self.time_series_data["resource_utilization_cpu"].add_data_point(
            current_time, 0.3 + 0.4 * np.random.random()  # 30-70% CPU
        )
        self.time_series_data["resource_utilization_memory"].add_data_point(
            current_time, 0.4 + 0.3 * np.random.random()  # 40-70% memory
        )
        self.time_series_data["agent_spawn_rate"].add_data_point(
            current_time, 0.1 * np.random.random()  # 0-10% spawn rate
        )
        self.time_series_data["error_rate"].add_data_point(
            current_time, 0.05 * np.random.random()  # 0-5% error rate
        )
        self.time_series_data["response_time"].add_data_point(
            current_time, 0.5 + 0.5 * np.random.random()  # 0.5-1.0 seconds
        )

        self._save_state()

    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """
        Analyze temporal patterns in the collected data

        This is the core pattern recognition algorithm.
        """
        self.logger.info("🔍 Analyzing temporal patterns...")

        # Ensure we have data to analyze
        self.collect_temporal_data()

        analysis_results = {
            "patterns_detected": 0,
            "forecasts_generated": 0,
            "metrics_analyzed": len(self.time_series_data),
            "data_points_total": sum(len(ts.values) for ts in self.time_series_data.values()),
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Analyze each time series for patterns
        for metric_name, time_series in self.time_series_data.items():
            if len(time_series.values) >= self.min_data_points:
                patterns = self._analyze_single_time_series(metric_name, time_series)
                analysis_results["patterns_detected"] += len(patterns)

        # Generate forecasts based on patterns
        forecasts = self._generate_temporal_forecasts()
        analysis_results["forecasts_generated"] += len(forecasts)

        self._save_state()

        self.logger.info(f"✅ Temporal analysis complete: {analysis_results['patterns_detected']} patterns, {analysis_results['forecasts_generated']} forecasts")

        return analysis_results

    def _analyze_single_time_series(self, metric_name: str, time_series: TimeSeriesData) -> List[TemporalPattern]:
        """Analyze a single time series for temporal patterns"""
        patterns = []

        # Get recent data (last 7 days)
        timestamps, values = time_series.get_recent_data(hours=168)  # 7 days

        if len(values) < self.min_data_points:
            return patterns

        # Convert to numpy arrays for analysis
        values_array = np.array(values)

        # 1. Analyze hourly patterns (if we have hourly data)
        if len(values) >= 24:  # At least 24 hours of data
            hourly_pattern = self._detect_hourly_pattern(metric_name, timestamps, values_array)
            if hourly_pattern:
                patterns.append(hourly_pattern)

        # 2. Analyze daily patterns (if we have daily data)
        if len(values) >= 7 * 24:  # At least 7 days of data
            daily_pattern = self._detect_daily_pattern(metric_name, timestamps, values_array)
            if daily_pattern:
                patterns.append(daily_pattern)

        # 3. Analyze weekly patterns (if we have weekly data)
        if len(values) >= 4 * 7 * 24:  # At least 4 weeks of data
            weekly_pattern = self._detect_weekly_pattern(metric_name, timestamps, values_array)
            if weekly_pattern:
                patterns.append(weekly_pattern)

        # 4. Analyze long-term trends
        if len(values) >= 30 * 24:  # At least 30 days of data
            trend_pattern = self._detect_trend_pattern(metric_name, timestamps, values_array)
            if trend_pattern:
                patterns.append(trend_pattern)

        # 5. Analyze cyclical patterns using autocorrelation
        cycle_pattern = self._detect_cyclical_pattern(metric_name, values_array)
        if cycle_pattern:
            patterns.append(cycle_pattern)

        return patterns

    def _detect_hourly_pattern(self, metric_name: str, timestamps: List[datetime],
                             values: np.ndarray) -> Optional[TemporalPattern]:
        """Detect hourly patterns within a day"""
        try:
            # Group by hour of day
            hourly_averages = {}
            for ts, val in zip(timestamps, values):
                hour = ts.hour
                if hour not in hourly_averages:
                    hourly_averages[hour] = []
                hourly_averages[hour].append(val)

            # Calculate average for each hour
            hourly_means = {hour: statistics.mean(vals) for hour, vals in hourly_averages.items()}

            if len(hourly_means) < 12:  # Need at least half a day
                return None

            # Find peaks and troughs
            sorted_hours = sorted(hourly_means.keys())
            hourly_values = [hourly_means[h] for h in sorted_hours]

            peaks = self._find_peaks(hourly_values)
            troughs = self._find_troughs(hourly_values)

            # Calculate pattern strength (coefficient of variation)
            mean_val = statistics.mean(hourly_values)
            std_val = statistics.stdev(hourly_values)
            strength = std_val / mean_val if mean_val > 0 else 0

            if strength > 0.1:  # Significant variation
                pattern = TemporalPattern(
                    pattern_id=f"hourly_{metric_name}_{int(datetime.now().timestamp())}",
                    pattern_type=TemporalPatternType.HOURLY_CYCLE,
                    description=f"Hourly pattern in {metric_name} with {strength:.1%} variation",
                    time_resolution=TimeResolution.HOUR,
                    cycle_length=24,
                    strength=strength,
                    confidence=min(strength * 10, 0.9),  # Higher variation = higher confidence
                    peak_times=[sorted_hours[p] for p in peaks],
                    trough_times=[sorted_hours[t] for t in troughs],
                    affected_metrics=[metric_name],
                    predictive_accuracy=strength * 0.8
                )
                self.temporal_patterns[pattern.pattern_id] = pattern
                return pattern

        except Exception as e:
            self.logger.debug(f"Hourly pattern detection failed for {metric_name}: {e}")

        return None

    def _detect_daily_pattern(self, metric_name: str, timestamps: List[datetime],
                            values: np.ndarray) -> Optional[TemporalPattern]:
        """Detect daily patterns (weekday vs weekend)"""
        try:
            # Group by day of week
            daily_averages = {}
            for ts, val in zip(timestamps, values):
                weekday = ts.weekday()  # 0=Monday, 6=Sunday
                if weekday not in daily_averages:
                    daily_averages[weekday] = []
                daily_averages[weekday].append(val)

            # Calculate average for each weekday
            daily_means = {day: statistics.mean(vals) for day, vals in daily_averages.items()}

            if len(daily_means) < 5:  # Need most weekdays
                return None

            # Find weekday vs weekend pattern
            weekday_vals = [daily_means.get(d, 0) for d in range(5)]  # Mon-Fri
            weekend_vals = [daily_means.get(d, 0) for d in [5, 6]]   # Sat-Sun

            if weekday_vals and weekend_vals:
                weekday_avg = statistics.mean(weekday_vals)
                weekend_avg = statistics.mean(weekend_vals)

                # Calculate difference
                difference = abs(weekday_avg - weekend_avg)
                avg_value = (weekday_avg + weekend_avg) / 2
                strength = difference / avg_value if avg_value > 0 else 0

                if strength > 0.15:  # Significant weekday/weekend difference
                    peak_times = [5, 6] if weekend_avg > weekday_avg else [0, 1, 2, 3, 4]
                    trough_times = [0, 1, 2, 3, 4] if weekend_avg > weekday_avg else [5, 6]

                    pattern = TemporalPattern(
                        pattern_id=f"daily_{metric_name}_{int(datetime.now().timestamp())}",
                        pattern_type=TemporalPatternType.DAILY_CYCLE,
                        description=f"Daily pattern in {metric_name}: {'weekends' if weekend_avg > weekday_avg else 'weekdays'} show higher activity",
                        time_resolution=TimeResolution.DAY,
                        cycle_length=7,
                        strength=strength,
                        confidence=0.8,
                        peak_times=peak_times,
                        trough_times=trough_times,
                        affected_metrics=[metric_name],
                        predictive_accuracy=strength * 0.9
                    )
                    self.temporal_patterns[pattern.pattern_id] = pattern
                    return pattern

        except Exception as e:
            self.logger.debug(f"Daily pattern detection failed for {metric_name}: {e}")

        return None

    def _detect_weekly_pattern(self, metric_name: str, timestamps: List[datetime],
                             values: np.ndarray) -> Optional[TemporalPattern]:
        """Detect weekly patterns (weeks of month)"""
        try:
            # Group by week of month
            weekly_averages = {}
            for ts, val in zip(timestamps, values):
                week_of_month = (ts.day - 1) // 7  # 0-3 (roughly)
                if week_of_month not in weekly_averages:
                    weekly_averages[week_of_month] = []
                weekly_averages[week_of_month].append(val)

            # Calculate averages
            weekly_means = {week: statistics.mean(vals) for week, vals in weekly_averages.items()}

            if len(weekly_means) < 3:  # Need at least 3 weeks
                return None

            # Find variation
            weekly_values = list(weekly_means.values())
            mean_val = statistics.mean(weekly_values)
            std_val = statistics.stdev(weekly_values)
            strength = std_val / mean_val if mean_val > 0 else 0

            if strength > 0.1:
                # Find peak week
                peak_week = max(weekly_means.keys(), key=lambda k: weekly_means[k])
                trough_week = min(weekly_means.keys(), key=lambda k: weekly_means[k])

                pattern = TemporalPattern(
                    pattern_id=f"weekly_{metric_name}_{int(datetime.now().timestamp())}",
                    pattern_type=TemporalPatternType.WEEKLY_CYCLE,
                    description=f"Weekly pattern in {metric_name} with peak in week {peak_week + 1} of month",
                    time_resolution=TimeResolution.WEEK,
                    cycle_length=4,
                    strength=strength,
                    confidence=0.7,
                    peak_times=[peak_week],
                    trough_times=[trough_week],
                    affected_metrics=[metric_name],
                    predictive_accuracy=strength * 0.7
                )
                self.temporal_patterns[pattern.pattern_id] = pattern
                return pattern

        except Exception as e:
            self.logger.debug(f"Weekly pattern detection failed for {metric_name}: {e}")

        return None

    def _detect_trend_pattern(self, metric_name: str, timestamps: List[datetime],
                            values: np.ndarray) -> Optional[TemporalPattern]:
        """Detect long-term trends"""
        try:
            # Simple linear regression for trend
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)

            # Calculate trend strength
            trend_magnitude = abs(slope) * len(values)
            avg_value = np.mean(values)
            strength = trend_magnitude / avg_value if avg_value > 0 else 0

            if strength > 0.05:  # Significant trend
                direction = "increasing" if slope > 0 else "decreasing"

                pattern = TemporalPattern(
                    pattern_id=f"trend_{metric_name}_{direction}_{int(datetime.now().timestamp())}",
                    pattern_type=TemporalPatternType.LONG_TERM_TREND,
                    description=f"Long-term {direction} trend in {metric_name} with strength {strength:.1%}",
                    time_resolution=TimeResolution.MONTH,
                    cycle_length=12,  # Annual cycle (placeholder)
                    strength=strength,
                    confidence=0.6,
                    peak_times=[],  # Not applicable for trends
                    trough_times=[],
                    affected_metrics=[metric_name],
                    predictive_accuracy=strength * 0.6
                )
                self.temporal_patterns[pattern.pattern_id] = pattern
                return pattern

        except Exception as e:
            self.logger.debug(f"Trend pattern detection failed for {metric_name}: {e}")

        return None

    def _detect_cyclical_pattern(self, metric_name: str, values: np.ndarray) -> Optional[TemporalPattern]:
        """Detect cyclical patterns using autocorrelation"""
        try:
            # Calculate autocorrelation
            autocorr = np.correlate(values, values, mode='full')
            autocorr = autocorr[autocorr.size // 2:]  # Second half
            autocorr = autocorr / autocorr[0]  # Normalize

            # Find peaks in autocorrelation (potential periods)
            peaks = []
            for i in range(1, min(len(autocorr)-1, 50)):  # Check first 50 lags
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1] and autocorr[i] > 0.3:
                    peaks.append((i, autocorr[i]))

            if peaks:
                best_peak = max(peaks, key=lambda x: x[1])
                period, strength = best_peak

                if strength > 0.4:  # Strong cyclical component
                    pattern = TemporalPattern(
                        pattern_id=f"cycle_{metric_name}_period_{period}_{int(datetime.now().timestamp())}",
                        pattern_type=TemporalPatternType.IRREGULAR_SPIKE,
                        description=f"Cyclical pattern in {metric_name} with period {period} and strength {strength:.1%}",
                        time_resolution=TimeResolution.HOUR,  # Assume hourly for now
                        cycle_length=period,
                        strength=strength,
                        confidence=strength * 0.8,
                        peak_times=[],  # Would need more sophisticated analysis
                        trough_times=[],
                        affected_metrics=[metric_name],
                        predictive_accuracy=strength * 0.7
                    )
                    self.temporal_patterns[pattern.pattern_id] = pattern
                    return pattern

        except Exception as e:
            self.logger.debug(f"Cyclical pattern detection failed for {metric_name}: {e}")

        return None

    def _find_peaks(self, values: List[float]) -> List[int]:
        """Find peak indices in a list of values"""
        peaks = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
        return peaks

    def _find_troughs(self, values: List[float]) -> List[int]:
        """Find trough indices in a list of values"""
        troughs = []
        for i in range(1, len(values) - 1):
            if values[i] < values[i-1] and values[i] < values[i+1]:
                troughs.append(i)
        return troughs

    def _generate_temporal_forecasts(self) -> List[TemporalForecast]:
        """Generate forecasts based on detected temporal patterns"""
        forecasts = []

        # Forecast each metric for the next 24 hours
        for metric_name in self.time_series_data.keys():
            forecast = self._forecast_metric(metric_name, hours_ahead=24)
            if forecast:
                forecasts.append(forecast)

        return forecasts

    def _forecast_metric(self, metric_name: str, hours_ahead: int) -> Optional[TemporalForecast]:
        """Forecast a specific metric using temporal patterns"""
        if metric_name not in self.time_series_data:
            return None

        time_series = self.time_series_data[metric_name]
        if len(time_series.values) < 5:
            return None

        # Get current value as baseline
        current_value = time_series.values[-1]
        forecast_time = datetime.now() + timedelta(hours=hours_ahead)

        # Apply relevant patterns
        relevant_patterns = [
            pattern for pattern in self.temporal_patterns.values()
            if metric_name in pattern.affected_metrics and pattern.confidence >= self.confidence_threshold
        ]

        if not relevant_patterns:
            # No patterns, use current value
            predicted_value = current_value
            confidence_interval = (current_value * 0.8, current_value * 1.2)
            contributing_patterns = []
            accuracy_estimate = 0.5
        else:
            # Apply pattern predictions
            pattern_predictions = []
            for pattern in relevant_patterns:
                prediction = pattern.predict_value(forecast_time, current_value)
                pattern_predictions.append(prediction)

            # Average predictions
            predicted_value = statistics.mean(pattern_predictions)

            # Calculate confidence interval based on pattern agreement
            if len(pattern_predictions) > 1:
                std_dev = statistics.stdev(pattern_predictions)
                confidence_interval = (
                    predicted_value - 1.96 * std_dev,
                    predicted_value + 1.96 * std_dev
                )
            else:
                confidence_interval = (predicted_value * 0.9, predicted_value * 1.1)

            contributing_patterns = [p.pattern_id for p in relevant_patterns]
            accuracy_estimate = statistics.mean([p.predictive_accuracy for p in relevant_patterns])

        forecast = TemporalForecast(
            forecast_id=f"forecast_{metric_name}_{int(datetime.now().timestamp())}",
            target_metric=metric_name,
            forecast_time=forecast_time,
            predicted_value=predicted_value,
            confidence_interval=confidence_interval,
            contributing_patterns=contributing_patterns,
            forecast_horizon=hours_ahead,
            accuracy_estimate=accuracy_estimate
        )

        self.temporal_forecasts[forecast.forecast_id] = forecast
        return forecast

    def get_optimal_schedule(self, task_type: str = "general") -> Dict[str, Any]:
        """
        Get optimal scheduling recommendations based on temporal patterns

        This tells users when to schedule tasks for maximum success.
        """
        recommendations = {
            "optimal_times": [],
            "avoid_times": [],
            "peak_performance_periods": [],
            "low_performance_periods": [],
            "confidence": 0.0,
            "based_on_patterns": 0
        }

        # Find patterns that affect workflow success
        success_patterns = [
            pattern for pattern in self.temporal_patterns.values()
            if "workflow_success" in pattern.affected_metrics and pattern.confidence > 0.6
        ]

        if success_patterns:
            recommendations["based_on_patterns"] = len(success_patterns)

            # Extract optimal times from patterns
            all_peak_times = []
            all_trough_times = []

            for pattern in success_patterns:
                all_peak_times.extend(pattern.peak_times)
                all_trough_times.extend(pattern.trough_times)

            # Count occurrences
            peak_counts = Counter(all_peak_times)
            trough_counts = Counter(all_trough_times)

            # Get most common optimal times
            recommendations["optimal_times"] = [time for time, count in peak_counts.most_common(3)]
            recommendations["avoid_times"] = [time for time, count in trough_counts.most_common(3)]

            # Calculate average confidence
            recommendations["confidence"] = statistics.mean([p.confidence for p in success_patterns])

        return recommendations

    def predict_workflow_success(self, scheduled_time: datetime) -> Dict[str, Any]:
        """
        Predict workflow success probability for a given time

        This is the core predictive capability for scheduling.
        """
        prediction = {
            "scheduled_time": scheduled_time.isoformat(),
            "success_probability": 0.5,  # Baseline
            "confidence": 0.0,
            "contributing_factors": [],
            "recommendations": []
        }

        # Get relevant patterns
        relevant_patterns = [
            pattern for pattern in self.temporal_patterns.values()
            if "workflow_success" in pattern.affected_metrics and pattern.confidence >= 0.5
        ]

        if relevant_patterns:
            # Calculate success probability based on patterns
            base_probability = 0.5
            adjustments = []

            for pattern in relevant_patterns:
                adjustment = pattern.predict_value(scheduled_time, 1.0) - 1.0  # Deviation from baseline
                adjustments.append(adjustment)
                prediction["contributing_factors"].append({
                    "pattern": pattern.description,
                    "impact": adjustment,
                    "confidence": pattern.confidence
                })

            # Apply average adjustment
            avg_adjustment = statistics.mean(adjustments) if adjustments else 0
            prediction["success_probability"] = max(0.1, min(0.9, base_probability + avg_adjustment))
            prediction["confidence"] = statistics.mean([p.confidence for p in relevant_patterns])

            # Generate recommendations
            if prediction["success_probability"] > 0.7:
                prediction["recommendations"].append("Excellent time for scheduling - high success probability")
            elif prediction["success_probability"] > 0.5:
                prediction["recommendations"].append("Good time for scheduling - moderate success probability")
            else:
                prediction["recommendations"].append("Consider rescheduling - low success probability predicted")
                prediction["recommendations"].append("Alternative times may yield better results")

        return prediction

    def get_temporal_status(self) -> Dict[str, Any]:
        """Get temporal pattern recognition status"""
        return {
            "patterns_detected": len(self.temporal_patterns),
            "active_forecasts": len(self.temporal_forecasts),
            "metrics_tracked": len(self.time_series_data),
            "total_data_points": sum(len(ts.values) for ts in self.time_series_data.values()),
            "pattern_types": self._count_pattern_types(),
            "last_analysis": datetime.now().isoformat(),
            "forecast_accuracy": self._calculate_forecast_accuracy()
        }

    def _count_pattern_types(self) -> Dict[str, int]:
        """Count patterns by type"""
        counts = {}
        for pattern in self.temporal_patterns.values():
            pattern_type = pattern.pattern_type.value
            counts[pattern_type] = counts.get(pattern_type, 0) + 1
        return counts

    def _calculate_forecast_accuracy(self) -> float:
        """Calculate forecast accuracy (simplified)"""
        # In practice, would compare forecasts to actual outcomes
        # For now, return average pattern predictive accuracy

        if not self.temporal_patterns:
            return 0.0

        accuracies = [p.predictive_accuracy for p in self.temporal_patterns.values()]
        return statistics.mean(accuracies) if accuracies else 0.0


def main():
    """Main execution"""
    temporal_recognition = TemporalPatternRecognition()

    print("⏰ Temporal Pattern Recognition - Time-Based Predictive Analysis")
    print("=" * 80)
    print("")

    # Analyze temporal patterns
    analysis = temporal_recognition.analyze_temporal_patterns()
    print("🔍 Temporal Analysis:")
    print(f"   Patterns Detected: {analysis['patterns_detected']}")
    print(f"   Forecasts Generated: {analysis['forecasts_generated']}")
    print(f"   Metrics Analyzed: {analysis['metrics_analyzed']}")
    print(f"   Total Data Points: {analysis['data_points_total']}")
    print("")

    # Get optimal schedule
    schedule = temporal_recognition.get_optimal_schedule()
    print("📅 Optimal Scheduling Recommendations:")
    print(f"   Optimal Times: {schedule['optimal_times']}")
    print(f"   Times to Avoid: {schedule['avoid_times']}")
    print(f"   Confidence: {schedule['confidence']:.1%}")
    print(f"   Based on {schedule['based_on_patterns']} patterns")
    print("")

    # Predict workflow success for different times
    test_times = [
        datetime.now() + timedelta(hours=1),
        datetime.now() + timedelta(hours=6),
        datetime.now() + timedelta(hours=12),
        datetime.now() + timedelta(hours=18)
    ]

    print("🎯 Workflow Success Predictions:")
    for test_time in test_times:
        prediction = temporal_recognition.predict_workflow_success(test_time)
        print(f"   {test_time.strftime('%H:%M')}: {prediction['success_probability']:.1%} success ({prediction['confidence']:.1%} confidence)")

    print("")
    print("⏰ Temporal pattern recognition active: Predicting the future through time analysis.")


if __name__ == "__main__":


    main()