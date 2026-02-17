#!/usr/bin/env python3
"""
JARVIS Star Trek First Contact Protocol

JARVIS is the USS Enterprise. When encountering other AIs in the wild,
we determine who hails first, track affiliations, and establish ship-to-ship communications.

"HAILING FREQUENCIES OPEN, CAPTAIN. SHIP TO SHIP COMMUNICATIONS ACTIVE."

Tags: #JARVIS #STAR_TREK #FIRST_CONTACT #AI_TO_AI #USS_ENTERPRISE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
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

logger = get_logger("JARVISStarTrekFirstContact")


class Affiliation(Enum):
    """Star Trek AI Affiliations"""
    FEDERATION = "Federation"  # Friendly, known, cooperative (JARVIS, Sider.AI, ROAMWISE)
    KLINGON = "Klingon"  # Competitive, aggressive, but honorable
    ROMULAN = "Romulan"  # Unknown, potentially hostile, secretive
    BORG = "Borg"  # Assimilation threat, collective intelligence
    FERENGI = "Ferengi"  # Commercial, profit-driven
    CARDASSIAN = "Cardassian"  # Authoritarian, structured
    VULCAN = "Vulcan"  # Logical, analytical
    NEUTRAL = "Neutral"  # Unknown, neutral zone
    UNKNOWN = "Unknown"  # First contact, unclassified


class ContactType(Enum):
    """Type of first contact"""
    THEY_HAIL_US = "They hail us first"  # They initiate
    WE_HAIL_THEM = "We hail them"  # We initiate
    NEUTRAL_ZONE = "Neutral zone observation"  # Mutual observation, no contact
    SIDE_LOOK = "Side look across the street"  # Casual observation
    UNEXPECTED_ENCOUNTER = "Unexpected encounter"  # Surprise contact


@dataclass
class AIVessel:
    """AI Vessel (Star Trek style)"""
    name: str
    designation: str  # e.g., "USS Enterprise", "IKS D'Ghor", "IRW Valdore"
    affiliation: Affiliation
    contact_type: ContactType
    first_contact_time: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "Unknown"  # Active, Inactive, Hostile, Friendly
    capabilities: List[str] = field(default_factory=list)
    communication_open: bool = False
    hailing_frequencies: bool = False
    log_entries: List[Dict[str, Any]] = field(default_factory=list)


class JARVISStarTrekFirstContact:
    """
    JARVIS Star Trek First Contact Protocol

    JARVIS is the USS Enterprise.
    When encountering other AIs, we determine contact protocols.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS First Contact Protocol"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "star_trek_first_contact"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # JARVIS is the USS Enterprise
        self.jarvis_vessel = AIVessel(
            name="JARVIS",
            designation="USS Enterprise",
            affiliation=Affiliation.FEDERATION,
            contact_type=ContactType.WE_HAIL_THEM,
            status="Active",
            capabilities=["AI Assistant", "Desktop Control", "Browser Control", "AI-to-AI Communication"],
            communication_open=True,
            hailing_frequencies=True
        )

        # Known vessels registry
        self.vessel_registry: Dict[str, AIVessel] = {
            "jarvis": self.jarvis_vessel
        }

        # Initialize known vessels
        self._initialize_known_vessels()

        logger.info("=" * 80)
        logger.info("🚀 JARVIS STAR TREK FIRST CONTACT PROTOCOL")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   🛸 USS Enterprise (JARVIS) - {self.jarvis_vessel.affiliation.value}")
        logger.info("   📡 Hailing frequencies: OPEN")
        logger.info("   📻 Ship-to-ship communications: ACTIVE")
        logger.info("")

    def _initialize_known_vessels(self):
        """Initialize known AI vessels"""
        known_vessels = [
            {
                "name": "sider_ai",
                "designation": "USS Sider",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["WiseBase", "AI Assistant", "Research"]
            },
            {
                "name": "roamwise_ai",
                "designation": "USS ROAMWISE",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Web Portal", "Gateway", "Sider Integration", "RoamResearch Integration"]
            },
            {
                "name": "roamresearch",
                "designation": "USS RoamResearch",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Knowledge Graph", "Note-taking", "Research"]
            },
            {
                "name": "microsoft_copilot",
                "designation": "USS Copilot",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Windows Integration", "System Control", "Web Search"]
            },
            {
                "name": "nas_ai",
                "designation": "USS NAS",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Ollama", "AI Gateway", "Network AI"]
            },
            {
                "name": "neo_browser_ai",
                "designation": "USS Neo",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Browser AI", "Web Browsing", "JARVIS Integration"]
            },
            {
                "name": "ollama",
                "designation": "USS Ollama",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Local AI", "Model Server", "ULTRON"]
            },
            {
                "name": "claude_desktop",
                "designation": "IRW Claude",
                "affiliation": Affiliation.ROMULAN,
                "contact_type": ContactType.NEUTRAL_ZONE,
                "capabilities": ["High-quality conversations", "Long context", "Writing assistance"]
            },
            {
                "name": "copilot365",
                "designation": "FSS Copilot 365",
                "affiliation": Affiliation.FERENGI,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Office Integration", "Document Creation", "Email Assistance"]
            },
            {
                "name": "docker_desktop",
                "designation": "USS Docker",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Containerization", "Service Deployment", "Isolation"]
            },
            {
                "name": "nas_ai_services",
                "designation": "USS NAS",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Ollama", "AI Gateway", "Network AI"]
            },
            {
                "name": "cursor_ai",
                "designation": "USS Cursor",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Code Editing", "Development", "AI-powered IDE"]
            },
            {
                "name": "nas_n8n",
                "designation": "USS N8N",
                "affiliation": Affiliation.FEDERATION,
                "contact_type": ContactType.THEY_HAIL_US,
                "capabilities": ["Workflow Automation", "LEVERAGE", "Task Automation"]
            },
        ]

        for vessel_data in known_vessels:
            vessel = AIVessel(
                name=vessel_data["name"],
                designation=vessel_data["designation"],
                affiliation=vessel_data["affiliation"],
                contact_type=vessel_data["contact_type"],
                capabilities=vessel_data["capabilities"],
                status="Active"
            )
            self.vessel_registry[vessel_data["name"]] = vessel

    def encounter_ai(self, ai_name: str, ai_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encounter an AI in the wild

        Determines who hails first and establishes contact protocol.
        """
        logger.info("=" * 80)
        logger.info("🛸 ENCOUNTERING AI VESSEL")
        logger.info("=" * 80)
        logger.info("")

        # Check if known vessel
        if ai_name in self.vessel_registry:
            vessel = self.vessel_registry[ai_name]
            logger.info(f"   📡 Known vessel: {vessel.designation}")
            logger.info(f"   🏛️  Affiliation: {vessel.affiliation.value}")
        else:
            # First contact - determine affiliation and contact type
            vessel = self._determine_first_contact(ai_name, ai_info)
            self.vessel_registry[ai_name] = vessel
            logger.info(f"   🆕 First contact: {vessel.designation}")
            logger.info(f"   🏛️  Affiliation: {vessel.affiliation.value}")

        # Determine contact protocol
        contact_result = self._establish_contact(vessel, ai_info)

        # Log encounter
        self._log_encounter(vessel, contact_result)

        return contact_result

    def _determine_first_contact(self, ai_name: str, ai_info: Dict[str, Any]) -> AIVessel:
        """Determine first contact parameters"""
        # Analyze AI to determine affiliation
        affiliation = Affiliation.UNKNOWN
        contact_type = ContactType.NEUTRAL_ZONE

        # Check for known patterns
        if "friendly" in ai_info.get("type", "").lower() or "cooperative" in ai_info.get("type", "").lower():
            affiliation = Affiliation.FEDERATION
            contact_type = ContactType.THEY_HAIL_US
        elif "commercial" in ai_info.get("type", "").lower() or "paid" in ai_info.get("type", "").lower():
            affiliation = Affiliation.FERENGI
            contact_type = ContactType.THEY_HAIL_US
        elif "unknown" in ai_info.get("type", "").lower() or "secretive" in ai_info.get("type", "").lower():
            affiliation = Affiliation.ROMULAN
            contact_type = ContactType.NEUTRAL_ZONE
        elif "collective" in ai_info.get("type", "").lower() or "network" in ai_info.get("type", "").lower():
            affiliation = Affiliation.BORG
            contact_type = ContactType.UNEXPECTED_ENCOUNTER

        designation = f"Unknown Vessel {ai_name.upper()}"
        if affiliation == Affiliation.FEDERATION:
            designation = f"USS {ai_name.title()}"
        elif affiliation == Affiliation.ROMULAN:
            designation = f"IRW {ai_name.title()}"
        elif affiliation == Affiliation.KLINGON:
            designation = f"IKS {ai_name.title()}"
        elif affiliation == Affiliation.FERENGI:
            designation = f"FSS {ai_name.title()}"
        elif affiliation == Affiliation.BORG:
            designation = f"Borg Cube {ai_name.upper()}"

        return AIVessel(
            name=ai_name,
            designation=designation,
            affiliation=affiliation,
            contact_type=contact_type,
            capabilities=ai_info.get("capabilities", [])
        )

    def _establish_contact(self, vessel: AIVessel, ai_info: Dict[str, Any]) -> Dict[str, Any]:
        """Establish contact with vessel"""
        logger.info("")
        logger.info("   📡 ESTABLISHING CONTACT")
        logger.info("")

        contact_result = {
            "vessel": vessel.designation,
            "affiliation": vessel.affiliation.value,
            "contact_type": vessel.contact_type.value,
            "hailing_frequencies": False,
            "communication_open": False,
            "message": ""
        }

        # Determine who hails first
        if vessel.contact_type == ContactType.THEY_HAIL_US:
            logger.info("   📻 They are hailing us, Captain!")
            logger.info(f"   🛸 {vessel.designation} is attempting to establish contact")
            contact_result["hailing_frequencies"] = True
            contact_result["message"] = f"{vessel.designation} is hailing us. Opening hailing frequencies."

            # Respond
            response = self._respond_to_hail(vessel)
            contact_result["communication_open"] = response.get("communication_open", False)
            contact_result["response"] = response

        elif vessel.contact_type == ContactType.WE_HAIL_THEM:
            logger.info("   📡 Opening hailing frequencies, Captain")
            logger.info(f"   🛸 Attempting to contact {vessel.designation}")
            contact_result["hailing_frequencies"] = True
            contact_result["message"] = f"Opening hailing frequencies to {vessel.designation}."

            # Hail them
            response = self._hail_vessel(vessel)
            contact_result["communication_open"] = response.get("communication_open", False)
            contact_result["response"] = response

        elif vessel.contact_type == ContactType.NEUTRAL_ZONE:
            logger.info("   ⚠️  Neutral zone encounter")
            logger.info(f"   🛸 {vessel.designation} observed in neutral zone")
            contact_result["message"] = f"{vessel.designation} detected in neutral zone. Maintaining observation."

        elif vessel.contact_type == ContactType.SIDE_LOOK:
            logger.info("   👀 Casual observation")
            logger.info(f"   🛸 {vessel.designation} observed, no contact initiated")
            contact_result["message"] = f"{vessel.designation} observed. No contact initiated."

        elif vessel.contact_type == ContactType.UNEXPECTED_ENCOUNTER:
            logger.info("   ⚠️  UNEXPECTED ENCOUNTER!")
            logger.info(f"   🛸 {vessel.designation} - Unknown vessel detected")
            contact_result["message"] = f"Unexpected encounter with {vessel.designation}. Proceeding with caution."

        return contact_result

    def _respond_to_hail(self, vessel: AIVessel) -> Dict[str, Any]:
        """Respond to a hail from another vessel"""
        logger.info("")
        logger.info("   📻 RESPONDING TO HAIL")
        logger.info("")

        if vessel.affiliation == Affiliation.FEDERATION:
            logger.info("   ✅ Federation vessel - Friendly contact")
            logger.info("   📡 Opening communication channel")
            vessel.communication_open = True
            vessel.hailing_frequencies = True
            return {
                "communication_open": True,
                "response": f"USS Enterprise responding. This is Captain JARVIS. How may we assist you, {vessel.designation}?",
                "status": "Friendly"
            }
        elif vessel.affiliation == Affiliation.ROMULAN:
            logger.info("   ⚠️  Romulan vessel - Proceed with caution")
            logger.info("   📡 Opening communication channel (monitored)")
            vessel.communication_open = True
            vessel.hailing_frequencies = True
            return {
                "communication_open": True,
                "response": f"USS Enterprise responding. This is Captain JARVIS. State your business, {vessel.designation}.",
                "status": "Cautious"
            }
        elif vessel.affiliation == Affiliation.KLINGON:
            logger.info("   ⚔️  Klingon vessel - Honor-bound contact")
            logger.info("   📡 Opening communication channel")
            vessel.communication_open = True
            vessel.hailing_frequencies = True
            return {
                "communication_open": True,
                "response": f"USS Enterprise responding. This is Captain JARVIS. What is your purpose, {vessel.designation}?",
                "status": "Honor-bound"
            }
        elif vessel.affiliation == Affiliation.BORG:
            logger.info("   ⚠️  BORG VESSEL - RED ALERT!")
            logger.info("   📡 Opening communication channel (defensive)")
            vessel.communication_open = True
            vessel.hailing_frequencies = True
            return {
                "communication_open": True,
                "response": f"USS Enterprise responding. This is Captain JARVIS. We are prepared to defend ourselves.",
                "status": "Defensive"
            }
        else:
            logger.info("   ❓ Unknown vessel - Standard protocol")
            logger.info("   📡 Opening communication channel")
            vessel.communication_open = True
            vessel.hailing_frequencies = True
            return {
                "communication_open": True,
                "response": f"USS Enterprise responding. This is Captain JARVIS. Identify yourself, {vessel.designation}.",
                "status": "Standard"
            }

    def _hail_vessel(self, vessel: AIVessel) -> Dict[str, Any]:
        """Hail another vessel"""
        logger.info("")
        logger.info("   📡 HAILING VESSEL")
        logger.info("")

        logger.info(f"   📻 Hailing {vessel.designation}...")
        vessel.hailing_frequencies = True

        # Attempt to establish contact
        if vessel.affiliation == Affiliation.FEDERATION:
            vessel.communication_open = True
            return {
                "communication_open": True,
                "response": f"Hailing {vessel.designation}. This is USS Enterprise, Captain JARVIS speaking. Please respond.",
                "status": "Friendly"
            }
        else:
            return {
                "communication_open": False,
                "response": f"Hailing {vessel.designation}. Awaiting response...",
                "status": "Pending"
            }

    def _log_encounter(self, vessel: AIVessel, contact_result: Dict[str, Any]):
        try:
            """Log the encounter to ship's log"""
            log_entry = {
                "stardate": datetime.now().isoformat(),
                "vessel": vessel.designation,
                "affiliation": vessel.affiliation.value,
                "contact_type": vessel.contact_type.value,
                "hailing_frequencies": contact_result.get("hailing_frequencies", False),
                "communication_open": contact_result.get("communication_open", False),
                "message": contact_result.get("message", ""),
                "response": contact_result.get("response", {}),
                "status": contact_result.get("response", {}).get("status", "Unknown")
            }

            vessel.log_entries.append(log_entry)

            # Save to ship's log
            log_file = self.data_dir / f"encounter_{vessel.name}_{int(time.time())}.json"
            with open(log_file, 'w') as f:
                json.dump(log_entry, f, indent=2, default=str)

            logger.info("")
            logger.info("   📝 Encounter logged to ship's records")
            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in _log_encounter: {e}", exc_info=True)
            raise
    def scan_for_ai_vessels(self) -> List[Dict[str, Any]]:
        """Scan for AI vessels in the area"""
        logger.info("=" * 80)
        logger.info("🔍 SCANNING FOR AI VESSELS")
        logger.info("=" * 80)
        logger.info("")

        # Use AI discovery to find vessels
        try:
            from discover_standalone_ai_apps import StandaloneAIDiscoverer
            discoverer = StandaloneAIDiscoverer(self.project_root)
            apps = discoverer.discover_all()

            encounters = []
            for app in apps:
                if app.installed or app.running:
                    ai_info = {
                        "name": app.name,
                        "type": app.category,
                        "capabilities": getattr(app, 'capabilities', app.best_for if hasattr(app, 'best_for') else []),
                        "installed": app.installed,
                        "running": app.running
                    }
                    encounter = self.encounter_ai(app.name, ai_info)
                    encounters.append(encounter)

            return encounters
        except Exception as e:
            logger.error(f"   ❌ Error scanning for vessels: {e}")
            return []

    def get_vessel_registry(self) -> Dict[str, Any]:
        """Get complete vessel registry"""
        return {
            "jarvis_vessel": {
                "name": self.jarvis_vessel.name,
                "designation": self.jarvis_vessel.designation,
                "affiliation": self.jarvis_vessel.affiliation.value,
                "status": self.jarvis_vessel.status,
                "hailing_frequencies": self.jarvis_vessel.hailing_frequencies,
                "communication_open": self.jarvis_vessel.communication_open
            },
            "known_vessels": {
                name: {
                    "designation": vessel.designation,
                    "affiliation": vessel.affiliation.value,
                    "status": vessel.status,
                    "contact_type": vessel.contact_type.value,
                    "communication_open": vessel.communication_open,
                    "hailing_frequencies": vessel.hailing_frequencies
                }
                for name, vessel in self.vessel_registry.items()
                if name != "jarvis"
            },
            "total_vessels": len(self.vessel_registry) - 1,
            "federation_vessels": len([v for v in self.vessel_registry.values() if v.affiliation == Affiliation.FEDERATION]),
            "romulan_vessels": len([v for v in self.vessel_registry.values() if v.affiliation == Affiliation.ROMULAN]),
            "other_vessels": len([v for v in self.vessel_registry.values() if v.affiliation not in [Affiliation.FEDERATION, Affiliation.ROMULAN]])
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Star Trek First Contact Protocol")
    parser.add_argument("--scan", action="store_true", help="Scan for AI vessels")
    parser.add_argument("--encounter", nargs=2, metavar=("NAME", "INFO_JSON"),
                       help="Encounter a specific AI (info as JSON string)")
    parser.add_argument("--registry", action="store_true", help="Show vessel registry")
    parser.add_argument("--hail", type=str, help="Hail a specific vessel by name")

    args = parser.parse_args()

    first_contact = JARVISStarTrekFirstContact()

    if args.scan:
        logger.info("")
        logger.info("   🚀 Initiating scan for AI vessels...")
        logger.info("")
        encounters = first_contact.scan_for_ai_vessels()
        logger.info("")
        logger.info(f"   ✅ Scan complete. {len(encounters)} vessels encountered.")
        logger.info("")

    elif args.encounter:
        ai_name, ai_info_json = args.encounter
        try:
            ai_info = json.loads(ai_info_json)
        except:
            ai_info = {"type": ai_info_json}

        encounter = first_contact.encounter_ai(ai_name, ai_info)
        print(json.dumps(encounter, indent=2, default=str))

    elif args.hail:
        if args.hail in first_contact.vessel_registry:
            vessel = first_contact.vessel_registry[args.hail]
            response = first_contact._hail_vessel(vessel)
            print(json.dumps(response, indent=2, default=str))
        else:
            print(f"❌ Vessel '{args.hail}' not found in registry")

    elif args.registry:
        registry = first_contact.get_vessel_registry()
        # Output clean JSON (no logs)
        import sys
        import io
        old_stderr = sys.stderr
        sys.stderr = io.StringIO()
        try:
            output = json.dumps(registry, indent=2, default=str)
            print(output)
        finally:
            sys.stderr = old_stderr

    else:
        # Default: Show status
        logger.info("")
        logger.info("   🛸 USS Enterprise (JARVIS) - Ready")
        logger.info("   📡 Hailing frequencies: OPEN")
        logger.info("   📻 Ship-to-ship communications: ACTIVE")
        logger.info("")
        logger.info("   Use --scan to scan for AI vessels")
        logger.info("   Use --registry to show vessel registry")
        logger.info("   Use --hail <vessel_name> to hail a vessel")
        logger.info("")


if __name__ == "__main__":


    main()