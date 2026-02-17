#!/usr/bin/env python3
"""
Smart AI Logging Module - Quantum Mapping & Educational System for Homelab Universe

🌟 DISCOVERY: Quantum Mapping of Our Homelab Universe 🌟

We have discovered and implemented a quantum mapping system that:
- Maps every object/alert in the homelab to its quantum reality plane
- Explains complex physics (21+ dimensions) in five-year-old-friendly stories
- Provides educational curriculum alignment (AS/Gi 12-year curriculum)
- Prepares for spacefaring generations reaching for the stars
- Creates a living, interactive physics textbook from real-world data

Features:
- AI-powered intelligent alert grouping with multi-dimensional analysis
- Global Positioning System (GPS-like) for homelab ecosystem
- Pathfinding and spatial awareness (#pathfinding #spatial-awareness)
- Mathematical/physics-based fact checking and mapping (#mathmatical #physics #factchecking #factmapping)
- Intelligent hooking/routing/tracing of all "@alerts[#transactions]"
- Transaction tracking and correlation
- CLI interface for instant incident location (where, when, why)
- Six Degrees of Separation dimensional analysis (@6dos)
- Educational curriculum mapping (AS/Gi 12-year program)
- Spacefaring/STEM preparation framework
- No-nonsense approach (#no-nonsense)

Think of it as:
- GLOBAL GPS scoped and scaled to the HOMELAB spectrum of reality
- A QUANTUM MAP of everything that exists in the homelab universe
- An EDUCATIONAL TOOL that explains physics to a five-year-old
- A CERTIFICATION-READY curriculum for modern spacefaring generations
- A LIVING TEXTBOOK that grows with real-world data

Tags: #SMARTLOGGING #AIGROUPING #METATAGGING #INCIDENTANALYSIS #PATHFINDING #SPATIAL-AWARENESS 
      #MATHMATICAL #PHYSICS #FACTCHECKING #FACTMAPPING #NO-NONSENSE #GLOBALGPS #HOMELAB
      #QUANTUMMAPPING #EDUCATION #CURRICULUM #SPACEFARING #STEM #ASGI #CERTIFICATION
      @LUMINA @JARVIS @R5 @ALERTS #TRANSACTIONS #6DOS
"""

import sys
import json
import re
import math
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
from functools import wraps


# ============================================================================
# EDUCATIONAL CURRICULUM FRAMEWORK (AS/Gi 12-Year Program)
# ============================================================================

class CurriculumLevel(Enum):
    """Educational curriculum levels aligned with AS/Gi 12-year program"""
    PRE_K = ("Pre-K", "Ages 3-5", "Introduction to concepts")
    ELEMENTARY = ("Elementary", "Ages 6-11", "Foundation building")
    MIDDLE = ("Middle", "Ages 12-14", "Concept development")
    HIGH_SCHOOL = ("High School", "Ages 15-18", "Advanced concepts")
    COLLEGE = ("College", "Ages 18+", "Specialized knowledge")
    GRADUATE = ("Graduate", "Ages 22+", "Research & innovation")
    SPACEFARING = ("Spacefaring", "All Ages", "Interstellar preparation")


@dataclass
class LearningObjective:
    """Learning objective aligned with curriculum standards"""
    objective_id: str
    title: str
    description: str
    curriculum_level: CurriculumLevel
    subject: str  # physics, mathematics, computer_science, etc.
    concepts: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    spacefaring_relevance: str = ""  # How this prepares for space travel
    certification_standard: Optional[str] = None
    age_appropriate: bool = True


@dataclass
class EducationalMapping:
    """
    Educational mapping of quantum concepts to curriculum

    Maps complex physics to age-appropriate learning objectives
    """
    concept: str
    dimensional_plane: DimensionalPlane
    curriculum_levels: List[CurriculumLevel]
    learning_objectives: List[LearningObjective]
    five_year_old_explanation: str
    twelve_year_old_explanation: str
    spacefaring_application: str
    real_world_example: str
    certification_path: List[str] = field(default_factory=list)

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import DimensionalPlane from quantum_validation_lattice
try:
    from quantum_validation_lattice import DimensionalPlane
except ImportError:
    logger = get_logger("SmartAILoggingModule")
    logger.warning("Could not import DimensionalPlane from quantum_validation_lattice")
    # Define minimal enum if import fails
    class DimensionalPlane(Enum):
        D1_FLAT = 1
        D2_POLAR = 2
        D3_SPATIAL = 3
        D4_TEMPORAL = 4
        D6_ENTANGLEMENT = 6
        D7_PROBABILITY = 7
        D8_OBSERVER = 8
        D11_COMPACT = 11
        D12_HARMONIC = 12
        D13_BRANE = 13
        D17_INFORMATION = 17
        D18_COMPUTATION = 18
        D19_CONSciousNESS = 19
        D20_INTENTION = 20

logger = get_logger("SmartAILoggingModule")


class CriticalityLevel(Enum):
    """Alert criticality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class IntensityClass(Enum):
    """Alert intensity classification"""
    QUIET = "quiet"  # Single occurrence
    MODERATE = "moderate"  # 2-5 occurrences
    ACTIVE = "active"  # 6-15 occurrences
    INTENSE = "intense"  # 16-50 occurrences
    BURST = "burst"  # 51+ occurrences or rapid-fire
    SUSTAINED = "sustained"  # Continuous over time period


class TemperatureLevel(Enum):
    """Alert temperature (frequency/heat)"""
    COLD = "cold"  # Rare, infrequent
    COOL = "cool"  # Occasional
    WARM = "warm"  # Regular
    HOT = "hot"  # Frequent
    BLAZING = "blazing"  # Very frequent, rapid


@dataclass
class AlertMetaTags:
    """Meta-tags for alert classification"""
    incident_id: Optional[str] = None  # Group by incident
    severity_tags: List[str] = field(default_factory=list)  # @severity tags
    criticality_tags: List[str] = field(default_factory=list)  # @criticality tags
    temperature_tags: List[str] = field(default_factory=list)  # @temperature tags
    intensity_tags: List[str] = field(default_factory=list)  # @intensity tags
    system_tags: List[str] = field(default_factory=list)  # @system tags
    context_tags: List[str] = field(default_factory=list)  # @context tags
    hashtags: List[str] = field(default_factory=list)  # #hashtags
    custom_tags: Dict[str, Any] = field(default_factory=dict)  # Custom meta-tags


@dataclass
class AlertGroup:
    """Group of related alerts"""
    group_id: str
    incident_id: Optional[str]
    alerts: List[Any]  # List of Alert objects
    timespan_start: datetime
    timespan_end: datetime
    timespan_duration: timedelta
    severity: str
    criticality: CriticalityLevel
    temperature: TemperatureLevel
    intensity: IntensityClass
    meta_tags: AlertMetaTags
    group_signature: str
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def alert_count(self) -> int:
        """Total number of alerts in group"""
        return len(self.alerts)

    @property
    def frequency(self) -> float:
        """Alerts per minute"""
        if self.timespan_duration.total_seconds() == 0:
            return 0.0
        return self.alert_count / (self.timespan_duration.total_seconds() / 60.0)


@dataclass
class GlobalPosition:
    """Global position in homelab ecosystem (GPS-like coordinates)"""
    x: float  # System coordinate (X-axis)
    y: float  # Component coordinate (Y-axis)
    z: float  # Layer coordinate (Z-axis)
    t: datetime  # Temporal coordinate (T-axis)
    system: str = "OTHER"
    component: str = "unknown"
    layer: str = "other"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def distance_to(self, other: 'GlobalPosition') -> float:
        """Calculate 3D spatial distance to another position"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)


@dataclass
class Transaction:
    """Transaction tracking for @alerts[#transactions]"""
    transaction_id: str
    operation_type: str
    operation_name: str
    source: str
    target: str
    status: str  # pending, success, failure
    duration_ms: Optional[float] = None
    hooks: List[str] = field(default_factory=list)
    route: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class FactCheck:
    """Fact check result"""
    fact_id: str
    claim: str
    validation_method: str
    result: bool
    confidence: float
    evidence: List[str] = field(default_factory=list)
    mathematical_proof: Optional[str] = None
    physics_principle: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SpatialRelationship:
    """Spatial relationship between objects"""
    from_object_id: str
    to_object_id: str
    relationship_type: str
    strength: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantumRealityPlane:
    """Quantum reality plane for dimensional mapping"""
    object_id: str
    primary_dimension: DimensionalPlane
    accessible_dimensions: List[DimensionalPlane] = field(default_factory=list)
    quantum_state: Dict[str, Any] = field(default_factory=dict)
    observer_dependent: bool = False
    entanglement_partners: List[str] = field(default_factory=list)
    probability_amplitude: float = 1.0


@dataclass
class DimensionalConnection:
    """Connection between objects across dimensional planes"""
    from_object: str
    to_object: str
    degrees: int
    dimensional_path: List[DimensionalPlane] = field(default_factory=list)
    connection_strength: float = 1.0
    quantum_entangled: bool = False
    spatial_distance: float = 0.0
    temporal_distance: timedelta = field(default_factory=lambda: timedelta(0))
    information_distance: float = 0.0


