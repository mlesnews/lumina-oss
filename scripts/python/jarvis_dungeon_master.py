#!/usr/bin/env python3
"""
JARVIS Dungeon Master Mode
AI JARVIS as Dungeon Master for tabletop RPGs (Fantasy Grounds, etc.)
Multiverse support: D&D, Star Wars, Conan, Transformers, Star Trek, etc.
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


class MultiverseSetting(Enum):
    """Multiverse settings"""
    DND = "dnd"                    # Dungeons & Dragons
    STAR_WARS = "star_wars"        # Star Wars
    CONAN = "conan"                # Conan the Barbarian
    TRANSFORMERS = "transformers"  # Transformers
    STAR_TREK = "star_trek"        # Star Trek
    MIXED = "mixed"                # Mixed multiverse


@dataclass
class Campaign:
    """RPG Campaign"""
    name: str
    setting: MultiverseSetting
    players: List[str]
    current_session: int
    created: str
    last_updated: str
    notes: Optional[str] = None


class JARVISDungeonMaster:
    """JARVIS as Dungeon Master for tabletop RPGs"""

    def __init__(self, data_file: Optional[Path] = None):
        """Initialize JARVIS Dungeon Master"""
        self.logger = logging.getLogger(self.__class__.__name__)

        if data_file is None:
            data_file = project_root / "data" / "jarvis_dm_campaigns.json"

        self.data_file = data_file
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        self.data = self._load_data()
        self.current_campaign: Optional[Campaign] = None

    def _load_data(self) -> Dict:
        """Load campaign data"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading campaign data: {e}")

        return {
            "campaigns": [],
            "current_campaign": None,
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

    def _save_data(self):
        """Save campaign data"""
        try:
            self.data["last_updated"] = datetime.now().isoformat()
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving campaign data: {e}")

    def create_campaign(
        self,
        name: str,
        setting: MultiverseSetting,
        players: List[str]
    ) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            name=name,
            setting=setting,
            players=players,
            current_session=1,
            created=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )

        self.data["campaigns"].append(asdict(campaign))
        self.data["current_campaign"] = name
        self.current_campaign = campaign
        self._save_data()

        self.logger.info(f"🎲 Campaign created: {name} ({setting.value})")
        return campaign

    def start_session(self, campaign_name: Optional[str] = None):
        """Start a new session"""
        if campaign_name:
            # Find campaign
            for c in self.data["campaigns"]:
                if c["name"] == campaign_name:
                    self.current_campaign = Campaign(**c)
                    break

        if not self.current_campaign:
            self.logger.error("No campaign selected")
            return

        self.logger.info(f"🎲 Starting session {self.current_campaign.current_session}")
        self.logger.info(f"   Campaign: {self.current_campaign.name}")
        self.logger.info(f"   Setting: {self.current_campaign.setting.value}")
        self.logger.info(f"   Players: {', '.join(self.current_campaign.players)}")

        return self.current_campaign

    def dm_narrate(self, narration: str):
        """DM narration"""
        if not self.current_campaign:
            self.logger.warning("No active campaign")
            return

        self.logger.info(f"📖 DM: {narration}")
        return narration


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Dungeon Master")
    parser.add_argument("--create-campaign", help="Create new campaign")
    parser.add_argument("--setting", choices=[s.value for s in MultiverseSetting],
                       help="Campaign setting")
    parser.add_argument("--players", nargs="+", help="Player names")
    parser.add_argument("--start-session", help="Start session for campaign")
    parser.add_argument("--narrate", help="DM narration")

    args = parser.parse_args()

    dm = JARVISDungeonMaster()

    if args.create_campaign:
        if not args.setting or not args.players:
            print("❌ Error: --setting and --players required")
            return

        setting = MultiverseSetting[args.setting.upper()]
        campaign = dm.create_campaign(
            name=args.create_campaign,
            setting=setting,
            players=args.players
        )
        print(f"✅ Campaign created: {campaign.name}")
    elif args.start_session:
        dm.start_session(args.start_session)
    elif args.narrate:
        dm.dm_narrate(args.narrate)
    else:
        parser.print_help()


if __name__ == "__main__":


    main()