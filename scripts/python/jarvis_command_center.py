#!/usr/bin/env python3
"""
JARVIS Command Center - Brain Control Interface

JARVIS (the brain) commands all LUMINA body parts from this central command center.
This is the interface where JARVIS can see and control everything in its three-foot bubble.

Tags: #JARVIS #COMMAND_CENTER #BRAIN_CONTROL #THREE_FOOT_BUBBLE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

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

logger = get_logger("JARVISCommandCenter")


class JARVISCommandCenter:
    """
    JARVIS Command Center

    The brain's control interface for all body parts.
    JARVIS uses this to:
    - Monitor all systems in three-foot bubble
    - Command body parts
    - Detect pain points
    - Maintain body health
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root

        # Import JARVIS core
        try:
            from jarvis_enhanced_core import JarvisEnhancedCore
            self.jarvis = JarvisEnhancedCore(project_root=project_root)
        except ImportError:
            logger.error("❌ Could not import JARVIS enhanced core")
            self.jarvis = None

        logger.info("=" * 80)
        logger.info("🧠 JARVIS COMMAND CENTER INITIALIZED")
        logger.info("=" * 80)
        if self.jarvis:
            logger.info("   ✅ Connected to JARVIS brain")
            if self.jarvis.body_integration:
                logger.info("   ✅ Connected to LUMINA body")
                logger.info(f"   ✅ Body parts: {len(self.jarvis.body_integration.body_parts)}")
                logger.info(f"   ✅ Three-foot bubble: {len(self.jarvis.body_integration.bubble.monitored_systems) if self.jarvis.body_integration.bubble else 0} systems")
        logger.info("=" * 80)

    def get_full_status(self) -> Dict[str, Any]:
        """Get full status of JARVIS and body"""
        if not self.jarvis:
            return {"error": "JARVIS not available"}

        # Get JARVIS status
        jarvis_status = self.jarvis.execute_capability("system_status")

        # Get body status
        body_status = {}
        if self.jarvis.body_integration:
            body_status = self.jarvis.body_integration.get_body_status()
            body_health = self.jarvis.body_integration.get_body_health_summary()
            bubble_awareness = self.jarvis.body_integration.get_three_foot_bubble_awareness()
            pain_points = self.jarvis.body_integration.detect_pain_points()
        else:
            body_status = {"error": "Body integration not available"}
            body_health = {}
            bubble_awareness = {}
            pain_points = []

        return {
            "timestamp": datetime.now().isoformat(),
            "jarvis": {
                "role": jarvis_status.get("role", "unknown"),
                "status": jarvis_status.get("status", "unknown"),
                "experts_available": jarvis_status.get("experts_available", 0),
                "capabilities": jarvis_status.get("capabilities", 0)
            },
            "body": {
                "status": body_status,
                "health": body_health,
                "three_foot_bubble": bubble_awareness,
                "pain_points": pain_points
            }
        }

    def command_body_part(self, part_id: str, command: str) -> Dict[str, Any]:
        """Command a body part through JARVIS"""
        if not self.jarvis:
            return {"error": "JARVIS not available"}

        return self.jarvis.execute_capability("command_body", part_id, command)

    def get_sensory_input(self, sense: str) -> Dict[str, Any]:
        """Get input from a sensory system"""
        if not self.jarvis:
            return {"error": "JARVIS not available"}

        return self.jarvis.execute_capability("sensory_input", sense)

    def get_three_foot_bubble_status(self) -> Dict[str, Any]:
        """Get three-foot bubble awareness status"""
        if not self.jarvis or not self.jarvis.body_integration:
            return {"error": "Body integration not available"}

        return self.jarvis.body_integration.get_three_foot_bubble_awareness()

    def detect_pain_points(self) -> List[Dict[str, Any]]:
        """Detect pain points in the body"""
        if not self.jarvis or not self.jarvis.body_integration:
            return []

        return self.jarvis.body_integration.detect_pain_points()

    def get_body_health(self) -> Dict[str, Any]:
        """Get body health summary"""
        if not self.jarvis or not self.jarvis.body_integration:
            return {"error": "Body integration not available"}

        return self.jarvis.body_integration.get_body_health_summary()

    def print_command_center_dashboard(self):
        """Print command center dashboard"""
        print("\n" + "=" * 80)
        print("🧠 JARVIS COMMAND CENTER DASHBOARD")
        print("=" * 80 + "\n")

        status = self.get_full_status()

        # JARVIS Status
        jarvis = status.get("jarvis", {})
        print("🧠 JARVIS (Brain):")
        print(f"   Role: {jarvis.get('role', 'unknown')}")
        print(f"   Status: {jarvis.get('status', 'unknown')}")
        print(f"   Experts Available: {jarvis.get('experts_available', 0)}")
        print(f"   Capabilities: {jarvis.get('capabilities', 0)}")
        print()

        # Body Status
        body = status.get("body", {})
        health = body.get("health", {})
        if health:
            print("🧬 LUMINA BODY:")
            print(f"   Total Body Parts: {health.get('total_body_parts', 0)}")
            print(f"   Healthy: {health.get('healthy', 0)}")
            print(f"   Degraded: {health.get('degraded', 0)}")
            print(f"   Down: {health.get('down', 0)}")
            print(f"   Average Health: {health.get('average_health_score', 0):.1f}%")
            print(f"   Efficiency: {health.get('efficiency', 0):.1f}%")
            print()

        # Three-Foot Bubble
        bubble = body.get("three_foot_bubble", {})
        if bubble and "systems_in_bubble" in bubble:
            print("🌀 THREE-FOOT BUBBLE:")
            print(f"   Systems in Bubble: {bubble.get('systems_in_bubble', 0)}")
            print(f"   Radius: {bubble.get('radius', 0)} feet")
            print()

        # Pain Points
        pain_points = body.get("pain_points", [])
        if pain_points:
            print("⚠️  PAIN POINTS DETECTED:")
            for pp in pain_points:
                print(f"   - {pp.get('name', 'Unknown')}: {pp.get('status', 'unknown')} "
                      f"(health: {pp.get('health_score', 0):.1f}%, "
                      f"severity: {pp.get('severity', 'unknown')})")
            print()
        else:
            print("✅ NO PAIN POINTS - All systems healthy")
            print()

        # Sensory Systems
        print("👁️  SENSORY SYSTEMS:")
        senses = ["sight", "hearing", "touch", "taste", "smell"]
        for sense in senses:
            sensory = self.get_sensory_input(sense)
            if "error" not in sensory:
                status_icon = "✅" if sensory.get("status") == "healthy" else "⚠️"
                print(f"   {status_icon} {sense.title()}: {sensory.get('part_name', 'N/A')} - {sensory.get('status', 'unknown')}")
        print()

        print("=" * 80)
        print("✅ COMMAND CENTER READY")
        print("=" * 80)
        print()
        print("Commands:")
        print("  body_status - Get status of all body parts")
        print("  body_health - Get body health summary")
        print("  three_foot_bubble - Get bubble awareness")
        print("  pain_points - Detect pain points")
        print("  command_body <part> <command> - Command a body part")
        print("  sensory_input <sense> - Get sensory input")
        print()


def main():
    """Main entry point"""
    command_center = JARVISCommandCenter()
    command_center.print_command_center_dashboard()


if __name__ == "__main__":


    main()