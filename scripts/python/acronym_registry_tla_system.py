#!/usr/bin/env python3
"""
Acronym Registry & TLA System

Tracks and manages acronyms (especially TLAs - Three-Letter Acronyms) used throughout the project.
Accommodates military communication style preference from 8 years active duty U.S. Air Force background.

Features:
- Acronym registry and definitions
- TLA (Three-Letter Acronym) tracking
- Acronym expansion/explanation
- Usage tracking
- Cultural context preservation

Tags: #TLA #acronyms #military #communication #registry
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("AcronymRegistryTLA")


class AcronymType(Enum):
    """Acronym type classification"""
    TLA = "TLA"  # Three-Letter Acronym
    FLA = "FLA"  # Four-Letter Acronym
    ACRONYM = "acronym"  # General acronym
    INITIALISM = "initialism"  # Pronounced letter by letter
    ABBREVIATION = "abbreviation"  # Shortened form


@dataclass
class Acronym:
    """Acronym definition"""
    acronym: str
    full_form: str
    acronym_type: AcronymType
    category: str = ""  # e.g., "system", "military", "technical"
    description: str = ""
    first_used: Optional[datetime] = None
    usage_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['acronym_type'] = self.acronym_type.value
        if self.first_used:
            result['first_used'] = self.first_used.isoformat()
        return result


class AcronymRegistryTLA:
    """
    Acronym Registry & TLA System

    Tracks acronyms (especially TLAs) used throughout the project.
    Accommodates military communication style preference.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize acronym registry"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "acronym_registry"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.data_dir / "acronym_registry.json"
        self.acronyms: Dict[str, Acronym] = {}

        # Load existing registry
        self.load_registry()

        # Initialize with known acronyms
        self._initialize_known_acronyms()

        logger.info("=" * 80)
        logger.info("📚 ACRONYM REGISTRY & TLA SYSTEM")
        logger.info("=" * 80)
        logger.info("   Accommodating military TLA communication style")
        logger.info("   User background: 8 years active duty U.S. Air Force")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_known_acronyms(self):
        """Initialize with known project acronyms"""
        known_acronyms = [
            {
                "acronym": "TLA",
                "full_form": "Three-Letter Acronym",
                "acronym_type": AcronymType.TLA,
                "category": "meta",
                "description": "Acronym for acronyms - military standard"
            },
            {
                "acronym": "AMP",
                "full_form": "Analytics Metrics Perspective",
                "acronym_type": AcronymType.TLA,
                "category": "system",
                "description": "Homelab analytics system (@AMP)"
            },
            {
                "acronym": "WOPR",
                "full_form": "War Operation Plan Response",
                "acronym_type": AcronymType.TLA,
                "category": "system",
                "description": "Testing system reference (from WarGames movie)"
            },
            {
                "acronym": "DOIT",
                "full_form": "Do It",
                "acronym_type": AcronymType.TLA,
                "category": "command",
                "description": "Direct action command"
            },
            {
                "acronym": "USAF",
                "full_form": "United States Air Force",
                "acronym_type": AcronymType.TLA,
                "category": "military",
                "description": "User's military service branch"
            },
            {
                "acronym": "NAS",
                "full_form": "Network Attached Storage",
                "acronym_type": AcronymType.TLA,
                "category": "hardware",
                "description": "Storage device"
            },
            {
                "acronym": "MCP",
                "full_form": "Model Context Protocol",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Protocol for AI model context"
            },
            {
                "acronym": "SSH",
                "full_form": "Secure Shell",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Network protocol"
            },
            {
                "acronym": "CPU",
                "full_form": "Central Processing Unit",
                "acronym_type": AcronymType.TLA,
                "category": "hardware",
                "description": "Processor"
            },
            {
                "acronym": "GPU",
                "full_form": "Graphics Processing Unit",
                "acronym_type": AcronymType.TLA,
                "category": "hardware",
                "description": "Graphics processor"
            },
            {
                "acronym": "API",
                "full_form": "Application Programming Interface",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Software interface"
            },
            {
                "acronym": "IDE",
                "full_form": "Integrated Development Environment",
                "acronym_type": AcronymType.TLA,
                "category": "software",
                "description": "Development tool"
            },
            {
                "acronym": "JSON",
                "full_form": "JavaScript Object Notation",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Data format"
            },
            {
                "acronym": "RDP",
                "full_form": "Remote Desktop Protocol",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Remote access protocol"
            },
            {
                "acronym": "DNS",
                "full_form": "Domain Name System",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Network naming system"
            },
            {
                "acronym": "IP",
                "full_form": "Internet Protocol",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Network protocol"
            },
            {
                "acronym": "MAC",
                "full_form": "Media Access Control",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Network address"
            },
            {
                "acronym": "OS",
                "full_form": "Operating System",
                "acronym_type": AcronymType.TLA,
                "category": "software",
                "description": "System software"
            },
            {
                "acronym": "VM",
                "full_form": "Virtual Machine",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Virtualized system"
            },
            {
                "acronym": "WMI",
                "full_form": "Windows Management Instrumentation",
                "acronym_type": AcronymType.TLA,
                "category": "technical",
                "description": "Windows system management"
            }
        ]

        for acro_data in known_acronyms:
            if acro_data['acronym'] not in self.acronyms:
                acronym = Acronym(
                    acronym=acro_data['acronym'],
                    full_form=acro_data['full_form'],
                    acronym_type=acro_data['acronym_type'],
                    category=acro_data.get('category', ''),
                    description=acro_data.get('description', ''),
                    first_used=datetime.now()
                )
                self.acronyms[acro_data['acronym']] = acronym

    def register_acronym(
        self,
        acronym: str,
        full_form: str,
        acronym_type: Optional[AcronymType] = None,
        category: str = "",
        description: str = ""
    ) -> Acronym:
        """Register a new acronym"""
        # Determine type if not provided
        if acronym_type is None:
            if len(acronym) == 3:
                acronym_type = AcronymType.TLA
            elif len(acronym) == 4:
                acronym_type = AcronymType.FLA
            else:
                acronym_type = AcronymType.ACRONYM

        if acronym in self.acronyms:
            # Update existing
            existing = self.acronyms[acronym]
            existing.usage_count += 1
            if not existing.full_form:
                existing.full_form = full_form
            if not existing.description:
                existing.description = description
            return existing
        else:
            # Create new
            new_acronym = Acronym(
                acronym=acronym,
                full_form=full_form,
                acronym_type=acronym_type,
                category=category,
                description=description,
                first_used=datetime.now(),
                usage_count=1
            )
            self.acronyms[acronym] = new_acronym
            logger.info(f"📝 Registered acronym: {acronym} = {full_form}")
            return new_acronym

    def lookup(self, acronym: str) -> Optional[Acronym]:
        """Look up an acronym"""
        return self.acronyms.get(acronym.upper())

    def expand(self, acronym: str) -> str:
        """Expand acronym to full form"""
        acro = self.lookup(acronym)
        if acro:
            return f"{acro.acronym} ({acro.full_form})"
        return acronym

    def get_all_tlas(self) -> List[Acronym]:
        """Get all Three-Letter Acronyms"""
        return [a for a in self.acronyms.values() if a.acronym_type == AcronymType.TLA]

    def get_by_category(self, category: str) -> List[Acronym]:
        """Get acronyms by category"""
        return [a for a in self.acronyms.values() if a.category == category]

    def save_registry(self):
        """Save acronym registry to file"""
        registry_data = {
            "last_updated": datetime.now().isoformat(),
            "total_acronyms": len(self.acronyms),
            "tla_count": len(self.get_all_tlas()),
            "acronyms": {k: v.to_dict() for k, v in self.acronyms.items()}
        }

        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, default=str)

        logger.info(f"💾 Saved acronym registry: {len(self.acronyms)} acronyms")

    def load_registry(self):
        """Load acronym registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry_data = json.load(f)

                for acro_key, acro_data in registry_data.get('acronyms', {}).items():
                    acronym = Acronym(
                        acronym=acro_data['acronym'],
                        full_form=acro_data['full_form'],
                        acronym_type=AcronymType(acro_data['acronym_type']),
                        category=acro_data.get('category', ''),
                        description=acro_data.get('description', ''),
                        usage_count=acro_data.get('usage_count', 0),
                        context=acro_data.get('context', {})
                    )
                    if acro_data.get('first_used'):
                        acronym.first_used = datetime.fromisoformat(acro_data['first_used'])

                    self.acronyms[acro_key] = acronym

                logger.info(f"📂 Loaded {len(self.acronyms)} acronyms from registry")
            except Exception as e:
                logger.debug(f"Could not load registry: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate acronym registry report"""
        tlas = self.get_all_tlas()

        report = {
            "report_date": datetime.now().isoformat(),
            "summary": {
                "total_acronyms": len(self.acronyms),
                "tla_count": len(tlas),
                "by_category": {}
            },
            "tlas": [a.to_dict() for a in sorted(tlas, key=lambda x: x.acronym)],
            "all_acronyms": [a.to_dict() for a in sorted(self.acronyms.values(), key=lambda x: x.acronym)]
        }

        # Count by category
        for acro in self.acronyms.values():
            cat = acro.category or "uncategorized"
            report["summary"]["by_category"][cat] = report["summary"]["by_category"].get(cat, 0) + 1

        return report


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Acronym Registry & TLA System")
    parser.add_argument('--register', nargs=3, metavar=('ACRONYM', 'FULL_FORM', 'CATEGORY'),
                       help='Register a new acronym')
    parser.add_argument('--lookup', type=str, help='Look up an acronym')
    parser.add_argument('--expand', type=str, help='Expand an acronym')
    parser.add_argument('--tlas', action='store_true', help='List all TLAs')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--save', action='store_true', help='Save registry')

    args = parser.parse_args()

    registry = AcronymRegistryTLA()

    if args.register:
        acronym, full_form, category = args.register
        registry.register_acronym(acronym, full_form, category=category)
        if args.save:
            registry.save_registry()

    elif args.lookup:
        acro = registry.lookup(args.lookup)
        if acro:
            print(f"\n{acro.acronym}: {acro.full_form}")
            print(f"Type: {acro.acronym_type.value}")
            print(f"Category: {acro.category}")
            print(f"Description: {acro.description}")
            print(f"Usage Count: {acro.usage_count}")
        else:
            print(f"\n❌ Acronym '{args.lookup}' not found in registry")

    elif args.expand:
        print(f"\n{registry.expand(args.expand)}")

    elif args.tlas:
        tlas = registry.get_all_tlas()
        print(f"\n📚 Three-Letter Acronyms (TLAs): {len(tlas)}")
        print("=" * 80)
        for tla in sorted(tlas, key=lambda x: x.acronym):
            print(f"  {tla.acronym:6s} = {tla.full_form}")
            if tla.description:
                print(f"           {tla.description}")
        print("")

    elif args.report:
        report = registry.generate_report()
        print("\n" + "=" * 80)
        print("📚 ACRONYM REGISTRY REPORT")
        print("=" * 80)
        print(f"Total Acronyms: {report['summary']['total_acronyms']}")
        print(f"TLAs: {report['summary']['tla_count']}")
        print(f"\nBy Category:")
        for cat, count in sorted(report['summary']['by_category'].items()):
            print(f"  {cat}: {count}")
        print("")

    else:
        # Default: show summary
        print("\n" + "=" * 80)
        print("📚 ACRONYM REGISTRY & TLA SYSTEM")
        print("=" * 80)
        print(f"Total Acronyms: {len(registry.acronyms)}")
        print(f"TLAs: {len(registry.get_all_tlas())}")
        print("\nUse --help for options")
        print("")


if __name__ == "__main__":


    main()