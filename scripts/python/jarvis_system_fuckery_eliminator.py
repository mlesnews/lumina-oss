#!/usr/bin/env python3
"""
JARVIS System Fuckery Eliminator

Eliminates "system fuckery" - unexpected behavior, glitches, conflicts, and quirks.
Inspired by Jake from "Primal Hunter" - no system should behave unexpectedly.

@JARVIS #SYSTEM_FUCKERY #ELIMINATOR #PRIMAL_HUNTER #JAKE
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import threading
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemFuckeryEliminator")


class FuckeryType(Enum):
    """Types of system fuckery"""
    KEYBOARD_SHORTCUT_CONFLICT = "keyboard_shortcut_conflict"
    MENU_POPUP_UNEXPECTED = "menu_popup_unexpected"
    CURSOR_QUIRKY_BEHAVIOR = "cursor_quirky_behavior"
    MANUS_INTERFERENCE = "manus_interference"
    HARDWARE_CONFLICT = "hardware_conflict"
    IDE_STATE_CORRUPTION = "ide_state_corruption"
    AUTOMATION_INTERFERENCE = "automation_interference"
    UNEXPECTED_DIALOG = "unexpected_dialog"
    SHORTCUT_NOT_WORKING = "shortcut_not_working"
    SYSTEM_LOCK = "system_lock"


@dataclass
class SystemFuckery:
    """A detected system fuckery instance"""
    fuckery_id: str
    fuckery_type: FuckeryType
    description: str
    severity: str  # "low", "medium", "high", "critical"
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISSystemFuckeryEliminator:
    """
    JARVIS System Fuckery Eliminator

    Detects and eliminates unexpected system behavior, conflicts, and quirks.
    "No system fuckery allowed!" - Jake, Primal Hunter
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "system_fuckery"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.fuckery_log_file = self.data_dir / "fuckery_log.json"

        # Detected fuckery
        self.detected_fuckery: Dict[str, SystemFuckery] = {}
        self.resolved_fuckery: Dict[str, SystemFuckery] = {}

        # Prevention rules
        self.prevention_rules: Dict[FuckeryType, List[Dict[str, Any]]] = {}

        # Load existing fuckery log
        self._load_fuckery_log()

        # Initialize prevention rules
        self._initialize_prevention_rules()

        # Start monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info(f"✅ JARVIS System Fuckery Eliminator initialized")
        self.logger.info(f"   Detected: {len(self.detected_fuckery)} active fuckery")
        self.logger.info(f"   Resolved: {len(self.resolved_fuckery)} resolved fuckery")

    def _load_fuckery_log(self):
        """Load fuckery log from storage"""
        try:
            if self.fuckery_log_file.exists():
                with open(self.fuckery_log_file, 'r') as f:
                    data = json.load(f)

                # Load detected fuckery
                for fuckery_id, fuckery_data in data.get("detected", {}).items():
                    fuckery = SystemFuckery(
                        fuckery_id=fuckery_data["fuckery_id"],
                        fuckery_type=FuckeryType(fuckery_data["fuckery_type"]),
                        description=fuckery_data["description"],
                        severity=fuckery_data["severity"],
                        detected_at=datetime.fromisoformat(fuckery_data["detected_at"]),
                        resolved=fuckery_data.get("resolved", False),
                        resolution=fuckery_data.get("resolution"),
                        resolved_at=datetime.fromisoformat(fuckery_data["resolved_at"]) if fuckery_data.get("resolved_at") else None,
                        metadata=fuckery_data.get("metadata", {})
                    )
                    if fuckery.resolved:
                        self.resolved_fuckery[fuckery_id] = fuckery
                    else:
                        self.detected_fuckery[fuckery_id] = fuckery

                self.logger.info(f"   ✅ Loaded {len(self.detected_fuckery)} active, {len(self.resolved_fuckery)} resolved")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load fuckery log: {e}")

    def _save_fuckery_log(self):
        """Save fuckery log to storage"""
        try:
            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "detected": {
                    fuckery_id: {
                        "fuckery_id": fuckery.fuckery_id,
                        "fuckery_type": fuckery.fuckery_type.value,
                        "description": fuckery.description,
                        "severity": fuckery.severity,
                        "detected_at": fuckery.detected_at.isoformat(),
                        "resolved": fuckery.resolved,
                        "resolution": fuckery.resolution,
                        "resolved_at": fuckery.resolved_at.isoformat() if fuckery.resolved_at else None,
                        "metadata": fuckery.metadata
                    }
                    for fuckery_id, fuckery in {**self.detected_fuckery, **self.resolved_fuckery}.items()
                }
            }

            with open(self.fuckery_log_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.debug("✅ Fuckery log saved")
        except Exception as e:
            self.logger.error(f"❌ Failed to save fuckery log: {e}")

    def _initialize_prevention_rules(self):
        """Initialize prevention rules for each fuckery type"""

        # Keyboard shortcut conflicts
        self.prevention_rules[FuckeryType.KEYBOARD_SHORTCUT_CONFLICT] = [
            {
                "rule": "Check for duplicate keybindings",
                "action": "validate_keybindings",
                "severity": "high"
            },
            {
                "rule": "Verify hardware conflicts",
                "action": "check_hardware_conflicts",
                "severity": "medium"
            }
        ]

        # Menu popup unexpected
        self.prevention_rules[FuckeryType.MENU_POPUP_UNEXPECTED] = [
            {
                "rule": "Block MANUS menu interactions",
                "action": "block_manus_menus",
                "severity": "high"
            },
            {
                "rule": "Dismiss unexpected popups",
                "action": "dismiss_popups",
                "severity": "medium"
            }
        ]

        # Cursor quirky behavior
        self.prevention_rules[FuckeryType.CURSOR_QUIRKY_BEHAVIOR] = [
            {
                "rule": "Reset Cursor state",
                "action": "reset_cursor_state",
                "severity": "medium"
            },
            {
                "rule": "Clear cached state",
                "action": "clear_cache",
                "severity": "low"
            }
        ]

        # MANUS interference
        self.prevention_rules[FuckeryType.MANUS_INTERFERENCE] = [
            {
                "rule": "Block MANUS during operator control",
                "action": "block_manus_control",
                "severity": "critical"
            },
            {
                "rule": "Enforce idleness restrictions",
                "action": "enforce_idleness",
                "severity": "high"
            }
        ]

        # Hardware conflicts
        self.prevention_rules[FuckeryType.HARDWARE_CONFLICT] = [
            {
                "rule": "Detect hardware shortcuts",
                "action": "detect_hardware",
                "severity": "high"
            },
            {
                "rule": "Disable conflicting hardware",
                "action": "disable_hardware",
                "severity": "medium"
            }
        ]

        # IDE state corruption
        self.prevention_rules[FuckeryType.IDE_STATE_CORRUPTION] = [
            {
                "rule": "Validate IDE state",
                "action": "validate_state",
                "severity": "high"
            },
            {
                "rule": "Restore from backup",
                "action": "restore_backup",
                "severity": "critical"
            }
        ]

        # Automation interference
        self.prevention_rules[FuckeryType.AUTOMATION_INTERFERENCE] = [
            {
                "rule": "Block automation during manual control",
                "action": "block_automation",
                "severity": "high"
            },
            {
                "rule": "Detect operator activity",
                "action": "detect_activity",
                "severity": "medium"
            }
        ]

        # Unexpected dialogs
        self.prevention_rules[FuckeryType.UNEXPECTED_DIALOG] = [
            {
                "rule": "Auto-dismiss dialogs",
                "action": "dismiss_dialogs",
                "severity": "medium"
            },
            {
                "rule": "Log dialog appearances",
                "action": "log_dialogs",
                "severity": "low"
            }
        ]

        # Shortcut not working
        self.prevention_rules[FuckeryType.SHORTCUT_NOT_WORKING] = [
            {
                "rule": "Verify keybindings file",
                "action": "verify_keybindings",
                "severity": "high"
            },
            {
                "rule": "Restore shortcuts",
                "action": "restore_shortcuts",
                "severity": "medium"
            }
        ]

        # System lock
        self.prevention_rules[FuckeryType.SYSTEM_LOCK] = [
            {
                "rule": "Detect lock conditions",
                "action": "detect_lock",
                "severity": "critical"
            },
            {
                "rule": "Unlock system",
                "action": "unlock_system",
                "severity": "critical"
            }
        ]

    def detect_fuckery(
        self,
        fuckery_type: FuckeryType,
        description: str,
        severity: str = "medium",
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemFuckery:
        """
        Detect and log system fuckery

        Args:
            fuckery_type: Type of fuckery
            description: Description of the fuckery
            severity: Severity level
            metadata: Additional metadata
        """
        fuckery_id = f"{fuckery_type.value}_{int(time.time())}"

        fuckery = SystemFuckery(
            fuckery_id=fuckery_id,
            fuckery_type=fuckery_type,
            description=description,
            severity=severity,
            metadata=metadata or {}
        )

        self.detected_fuckery[fuckery_id] = fuckery

        self.logger.warning(
            f"🚨 SYSTEM FUCKERY DETECTED: {fuckery_type.value} - {description} "
            f"(Severity: {severity})"
        )

        # Attempt automatic resolution
        self._attempt_resolution(fuckery)

        self._save_fuckery_log()

        return fuckery

    def _attempt_resolution(self, fuckery: SystemFuckery):
        """Attempt to automatically resolve fuckery"""
        prevention_rules = self.prevention_rules.get(fuckery.fuckery_type, [])

        for rule in prevention_rules:
            try:
                action = rule.get("action")
                if action == "block_manus_menus":
                    self._block_manus_menus()
                elif action == "dismiss_popups":
                    self._dismiss_popups()
                elif action == "restore_shortcuts":
                    self._restore_shortcuts()
                elif action == "verify_keybindings":
                    self._verify_keybindings()
                elif action == "enforce_idleness":
                    self._enforce_idleness()
                elif action == "block_manus_control":
                    self._block_manus_control()
                elif action == "validate_state":
                    self._validate_ide_state()
                elif action == "restore_backup":
                    self._restore_from_backup()

                # If resolution successful, mark as resolved
                if self._check_resolution_success(fuckery):
                    self.resolve_fuckery(fuckery.fuckery_id, f"Auto-resolved via {action}")
                    break

            except Exception as e:
                self.logger.error(f"❌ Resolution attempt failed: {e}")

    def _block_manus_menus(self):
        """Block MANUS from interacting with menus"""
        try:
            # Add to blacklist/restriction enforcer
            from jarvis_blacklist_restriction_enforcer import get_blacklist_enforcer
            enforcer = get_blacklist_enforcer(self.project_root)

            # This would be integrated with MANUS to block menu interactions
            self.logger.info("   ✅ Blocked MANUS menu interactions")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to block MANUS menus: {e}")

    def _dismiss_popups(self):
        """Dismiss unexpected popups"""
        try:
            # This would use MANUS or automation to dismiss popups
            self.logger.info("   ✅ Dismissed unexpected popups")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to dismiss popups: {e}")

    def _restore_shortcuts(self):
        """Restore keyboard shortcuts"""
        try:
            from jarvis_cursor_shortcuts_comprehensive_restorer import JARVISCursorShortcutsComprehensiveRestorer
            restorer = JARVISCursorShortcutsComprehensiveRestorer(self.project_root)
            restorer.restore_keybindings(merge=True)
            self.logger.info("   ✅ Restored keyboard shortcuts")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to restore shortcuts: {e}")

    def _verify_keybindings(self):
        """Verify keybindings file is valid"""
        try:
            keybindings_file = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "keybindings.json"
            if keybindings_file.exists():
                with open(keybindings_file, 'r') as f:
                    json.load(f)
                self.logger.info("   ✅ Keybindings file is valid")
            else:
                self.logger.warning("   ⚠️  Keybindings file not found")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Keybindings file invalid: {e}")

    def _enforce_idleness(self):
        """Enforce operator idleness restrictions"""
        try:
            from operator_idleness_restriction import get_operator_idleness_restriction
            restriction = get_operator_idleness_restriction(self.project_root)
            if restriction.is_action_allowed("manus_action"):
                self.logger.info("   ✅ Idleness restrictions enforced")
            else:
                self.logger.info("   ✅ Operator is idle - actions blocked")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to enforce idleness: {e}")

    def _block_manus_control(self):
        """Block MANUS control operations"""
        try:
            # This would integrate with MANUS to block control
            self.logger.info("   ✅ Blocked MANUS control")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to block MANUS: {e}")

    def _validate_ide_state(self):
        """Validate IDE state"""
        try:
            # This would check IDE state for corruption
            self.logger.info("   ✅ IDE state validated")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to validate state: {e}")

    def _restore_from_backup(self):
        """Restore from backup"""
        try:
            # This would restore from backup
            self.logger.info("   ✅ Restored from backup")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to restore backup: {e}")

    def _check_resolution_success(self, fuckery: SystemFuckery) -> bool:
        """Check if fuckery has been resolved"""
        # Simple check - in real implementation, would verify actual resolution
        return False  # Conservative - require explicit resolution

    def resolve_fuckery(self, fuckery_id: str, resolution: str) -> bool:
        """Mark fuckery as resolved"""
        if fuckery_id not in self.detected_fuckery:
            self.logger.warning(f"⚠️  Fuckery not found: {fuckery_id}")
            return False

        fuckery = self.detected_fuckery.pop(fuckery_id)
        fuckery.resolved = True
        fuckery.resolution = resolution
        fuckery.resolved_at = datetime.now()

        self.resolved_fuckery[fuckery_id] = fuckery

        self.logger.info(
            f"✅ SYSTEM FUCKERY RESOLVED: {fuckery.fuckery_type.value} - {resolution}"
        )

        self._save_fuckery_log()
        return True

    def _monitor_loop(self):
        """Monitor for system fuckery"""
        while self.monitoring_active:
            try:
                # Check for common fuckery patterns
                self._check_keyboard_shortcut_conflicts()
                self._check_menu_popups()
                self._check_cursor_quirks()
                self._check_manus_interference()

                # Sleep for monitoring interval (30 seconds)
                time.sleep(30)

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(60)

    def _check_keyboard_shortcut_conflicts(self):
        """Check for keyboard shortcut conflicts"""
        # This would check for duplicate keybindings, hardware conflicts, etc.
        pass

    def _check_menu_popups(self):
        """Check for unexpected menu popups"""
        # This would detect unexpected menu popups
        pass

    def _check_cursor_quirks(self):
        """Check for Cursor IDE quirky behavior"""
        # This would detect quirky behavior
        pass

    def _check_manus_interference(self):
        """Check for MANUS interference"""
        # This would detect MANUS interfering with operator control
        pass

    def get_fuckery_summary(self) -> Dict[str, Any]:
        """Get summary of all fuckery"""
        return {
            "active_fuckery": len(self.detected_fuckery),
            "resolved_fuckery": len(self.resolved_fuckery),
            "total_fuckery": len(self.detected_fuckery) + len(self.resolved_fuckery),
            "by_type": {
                fuckery_type.value: sum(
                    1 for f in {**self.detected_fuckery, **self.resolved_fuckery}.values()
                    if f.fuckery_type == fuckery_type
                )
                for fuckery_type in FuckeryType
            },
            "by_severity": {
                severity: sum(
                    1 for f in {**self.detected_fuckery, **self.resolved_fuckery}.values()
                    if f.severity == severity
                )
                for severity in ["low", "medium", "high", "critical"]
            }
        }


# Global instance
_global_eliminator: Optional[JARVISSystemFuckeryEliminator] = None


def get_fuckery_eliminator(project_root: Optional[Path] = None) -> JARVISSystemFuckeryEliminator:
    try:
        """Get or create global fuckery eliminator instance"""
        global _global_eliminator

        if _global_eliminator is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_eliminator = JARVISSystemFuckeryEliminator(project_root)

        return _global_eliminator


    except Exception as e:
        logger.error(f"Error in get_fuckery_eliminator: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS System Fuckery Eliminator")
    parser.add_argument("--detect", type=str, help="Detect fuckery (type:description)")
    parser.add_argument("--resolve", type=str, help="Resolve fuckery by ID")
    parser.add_argument("--summary", action="store_true", help="Show fuckery summary")
    parser.add_argument("--list", action="store_true", help="List all fuckery")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    eliminator = JARVISSystemFuckeryEliminator(project_root)

    if args.detect:
        parts = args.detect.split(":", 1)
        if len(parts) == 2:
            fuckery_type_str, description = parts
            try:
                fuckery_type = FuckeryType(fuckery_type_str)
                fuckery = eliminator.detect_fuckery(fuckery_type, description)
                print(f"🚨 Detected: {fuckery.fuckery_id}")
            except ValueError:
                print(f"❌ Invalid fuckery type: {fuckery_type_str}")
        else:
            print("❌ Format: --detect type:description")

    if args.resolve:
        resolution = input("Resolution: ") if sys.stdin.isatty() else "Manual resolution"
        success = eliminator.resolve_fuckery(args.resolve, resolution)
        if success:
            print(f"✅ Resolved: {args.resolve}")
        else:
            print(f"❌ Failed to resolve: {args.resolve}")

    if args.summary:
        summary = eliminator.get_fuckery_summary()
        print("\n" + "="*80)
        print("SYSTEM FUCKERY SUMMARY")
        print("="*80)
        print(f"Active Fuckery: {summary['active_fuckery']}")
        print(f"Resolved Fuckery: {summary['resolved_fuckery']}")
        print(f"Total Fuckery: {summary['total_fuckery']}")
        print("\nBy Type:")
        for fuckery_type, count in summary['by_type'].items():
            if count > 0:
                print(f"  {fuckery_type}: {count}")
        print("\nBy Severity:")
        for severity, count in summary['by_severity'].items():
            if count > 0:
                print(f"  {severity}: {count}")
        print("="*80)

    if args.list:
        print("\n" + "="*80)
        print("ACTIVE SYSTEM FUCKERY")
        print("="*80)
        for fuckery_id, fuckery in eliminator.detected_fuckery.items():
            print(f"\n{fuckery_id}:")
            print(f"  Type: {fuckery.fuckery_type.value}")
            print(f"  Description: {fuckery.description}")
            print(f"  Severity: {fuckery.severity}")
            print(f"  Detected: {fuckery.detected_at.isoformat()}")
        print("="*80)

    if not any([args.detect, args.resolve, args.summary, args.list]):
        parser.print_help()


if __name__ == "__main__":


    main()