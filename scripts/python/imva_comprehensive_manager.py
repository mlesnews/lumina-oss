#!/usr/bin/env python3
"""
IMVA Comprehensive Manager - Robust Iron Man Virtual Assistant System

Comprehensive system for managing IMVA with:
- Multiple armor variants (Mark V, Mark III, Mark VI, Mark VII, Mark XLII, Mark L, Hulkbuster)
- Tony Stark character states (casual, business, workshop, suiting up)
- Rich action/animation system
- Outfit management
- State transitions
- Event handling

Makes IMVA as robust and comprehensive as ACE.

Tags: #IMVA #IRON_MAN #COMPREHENSIVE #MANAGER @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

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

logger = get_logger("IMVAComprehensiveManager")


class IMVAState(Enum):
    """IMVA State"""
    IDLE = "idle"
    WALKING = "walking"
    FLYING = "flying"
    WORKING = "working"
    THINKING = "thinking"
    SLEEPING = "sleeping"
    NOTIFYING = "notifying"
    SUITING_UP = "suiting_up"
    SUITING_DOWN = "suiting_down"
    COMBAT = "combat"
    DAMAGED = "damaged"
    CELEBRATING = "celebrating"
    SCANNING = "scanning"


class IMVAType(Enum):
    """IMVA Type"""
    ARMOR = "armor"
    TONY_STARK = "tony_stark"


@dataclass
class IMVAAction:
    """IMVA Action"""
    name: str
    description: str
    action_type: str
    animation: str
    duration: float
    requires_armor: bool = False
    requires_tony: bool = False
    effects: List[str] = field(default_factory=list)
    callback: Optional[Callable] = None


@dataclass
class IMVAOutfit:
    """IMVA Outfit/Armor"""
    name: str
    display_name: str
    outfit_type: str
    mark_level: Optional[int] = None
    description: str = ""
    color_scheme: Dict[str, str] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)
    capabilities: Dict[str, str] = field(default_factory=dict)
    file: str = ""


class IMVAComprehensiveManager:
    """
    IMVA Comprehensive Manager

    Manages all IMVA variants, actions, states, and transitions.
    Makes IMVA as robust as ACE.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize IMVA Comprehensive Manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.scripts_dir = self.project_root / "scripts" / "python"

        # Load configurations
        self.armors_config = self._load_config("imva_armors_config.json")
        self.actions_config = self._load_config("imva_actions_config.json")

        # Current state
        self.current_type: Optional[IMVAType] = None
        self.current_outfit: Optional[str] = None
        self.current_state: IMVAState = IMVAState.IDLE
        self.current_action: Optional[str] = None

        # Active assistant instance
        self.active_assistant = None
        self.assistant_thread = None

        # Action registry
        self.actions: Dict[str, IMVAAction] = {}
        self._register_actions()

        # Outfit registry
        self.armors: Dict[str, IMVAOutfit] = {}
        self.tony_variants: Dict[str, IMVAOutfit] = {}
        self._register_outfits()

        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}

        # State history
        self.state_history: List[Dict[str, Any]] = []

        logger.info("✅ IMVA Comprehensive Manager initialized")
        logger.info(f"   Armors: {len(self.armors)}")
        logger.info(f"   Tony Variants: {len(self.tony_variants)}")
        logger.info(f"   Actions: {len(self.actions)}")

    def _load_config(self, filename: str) -> Dict[str, Any]:
        """Load configuration file"""
        config_file = self.config_dir / filename
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load {filename}: {e}")
        return {}

    def _register_actions(self):
        """Register all actions from config"""
        if "actions" in self.actions_config:
            for action_name, action_data in self.actions_config["actions"].items():
                action = IMVAAction(
                    name=action_data.get("name", action_name),
                    description=action_data.get("description", ""),
                    action_type=action_data.get("type", "state"),
                    animation=action_data.get("animation", ""),
                    duration=self._parse_duration(action_data.get("duration", "continuous")),
                    requires_armor=action_data.get("requires_armor", False),
                    requires_tony=action_data.get("requires_tony", False),
                    effects=action_data.get("effects", [])
                )
                self.actions[action_name] = action

    def _register_outfits(self):
        """Register all outfits from config"""
        # Register armors
        if "armors" in self.armors_config:
            for armor_name, armor_data in self.armors_config["armors"].items():
                outfit = IMVAOutfit(
                    name=armor_data.get("name", armor_name),
                    display_name=armor_data.get("display_name", armor_name),
                    outfit_type=armor_data.get("type", "armor"),
                    mark_level=armor_data.get("mark_level"),
                    description=armor_data.get("description", ""),
                    color_scheme=armor_data.get("color_scheme", {}),
                    features=armor_data.get("features", []),
                    capabilities=armor_data.get("capabilities", {}),
                    file=armor_data.get("file", "")
                )
                self.armors[armor_name] = outfit

        # Register Tony variants
        if "tony_stark_variants" in self.armors_config:
            for tony_name, tony_data in self.armors_config["tony_stark_variants"].items():
                outfit = IMVAOutfit(
                    name=tony_data.get("name", tony_name),
                    display_name=tony_data.get("display_name", tony_name),
                    outfit_type=tony_data.get("type", "character"),
                    description=tony_data.get("description", ""),
                    color_scheme=tony_data.get("color_scheme", {}),
                    features=tony_data.get("features", []),
                    file=tony_data.get("file", "")
                )
                self.tony_variants[tony_name] = outfit

    def _parse_duration(self, duration_str: str) -> float:
        """Parse duration string to float"""
        if duration_str == "continuous":
            return -1.0  # Continuous
        if "seconds" in duration_str or "second" in duration_str:
            # Extract number
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', duration_str)
            if match:
                return float(match.group(1))
        return 2.0  # Default

    def list_armors(self) -> List[str]:
        """List all available armors"""
        return list(self.armors.keys())

    def list_tony_variants(self) -> List[str]:
        """List all available Tony Stark variants"""
        return list(self.tony_variants.keys())

    def list_actions(self, filter_type: Optional[str] = None) -> List[str]:
        """List all available actions"""
        actions = list(self.actions.keys())
        if filter_type:
            # Filter by type
            return [a for a in actions if self.actions[a].action_type == filter_type]
        return actions

    def get_outfit_info(self, outfit_name: str) -> Optional[Dict[str, Any]]:
        """Get outfit information"""
        if outfit_name in self.armors:
            outfit = self.armors[outfit_name]
            return {
                "name": outfit.name,
                "display_name": outfit.display_name,
                "type": outfit.outfit_type,
                "mark_level": outfit.mark_level,
                "description": outfit.description,
                "color_scheme": outfit.color_scheme,
                "features": outfit.features,
                "capabilities": outfit.capabilities
            }
        elif outfit_name in self.tony_variants:
            outfit = self.tony_variants[outfit_name]
            return {
                "name": outfit.name,
                "display_name": outfit.display_name,
                "type": outfit.outfit_type,
                "description": outfit.description,
                "color_scheme": outfit.color_scheme,
                "features": outfit.features
            }
        return None

    def can_perform_action(self, action_name: str) -> tuple[bool, str]:
        """Check if current outfit can perform action"""
        if action_name not in self.actions:
            return (False, f"Action '{action_name}' not found")

        action = self.actions[action_name]

        # Check requirements
        if action.requires_armor:
            if self.current_type != IMVAType.ARMOR:
                return (False, f"Action '{action_name}' requires armor")

        if action.requires_tony:
            if self.current_type != IMVAType.TONY_STARK:
                return (False, f"Action '{action_name}' requires Tony Stark")

        return (True, "Action can be performed")

    def set_outfit(self, outfit_name: str) -> bool:
        """Set current outfit"""
        if outfit_name in self.armors:
            self.current_type = IMVAType.ARMOR
            self.current_outfit = outfit_name
            logger.info(f"✅ Switched to armor: {outfit_name}")
            self._emit_event("outfit_changed", {"outfit": outfit_name, "type": "armor"})
            return True
        elif outfit_name in self.tony_variants:
            self.current_type = IMVAType.TONY_STARK
            self.current_outfit = outfit_name
            logger.info(f"✅ Switched to Tony variant: {outfit_name}")
            self._emit_event("outfit_changed", {"outfit": outfit_name, "type": "tony_stark"})
            return True
        else:
            logger.warning(f"⚠️  Outfit '{outfit_name}' not found")
            return False

    def set_state(self, state: IMVAState):
        """Set current state"""
        old_state = self.current_state
        self.current_state = state

        # Record state change
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "old_state": old_state.value,
            "new_state": state.value,
            "outfit": self.current_outfit
        })

        # Keep only last 100 state changes
        if len(self.state_history) > 100:
            self.state_history.pop(0)

        logger.info(f"🔄 State changed: {old_state.value} → {state.value}")
        self._emit_event("state_changed", {
            "old_state": old_state.value,
            "new_state": state.value
        })

    def perform_action(self, action_name: str) -> bool:
        """Perform an action"""
        can_perform, reason = self.can_perform_action(action_name)
        if not can_perform:
            logger.warning(f"⚠️  Cannot perform action '{action_name}': {reason}")
            return False

        action = self.actions[action_name]
        self.current_action = action_name

        logger.info(f"🎬 Performing action: {action_name}")
        self._emit_event("action_started", {"action": action_name})

        # Map action to state if applicable
        state_mapping = {
            "idle": IMVAState.IDLE,
            "walking": IMVAState.WALKING,
            "flying": IMVAState.FLYING,
            "working": IMVAState.WORKING,
            "thinking": IMVAState.THINKING,
            "sleeping": IMVAState.SLEEPING,
            "notifying": IMVAState.NOTIFYING,
            "suit_up": IMVAState.SUITING_UP,
            "suit_down": IMVAState.SUITING_DOWN,
            "combat_stance": IMVAState.COMBAT,
            "damaged": IMVAState.DAMAGED,
            "celebrating": IMVAState.CELEBRATING,
            "scanning": IMVAState.SCANNING
        }

        if action_name in state_mapping:
            self.set_state(state_mapping[action_name])

        # Execute action callback if available
        if action.callback:
            try:
                action.callback()
            except Exception as e:
                logger.error(f"❌ Action callback error: {e}")

        # If action has duration, schedule completion
        if action.duration > 0:
            threading.Timer(action.duration, self._action_complete, args=[action_name]).start()
        else:
            # Continuous action
            pass

        return True

    def _action_complete(self, action_name: str):
        """Action completion handler"""
        if self.current_action == action_name:
            self.current_action = None
            logger.info(f"✅ Action completed: {action_name}")
            self._emit_event("action_completed", {"action": action_name})

    def launch_assistant(self, outfit_name: Optional[str] = None) -> bool:
        """Launch IMVA assistant with specified outfit"""
        if outfit_name:
            if not self.set_outfit(outfit_name):
                return False
        else:
            # Use default
            default_armor = self.armors_config.get("default_armor", "mark_v")
            if default_armor in self.armors:
                self.set_outfit(default_armor)
            else:
                logger.error("❌ No default armor found")
                return False

        # Get outfit file
        if self.current_outfit in self.armors:
            outfit = self.armors[self.current_outfit]
            assistant_file = outfit.file
        elif self.current_outfit in self.tony_variants:
            outfit = self.tony_variants[self.current_outfit]
            assistant_file = outfit.file
        else:
            logger.error("❌ Current outfit not found")
            return False

        if not assistant_file:
            logger.error(f"❌ No assistant file for outfit '{self.current_outfit}'")
            return False

        # Launch assistant
        assistant_path = self.scripts_dir / assistant_file
        if not assistant_path.exists():
            logger.warning(f"⚠️  Assistant file not found: {assistant_path}")
            logger.info(f"   Using fallback: jarvis_mark_v_desktop_assistant.py")
            assistant_path = self.scripts_dir / "jarvis_mark_v_desktop_assistant.py"

        try:
            # Import and launch
            import importlib.util
            spec = importlib.util.spec_from_file_location("imva_assistant", assistant_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find main class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.endswith("Assistant") and
                        hasattr(attr, "start")):
                        self.active_assistant = attr()
                        self.assistant_thread = threading.Thread(
                            target=self.active_assistant.start,
                            daemon=True
                        )
                        self.assistant_thread.start()
                        logger.info(f"✅ Launched IMVA assistant: {self.current_outfit}")
                        return True
        except Exception as e:
            logger.error(f"❌ Error launching assistant: {e}")
            import traceback
            traceback.print_exc()

        return False

    def register_event_handler(self, event_name: str, handler: Callable):
        """Register event handler"""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def _emit_event(self, event_name: str, data: Dict[str, Any]):
        """Emit event to handlers"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"❌ Event handler error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "current_type": self.current_type.value if self.current_type else None,
            "current_outfit": self.current_outfit,
            "current_state": self.current_state.value,
            "current_action": self.current_action,
            "available_armors": len(self.armors),
            "available_tony_variants": len(self.tony_variants),
            "available_actions": len(self.actions),
            "assistant_active": self.active_assistant is not None
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="IMVA Comprehensive Manager")
    parser.add_argument('--list-armors', action='store_true', help='List all armors')
    parser.add_argument('--list-tony', action='store_true', help='List all Tony variants')
    parser.add_argument('--list-actions', action='store_true', help='List all actions')
    parser.add_argument('--outfit', type=str, help='Set outfit')
    parser.add_argument('--action', type=str, help='Perform action')
    parser.add_argument('--launch', type=str, help='Launch assistant with outfit')
    parser.add_argument('--status', action='store_true', help='Show status')

    args = parser.parse_args()

    manager = IMVAComprehensiveManager()

    if args.list_armors:
        print("\n🦾 Available Armors:")
        print("=" * 80)
        for armor_name in manager.list_armors():
            info = manager.get_outfit_info(armor_name)
            if info:
                print(f"  • {info['display_name']} ({armor_name})")
                print(f"    {info['description']}")
                if info.get('mark_level'):
                    print(f"    Mark Level: {info['mark_level']}")
        return 0

    if args.list_tony:
        print("\n👤 Available Tony Stark Variants:")
        print("=" * 80)
        for tony_name in manager.list_tony_variants():
            info = manager.get_outfit_info(tony_name)
            if info:
                print(f"  • {info['display_name']} ({tony_name})")
                print(f"    {info['description']}")
        return 0

    if args.list_actions:
        print("\n🎬 Available Actions:")
        print("=" * 80)
        for action_name in manager.list_actions():
            action = manager.actions[action_name]
            print(f"  • {action.name} ({action_name})")
            print(f"    Type: {action.action_type}")
            print(f"    Description: {action.description}")
        return 0

    if args.outfit:
        if manager.set_outfit(args.outfit):
            print(f"✅ Switched to outfit: {args.outfit}")
        else:
            print(f"❌ Could not switch to outfit: {args.outfit}")
        return 0

    if args.action:
        if manager.perform_action(args.action):
            print(f"✅ Performing action: {args.action}")
        else:
            print(f"❌ Could not perform action: {args.action}")
        return 0

    if args.launch:
        if manager.launch_assistant(args.launch):
            print(f"✅ Launched IMVA: {args.launch}")
            print("   Press Ctrl+C to stop")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n⏹️  Stopping IMVA...")
        else:
            print(f"❌ Could not launch IMVA: {args.launch}")
        return 0

    if args.status:
        status = manager.get_status()
        print("\n📊 IMVA Status:")
        print("=" * 80)
        for key, value in status.items():
            print(f"  {key}: {value}")
        return 0

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":


    sys.exit(main())