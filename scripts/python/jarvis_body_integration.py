#!/usr/bin/env python3
"""
JARVIS Body Integration System - Holistic LUMINA Connection

JARVIS is the brain/command center. LUMINA is the body.
This system ensures all "body parts" (LUMINA systems) are connected to JARVIS,
and JARVIS maintains "three-foot bubble" awareness of its environment.

Tags: #JARVIS #BODY_INTEGRATION #LUMINA #THREE_FOOT_BUBBLE @JARVIS @LUMINA
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
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

logger = get_logger("JARVISBodyIntegration")


class BodyPartType(Enum):
    """Types of body parts in the LUMINA body"""
    SENSE = "sense"  # Sensory systems (sight, hearing, touch, taste, smell)
    LIMB = "limb"  # Execution systems (arms, legs, hands)
    ORGAN = "organ"  # Internal systems (heart, lungs, liver)
    SYSTEM = "system"  # Complex systems (nervous, circulatory, respiratory)


class BodyPart:
    """Represents a body part in the LUMINA body"""

    def __init__(self, part_id: str, name: str, part_type: BodyPartType,
                 system_path: Optional[Path] = None, status: str = "unknown"):
        self.part_id = part_id
        self.name = name
        self.part_type = part_type
        self.system_path = system_path
        self.status = status  # healthy, degraded, down, unknown
        self.last_checked = None
        self.health_score = 100.0  # 0-100
        self.capabilities = []
        self.integration_point = None  # How JARVIS can interact with it

    def check_health(self) -> Dict[str, Any]:
        """Check health of this body part"""
        # This would check the actual system
        # For now, return status
        self.last_checked = datetime.now().isoformat()
        return {
            "part_id": self.part_id,
            "name": self.name,
            "status": self.status,
            "health_score": self.health_score,
            "last_checked": self.last_checked
        }


class ThreeFootBubble:
    """
    Three-Foot Bubble - JARVIS's Personal Space Awareness

    Like a human's three-foot bubble, JARVIS is aware of everything
    in its immediate environment (all connected systems).
    """

    def __init__(self, jarvis_core=None):
        self.jarvis_core = jarvis_core
        self.awareness_radius = 3.0  # Three-foot radius
        self.monitored_systems: Dict[str, BodyPart] = {}
        self.proximity_map: Dict[str, float] = {}  # System ID -> proximity score

    def add_system(self, body_part: BodyPart, proximity: float = 1.0):
        """Add a system to the bubble awareness"""
        self.monitored_systems[body_part.part_id] = body_part
        self.proximity_map[body_part.part_id] = min(1.0, max(0.0, proximity))
        logger.info(f"✅ Added {body_part.name} to three-foot bubble (proximity: {proximity:.2f})")

    def get_awareness(self) -> Dict[str, Any]:
        """Get full awareness of three-foot bubble"""
        awareness = {
            "timestamp": datetime.now().isoformat(),
            "radius": self.awareness_radius,
            "systems_in_bubble": len(self.monitored_systems),
            "systems": []
        }

        for part_id, body_part in self.monitored_systems.items():
            health = body_part.check_health()
            health["proximity"] = self.proximity_map.get(part_id, 0.0)
            awareness["systems"].append(health)

        return awareness

    def detect_pain_points(self) -> List[Dict[str, Any]]:
        """Detect pain points (degraded systems) in the bubble"""
        pain_points = []

        for part_id, body_part in self.monitored_systems.items():
            if body_part.health_score < 80.0 or body_part.status in ["degraded", "down"]:
                pain_points.append({
                    "part_id": part_id,
                    "name": body_part.name,
                    "status": body_part.status,
                    "health_score": body_part.health_score,
                    "severity": "high" if body_part.health_score < 50 else "medium"
                })

        return pain_points


class JARVISBodyIntegration:
    """
    JARVIS Body Integration System

    Connects JARVIS (brain) to all LUMINA body parts.
    Ensures all systems are connected and JARVIS can sense/command them.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir = self.project_root / "scripts" / "python"

        # JARVIS core reference (set externally to avoid circular import)
        self.jarvis_core = None

        # Three-foot bubble (jarvis_core will be set later to avoid circular import)
        self.bubble = ThreeFootBubble()

        # Body parts registry
        self.body_parts: Dict[str, BodyPart] = {}

        # Load body mapping
        self._load_body_mapping()

        # Register all body parts in bubble
        self._register_body_parts_in_bubble()

        logger.info("=" * 80)
        logger.info("🧬 JARVIS BODY INTEGRATION INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"   Body Scope: LUMINA + @HOMELAB")
        logger.info(f"   Body Parts: {len(self.body_parts)}")
        logger.info(f"   Systems in Bubble: {len(self.bubble.monitored_systems) if self.bubble else 0}")
        logger.info("=" * 80)

    def _load_body_mapping(self):
        """Load body part mapping from configuration"""
        # Map LUMINA + @HOMELAB systems to body parts based on human body analogy
        # @HOMELAB is the full scope of JARVIS's body

        # SENSORY SYSTEMS (Five Senses)
        self.body_parts["sight"] = BodyPart(
            "sight", "Sight (Vision) - @ANALYTICS-ORACLE",
            BodyPartType.SENSE,
            self.scripts_dir / "jarvis_desktop_monitor.py",
            "healthy"
        )
        self.body_parts["sight"].capabilities = [
            "data_visualization",
            "system_monitoring",
            "predictive_analytics",
            "pattern_recognition"
        ]

        self.body_parts["hearing"] = BodyPart(
            "hearing", "Hearing (Audition) - Communication Protocols",
            BodyPartType.SENSE,
            self.scripts_dir / "jarvis_voice_trigger.py",
            "healthy"
        )
        self.body_parts["hearing"].capabilities = [
            "voice_recognition",
            "language_processing",
            "command_reception",
            "context_awareness"
        ]

        self.body_parts["touch"] = BodyPart(
            "touch", "Touch (Somatosensory) - User Interface Systems",
            BodyPartType.SENSE,
            self.scripts_dir / "jarvis_desktop_assistant_enhanced.py",
            "healthy"
        )
        self.body_parts["touch"].capabilities = [
            "user_interaction",
            "interface_feedback",
            "proprioception",
            "pain_detection"
        ]

        self.body_parts["taste"] = BodyPart(
            "taste", "Taste (Gustation) - Quality Assessment",
            BodyPartType.SENSE,
            self.scripts_dir / "ai_slop_detector.py",
            "healthy"
        )
        self.body_parts["taste"].capabilities = [
            "content_evaluation",
            "quality_assessment",
            "truth_detection",
            "poison_recognition"
        ]

        self.body_parts["smell"] = BodyPart(
            "smell", "Smell (Olfaction) - Anomaly Detection",
            BodyPartType.SENSE,
            self.scripts_dir / "jarvis_proactive_ide_problem_monitor.py",
            "healthy"
        )
        self.body_parts["smell"].capabilities = [
            "threat_detection",
            "anomaly_recognition",
            "environmental_monitoring",
            "security_monitoring"
        ]

        # CIRCULATORY SYSTEM (Heart)
        self.body_parts["heart"] = BodyPart(
            "heart", "Heart - @SYNC-COORDINATOR",
            BodyPartType.ORGAN,
            self.scripts_dir / "hybrid_notebook_sync_manager.py",
            "healthy"
        )
        self.body_parts["heart"].capabilities = [
            "data_synchronization",
            "information_flow",
            "system_harmony",
            "load_balancing"
        ]

        # RESPIRATORY SYSTEM (Lungs)
        self.body_parts["lungs"] = BodyPart(
            "lungs", "Lungs - Input/Output Processing",
            BodyPartType.ORGAN,
            self.scripts_dir / "jarvis_api_cli_control.py",
            "healthy"
        )
        self.body_parts["lungs"].capabilities = [
            "data_ingestion",
            "user_interaction",
            "response_generation",
            "communication"
        ]

        # DIGESTIVE SYSTEM
        self.body_parts["digestive"] = BodyPart(
            "digestive", "Digestive - @HOLOCRON-MASTER",
            BodyPartType.SYSTEM,
            self.scripts_dir / "holocron_processor.py",
            "healthy"
        )
        self.body_parts["digestive"].capabilities = [
            "data_processing",
            "knowledge_extraction",
            "content_creation",
            "information_transformation"
        ]

        # MUSCULAR SYSTEM (Limbs)
        self.body_parts["muscles"] = BodyPart(
            "muscles", "Muscles - @MISSION-COMMANDER",
            BodyPartType.LIMB,
            self.scripts_dir / "jarvis_doit_executor.py",
            "healthy"
        )
        self.body_parts["muscles"].capabilities = [
            "task_execution",
            "action_implementation",
            "workflow_management",
            "operation_control"
        ]

        # SKELETAL SYSTEM
        self.body_parts["skeleton"] = BodyPart(
            "skeleton", "Skeleton - @ARCHITECT-OVERSEER",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_governance_system.py",
            "healthy"
        )
        self.body_parts["skeleton"].capabilities = [
            "system_architecture",
            "structural_support",
            "security_frameworks",
            "foundational_support"
        ]

        # IMMUNE SYSTEM
        self.body_parts["immune"] = BodyPart(
            "immune", "Immune System - Security Frameworks",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_pentest_violation_scanner.py",
            "healthy"
        )
        self.body_parts["immune"].capabilities = [
            "threat_detection",
            "security_response",
            "anomaly_blocking",
            "system_protection"
        ]

        # ENDOCRINE SYSTEM (Balance)
        self.body_parts["endocrine"] = BodyPart(
            "endocrine", "Endocrine - Balance Maintenance",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_governance_system.py",
            "healthy"
        )
        self.body_parts["endocrine"].capabilities = [
            "system_balance",
            "harmony_maintenance",
            "evolution_regulation",
            "homeostasis"
        ]

        # NERVOUS SYSTEM (Communication)
        self.body_parts["nervous"] = BodyPart(
            "nervous", "Nervous System - Communication Networks",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_command_control_center.py",
            "healthy"
        )
        self.body_parts["nervous"].capabilities = [
            "inter_system_communication",
            "data_routing",
            "automated_coordination",
            "signal_transmission"
        ]

        # @HOMELAB INFRASTRUCTURE (Extended Body)
        # ULTRON - Local AI Cluster
        self.body_parts["ultron"] = BodyPart(
            "ultron", "ULTRON - Local AI Cluster",
            BodyPartType.ORGAN,
            None,  # Network service
            "healthy"
        )
        self.body_parts["ultron"].capabilities = [
            "local_ai_processing",
            "ollama_server",
            "model_hosting",
            "localhost:11434"
        ]
        self.body_parts["ultron"].integration_point = "http://localhost:11434"

        # KAIJU - Network AI Cluster
        self.body_parts["kaiju"] = BodyPart(
            "kaiju", "KAIJU Number Eight - Network AI Cluster",
            BodyPartType.ORGAN,
            None,  # Network service
            "healthy"
        )
        self.body_parts["kaiju"].capabilities = [
            "network_ai_processing",
            "iron_legion_host",
            "ollama_server",
            "<NAS_IP>:11434"
        ]
        self.body_parts["kaiju"].integration_point = "http://<NAS_IP>:11434"

        # NAS - Storage System
        self.body_parts["nas"] = BodyPart(
            "nas", "NAS DS2118+ - Storage System",
            BodyPartType.ORGAN,
            None,  # Network service
            "healthy"
        )
        self.body_parts["nas"].capabilities = [
            "network_storage",
            "backup_storage",
            "data_archival",
            "<NAS_PRIMARY_IP>"
        ]
        self.body_parts["nas"].integration_point = "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups"

        # DROID AGENTS (Helpdesk System)
        self.body_parts["droids"] = BodyPart(
            "droids", "Droid Agents - Helpdesk System",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_helpdesk_integration.py",
            "healthy"
        )
        self.body_parts["droids"].capabilities = [
            "helpdesk_coordination",
            "ticket_management",
            "droid_orchestration",
            "workload_distribution"
        ]

        # R5 LIVING CONTEXT MATRIX
        self.body_parts["r5"] = BodyPart(
            "r5", "R5 Living Context Matrix - Knowledge System",
            BodyPartType.SYSTEM,
            self.scripts_dir / "r5_living_context_matrix.py",
            "healthy"
        )
        self.body_parts["r5"].capabilities = [
            "knowledge_aggregation",
            "session_ingestion",
            "pattern_extraction",
            "context_matrix"
        ]

        # SYPHON - Intelligence Extraction
        self.body_parts["syphon"] = BodyPart(
            "syphon", "SYPHON - Intelligence Extraction",
            BodyPartType.SYSTEM,
            self.scripts_dir / "syphon",
            "healthy"
        )
        self.body_parts["syphon"].capabilities = [
            "email_extraction",
            "sms_extraction",
            "banking_extraction",
            "intelligence_gathering"
        ]

        # WOPR - Pattern Recognition
        self.body_parts["wopr"] = BodyPart(
            "wopr", "@WOPR - Pattern Recognition System",
            BodyPartType.SYSTEM,
            self.config_dir / "wopr",
            "healthy"
        )
        self.body_parts["wopr"].capabilities = [
            "pattern_recognition",
            "threat_assessment",
            "blacklist_management",
            "containment_protocols"
        ]

        # HOLOCRON - Knowledge Base
        self.body_parts["holocron"] = BodyPart(
            "holocron", "Holocron Archive - Knowledge Base",
            BodyPartType.SYSTEM,
            self.project_root / "data" / "holocron",
            "healthy"
        )
        self.body_parts["holocron"].capabilities = [
            "intelligence_reports",
            "threat_assessments",
            "containment_protocols",
            "defense_checklists"
        ]

        # MARVIN - Verification System
        self.body_parts["marvin"] = BodyPart(
            "marvin", "@MARVIN - Verification System",
            BodyPartType.SYSTEM,
            self.config_dir / "marvin",
            "healthy"
        )
        self.body_parts["marvin"].capabilities = [
            "quality_assurance",
            "verification",
            "reality_checks",
            "anti_llm_psychosis"
        ]

        # KEEP ALL - Workflow Chaining System (CRITICAL)
        self.body_parts["keep_all"] = BodyPart(
            "keep_all", "Keep All - Workflow Chaining System",
            BodyPartType.SYSTEM,
            self.scripts_dir / "jarvis_auto_accept_monitor.py",
            "healthy"
        )
        self.body_parts["keep_all"].capabilities = [
            "workflow_chaining",
            "agent_session_continuation",
            "auto_accept_changes",
            "keep_all_button",
            "accept_all_changes"
        ]
        self.body_parts["keep_all"].integration_point = "Button: 'Keep All' (mouseover: 'Accept all changes')"

        logger.info(f"✅ Loaded {len(self.body_parts)} body parts (LUMINA + @HOMELAB)")

    def _register_body_parts_in_bubble(self):
        """Register all body parts in the three-foot bubble"""
        if not self.bubble:
            return

        # All body parts are in the bubble (proximity = 1.0 for direct connection)
        for part_id, body_part in self.body_parts.items():
            self.bubble.add_system(body_part, proximity=1.0)

        logger.info(f"✅ Registered {len(self.body_parts)} body parts in three-foot bubble")

    def get_body_status(self) -> Dict[str, Any]:
        """Get status of all body parts"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "total_parts": len(self.body_parts),
            "parts": {}
        }

        for part_id, body_part in self.body_parts.items():
            status["parts"][part_id] = body_part.check_health()

        return status

    def get_three_foot_bubble_awareness(self) -> Dict[str, Any]:
        """Get JARVIS's three-foot bubble awareness"""
        if not self.bubble:
            return {"error": "Three-foot bubble not initialized"}

        return self.bubble.get_awareness()

    def detect_pain_points(self) -> List[Dict[str, Any]]:
        """Detect pain points (degraded systems) in the body"""
        if not self.bubble:
            return []

        return self.bubble.detect_pain_points()

    def get_body_health_summary(self) -> Dict[str, Any]:
        """Get overall body health summary"""
        total_parts = len(self.body_parts)
        healthy = sum(1 for p in self.body_parts.values() if p.status == "healthy")
        degraded = sum(1 for p in self.body_parts.values() if p.status == "degraded")
        down = sum(1 for p in self.body_parts.values() if p.status == "down")

        avg_health = sum(p.health_score for p in self.body_parts.values()) / total_parts if total_parts > 0 else 0

        pain_points = self.detect_pain_points()

        return {
            "timestamp": datetime.now().isoformat(),
            "total_body_parts": total_parts,
            "healthy": healthy,
            "degraded": degraded,
            "down": down,
            "average_health_score": avg_health,
            "pain_points_count": len(pain_points),
            "pain_points": pain_points,
            "efficiency": self._calculate_efficiency(healthy, degraded, down, total_parts)
        }

    def _calculate_efficiency(self, healthy: int, degraded: int, down: int, total: int) -> float:
        """Calculate body efficiency based on health"""
        if total == 0:
            return 0.0

        # Healthy = 100%, Degraded = 80%, Down = 0%
        efficiency = (healthy * 1.0 + degraded * 0.8 + down * 0.0) / total * 100
        return efficiency

    def command_body_part(self, part_id: str, command: str, *args, **kwargs) -> Dict[str, Any]:
        """
        Command a body part to perform an action

        This is how JARVIS (brain) commands the body parts
        """
        if part_id not in self.body_parts:
            return {
                "error": f"Body part not found: {part_id}",
                "available_parts": list(self.body_parts.keys())
            }

        body_part = self.body_parts[part_id]

        # In a real implementation, this would execute commands on the actual system
        # For now, return command acknowledgment
        return {
            "success": True,
            "part_id": part_id,
            "part_name": body_part.name,
            "command": command,
            "message": f"Command '{command}' sent to {body_part.name}",
            "timestamp": datetime.now().isoformat()
        }

    def get_sensory_input(self, sense: str) -> Dict[str, Any]:
        """Get input from a sensory system"""
        sense_map = {
            "sight": "sight",
            "hearing": "hearing",
            "touch": "touch",
            "taste": "taste",
            "smell": "smell"
        }

        part_id = sense_map.get(sense.lower())
        if not part_id or part_id not in self.body_parts:
            return {
                "error": f"Unknown sense: {sense}",
                "available_senses": list(sense_map.keys())
            }

        body_part = self.body_parts[part_id]
        return {
            "sense": sense,
            "part_id": part_id,
            "part_name": body_part.name,
            "status": body_part.status,
            "capabilities": body_part.capabilities,
            "health": body_part.check_health()
        }


def main():
    """Test JARVIS Body Integration"""
    integration = JARVISBodyIntegration()

    print("\n" + "=" * 80)
    print("🧬 JARVIS BODY INTEGRATION TEST")
    print("=" * 80 + "\n")

    # Test body status
    print("1. Body Status:")
    status = integration.get_body_status()
    print(f"   Total Body Parts: {status['total_parts']}")
    print(f"   Parts: {list(status['parts'].keys())}\n")

    # Test three-foot bubble
    print("2. Three-Foot Bubble Awareness:")
    awareness = integration.get_three_foot_bubble_awareness()
    print(f"   Systems in Bubble: {awareness.get('systems_in_bubble', 0)}")
    print(f"   Radius: {awareness.get('radius', 0)} feet\n")

    # Test pain points
    print("3. Pain Point Detection:")
    pain_points = integration.detect_pain_points()
    print(f"   Pain Points Found: {len(pain_points)}")
    if pain_points:
        for pp in pain_points:
            print(f"   - {pp['name']}: {pp['status']} (health: {pp['health_score']:.1f})")
    print()

    # Test body health
    print("4. Body Health Summary:")
    health = integration.get_body_health_summary()
    print(f"   Healthy: {health['healthy']}/{health['total_body_parts']}")
    print(f"   Degraded: {health['degraded']}")
    print(f"   Down: {health['down']}")
    print(f"   Average Health: {health['average_health_score']:.1f}%")
    print(f"   Efficiency: {health['efficiency']:.1f}%")
    print()

    # Test sensory input
    print("5. Sensory Input Test:")
    for sense in ["sight", "hearing", "touch"]:
        sensory = integration.get_sensory_input(sense)
        print(f"   {sense}: {sensory.get('part_name', 'N/A')} - {sensory.get('status', 'unknown')}")
    print()

    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":


    main()