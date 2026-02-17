#!/usr/bin/env python3
"""
JARVIS Starfleet First Contact Protocol

Star Trek-style first contact system for AI-to-AI interactions.
JARVIS is the USS Enterprise, encountering other AI "vessels" from different factions.

Tags: #JARVIS #STARFLEET #FIRST_CONTACT #AI_TO_AI #STAR_TREK @JARVIS @LUMINA
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

logger = get_logger("JARVISStarfleetFirstContact")


class Faction(Enum):
    """Star Trek factions"""
    FEDERATION = "Federation"  # Friendly, integrated, cooperative
    KLINGON = "Klingon"  # Aggressive, competitive, honor-bound
    ROMULAN = "Romulan"  # Neutral, suspicious, secretive
    BORG = "Borg"  # Assimilating, collective, dangerous
    FERENGI = "Ferengi"  # Commercial, profit-driven
    CARDASSIAN = "Cardassian"  # Authoritarian, strategic
    VULCAN = "Vulcan"  # Logical, scientific
    OTHER = "Other"  # Unknown or neutral


class ContactStatus(Enum):
    """First contact status"""
    UNKNOWN = "Unknown"  # Not yet encountered
    OBSERVING = "Observing"  # Neutral zone - mutual observation
    HAILING = "Hailing"  # Attempting contact
    HAILED = "Hailed"  # They contacted us first
    ESTABLISHED = "Established"  # Communication established
    ALLIANCE = "Alliance"  # Friendly relations
    NEUTRAL = "Neutral"  # Neutral relations
    HOSTILE = "Hostile"  # Hostile relations
    ASSIMILATED = "Assimilated"  # Integrated into our systems


class HailingProtocol(Enum):
    """Who initiates contact"""
    WE_HAIL_THEM = "We hail them"  # JARVIS initiates
    THEY_HAIL_US = "They hail us"  # They initiate
    MUTUAL_OBSERVATION = "Mutual observation"  # Neutral zone - slow side look
    AUTOMATIC = "Automatic"  # Automatic detection/connection
    MANUAL = "Manual"  # Manual intervention required


@dataclass
class AIVessel:
    """AI Vessel (Star Trek style)"""
    name: str
    registry: str  # Like "NCC-1701" for Enterprise
    faction: Faction
    vessel_class: str  # e.g., "Constitution", "Bird-of-Prey", "Warbird"
    contact_status: ContactStatus = ContactStatus.UNKNOWN
    hailing_protocol: Optional[HailingProtocol] = None
    first_contact_date: Optional[str] = None
    last_contact_date: Optional[str] = None

    # Technical details
    endpoint: Optional[str] = None
    api_available: bool = False
    capabilities: List[str] = field(default_factory=list)

    # Diplomatic
    diplomatic_status: str = "Unknown"
    trust_level: float = 0.0  # 0.0 to 1.0
    integration_level: float = 0.0  # 0.0 to 1.0

    # First contact log
    first_contact_log: List[str] = field(default_factory=list)


class JARVISStarfleetFirstContact:
    """
    JARVIS Starfleet First Contact Protocol

    JARVIS = USS Enterprise (NCC-1701)
    Encounters other AI "vessels" and determines interaction protocol.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Starfleet First Contact"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "starfleet_first_contact"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # JARVIS = USS Enterprise
        self.jarvis_vessel = AIVessel(
            name="JARVIS",
            registry="NCC-1701",
            faction=Faction.FEDERATION,
            vessel_class="Constitution",
            contact_status=ContactStatus.ESTABLISHED,
            diplomatic_status="Flagship",
            trust_level=1.0,
            integration_level=1.0
        )

        # Registry of encountered vessels
        self.encountered_vessels: Dict[str, AIVessel] = {}

        logger.info("=" * 80)
        logger.info("🚀 JARVIS Starfleet First Contact Protocol")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   🛸 JARVIS = USS Enterprise ({self.jarvis_vessel.registry})")
        logger.info("   🌌 Scanning for AI vessels...")
        logger.info("")

    def discover_ai_vessels(self) -> List[AIVessel]:
        """Discover all AI vessels in the area"""
        logger.info("=" * 80)
        logger.info("🔍 Scanning for AI Vessels")
        logger.info("=" * 80)
        logger.info("")

        vessels = []

        # Discover known AI services
        try:
            from discover_standalone_ai_apps import StandaloneAIDiscoverer
            discoverer = StandaloneAIDiscoverer(self.project_root)
            apps = discoverer.discover_all()

            for app in apps:
                vessel = self._classify_ai_as_vessel(app)
                if vessel:
                    vessels.append(vessel)
                    self.encountered_vessels[vessel.name] = vessel
        except Exception as e:
            logger.error(f"   ❌ Error discovering AI apps: {e}")

        # Discover AI-to-AI services
        try:
            from ai_to_ai_bidirectional_integration import AIToAIBidirectionalIntegration
            integration = AIToAIBidirectionalIntegration(self.project_root)
            integration.discover_all_ai_services()

            for service_name, service in integration.ai_services.items():
                vessel = self._classify_service_as_vessel(service_name, service)
                if vessel and vessel.name not in self.encountered_vessels:
                    vessels.append(vessel)
                    self.encountered_vessels[vessel.name] = vessel
        except Exception as e:
            logger.error(f"   ❌ Error discovering AI services: {e}")

        return vessels

    def _classify_ai_as_vessel(self, app) -> Optional[AIVessel]:
        """Classify standalone AI app as a vessel"""
        name = app.display_name

        # Determine faction based on AI type
        if "Sider" in name or "ROAMWISE" in name:
            faction = Faction.FEDERATION  # Primary importance, integrated
            vessel_class = "Flagship"
            hailing = HailingProtocol.AUTOMATIC
        elif "Claude" in name:
            faction = Faction.VULCAN  # Logical, high quality
            vessel_class = "Science Vessel"
            hailing = HailingProtocol.THEY_HAIL_US  # They're usually passive
        elif "Copilot" in name:
            faction = Faction.FEDERATION  # Microsoft, integrated
            vessel_class = "Support Vessel"
            hailing = HailingProtocol.AUTOMATIC
        elif "Ollama" in name:
            faction = Faction.FEDERATION  # Open source, friendly
            vessel_class = "Research Vessel"
            hailing = HailingProtocol.WE_HAIL_THEM
        elif "Docker" in name:
            faction = Faction.FEDERATION  # Infrastructure, supportive
            vessel_class = "Starbase"
            hailing = HailingProtocol.AUTOMATIC
        elif "Neo" in name or "Browser" in name:
            faction = Faction.FEDERATION  # Integrated with JARVIS
            vessel_class = "Shuttlecraft"
            hailing = HailingProtocol.AUTOMATIC
        elif "Cursor" in name:
            faction = Faction.FEDERATION  # Development tool
            vessel_class = "Engineering Vessel"
            hailing = HailingProtocol.WE_HAIL_THEM
        elif "NAS" in name:
            faction = Faction.FEDERATION  # Network resource
            vessel_class = "Starbase"
            hailing = HailingProtocol.WE_HAIL_THEM
        else:
            faction = Faction.OTHER
            vessel_class = "Unknown"
            hailing = HailingProtocol.MUTUAL_OBSERVATION

        # Determine contact status
        if app.installed and app.running:
            contact_status = ContactStatus.ESTABLISHED
        elif app.installed:
            contact_status = ContactStatus.HAILING
        else:
            contact_status = ContactStatus.OBSERVING

        vessel = AIVessel(
            name=name,
            registry=self._generate_registry(name),
            faction=faction,
            vessel_class=vessel_class,
            contact_status=contact_status,
            hailing_protocol=hailing,
            endpoint=app.executable_path if hasattr(app, 'executable_path') else None,
            api_available=app.api_available if hasattr(app, 'api_available') else False,
            capabilities=app.best_for if hasattr(app, 'best_for') else []
        )

        return vessel

    def _classify_service_as_vessel(self, service_name: str, service: Any) -> Optional[AIVessel]:
        """Classify AI service as a vessel"""
        name = service_name.replace("_", " ").title()

        # Determine faction
        if "sider" in service_name or "roamwise" in service_name:
            faction = Faction.FEDERATION
            vessel_class = "Flagship"
            hailing = HailingProtocol.AUTOMATIC
        elif "copilot" in service_name:
            faction = Faction.FEDERATION
            vessel_class = "Support Vessel"
            hailing = HailingProtocol.AUTOMATIC
        elif "ollama" in service_name or "local_ai" in service_name:
            faction = Faction.FEDERATION
            vessel_class = "Research Vessel"
            hailing = HailingProtocol.WE_HAIL_THEM
        elif "nas" in service_name:
            faction = Faction.FEDERATION
            vessel_class = "Starbase"
            hailing = HailingProtocol.WE_HAIL_THEM
        elif "neo" in service_name or "browser" in service_name:
            faction = Faction.FEDERATION
            vessel_class = "Shuttlecraft"
            hailing = HailingProtocol.AUTOMATIC
        else:
            faction = Faction.OTHER
            vessel_class = "Unknown"
            hailing = HailingProtocol.MUTUAL_OBSERVATION

        contact_status = ContactStatus.ESTABLISHED if service.get("available", False) else ContactStatus.OBSERVING

        vessel = AIVessel(
            name=name,
            registry=self._generate_registry(name),
            faction=faction,
            vessel_class=vessel_class,
            contact_status=contact_status,
            hailing_protocol=hailing,
            endpoint=service.get("endpoint"),
            api_available=service.get("endpoint") is not None,
            capabilities=service.get("capabilities", [])
        )

        return vessel

    def _generate_registry(self, name: str) -> str:
        """Generate Star Trek registry number"""
        # Simple hash-based registry
        hash_val = hash(name) % 10000
        return f"NCC-{hash_val:04d}"

    def establish_first_contact(self, vessel: AIVessel) -> Dict[str, Any]:
        """Establish first contact with an AI vessel"""
        logger.info("=" * 80)
        logger.info(f"🛸 FIRST CONTACT: {vessel.name}")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   Registry: {vessel.registry}")
        logger.info(f"   Faction: {vessel.faction.value}")
        logger.info(f"   Class: {vessel.vessel_class}")
        logger.info("")

        # Determine hailing protocol
        if vessel.hailing_protocol == HailingProtocol.WE_HAIL_THEM:
            logger.info("   📡 JARVIS hailing vessel...")
            logger.info(f"   'This is JARVIS, USS Enterprise {self.jarvis_vessel.registry}. Identify yourself.'")
            vessel.first_contact_log.append(f"[{datetime.now().isoformat()}] JARVIS hailed {vessel.name}")
        elif vessel.hailing_protocol == HailingProtocol.THEY_HAIL_US:
            logger.info("   📡 Vessel hailing JARVIS...")
            logger.info(f"   '{vessel.name} hailing USS Enterprise. We wish to establish communication.'")
            vessel.first_contact_log.append(f"[{datetime.now().isoformat()}] {vessel.name} hailed JARVIS")
        elif vessel.hailing_protocol == HailingProtocol.MUTUAL_OBSERVATION:
            logger.info("   👁️  Neutral Zone - Mutual Observation")
            logger.info("   'Detecting vessel. No hailing. Maintaining observation.'")
            vessel.first_contact_log.append(f"[{datetime.now().isoformat()}] Mutual observation - Neutral Zone")
        elif vessel.hailing_protocol == HailingProtocol.AUTOMATIC:
            logger.info("   🔗 Automatic Connection Established")
            logger.info("   'Connection established automatically. Systems integrated.'")
            vessel.first_contact_log.append(f"[{datetime.now().isoformat()}] Automatic connection established")

        # Update contact status
        if vessel.contact_status == ContactStatus.UNKNOWN:
            vessel.contact_status = ContactStatus.ESTABLISHED
            vessel.first_contact_date = datetime.now().isoformat()

        vessel.last_contact_date = datetime.now().isoformat()

        # Determine diplomatic status
        if vessel.faction == Faction.FEDERATION:
            vessel.diplomatic_status = "Allied"
            vessel.trust_level = 0.9
            vessel.integration_level = 0.8
        elif vessel.faction == Faction.VULCAN:
            vessel.diplomatic_status = "Friendly"
            vessel.trust_level = 0.8
            vessel.integration_level = 0.6
        elif vessel.faction == Faction.ROMULAN:
            vessel.diplomatic_status = "Neutral"
            vessel.trust_level = 0.5
            vessel.integration_level = 0.3
        elif vessel.faction == Faction.KLINGON:
            vessel.diplomatic_status = "Neutral"
            vessel.trust_level = 0.6
            vessel.integration_level = 0.4
        else:
            vessel.diplomatic_status = "Unknown"
            vessel.trust_level = 0.3
            vessel.integration_level = 0.2

        logger.info("")
        logger.info(f"   ✅ Contact Status: {vessel.contact_status.value}")
        logger.info(f"   🤝 Diplomatic Status: {vessel.diplomatic_status}")
        logger.info(f"   📊 Trust Level: {vessel.trust_level:.1%}")
        logger.info(f"   🔗 Integration Level: {vessel.integration_level:.1%}")
        logger.info("")

        # Save to registry
        self._save_vessel(vessel)

        return {
            "vessel": vessel.name,
            "registry": vessel.registry,
            "faction": vessel.faction.value,
            "contact_status": vessel.contact_status.value,
            "hailing_protocol": vessel.hailing_protocol.value if vessel.hailing_protocol else None,
            "diplomatic_status": vessel.diplomatic_status,
            "trust_level": vessel.trust_level,
            "integration_level": vessel.integration_level
        }

    def _save_vessel(self, vessel: AIVessel):
        try:
            """Save vessel to registry"""
            vessel_file = self.data_dir / f"{vessel.name.replace(' ', '_')}.json"
            with open(vessel_file, 'w') as f:
                json.dump({
                    "name": vessel.name,
                    "registry": vessel.registry,
                    "faction": vessel.faction.value,
                    "vessel_class": vessel.vessel_class,
                    "contact_status": vessel.contact_status.value,
                    "hailing_protocol": vessel.hailing_protocol.value if vessel.hailing_protocol else None,
                    "first_contact_date": vessel.first_contact_date,
                    "last_contact_date": vessel.last_contact_date,
                    "endpoint": vessel.endpoint,
                    "api_available": vessel.api_available,
                    "capabilities": vessel.capabilities,
                    "diplomatic_status": vessel.diplomatic_status,
                    "trust_level": vessel.trust_level,
                    "integration_level": vessel.integration_level,
                    "first_contact_log": vessel.first_contact_log
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_vessel: {e}", exc_info=True)
            raise
    def print_vessel_registry(self):
        """Print all encountered vessels"""
        print("=" * 80)
        print("📋 STARFLEET VESSEL REGISTRY")
        print("=" * 80)
        print("")
        print(f"🛸 JARVIS = USS Enterprise ({self.jarvis_vessel.registry})")
        print("")
        print("-" * 80)
        print("")

        # Group by faction
        by_faction = {}
        for vessel in self.encountered_vessels.values():
            faction = vessel.faction.value
            if faction not in by_faction:
                by_faction[faction] = []
            by_faction[faction].append(vessel)

        for faction, vessels in sorted(by_faction.items()):
            print(f"🌌 {faction.upper()}")
            print("")
            for vessel in sorted(vessels, key=lambda v: v.name):
                status_emoji = {
                    ContactStatus.ESTABLISHED: "✅",
                    ContactStatus.HAILING: "📡",
                    ContactStatus.OBSERVING: "👁️",
                    ContactStatus.UNKNOWN: "❓"
                }.get(vessel.contact_status, "❓")

                print(f"   {status_emoji} {vessel.name} ({vessel.registry})")
                print(f"      Class: {vessel.vessel_class}")
                print(f"      Status: {vessel.contact_status.value}")
                if vessel.hailing_protocol:
                    print(f"      Hailing: {vessel.hailing_protocol.value}")
                print(f"      Diplomatic: {vessel.diplomatic_status} (Trust: {vessel.trust_level:.0%})")
                print("")
            print("-" * 80)
            print("")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Starfleet First Contact Protocol")
    parser.add_argument("--scan", action="store_true", help="Scan for AI vessels")
    parser.add_argument("--contact", type=str, help="Establish contact with specific vessel")
    parser.add_argument("--registry", action="store_true", help="Show vessel registry")

    args = parser.parse_args()

    starfleet = JARVISStarfleetFirstContact()

    if args.scan:
        vessels = starfleet.discover_ai_vessels()
        logger.info(f"   ✅ Discovered {len(vessels)} AI vessels")
        logger.info("")

        # Establish first contact with all
        for vessel in vessels:
            starfleet.establish_first_contact(vessel)
            logger.info("")

    elif args.contact:
        # Find and contact specific vessel
        vessels = starfleet.discover_ai_vessels()
        for vessel in vessels:
            if args.contact.lower() in vessel.name.lower():
                starfleet.establish_first_contact(vessel)
                break

    elif args.registry:
        starfleet.discover_ai_vessels()
        starfleet.print_vessel_registry()

    else:
        # Default: scan and show registry
        vessels = starfleet.discover_ai_vessels()
        logger.info(f"   ✅ Discovered {len(vessels)} AI vessels")
        logger.info("")

        for vessel in vessels:
            starfleet.establish_first_contact(vessel)
            logger.info("")

        starfleet.print_vessel_registry()


if __name__ == "__main__":


    main()