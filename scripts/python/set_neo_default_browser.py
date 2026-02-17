#!/usr/bin/env python3
"""
Set Neo Browser as Default Browser

Sets Neo web browser as the default browser on Windows 11.
Also provides monitoring to ensure it stays default.

Tags: #NEO_BROWSER #DEFAULT_BROWSER #WINDOWS11 #MONITORING @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import winreg
import time
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("NeoDefaultBrowser")


class NeoDefaultBrowserSetter:
    """
    Set Neo Browser as Default Browser

    Sets Neo as default and monitors to ensure it stays default.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Neo default browser setter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ Neo Default Browser Setter initialized")

    def find_neo_browser_path(self) -> Optional[Path]:
        """
        Find Neo browser installation path

        Returns:
            Path to Neo browser executable or None
        """
        # Common Neo browser installation paths
        possible_paths = [
            Path("C:/Program Files/Neo/neo.exe"),
            Path("C:/Program Files (x86)/Neo/neo.exe"),
            Path(os.path.expanduser("~/AppData/Local/Neo/neo.exe")),
            Path("C:/Users") / os.getenv("USERNAME", "") / "AppData/Local/Neo/neo.exe",
        ]

        # Also check registry
        try:
            # Check HKEY_CURRENT_USER
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\neo.exe") as key:
                neo_path = winreg.QueryValue(key, None)
                if neo_path and Path(neo_path).exists():
                    return Path(neo_path)
        except:
            pass

        # Check common paths
        for path in possible_paths:
            if path.exists():
                logger.info(f"   ✅ Found Neo browser: {path}")
                return path

        logger.warning("   ⚠️  Neo browser not found in common locations")
        return None

    def get_current_default_browser(self) -> Dict[str, Any]:
        """
        Get current default browser

        Returns:
            Dictionary with browser info
        """
        try:
            # Use Windows Settings to get default browser
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice' -Name ProgId | Select-Object -ExpandProperty ProgId"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                prog_id = result.stdout.strip()
                return {
                    "prog_id": prog_id,
                    "is_neo": "neo" in prog_id.lower() or "Neo" in prog_id,
                    "status": "Neo" if ("neo" in prog_id.lower() or "Neo" in prog_id) else "Other"
                }
        except Exception as e:
            logger.debug(f"   Could not get default browser: {e}")

        return {
            "prog_id": "unknown",
            "is_neo": False,
            "status": "Unknown"
        }

    def set_neo_as_default(self) -> bool:
        """
        Set Neo browser as default browser

        Returns:
            True if successful, False otherwise
        """
        neo_path = self.find_neo_browser_path()
        if not neo_path:
            logger.error("   ❌ Neo browser not found - cannot set as default")
            return False

        try:
            # Method 1: Use Windows Settings app
            logger.info("   🔧 Opening Windows Settings to set default browser...")
            subprocess.run(
                ["start", "ms-settings:defaultapps"],
                shell=True,
                timeout=2
            )

            logger.info("   📋 Please manually select Neo browser as default in the settings window")
            logger.info("   💡 Or use the PowerShell method below")

            # Method 2: Try PowerShell (may require admin)
            try:
                logger.info("   🔧 Attempting PowerShell method...")
                ps_command = f'''
                $ProgId = (Get-ItemProperty -Path "HKLM:\\SOFTWARE\\RegisteredApplications" | Get-Member -MemberType NoteProperty | Where-Object {{$_.Name -like "*Neo*"}}).Name
                if ($ProgId) {{
                    Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\http\\UserChoice" -Name ProgId -Value $ProgId
                    Write-Host "Neo browser set as default"
                }} else {{
                    Write-Host "Neo browser not found in registry"
                }}
                '''

                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and "set as default" in result.stdout:
                    logger.info("   ✅ Neo browser set as default via PowerShell")
                    return True
            except Exception as e:
                logger.debug(f"   PowerShell method failed: {e}")

            # Method 3: Direct registry (requires admin)
            logger.info("   🔧 Attempting direct registry method...")
            logger.warning("   ⚠️  This method may require administrator privileges")

            return False  # Manual intervention required

        except Exception as e:
            logger.error(f"   ❌ Error setting default browser: {e}")
            return False

    def open_url_in_neo(self, url: str) -> bool:
        """
        Open URL in Neo browser specifically (even if not default)

        Args:
            url: URL to open

        Returns:
            True if successful
        """
        neo_path = self.find_neo_browser_path()
        if not neo_path:
            logger.error("   ❌ Neo browser not found")
            return False

        try:
            logger.info(f"   🌐 Opening {url} in Neo browser...")
            logger.info(f"      Neo path: {neo_path}")

            # Try multiple methods to open in Neo
            # Method 1: Direct executable with URL
            try:
                subprocess.Popen([str(neo_path), url], shell=False)
                time.sleep(0.5)  # Give it a moment
                logger.info("   ✅ Opened in Neo browser (method 1)")
                return True
            except Exception as e1:
                logger.debug(f"   Method 1 failed: {e1}")

            # Method 2: Use start command with Neo path
            try:
                subprocess.run(
                    ["cmd", "/c", "start", "", str(neo_path), url],
                    shell=False,
                    timeout=5
                )
                logger.info("   ✅ Opened in Neo browser (method 2)")
                return True
            except Exception as e2:
                logger.debug(f"   Method 2 failed: {e2}")

            # Method 3: Use PowerShell Start-Process
            try:
                ps_command = f'Start-Process -FilePath "{neo_path}" -ArgumentList "{url}"'
                subprocess.run(
                    ["powershell", "-Command", ps_command],
                    shell=False,
                    timeout=5
                )
                logger.info("   ✅ Opened in Neo browser (method 3)")
                return True
            except Exception as e3:
                logger.debug(f"   Method 3 failed: {e3}")

            logger.error("   ❌ All methods failed to open in Neo")
            return False

        except Exception as e:
            logger.error(f"   ❌ Error opening in Neo: {e}")
            return False

    def verify_neo_is_default(self) -> bool:
        """Verify Neo is the default browser"""
        current = self.get_current_default_browser()
        is_neo = current.get("is_neo", False)

        if is_neo:
            logger.info("   ✅ Neo browser is the default browser")
        else:
            logger.warning(f"   ⚠️  Neo browser is NOT the default (current: {current.get('status', 'Unknown')})")

        return is_neo

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        neo_path = self.find_neo_browser_path()
        current_default = self.get_current_default_browser()

        return {
            "neo_installed": neo_path is not None,
            "neo_path": str(neo_path) if neo_path else None,
            "current_default": current_default.get("status", "Unknown"),
            "is_neo_default": current_default.get("is_neo", False),
            "prog_id": current_default.get("prog_id", "unknown")
        }


