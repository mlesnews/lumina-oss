#!/usr/bin/env python3
"""
RoamWise Atlas Visualization System

Hybrid WOW-Atlas/DEFCON Global Map with:
- Journaled events (RoamResearch-style knowledge graph)
- WiseBase presentation layer
- Overlayed topographical inference layers
- Hot-spot/DEFCON threat mapping
- Visual representation of opposing topographical layers
- Path forks, dead-ends, misdirection, pitfalls
- Ambush/blindside potential prediction
- Top 3 essential threats to @TRIAGE, @PROCESS, @CoA

Tags: #ROAMWISE #ATLAS #DEFCON #WISEBASE #JOURNALED_EVENTS #THREAT_MAP #HOTSPOT #TRIAGE #PROCESS #CoA #AMBUSH #BLINDSIDE @JARVIS @LUMINA @TRIAGE @PROCESS @CoA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
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

logger = get_logger("RoamWiseAtlas")


class DEFCONLevel(Enum):
    """DEFCON threat level"""
    DEFCON5 = 5  # Normal readiness
    DEFCON4 = 4  # Increased readiness
    DEFCON3 = 3  # Increased readiness above normal
    DEFCON2 = 2  # Next step to nuclear war
    DEFCON1 = 1  # Maximum readiness (nuclear war imminent)


class HotSpotType(Enum):
    """Hot-spot classification"""
    AMBUSH = "ambush"  # High ambush potential
    BLINDSIDE = "blindside"  # High blindside potential
    DEAD_END = "dead_end"  # Path termination
    MISDIRECTION = "misdirection"  # Wrong direction
    PITFALL = "pitfall"  # Subtle trap
    FORK = "fork"  # Multiple paths
    COORDINATION_GAP = "coordination_gap"  # Agent coordination failure


@dataclass
class JournaledEvent:
    """Journaled event (RoamResearch-style)"""
    event_id: str
    timestamp: str
    event_type: str  # "action", "decision", "threat", "coordination", "failure"
    title: str
    description: str
    tags: List[str] = field(default_factory=list)
    linked_events: List[str] = field(default_factory=list)  # Bidirectional links
    agents_involved: List[str] = field(default_factory=list)
    systems_affected: List[str] = field(default_factory=list)
    outcome: str = ""  # "success", "failure", "partial", "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AtlasNode:
    """Node in WOW-Atlas/DEFCON map"""
    node_id: str
    name: str
    x: float  # Map coordinates
    y: float
    z: float  # Elevation/layer
    defcon_level: DEFCONLevel
    hotspot_type: Optional[HotSpotType] = None
    threat_score: float = 0.0  # 0.0 - 1.0
    ambush_potential: float = 0.0
    blindside_potential: float = 0.0
    terrain_type: str = "plateau"  # "high_ground", "plateau", "valley", "ravine"
    connections: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)  # Linked journaled events
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TopographicalLayer:
    """Overlayed topographical layer"""
    layer_id: str
    name: str
    layer_type: str  # "operational", "threat", "inference", "agent", "temporal"
    nodes: Dict[str, AtlasNode] = field(default_factory=dict)
    connections: List[Tuple[str, str]] = field(default_factory=list)
    opacity: float = 0.7  # For overlay visualization
    color_scheme: str = "default"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatHotSpot:
    """Threat hot-spot on map"""
    hotspot_id: str
    name: str
    hotspot_type: HotSpotType
    defcon_level: DEFCONLevel
    location: Tuple[float, float, float]  # x, y, z
    threat_score: float
    ambush_potential: float
    blindside_potential: float
    affected_systems: List[str] = field(default_factory=list)
    mitigation_strategies: List[str] = field(default_factory=list)
    cover_our_arses: List[str] = field(default_factory=list)
    events: List[str] = field(default_factory=list)  # Related journaled events


class RoamWiseAtlasVisualization:
    """
    RoamWise Atlas Visualization System

    Combines:
    - Journaled events (RoamResearch knowledge graph)
    - WiseBase presentation layer
    - WOW-Atlas/DEFCON global map
    - Overlayed topographical layers
    - Threat hot-spot mapping
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RoamWise Atlas system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "roamwise_atlas"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.events_file = self.data_dir / "journaled_events.json"
        self.atlas_file = self.data_dir / "atlas_map.json"
        self.layers_file = self.data_dir / "topographical_layers.json"
        self.hotspots_file = self.data_dir / "threat_hotspots.json"

        # Data structures
        self.journaled_events: Dict[str, JournaledEvent] = {}
        self.atlas_nodes: Dict[str, AtlasNode] = {}
        self.topographical_layers: Dict[str, TopographicalLayer] = {}
        self.threat_hotspots: Dict[str, ThreatHotSpot] = {}

        # Load existing data
        self._load_data()

        # Initialize default layers
        self._initialize_default_layers()

        # Identify top 3 threats
        self._identify_top3_threats()

        logger.info("✅ RoamWise Atlas Visualization System initialized")
        logger.info(f"   Journaled events: {len(self.journaled_events)}")
        logger.info(f"   Atlas nodes: {len(self.atlas_nodes)}")
        logger.info(f"   Topographical layers: {len(self.topographical_layers)}")
        logger.info(f"   Threat hot-spots: {len(self.threat_hotspots)}")

    def _load_data(self):
        """Load existing data"""
        # Load journaled events
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.journaled_events = {
                        k: JournaledEvent(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load events: {e}")

        # Load atlas nodes
        if self.atlas_file.exists():
            try:
                with open(self.atlas_file, 'r') as f:
                    data = json.load(f)
                    self.atlas_nodes = {
                        k: AtlasNode(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load atlas: {e}")

        # Load layers
        if self.layers_file.exists():
            try:
                with open(self.layers_file, 'r') as f:
                    data = json.load(f)
                    self.topographical_layers = {
                        k: TopographicalLayer(
                            layer_id=k,
                            name=v.get("name", ""),
                            layer_type=v.get("layer_type", ""),
                            nodes={nk: AtlasNode(**nv) for nk, nv in v.get("nodes", {}).items()},
                            connections=[tuple(c) for c in v.get("connections", [])],
                            opacity=v.get("opacity", 0.7),
                            color_scheme=v.get("color_scheme", "default"),
                            metadata=v.get("metadata", {})
                        )
                        for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load layers: {e}")

        # Load hot-spots
        if self.hotspots_file.exists():
            try:
                with open(self.hotspots_file, 'r') as f:
                    data = json.load(f)
                    self.threat_hotspots = {
                        k: ThreatHotSpot(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load hot-spots: {e}")

    def _save_data(self):
        """Save all data"""
        # Save journaled events
        try:
            with open(self.events_file, 'w') as f:
                json.dump({
                    k: {
                        "event_id": v.event_id,
                        "timestamp": v.timestamp,
                        "event_type": v.event_type,
                        "title": v.title,
                        "description": v.description,
                        "tags": v.tags,
                        "linked_events": v.linked_events,
                        "agents_involved": v.agents_involved,
                        "systems_affected": v.systems_affected,
                        "outcome": v.outcome,
                        "metadata": v.metadata
                    }
                    for k, v in self.journaled_events.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving events: {e}")

        # Save atlas nodes
        try:
            with open(self.atlas_file, 'w') as f:
                json.dump({
                    k: {
                        "node_id": v.node_id,
                        "name": v.name,
                        "x": v.x,
                        "y": v.y,
                        "z": v.z,
                        "defcon_level": v.defcon_level.value,
                        "hotspot_type": v.hotspot_type.value if v.hotspot_type else None,
                        "threat_score": v.threat_score,
                        "ambush_potential": v.ambush_potential,
                        "blindside_potential": v.blindside_potential,
                        "terrain_type": v.terrain_type,
                        "connections": v.connections,
                        "events": v.events,
                        "tags": v.tags,
                        "metadata": v.metadata
                    }
                    for k, v in self.atlas_nodes.items()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"   ❌ Error saving atlas: {e}")

    def _initialize_default_layers(self):
        """Initialize default topographical layers"""
        if self.topographical_layers:
            return  # Already initialized

        # Layer 1: Operational Terrain
        operational_layer = TopographicalLayer(
            layer_id="operational",
            name="Operational Terrain",
            layer_type="operational",
            opacity=0.8,
            color_scheme="terrain"
        )

        # High Ground nodes
        operational_layer.nodes["jarvis_doit_rr"] = AtlasNode(
            node_id="jarvis_doit_rr",
            name="@JARVIS @DOIT @RR",
            x=50.0, y=50.0, z=100.0,
            defcon_level=DEFCONLevel.DEFCON5,
            threat_score=0.1,
            terrain_type="high_ground",
            tags=["@JARVIS", "@DOIT", "@RR"]
        )

        # Plateau nodes
        operational_layer.nodes["triage_process"] = AtlasNode(
            node_id="triage_process",
            name="@TRIAGE @PROCESS",
            x=30.0, y=30.0, z=50.0,
            defcon_level=DEFCONLevel.DEFCON4,
            threat_score=0.3,
            terrain_type="plateau",
            tags=["@TRIAGE", "@PROCESS"]
        )

        # Valley nodes
        operational_layer.nodes["coa_coordination"] = AtlasNode(
            node_id="coa_coordination",
            name="@CoA Coordination",
            x=20.0, y=20.0, z=25.0,
            defcon_level=DEFCONLevel.DEFCON3,
            threat_score=0.6,
            terrain_type="valley",
            tags=["@CoA", "@AI2AI"]
        )

        # Ravine nodes (danger zones)
        operational_layer.nodes["dead_end_trap"] = AtlasNode(
            node_id="dead_end_trap",
            name="Dead-End Trap",
            x=10.0, y=10.0, z=5.0,
            defcon_level=DEFCONLevel.DEFCON2,
            threat_score=0.9,
            hotspot_type=HotSpotType.DEAD_END,
            ambush_potential=0.8,
            terrain_type="ravine",
            tags=[]
        )

        self.topographical_layers["operational"] = operational_layer

        # Layer 2: Threat Topography
        threat_layer = TopographicalLayer(
            layer_id="threat",
            name="Threat Topography",
            layer_type="threat",
            opacity=0.6,
            color_scheme="defcon"
        )

        # Add threat nodes
        threat_layer.nodes["triage_cascade"] = AtlasNode(
            node_id="triage_cascade",
            name="TRIAGE Cascade Failure",
            x=25.0, y=25.0, z=30.0,
            defcon_level=DEFCONLevel.DEFCON1,
            threat_score=0.95,
            hotspot_type=HotSpotType.AMBUSH,
            ambush_potential=0.85,
            blindside_potential=0.75,
            terrain_type="ravine",
            tags=["@TRIAGE", "cascade", "failure"]
        )

        threat_layer.nodes["process_deadlock"] = AtlasNode(
            node_id="process_deadlock",
            name="PROCESS Deadlock",
            x=35.0, y=35.0, z=20.0,
            defcon_level=DEFCONLevel.DEFCON1,
            threat_score=0.90,
            hotspot_type=HotSpotType.BLINDSIDE,
            ambush_potential=0.80,
            blindside_potential=0.70,
            terrain_type="ravine",
            tags=["@PROCESS", "deadlock"]
        )

        threat_layer.nodes["coa_breakdown"] = AtlasNode(
            node_id="coa_breakdown",
            name="Agent Coordination Breakdown",
            x=15.0, y=15.0, z=10.0,
            defcon_level=DEFCONLevel.DEFCON1,
            threat_score=0.98,
            hotspot_type=HotSpotType.COORDINATION_GAP,
            ambush_potential=0.90,
            blindside_potential=0.85,
            terrain_type="ravine",
            tags=["@CoA", "coordination", "breakdown"]
        )

        self.topographical_layers["threat"] = threat_layer

        # Create hot-spots from threat nodes
        self._create_hotspots_from_threats()

    def _create_hotspots_from_threats(self):
        """Create threat hot-spots from threat layer nodes"""
        threat_layer = self.topographical_layers.get("threat")
        if not threat_layer:
            return

        for node_id, node in threat_layer.nodes.items():
            if node.hotspot_type:
                hotspot = ThreatHotSpot(
                    hotspot_id=node_id,
                    name=node.name,
                    hotspot_type=node.hotspot_type,
                    defcon_level=node.defcon_level,
                    location=(node.x, node.y, node.z),
                    threat_score=node.threat_score,
                    ambush_potential=node.ambush_potential,
                    blindside_potential=node.blindside_potential,
                    affected_systems=node.tags,
                    mitigation_strategies=[],
                    cover_our_arses=[],
                    events=node.events
                )
                self.threat_hotspots[node_id] = hotspot

    def _identify_top3_threats(self):
        """Identify and document top 3 essential threats"""
        # Threat 1: TRIAGE Cascade Failure
        if "threat_001_triage" not in self.threat_hotspots:
            self.threat_hotspots["threat_001_triage"] = ThreatHotSpot(
                hotspot_id="threat_001_triage",
                name="TRIAGE Cascade Failure",
                hotspot_type=HotSpotType.AMBUSH,
                defcon_level=DEFCONLevel.DEFCON1,
                location=(25.0, 25.0, 30.0),
                threat_score=0.95,
                ambush_potential=0.85,
                blindside_potential=0.75,
                affected_systems=["@TRIAGE", "@DOIT", "@JARVIS"],
                mitigation_strategies=[
                    "Fallback priority system (default to 'medium')",
                    "Redundant routing paths",
                    "Agent reserve pool",
                    "Circuit breaker (auto-disable if failure rate > 50%)",
                    "Manual override capability"
                ],
                cover_our_arses=[
                    "Priority validation layer",
                    "Routing redundancy",
                    "Agent availability checks",
                    "Failure rate monitoring",
                    "Human intervention capability"
                ]
            )

        # Threat 2: PROCESS Deadlock
        if "threat_002_process" not in self.threat_hotspots:
            self.threat_hotspots["threat_002_process"] = ThreatHotSpot(
                hotspot_id="threat_002_process",
                name="PROCESS Deadlock and Circular Dependencies",
                hotspot_type=HotSpotType.BLINDSIDE,
                defcon_level=DEFCONLevel.DEFCON1,
                location=(35.0, 35.0, 20.0),
                threat_score=0.90,
                ambush_potential=0.80,
                blindside_potential=0.70,
                affected_systems=["@PROCESS", "@CoA", "@AI2AI"],
                mitigation_strategies=[
                    "Deadlock detection algorithms",
                    "Timeout mechanisms on all steps",
                    "Dependency graph validation",
                    "Break-glass protocol",
                    "Process isolation"
                ],
                cover_our_arses=[
                    "Pre-execution dependency validation",
                    "Timeout enforcement",
                    "Cycle detection",
                    "Force unlock mechanism",
                    "Process isolation capability"
                ]
            )

        # Threat 3: @CoA Coordination Breakdown
        if "threat_003_coa" not in self.threat_hotspots:
            self.threat_hotspots["threat_003_coa"] = ThreatHotSpot(
                hotspot_id="threat_003_coa",
                name="Agent Coordination Breakdown (@CoA Failure)",
                hotspot_type=HotSpotType.COORDINATION_GAP,
                defcon_level=DEFCONLevel.DEFCON1,
                location=(15.0, 15.0, 10.0),
                threat_score=0.98,
                ambush_potential=0.90,
                blindside_potential=0.85,
                affected_systems=["@CoA", "@AI2AI", "@AGENT2AGENT", "@JARVIS"],
                mitigation_strategies=[
                    "Heartbeat monitoring",
                    "State synchronization",
                    "Conflict resolution protocols",
                    "Isolation mode for failing agents",
                    "Emergency shutdown",
                    "Audit trail"
                ],
                cover_our_arses=[
                    "Agent health monitoring",
                    "Communication redundancy",
                    "State verification",
                    "Conflict detection",
                    "Graceful degradation",
                    "Complete action logging"
                ]
            )

    def journal_event(
        self,
        event_type: str,
        title: str,
        description: str,
        tags: List[str] = None,
        agents_involved: List[str] = None,
        systems_affected: List[str] = None,
        outcome: str = "unknown",
        link_to_events: List[str] = None
    ) -> JournaledEvent:
        """Journal an event (RoamResearch-style)"""
        event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        event = JournaledEvent(
            event_id=event_id,
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            title=title,
            description=description,
            tags=tags or [],
            linked_events=link_to_events or [],
            agents_involved=agents_involved or [],
            systems_affected=systems_affected or [],
            outcome=outcome,
            metadata={}
        )

        # Create bidirectional links
        for linked_id in event.linked_events:
            if linked_id in self.journaled_events:
                if event_id not in self.journaled_events[linked_id].linked_events:
                    self.journaled_events[linked_id].linked_events.append(event_id)

        self.journaled_events[event_id] = event
        self._save_data()

        logger.info(f"   ✅ Journaled event: {title}")

        return event

    def visualize_atlas(
        self,
        layer_ids: List[str] = None,
        output_format: str = "ascii",
        output_file: Optional[Path] = None
    ) -> str:
        """
        Generate WOW-Atlas/DEFCON visualization

        Args:
            layer_ids: Which layers to visualize (None = all)
            output_format: "ascii", "json", "markdown"
            output_file: Optional file to save output
        """
        if layer_ids is None:
            layer_ids = list(self.topographical_layers.keys())

        if output_format == "ascii":
            return self._visualize_ascii_atlas(layer_ids, output_file)
        elif output_format == "json":
            return self._visualize_json_atlas(layer_ids, output_file)
        elif output_format == "markdown":
            return self._visualize_markdown_atlas(layer_ids, output_file)
        else:
            return self._visualize_ascii_atlas(layer_ids, output_file)

    def _visualize_ascii_atlas(self, layer_ids: List[str], output_file: Optional[Path]) -> str:
        try:
            """Generate ASCII WOW-Atlas visualization"""
            lines = []
            lines.append("=" * 100)
            lines.append("ROAMWISE ATLAS - WOW-ATLAS/DEFCON GLOBAL MAP")
            lines.append("=" * 100)
            lines.append("")

            # DEFCON Legend
            lines.append("DEFCON LEVELS:")
            lines.append("  DEFCON 5 (🟢) - Normal readiness")
            lines.append("  DEFCON 4 (🟡) - Increased readiness")
            lines.append("  DEFCON 3 (🟠) - Increased readiness above normal")
            lines.append("  DEFCON 2 (🔴) - Next step to nuclear war")
            lines.append("  DEFCON 1 (⚫) - Maximum readiness (nuclear war imminent)")
            lines.append("")

            # Hot-spot Legend
            lines.append("HOT-SPOT TYPES:")
            lines.append("  🎯 AMBUSH - High ambush potential")
            lines.append("  👁️  BLINDSIDE - High blindside potential")
            lines.append("  🚫 DEAD_END - Path termination")
            lines.append("  🔀 MISDIRECTION - Wrong direction")
            lines.append("  ⚠️  PITFALL - Subtle trap")
            lines.append("  🍴 FORK - Multiple paths")
            lines.append("  🔗 COORDINATION_GAP - Agent coordination failure")
            lines.append("")
            lines.append("=" * 100)
            lines.append("")

            # Top 3 Threats
            lines.append("TOP 3 ESSENTIAL THREATS:")
            lines.append("-" * 100)
            top3 = [
                self.threat_hotspots.get("threat_001_triage"),
                self.threat_hotspots.get("threat_002_process"),
                self.threat_hotspots.get("threat_003_coa")
            ]

            for i, threat in enumerate(top3, 1):
                if threat:
                    defcon_icon = "⚫" if threat.defcon_level == DEFCONLevel.DEFCON1 else \
                                 "🔴" if threat.defcon_level == DEFCONLevel.DEFCON2 else \
                                 "🟠" if threat.defcon_level == DEFCONLevel.DEFCON3 else \
                                 "🟡" if threat.defcon_level == DEFCONLevel.DEFCON4 else "🟢"

                    hotspot_icon = "🎯" if threat.hotspot_type == HotSpotType.AMBUSH else \
                                 "👁️" if threat.hotspot_type == HotSpotType.BLINDSIDE else \
                                 "🔗" if threat.hotspot_type == HotSpotType.COORDINATION_GAP else "⚠️"

                    lines.append(f"{i}. {defcon_icon} {hotspot_icon} {threat.name}")
                    lines.append(f"   Threat Score: {threat.threat_score:.1%}")
                    lines.append(f"   Ambush Potential: {threat.ambush_potential:.1%}")
                    lines.append(f"   Blindside Potential: {threat.blindside_potential:.1%}")
                    lines.append(f"   Affected Systems: {', '.join(threat.affected_systems)}")
                    lines.append(f"   Location: ({threat.location[0]:.1f}, {threat.location[1]:.1f}, {threat.location[2]:.1f})")
                    lines.append("")

            lines.append("=" * 100)
            lines.append("")

            # Layer Visualizations
            for layer_id in layer_ids:
                layer = self.topographical_layers.get(layer_id)
                if not layer:
                    continue

                lines.append(f"LAYER: {layer.name.upper()} ({layer.layer_type})")
                lines.append("-" * 100)

                # Group nodes by DEFCON level
                by_defcon = {}
                for node in layer.nodes.values():
                    defcon = node.defcon_level.value
                    if defcon not in by_defcon:
                        by_defcon[defcon] = []
                    by_defcon[defcon].append(node)

                # Display by DEFCON (1 = highest threat)
                for defcon_level in sorted(by_defcon.keys()):
                    defcon_icon = "⚫" if defcon_level == 1 else \
                                 "🔴" if defcon_level == 2 else \
                                 "🟠" if defcon_level == 3 else \
                                 "🟡" if defcon_level == 4 else "🟢"

                    lines.append(f"\nDEFCON {defcon_level} {defcon_icon}:")

                    for node in by_defcon[defcon_level]:
                        hotspot_icon = ""
                        if node.hotspot_type:
                            hotspot_icon = "🎯" if node.hotspot_type == HotSpotType.AMBUSH else \
                                         "👁️" if node.hotspot_type == HotSpotType.BLINDSIDE else \
                                         "🚫" if node.hotspot_type == HotSpotType.DEAD_END else \
                                         "🔀" if node.hotspot_type == HotSpotType.MISDIRECTION else \
                                         "⚠️" if node.hotspot_type == HotSpotType.PITFALL else \
                                         "🍴" if node.hotspot_type == HotSpotType.FORK else \
                                         "🔗" if node.hotspot_type == HotSpotType.COORDINATION_GAP else ""

                        terrain_icon = "⛰️" if node.terrain_type == "high_ground" else \
                                      "🏔️" if node.terrain_type == "plateau" else \
                                      "🏞️" if node.terrain_type == "valley" else "🕳️"

                        lines.append(f"  {defcon_icon} {hotspot_icon} {terrain_icon} {node.name}")
                        lines.append(f"     Location: ({node.x:.1f}, {node.y:.1f}, {node.z:.1f})")
                        lines.append(f"     Threat: {node.threat_score:.1%} | Ambush: {node.ambush_potential:.1%} | Blindside: {node.blindside_potential:.1%}")
                        if node.tags:
                            lines.append(f"     Tags: {', '.join(node.tags)}")
                        if node.connections:
                            lines.append(f"     → {', '.join(node.connections)}")
                        lines.append("")

                lines.append("")

            lines.append("=" * 100)

            result = "\n".join(lines)

            if output_file:
                output_file.write_text(result)
                logger.info(f"   ✅ Atlas visualization saved to {output_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in _visualize_ascii_atlas: {e}", exc_info=True)
            raise
    def _visualize_json_atlas(self, layer_ids: List[str], output_file: Optional[Path]) -> str:
        try:
            """Generate JSON atlas visualization"""
            data = {
                "timestamp": datetime.now().isoformat(),
                "layers": {
                    layer_id: {
                        "layer_id": layer.layer_id,
                        "name": layer.name,
                        "layer_type": layer.layer_type,
                        "nodes": {
                            node_id: {
                                "node_id": node.node_id,
                                "name": node.name,
                                "location": [node.x, node.y, node.z],
                                "defcon_level": node.defcon_level.value,
                                "hotspot_type": node.hotspot_type.value if node.hotspot_type else None,
                                "threat_score": node.threat_score,
                                "ambush_potential": node.ambush_potential,
                                "blindside_potential": node.blindside_potential,
                                "terrain_type": node.terrain_type,
                                "tags": node.tags
                            }
                            for node_id, node in layer.nodes.items()
                        }
                    }
                    for layer_id, layer in [(lid, self.topographical_layers.get(lid)) for lid in layer_ids]
                    if layer
                },
                "top3_threats": [
                    {
                        "hotspot_id": threat.hotspot_id,
                        "name": threat.name,
                        "hotspot_type": threat.hotspot_type.value,
                        "defcon_level": threat.defcon_level.value,
                        "location": list(threat.location),
                        "threat_score": threat.threat_score,
                        "ambush_potential": threat.ambush_potential,
                        "blindside_potential": threat.blindside_potential,
                        "affected_systems": threat.affected_systems,
                        "mitigation_strategies": threat.mitigation_strategies,
                        "cover_our_arses": threat.cover_our_arses
                    }
                    for threat in [
                        self.threat_hotspots.get("threat_001_triage"),
                        self.threat_hotspots.get("threat_002_process"),
                        self.threat_hotspots.get("threat_003_coa")
                    ]
                    if threat
                ]
            }

            result = json.dumps(data, indent=2)

            if output_file:
                output_file.write_text(result)
                logger.info(f"   ✅ JSON atlas saved to {output_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in _visualize_json_atlas: {e}", exc_info=True)
            raise
    def _visualize_markdown_atlas(self, layer_ids: List[str], output_file: Optional[Path]) -> str:
        try:
            """Generate Markdown atlas visualization"""
            lines = []
            lines.append("# RoamWise Atlas - WOW-Atlas/DEFCON Global Map")
            lines.append("")
            lines.append(f"**Generated:** {datetime.now().isoformat()}")
            lines.append("")

            # Top 3 Threats
            lines.append("## Top 3 Essential Threats")
            lines.append("")
            top3 = [
                self.threat_hotspots.get("threat_001_triage"),
                self.threat_hotspots.get("threat_002_process"),
                self.threat_hotspots.get("threat_003_coa")
            ]

            for i, threat in enumerate(top3, 1):
                if threat:
                    lines.append(f"### {i}. {threat.name}")
                    lines.append("")
                    lines.append(f"- **DEFCON Level:** {threat.defcon_level.value}")
                    lines.append(f"- **Hot-Spot Type:** {threat.hotspot_type.value}")
                    lines.append(f"- **Threat Score:** {threat.threat_score:.1%}")
                    lines.append(f"- **Ambush Potential:** {threat.ambush_potential:.1%}")
                    lines.append(f"- **Blindside Potential:** {threat.blindside_potential:.1%}")
                    lines.append(f"- **Affected Systems:** {', '.join(threat.affected_systems)}")
                    lines.append("")
                    lines.append("#### Mitigation Strategies")
                    for strategy in threat.mitigation_strategies:
                        lines.append(f"- {strategy}")
                    lines.append("")
                    lines.append("#### Cover-Our-Arses")
                    for coa in threat.cover_our_arses:
                        lines.append(f"- {coa}")
                    lines.append("")

            # Layers
            lines.append("## Topographical Layers")
            lines.append("")

            for layer_id in layer_ids:
                layer = self.topographical_layers.get(layer_id)
                if not layer:
                    continue

                lines.append(f"### {layer.name}")
                lines.append("")
                lines.append(f"**Type:** {layer.layer_type}")
                lines.append("")

                for node in layer.nodes.values():
                    lines.append(f"#### {node.name}")
                    lines.append("")
                    lines.append(f"- **Location:** ({node.x:.1f}, {node.y:.1f}, {node.z:.1f})")
                    lines.append(f"- **DEFCON:** {node.defcon_level.value}")
                    lines.append(f"- **Threat Score:** {node.threat_score:.1%}")
                    if node.hotspot_type:
                        lines.append(f"- **Hot-Spot:** {node.hotspot_type.value}")
                    lines.append("")

            result = "\n".join(lines)

            if output_file:
                output_file.write_text(result)
                logger.info(f"   ✅ Markdown atlas saved to {output_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in _visualize_markdown_atlas: {e}", exc_info=True)
            raise
    def get_top3_threats(self) -> List[ThreatHotSpot]:
        """Get top 3 essential threats"""
        return [
            self.threat_hotspots.get("threat_001_triage"),
            self.threat_hotspots.get("threat_002_process"),
            self.threat_hotspots.get("threat_003_coa")
        ]


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="RoamWise Atlas Visualization System")
        parser.add_argument("--visualize", action="store_true", help="Visualize atlas")
        parser.add_argument("--format", type=str, default="ascii", choices=["ascii", "json", "markdown"], help="Output format")
        parser.add_argument("--layers", type=str, nargs="+", help="Layers to visualize (default: all)")
        parser.add_argument("--get-threats", action="store_true", help="Get top 3 threats")
        parser.add_argument("--journal", type=str, nargs=4, metavar=("TYPE", "TITLE", "DESCRIPTION", "TAGS"), help="Journal an event")
        parser.add_argument("--output", type=str, help="Output file path")

        args = parser.parse_args()

        system = RoamWiseAtlasVisualization()

        if args.visualize:
            output_file = Path(args.output) if args.output else None
            viz = system.visualize_atlas(
                layer_ids=args.layers,
                output_format=args.format,
                output_file=output_file
            )
            print(viz)

        elif args.get_threats:
            threats = system.get_top3_threats()
            print("Top 3 Essential Threats:")
            for i, threat in enumerate(threats, 1):
                if threat:
                    print(f"\n{i}. {threat.name}")
                    print(f"   DEFCON: {threat.defcon_level.value}")
                    print(f"   Threat Score: {threat.threat_score:.1%}")
                    print(f"   Ambush: {threat.ambush_potential:.1%} | Blindside: {threat.blindside_potential:.1%}")

        elif args.journal:
            event_type, title, description, tags_str = args.journal
            tags = [t.strip() for t in tags_str.split(",")]
            event = system.journal_event(
                event_type=event_type,
                title=title,
                description=description,
                tags=tags
            )
            print(f"✅ Journaled event: {event.event_id}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()