#!/usr/bin/env python3
"""
LUMINA Hotkey Manager - Persistent Global Hotkeys

Manages persistent global hotkeys (Right Alt, F23) that survive reboots.
Part of LUMINA core initialization.

Hotkeys:
- Right Alt (RAlt) → @DOIT + Enter
- F23 (MS-Copilot Key) → @JARVIS + Enter + Voice Input

Tags: #LUMINA_CORE #HOTKEYS #PERSISTENT #AUTOHOTKEY @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import winreg
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaHotkeyManager")

# Hotkey configuration
HOTKEY_CONFIG = {
    "right_alt": {
        "key": "RAlt",
        "action": "@DOIT + Enter",
        "description": "Right Alt → @DOIT + Enter",
        "enabled": True
    },
    "f23": {
        "key": "F23",
        "action": "@JARVIS + Enter + Voice Input",
        "description": "F23 (MS-Copilot Key) → @JARVIS + Enter + Voice Input",
        "enabled": True
    }
}


class LuminaHotkeyManager:
    """
    LUMINA Hotkey Manager

    Manages persistent global hotkeys that survive reboots.
    Part of LUMINA core initialization.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize hotkey manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.config_file = self.config_dir / "lumina_hotkeys.json"
        self.autohotkey_script = self.project_root / "scripts" / "autohotkey" / "left_alt_doit_fixed.ahk"

        # Load configuration
        self.config = self._load_config()

        logger.info("="*80)
        logger.info("🎹 LUMINA HOTKEY MANAGER")
        logger.info("="*80)
        logger.info(f"   Config: {self.config_file}")
        logger.info(f"   AutoHotkey Script: {self.autohotkey_script}")
        logger.info("="*80)

    def _load_config(self) -> Dict[str, Any]:
        """Load hotkey configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, default in HOTKEY_CONFIG.items():
                        if key not in config.get("hotkeys", {}):
                            config.setdefault("hotkeys", {})[key] = default
                    return config
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        # Default configuration
        return {
            "version": "1.0.0",
            "enabled": True,
            "autostart": True,
            "hotkeys": HOTKEY_CONFIG.copy(),
            "last_updated": datetime.now().isoformat(),
            "description": "LUMINA Core - Persistent Global Hotkeys",
            "tags": ["#LUMINA_CORE", "#HOTKEYS", "#PERSISTENT", "#AUTOHOTKEY", "@JARVIS", "@LUMINA"]
        }

    def _save_config(self):
        """Save hotkey configuration"""
        try:
            self.config["last_updated"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Config saved: {self.config_file}")
        except Exception as e:
            logger.error(f"   ❌ Error saving config: {e}")

    def is_autohotkey_running(self) -> bool:
        """Check if AutoHotkey script is running"""
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq AutoHotkey.exe"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return "AutoHotkey.exe" in result.stdout
        except:
            return False

    def start_hotkeys(self) -> bool:
        """Start AutoHotkey script with hotkeys"""
        if not self.config.get("enabled", True):
            logger.info("   ⚠️  Hotkeys disabled in config")
            return False

        if not self.autohotkey_script.exists():
            logger.error(f"   ❌ AutoHotkey script not found: {self.autohotkey_script}")
            return False

        # Check if already running
        if self.is_autohotkey_running():
            logger.info("   ✅ AutoHotkey already running")
            return True

        try:
            # Find AutoHotkey executable
            autohotkey_exe = None

            # Try common locations
            common_paths = [
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
                r"C:\Users\{}\AppData\Local\Programs\AutoHotkey\AutoHotkey.exe".format(
                    Path.home().name
                )
            ]

            for path in common_paths:
                if Path(path).exists():
                    autohotkey_exe = path
                    break

            # Try PATH
            if not autohotkey_exe:
                try:
                    result = subprocess.run(
                        ["where", "autohotkey"],
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if result.returncode == 0:
                        autohotkey_exe = result.stdout.strip().split('\n')[0]
                except:
                    pass

            if not autohotkey_exe:
                logger.error("   ❌ AutoHotkey not found")
                logger.info("   💡 Install AutoHotkey from: https://www.autohotkey.com/")
                return False

            # Start AutoHotkey script
            logger.info(f"   🚀 Starting AutoHotkey script...")
            logger.info(f"      Script: {self.autohotkey_script.name}")
            logger.info(f"      Executable: {autohotkey_exe}")

            subprocess.Popen(
                [autohotkey_exe, str(self.autohotkey_script)],
                cwd=str(self.project_root),
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            )

            # Wait a moment to check if it started
            import time
            time.sleep(1)

            if self.is_autohotkey_running():
                logger.info("   ✅ AutoHotkey script started successfully")
                logger.info("")
                logger.info("   🎹 Active Hotkeys:")
                for key, hotkey in self.config.get("hotkeys", {}).items():
                    if hotkey.get("enabled", True):
                        logger.info(f"      • {hotkey['key']}: {hotkey['description']}")
                return True
            else:
                logger.warning("   ⚠️  AutoHotkey may not have started")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error starting AutoHotkey: {e}")
            return False

    def enable_autostart(self) -> bool:
        """Enable autostart on Windows boot (Registry)"""
        try:
            # Registry path for current user startup
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

            # Create a launcher script
            launcher_script = self.project_root / "scripts" / "python" / "lumina_hotkey_autostart.pyw"

            # Create launcher script
            launcher_content = f'''#!/usr/bin/env pythonw
"""LUMINA Hotkey Autostart Launcher"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lumina_hotkey_manager import LuminaHotkeyManager