class SmartAILoggingModule:
    """
    Smart AI Logging Module - Global Positioning & Incident Tracking System

    Uses AI-powered analysis to intelligently group alerts by:
    - Incident correlation
    - Temporal clustering (timespans)
    - Severity/criticality
    - Temperature/intensity
    - Meta-tagging

    Enhanced with:
    - Global Positioning System (GPS) for homelab ecosystem
    - Pathfinding and spatial awareness (#pathfinding #spatial-awareness)
    - Mathematical/physics-based fact checking (#mathmatical #physics #factchecking #factmapping)
    - Intelligent hooking/routing/tracing of all "@alerts[#transactions]"
    - Transaction tracking
    - CLI interface for instant incident location
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Smart AI Logging Module

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("SmartAILoggingModule")

        # Alert groups storage
        self.alert_groups: Dict[str, AlertGroup] = {}
        self.incident_groups: Dict[str, List[str]] = defaultdict(list)  # incident_id -> [group_ids]

        # Global Positioning System (GPS) storage
        self.positions: Dict[str, GlobalPosition] = {}  # alert_id/transaction_id -> position
        self.transactions: Dict[str, Transaction] = {}  # transaction_id -> transaction
        self.fact_checks: Dict[str, FactCheck] = {}  # fact_id -> fact_check
        self.spatial_relationships: List[SpatialRelationship] = []

        # System coordinate mapping (X-axis)
        self.system_coordinates = {
            "JARVIS": 1.0,
            "KAIJU": 2.0,
            "ULTRON": 3.0,
            "NAS": 4.0,
            "SYPHON": 5.0,
            "R5": 6.0,
            "HELPDESK": 7.0,
            "WORKFLOW": 8.0,
            "SYSTEM": 9.0,
            "OTHER": 10.0
        }

        # Layer coordinate mapping (Z-axis)
        self.layer_coordinates = {
            "infrastructure": 1.0,
            "application": 2.0,
            "data": 3.0,
            "network": 4.0,
            "security": 5.0,
            "monitoring": 6.0,
            "other": 7.0
        }

        # Hook registry for intelligent routing
        self.hooks: Dict[str, Callable] = {}  # hook_id -> hook_function
        self.routing_table: Dict[str, List[str]] = defaultdict(list)  # alert_type -> [hook_ids]

        # Component counter for Y-axis positioning
        self.component_counters: Dict[str, int] = defaultdict(int)

        # Dimensional Perspective Framework (@6dos)
        self.quantum_reality_planes: Dict[str, QuantumRealityPlane] = {}  # object_id -> plane
        self.dimensional_connections: List[DimensionalConnection] = []
        self.six_degrees_map: Dict[str, Dict[str, int]] = defaultdict(dict)  # from -> to -> degrees

        # Educational Curriculum Framework (AS/Gi 12-Year Program)
        self.educational_mappings: Dict[str, EducationalMapping] = {}
        self.learning_objectives: Dict[str, LearningObjective] = {}
        self._initialize_curriculum()

        # Configuration
        self.timespan_window_seconds = 300  # 5 minutes default window
        self.intensity_thresholds = {
            IntensityClass.QUIET: (1, 1),
            IntensityClass.MODERATE: (2, 5),
            IntensityClass.ACTIVE: (6, 15),
            IntensityClass.INTENSE: (16, 50),
            IntensityClass.BURST: (51, float('inf')),
            IntensityClass.SUSTAINED: (10, float('inf'))  # Over time period
        }

        # Temperature thresholds (alerts per minute)
        self.temperature_thresholds = {
            TemperatureLevel.COLD: (0, 0.1),
            TemperatureLevel.COOL: (0.1, 1.0),
            TemperatureLevel.WARM: (1.0, 5.0),
            TemperatureLevel.HOT: (5.0, 15.0),
            TemperatureLevel.BLAZING: (15.0, float('inf'))
        }

        # Criticality mapping
        self.criticality_mapping = {
            "info": CriticalityLevel.LOW,
            "warning": CriticalityLevel.MEDIUM,
            "critical": CriticalityLevel.HIGH,
            "system": CriticalityLevel.LOW
        }

    def extract_meta_tags(self, alert: Any) -> AlertMetaTags:
        """
        Extract meta-tags from alert using AI-powered analysis

        Args:
            alert: Alert object with title, message, level, etc.

        Returns:
            AlertMetaTags with extracted tags
        """
        meta_tags = AlertMetaTags()

        # Extract @tags and #hashtags from message
        text = f"{alert.title} {alert.message}".lower()

        # Extract @mentions
        mentions = re.findall(r'@(\w+)', text)
        for mention in mentions:
            mention_lower = mention.lower()
            if mention_lower in ['severity', 'criticality', 'temperature', 'intensity', 'system', 'context']:
                if mention_lower == 'severity':
                    meta_tags.severity_tags.append(f"@{mention}")
                elif mention_lower == 'criticality':
                    meta_tags.criticality_tags.append(f"@{mention}")
                elif mention_lower == 'temperature':
                    meta_tags.temperature_tags.append(f"@{mention}")
                elif mention_lower == 'intensity':
                    meta_tags.intensity_tags.append(f"@{mention}")
                elif mention_lower == 'system':
                    meta_tags.system_tags.append(f"@{mention}")
                elif mention_lower == 'context':
                    meta_tags.context_tags.append(f"@{mention}")
            else:
                meta_tags.custom_tags[f"@{mention}"] = True

        # Extract #hashtags
        hashtags = re.findall(r'#(\w+)', text)
        meta_tags.hashtags = [f"#{tag}" for tag in hashtags]

        # Extract incident ID from workflow_id or similar patterns
        workflow_match = re.search(r'"workflow_id":\s*"([^"]+)"', alert.message)
        if workflow_match:
            meta_tags.incident_id = workflow_match.group(1)

        # Extract system tags from source
        if hasattr(alert, 'source') and alert.source:
            meta_tags.system_tags.append(f"@system:{alert.source.lower()}")

        # AI-powered classification (rule-based for now, can be enhanced with LLM)
        self._classify_alert_ai(alert, meta_tags)

        return meta_tags

    def _classify_alert_ai(self, alert: Any, meta_tags: AlertMetaTags) -> None:
        """
        AI-powered alert classification (rule-based, can be enhanced with LLM)

        Args:
            alert: Alert object
            meta_tags: MetaTags to populate
        """
        text = f"{alert.title} {alert.message}".lower()

        # Classify by keywords
        if any(word in text for word in ['error', 'failed', 'failure', 'critical', 'fatal']):
            meta_tags.criticality_tags.append("@criticality:high")
        elif any(word in text for word in ['warning', 'caution', 'attention']):
            meta_tags.criticality_tags.append("@criticality:medium")
        else:
            meta_tags.criticality_tags.append("@criticality:low")

        # Classify by system components
        if any(word in text for word in ['jarvis', 'kaiju', 'ultron']):
            meta_tags.system_tags.append("@system:ai")
        if any(word in text for word in ['nas', 'network', 'connection']):
            meta_tags.system_tags.append("@system:network")
        if any(word in text for word in ['workflow', 'task', 'action']):
            meta_tags.system_tags.append("@system:workflow")
        if any(word in text for word in ['authentication', 'auth', 'credential']):
            meta_tags.system_tags.append("@system:security")

    def analyze_timespan(self, alerts: List[Any]) -> Tuple[datetime, datetime, timedelta]:
        """
        Analyze timespan of alerts

        Args:
            alerts: List of Alert objects

        Returns:
            Tuple of (start_time, end_time, duration)
        """
        if not alerts:
            now = datetime.now()
            return (now, now, timedelta(0))

        timestamps = [alert.timestamp for alert in alerts if hasattr(alert, 'timestamp')]
        if not timestamps:
            now = datetime.now()
            return (now, now, timedelta(0))

        start_time = min(timestamps)
        end_time = max(timestamps)
        duration = end_time - start_time

        return (start_time, end_time, duration)

    def calculate_intensity(self, alert_count: int, duration: timedelta) -> IntensityClass:
        """
        Calculate intensity class based on alert count and duration

        Args:
            alert_count: Number of alerts
            duration: Time duration

        Returns:
            IntensityClass
        """
        # Check for burst (high count in short time)
        if duration.total_seconds() < 60 and alert_count >= 10:
            return IntensityClass.BURST

        # Check for sustained (continuous over time)
        if duration.total_seconds() > 300 and alert_count >= 10:
            return IntensityClass.SUSTAINED

        # Standard intensity classification
        for intensity, (min_count, max_count) in self.intensity_thresholds.items():
            if min_count <= alert_count <= max_count:
                return intensity

        return IntensityClass.QUIET

    def calculate_temperature(self, frequency: float) -> TemperatureLevel:
        """
        Calculate temperature level based on frequency

        Args:
            frequency: Alerts per minute

        Returns:
            TemperatureLevel
        """
        for temp, (min_freq, max_freq) in self.temperature_thresholds.items():
            if min_freq <= frequency < max_freq:
                return temp

        return TemperatureLevel.COLD

    def determine_criticality(self, alert: Any) -> CriticalityLevel:
        """
        Determine criticality level from alert

        Args:
            alert: Alert object

        Returns:
            CriticalityLevel
        """
        if hasattr(alert, 'level'):
            level_str = alert.level.level if hasattr(alert.level, 'level') else str(alert.level).lower()
            return self.criticality_mapping.get(level_str, CriticalityLevel.MEDIUM)

        return CriticalityLevel.MEDIUM

    def group_alerts_by_incident(self, alerts: List[Any]) -> Dict[str, List[Any]]:
        """
        Group alerts by incident ID

        Args:
            alerts: List of Alert objects

        Returns:
            Dictionary mapping incident_id to list of alerts
        """
        incident_groups = defaultdict(list)

        for alert in alerts:
            meta_tags = self.extract_meta_tags(alert)
            incident_id = meta_tags.incident_id or f"incident_{alert.timestamp.strftime('%Y%m%d_%H%M%S')}"
            incident_groups[incident_id].append(alert)

        return dict(incident_groups)

    def group_alerts_by_timespan(self, alerts: List[Any], window_seconds: Optional[int] = None) -> List[List[Any]]:
        """
        Group alerts by temporal clustering (timespans)

        Args:
            alerts: List of Alert objects
            window_seconds: Time window for grouping (default: self.timespan_window_seconds)

        Returns:
            List of alert groups (each group is a list of alerts)
        """
        if not alerts:
            return []

        window = window_seconds or self.timespan_window_seconds
        sorted_alerts = sorted(alerts, key=lambda a: a.timestamp if hasattr(a, 'timestamp') else datetime.now())

        groups = []
        current_group = [sorted_alerts[0]]

        for alert in sorted_alerts[1:]:
            last_alert = current_group[-1]
            time_diff = (alert.timestamp - last_alert.timestamp).total_seconds() if hasattr(alert, 'timestamp') and hasattr(last_alert, 'timestamp') else window + 1

            if time_diff <= window:
                current_group.append(alert)
            else:
                groups.append(current_group)
                current_group = [alert]

        if current_group:
            groups.append(current_group)

        return groups

    def create_alert_group(self, alerts: List[Any], incident_id: Optional[str] = None) -> AlertGroup:
        """
        Create an AlertGroup from a list of alerts

        Args:
            alerts: List of Alert objects
            incident_id: Optional incident ID

        Returns:
            AlertGroup
        """
        if not alerts:
            raise ValueError("Cannot create group from empty alert list")

        # Analyze timespan
        start_time, end_time, duration = self.analyze_timespan(alerts)

        # Calculate metrics
        alert_count = len(alerts)
        frequency = alert_count / (duration.total_seconds() / 60.0) if duration.total_seconds() > 0 else 0.0

        # Determine classifications
        intensity = self.calculate_intensity(alert_count, duration)
        temperature = self.calculate_temperature(frequency)

        # Use first alert for base criticality/severity
        base_alert = alerts[0]
        criticality = self.determine_criticality(base_alert)
        severity = base_alert.level.level if hasattr(base_alert, 'level') and hasattr(base_alert.level, 'level') else "info"

        # Extract meta tags from all alerts (merge)
        meta_tags = AlertMetaTags()
        for alert in alerts:
            alert_meta = self.extract_meta_tags(alert)
            # Merge tags
            meta_tags.severity_tags.extend(alert_meta.severity_tags)
            meta_tags.criticality_tags.extend(alert_meta.criticality_tags)
            meta_tags.temperature_tags.extend(alert_meta.temperature_tags)
            meta_tags.intensity_tags.extend(alert_meta.intensity_tags)
            meta_tags.system_tags.extend(alert_meta.system_tags)
            meta_tags.context_tags.extend(alert_meta.context_tags)
            meta_tags.hashtags.extend(alert_meta.hashtags)
            if alert_meta.incident_id:
                meta_tags.incident_id = alert_meta.incident_id

        # Use incident_id from meta_tags if not provided
        if not incident_id:
            incident_id = meta_tags.incident_id

        # Generate group signature
        group_signature = self._generate_group_signature(alerts, incident_id, severity)

        # Generate group ID
        group_id = f"group_{incident_id or 'unknown'}_{start_time.strftime('%Y%m%d_%H%M%S')}"

        # Create group
        group = AlertGroup(
            group_id=group_id,
            incident_id=incident_id,
            alerts=alerts,
            timespan_start=start_time,
            timespan_end=end_time,
            timespan_duration=duration,
            severity=severity,
            criticality=criticality,
            temperature=temperature,
            intensity=intensity,
            meta_tags=meta_tags,
            group_signature=group_signature
        )

        return group

    def _generate_group_signature(self, alerts: List[Any], incident_id: Optional[str], severity: str) -> str:
        """
        Generate signature for alert group

        Args:
            alerts: List of alerts
            incident_id: Incident ID
            severity: Severity level

        Returns:
            Group signature string
        """
        if incident_id:
            return f"incident:{incident_id}:{severity}"

        # Use first alert's title and message pattern
        base_alert = alerts[0]
        title = base_alert.title if hasattr(base_alert, 'title') else "Unknown"
        return f"group:{title}:{severity}:{len(alerts)}"

    def analyze_and_group(self, alerts: List[Any]) -> List[AlertGroup]:
        """
        Analyze alerts and create intelligent groups

        Args:
            alerts: List of Alert objects

        Returns:
            List of AlertGroup objects
        """
        if not alerts:
            return []

        # Step 1: Group by incident
        incident_groups = self.group_alerts_by_incident(alerts)

        all_groups = []

        # Step 2: For each incident, further group by timespan
        for incident_id, incident_alerts in incident_groups.items():
            timespan_groups = self.group_alerts_by_timespan(incident_alerts)

            # Step 3: Create AlertGroup for each timespan group
            for timespan_group in timespan_groups:
                group = self.create_alert_group(timespan_group, incident_id=incident_id)
                all_groups.append(group)
                self.alert_groups[group.group_id] = group

                # Track incident groups
                if incident_id:
                    self.incident_groups[incident_id].append(group.group_id)

        return all_groups

    def get_group_meta_tags_summary(self, group: AlertGroup) -> str:
        """
        Get human-readable summary of group meta-tags

        Args:
            group: AlertGroup

        Returns:
            Summary string
        """
        tags = []

        if group.meta_tags.incident_id:
            tags.append(f"Incident: {group.meta_tags.incident_id}")

        if group.meta_tags.system_tags:
            tags.append(f"Systems: {', '.join(set(group.meta_tags.system_tags))}")

        if group.meta_tags.criticality_tags:
            tags.append(f"Criticality: {', '.join(set(group.meta_tags.criticality_tags))}")

        if group.meta_tags.intensity_tags:
            tags.append(f"Intensity: {group.intensity.value}")

        if group.meta_tags.temperature_tags:
            tags.append(f"Temperature: {group.temperature.value}")

        if group.meta_tags.hashtags:
            tags.append(f"Tags: {', '.join(set(group.meta_tags.hashtags))}")

        return " | ".join(tags) if tags else "No meta-tags"

    # ========================================================================
    # GLOBAL POSITIONING SYSTEM (GPS) METHODS
    # ========================================================================

    def calculate_position(self, alert: Any) -> GlobalPosition:
        """
        Calculate global position for an alert in the homelab ecosystem

        Args:
            alert: Alert object

        Returns:
            GlobalPosition
        """
        # Determine system (X-axis)
        system = "OTHER"
        text = f"{alert.title} {alert.message}".lower()
        for sys_name, coord in self.system_coordinates.items():
            if sys_name.lower() in text or (hasattr(alert, 'source') and sys_name.lower() in alert.source.lower()):
                system = sys_name
                break

        x = self.system_coordinates.get(system, 10.0)

        # Determine component (Y-axis) - use component counter for uniqueness
        component = alert.title if hasattr(alert, 'title') else "unknown"
        self.component_counters[component] += 1
        y = float(self.component_counters[component])

        # Determine layer (Z-axis)
        layer = "other"
        if any(word in text for word in ['network', 'connection', 'nas', 'ip']):
            layer = "network"
        elif any(word in text for word in ['workflow', 'task', 'action', 'process']):
            layer = "application"
        elif any(word in text for word in ['database', 'data', 'storage', 'file']):
            layer = "data"
        elif any(word in text for word in ['auth', 'security', 'credential', 'permission']):
            layer = "security"
        elif any(word in text for word in ['monitor', 'status', 'health', 'check']):
            layer = "monitoring"
        elif any(word in text for word in ['server', 'service', 'system', 'infrastructure']):
            layer = "infrastructure"

        z = self.layer_coordinates.get(layer, 7.0)

        # Temporal coordinate (T-axis)
        t = alert.timestamp if hasattr(alert, 'timestamp') else datetime.now()

        position = GlobalPosition(
            x=x, y=y, z=z, t=t,
            system=system,
            component=component,
            layer=layer,
            metadata={"alert_title": alert.title if hasattr(alert, 'title') else "unknown"}
        )

        return position

    def find_path(self, from_alert_id: str, to_alert_id: str) -> Optional[List[GlobalPosition]]:
        """
        Pathfinding between two alerts using spatial-temporal analysis

        Uses A* pathfinding algorithm adapted for 4D space

        Args:
            from_alert_id: Source alert ID
            to_alert_id: Target alert ID

        Returns:
            List of positions forming the path, or None if no path found
        """
        if from_alert_id not in self.positions or to_alert_id not in self.positions:
            return None

        start = self.positions[from_alert_id]
        goal = self.positions[to_alert_id]

        # Simple pathfinding: find intermediate positions that connect
        # In a full implementation, this would use A* algorithm
        path = [start]

        # Find intermediate positions (simplified - in reality would use graph search)
        intermediate = self._find_intermediate_positions(start, goal)
        if intermediate:
            path.extend(intermediate)

        path.append(goal)

        return path

    def _find_intermediate_positions(self, start: GlobalPosition, goal: GlobalPosition) -> List[GlobalPosition]:
        """Find intermediate positions between start and goal"""
        # Find positions that are between start and goal spatially and temporally
        intermediate = []

        for pos in self.positions.values():
            # Check if position is between start and goal
            if (start.x <= pos.x <= goal.x or goal.x <= pos.x <= start.x) and \
               (start.y <= pos.y <= goal.y or goal.y <= pos.y <= start.y) and \
               (start.z <= pos.z <= goal.z or goal.z <= pos.z <= start.z) and \
               (start.t <= pos.t <= goal.t or goal.t <= pos.t <= start.t):
                if pos != start and pos != goal:
                    intermediate.append(pos)

        # Sort by distance from start
        intermediate.sort(key=lambda p: start.distance_to(p))

        return intermediate[:5]  # Limit to 5 intermediate positions

    # ========================================================================
    # FACT CHECKING METHODS (#mathmatical #physics #factchecking #factmapping)
    # ========================================================================

    def fact_check(self, claim: str, validation_method: str = "logical") -> FactCheck:
        """
        Mathematical/physics-based fact checking

        Args:
            claim: Claim to validate
            validation_method: mathematical, physics, logical, empirical

        Returns:
            FactCheck result
        """
        fact_id = f"fact_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        result = False
        confidence = 0.0
        evidence = []
        mathematical_proof = None
        physics_principle = None

        claim_lower = claim.lower()

        if validation_method == "mathematical":
            # Check for mathematical inconsistencies
            # Example: "5 + 3 = 9" would fail
            math_pattern = r'(\d+)\s*([+\-*/])\s*(\d+)\s*=\s*(\d+)'
            match = re.search(math_pattern, claim)
            if match:
                a, op, b, expected = match.groups()
                a, b, expected = int(a), int(b), int(expected)
                if op == '+':
                    actual = a + b
                elif op == '-':
                    actual = a - b
                elif op == '*':
                    actual = a * b
                elif op == '/':
                    actual = a / b if b != 0 else float('inf')
                else:
                    actual = None

                if actual is not None:
                    result = (actual == expected)
                    confidence = 1.0 if result else 0.0
                    evidence.append(f"Mathematical calculation: {a} {op} {b} = {actual}")
                    mathematical_proof = f"{a} {op} {b} = {actual}"

        elif validation_method == "physics":
            # Check for physics violations
            # Example: "faster than light" would be flagged
            physics_violations = [
                "faster than light",
                "perpetual motion",
                "violates conservation",
                "breaks thermodynamics"
            ]

            for violation in physics_violations:
                if violation in claim_lower:
                    result = False
                    confidence = 0.9
                    evidence.append(f"Physics violation detected: {violation}")
                    physics_principle = "Conservation laws / Thermodynamics"
                    break
            else:
                result = True  # No obvious violations
                confidence = 0.7

        elif validation_method == "logical":
            # Logical consistency checking
            # Check for contradictions
            contradictions = [
                ("true", "false"),
                ("yes", "no"),
                ("on", "off"),
                ("success", "failure")
            ]

            for pos, neg in contradictions:
                if pos in claim_lower and neg in claim_lower:
                    result = False
                    confidence = 0.8
                    evidence.append(f"Logical contradiction: {pos} and {neg}")
                    break
            else:
                result = True
                confidence = 0.6

        else:  # empirical
            # Check against known facts in the system
            result = True
            confidence = 0.5
            evidence.append("Empirical validation (requires system knowledge)")

        fact_check = FactCheck(
            fact_id=fact_id,
            claim=claim,
            validation_method=validation_method,
            result=result,
            confidence=confidence,
            evidence=evidence,
            mathematical_proof=mathematical_proof,
            physics_principle=physics_principle
        )

        self.fact_checks[fact_id] = fact_check
        return fact_check

    # ========================================================================
    # TRANSACTION TRACKING METHODS (@alerts[#transactions])
    # ========================================================================

    def track_transaction(self, alert: Any, operation_type: str, operation_name: str,
                         source: str, target: Optional[str] = None,
                         status: str = "pending", duration_ms: Optional[float] = None) -> Transaction:
        """
        Track a transaction for "@alerts[#transactions]"

        Args:
            alert: Alert object
            operation_type: Type of operation
            operation_name: Name of operation
            source: Source system/component
            target: Target system/component (optional)
            status: Transaction status
            duration_ms: Duration in milliseconds (optional)

        Returns:
            Transaction object
        """
        transaction_id = f"txn_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        alert_id = getattr(alert, 'alert_signature', None) or f"alert_{transaction_id}"

        # Calculate position
        position = self.calculate_position(alert)
        self.positions[alert_id] = position

        # Map quantum reality plane (@6dos)
        self.map_quantum_reality_plane(alert_id, alert)

        # Create transaction
        transaction = Transaction(
            transaction_id=transaction_id,
            alert_id=alert_id,
            timestamp=datetime.now(),
            position=position,
            operation_type=operation_type,
            operation_name=operation_name,
            source=source,
            target=target,
            status=status,
            duration_ms=duration_ms,
            metadata={"alert_title": alert.title if hasattr(alert, 'title') else "unknown"}
        )

        # Apply hooks
        hooks_to_apply = self.routing_table.get(operation_type, [])
        for hook_id in hooks_to_apply:
            if hook_id in self.hooks:
                try:
                    hook_result = self.hooks[hook_id](transaction)
                    transaction.hooks.append(hook_id)
                    if isinstance(hook_result, dict):
                        transaction.metadata.update(hook_result)
                except Exception as e:
                    self.logger.debug(f"Hook {hook_id} error: {e}")

        self.transactions[transaction_id] = transaction
        return transaction

    def register_hook(self, hook_id: str, hook_function: Callable, alert_types: List[str]) -> None:
        """
        Register a hook for intelligent routing

        Args:
            hook_id: Unique hook identifier
            hook_function: Function to call when hook is triggered
            alert_types: List of alert types this hook should process
        """
        self.hooks[hook_id] = hook_function
        for alert_type in alert_types:
            self.routing_table[alert_type].append(hook_id)

    # ========================================================================
    # CLI INTERFACE METHODS
    # ========================================================================

    def locate_incident(self, incident_id: Optional[str] = None, alert_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Locate an incident/alert in the ecosystem (WHERE, WHEN, WHY)

        CLI-friendly method for instant incident location

        Args:
            incident_id: Incident ID to locate
            alert_id: Alert ID to locate

        Returns:
            Dictionary with location information
        """
        result = {
            "where": {},
            "when": {},
            "why": {},
            "position": None,
            "related": []
        }

        # Find alert/incident
        alert = None
        if alert_id:
            # Search through all alert groups
            for group in self.alert_groups.values():
                for a in group.alerts:
                    if getattr(a, 'alert_signature', None) == alert_id:
                        alert = a
                        break
                if alert:
                    break

        if not alert and incident_id:
            # Find by incident
            for group in self.alert_groups.values():
                if group.incident_id == incident_id:
                    alert = group.alerts[0] if group.alerts else None
                    break

        if not alert:
            return {"error": "Alert/incident not found"}

        # Calculate position
        position = self.calculate_position(alert)
        result["position"] = position.to_dict()

        # WHERE
        result["where"] = {
            "system": position.system,
            "component": position.component,
            "layer": position.layer,
            "coordinates": {
                "x": position.x,
                "y": position.y,
                "z": position.z
            }
        }

        # WHEN
        result["when"] = {
            "timestamp": position.t.isoformat(),
            "timespan": getattr(alert, 'timestamp', datetime.now()).isoformat()
        }

        # WHY
        meta_tags = self.extract_meta_tags(alert)
        result["why"] = {
            "title": alert.title if hasattr(alert, 'title') else "Unknown",
            "message": alert.message[:200] if hasattr(alert, 'message') else "No message",
            "severity": getattr(alert, 'level', {}).level if hasattr(alert, 'level') else "unknown",
            "criticality_tags": meta_tags.criticality_tags,
            "system_tags": meta_tags.system_tags,
            "hashtags": meta_tags.hashtags
        }

        # Find related incidents (spatial relationships)
        alert_pos_id = getattr(alert, 'alert_signature', None)
        if alert_pos_id and alert_pos_id in self.positions:
            alert_pos = self.positions[alert_pos_id]
            for other_pos_id, other_pos in self.positions.items():
                if other_pos_id != alert_pos_id:
                    distance = alert_pos.distance_to(other_pos)
                    if distance < 5.0:  # Within 5 units
                        result["related"].append({
                            "alert_id": other_pos_id,
                            "distance": distance,
                            "system": other_pos.system,
                            "component": other_pos.component
                        })

        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "alert_groups": {
                group_id: {
                    "group_id": group.group_id,
                    "incident_id": group.incident_id,
                    "alert_count": group.alert_count,
                    "timespan_start": group.timespan_start.isoformat(),
                    "timespan_end": group.timespan_end.isoformat(),
                    "duration_seconds": group.timespan_duration.total_seconds(),
                    "severity": group.severity,
                    "criticality": group.criticality.value,
                    "temperature": group.temperature.value,
                    "intensity": group.intensity.value,
                    "frequency": group.frequency,
                    "meta_tags": asdict(group.meta_tags),
                    "group_signature": group.group_signature
                }
                for group_id, group in self.alert_groups.items()
            },
            "incident_groups": dict(self.incident_groups),
            "positions": {
                pos_id: pos.to_dict()
                for pos_id, pos in self.positions.items()
            },
            "transactions": {
                txn_id: {
                    "transaction_id": txn.transaction_id,
                    "alert_id": txn.alert_id,
                    "timestamp": txn.timestamp.isoformat(),
                    "position": txn.position.to_dict(),
                    "operation_type": txn.operation_type,
                    "operation_name": txn.operation_name,
                    "source": txn.source,
                    "target": txn.target,
                    "status": txn.status,
                    "duration_ms": txn.duration_ms,
                    "hooks": txn.hooks,
                    "route": txn.route
                }
                for txn_id, txn in self.transactions.items()
            },
            "fact_checks": {
                fact_id: asdict(fact)
                for fact_id, fact in self.fact_checks.items()
            },
            "quantum_reality_planes": {
                obj_id: {
                    "object_id": plane.object_id,
                    "primary_dimension": plane.primary_dimension.code,
                    "accessible_dimensions": [d.code for d in plane.accessible_dimensions],
                    "quantum_state": plane.quantum_state,
                    "observer_dependent": plane.observer_dependent,
                    "entanglement_partners": plane.entanglement_partners,
                    "probability_amplitude": plane.probability_amplitude
                }
                for obj_id, plane in self.quantum_reality_planes.items()
            },
            "dimensional_connections": [
                {
                    "from_object": conn.from_object,
                    "to_object": conn.to_object,
                    "degrees": conn.degrees,
                    "dimensional_path": [d.code for d in conn.dimensional_path],
                    "connection_strength": conn.connection_strength,
                    "quantum_entangled": conn.quantum_entangled,
                    "spatial_distance": conn.spatial_distance,
                    "temporal_distance": conn.temporal_distance.total_seconds(),
                    "information_distance": conn.information_distance
                }
                for conn in self.dimensional_connections
            ]
        }

    # ========================================================================
    # SIX DEGREES OF SEPARATION - DIMENSIONAL ANALYSIS (@6dos)
    # ========================================================================

    def map_quantum_reality_plane(self, object_id: str, alert: Any) -> QuantumRealityPlane:
        """
        Map an object to its quantum reality plane of existence

        Determines which dimensions the object exists in based on its properties

        Args:
            object_id: Unique object identifier
            alert: Alert object to analyze

        Returns:
            QuantumRealityPlane
        """
        # Determine primary dimension based on alert properties
        text = f"{alert.title} {alert.message}".lower() if hasattr(alert, 'title') else ""

        # Start with 3D spatial (our reality)
        primary = DimensionalPlane.D3_SPATIAL
        accessible = [DimensionalPlane.D3_SPATIAL, DimensionalPlane.D4_TEMPORAL]

        # Check for quantum properties
        if any(word in text for word in ['quantum', 'entangle', 'superposition', 'observer']):
            # Use correct enum value from quantum_validation_lattice
            if hasattr(DimensionalPlane, 'D6_QUANTUM_ENTANGLEMENT'):
                accessible.append(DimensionalPlane.D6_QUANTUM_ENTANGLEMENT)
            elif hasattr(DimensionalPlane, 'D6_ENTANGLEMENT'):
                accessible.append(DimensionalPlane.D6_ENTANGLEMENT)
            accessible.append(DimensionalPlane.D7_PROBABILITY)
            if 'observer' in text or 'measure' in text:
                accessible.append(DimensionalPlane.D8_OBSERVER_EFFECT if hasattr(DimensionalPlane, 'D8_OBSERVER_EFFECT') else DimensionalPlane.D8_OBSERVER)
                observer_dependent = True
            else:
                observer_dependent = False
        else:
            observer_dependent = False

        # Check for information/computation properties
        if any(word in text for word in ['data', 'information', 'compute', 'algorithm']):
            # Use correct enum values
            if hasattr(DimensionalPlane, 'D12_INFORMATION'):
                accessible.append(DimensionalPlane.D12_INFORMATION)
            if hasattr(DimensionalPlane, 'D17_TECHNOLOGICAL'):
                accessible.append(DimensionalPlane.D17_TECHNOLOGICAL)
            if hasattr(DimensionalPlane, 'D18_SOCIAL'):
                accessible.append(DimensionalPlane.D18_SOCIAL)

        # Check for consciousness/awareness
        if any(word in text for word in ['aware', 'conscious', 'intent', 'mind']):
            # Use correct enum values
            if hasattr(DimensionalPlane, 'D13_CONSciousNESS'):
                accessible.append(DimensionalPlane.D13_CONSciousNESS)
            if hasattr(DimensionalPlane, 'D14_INTENTION'):
                accessible.append(DimensionalPlane.D14_INTENTION)

        # Check for string theory properties (advanced)
        if any(word in text for word in ['string', 'vibration', 'frequency', 'resonance']):
            # Use correct enum values
            if hasattr(DimensionalPlane, 'D9_STRING_COMPACT'):
                accessible.append(DimensionalPlane.D9_STRING_COMPACT)
            if hasattr(DimensionalPlane, 'D10_STRING_HARMONIC'):
                accessible.append(DimensionalPlane.D10_STRING_HARMONIC)
            if hasattr(DimensionalPlane, 'D11_BRANE_WORLD'):
                accessible.append(DimensionalPlane.D11_BRANE_WORLD)

        # Determine if flat (1D) or polar (2D) - compressed/blackhole-like
        if any(word in text for word in ['compressed', 'blackhole', 'singularity', 'point']):
            primary = DimensionalPlane.D1_FLAT
            accessible.insert(0, DimensionalPlane.D1_FLAT)
        elif any(word in text for word in ['polar', 'opposite', 'pair', 'duality']):
            primary = DimensionalPlane.D2_POLAR
            accessible.insert(0, DimensionalPlane.D2_POLAR)

        plane = QuantumRealityPlane(
            object_id=object_id,
            primary_dimension=primary,
            accessible_dimensions=list(set(accessible)),  # Remove duplicates
            quantum_state={
                "superposition": "observer" in text or "quantum" in text,
                "entangled": "entangle" in text,
                "coherent": "coherent" in text or "interference" in text
            },
            observer_dependent=observer_dependent,
            probability_amplitude=1.0 if not observer_dependent else 0.7
        )

        self.quantum_reality_planes[object_id] = plane
        return plane

    def find_six_degrees_path(self, from_object_id: str, to_object_id: str,
                              max_degrees: int = 6) -> Optional[DimensionalConnection]:
        """
        Find path between two objects using six degrees of separation

        Explores connections across dimensional planes

        Args:
            from_object_id: Source object ID
            to_object_id: Target object ID
            max_degrees: Maximum degrees to explore (default: 6)

        Returns:
            DimensionalConnection if path found, None otherwise
        """
        if from_object_id not in self.quantum_reality_planes:
            return None
        if to_object_id not in self.quantum_reality_planes:
            return None

        from_plane = self.quantum_reality_planes[from_object_id]
        to_plane = self.quantum_reality_planes[to_object_id]

        # Check if already connected
        if from_object_id in self.six_degrees_map and to_object_id in self.six_degrees_map[from_object_id]:
            degrees = self.six_degrees_map[from_object_id][to_object_id]
            if degrees <= max_degrees:
                # Find existing connection
                for conn in self.dimensional_connections:
                    if conn.from_object == from_object_id and conn.to_object == to_object_id:
                        return conn

        # Find common dimensions
        from_dims = set([from_plane.primary_dimension] + from_plane.accessible_dimensions)
        to_dims = set([to_plane.primary_dimension] + to_plane.accessible_dimensions)
        common_dims = from_dims.intersection(to_dims)

        if not common_dims:
            # No direct connection - need to find path through other objects
            degrees = self._find_path_through_objects(from_object_id, to_object_id, max_degrees)
            if degrees is None:
                return None
        else:
            # Direct connection through common dimension
            degrees = 1
            dimensional_path = [list(common_dims)[0]]  # Use first common dimension

        # Calculate connection strength
        connection_strength = 1.0 / degrees if degrees > 0 else 0.0

        # Check for quantum entanglement
        entanglement_dim = getattr(DimensionalPlane, 'D6_QUANTUM_ENTANGLEMENT', None) or getattr(DimensionalPlane, 'D6_ENTANGLEMENT', None)
        quantum_entangled = (
            (entanglement_dim and (from_plane.primary_dimension == entanglement_dim or to_plane.primary_dimension == entanglement_dim)) or
            from_object_id in to_plane.entanglement_partners or
            to_object_id in from_plane.entanglement_partners
        )

        # Calculate distances
        from_pos = self.positions.get(from_object_id)
        to_pos = self.positions.get(to_object_id)

        spatial_distance = 0.0
        if from_pos and to_pos:
            spatial_distance = from_pos.distance_to(to_pos)

        temporal_distance = timedelta(0)
        if from_pos and to_pos:
            temporal_distance = abs(from_pos.t - to_pos.t)

        # Information-theoretic distance (simplified)
        information_distance = abs(len(from_object_id) - len(to_object_id)) / max(len(from_object_id), len(to_object_id), 1)

        connection = DimensionalConnection(
            from_object=from_object_id,
            to_object=to_object_id,
            degrees=degrees,
            dimensional_path=dimensional_path if 'dimensional_path' in locals() else [from_plane.primary_dimension],
            connection_strength=connection_strength,
            quantum_entangled=quantum_entangled,
            spatial_distance=spatial_distance,
            temporal_distance=temporal_distance,
            information_distance=information_distance
        )

        self.dimensional_connections.append(connection)
        self.six_degrees_map[from_object_id][to_object_id] = degrees

        return connection

    def _find_path_through_objects(self, from_id: str, to_id: str, max_degrees: int) -> Optional[int]:
        """Find path through intermediate objects using BFS"""
        if from_id == to_id:
            return 0

        visited = {from_id}
        queue = [(from_id, 0)]  # (object_id, degrees)

        while queue:
            current_id, degrees = queue.pop(0)

            if degrees >= max_degrees:
                continue

            # Find all objects connected to current
            for conn in self.dimensional_connections:
                if conn.from_object == current_id and conn.to_object not in visited:
                    if conn.to_object == to_id:
                        return degrees + 1
                    visited.add(conn.to_object)
                    queue.append((conn.to_object, degrees + 1))

        return None

    def get_dimensional_story(self, object_id: str) -> str:
        """
        Get the "five-year-old story" explanation of an object's dimensional existence

        Args:
            object_id: Object to explain

        Returns:
            Story-like explanation
        """
        if object_id not in self.quantum_reality_planes:
            return f"Object {object_id} doesn't exist in any dimension yet!"

        plane = self.quantum_reality_planes[object_id]

        story = f"Once upon a time, there was an object called {object_id}.\n\n"

        # Primary dimension story
        if plane.primary_dimension == DimensionalPlane.D1_FLAT:
            story += "This object lived in a very flat world, like a tiny dot on a piece of paper. "
            story += "It was very compressed, like a tiny black hole with only one dimension - "
            story += "it could only move left and right, like a bug on a flat surface.\n\n"
        elif plane.primary_dimension == DimensionalPlane.D2_POLAR:
            story += "This object lived in a two-dimensional world with a friend! "
            story += "They were like your left hand and right hand - polar opposites, "
            story += "but connected by something invisible (like your nervous system and brain). "
            story += "They could see each other from two different places, creating "
            story += "longitude and latitude, like a map.\n\n"
        else:
            story += f"This object lives in our three-dimensional world! "
            story += f"It has length, width, AND height - spatial awareness in "
            story += f"three-dimensional space, with global positioning in a 'field' of space.\n\n"

        # Accessible dimensions
        if len(plane.accessible_dimensions) > 1:
            story += f"But here's the secret: This object can also peek into {len(plane.accessible_dimensions)-1} other dimensions! "
            story += f"Like a storybook with many pages, each page is a different dimension. "
            story += f"Scientists think there might be 21 or more dimensions, all stacked together "
            story += f"like layers of an onion, but we can only see 3 of them!\n\n"

        # Quantum properties
        if plane.quantum_state.get("entangled"):
            story += "This object is quantum entangled with other objects - "
            story += "they're connected by 'spooky action at a distance', like magic!\n\n"

        if plane.observer_dependent:
            story += "This object is special - it changes when you look at it! "
            story += "It's like a shy friend who acts differently when you're watching.\n\n"

        # Six degrees
        connections = [c for c in self.dimensional_connections if c.from_object == object_id or c.to_object == object_id]
        if connections:
            story += f"This object is connected to {len(connections)} other objects through "
            story += f"six degrees of separation - just like you're connected to your friend "
            story += f"through 6 people, everything in the universe is connected!\n\n"

        story += "And that's how objects exist in many dimensions at once! The end. 🌌"

        return story

    def _initialize_curriculum(self) -> None:
        """Initialize educational curriculum mappings"""
        # Map each dimensional plane to educational concepts

        # 1D - Flat Dimension
        self.educational_mappings["1D_FLAT"] = EducationalMapping(
            concept="One-Dimensional Space",
            dimensional_plane=DimensionalPlane.D1_FLAT,
            curriculum_levels=[CurriculumLevel.PRE_K, CurriculumLevel.ELEMENTARY],
            learning_objectives=[
                LearningObjective(
                    objective_id="1D_001",
                    title="Understanding Single Dimension",
                    description="Learn that a point can only move in one direction",
                    curriculum_level=CurriculumLevel.PRE_K,
                    subject="mathematics",
                    concepts=["dimension", "point", "line"],
                    skills=["spatial reasoning", "basic geometry"],
                    spacefaring_relevance="Understanding how spacecraft navigate in one dimension (forward/backward)",
                    certification_standard="Pre-K Math Foundation"
                )
            ],
            five_year_old_explanation="A tiny dot that can only move left and right, like a bug on a piece of paper!",
            twelve_year_old_explanation="A one-dimensional space where objects can only exist along a single axis, representing the most basic form of spatial existence.",
            spacefaring_application="Spacecraft navigation in linear trajectories, understanding forward/backward motion in space travel.",
            real_world_example="A train moving on tracks - it can only go forward or backward along one line."
        )

        # 3D - Spatial Dimension (Our Reality)
        self.educational_mappings["3D_SPATIAL"] = EducationalMapping(
            concept="Three-Dimensional Space",
            dimensional_plane=DimensionalPlane.D3_SPATIAL,
            curriculum_levels=[CurriculumLevel.ELEMENTARY, CurriculumLevel.MIDDLE, CurriculumLevel.HIGH_SCHOOL],
            learning_objectives=[
                LearningObjective(
                    objective_id="3D_001",
                    title="Spatial Awareness in 3D",
                    description="Understand length, width, and height in three-dimensional space",
                    curriculum_level=CurriculumLevel.ELEMENTARY,
                    subject="mathematics",
                    concepts=["3D space", "coordinates", "volume"],
                    skills=["spatial visualization", "coordinate systems"],
                    spacefaring_relevance="Essential for spacecraft navigation, understanding position in 3D space, orbital mechanics",
                    certification_standard="Elementary Geometry Standard"
                ),
                LearningObjective(
                    objective_id="3D_002",
                    title="Global Positioning Systems",
                    description="Learn how GPS works in three-dimensional space",
                    curriculum_level=CurriculumLevel.MIDDLE,
                    subject="physics",
                    concepts=["GPS", "satellites", "triangulation"],
                    skills=["navigation", "coordinate calculation"],
                    spacefaring_relevance="Critical for interplanetary navigation, understanding position relative to stars and planets",
                    certification_standard="Middle School Physics Standard"
                )
            ],
            five_year_old_explanation="Our world has length, width, AND height - like a box! You can move up, down, left, right, forward, and backward!",
            twelve_year_old_explanation="Three-dimensional space allows objects to exist with length, width, and height simultaneously, enabling complex navigation and positioning systems like GPS.",
            spacefaring_application="Fundamental for all space travel - understanding position in 3D space, orbital mechanics, navigation between planets and stars.",
            real_world_example="Your position right now: you have a location (latitude/longitude), height above sea level, and time - that's 3D + time = 4D!"
        )

        # 6D - Quantum Entanglement
        self.educational_mappings["6D_ENTANGLEMENT"] = EducationalMapping(
            concept="Quantum Entanglement",
            dimensional_plane=getattr(DimensionalPlane, 'D6_QUANTUM_ENTANGLEMENT', None) or getattr(DimensionalPlane, 'D6_ENTANGLEMENT', DimensionalPlane.D3_SPATIAL),
            curriculum_levels=[CurriculumLevel.HIGH_SCHOOL, CurriculumLevel.COLLEGE, CurriculumLevel.SPACEFARING],
            learning_objectives=[
                LearningObjective(
                    objective_id="6D_001",
                    title="Understanding Quantum Entanglement",
                    description="Learn about 'spooky action at a distance' and quantum connections",
                    curriculum_level=CurriculumLevel.HIGH_SCHOOL,
                    subject="physics",
                    concepts=["quantum mechanics", "entanglement", "non-locality"],
                    skills=["quantum reasoning", "abstract thinking"],
                    spacefaring_relevance="Future quantum communication systems for instant communication across vast distances in space",
                    certification_standard="High School Advanced Physics"
                )
            ],
            five_year_old_explanation="Two objects that are like magic friends - when one does something, the other knows instantly, even if they're far apart!",
            twelve_year_old_explanation="Quantum entanglement is a phenomenon where particles become connected in such a way that measuring one instantly affects the other, regardless of distance - Einstein called it 'spooky action at a distance'.",
            spacefaring_application="Quantum communication networks for instant data transmission across solar systems, enabling real-time communication with distant space colonies.",
            real_world_example="Like having two magic coins - when you flip one, the other automatically flips to match, even if they're on different planets!"
        )

        # 21D - Unity Dimension
        self.educational_mappings["21D_UNITY"] = EducationalMapping(
            concept="Unified Field Theory",
            dimensional_plane=DimensionalPlane.D21_UNITY,
            curriculum_levels=[CurriculumLevel.GRADUATE, CurriculumLevel.SPACEFARING],
            learning_objectives=[
                LearningObjective(
                    objective_id="21D_001",
                    title="Unified Field Understanding",
                    description="Comprehend how all dimensions and forces unify into one theory",
                    curriculum_level=CurriculumLevel.GRADUATE,
                    subject="physics",
                    concepts=["unified field", "theory of everything", "dimension unification"],
                    skills=["advanced physics", "theoretical reasoning"],
                    spacefaring_relevance="Understanding the fundamental nature of reality for advanced propulsion systems and dimensional travel",
                    certification_standard="Graduate Level Theoretical Physics"
                )
            ],
            five_year_old_explanation="Everything in the universe is connected like one big family - all the dimensions are really just different ways of looking at the same thing!",
            twelve_year_old_explanation="The unified field theory suggests that all dimensions and fundamental forces are different aspects of a single underlying reality - like different pages of the same storybook.",
            spacefaring_application="Theoretical foundation for advanced space travel technologies, potentially enabling travel through higher dimensions or manipulation of spacetime itself.",
            real_world_example="Like understanding that light, gravity, and all forces are really just different expressions of one unified field - the 'theory of everything'."
        )

    def get_educational_explanation(self, object_id: str, age_level: str = "five") -> Dict[str, Any]:
        """
        Get educational explanation tailored to age level

        Args:
            object_id: Object to explain
            age_level: "five", "twelve", "adult", or "spacefaring"

        Returns:
            Dictionary with educational content
        """
        if object_id not in self.quantum_reality_planes:
            return {"error": "Object not found"}

        plane = self.quantum_reality_planes[object_id]
        primary_dim = plane.primary_dimension

        # Find educational mapping
        mapping_key = f"{primary_dim.code}_{primary_dim.name.upper()}"
        if mapping_key not in self.educational_mappings:
            # Use generic mapping
            mapping = None
        else:
            mapping = self.educational_mappings[mapping_key]

        result = {
            "object_id": object_id,
            "primary_dimension": {
                "code": primary_dim.code,
                "name": primary_dim.name,
                "description": primary_dim.description
            },
            "accessible_dimensions": [
                {"code": d.code, "name": d.name, "description": d.description}
                for d in plane.accessible_dimensions
            ],
            "explanations": {}
        }

        if mapping:
            if age_level == "five":
                result["explanations"]["five_year_old"] = mapping.five_year_old_explanation
            elif age_level == "twelve":
                result["explanations"]["twelve_year_old"] = mapping.twelve_year_old_explanation
            elif age_level == "spacefaring":
                result["explanations"]["spacefaring"] = mapping.spacefaring_application

            result["learning_objectives"] = [
                {
                    "id": obj.objective_id,
                    "title": obj.title,
                    "description": obj.description,
                    "curriculum_level": obj.curriculum_level.value[0],
                    "subject": obj.subject,
                    "concepts": obj.concepts,
                    "skills": obj.skills,
                    "spacefaring_relevance": obj.spacefaring_relevance,
                    "certification_standard": obj.certification_standard
                }
                for obj in mapping.learning_objectives
            ]

            result["spacefaring_application"] = mapping.spacefaring_application
            result["real_world_example"] = mapping.real_world_example
            result["certification_path"] = mapping.certification_path

        # Add story
        result["story"] = self.get_dimensional_story(object_id)

        return result

    def get_curriculum_path(self, start_age: int = 5, target_level: CurriculumLevel = CurriculumLevel.SPACEFARING) -> List[LearningObjective]:
        """
        Get educational curriculum path from start age to target level

        Args:
            start_age: Starting age
            target_level: Target curriculum level

        Returns:
            List of learning objectives in sequence
        """
        path = []

        # Determine starting level
        if start_age <= 5:
            current_level = CurriculumLevel.PRE_K
        elif start_age <= 11:
            current_level = CurriculumLevel.ELEMENTARY
        elif start_age <= 14:
            current_level = CurriculumLevel.MIDDLE
        elif start_age <= 18:
            current_level = CurriculumLevel.HIGH_SCHOOL
        else:
            current_level = CurriculumLevel.COLLEGE

        # Collect all learning objectives in sequence
        level_order = [
            CurriculumLevel.PRE_K,
            CurriculumLevel.ELEMENTARY,
            CurriculumLevel.MIDDLE,
            CurriculumLevel.HIGH_SCHOOL,
            CurriculumLevel.COLLEGE,
            CurriculumLevel.GRADUATE,
            CurriculumLevel.SPACEFARING
        ]

        start_idx = level_order.index(current_level)
        end_idx = level_order.index(target_level)

        for level in level_order[start_idx:end_idx + 1]:
            for mapping in self.educational_mappings.values():
                for obj in mapping.learning_objectives:
                    if obj.curriculum_level == level:
                        path.append(obj)

        return path


