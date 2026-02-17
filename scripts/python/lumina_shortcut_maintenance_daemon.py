#!/usr/bin/env python3
"""
LUMINA Shortcut Maintenance Daemon
===================================
Persistent daemon that monitors and restores Windows shortcuts to prevent
them from disappearing. Automatically restores shortcuts based on registry
configuration.

Features:
- Monitors desktop, start menu, and taskbar shortcuts
- Automatically restores missing shortcuts
- Backs up shortcuts before modification
- Integrates with unified logging system
- Runs continuously in background

@LUMINA @SHORTCUTS @MAINTENANCE @PERSISTENT @DAEMON
"""

import sys
import json
import time
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from lumina_unified_logger import LuminaUnifiedLogger


@dataclass
class ShortcutConfig:
    """Configuration for a single shortcut"""
    name: str
    target_paths: List[str]
    working_directory: Optional[str]
    description: str
    icon_path: Optional[str]
    locations: List[str]  # desktop, start_menu, taskbar
    pin_to_taskbar: bool


class ShortcutMaintenanceDaemon:
    """
    Persistent daemon that monitors and restores Windows shortcuts.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the shortcut maintenance daemon.

        Args:
            config_path: Path to shortcuts registry JSON file
        """
        self.logger = LuminaUnifiedLogger("System", "ShortcutMaintenance")
        self._logger = self.logger.get_logger()

        # Load configuration
        if config_path is None:
            config_path = PROJECT_ROOT / "config" / "shortcuts_registry.json"

        self.config_path = Path(config_path)
        self.shortcuts: List[ShortcutConfig] = []
        self.maintenance_config: Dict[str, Any] = {}
        self._load_config()

        # Runtime state
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self.restored_count = 0
        self.last_check: Optional[datetime] = None

        # Backup directory
        backup_dir = self.maintenance_config.get("backup_location", 
            f"{Path.home()}\\Documents\\Lumina\\ShortcutsBackup")
        self.backup_dir = Path(backup_dir.replace("$env:USERPROFILE", str(Path.home())))
        if self.maintenance_config.get("backup_shortcuts", True):
            self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """Load shortcuts configuration from JSON file"""
        try:
            if not self.config_path.exists():
                self._logger.warning(f"Shortcuts registry not found: {self.config_path}")
                self._logger.info("Creating default shortcuts registry...")
                self._create_default_config()

            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load shortcuts
            self.shortcuts = []
            for sc_data in config.get("shortcuts", []):
                sc = ShortcutConfig(
                    name=sc_data["name"],
                    target_paths=sc_data["target_paths"],
                    working_directory=sc_data.get("working_directory"),
                    description=sc_data.get("description", ""),
                    icon_path=sc_data.get("icon_path"),
                    locations=sc_data.get("locations", ["desktop"]),
                    pin_to_taskbar=sc_data.get("pin_to_taskbar", False)
                )
                self.shortcuts.append(sc)

            # Load maintenance config
            self.maintenance_config = config.get("maintenance", {})
            self._logger.info(f"Loaded {len(self.shortcuts)} shortcuts from registry")

        except Exception as e:
            self._logger.error(f"Failed to load shortcuts config: {e}")
            self.shortcuts = []
            self.maintenance_config = {}

    def _create_default_config(self):
        """Create default shortcuts registry if missing"""
        default_config = {
            "shortcuts": [],
            "maintenance": {
                "check_interval_minutes": 5,
                "restore_on_startup": True,
                "restore_on_missing": True,
                "verify_targets_exist": True,
                "backup_shortcuts": True,
                "backup_location": "$env:USERPROFILE\\Documents\\Lumina\\ShortcutsBackup"
            }
        }

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)

        self._logger.info(f"Created default shortcuts registry: {self.config_path}")

    def _expand_env_vars(self, path: str) -> str:
        """Expand environment variables in path string"""
        import os
        # Replace PowerShell-style env vars with Python-style
        path = path.replace("$env:USERPROFILE", os.environ.get("USERPROFILE", ""))
        path = path.replace("$env:LOCALAPPDATA", os.environ.get("LOCALAPPDATA", ""))
        path = path.replace("$env:PROGRAMFILES", os.environ.get("PROGRAMFILES", ""))
        path = path.replace("$env:PROGRAMFILES(X86)", os.environ.get("PROGRAMFILES(X86)", ""))
        path = path.replace("$env:WINDIR", os.environ.get("WINDIR", ""))
        path = path.replace("$env:APPDATA", os.environ.get("APPDATA", ""))
        return path

    def _find_target_path(self, shortcut: ShortcutConfig) -> Optional[Path]:
        try:
            """
            Find the actual target path for a shortcut by checking multiple possibilities.

            Returns:
                Path to the target executable, or None if not found
            """
            for target_pattern in shortcut.target_paths:
                expanded = self._expand_env_vars(target_pattern)

                # Handle wildcards
                if "*" in expanded:
                    parent_dir = Path(expanded).parent
                    pattern = Path(expanded).name
                    if parent_dir.exists():
                        matches = list(parent_dir.glob(pattern))
                        if matches:
                            return Path(matches[0])
                else:
                    target_path = Path(expanded)
                    if target_path.exists():
                        return target_path

            return None

        except Exception as e:
            self.logger.error(f"Error in _find_target_path: {e}", exc_info=True)
            raise
    def _create_shortcut_ps1(self, shortcut: ShortcutConfig, target_path: Path, 
                             shortcut_path: Path) -> bool:
        """
        Create a Windows shortcut using PowerShell.

        Returns:
            True if successful, False otherwise
        """
        try:
            working_dir = shortcut.working_directory or str(target_path.parent)
            working_dir = self._expand_env_vars(working_dir)

            # PowerShell script to create shortcut
            ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut('{shortcut_path}')
