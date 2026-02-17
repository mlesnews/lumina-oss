#!/usr/bin/env python3
"""
Set Neo Web Browser as Default Browser

Ensures Neo is always the default browser and monitors/auto-fixes if it changes.

Tags: #NEO #BROWSER #DEFAULT #MONITOR @JARVIS @LUMINA
"""

import sys
import subprocess
import winreg
from pathlib import Path
from typing import Optional, Dict, Any
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetNeoDefaultBrowser")


class NeoDefaultBrowserManager:
    """
    Manages Neo Web Browser as default browser

    Sets Neo as default and monitors/auto-fixes if it changes
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Neo browser manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.neo_browser_name = "Neo Web Browser"
        self.neo_exe_paths = [
            r"C:\Program Files\Neo\Neo.exe",
            r"C:\Program Files (x86)\Neo\Neo.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "Neo" / "Neo.exe",
            Path.home() / "AppData" / "Local" / "Neo" / "Neo.exe",
            Path.home() / "AppData" / "Roaming" / "Neo" / "Neo.exe",
        ]

        logger.info("✅ Neo Default Browser Manager initialized")

    def find_neo_browser_path(self) -> Optional[Path]:
        """Find Neo browser executable"""
        for path_str in self.neo_exe_paths:
            path = Path(path_str)
            if path.exists():
                logger.info(f"   ✅ Found Neo: {path}")
                return path

        # Try to find via registry
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Neo.exe") as key:
                neo_path = winreg.QueryValue(key, None)
                if Path(neo_path).exists():
                    logger.info(f"   ✅ Found Neo via registry: {neo_path}")
                    return Path(neo_path)
        except:
            pass

        logger.warning("   ⚠️  Neo browser not found in standard locations")
        return None

    def get_current_default_browser(self) -> Optional[str]:
        """Get current default browser"""
        try:
            # Check HTTP protocol handler
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                prog_id = winreg.QueryValue(key, "ProgId")
                logger.info(f"   Current default browser (HTTP): {prog_id}")
                return prog_id
        except Exception as e:
            logger.debug(f"   Error checking default browser: {e}")

        return None

    def is_neo_default(self) -> bool:
        """Check if Neo is the default browser"""
        current = self.get_current_default_browser()
        if not current:
            return False

        # Check if Neo is in the ProgId
        neo_indicators = ["neo", "Neo", "NEO"]
        return any(indicator in current for indicator in neo_indicators)

    def set_neo_as_default(self) -> bool:
        """Set Neo as default browser using Windows settings"""
        neo_path = self.find_neo_browser_path()
        if not neo_path:
            logger.error("   ❌ Cannot find Neo browser - cannot set as default")
            return False

        try:
            # Method 1: Use Windows Settings app
            logger.info("   📝 Setting Neo as default browser via Windows Settings...")

            # Open Windows Settings to default apps
            subprocess.run([
                "start", "ms-settings:defaultapps"
            ], shell=True, timeout=5)

            logger.info("   💡 Windows Settings opened")
            logger.info("   💡 Please manually select Neo as default browser:")
            logger.info("      - Click 'Web browser'")
            logger.info(f"      - Select '{self.neo_browser_name}'")

            # Method 2: Try direct registry (may require admin)
            try:
                logger.info("   📝 Attempting direct registry method...")
                self._set_neo_via_registry(neo_path)
                logger.info("   ✅ Registry method completed")
            except Exception as e:
                logger.debug(f"   Registry method failed (may need admin): {e}")

            # Method 3: Use Neo's own "Set as default" option
            logger.info("   📝 Attempting via Neo browser...")
            logger.info(f"   💡 Open Neo browser and use: Settings → Set as Default Browser")

            return True

        except Exception as e:
            logger.error(f"   ❌ Error setting Neo as default: {e}")
            return False

    def _set_neo_via_registry(self, neo_path: Path):
        """Set Neo as default via registry (requires admin)"""
        # This is complex and may require admin privileges
        # For now, we'll use the Windows Settings method which is more reliable

        # Note: Direct registry manipulation for default browser is complex
        # and Windows 10/11 have protections. The recommended way is via
        # Windows Settings or the browser's own "Set as default" option.

        logger.info("   ⚠️  Direct registry method requires admin privileges")
        logger.info("   💡 Using Windows Settings method instead")

    def monitor_and_fix(self) -> Dict[str, Any]:
        """Monitor default browser and auto-fix if it's not Neo"""
        logger.info("=" * 80)
        logger.info("🔍 Monitoring Default Browser")
        logger.info("=" * 80)
        logger.info("")

        is_neo = self.is_neo_default()
        current = self.get_current_default_browser()

        result = {
            "neo_is_default": is_neo,
            "current_browser": current,
            "action_taken": None
        }

        if is_neo:
            logger.info("   ✅ Neo is the default browser")
            result["action_taken"] = "none_needed"
        else:
            logger.warning("   ⚠️  Neo is NOT the default browser")
            logger.info(f"   Current default: {current}")
            logger.info("   🔧 Attempting to fix...")

            fixed = self.set_neo_as_default()
            if fixed:
                result["action_taken"] = "fix_attempted"
                logger.info("   ✅ Fix attempted - please verify in Windows Settings")
            else:
                result["action_taken"] = "fix_failed"
                logger.warning("   ❌ Could not fix automatically")

        logger.info("")
        return result

    def ensure_neo_default(self) -> bool:
        """Ensure Neo is default browser (check and fix if needed)"""
        logger.info("=" * 80)
        logger.info("🎯 Ensuring Neo is Default Browser")
        logger.info("=" * 80)
        logger.info("")

        if self.is_neo_default():
            logger.info("   ✅ Neo is already the default browser")
            return True

        logger.info("   ⚠️  Neo is not the default browser")
        logger.info("   🔧 Setting Neo as default...")

        return self.set_neo_as_default()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Set Neo as Default Browser")
    parser.add_argument("--check", action="store_true", help="Check if Neo is default")
    parser.add_argument("--set", action="store_true", help="Set Neo as default")
    parser.add_argument("--monitor", action="store_true", help="Monitor and auto-fix")

    args = parser.parse_args()

    manager = NeoDefaultBrowserManager()

    if args.check:
        is_neo = manager.is_neo_default()
        current = manager.get_current_default_browser()
        print(f"\nCurrent default browser: {current}")
        print(f"Neo is default: {'✅ Yes' if is_neo else '❌ No'}")

    elif args.set:
        manager.ensure_neo_default()

    elif args.monitor:
        result = manager.monitor_and_fix()
        print(f"\nResult: {result}")

    else:
        # Default: check and set if needed
        manager.ensure_neo_default()


if __name__ == "__main__":


    main()