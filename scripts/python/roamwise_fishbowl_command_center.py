#!/usr/bin/env python3
"""
@ROAMWISE.AI FISHBOWL Command Center

Customer Portal Gateway with:
- Public/Private/Premium feature tiering
- RBAC (Role-Based Access Control)
- STARGATE entry point
- Multiversal Galactic Map visualization
- Energy Consumption Scale progression
- DUNE | FOUNDATION | WoW Galaxy (Reality-Zero) Atlas
- Jedi-Pathfinder | Hyperspace Lanes
- Life-domain-end waypoints

"Connecting the dots" - Integration hub for all systems

Tags: #roamwise #fishbowl #command_center #gateway #rbac #stargate #galactic_map
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("ROAMWISEFishbowlCommandCenter")

# Import METACLOUD @WOP system
try:
    from metacloud_wop_system import MetacloudWOPSystem
    METACLOUD_AVAILABLE = True
except ImportError:
    METACLOUD_AVAILABLE = False
    logger.debug("METACLOUD @WOP system not available")


class AccessTier(Enum):
    """Access tier levels"""
    PUBLIC = "public"
    PRIVATE = "private"
    PREMIUM = "premium"


class UserRole(Enum):
    """User roles for RBAC"""
    GUEST = "guest"  # Public tier
    USER = "user"  # Private tier
    PREMIUM_USER = "premium_user"  # Premium tier
    ADMIN = "admin"  # Full access
    OPERATOR = "operator"  # System operator


class EnergyConsumptionTier(Enum):
    """Energy Consumption Scale tiers"""
    TIER_1 = "tier_1"  # Basic energy consumption
    TIER_2 = "tier_2"  # Moderate energy consumption
    TIER_3 = "tier_3"  # High energy consumption
    TIER_4 = "tier_4"  # Very high energy consumption
    TIER_5 = "tier_5"  # Maximum energy consumption


class GalaxyType(Enum):
    """Galaxy types in multiversal map"""
    DUNE = "dune"  # DUNE universe
    FOUNDATION = "foundation"  # Foundation universe
    WOW_REALITY_ZERO = "wow_reality_zero"  # WoW Galaxy (Reality-Zero) Atlas
    JEDI_PATHFINDER = "jedi_pathfinder"  # Jedi-Pathfinder
    HYPERSPACE_LANES = "hyperspace_lanes"  # Hyperspace Lanes
    LIFE_DOMAIN_END = "life_domain_end"  # Life-domain-end waypoints


@dataclass
class Waypoint:
    """Waypoint in galactic map"""
    waypoint_id: str
    name: str
    galaxy: GalaxyType
    coordinates: Dict[str, float]  # x, y, z coordinates
    energy_tier: EnergyConsumptionTier
    description: str
    accessible_tiers: List[AccessTier]
    required_roles: List[UserRole]
    connected_waypoints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['galaxy'] = self.galaxy.value
        result['energy_tier'] = self.energy_tier.value
        result['accessible_tiers'] = [t.value for t in self.accessible_tiers]
        result['required_roles'] = [r.value for r in self.required_roles]
        return result


@dataclass
class User:
    """User account"""
    user_id: str
    username: str
    email: str
    access_tier: AccessTier
    roles: List[UserRole]
    current_waypoint: Optional[str] = None
    energy_tier: EnergyConsumptionTier = EnergyConsumptionTier.TIER_1
    created_at: datetime = field(default_factory=datetime.now)
    last_access: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['access_tier'] = self.access_tier.value
        result['roles'] = [r.value for r in self.roles]
        result['energy_tier'] = self.energy_tier.value
        if self.current_waypoint:
            result['current_waypoint'] = self.current_waypoint
        result['created_at'] = self.created_at.isoformat()
        result['last_access'] = self.last_access.isoformat()
        return result


class ROAMWISEFishbowlCommandCenter:
    """
    @ROAMWISE.AI FISHBOWL Command Center

    Customer Portal Gateway with tiered access, RBAC, and galactic map
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize FISHBOWL command center"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "roamwise_fishbowl"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Users
        self.users: Dict[str, User] = {}

        # Waypoints (galactic map)
        self.waypoints: Dict[str, Waypoint] = {}

        # Initialize galactic map
        self._initialize_galactic_map()

        # Initialize METACLOUD @WOP system
        if METACLOUD_AVAILABLE:
            self.metacloud = MetacloudWOPSystem(project_root)
            logger.info("☁️  METACLOUD @WOP system integrated")
        else:
            self.metacloud = None

        # Load saved state
        self._load_state()

        logger.info("=" * 80)
        logger.info("🌌 @ROAMWISE.AI FISHBOWL COMMAND CENTER")
        logger.info("=" * 80)
        logger.info("   STARGATE Entry Point")
        logger.info("   Multiversal Galactic Map")
        logger.info("   Public/Private/Premium Tiering + RBAC")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_galactic_map(self):
        """Initialize multiversal galactic map with waypoints"""
        # DUNE Universe waypoints
        self.waypoints["dune_arrakis"] = Waypoint(
            waypoint_id="dune_arrakis",
            name="Arrakis - Desert Planet",
            galaxy=GalaxyType.DUNE,
            coordinates={"x": 0.0, "y": 0.0, "z": 0.0},
            energy_tier=EnergyConsumptionTier.TIER_5,
            description="The desert planet, source of spice",
            accessible_tiers=[AccessTier.PREMIUM],
            required_roles=[UserRole.PREMIUM_USER, UserRole.ADMIN]
        )

        # Foundation Universe waypoints
        self.waypoints["foundation_terminal"] = Waypoint(
            waypoint_id="foundation_terminal",
            name="Foundation Terminal",
            galaxy=GalaxyType.FOUNDATION,
            coordinates={"x": 100.0, "y": 0.0, "z": 0.0},
            energy_tier=EnergyConsumptionTier.TIER_4,
            description="Foundation civilization hub",
            accessible_tiers=[AccessTier.PRIVATE, AccessTier.PREMIUM],
            required_roles=[UserRole.USER, UserRole.PREMIUM_USER, UserRole.ADMIN]
        )

        # WoW Reality-Zero Atlas waypoints
        self.waypoints["wow_azeroth"] = Waypoint(
            waypoint_id="wow_azeroth",
            name="Azeroth - Reality Zero",
            galaxy=GalaxyType.WOW_REALITY_ZERO,
            coordinates={"x": 0.0, "y": 100.0, "z": 0.0},
            energy_tier=EnergyConsumptionTier.TIER_3,
            description="World of Warcraft reality-zero atlas",
            accessible_tiers=[AccessTier.PUBLIC, AccessTier.PRIVATE, AccessTier.PREMIUM],
            required_roles=[UserRole.GUEST, UserRole.USER, UserRole.PREMIUM_USER, UserRole.ADMIN]
        )

        # Jedi-Pathfinder waypoints
        self.waypoints["jedi_temple"] = Waypoint(
            waypoint_id="jedi_temple",
            name="Jedi Temple - Pathfinder",
            galaxy=GalaxyType.JEDI_PATHFINDER,
            coordinates={"x": 0.0, "y": 0.0, "z": 100.0},
            energy_tier=EnergyConsumptionTier.TIER_4,
            description="Jedi pathfinding and navigation",
            accessible_tiers=[AccessTier.PRIVATE, AccessTier.PREMIUM],
            required_roles=[UserRole.USER, UserRole.PREMIUM_USER, UserRole.ADMIN]
        )

        # Hyperspace Lanes waypoints
        self.waypoints["hyperspace_core"] = Waypoint(
            waypoint_id="hyperspace_core",
            name="Hyperspace Core",
            galaxy=GalaxyType.HYPERSPACE_LANES,
            coordinates={"x": 50.0, "y": 50.0, "z": 50.0},
            energy_tier=EnergyConsumptionTier.TIER_5,
            description="Hyperspace lane network core",
            accessible_tiers=[AccessTier.PREMIUM],
            required_roles=[UserRole.PREMIUM_USER, UserRole.ADMIN]
        )

        # Life-domain-end waypoints
        self.waypoints["life_domain_end"] = Waypoint(
            waypoint_id="life_domain_end",
            name="Life Domain End",
            galaxy=GalaxyType.LIFE_DOMAIN_END,
            coordinates={"x": -100.0, "y": -100.0, "z": -100.0},
            energy_tier=EnergyConsumptionTier.TIER_5,
            description="Life-domain-end waypoint - ultimate destination",
            accessible_tiers=[AccessTier.PREMIUM],
            required_roles=[UserRole.ADMIN, UserRole.OPERATOR]
        )

        # Connect waypoints (hyperspace lanes)
        self.waypoints["dune_arrakis"].connected_waypoints = ["hyperspace_core"]
        self.waypoints["foundation_terminal"].connected_waypoints = ["hyperspace_core", "wow_azeroth"]
        self.waypoints["wow_azeroth"].connected_waypoints = ["foundation_terminal", "jedi_temple"]
        self.waypoints["jedi_temple"].connected_waypoints = ["wow_azeroth", "hyperspace_core"]
        self.waypoints["hyperspace_core"].connected_waypoints = ["dune_arrakis", "foundation_terminal", "jedi_temple", "life_domain_end"]
        self.waypoints["life_domain_end"].connected_waypoints = ["hyperspace_core"]

        logger.info(f"✅ Initialized {len(self.waypoints)} waypoints across {len(GalaxyType)} galaxies")

    def create_user(
        self,
        username: str,
        email: str,
        access_tier: AccessTier,
        roles: Optional[List[UserRole]] = None
    ) -> User:
        """Create new user account"""
        user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        if roles is None:
            # Default roles based on tier
            if access_tier == AccessTier.PUBLIC:
                roles = [UserRole.GUEST]
            elif access_tier == AccessTier.PRIVATE:
                roles = [UserRole.USER]
            elif access_tier == AccessTier.PREMIUM:
                roles = [UserRole.PREMIUM_USER]

        user = User(
            user_id=user_id,
            username=username,
            email=email,
            access_tier=access_tier,
            roles=roles,
            current_waypoint="wow_azeroth",  # Default starting point
            energy_tier=EnergyConsumptionTier.TIER_1
        )

        self.users[user_id] = user

        logger.info(f"✅ Created user: {username} ({access_tier.value} tier)")

        return user

    def stargate_entry(self, user_id: str) -> Dict[str, Any]:
        """STARGATE entry point - user enters the multiversal map"""
        if user_id not in self.users:
            logger.warning(f"⚠️  User {user_id} not found")
            return {}

        user = self.users[user_id]
        user.last_access = datetime.now()

        # Get accessible waypoints
        accessible_waypoints = self.get_accessible_waypoints(user)

        entry_data = {
            "user": user.to_dict(),
            "stargate_entry": True,
            "accessible_waypoints": [w.to_dict() for w in accessible_waypoints],
            "galactic_map": self.get_galactic_map_summary(),
            "energy_consumption_scale": self.get_energy_consumption_scale(),
            "entry_timestamp": datetime.now().isoformat()
        }

        logger.info(f"🌌 STARGATE entry: {user.username} entered multiversal map")

        return entry_data

    def get_accessible_waypoints(self, user: User) -> List[Waypoint]:
        """Get waypoints accessible to user based on tier and roles"""
        accessible = []

        for waypoint in self.waypoints.values():
            # Check tier access
            if user.access_tier not in waypoint.accessible_tiers:
                continue

            # Check role access
            if not any(role in waypoint.required_roles for role in user.roles):
                continue

            accessible.append(waypoint)

        return accessible

    def navigate_to_waypoint(self, user_id: str, waypoint_id: str) -> bool:
        """Navigate user to waypoint"""
        if user_id not in self.users:
            return False

        if waypoint_id not in self.waypoints:
            return False

        user = self.users[user_id]
        waypoint = self.waypoints[waypoint_id]

        # Check access
        accessible = self.get_accessible_waypoints(user)
        if waypoint not in accessible:
            logger.warning(f"⚠️  User {user.username} cannot access waypoint {waypoint_id}")
            return False

        # Check if waypoint is connected from current location
        if user.current_waypoint:
            current = self.waypoints.get(user.current_waypoint)
            if current and waypoint_id not in current.connected_waypoints:
                # Check if connected via hyperspace core
                if "hyperspace_core" in current.connected_waypoints and waypoint_id in self.waypoints["hyperspace_core"].connected_waypoints:
                    pass  # Can travel via hyperspace
                else:
                    logger.warning(f"⚠️  Waypoint {waypoint_id} not directly connected")
                    return False

        # Navigate
        user.current_waypoint = waypoint_id
        user.energy_tier = waypoint.energy_tier
        user.last_access = datetime.now()

        logger.info(f"🌌 Navigated {user.username} to {waypoint.name}")

        return True

    def get_galactic_map_summary(self) -> Dict[str, Any]:
        """Get summary of galactic map"""
        galaxies = {}
        for galaxy_type in GalaxyType:
            waypoints_in_galaxy = [w for w in self.waypoints.values() if w.galaxy == galaxy_type]
            galaxies[galaxy_type.value] = {
                "waypoint_count": len(waypoints_in_galaxy),
                "waypoints": [w.name for w in waypoints_in_galaxy]
            }

        return {
            "total_waypoints": len(self.waypoints),
            "total_galaxies": len(GalaxyType),
            "galaxies": galaxies,
            "hyperspace_network": {
                "core_waypoint": "hyperspace_core",
                "connected_waypoints": len(self.waypoints["hyperspace_core"].connected_waypoints)
            }
        }

    def get_energy_consumption_scale(self) -> Dict[str, Any]:
        """Get Energy Consumption Scale tiers"""
        return {
            "tiers": {
                tier.value: {
                    "level": i + 1,
                    "description": f"Tier {i + 1} energy consumption",
                    "waypoints": [
                        w.name for w in self.waypoints.values()
                        if w.energy_tier == tier
                    ]
                }
                for i, tier in enumerate(EnergyConsumptionTier)
            },
            "progression": "Users progress through tiers as they access higher energy waypoints"
        }

    def get_fishbowl_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get FISHBOWL command center dashboard for user"""
        if user_id not in self.users:
            return {}

        user = self.users[user_id]
        accessible_waypoints = self.get_accessible_waypoints(user)

        dashboard = {
            "user": user.to_dict(),
            "dashboard": {
                "current_location": self.waypoints[user.current_waypoint].to_dict() if user.current_waypoint else None,
                "accessible_waypoints": len(accessible_waypoints),
                "energy_tier": user.energy_tier.value,
                "access_tier": user.access_tier.value,
                "roles": [r.value for r in user.roles]
            },
            "galactic_map": self.get_galactic_map_summary(),
            "energy_scale": self.get_energy_consumption_scale(),
            "timestamp": datetime.now().isoformat()
        }

        # Add METACLOUD @WOP if available
        if self.metacloud:
            dashboard["metacloud"] = self.metacloud.get_metacloud(limit=20)

        return dashboard

    def _load_state(self):
        """Load FISHBOWL state from file"""
        state_file = self.data_dir / "fishbowl_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Load users
            for uid, user_data in state.get('users', {}).items():
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    access_tier=AccessTier(user_data['access_tier']),
                    roles=[UserRole(r) for r in user_data['roles']],
                    current_waypoint=user_data.get('current_waypoint'),
                    energy_tier=EnergyConsumptionTier(user_data.get('energy_tier', 'tier_1')),
                    created_at=datetime.fromisoformat(user_data['created_at']),
                    last_access=datetime.fromisoformat(user_data['last_access'])
                )
                self.users[uid] = user

            logger.info(f"📂 Loaded {len(self.users)} users from state")
        except Exception as e:
            logger.debug(f"Could not load state: {e}")

    def save_state(self):
        try:
            """Save FISHBOWL state"""
            state_file = self.data_dir / "fishbowl_state.json"

            state = {
                "users": {uid: u.to_dict() for uid, u in self.users.items()},
                "waypoints": {wid: w.to_dict() for wid, w in self.waypoints.items()},
                "saved_at": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"💾 FISHBOWL state saved: {state_file}")


        except Exception as e:
            self.logger.error(f"Error in save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="@ROAMWISE.AI FISHBOWL Command Center")
    parser.add_argument('--create-user', nargs=3, metavar=('USERNAME', 'EMAIL', 'TIER'),
                       help='Create new user')
    parser.add_argument('--stargate', type=str, metavar='USER_ID', help='STARGATE entry')
    parser.add_argument('--navigate', nargs=2, metavar=('USER_ID', 'WAYPOINT_ID'),
                       help='Navigate to waypoint')
    parser.add_argument('--dashboard', type=str, metavar='USER_ID', help='Get dashboard')
    parser.add_argument('--map', action='store_true', help='Show galactic map')
    parser.add_argument('--save', action='store_true', help='Save state')

    args = parser.parse_args()

    fishbowl = ROAMWISEFishbowlCommandCenter()

    if args.create_user:
        username, email, tier_str = args.create_user
        tier = AccessTier(tier_str.lower())
        user = fishbowl.create_user(username, email, tier)
        print(f"\n✅ Created user: {user.user_id}")
        print(f"   Username: {user.username}")
        print(f"   Tier: {user.access_tier.value}")
        print(f"   Roles: {[r.value for r in user.roles]}")
        if args.save:
            fishbowl.save_state()

    elif args.stargate:
        entry = fishbowl.stargate_entry(args.stargate)
        if entry:
            print("\n" + "=" * 80)
            print("🌌 STARGATE ENTRY")
            print("=" * 80)
            print(f"User: {entry['user']['username']}")
            print(f"Accessible Waypoints: {len(entry['accessible_waypoints'])}")
            print(f"Energy Tier: {entry['user']['energy_tier']}")
            print("")
            print("Galactic Map:")
            for galaxy, data in entry['galactic_map']['galaxies'].items():
                print(f"   {galaxy}: {data['waypoint_count']} waypoints")
            print("")
            print("=" * 80)
            print("")
        if args.save:
            fishbowl.save_state()

    elif args.navigate:
        user_id, waypoint_id = args.navigate
        success = fishbowl.navigate_to_waypoint(user_id, waypoint_id)
        if success:
            print(f"\n✅ Navigated to {waypoint_id}")
        else:
            print(f"\n❌ Navigation failed")
        if args.save:
            fishbowl.save_state()

    elif args.dashboard:
        dashboard = fishbowl.get_fishbowl_dashboard(args.dashboard)
        if dashboard:
            print("\n" + "=" * 80)
            print("🌌 FISHBOWL COMMAND CENTER DASHBOARD")
            print("=" * 80)
            print(f"User: {dashboard['user']['username']}")
            print(f"Current Location: {dashboard['dashboard']['current_location']['name'] if dashboard['dashboard']['current_location'] else 'None'}")
            print(f"Accessible Waypoints: {dashboard['dashboard']['accessible_waypoints']}")
            print(f"Energy Tier: {dashboard['dashboard']['energy_tier']}")
            print(f"Access Tier: {dashboard['dashboard']['access_tier']}")
            print("")

            # Show METACLOUD if available
            if 'metacloud' in dashboard:
                cloud = dashboard['metacloud']
                print("☁️  METACLOUD @WOP & @TAGS")
                print("-" * 80)
                print(f"Total @WOP: {cloud['words_of_power']['total']}")
                print(f"Total @tags: {cloud['short_tags']['total']}")
                print("")
                print("Top @WOP:")
                for wop in cloud['words_of_power']['popular'][:5]:
                    print(f"   {wop['word']} ({wop['pronunciation']}) - Score: {wop['popularity_score']:.1f}")
                print("")
                print("Top @tags:")
                for tag in cloud['short_tags']['popular'][:5]:
                    print(f"   {tag['tag']} ({tag['shorthand']}) - Score: {tag['popularity_score']:.1f}")
                print("")

            print("=" * 80)
            print("")
        if args.save:
            fishbowl.save_state()

    elif args.map:
        map_summary = fishbowl.get_galactic_map_summary()
        print("\n" + "=" * 80)
        print("🌌 MULTIVERSAL GALACTIC MAP")
        print("=" * 80)
        print(f"Total Waypoints: {map_summary['total_waypoints']}")
        print(f"Total Galaxies: {map_summary['total_galaxies']}")
        print("")
        for galaxy, data in map_summary['galaxies'].items():
            print(f"📊 {galaxy.upper()}:")
            print(f"   Waypoints: {data['waypoint_count']}")
            for waypoint_name in data['waypoints']:
                print(f"      - {waypoint_name}")
            print("")
        print("=" * 80)
        print("")

    else:
        print("\n" + "=" * 80)
        print("🌌 @ROAMWISE.AI FISHBOWL COMMAND CENTER")
        print("=" * 80)
        print("   STARGATE Entry Point")
        print("   Multiversal Galactic Map")
        print("")
        print("Use --create-user to create user")
        print("Use --stargate to enter via STARGATE")
        print("Use --navigate to navigate to waypoint")
        print("Use --dashboard to view dashboard")
        print("Use --map to show galactic map")
        print("=" * 80)
        print("")

    if args.save:
        fishbowl.save_state()


if __name__ == "__main__":


    main()