$Shortcut.TargetPath = '{target_path}'
$Shortcut.WorkingDirectory = '{working_dir}'
$Shortcut.Description = '{shortcut.description}'
"""
            if shortcut.icon_path:
                ps_script += f"$Shortcut.IconLocation = '{shortcut.icon_path}'\n"

            ps_script += "$Shortcut.Save()\n"

            # Execute PowerShell script
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0 and shortcut_path.exists():
                return True
            else:
                self._logger.warning(f"PowerShell shortcut creation returned: {result.stderr}")
                return False

        except Exception as e:
            self._logger.error(f"Failed to create shortcut via PowerShell: {e}")
            return False

    def _backup_shortcut(self, shortcut_path: Path) -> bool:
        """Backup an existing shortcut before modification"""
        if not self.maintenance_config.get("backup_shortcuts", True):
            return True

        try:
            if shortcut_path.exists():
                backup_path = self.backup_dir / f"{shortcut_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lnk"
                import shutil
                shutil.copy2(shortcut_path, backup_path)
                return True
        except Exception as e:
            self._logger.warning(f"Failed to backup shortcut {shortcut_path}: {e}")

        return False

    def _restore_shortcut(self, shortcut: ShortcutConfig) -> bool:
        try:
            """
            Restore a single shortcut to all configured locations.

            Returns:
                True if at least one location was restored, False otherwise
            """
            # Find target executable
            target_path = self._find_target_path(shortcut)
            if not target_path:
                if self.maintenance_config.get("verify_targets_exist", True):
                    self._logger.debug(f"Target not found for {shortcut.name}, skipping")
                    return False
                # If verification disabled, use first path as fallback
                target_path = Path(self._expand_env_vars(shortcut.target_paths[0]))

            restored = False

            # Restore to desktop
            if "desktop" in shortcut.locations:
                desktop_path = Path.home() / "Desktop"
                shortcut_path = desktop_path / f"{shortcut.name}.lnk"

                if not shortcut_path.exists():
                    self._backup_shortcut(shortcut_path)
                    if self._create_shortcut_ps1(shortcut, target_path, shortcut_path):
                        self._logger.info(f"✅ Restored desktop shortcut: {shortcut.name}")
                        restored = True
                    else:
                        self._logger.warning(f"❌ Failed to restore desktop shortcut: {shortcut.name}")
                else:
                    self._logger.debug(f"Desktop shortcut exists: {shortcut.name}")

            # Restore to start menu
            if "start_menu" in shortcut.locations:
                start_menu_path = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
                shortcut_path = start_menu_path / f"{shortcut.name}.lnk"

                if not shortcut_path.exists():
                    start_menu_path.mkdir(parents=True, exist_ok=True)
                    self._backup_shortcut(shortcut_path)
                    if self._create_shortcut_ps1(shortcut, target_path, shortcut_path):
                        self._logger.info(f"✅ Restored start menu shortcut: {shortcut.name}")
                        restored = True
                    else:
                        self._logger.warning(f"❌ Failed to restore start menu shortcut: {shortcut.name}")
                else:
                    self._logger.debug(f"Start menu shortcut exists: {shortcut.name}")

            # Pin to taskbar (requires additional PowerShell)
            if shortcut.pin_to_taskbar:
                self._pin_to_taskbar(shortcut, target_path)

            return restored

        except Exception as e:
            self.logger.error(f"Error in _restore_shortcut: {e}", exc_info=True)
            raise
    def _pin_to_taskbar(self, shortcut: ShortcutConfig, target_path: Path):
        """Pin application to taskbar using PowerShell"""
        try:
            ps_script = f"""