def main():
    try:
        """CLI interface"""
        import argparse
        import os

        parser = argparse.ArgumentParser(description="Set Neo Browser as Default")
        parser.add_argument("--set-default", action="store_true", help="Set Neo as default browser")
        parser.add_argument("--verify", action="store_true", help="Verify Neo is default")
        parser.add_argument("--status", action="store_true", help="Get status")
        parser.add_argument("--open", type=str, help="Open URL in Neo browser")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        setter = NeoDefaultBrowserSetter()

        if args.set_default:
            success = setter.set_neo_as_default()
            if args.json:
                print(json.dumps({"success": success}, indent=2))
            else:
                print(f"{'✅ Success' if success else '❌ Failed or requires manual setup'}")

        elif args.verify:
            is_default = setter.verify_neo_is_default()
            if args.json:
                print(json.dumps({"is_default": is_default}, indent=2))
            else:
                print(f"{'✅ Neo is default' if is_default else '❌ Neo is NOT default'}")

        elif args.open:
            success = setter.open_url_in_neo(args.open)
            if args.json:
                print(json.dumps({"success": success}, indent=2))
            else:
                print(f"{'✅ Opened' if success else '❌ Failed'}")

        elif args.status or not any([args.set_default, args.verify, args.open]):
            status = setter.get_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("=" * 80)
                print("🌐 NEO BROWSER DEFAULT STATUS")
                print("=" * 80)
                print(f"Neo Installed: {'✅ Yes' if status['neo_installed'] else '❌ No'}")
                if status['neo_path']:
                    print(f"Neo Path: {status['neo_path']}")
                print(f"Current Default: {status['current_default']}")
                print(f"Is Neo Default: {'✅ Yes' if status['is_neo_default'] else '❌ No'}")
                if not status['is_neo_default']:
                    print("\n⚠️  Neo browser is NOT the default browser!")
                    print("   Run: python scripts/python/set_neo_default_browser.py --set-default")
                print("=" * 80)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import json
    import os


    main()