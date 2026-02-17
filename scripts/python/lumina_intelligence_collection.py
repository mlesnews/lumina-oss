#!/usr/bin/env python3
"""
LUMINA Intelligence Collection System

Hourly and daily intelligence collection, collation, and aggregation:
- Hourly data collection
- Daily aggregation
- Data collation and structuring
- Dynamic/evolutionary initiative generation (NOT static)
- Actionable initiatives from data

Tags: #LUMINA #INTELLIGENCE #DATA_COLLECTION #AGGREGATION #INITIATIVES @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

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

logger = get_logger("LUMINAIntelligence")


class CollectionFrequency(Enum):
    """Collection frequency"""
    HOURLY = "hourly"
    DAILY = "daily"
    REAL_TIME = "real_time"


class DataSource(Enum):
    """Data sources"""
    USER_INTERACTIONS = "user_interactions"
    SYSTEM_METRICS = "system_metrics"
    COACHING_SESSIONS = "coaching_sessions"
    TASK_COMPLETION = "task_completion"
    GOAL_PROGRESS = "goal_progress"
    HABIT_TRACKING = "habit_tracking"
    MOOD_ENERGY = "mood_energy"
    TIME_USAGE = "time_usage"
    PRODUCTIVITY = "productivity"
    LEARNING = "learning"


@dataclass
class IntelligenceDataPoint:
    """A single intelligence data point"""
    data_id: str
    source: str  # DataSource value
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregatedIntelligence:
    """Aggregated intelligence data"""
    aggregation_id: str
    frequency: str  # CollectionFrequency value
    period_start: str
    period_end: str
    data_points: List[IntelligenceDataPoint] = field(default_factory=list)
    aggregated_metrics: Dict[str, Any] = field(default_factory=dict)
    patterns: List[Dict[str, Any]] = field(default_factory=list)
    trends: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionableInitiative:
    """An actionable initiative (dynamic/evolutionary, NOT static)"""
    initiative_id: str
    title: str
    description: str
    priority: int = 5  # 1-10
    category: str = ""
    life_domain: Optional[str] = None
    data_evidence: List[str] = field(default_factory=list)
    action_steps: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    success_metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    evolution_level: float = 1.0  # Dynamic - evolves based on results
    effectiveness_history: List[float] = field(default_factory=list)
    is_static: bool = False  # MUST be False - initiatives are dynamic
    metadata: Dict[str, Any] = field(default_factory=dict)


# Auto-register with cron scheduler
try:
    from auto_cron_registration import CronScheduleConfig, get_registry
    AUTO_CRON_AVAILABLE = True
except ImportError:
    AUTO_CRON_AVAILABLE = False
    logger.debug("   Auto cron registration not available")


class LUMINAIntelligenceCollection:
    """
    LUMINA Intelligence Collection System

    Hourly and daily intelligence:
    - Data collection from multiple sources
    - Collation and aggregation
    - Pattern recognition
    - Trend analysis
    - Dynamic/evolutionary initiative generation (NOT static)

    Auto-registered with cron scheduler for hourly and daily runs.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intelligence collection system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "intelligence_collection"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data directories
        self.hourly_dir = self.data_dir / "hourly"
        self.hourly_dir.mkdir(exist_ok=True)
        self.daily_dir = self.data_dir / "daily"
        self.daily_dir.mkdir(exist_ok=True)
        self.initiatives_dir = self.data_dir / "initiatives"
        self.initiatives_dir.mkdir(exist_ok=True)

        # Current collections
        self.hourly_collection: Optional[AggregatedIntelligence] = None
        self.daily_collection: Optional[AggregatedIntelligence] = None

        # Initiatives (dynamic/evolutionary)
        self.initiatives: Dict[str, ActionableInitiative] = {}

        # Auto-register with cron scheduler
        if AUTO_CRON_AVAILABLE:
            try:
                registry = get_registry()

                # Register hourly collection
                registry.register_service(
                    service_id="lumina-intelligence-hourly",
                    service_name="LUMINA Intelligence Collection - Hourly",
                    script_path="scripts/python/lumina_intelligence_collection.py",
                    schedule_config=CronScheduleConfig.hourly(
                        minute=0,
                        description="Hourly intelligence data collection",
                        tags=["intelligence", "hourly", "data_collection"]
                    ),
                    command_template="python /volume1/docker/lumina/scripts/python/lumina_intelligence_collection.py --collect-hourly",
                    auto_deploy=True
                )

                # Register daily aggregation
                registry.register_service(
                    service_id="lumina-intelligence-daily",
                    service_name="LUMINA Intelligence Collection - Daily",
                    script_path="scripts/python/lumina_intelligence_collection.py",
                    schedule_config=CronScheduleConfig.daily(
                        hour=2,
                        minute=0,
                        description="Daily intelligence aggregation",
                        tags=["intelligence", "daily", "aggregation"]
                    ),
                    command_template="python /volume1/docker/lumina/scripts/python/lumina_intelligence_collection.py --aggregate-daily",
                    auto_deploy=True
                )

                logger.info("   ✅ Auto-registered with cron scheduler")
            except Exception as e:
                logger.debug(f"   Could not auto-register with cron: {e}")

        logger.info("✅ LUMINA Intelligence Collection System initialized")
        logger.info("   Hourly collection: Ready")
        logger.info("   Daily aggregation: Ready")
        logger.info("   Initiative generation: Dynamic/Evolutionary (NOT static)")

    def collect_hourly_intelligence(self) -> AggregatedIntelligence:
        """
        Collect hourly intelligence

        Gathers data from all sources for the current hour
        """
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        collection_id = f"hourly_{hour_start.strftime('%Y%m%d_%H%M%S')}"

        # Collect data from all sources
        data_points = []

        # User interactions
        data_points.append(IntelligenceDataPoint(
            data_id=f"user_int_{now.strftime('%Y%m%d_%H%M%S')}",
            source=DataSource.USER_INTERACTIONS.value,
            timestamp=now.isoformat(),
            data={"interactions": self._collect_user_interactions(hour_start, hour_end)}
        ))

        # System metrics
        data_points.append(IntelligenceDataPoint(
            data_id=f"sys_metrics_{now.strftime('%Y%m%d_%H%M%S')}",
            source=DataSource.SYSTEM_METRICS.value,
            timestamp=now.isoformat(),
            data={"metrics": self._collect_system_metrics()}
        ))

        # Coaching sessions
        data_points.append(IntelligenceDataPoint(
            data_id=f"coaching_{now.strftime('%Y%m%d_%H%M%S')}",
            source=DataSource.COACHING_SESSIONS.value,
            timestamp=now.isoformat(),
            data={"sessions": self._collect_coaching_sessions(hour_start, hour_end)}
        ))

        # Task completion
        data_points.append(IntelligenceDataPoint(
            data_id=f"tasks_{now.strftime('%Y%m%d_%H%M%S')}",
            source=DataSource.TASK_COMPLETION.value,
            timestamp=now.isoformat(),
            data={"tasks": self._collect_task_completion(hour_start, hour_end)}
        ))

        # Aggregate metrics
        aggregated_metrics = self._aggregate_metrics(data_points)

        # Identify patterns
        patterns = self._identify_patterns(data_points)

        # Identify trends
        trends = self._identify_trends(data_points)

        aggregation = AggregatedIntelligence(
            aggregation_id=collection_id,
            frequency=CollectionFrequency.HOURLY.value,
            period_start=hour_start.isoformat(),
            period_end=hour_end.isoformat(),
            data_points=data_points,
            aggregated_metrics=aggregated_metrics,
            patterns=patterns,
            trends=trends
        )

        # Save hourly collection
        self._save_collection(aggregation, self.hourly_dir)
        self.hourly_collection = aggregation

        logger.info(f"   📊 Hourly intelligence collected: {len(data_points)} data points")

        return aggregation

    def aggregate_daily_intelligence(self) -> AggregatedIntelligence:
        """
        Aggregate daily intelligence

        Aggregates all hourly collections for the day
        """
        today = datetime.now().date()
        day_start = datetime.combine(today, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        collection_id = f"daily_{today.strftime('%Y%m%d')}"

        # Load all hourly collections for the day
        hourly_collections = self._load_hourly_collections(day_start, day_end)

        # Aggregate all data points
        all_data_points = []
        for hourly in hourly_collections:
            all_data_points.extend(hourly.data_points)

        # Aggregate metrics across all hours
        aggregated_metrics = self._aggregate_metrics(all_data_points)

        # Identify daily patterns
        patterns = self._identify_patterns(all_data_points)

        # Identify daily trends
        trends = self._identify_trends(all_data_points)

        # Cross-hour analysis
        cross_hour_analysis = self._cross_hour_analysis(hourly_collections)

        aggregation = AggregatedIntelligence(
            aggregation_id=collection_id,
            frequency=CollectionFrequency.DAILY.value,
            period_start=day_start.isoformat(),
            period_end=day_end.isoformat(),
            data_points=all_data_points,
            aggregated_metrics=aggregated_metrics,
            patterns=patterns,
            trends=trends,
            metadata={"cross_hour_analysis": cross_hour_analysis}
        )

        # Save daily aggregation
        self._save_collection(aggregation, self.daily_dir)
        self.daily_collection = aggregation

        logger.info(f"   📊 Daily intelligence aggregated: {len(all_data_points)} data points from {len(hourly_collections)} hours")

        return aggregation

    def generate_actionable_initiatives(
        self,
        aggregation: Optional[AggregatedIntelligence] = None
    ) -> List[ActionableInitiative]:
        """
        Generate actionable initiatives from intelligence data

        CRITICAL: Initiatives are dynamic/evolutionary, NOT static
        - Evolve based on results
        - Adapt to changing patterns
        - Learn from effectiveness
        """
        if aggregation is None:
            aggregation = self.daily_collection or self.hourly_collection

        if aggregation is None:
            logger.warning("No aggregation data available")
            return []

        initiatives = []

        # Generate initiatives from patterns
        for pattern in aggregation.patterns:
            initiative = self._pattern_to_initiative(pattern, aggregation)
            if initiative:
                initiatives.append(initiative)

        # Generate initiatives from trends
        for trend in aggregation.trends:
            initiative = self._trend_to_initiative(trend, aggregation)
            if initiative:
                initiatives.append(initiative)

        # Generate initiatives from metrics
        metric_initiatives = self._metrics_to_initiatives(aggregation.aggregated_metrics, aggregation)
        initiatives.extend(metric_initiatives)

        # Save initiatives
        for initiative in initiatives:
            self.initiatives[initiative.initiative_id] = initiative
            self._save_initiative(initiative)

        logger.info(f"   🎯 Generated {len(initiatives)} actionable initiatives (dynamic/evolutionary)")

        return initiatives

    def _collect_user_interactions(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Collect user interaction data"""
        # This would collect from actual interaction logs
        return {
            "count": 0,  # Placeholder
            "types": [],
            "duration": 0
        }

    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "active_systems": []
        }

    def _collect_coaching_sessions(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """Collect coaching session data"""
        return []

    def _collect_task_completion(self, start: datetime, end: datetime) -> Dict[str, Any]:
        """Collect task completion data"""
        return {
            "completed": 0,
            "pending": 0,
            "overdue": 0
        }

    def _aggregate_metrics(self, data_points: List[IntelligenceDataPoint]) -> Dict[str, Any]:
        """Aggregate metrics from data points"""
        metrics = {}

        for point in data_points:
            source = point.source
            if source not in metrics:
                metrics[source] = {}

            # Aggregate data
            for key, value in point.data.items():
                if key not in metrics[source]:
                    metrics[source][key] = []
                metrics[source][key].append(value)

        # Calculate aggregates
        aggregated = {}
        for source, source_metrics in metrics.items():
            aggregated[source] = {}
            for key, values in source_metrics.items():
                if isinstance(values[0], (int, float)):
                    aggregated[source][key] = {
                        "sum": sum(values),
                        "avg": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "count": len(values)
                    }
                else:
                    aggregated[source][key] = values

        return aggregated

    def _identify_patterns(self, data_points: List[IntelligenceDataPoint]) -> List[Dict[str, Any]]:
        """Identify patterns in data"""
        patterns = []

        # Simple pattern identification (can be enhanced with ML)
        # Group by time, source, etc.

        return patterns

    def _identify_trends(self, data_points: List[IntelligenceDataPoint]) -> List[Dict[str, Any]]:
        """Identify trends in data"""
        trends = []

        # Simple trend identification (can be enhanced)

        return trends

    def _cross_hour_analysis(self, hourly_collections: List[AggregatedIntelligence]) -> Dict[str, Any]:
        """Cross-hour analysis"""
        return {
            "hourly_variation": {},
            "peak_hours": [],
            "low_hours": []
        }

    def _pattern_to_initiative(
        self,
        pattern: Dict[str, Any],
        aggregation: AggregatedIntelligence
    ) -> Optional[ActionableInitiative]:
        """Convert pattern to actionable initiative (dynamic)"""
        initiative_id = f"initiative_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        initiative = ActionableInitiative(
            initiative_id=initiative_id,
            title=f"Initiative from Pattern: {pattern.get('type', 'Unknown')}",
            description=f"Actionable initiative based on identified pattern",
            priority=7,
            data_evidence=[f"Pattern: {pattern}"],
            action_steps=["Analyze pattern", "Create action plan", "Execute", "Monitor"],
            expected_outcome="Improved outcomes based on pattern",
            created_at=datetime.now().isoformat(),
            is_static=False,  # CRITICAL: Dynamic, not static
            evolution_level=1.0,
            metadata={"source": "pattern", "pattern_data": pattern}
        )

        return initiative

    def _trend_to_initiative(
        self,
        trend: Dict[str, Any],
        aggregation: AggregatedIntelligence
    ) -> Optional[ActionableInitiative]:
        """Convert trend to actionable initiative (dynamic)"""
        initiative_id = f"initiative_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        initiative = ActionableInitiative(
            initiative_id=initiative_id,
            title=f"Initiative from Trend: {trend.get('direction', 'Unknown')}",
            description=f"Actionable initiative based on identified trend",
            priority=6,
            data_evidence=[f"Trend: {trend}"],
            action_steps=["Analyze trend", "Create response plan", "Execute", "Monitor"],
            expected_outcome="Trend addressed or leveraged",
            created_at=datetime.now().isoformat(),
            is_static=False,  # CRITICAL: Dynamic
            evolution_level=1.0,
            metadata={"source": "trend", "trend_data": trend}
        )

        return initiative

    def _metrics_to_initiatives(
        self,
        metrics: Dict[str, Any],
        aggregation: AggregatedIntelligence
    ) -> List[ActionableInitiative]:
        """Generate initiatives from metrics (dynamic)"""
        initiatives = []

        # Generate initiatives based on metric thresholds, anomalies, etc.

        return initiatives

    def evolve_initiative(
        self,
        initiative_id: str,
        effectiveness: float,
        new_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Evolve an initiative based on results

        CRITICAL: Initiatives evolve, they are NOT static
        """
        if initiative_id not in self.initiatives:
            return False

        initiative = self.initiatives[initiative_id]

        # Record effectiveness
        initiative.effectiveness_history.append(effectiveness)
        if len(initiative.effectiveness_history) > 100:
            initiative.effectiveness_history.pop(0)

        # Evolve based on effectiveness
        avg_effectiveness = sum(initiative.effectiveness_history) / len(initiative.effectiveness_history)

        if avg_effectiveness > 0.8:
            # High effectiveness - can expand or optimize
            initiative.evolution_level = min(2.0, initiative.evolution_level * 1.1)
        elif avg_effectiveness < 0.5:
            # Low effectiveness - adapt or retire
            initiative.evolution_level = max(0.5, initiative.evolution_level * 0.9)

        # Update with new data
        if new_data:
            initiative.metadata.update(new_data)

        # Ensure it's not static
        initiative.is_static = False

        self._save_initiative(initiative)

        logger.info(f"   🔄 Initiative evolved: {initiative_id} (effectiveness: {avg_effectiveness:.2f})")

        return True

    def _save_collection(self, aggregation: AggregatedIntelligence, directory: Path):
        """Save collection to file"""
        file_path = directory / f"{aggregation.aggregation_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Convert to dict, handling nested dataclasses
                data = asdict(aggregation)
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving collection: {e}")

    def _load_hourly_collections(self, start: datetime, end: datetime) -> List[AggregatedIntelligence]:
        """Load hourly collections for a period"""
        collections = []

        current = start
        while current < end:
            collection_id = f"hourly_{current.strftime('%Y%m%d_%H%M%S')}"
            file_path = self.hourly_dir / f"{collection_id}.json"

            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Reconstruct data points
                        data_points = [
                            IntelligenceDataPoint(**dp) for dp in data.get('data_points', [])
                        ]
                        data['data_points'] = data_points
                        collections.append(AggregatedIntelligence(**data))
                except Exception as e:
                    logger.debug(f"Could not load collection {collection_id}: {e}")

            current += timedelta(hours=1)

        return collections

    def _save_initiative(self, initiative: ActionableInitiative):
        """Save initiative"""
        file_path = self.initiatives_dir / f"{initiative.initiative_id}.json"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(initiative), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving initiative: {e}")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Intelligence Collection")
        parser.add_argument("--collect-hourly", action="store_true", help="Collect hourly intelligence")
        parser.add_argument("--aggregate-daily", action="store_true", help="Aggregate daily intelligence")
        parser.add_argument("--generate-initiatives", action="store_true", help="Generate actionable initiatives")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        intel = LUMINAIntelligenceCollection()

        if args.collect_hourly:
            collection = intel.collect_hourly_intelligence()
            if args.json:
                print(json.dumps(asdict(collection), indent=2, default=str))
            else:
                print(f"✅ Hourly intelligence collected: {collection.aggregation_id}")

        elif args.aggregate_daily:
            aggregation = intel.aggregate_daily_intelligence()
            if args.json:
                print(json.dumps(asdict(aggregation), indent=2, default=str))
            else:
                print(f"✅ Daily intelligence aggregated: {aggregation.aggregation_id}")

        elif args.generate_initiatives:
            initiatives = intel.generate_actionable_initiatives()
            if args.json:
                print(json.dumps([asdict(i) for i in initiatives], indent=2, default=str))
            else:
                print(f"✅ Generated {len(initiatives)} initiatives")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()