manager = LuminaHotkeyManager()
manager.start_hotkeys()
'''

            with open(launcher_script, 'w', encoding='utf-8') as f:
                f.write(launcher_content)

            # Find Pythonw executable
            pythonw_exe = sys.executable.replace("python.exe", "pythonw.exe")
            if not Path(pythonw_exe).exists():
                pythonw_exe = sys.executable

            # Register in startup
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_SET_VALUE
            )

            winreg.SetValueEx(
                key,
                "LUMINA_Hotkeys",
                0,
                winreg.REG_SZ,
                f'"{pythonw_exe}" "{launcher_script}"'
            )

            winreg.CloseKey(key)

            logger.info("   ✅ Autostart enabled in Windows Registry")
            logger.info(f"      Registry: HKEY_CURRENT_USER\\{reg_path}")
            logger.info(f"      Value: LUMINA_Hotkeys")
            logger.info(f"      Command: {pythonw_exe} {launcher_script}")

            self.config["autostart"] = True
            self._save_config()

            return True

        except Exception as e:
            logger.error(f"   ❌ Error enabling autostart: {e}")
            return False

    def disable_autostart(self) -> bool:
        """Disable autostart"""
        try:
            reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                reg_path,
                0,
                winreg.KEY_SET_VALUE
            )

            try:
                winreg.DeleteValue(key, "LUMINA_Hotkeys")
                logger.info("   ✅ Autostart disabled")
            except FileNotFoundError:
                logger.info("   ℹ️  Autostart was not enabled")

            winreg.CloseKey(key)

            self.config["autostart"] = False
            self._save_config()

            return True

        except Exception as e:
            logger.error(f"   ❌ Error disabling autostart: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        try:
            """Get hotkey manager status"""
            return {
                "enabled": self.config.get("enabled", True),
                "autostart": self.config.get("autostart", False),
                "autohotkey_running": self.is_autohotkey_running(),
                "script_exists": self.autohotkey_script.exists(),
                "hotkeys": self.config.get("hotkeys", {}),
                "config_file": str(self.config_file)
            }


        except Exception as e:
            self.logger.error(f"Error in get_status: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Hotkey Manager - Persistent Global Hotkeys")
    parser.add_argument("--start", action="store_true", help="Start hotkeys")
    parser.add_argument("--enable-autostart", action="store_true", help="Enable autostart on boot")
    parser.add_argument("--disable-autostart", action="store_true", help="Disable autostart")
    parser.add_argument("--status", action="store_true", help="Show status")

    args = parser.parse_args()

    manager = LuminaHotkeyManager()

    if args.start:
        manager.start_hotkeys()
    elif args.enable_autostart:
        manager.enable_autostart()
    elif args.disable_autostart:
        manager.disable_autostart()
    elif args.status:
        status = manager.get_status()
        print("\n📊 LUMINA Hotkey Manager Status:")
        print(f"   Enabled: {status['enabled']}")
        print(f"   Autostart: {status['autostart']}")
        print(f"   AutoHotkey Running: {status['autohotkey_running']}")
        print(f"   Script Exists: {status['script_exists']}")
        print("\n🎹 Hotkeys:")
        for key, hotkey in status['hotkeys'].items():
            enabled = "✅" if hotkey.get("enabled", True) else "❌"
            print(f"   {enabled} {hotkey['key']}: {hotkey['description']}")
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())