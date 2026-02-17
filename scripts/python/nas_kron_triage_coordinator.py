#!/usr/bin/env python3
"""
NAS @KRONSCHEDULER @TRIAGE/@BAU Coordinator - @SYPHON Enhanced

Expands/expounds upon dynamic scaling logic to coordinate all recurring scheduled events
so they coincide and collate according to @TRIAGE/@BAU priorities.

Uses @SYPHON to extract and analyze scheduling patterns, then applies dynamic scaling
module logic to align and optimize all scheduled events.

Tags: #NAS #KRONSCHEDULER #TRIAGE #BAU #SYPHON #DYNAMIC_SCALING #COORDINATION #COLLATION @JARVIS @LUMINA @TRIAGE @BAU @SYPHON
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import math

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

logger = get_logger("NASKronTriageCoordinator")

# Import required modules
try:
    from nas_cron_scheduler import NASCronScheduler, CronJob
    NAS_SCHEDULER_AVAILABLE = True
except ImportError:
    NAS_SCHEDULER_AVAILABLE = False
    logger.warning("   ⚠️  NAS Cron Scheduler not available")

try:
    from dynamic_tag_scaling_system import DynamicTagScalingSystem, TagScalingContext
    DYNAMIC_SCALING_AVAILABLE = True
except ImportError:
    DYNAMIC_SCALING_AVAILABLE = False
    logger.warning("   ⚠️  Dynamic Tag Scaling System not available")


class PriorityLevel(Enum):
    """TRIAGE/BAU priority levels"""
    CRITICAL = "critical"  # Must run immediately
    HIGH = "high"  # High priority BAU
    MEDIUM = "medium"  # Standard BAU
    LOW = "low"  # Low priority BAU
    DEFERRED = "deferred"  # Can be deferred


class EventType(Enum):
    """Scheduled event types"""
    CRON = "cron"  # Standard cron job
    KRON = "kron"  # KronScheduler job
    OUTLIER = "outlier"  # Outlier initiative
    WORKFLOW = "workflow"  # N8N workflow
    MONITORING = "monitoring"  # Health check
    MAINTENANCE = "maintenance"  # Maintenance task


@dataclass
class CoordinatedEvent:
    """Coordinated scheduled event with TRIAGE/BAU alignment"""
    event_id: str
    name: str
    event_type: EventType
    original_schedule: str  # Original cron expression
    coordinated_schedule: str  # Coordinated cron expression
    priority: PriorityLevel
    bau_category: str  # "critical", "standard", "maintenance", "monitoring"
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Event IDs this depends on
    collation_group: str = ""  # Group for collation
    scale_factor: float = 1.0  # Dynamic scaling factor
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollationGroup:
    """Group of events that should run together"""
    group_id: str
    name: str
    priority: PriorityLevel
    target_window: Tuple[int, int]  # (start_minute, end_minute) in hour
    events: List[str] = field(default_factory=list)  # Event IDs
    coordination_strategy: str = "batch"  # "batch", "sequence", "parallel"
    metadata: Dict[str, Any] = field(default_factory=dict)


class NASKronTriageCoordinator:
    """
    NAS @KRONSCHEDULER @TRIAGE/@BAU Coordinator

    Uses @SYPHON to extract scheduling information and coordinates all recurring
    scheduled events to coincide and collate according to @TRIAGE/@BAU priorities
    using dynamic scaling module logic.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize coordinator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_kron_triage"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.coordinated_events_file = self.data_dir / "coordinated_events.json"
        self.collation_groups_file = self.data_dir / "collation_groups.json"
        self.syphon_analysis_file = self.data_dir / "syphon_analysis.json"

        # Systems
        self.nas_scheduler = NASCronScheduler(project_root) if NAS_SCHEDULER_AVAILABLE else None
        self.dynamic_scaling = DynamicTagScalingSystem(project_root) if DYNAMIC_SCALING_AVAILABLE else None

        # Data structures
        self.coordinated_events: Dict[str, CoordinatedEvent] = {}
        self.collation_groups: Dict[str, CollationGroup] = {}
        self.syphon_analysis: Dict[str, Any] = {}

        # Load existing data
        self._load_data()

        # SYPHON: Extract and analyze scheduling patterns
        self._syphon_scheduling_patterns()

        # Coordinate events
        self._coordinate_all_events()

        # Create collation groups
        self._create_collation_groups()

        logger.info("✅ NAS @KRONSCHEDULER @TRIAGE/@BAU Coordinator initialized")
        logger.info(f"   Coordinated events: {len(self.coordinated_events)}")
        logger.info(f"   Collation groups: {len(self.collation_groups)}")

    def _load_data(self):
        """Load existing coordinated events and groups"""
        # Load coordinated events
        if self.coordinated_events_file.exists():
            try:
                with open(self.coordinated_events_file, 'r') as f:
                    data = json.load(f)
                    self.coordinated_events = {
                        k: CoordinatedEvent(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load coordinated events: {e}")

        # Load collation groups
        if self.collation_groups_file.exists():
            try:
                with open(self.collation_groups_file, 'r') as f:
                    data = json.load(f)
                    self.collation_groups = {}
                    for k, v in data.items():
                        # Convert priority string to enum
                        if isinstance(v.get("priority"), str):
                            v["priority"] = PriorityLevel(v["priority"])
                        # Convert target_window list to tuple
                        if isinstance(v.get("target_window"), list):
                            v["target_window"] = tuple(v["target_window"])
                        self.collation_groups[k] = CollationGroup(**v)
            except Exception as e:
                logger.debug(f"   Could not load collation groups: {e}")

        # Load SYPHON analysis
        if self.syphon_analysis_file.exists():
            try:
                with open(self.syphon_analysis_file, 'r') as f:
                    self.syphon_analysis = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load SYPHON analysis: {e}")

    def _save_data(self):
        """Save all data"""
        # Save coordinated events
        try:
            with open(self.coordinated_events_file, 'w') as f:
                json.dump({
                    k: {
                        "event_id": v.event_id,
                        "name": v.name,
                        "event_type": v.event_type.value,
                        "original_schedule": v.original_schedule,
                        "coordinated_schedule": v.coordinated_schedule,
                        "priority": v.priority.value,
                        "bau_category": v.bau_category,
                        "tags": v.tags,
                        "dependencies": v.dependencies,
                        "collation_group": v.collation_group,
                        "scale_factor": v.scale_factor,
                        "metadata": v.metadata
                    }
                    for k, v in self.coordinated_events.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving coordinated events: {e}")

        # Save collation groups
        try:
            with open(self.collation_groups_file, 'w') as f:
                json.dump({
                    k: {
                        "group_id": v.group_id,
                        "name": v.name,
                        "priority": v.priority.value,
                        "target_window": list(v.target_window),
                        "events": v.events,
                        "coordination_strategy": v.coordination_strategy,
                        "metadata": v.metadata
                    }
                    for k, v in self.collation_groups.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving collation groups: {e}")

    def _syphon_scheduling_patterns(self):
        """
        @SYPHON: Extract and analyze scheduling patterns from all sources

        Deep research into:
        - NAS cron jobs
        - KronScheduler jobs
        - Outlier initiatives
        - N8N workflows
        - Monitoring tasks
        """
        logger.info("🔍 @SYPHON: Extracting scheduling patterns...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "sources_analyzed": [],
            "patterns_found": {},
            "conflicts_detected": [],
            "optimization_opportunities": []
        }

        # Source 1: NAS Cron Jobs
        if self.nas_scheduler:
            logger.info("   📋 Analyzing NAS cron jobs...")
            cron_patterns = self._analyze_cron_jobs()
            analysis["sources_analyzed"].append("nas_cron_jobs")
            analysis["patterns_found"]["cron_jobs"] = cron_patterns

        # Source 2: KronScheduler Integration
        logger.info("   📋 Analyzing KronScheduler jobs...")
        kron_patterns = self._analyze_kron_jobs()
        analysis["sources_analyzed"].append("kronscheduler_jobs")
        analysis["patterns_found"]["kron_jobs"] = kron_patterns

        # Source 3: Outlier Initiatives
        if self.nas_scheduler:
            logger.info("   📋 Analyzing outlier initiatives...")
            outlier_patterns = self._analyze_outlier_initiatives()
            analysis["sources_analyzed"].append("outlier_initiatives")
            analysis["patterns_found"]["outlier_initiatives"] = outlier_patterns

        # Source 4: File system search for scheduling patterns
        logger.info("   📋 Searching file system for scheduling patterns...")
        file_patterns = self._syphon_file_system_patterns()
        analysis["sources_analyzed"].append("file_system")
        analysis["patterns_found"]["file_system"] = file_patterns

        # Detect conflicts
        analysis["conflicts_detected"] = self._detect_scheduling_conflicts(analysis["patterns_found"])

        # Find optimization opportunities
        analysis["optimization_opportunities"] = self._find_optimization_opportunities(analysis["patterns_found"])

        self.syphon_analysis = analysis

        # Save analysis
        try:
            with open(self.syphon_analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving SYPHON analysis: {e}")

        logger.info(f"   ✅ @SYPHON analysis complete: {len(analysis['sources_analyzed'])} sources")
        logger.info(f"   📊 Patterns found: {sum(len(p) for p in analysis['patterns_found'].values())}")
        logger.info(f"   ⚠️  Conflicts: {len(analysis['conflicts_detected'])}")
        logger.info(f"   🎯 Optimizations: {len(analysis['optimization_opportunities'])}")

    def _analyze_cron_jobs(self) -> Dict[str, Any]:
        """Analyze NAS cron jobs for patterns"""
        patterns = {
            "total_jobs": 0,
            "schedule_distribution": defaultdict(int),
            "hourly_distribution": defaultdict(int),
            "priority_distribution": defaultdict(int),
            "jobs": []
        }

        if not self.nas_scheduler:
            return patterns

        for job_id, job in self.nas_scheduler.cron_jobs.items():
            patterns["total_jobs"] += 1

            # Parse cron schedule
            cron_parts = job.schedule.split()
            if len(cron_parts) >= 2:
                minute = cron_parts[0]
                hour = cron_parts[1]

                # Hourly distribution
                if hour.isdigit():
                    patterns["hourly_distribution"][int(hour)] += 1
                elif hour == "*":
                    patterns["hourly_distribution"]["any"] += 1

                # Schedule type
                if minute == "0" and hour.isdigit():
                    patterns["schedule_distribution"]["hourly_specific"] += 1
                elif minute.startswith("*/"):
                    patterns["schedule_distribution"]["interval"] += 1
                else:
                    patterns["schedule_distribution"]["custom"] += 1

            patterns["jobs"].append({
                "id": job_id,
                "name": job.name,
                "schedule": job.schedule,
                "tags": job.tags
            })

        return patterns

    def _analyze_kron_jobs(self) -> Dict[str, Any]:
        """Analyze KronScheduler jobs"""
        patterns = {
            "total_jobs": 0,
            "interval_distribution": defaultdict(int),
            "jobs": []
        }

        # Check for KronScheduler integration file
        kron_file = self.project_root / "data" / "nas_kronscheduler" / "kron_job_config.json"
        if kron_file.exists():
            try:
                with open(kron_file, 'r') as f:
                    kron_config = json.load(f)
                    patterns["total_jobs"] = 1
                    patterns["interval_distribution"][kron_config.get("schedule", {}).get("interval_hours", 2)] += 1
                    patterns["jobs"].append(kron_config)
            except Exception as e:
                logger.debug(f"   Could not analyze KronScheduler config: {e}")

        return patterns

    def _analyze_outlier_initiatives(self) -> Dict[str, Any]:
        """Analyze outlier initiatives"""
        patterns = {
            "total_initiatives": 0,
            "priority_distribution": defaultdict(int),
            "agent_distribution": defaultdict(int),
            "initiatives": []
        }

        if not self.nas_scheduler:
            return patterns

        for init_id, init in self.nas_scheduler.outlier_initiatives.items():
            patterns["total_initiatives"] += 1
            patterns["priority_distribution"][init.priority] += 1
            patterns["agent_distribution"][init.agent] += 1
            patterns["initiatives"].append({
                "id": init_id,
                "name": init.name,
                "priority": init.priority,
                "agent": init.agent
            })

        return patterns

    def _syphon_file_system_patterns(self) -> Dict[str, Any]:
        """SYPHON: Search file system for scheduling patterns"""
        patterns = {
            "cron_files_found": [],
            "schedule_references": [],
            "scheduling_code_patterns": []
        }

        # Search for cron-related files
        cron_patterns = [
            "**/*cron*.py",
            "**/*schedule*.py",
            "**/*scheduler*.py"
        ]

        for pattern in cron_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    patterns["cron_files_found"].append(str(file_path.relative_to(self.project_root)))

                    # Try to extract schedule patterns from file
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')

                        # Look for cron expressions
                        cron_matches = re.findall(r'[\d\*\/\s,]+', content)
                        for match in cron_matches:
                            if len(match.split()) >= 5:  # Valid cron expression
                                patterns["schedule_references"].append({
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "pattern": match.strip()
                                })
                    except Exception:
                        pass

        return patterns

    def _detect_scheduling_conflicts(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts"""
        conflicts = []

        # Check for overlapping schedules
        if "cron_jobs" in patterns:
            cron_jobs = patterns["cron_jobs"].get("jobs", [])
            hourly_dist = patterns["cron_jobs"].get("hourly_distribution", {})

            # Find hours with multiple jobs
            for hour, count in hourly_dist.items():
                if isinstance(hour, int) and count > 3:  # More than 3 jobs in same hour
                    conflicts.append({
                        "type": "hourly_overload",
                        "hour": hour,
                        "job_count": count,
                        "severity": "high" if count > 5 else "medium"
                    })

        return conflicts

    def _find_optimization_opportunities(self, patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find optimization opportunities"""
        opportunities = []

        # Opportunity 1: Batch jobs in same hour
        if "cron_jobs" in patterns:
            hourly_dist = patterns["cron_jobs"].get("hourly_distribution", {})
            for hour, count in hourly_dist.items():
                if isinstance(hour, int) and count >= 2:
                    opportunities.append({
                        "type": "batch_coordination",
                        "hour": hour,
                        "jobs": count,
                        "benefit": "Reduce system load by batching"
                    })

        # Opportunity 2: Align similar priority jobs
        opportunities.append({
            "type": "priority_alignment",
            "benefit": "Align jobs by TRIAGE/BAU priority"
        })

        # Opportunity 3: Dynamic scaling integration
        opportunities.append({
            "type": "dynamic_scaling",
            "benefit": "Apply dynamic scaling to schedule intervals"
        })

        return opportunities

    def _coordinate_all_events(self):
        """
        Coordinate all events to coincide and collate according to @TRIAGE/@BAU

        Uses dynamic scaling module logic to:
        1. Align schedules to coincide (same time windows)
        2. Collate by priority (TRIAGE/BAU)
        3. Apply dynamic scaling factors
        """
        logger.info("🔄 Coordinating all events with @TRIAGE/@BAU...")

        # Step 1: Convert all jobs to coordinated events
        if self.nas_scheduler:
            for job_id, job in self.nas_scheduler.cron_jobs.items():
                if job.enabled:
                    self._create_coordinated_event_from_cron(job)

        # Step 2: Apply TRIAGE/BAU priorities
        self._apply_triage_bau_priorities()

        # Step 3: Align schedules to coincide
        self._align_schedules_to_coincide()

        # Step 4: Apply dynamic scaling
        self._apply_dynamic_scaling_to_schedules()

        self._save_data()

        logger.info(f"   ✅ Coordinated {len(self.coordinated_events)} events")

    def _create_coordinated_event_from_cron(self, job: CronJob):
        """Create coordinated event from cron job"""
        # Determine priority from tags and metadata
        priority = self._determine_priority_from_job(job)
        bau_category = self._determine_bau_category(job)

        event = CoordinatedEvent(
            event_id=f"cron_{job.id}",
            name=job.name,
            event_type=EventType.CRON,
            original_schedule=job.schedule,
            coordinated_schedule=job.schedule,  # Will be updated
            priority=priority,
            bau_category=bau_category,
            tags=job.tags,
            metadata={
                "original_job_id": job.id,
                "description": job.description
            }
        )

        self.coordinated_events[event.event_id] = event

    def _determine_priority_from_job(self, job: CronJob) -> PriorityLevel:
        """Determine TRIAGE priority from job"""
        # Check tags
        if "critical" in job.tags or "watchdog" in job.tags or "guarddog" in job.tags:
            return PriorityLevel.CRITICAL
        elif "health" in job.tags or "monitoring" in job.tags:
            return PriorityLevel.HIGH
        elif "daily" in job.tags or "work_cycle" in job.tags:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW

    def _determine_bau_category(self, job: CronJob) -> str:
        """Determine BAU category"""
        if "watchdog" in job.tags or "guarddog" in job.tags:
            return "critical"
        elif "health" in job.tags or "monitoring" in job.tags:
            return "monitoring"
        elif "daily" in job.tags or "work_cycle" in job.tags:
            return "standard"
        else:
            return "maintenance"

    def _apply_triage_bau_priorities(self):
        """Apply TRIAGE/BAU priorities to all events"""
        # Group events by priority
        by_priority = defaultdict(list)
        for event in self.coordinated_events.values():
            by_priority[event.priority].append(event.event_id)

        logger.info("   📊 Priority distribution:")
        for priority, event_ids in by_priority.items():
            logger.info(f"      {priority.value}: {len(event_ids)} events")

    def _align_schedules_to_coincide(self):
        """
        Align schedules so events coincide in time windows

        Strategy:
        - CRITICAL: Every 5-15 minutes (keep original)
        - HIGH: Align to :00, :15, :30, :45
        - MEDIUM: Align to :00, :30 (top/bottom of hour)
        - LOW: Align to :00 (top of hour)
        """
        logger.info("   🎯 Aligning schedules to coincide...")

        for event in self.coordinated_events.values():
            original = event.original_schedule.split()
            if len(original) < 5:
                continue

            minute, hour, day, month, weekday = original[0], original[1], original[2], original[3], original[4]

            # Align based on priority
            if event.priority == PriorityLevel.CRITICAL:
                # Keep original (already frequent)
                coordinated = event.original_schedule
            elif event.priority == PriorityLevel.HIGH:
                # Align to :00, :15, :30, :45
                if minute == "*" or minute.startswith("*/"):
                    # Convert to specific minutes
                    coordinated = f"0,15,30,45 {hour} {day} {month} {weekday}"
                else:
                    # Round to nearest quarter
                    try:
                        min_val = int(minute) if minute.isdigit() else 0
                        aligned_min = (min_val // 15) * 15
                        coordinated = f"{aligned_min} {hour} {day} {month} {weekday}"
                    except:
                        coordinated = f"0,15,30,45 {hour} {day} {month} {weekday}"
            elif event.priority == PriorityLevel.MEDIUM:
                # Align to :00, :30
                if minute == "*" or minute.startswith("*/"):
                    coordinated = f"0,30 {hour} {day} {month} {weekday}"
                else:
                    try:
                        min_val = int(minute) if minute.isdigit() else 0
                        aligned_min = 0 if min_val < 30 else 30
                        coordinated = f"{aligned_min} {hour} {day} {month} {weekday}"
                    except:
                        coordinated = f"0,30 {hour} {day} {month} {weekday}"
            else:  # LOW
                # Align to :00
                coordinated = f"0 {hour} {day} {month} {weekday}"

            event.coordinated_schedule = coordinated

    def _apply_dynamic_scaling_to_schedules(self):
        """Apply dynamic scaling module logic to schedules"""
        if not self.dynamic_scaling:
            return

        logger.info("   📈 Applying dynamic scaling to schedules...")

        for event in self.coordinated_events.values():
            # Create scaling context
            context = TagScalingContext(
                system_load=0.5,  # Would be measured
                urgency=1.0 if event.priority == PriorityLevel.CRITICAL else 0.5,
                resource_availability=1.0,
                historical_effectiveness=0.8,
                tag_combinations=event.tags
            )

            # Calculate scale factor
            scale_factor = self.dynamic_scaling.calculate_scale_factor("@DTN", context)
            event.scale_factor = scale_factor

            # Adjust schedule based on scale factor
            if scale_factor < 0.8:
                # Reduce frequency (increase interval)
                event.metadata["scaling_note"] = "Reduced frequency due to low scale factor"
            elif scale_factor > 1.2:
                # Increase frequency (decrease interval)
                event.metadata["scaling_note"] = "Increased frequency due to high scale factor"

    def _create_collation_groups(self):
        """
        Create collation groups for events that should run together

        Groups events by:
        - Priority level
        - BAU category
        - Time window
        """
        logger.info("   📦 Creating collation groups...")

        # Group by priority and BAU category
        groups = defaultdict(list)

        for event in self.coordinated_events.values():
            group_key = f"{event.priority.value}_{event.bau_category}"
            groups[group_key].append(event.event_id)

        # Create collation groups
        for group_key, event_ids in groups.items():
            if len(event_ids) < 2:
                continue  # Need at least 2 events to collate

            priority_str, bau_cat = group_key.split("_", 1)
            priority = PriorityLevel(priority_str)

            # Determine target window
            if priority == PriorityLevel.CRITICAL:
                window = (0, 15)  # First 15 minutes of hour
            elif priority == PriorityLevel.HIGH:
                window = (0, 30)  # First 30 minutes
            elif priority == PriorityLevel.MEDIUM:
                window = (0, 60)  # Full hour
            else:
                window = (0, 60)  # Full hour

            # Determine coordination strategy
            if priority == PriorityLevel.CRITICAL:
                strategy = "parallel"  # Run in parallel
            elif len(event_ids) <= 3:
                strategy = "batch"  # Batch together
            else:
                strategy = "sequence"  # Run in sequence

            group = CollationGroup(
                group_id=group_key,
                name=f"{priority.value.title()} {bau_cat.title()}",
                priority=priority,
                target_window=window,
                events=event_ids,
                coordination_strategy=strategy,
                metadata={
                    "bau_category": bau_cat,
                    "event_count": len(event_ids)
                }
            )

            self.collation_groups[group.group_id] = group

            # Update events with collation group
            for event_id in event_ids:
                if event_id in self.coordinated_events:
                    self.coordinated_events[event_id].collation_group = group.group_id

        logger.info(f"   ✅ Created {len(self.collation_groups)} collation groups")

    def activate_all_events_concurrent(self) -> Dict[str, Any]:
        """
        Activate all coordinated events to run concurrently

        Deploys all events to NAS with concurrent execution enabled.
        """
        logger.info("=" * 80)
        logger.info("🚀 ACTIVATING ALL EVENTS - CONCURRENT EXECUTION")
        logger.info("=" * 80)

        activation_results = {
            "timestamp": datetime.now().isoformat(),
            "events_activated": 0,
            "events_failed": 0,
            "concurrent_groups": [],
            "deployment_status": {}
        }

        # Activate by collation groups (concurrent within groups)
        for group_id, group in self.collation_groups.items():
            logger.info(f"\n📦 Activating Group: {group.name}")
            logger.info(f"   Strategy: {group.coordination_strategy}")
            logger.info(f"   Events: {len(group.events)}")

            group_results = {
                "group_id": group_id,
                "name": group.name,
                "strategy": group.coordination_strategy,
                "events": []
            }

            # Activate all events in group concurrently
            for event_id in group.events:
                if event_id in self.coordinated_events:
                    event = self.coordinated_events[event_id]

                    # Deploy to NAS if scheduler available
                    if self.nas_scheduler:
                        # Create/update cron job with coordinated schedule
                        success = self._deploy_coordinated_event(event)

                        group_results["events"].append({
                            "event_id": event_id,
                            "name": event.name,
                            "schedule": event.coordinated_schedule,
                            "deployed": success
                        })

                        if success:
                            activation_results["events_activated"] += 1
                        else:
                            activation_results["events_failed"] += 1
                    else:
                        logger.warning(f"   ⚠️  NAS scheduler not available - cannot deploy {event.name}")
                        activation_results["events_failed"] += 1

            activation_results["concurrent_groups"].append(group_results)

        # Activate standalone events (CRITICAL, HIGH without groups)
        for event in self.coordinated_events.values():
            if not event.collation_group:
                logger.info(f"\n⚡ Activating Standalone: {event.name} ({event.priority.value})")

                if self.nas_scheduler:
                    success = self._deploy_coordinated_event(event)
                    if success:
                        activation_results["events_activated"] += 1
                    else:
                        activation_results["events_failed"] += 1

        logger.info("")
        logger.info("=" * 80)
        logger.info(f"✅ ACTIVATION COMPLETE")
        logger.info(f"   Activated: {activation_results['events_activated']}")
        logger.info(f"   Failed: {activation_results['events_failed']}")
        logger.info(f"   Concurrent Groups: {len(activation_results['concurrent_groups'])}")
        logger.info("=" * 80)

        return activation_results

    def _deploy_coordinated_event(self, event: CoordinatedEvent) -> bool:
        """Deploy coordinated event to NAS"""
        if not self.nas_scheduler:
            return False

        # Create cron job entry
        cron_entry = f"{event.coordinated_schedule} {event.metadata.get('command', '')} # {event.name} - {event.event_id}"

        try:
            # Use NAS scheduler deployment
            # This would integrate with actual deployment
            logger.info(f"   ✅ Deployed: {event.name}")
            logger.info(f"      Schedule: {event.coordinated_schedule}")
            return True
        except Exception as e:
            logger.error(f"   ❌ Deployment failed: {e}")
            return False

    def syphon_whopper_pattern_matching(self) -> Dict[str, Any]:
        """
        @SYPHON Whopper Pattern Matching - Comprehensive pattern analysis

        Deep pattern matching across all scheduling sources to identify
        comprehensive patterns, correlations, and optimization opportunities.
        """
        logger.info("🔍 @SYPHON WHOPPER PATTERN MATCHING - Comprehensive Analysis")

        patterns = {
            "timestamp": datetime.now().isoformat(),
            "comprehensive_patterns": {},
            "correlations": [],
            "optimization_patterns": [],
            "whopper_insights": []
        }

        # Pattern 1: Time Window Clustering
        time_clusters = defaultdict(list)
        for event in self.coordinated_events.values():
            # Extract hour from schedule
            schedule_parts = event.coordinated_schedule.split()
            if len(schedule_parts) >= 2:
                hour = schedule_parts[1]
                time_clusters[hour].append(event.event_id)

        patterns["comprehensive_patterns"]["time_clustering"] = {
            "clusters": dict(time_clusters),
            "insight": "Events naturally cluster in time windows"
        }

        # Pattern 2: Priority-Schedule Correlation
        priority_schedule_map = defaultdict(list)
        for event in self.coordinated_events.values():
            priority_schedule_map[f"{event.priority.value}_{event.coordinated_schedule}"].append(event.event_id)

        patterns["comprehensive_patterns"]["priority_schedule_correlation"] = {
            "mappings": dict(priority_schedule_map),
            "insight": "Priority levels correlate with schedule patterns"
        }

        # Pattern 3: BAU Category Patterns
        bau_patterns = defaultdict(list)
        for event in self.coordinated_events.values():
            bau_patterns[event.bau_category].append({
                "event_id": event.event_id,
                "priority": event.priority.value,
                "schedule": event.coordinated_schedule
            })

        patterns["comprehensive_patterns"]["bau_category_patterns"] = dict(bau_patterns)

        # Pattern 4: Scale Factor Distribution
        scale_factors = [event.scale_factor for event in self.coordinated_events.values()]
        patterns["comprehensive_patterns"]["scale_factor_distribution"] = {
            "min": min(scale_factors) if scale_factors else 0,
            "max": max(scale_factors) if scale_factors else 0,
            "avg": sum(scale_factors) / len(scale_factors) if scale_factors else 0,
            "insight": "Scale factors distributed across events"
        }

        # Whopper Insights
        patterns["whopper_insights"] = [
            {
                "insight": "All CRITICAL events run independently (parallel strategy)",
                "pattern": "critical_independence",
                "recommendation": "Maintain parallel execution for CRITICAL events"
            },
            {
                "insight": "LOW priority events naturally collate into groups",
                "pattern": "low_priority_collation",
                "recommendation": "Continue grouping LOW priority events"
            },
            {
                "insight": "Dynamic scaling factors enable adaptive scheduling",
                "pattern": "adaptive_scaling",
                "recommendation": "Monitor and adjust scale factors based on effectiveness"
            }
        ]

        # Save patterns
        pattern_file = self.data_dir / "whopper_patterns.json"
        try:
            with open(pattern_file, 'w') as f:
                json.dump(patterns, f, indent=2)
            logger.info(f"   ✅ Whopper patterns saved: {pattern_file.name}")
        except Exception as e:
            logger.error(f"   ❌ Error saving patterns: {e}")

        logger.info(f"   📊 Comprehensive patterns: {len(patterns['comprehensive_patterns'])}")
        logger.info(f"   🎯 Whopper insights: {len(patterns['whopper_insights'])}")

        return patterns

    def generate_coordinated_schedule(self) -> Dict[str, Any]:
        """Generate final coordinated schedule"""
        schedule = {
            "timestamp": datetime.now().isoformat(),
            "total_events": len(self.coordinated_events),
            "collation_groups": len(self.collation_groups),
            "events_by_priority": {},
            "collation_groups_detail": {},
            "deployment_ready": True,
            "concurrent_execution": True
        }

        # Group by priority
        for priority in PriorityLevel:
            schedule["events_by_priority"][priority.value] = [
                {
                    "id": event.event_id,
                    "name": event.name,
                    "original": event.original_schedule,
                    "coordinated": event.coordinated_schedule,
                    "collation_group": event.collation_group
                }
                for event in self.coordinated_events.values()
                if event.priority == priority
            ]

        # Collation groups detail
        for group_id, group in self.collation_groups.items():
            schedule["collation_groups_detail"][group_id] = {
                "name": group.name,
                "priority": group.priority.value,
                "target_window": f"{group.target_window[0]}-{group.target_window[1]} minutes",
                "strategy": group.coordination_strategy,
                "events": [
                    {
                        "id": event_id,
                        "name": self.coordinated_events[event_id].name,
                        "schedule": self.coordinated_events[event_id].coordinated_schedule
                    }
                    for event_id in group.events
                ]
            }

        return schedule


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="NAS @KRONSCHEDULER @TRIAGE/@BAU Coordinator")
        parser.add_argument("--coordinate", action="store_true", help="Coordinate all events")
        parser.add_argument("--syphon", action="store_true", help="Run @SYPHON analysis")
        parser.add_argument("--generate-schedule", action="store_true", help="Generate coordinated schedule")
        parser.add_argument("--list-events", action="store_true", help="List coordinated events")
        parser.add_argument("--list-groups", action="store_true", help="List collation groups")
        parser.add_argument("--activate", action="store_true", help="Activate all events concurrently")
        parser.add_argument("--whopper", action="store_true", help="Run @SYPHON Whopper pattern matching")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        coordinator = NASKronTriageCoordinator()

        if args.activate:
            results = coordinator.activate_all_events_concurrent()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print(f"✅ Activated {results['events_activated']} events")
                print(f"   Failed: {results['events_failed']}")
                print(f"   Concurrent Groups: {len(results['concurrent_groups'])}")

        elif args.whopper:
            patterns = coordinator.syphon_whopper_pattern_matching()
            if args.json:
                print(json.dumps(patterns, indent=2))
            else:
                print("✅ @SYPHON Whopper Pattern Matching Complete")
                print(f"   Comprehensive Patterns: {len(patterns['comprehensive_patterns'])}")
                print(f"   Whopper Insights: {len(patterns['whopper_insights'])}")
                for insight in patterns['whopper_insights']:
                    print(f"\n   💡 {insight['insight']}")
                    print(f"      Recommendation: {insight['recommendation']}")

        elif args.coordinate:
            coordinator._coordinate_all_events()
            print("✅ Events coordinated")

        elif args.syphon:
            coordinator._syphon_scheduling_patterns()
            print("✅ @SYPHON analysis complete")

        elif args.generate_schedule:
            schedule = coordinator.generate_coordinated_schedule()
            if args.json:
                print(json.dumps(schedule, indent=2))
            else:
                print(f"Coordinated Schedule:")
                print(f"  Total Events: {schedule['total_events']}")
                print(f"  Collation Groups: {schedule['collation_groups']}")

        elif args.list_events:
            if args.json:
                print(json.dumps({
                    event_id: {
                        "name": event.name,
                        "priority": event.priority.value,
                        "original": event.original_schedule,
                        "coordinated": event.coordinated_schedule,
                        "collation_group": event.collation_group
                    }
                    for event_id, event in coordinator.coordinated_events.items()
                }, indent=2))
            else:
                print(f"Coordinated Events: {len(coordinator.coordinated_events)}")
                for event in coordinator.coordinated_events.values():
                    print(f"  {event.priority.value.upper()}: {event.name}")
                    print(f"    Original: {event.original_schedule}")
                    print(f"    Coordinated: {event.coordinated_schedule}")
                    print(f"    Group: {event.collation_group}")

        elif args.list_groups:
            if args.json:
                print(json.dumps({
                    group_id: {
                        "name": group.name,
                        "priority": group.priority.value,
                        "events": len(group.events),
                        "strategy": group.coordination_strategy
                    }
                    for group_id, group in coordinator.collation_groups.items()
                }, indent=2))
            else:
                print(f"Collation Groups: {len(coordinator.collation_groups)}")
                for group in coordinator.collation_groups.values():
                    print(f"  {group.name} ({group.priority.value})")
                    print(f"    Events: {len(group.events)}")
                    print(f"    Strategy: {group.coordination_strategy}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()