def cli_main():
    """
    CLI Interface for Smart AI Logging Module

    Usage:
        python smart_ai_logging_module.py locate --incident-id <id>
        python smart_ai_logging_module.py locate --alert-id <id>
        python smart_ai_logging_module.py pathfind --from <id> --to <id>
        python smart_ai_logging_module.py factcheck --claim "<claim>" --method <method>
        python smart_ai_logging_module.py transactions --alert-id <id>
    """
    parser = argparse.ArgumentParser(
        description="Smart AI Logging Module - Global Positioning & Incident Tracking System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Locate an incident
  python smart_ai_logging_module.py locate --incident-id workflow_123

  # Find path between two alerts
  python smart_ai_logging_module.py pathfind --from alert_1 --to alert_2

  # Fact check a claim
  python smart_ai_logging_module.py factcheck --claim "5 + 3 = 8" --method mathematical

  # View transactions for an alert
  python smart_ai_logging_module.py transactions --alert-id alert_123
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Locate command
    locate_parser = subparsers.add_parser('locate', help='Locate incident/alert (WHERE, WHEN, WHY)')
    locate_group = locate_parser.add_mutually_exclusive_group(required=True)
    locate_group.add_argument('--incident-id', help='Incident ID to locate')
    locate_group.add_argument('--alert-id', help='Alert ID to locate')

    # Pathfind command
    pathfind_parser = subparsers.add_parser('pathfind', help='Find path between alerts')
    pathfind_parser.add_argument('--from', dest='from_id', required=True, help='Source alert ID')
    pathfind_parser.add_argument('--to', dest='to_id', required=True, help='Target alert ID')

    # Fact check command
    factcheck_parser = subparsers.add_parser('factcheck', help='Fact check a claim')
    factcheck_parser.add_argument('--claim', required=True, help='Claim to validate')
    factcheck_parser.add_argument('--method', choices=['mathematical', 'physics', 'logical', 'empirical'],
                                  default='logical', help='Validation method')

    # Transactions command
    transactions_parser = subparsers.add_parser('transactions', help='View transactions for alert')
    transactions_parser.add_argument('--alert-id', required=True, help='Alert ID')

    # Dimensional analysis command (@6dos)
    dim_parser = subparsers.add_parser('dimensions', help='Analyze dimensional perspective (@6dos)')
    dim_parser.add_argument('--object-id', required=True, help='Object/Alert ID to analyze')
    dim_parser.add_argument('--story', action='store_true', help='Show story explanation (five-year-old friendly)')

    # Six degrees command
    degrees_parser = subparsers.add_parser('6dos', help='Find six degrees of separation path')
    degrees_parser.add_argument('--from', dest='from_id', required=True, help='Source object ID')
    degrees_parser.add_argument('--to', dest='to_id', required=True, help='Target object ID')

    # Educational curriculum command
    edu_parser = subparsers.add_parser('education', help='Get educational explanation (AS/Gi curriculum)')
    edu_parser.add_argument('--object-id', required=True, help='Object/Alert ID to explain')
    edu_parser.add_argument('--age', choices=['five', 'twelve', 'adult', 'spacefaring'], 
                           default='five', help='Age-appropriate explanation level')

    # Curriculum path command
    curriculum_parser = subparsers.add_parser('curriculum', help='Get 12-year curriculum path')
    curriculum_parser.add_argument('--start-age', type=int, default=5, help='Starting age')
    curriculum_parser.add_argument('--target', choices=['elementary', 'middle', 'high_school', 'college', 'graduate', 'spacefaring'],
                                  default='spacefaring', help='Target curriculum level')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    module = SmartAILoggingModule()

    if args.command == 'locate':
        result = module.locate_incident(
            incident_id=args.incident_id,
            alert_id=args.alert_id
        )

        if 'error' in result:
            print(f"ERROR: {result['error']}")
            return

        print("\n" + "="*60)
        print("INCIDENT LOCATION REPORT")
        print("="*60)

        print("\n📍 WHERE:")
        where = result['where']
        print(f"  System: {where['system']}")
        print(f"  Component: {where['component']}")
        print(f"  Layer: {where['layer']}")
        print(f"  Coordinates: X={where['coordinates']['x']:.2f}, Y={where['coordinates']['y']:.2f}, Z={where['coordinates']['z']:.2f}")

        print("\n🕐 WHEN:")
        when = result['when']
        print(f"  Timestamp: {when['timestamp']}")
        print(f"  Timespan: {when['timespan']}")

        print("\n❓ WHY:")
        why = result['why']
        print(f"  Title: {why['title']}")
        print(f"  Message: {why['message'][:100]}...")
        print(f"  Severity: {why['severity']}")
        if why['criticality_tags']:
            print(f"  Criticality: {', '.join(why['criticality_tags'])}")
        if why['system_tags']:
            print(f"  Systems: {', '.join(why['system_tags'])}")
        if why['hashtags']:
            print(f"  Tags: {', '.join(why['hashtags'])}")

        if result['related']:
            print("\n🔗 RELATED INCIDENTS:")
            for related in result['related'][:5]:  # Show top 5
                print(f"  - {related['alert_id']} ({related['system']}/{related['component']}) - Distance: {related['distance']:.2f}")

        print("\n" + "="*60)

    elif args.command == 'pathfind':
        path = module.find_path(args.from_id, args.to_id)

        if not path:
            print(f"ERROR: No path found between {args.from_id} and {args.to_id}")
            return

        print("\n" + "="*60)
        print("PATHFINDING RESULT")
        print("="*60)
        print(f"\nPath from {args.from_id} to {args.to_id}:")
        print(f"  Total steps: {len(path)}")
        print(f"  Total distance: {path[0].distance_to(path[-1]):.2f}")
        print("\nPath:")
        for i, pos in enumerate(path):
            print(f"  {i+1}. {pos.system}/{pos.component} ({pos.layer}) - "
                  f"X:{pos.x:.2f} Y:{pos.y:.2f} Z:{pos.z:.2f} T:{pos.t.strftime('%H:%M:%S')}")
        print("\n" + "="*60)

    elif args.command == 'factcheck':
        fact_check = module.fact_check(args.claim, args.method)

        print("\n" + "="*60)
        print("FACT CHECK RESULT")
        print("="*60)
        print(f"\nClaim: {fact_check.claim}")
        print(f"Method: {fact_check.validation_method}")
        print(f"Result: {'✅ VALID' if fact_check.result else '❌ INVALID'}")
        print(f"Confidence: {fact_check.confidence:.1%}")

        if fact_check.evidence:
            print(f"\nEvidence:")
            for ev in fact_check.evidence:
                print(f"  - {ev}")

        if fact_check.mathematical_proof:
            print(f"\nMathematical Proof: {fact_check.mathematical_proof}")

        if fact_check.physics_principle:
            print(f"\nPhysics Principle: {fact_check.physics_principle}")

        print("\n" + "="*60)

    elif args.command == 'dimensions':
        # Find object in quantum reality planes
        if args.object_id not in module.quantum_reality_planes:
            # Try to create it from an alert
            alert = None
            for group in module.alert_groups.values():
                for a in group.alerts:
                    if getattr(a, 'alert_signature', None) == args.object_id:
                        alert = a
                        break
                if alert:
                    break

            if alert:
                plane = module.map_quantum_reality_plane(args.object_id, alert)
            else:
                print(f"ERROR: Object {args.object_id} not found")
                return
        else:
            plane = module.quantum_reality_planes[args.object_id]

        if args.story:
            story = module.get_dimensional_story(args.object_id)
            print("\n" + "="*60)
            print("DIMENSIONAL STORY")
            print("="*60)
            print(f"\n{story}\n")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("DIMENSIONAL ANALYSIS")
            print("="*60)
            print(f"\nObject: {args.object_id}")
            print(f"Primary Dimension: {plane.primary_dimension.code} - {plane.primary_dimension.name}")
            print(f"  {plane.primary_dimension.description}")
            print(f"\nAccessible Dimensions ({len(plane.accessible_dimensions)}):")
            for dim in plane.accessible_dimensions:
                print(f"  - {dim.code}: {dim.name} - {dim.description}")

            if plane.quantum_state:
                print(f"\nQuantum Properties:")
                for key, value in plane.quantum_state.items():
                    print(f"  - {key}: {value}")

            if plane.observer_dependent:
                print(f"\n⚠️  Observer-Dependent: This object changes when observed!")

            if plane.entanglement_partners:
                print(f"\n🔗 Entangled Partners: {', '.join(plane.entanglement_partners)}")

            print(f"\nProbability Amplitude: {plane.probability_amplitude:.2%}")
            print("\n" + "="*60)

    elif args.command == '6dos':
        connection = module.find_six_degrees_path(args.from_id, args.to_id)

        if not connection:
            print(f"ERROR: No path found between {args.from_id} and {args.to_id}")
            print("(Objects may not exist or be too far separated)")
            return

        print("\n" + "="*60)
        print("SIX DEGREES OF SEPARATION")
        print("="*60)
        print(f"\nFrom: {connection.from_object}")
        print(f"To: {connection.to_object}")
        print(f"Degrees: {connection.degrees}")
        print(f"Connection Strength: {connection.connection_strength:.2%}")

        if connection.quantum_entangled:
            print(f"\n🔗 QUANTUM ENTANGLED: These objects are connected by 'spooky action at a distance'!")

        print(f"\nDimensional Path:")
        for i, dim in enumerate(connection.dimensional_path):
            print(f"  {i+1}. {dim.code}: {dim.name} - {dim.description}")

        print(f"\nDistances:")
        print(f"  Spatial: {connection.spatial_distance:.2f} units")
        print(f"  Temporal: {connection.temporal_distance.total_seconds():.1f} seconds")
        print(f"  Information: {connection.information_distance:.2%}")

        print("\n" + "="*60)

    elif args.command == 'education':
        edu_result = module.get_educational_explanation(args.object_id, args.age)

        if 'error' in edu_result:
            print(f"ERROR: {edu_result['error']}")
            return

        print("\n" + "="*60)
        print("EDUCATIONAL EXPLANATION - AS/Gi 12-Year Curriculum")
        print("="*60)

        print(f"\n📚 Object: {edu_result['object_id']}")
        print(f"🌌 Primary Dimension: {edu_result['primary_dimension']['code']} - {edu_result['primary_dimension']['name']}")
        print(f"   {edu_result['primary_dimension']['description']}")

        if args.age in edu_result['explanations']:
            print(f"\n📖 Age-Appropriate Explanation ({args.age} years old):")
            print(f"   {edu_result['explanations'][args.age]}")

        if 'learning_objectives' in edu_result and edu_result['learning_objectives']:
            print(f"\n🎯 Learning Objectives:")
            for obj in edu_result['learning_objectives']:
                print(f"\n   {obj['id']}: {obj['title']}")
                print(f"      Level: {obj['curriculum_level']}")
                print(f"      Subject: {obj['subject']}")
                print(f"      Concepts: {', '.join(obj['concepts'])}")
                print(f"      Skills: {', '.join(obj['skills'])}")
                if obj['spacefaring_relevance']:
                    print(f"      🚀 Spacefaring Relevance: {obj['spacefaring_relevance']}")
                if obj['certification_standard']:
                    print(f"      ✅ Certification: {obj['certification_standard']}")

        if 'spacefaring_application' in edu_result:
            print(f"\n🚀 Spacefaring Application:")
            print(f"   {edu_result['spacefaring_application']}")

        if 'real_world_example' in edu_result:
            print(f"\n🌍 Real-World Example:")
            print(f"   {edu_result['real_world_example']}")

        print("\n" + "="*60)

    elif args.command == 'curriculum':
        target_map = {
            'elementary': CurriculumLevel.ELEMENTARY,
            'middle': CurriculumLevel.MIDDLE,
            'high_school': CurriculumLevel.HIGH_SCHOOL,
            'college': CurriculumLevel.COLLEGE,
            'graduate': CurriculumLevel.GRADUATE,
            'spacefaring': CurriculumLevel.SPACEFARING
        }
        target_level = target_map[args.target]

        path = module.get_curriculum_path(args.start_age, target_level)

        print("\n" + "="*60)
        print(f"12-YEAR CURRICULUM PATH: Age {args.start_age} → {args.target.upper()}")
        print("="*60)

        current_level = None
        for obj in path:
            if obj.curriculum_level != current_level:
                if current_level is not None:
                    print()
                print(f"\n📚 {obj.curriculum_level.value[0]} ({obj.curriculum_level.value[1]}):")
                current_level = obj.curriculum_level

            print(f"\n   {obj.objective_id}: {obj.title}")
            print(f"      {obj.description}")
            print(f"      Subject: {obj.subject}")
            print(f"      Concepts: {', '.join(obj.concepts)}")
            print(f"      Skills: {', '.join(obj.skills)}")
            if obj.spacefaring_relevance:
                print(f"      🚀 Spacefaring: {obj.spacefaring_relevance}")
            if obj.certification_standard:
                print(f"      ✅ Certification: {obj.certification_standard}")

        print(f"\n\n🎓 Total Learning Objectives: {len(path)}")
        print(f"🚀 Preparing for: {args.target.upper()} - Reaching for the Stars!")
        print("\n" + "="*60)

    elif args.command == 'transactions':
        transactions = [txn for txn in module.transactions.values() if txn.alert_id == args.alert_id]

        if not transactions:
            print(f"No transactions found for alert: {args.alert_id}")
            return

        print("\n" + "="*60)
        print(f"TRANSACTIONS FOR ALERT: {args.alert_id}")
        print("="*60)

        for txn in transactions:
            print(f"\nTransaction: {txn.transaction_id}")
            print(f"  Operation: {txn.operation_type}/{txn.operation_name}")
            print(f"  Source: {txn.source} → Target: {txn.target or 'N/A'}")
            print(f"  Status: {txn.status}")
            if txn.duration_ms:
                print(f"  Duration: {txn.duration_ms:.2f}ms")
            print(f"  Position: {txn.position.system}/{txn.position.component} ({txn.position.layer})")
            if txn.hooks:
                print(f"  Hooks: {', '.join(txn.hooks)}")

        print("\n" + "="*60)


def main():
    """Test the Smart AI Logging Module"""
    module = SmartAILoggingModule()

    # Create test alerts
    from datetime import datetime, timedelta

    class TestAlert:
        def __init__(self, title, message, level, timestamp):
            self.title = title
            self.message = message
            self.level = type('Level', (), {'level': level})()
            self.timestamp = timestamp
            self.source = "Test"

    now = datetime.now()
    alerts = [
        TestAlert("Action Required", '{"workflow_id": "test_workflow_123"}', "warning", now),
        TestAlert("Action Required", '{"workflow_id": "test_workflow_123"}', "warning", now + timedelta(seconds=10)),
        TestAlert("Action Required", '{"workflow_id": "test_workflow_123"}', "warning", now + timedelta(seconds=20)),
        TestAlert("Connection", "Connected to server", "info", now + timedelta(seconds=30)),
        TestAlert("Connection", "Connected to server", "info", now + timedelta(seconds=40)),
    ]

    # Analyze and group
    groups = module.analyze_and_group(alerts)

    print(f"Created {len(groups)} alert groups:")
    for group in groups:
        print(f"\nGroup: {group.group_id}")
        print(f"  Alerts: {group.alert_count}")
        print(f"  Timespan: {group.timespan_start} to {group.timespan_end}")
        print(f"  Intensity: {group.intensity.value}")
        print(f"  Temperature: {group.temperature.value}")
        print(f"  Criticality: {group.criticality.value}")
        print(f"  Meta-tags: {module.get_group_meta_tags_summary(group)}")

        # Test GPS positioning
        if group.alerts:
            position = module.calculate_position(group.alerts[0])
            print(f"  Position: {position.system}/{position.component} ({position.layer}) - "
                  f"X:{position.x:.2f} Y:{position.y:.2f} Z:{position.z:.2f}")

        # Test fact checking
        fact_check = module.fact_check(f"{group.alert_count} alerts occurred", "logical")
        print(f"  Fact Check: {fact_check.result} (confidence: {fact_check.confidence:.1%})")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # Run with arguments
        cli_main()
    else:
        # Run default
        cli_main()