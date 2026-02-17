import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Configuration Paths
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
CONFIG_DIR = WORKSPACE_ROOT / "config"
VSCODE_SETTINGS_PATH = WORKSPACE_ROOT / ".vscode" / "settings.json"
CURSOR_SETTINGS_PATH = WORKSPACE_ROOT / ".cursor" / "settings.json"
EXTENSIONS_CONFIG_PATH = CONFIG_DIR / "lumina_vscode_extensions.json"
OPTIMAL_SETTINGS_PATH = CONFIG_DIR / "multi_ide_optimal_settings.json"

# Import notification manager
try:
    from notification_fix_manager import NotificationFixManager
    NOTIFICATION_MANAGER_AVAILABLE = True
except ImportError:
    NOTIFICATION_MANAGER_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class UniversalIDECAManager:
    def __init__(self):
        self.extensions_config = self._load_json(EXTENSIONS_CONFIG_PATH)
        self.optimal_settings = self._load_json(OPTIMAL_SETTINGS_PATH)

        # Initialize notification manager if available
        if NOTIFICATION_MANAGER_AVAILABLE:
            self.notification_manager = NotificationFixManager()
        else:
            self.notification_manager = None
            print("Warning: NotificationFixManager not available")

    def _load_json(self, path: Path) -> Dict[str, Any]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {path}")
            return {}

    def get_installed_extensions(self) -> List[str]:
        """
        Retrieves installed extensions using the 'code' command line interface.
        Falls back to checking the user profile directory if 'code' is not available.
        """
        try:
            # Try getting extensions via CLI
            result = subprocess.run(
                ["code", "--list-extensions"],
                capture_output=True,
                text=True,
                shell=True,
            )
            if result.returncode == 0:
                return [
                    ext.lower() for ext in result.stdout.splitlines() if ext.strip()
                ]
        except Exception:
            pass

        # Fallback: Check standard extension directories (Windows specific for now)
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            ext_dir = Path(user_profile) / ".vscode" / "extensions"
            if ext_dir.exists():
                # This is a rough approximation as folder names usually contain version numbers
                # e.g., ms-python.python-2023.1.0
                extensions = []
                for item in ext_dir.iterdir():
                    if item.is_dir():
                        # Extract publisher.extension from folder name
                        parts = item.name.split("-")
                        if len(parts) >= 2:
                            # Heuristic: join all but the last part (version)
                            # This is imperfect but serves as a fallback
                            ext_name = "-".join(parts[:-1])
                            extensions.append(ext_name.lower())
                return extensions
        return []

    def audit_extensions(self):
        """
        Compares installed extensions against the SSoT.
        """
        print("--- Universal IDE-CA Extension Audit ---")
        installed = set(self.get_installed_extensions())

        required = set()
        if "extensions" in self.extensions_config:
            # Handle different structures if necessary, assuming simple list or dict
            # Based on previous read, it might be a list of strings or objects
            # Let's assume the file structure we saw earlier
            pass
            # For this implementation, we'll assume the structure from the file read earlier
            # which was a dict with categories.

        # Flatten the config to get a list of required extension IDs
        for category, exts in self.extensions_config.items():
            if isinstance(exts, list):
                for ext in exts:
                    if isinstance(ext, str):
                        required.add(ext.lower())
                    elif isinstance(ext, dict) and "id" in ext:
                        required.add(ext["id"].lower())

        missing = required - installed
        extra = installed - required

        print(f"Total Required: {len(required)}")
        print(f"Total Installed: {len(installed)}")

        if missing:
            print("\n[MISSING EXTENSIONS] - Action Required:")
            for ext in sorted(missing):
                print(f"  - {ext}")
        else:
            print("\n[OK] All required extensions are installed.")

    def sync_settings(self):
        """
        Ensures .cursor/settings.json matches the @Peak configuration in .vscode/settings.json
        """
        print("\n--- Universal IDE-CA Settings Sync ---")

        vscode_settings = self._load_json(VSCODE_SETTINGS_PATH)
        cursor_settings = self._load_json(CURSOR_SETTINGS_PATH)

        if not vscode_settings:
            print("Critical: VS Code settings (Source) missing.")
            return

        # Define critical sections to sync
        critical_prefixes = [
            "kilocode.",
            "jarvis.",
            "lumina.",
            "mcp.",
            "continue.",
            "cline.",
        ]

        updates_made = False
        for key, value in vscode_settings.items():
            if any(key.startswith(prefix) for prefix in critical_prefixes):
                if key not in cursor_settings or cursor_settings[key] != value:
                    cursor_settings[key] = value
                    updates_made = True
                    print(f"Synced setting: {key}")

        if updates_made:
            try:
                with open(CURSOR_SETTINGS_PATH, "w", encoding="utf-8") as f:
                    json.dump(cursor_settings, f, indent=2)
                print(
                    "\n[SUCCESS] Cursor settings updated to match Universal IDE-CA Standard."
                )
            except Exception as e:
                print(f"\n[ERROR] Failed to write Cursor settings: {e}")
        else:
            print("\n[OK] Cursor settings are already in sync.")

    def handle_notification(self, notification_type: str, message: str,
                          source: str = "vscode", severity: str = "medium",
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle VS Code system notifications from Cursor IDE

        Args:
            notification_type: Type of notification (vscode_task_error, extension_warning, etc.)
            message: Notification message
            source: Source of notification (vscode, cursor, etc.)
            severity: Severity level (low, medium, high, critical)
            metadata: Additional metadata about the notification

        Returns:
            True if notification was handled/fixed, False otherwise
        """
        if not self.notification_manager:
            print("⚠️  Notification manager not available")
            return False

        print(f"\n📢 Handling notification: {notification_type}")
        print(f"   Source: {source}")
        print(f"   Message: {message[:100]}...")

        fixed = self.notification_manager.report_notification(
            notification_type=notification_type,
            message=message,
            source=source,
            severity=severity,
            metadata=metadata
        )

        if fixed:
            print(f"✅ Notification handled successfully")
        else:
            print(f"⚠️  Notification could not be auto-fixed")

        return fixed

    def process_vscode_notifications(self) -> Dict[str, Any]:
        """
        Process all actionable VS Code notifications from Cursor IDE

        Returns:
            Dict with processing results
        """
        if not self.notification_manager:
            return {"error": "Notification manager not available"}

        print("\n--- Processing VS Code Notifications ---")

        # Get notification summary
        summary = self.notification_manager.get_notification_summary(hours=24)

        print(f"Total notifications (24h): {summary['total_notifications']}")
        print(f"Fixed: {summary['fixed_notifications']}")
        print(f"Unfixed: {summary['unfixed_notifications']}")
        print(f"Suppressed: {summary['suppressed_count']}")

        # Process unfixed notifications
        if summary['unfixed_notifications'] > 0:
            print("\n⚠️  Unfixed notifications detected. Review required.")

        return summary

    def update_notification_settings(self):
        """
        Update IDE settings to handle notifications properly
        """
        print("\n--- Updating Notification Settings ---")

        # Update VS Code settings
        vscode_settings = self._load_json(VSCODE_SETTINGS_PATH)
        if not vscode_settings:
            vscode_settings = {}

        # Add notification handling settings
        notification_settings = {
            "notification.showErrors": "always",
            "notification.showWarnings": "always",
            "notification.showInfo": "never",
            "notification.showProgress": "never",
            "notification.silent": False,
            "task.autoDetect": "on",
            "task.quickOpen.detail": True,
            "task.quickOpen.skip": False,
            "task.quickOpen.history": 10,
            "task.problemMatchers.neverPrompt": False,
            "task.allowAutomaticTasks": "on",
            "task.slowProviderWarning": True,
            "extensions.autoCheckUpdates": True,
            "extensions.autoUpdate": False,
            "extensions.showRecommendationsOnlyOnDemand": False,
            "extensions.ignoreRecommendations": False
        }

        updated = False
        for key, value in notification_settings.items():
            if key not in vscode_settings or vscode_settings[key] != value:
                vscode_settings[key] = value
                updated = True
                print(f"Updated setting: {key} = {value}")

        if updated:
            try:
                VSCODE_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(VSCODE_SETTINGS_PATH, "w", encoding="utf-8") as f:
                    json.dump(vscode_settings, f, indent=2)
                print("✅ VS Code notification settings updated")
            except Exception as e:
                print(f"❌ Failed to update VS Code settings: {e}")

        # Update Cursor settings (sync from VS Code)
        self.sync_settings()

        print("✅ Notification settings update complete")

    def configure_notification_handling(self):
        """
        Configure comprehensive notification handling for all IDEs
        """
        print("\n--- Configuring Notification Handling ---")

        # Update settings
        self.update_notification_settings()

        # Process existing notifications
        self.process_vscode_notifications()

        print("✅ Notification handling configured")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Universal IDE/CA Manager")
    parser.add_argument("--audit", action="store_true", help="Audit extensions")
    parser.add_argument("--sync", action="store_true", help="Sync settings")
    parser.add_argument("--handle-notification", type=str, metavar="TYPE", help="Handle a notification")
    parser.add_argument("--message", type=str, help="Notification message")
    parser.add_argument("--source", type=str, default="vscode", help="Notification source")
    parser.add_argument("--process-notifications", action="store_true", help="Process all notifications")
    parser.add_argument("--configure-notifications", action="store_true", help="Configure notification handling")

    args = parser.parse_args()

    manager = UniversalIDECAManager()

    if args.audit:
        manager.audit_extensions()

    if args.sync:
        manager.sync_settings()

    if args.handle_notification:
        if not args.message:
            print("❌ --message required when using --handle-notification")
            sys.exit(1)
        manager.handle_notification(args.handle_notification, args.message, args.source)

    if args.process_notifications:
        manager.process_vscode_notifications()

    if args.configure_notifications:
        manager.configure_notification_handling()

    if not any([args.audit, args.sync, args.handle_notification, args.process_notifications, args.configure_notifications]):
        manager.audit_extensions()
        manager.sync_settings()
