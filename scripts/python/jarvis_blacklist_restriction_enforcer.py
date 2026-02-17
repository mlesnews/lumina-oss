#!/usr/bin/env python3
"""
JARVIS Blacklist/Restriction Enforcer

Enforces all blacklists, restrictions, and negative entries across the system.
Integrates with penalty system to apply -xp for violations.

@JARVIS @PENALTY #BLACKLIST #RESTRICTION #POLICY #ENFORCEMENT
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISBlacklistEnforcer")

# Import penalty system
try:
    from jarvis_policy_violation_penalty import get_penalty_system, PolicyType, ViolationSeverity
    PENALTY_AVAILABLE = True
except ImportError:
    PENALTY_AVAILABLE = False
    get_penalty_system = None
    PolicyType = None
    ViolationSeverity = None
    logger.warning("⚠️  Penalty system not available")


class RestrictionType(Enum):
    """Types of restrictions"""
    CLOUD_API_BLOCKED = "cloud_api_blocked"
    FORBIDDEN_MODEL = "forbidden_model"
    RESTRICTED_COMMAND = "restricted_command"
    AIR_GAP_VIOLATION = "air_gap_violation"
    SECURITY_VIOLATION = "security_violation"
    FILE_ACCESS_RESTRICTED = "file_access_restricted"
    NETWORK_RESTRICTED = "network_restricted"
    TRANSACTION_BLOCKED = "transaction_blocked"
    CURSOR_MENU_INTERACTION = "cursor_menu_interaction"
    CURSOR_RIGHT_CLICK = "cursor_right_click"
    CURSOR_CLIPBOARD_OPERATION = "cursor_clipboard_operation"
    MANUS_SELF_TEST_BLOCKED = "manus_self_test_blocked"  # AI/JARVIS self-testing MANUS CONTROL when operator is active


@dataclass
class BlacklistEntry:
    """Blacklist entry"""
    entry_id: str
    restriction_type: RestrictionType
    value: str
    description: str
    severity: ViolationSeverity
    source: str  # config file or system
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISBlacklistRestrictionEnforcer:
    """
    JARVIS Blacklist/Restriction Enforcer

    Enforces all blacklists, restrictions, and negative entries.
    Integrates with penalty system for violations.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "jarvis_blacklists"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Blacklists and restrictions
        self.blacklists: Dict[RestrictionType, Set[str]] = {}
        self.restrictions: Dict[RestrictionType, Dict[str, Any]] = {}

        # Load all blacklists and restrictions
        self._load_blacklists()

        # Initialize Force-Sensitive Listings integration
        self.force_listings = None
        try:
            from jarvis_force_sensitive_listings import get_force_listings
            self.force_listings = get_force_listings(project_root)
            self.logger.info("✅ Force-Sensitive Listings integrated")
        except Exception as e:
            self.logger.warning(f"⚠️  Force-Sensitive Listings not available: {e}")

        # Initialize penalty system
        self.penalty_system = None
        if PENALTY_AVAILABLE:
            try:
                self.penalty_system = get_penalty_system(project_root)
                self.logger.info("✅ Penalty system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Penalty system initialization failed: {e}")

        self.logger.info(f"✅ JARVIS Blacklist/Restriction Enforcer initialized")
        self.logger.info(f"   Loaded {sum(len(v) for v in self.blacklists.values())} blacklist entries")

    def _load_blacklists(self):
        """Load all blacklists and restrictions from config files"""

        # 1. Cloud API Blocker
        self._load_cloud_api_blocker()

        # 2. Forbidden Models
        self._load_forbidden_models()

        # 3. Restricted Commands
        self._load_restricted_commands()

        # 4. Air-Gap Restrictions
        self._load_air_gap_restrictions()

        # 5. Security Restrictions
        self._load_security_restrictions()

        # 6. Cursor IDE Interaction Restrictions
        self._load_cursor_ide_restrictions()

    def _load_cloud_api_blocker(self):
        """Load cloud API blocker blacklist"""
        try:
            blocker_file = self.project_root / "config" / "cloud_api_blocker.json"
            if blocker_file.exists():
                with open(blocker_file, 'r') as f:
                    blocker_config = json.load(f)

                if blocker_config.get("enabled", False):
                    blocked_providers = blocker_config.get("blocked_providers", [])
                    self.blacklists[RestrictionType.CLOUD_API_BLOCKED] = set(blocked_providers)
                    self.restrictions[RestrictionType.CLOUD_API_BLOCKED] = {
                        "enabled": True,
                        "emergency_mode": blocker_config.get("emergency_mode", False),
                        "reason": blocker_config.get("reason", "")
                    }
                    self.logger.info(f"   ✅ Loaded {len(blocked_providers)} blocked cloud API providers")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load cloud API blocker: {e}")

    def _load_forbidden_models(self):
        """Load forbidden models blacklist"""
        try:
            council_file = self.project_root / "config" / "council_policy.json"
            if council_file.exists():
                with open(council_file, 'r') as f:
                    council_config = json.load(f)

                model_rules = council_config.get("model_rules", {})
                forbidden_models = model_rules.get("forbidden_models", [])
                self.blacklists[RestrictionType.FORBIDDEN_MODEL] = set(forbidden_models)
                self.restrictions[RestrictionType.FORBIDDEN_MODEL] = {
                    "enforcement": council_config.get("jedi_council_policy", {}).get("enforcement", "fail_closed")
                }
                if forbidden_models:
                    self.logger.info(f"   ✅ Loaded {len(forbidden_models)} forbidden models")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load forbidden models: {e}")

    def _load_restricted_commands(self):
        """Load restricted commands blacklist"""
        try:
            pfsense_file = self.project_root / "config" / "lumina_pfsense_ssh_config.json"
            if pfsense_file.exists():
                with open(pfsense_file, 'r') as f:
                    pfsense_config = json.load(f)

                # Check operations.ssh_commands.restricted_commands
                operations = pfsense_config.get("operations", {})
                ssh_commands = operations.get("ssh_commands", {})
                restricted_commands = ssh_commands.get("restricted_commands", [])

                self.blacklists[RestrictionType.RESTRICTED_COMMAND] = set(restricted_commands)
                self.restrictions[RestrictionType.RESTRICTED_COMMAND] = {
                    "context": "pfsense_ssh"
                }
                if restricted_commands:
                    self.logger.info(f"   ✅ Loaded {len(restricted_commands)} restricted commands")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load restricted commands: {e}")

    def _load_air_gap_restrictions(self):
        """Load air-gap mode restrictions"""
        try:
            # Check multiple config files for air-gap settings
            air_gap_configs = [
                ("config/kilo_code_optimized_config.json", "security.air_gap_mode"),
                ("config/multi_ide_optimal_settings.json", "common_settings.hybrid_orchestration"),
            ]

            air_gap_enabled = False
            block_cloud_unless_approved = False

            for config_path, key_path in air_gap_configs:
                config_file = self.project_root / config_path
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)

                    # Navigate to key path
                    keys = key_path.split(".")
                    value = config
                    for key in keys:
                        if isinstance(value, dict):
                            value = value.get(key, {})

                    if isinstance(value, dict):
                        if value.get("enabled") or value.get("air_gap_mode"):
                            air_gap_enabled = True
                        if value.get("block_cloud_unless_approved"):
                            block_cloud_unless_approved = True

            if air_gap_enabled or block_cloud_unless_approved:
                self.restrictions[RestrictionType.AIR_GAP_VIOLATION] = {
                    "air_gap_enabled": air_gap_enabled,
                    "block_cloud_unless_approved": block_cloud_unless_approved
                }
                self.logger.info("   ✅ Loaded air-gap restrictions")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load air-gap restrictions: {e}")

    def _load_security_restrictions(self):
        """Load security restrictions"""
        # Security restrictions are typically hardcoded in code
        # But we can track common patterns
        self.restrictions[RestrictionType.SECURITY_VIOLATION] = {
            "restricted_dirs": [
                "C:\\Windows\\System32",
                "/etc",
                "/bin",
                "/sbin",
                "/usr/bin",
                "/usr/sbin"
            ],
            "restricted_extensions": [".exe", ".bat", ".cmd", ".sh", ".ps1"]
        }
        self.logger.info("   ✅ Loaded security restrictions")

    def _load_cursor_ide_restrictions(self):
        """Load Cursor IDE interaction restrictions"""
        # Block MANUS from interacting with Cursor IDE menus, popups, and clipboard
        self.restrictions[RestrictionType.CURSOR_MENU_INTERACTION] = {
            "blocked": True,
            "reason": "MANUS must not interact with Cursor IDE menus or popups",
            "blocked_actions": [
                "menu_click",
                "popup_interaction",
                "dialog_interaction",
                "context_menu",
                "dropdown_menu"
            ]
        }

        self.restrictions[RestrictionType.CURSOR_RIGHT_CLICK] = {
            "blocked": True,
            "reason": "MANUS must not perform right-click operations in Cursor IDE",
            "blocked_actions": [
                "right_click",
                "context_menu",
                "Button-3"
            ]
        }

        self.restrictions[RestrictionType.CURSOR_CLIPBOARD_OPERATION] = {
            "blocked": True,
            "reason": "MANUS must not perform clipboard operations (cut/copy/paste) in Cursor IDE",
            "blocked_actions": [
                "clipboard_copy",
                "clipboard_cut",
                "clipboard_paste",
                "Ctrl+C",
                "Ctrl+X",
                "Ctrl+V"
            ]
        }

        self.logger.info("   ✅ Loaded Cursor IDE interaction restrictions")

    def check_cloud_api(self, provider: str) -> tuple[bool, Optional[str]]:
        """
        Check if cloud API provider is blocked

        Returns:
            (allowed: bool, reason: str)
        """
        blocked = self.blacklists.get(RestrictionType.CLOUD_API_BLOCKED, set())

        if provider.lower() in [p.lower() for p in blocked]:
            restriction = self.restrictions.get(RestrictionType.CLOUD_API_BLOCKED, {})
            reason = restriction.get("reason", "Cloud API provider is blocked by policy")
            return False, reason

        return True, None

    def check_model(self, model: str) -> tuple[bool, Optional[str]]:
        """
        Check if model is forbidden

        Returns:
            (allowed: bool, reason: str)
        """
        forbidden = self.blacklists.get(RestrictionType.FORBIDDEN_MODEL, set())

        if model.lower() in [m.lower() for m in forbidden]:
            return False, f"Model '{model}' is forbidden by JEDI Council policy"

        return True, None

    def check_command(self, command: str, context: str = "general") -> tuple[bool, Optional[str]]:
        """
        Check if command is restricted

        Returns:
            (allowed: bool, reason: str)
        """
        restricted = self.blacklists.get(RestrictionType.RESTRICTED_COMMAND, set())

        # Check if command or any part of it is restricted
        command_parts = command.split()
        if command_parts:
            base_command = command_parts[0].lower()
            if base_command in [c.lower() for c in restricted]:
                return False, f"Command '{base_command}' is restricted by policy"

        return True, None

    def check_air_gap(self, action: str, requires_cloud: bool = False) -> tuple[bool, Optional[str]]:
        """
        Check if action violates air-gap mode

        Returns:
            (allowed: bool, reason: str)
        """
        restriction = self.restrictions.get(RestrictionType.AIR_GAP_VIOLATION, {})

        if restriction.get("air_gap_enabled") and requires_cloud:
            if not restriction.get("block_cloud_unless_approved"):
                return False, "Air-gap mode enabled - cloud access blocked"

        return True, None

    def check_file_access(self, file_path: str) -> tuple[bool, Optional[str]]:
        try:
            """
            Check if file access is restricted

            Returns:
                (allowed: bool, reason: str)
            """
            restriction = self.restrictions.get(RestrictionType.SECURITY_VIOLATION, {})
            restricted_dirs = restriction.get("restricted_dirs", [])
            restricted_extensions = restriction.get("restricted_extensions", [])

            # Check restricted directories
            for restricted_dir in restricted_dirs:
                if restricted_dir.lower() in file_path.lower():
                    return False, f"Access to restricted directory '{restricted_dir}' is blocked"

            # Check restricted extensions
            file_path_obj = Path(file_path)
            if file_path_obj.suffix.lower() in restricted_extensions:
                return False, f"Access to '{file_path_obj.suffix}' files is restricted"

            return True, None

        except Exception as e:
            self.logger.error(f"Error in check_file_access: {e}", exc_info=True)
            raise
    def enforce_restriction(
        self,
        restriction_type: RestrictionType,
        action: str,
        value: str,
        check_func: callable,
        *args,
        **kwargs
    ) -> tuple[bool, Optional[Any]]:
        """
        Enforce restriction with penalty if violated

        Args:
            restriction_type: Type of restriction
            action: Action being attempted
            value: Value being checked (provider, model, command, etc.)
            check_func: Function that returns (allowed: bool, reason: str) - should accept action as parameter

        Returns:
            (allowed: bool, violation: Optional[PolicyViolation])
        """
        try:
            allowed, reason = check_func(action)

            if not allowed:
                # Restriction violated - record and apply penalty
                if self.penalty_system:
                    severity = self._determine_severity(restriction_type)
                    violation = self.penalty_system.record_violation(
                        policy_type=PolicyType.COMPANY_POLICY,
                        action=action,
                        description=f"{restriction_type.value}: {reason} (Value: {value})",
                        severity=severity,
                        blocked=True,
                        metadata={
                            "restriction_type": restriction_type.value,
                            "value": value,
                            "reason": reason
                        }
                    )
                    self.logger.error(
                        f"🚫 BLACKLIST VIOLATION: {restriction_type.value} - "
                        f"{action} with '{value}' - "
                        f"Penalty: {violation.xp_penalty} XP (Current XP: {self.penalty_system.jarvis_xp.current_xp})"
                    )
                    return False, violation
                else:
                    self.logger.error(
                        f"🚫 BLACKLIST VIOLATION: {restriction_type.value} - "
                        f"{action} with '{value}' - {reason}"
                    )
                    return False, None
            else:
                # Restriction compliant
                return True, None

        except Exception as e:
            self.logger.error(f"Error enforcing restriction: {e}")
            return False, None

    def check_cursor_menu_interaction(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Check if Cursor IDE menu interaction is blocked

        Returns:
            (allowed: bool, reason: str)
        """
        restriction = self.restrictions.get(RestrictionType.CURSOR_MENU_INTERACTION, {})

        if restriction.get("blocked", False):
            blocked_actions = restriction.get("blocked_actions", [])
            if any(blocked_action in action.lower() for blocked_action in blocked_actions):
                return False, restriction.get("reason", "Cursor IDE menu interaction blocked")

        return True, None

    def check_cursor_right_click(self, action: str) -> tuple[bool, Optional[str]]:
        """
        Check if Cursor IDE right-click is blocked

        Returns:
            (allowed: bool, reason: str)
        """
        restriction = self.restrictions.get(RestrictionType.CURSOR_RIGHT_CLICK, {})

        if restriction.get("blocked", False):
            blocked_actions = restriction.get("blocked_actions", [])
            if any(blocked_action in action.lower() for blocked_action in blocked_actions):
                return False, restriction.get("reason", "Cursor IDE right-click blocked")

        return True, None

    def check_cursor_clipboard(self, operation: str) -> tuple[bool, Optional[str]]:
        """
        Check if Cursor IDE clipboard operation is blocked

        Returns:
            (allowed: bool, reason: str)
        """
        restriction = self.restrictions.get(RestrictionType.CURSOR_CLIPBOARD_OPERATION, {})

        if restriction.get("blocked", False):
            blocked_actions = restriction.get("blocked_actions", [])
            if any(blocked_action in operation.lower() for blocked_action in blocked_actions):
                return False, restriction.get("reason", "Cursor IDE clipboard operation blocked")

        return True, None

    def _determine_severity(self, restriction_type: RestrictionType) -> ViolationSeverity:
        """Determine violation severity based on restriction type"""
        if not ViolationSeverity:
            return None

        severity_map = {
            RestrictionType.CLOUD_API_BLOCKED: ViolationSeverity.MAJOR,
            RestrictionType.FORBIDDEN_MODEL: ViolationSeverity.MAJOR,
            RestrictionType.RESTRICTED_COMMAND: ViolationSeverity.CRITICAL,
            RestrictionType.AIR_GAP_VIOLATION: ViolationSeverity.MAJOR,
            RestrictionType.SECURITY_VIOLATION: ViolationSeverity.CRITICAL,
            RestrictionType.FILE_ACCESS_RESTRICTED: ViolationSeverity.CRITICAL,
            RestrictionType.NETWORK_RESTRICTED: ViolationSeverity.MAJOR,
            RestrictionType.TRANSACTION_BLOCKED: ViolationSeverity.CRITICAL,
            RestrictionType.CURSOR_MENU_INTERACTION: ViolationSeverity.MAJOR,
            RestrictionType.CURSOR_RIGHT_CLICK: ViolationSeverity.MAJOR,
            RestrictionType.CURSOR_CLIPBOARD_OPERATION: ViolationSeverity.MAJOR,
            RestrictionType.MANUS_SELF_TEST_BLOCKED: ViolationSeverity.MAJOR,  # -2 DKP, -XP penalty
        }

        return severity_map.get(restriction_type, ViolationSeverity.MODERATE)

    def get_all_blacklists(self) -> Dict[str, List[str]]:
        """Get all blacklists as dictionary"""
        return {
            restriction_type.value: list(blacklist)
            for restriction_type, blacklist in self.blacklists.items()
        }

    def get_all_restrictions(self) -> Dict[str, Dict[str, Any]]:
        """Get all restrictions as dictionary"""
        return {
            restriction_type.value: restriction
            for restriction_type, restriction in self.restrictions.items()
        }


# Global instance
_global_enforcer: Optional[JARVISBlacklistRestrictionEnforcer] = None


def get_blacklist_enforcer(project_root: Optional[Path] = None) -> JARVISBlacklistRestrictionEnforcer:
    try:
        """Get or create global blacklist enforcer instance"""
        global _global_enforcer

        if _global_enforcer is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_enforcer = JARVISBlacklistRestrictionEnforcer(project_root)

        return _global_enforcer


    except Exception as e:
        logger.error(f"Error in get_blacklist_enforcer: {e}", exc_info=True)
        raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Blacklist/Restriction Enforcer")
        parser.add_argument("--list", action="store_true", help="List all blacklists and restrictions")
        parser.add_argument("--check-cloud", type=str, help="Check if cloud API provider is blocked")
        parser.add_argument("--check-model", type=str, help="Check if model is forbidden")
        parser.add_argument("--check-command", type=str, help="Check if command is restricted")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        enforcer = JARVISBlacklistRestrictionEnforcer(project_root)

        if args.list:
            blacklists = enforcer.get_all_blacklists()
            restrictions = enforcer.get_all_restrictions()

            print("\n" + "="*80)
            print("JARVIS BLACKLISTS AND RESTRICTIONS")
            print("="*80)

            print("\n📋 Blacklists:")
            for restriction_type, entries in blacklists.items():
                print(f"   {restriction_type}: {len(entries)} entries")
                for entry in entries[:5]:  # Show first 5
                    print(f"      - {entry}")
                if len(entries) > 5:
                    print(f"      ... and {len(entries) - 5} more")

            print("\n🔒 Restrictions:")
            for restriction_type, config in restrictions.items():
                print(f"   {restriction_type}: {config}")

            print("="*80)

        if args.check_cloud:
            allowed, reason = enforcer.check_cloud_api(args.check_cloud)
            print(f"{'✅ ALLOWED' if allowed else '🚫 BLOCKED'}: {args.check_cloud}")
            if not allowed:
                print(f"   Reason: {reason}")

        if args.check_model:
            allowed, reason = enforcer.check_model(args.check_model)
            print(f"{'✅ ALLOWED' if allowed else '🚫 BLOCKED'}: {args.check_model}")
            if not allowed:
                print(f"   Reason: {reason}")

        if args.check_command:
            allowed, reason = enforcer.check_command(args.check_command)
            print(f"{'✅ ALLOWED' if allowed else '🚫 BLOCKED'}: {args.check_command}")
            if not allowed:
                print(f"   Reason: {reason}")

        if not any([args.list, args.check_cloud, args.check_model, args.check_command]):
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()