$shell = New-Object -ComObject Shell.Application
$folder = $shell.Namespace('{target_path.parent}')
$item = $folder.ParseName('{target_path.name}')
$item.InvokeVerb('taskbarpin')
"""
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0:
                self._logger.info(f"✅ Pinned to taskbar: {shortcut.name}")
            else:
                self._logger.debug(f"Taskbar pin may have failed for {shortcut.name}: {result.stderr}")
        except Exception as e:
            self._logger.debug(f"Taskbar pin failed for {shortcut.name}: {e}")

    def restore_all_shortcuts(self) -> Dict[str, Any]:
        """
        Restore all shortcuts from registry.

        Returns:
            Dictionary with restoration results
        """
        self._logger.info("=" * 70)
        self._logger.info("SHORTCUT RESTORATION - Checking and restoring shortcuts...")
        self._logger.info("=" * 70)

        restored = 0
        skipped = 0
        failed = 0

        for shortcut in self.shortcuts:
            try:
                if self._restore_shortcut(shortcut):
                    restored += 1
                else:
                    skipped += 1
            except Exception as e:
                self._logger.error(f"Error restoring {shortcut.name}: {e}")
                failed += 1

        self.restored_count += restored

        result = {
            "restored": restored,
            "skipped": skipped,
            "failed": failed,
            "total": len(self.shortcuts),
            "timestamp": datetime.now().isoformat()
        }

        self._logger.info("")
        self._logger.info(f"Restoration complete: {restored} restored, {skipped} skipped, {failed} failed")
        self._logger.info("=" * 70)

        return result

    def _monitoring_loop(self):
        """Background monitoring loop"""
        check_interval = self.maintenance_config.get("check_interval_minutes", 5) * 60

        self._logger.info(f"Shortcut monitoring started (check interval: {check_interval}s)")

        while self.running:
            try:
                time.sleep(check_interval)

                if not self.running:
                    break

                self._logger.debug("Running periodic shortcut check...")
                self.last_check = datetime.now()

                # Check and restore missing shortcuts
                if self.maintenance_config.get("restore_on_missing", True):
                    self.restore_all_shortcuts()

            except Exception as e:
                self._logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait before retrying

    def start(self, background: bool = True):
        """Start the maintenance daemon"""
        if self.running:
            self._logger.warning("Daemon already running")
            return

        self.running = True

        # Initial restoration
        if self.maintenance_config.get("restore_on_startup", True):
            self.restore_all_shortcuts()

        # Start monitoring thread
        if background:
            self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._thread.start()
            self._logger.info("Shortcut maintenance daemon started in background")
        else:
            self._logger.info("Shortcut maintenance daemon running in foreground")
            self._monitoring_loop()

    def stop(self):
        """Stop the maintenance daemon"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._logger.info("Shortcut maintenance daemon stopped")

    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status"""
        return {
            "running": self.running,
            "shortcuts_registered": len(self.shortcuts),
            "restored_count": self.restored_count,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "check_interval_minutes": self.maintenance_config.get("check_interval_minutes", 5)
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Shortcut Maintenance Daemon")
    parser.add_argument("--restore-only", action="store_true", 
                       help="Restore shortcuts once and exit (no daemon)")
    parser.add_argument("--foreground", action="store_true",
                       help="Run in foreground (blocking)")
    parser.add_argument("--config", type=Path,
                       help="Path to shortcuts registry JSON file")

    args = parser.parse_args()

    daemon = ShortcutMaintenanceDaemon(config_path=args.config)

    if args.restore_only:
        result = daemon.restore_all_shortcuts()
        print(f"\nRestoration complete: {result}")
        return

    # Run daemon
    try:
        daemon.start(background=not args.foreground)

        if args.foreground:
            # Keep running
            while True:
                time.sleep(60)
        else:
            # Wait a bit then exit (daemon runs in background thread)
            time.sleep(2)
            status = daemon.get_status()
            print(f"\nDaemon started. Status: {status}")

    except KeyboardInterrupt:
        print("\nStopping daemon...")
        daemon.stop()


if __name__ == "__main__":

    main()