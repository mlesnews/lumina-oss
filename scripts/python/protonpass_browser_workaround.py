#!/usr/bin/env python3
"""
ProtonPass Browser Workaround
Handles browser detection issues for Chromium-based browsers (Neo, Edge, etc.)

Tags: #PROTONPASS #BROWSER #CHROMIUM #WORKAROUND #JARVIS
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProtonPassBrowserWorkaround")


class ProtonPassBrowserWorkaround:
    """
    Workaround for ProtonPass browser detection issues

    ProtonPass may complain about Chrome-only support, but Chromium-based
    browsers (Neo, Edge, Brave, etc.) should work with proper user agent
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize browser workaround"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        logger.info("=" * 70)
        logger.info("🌐 PROTONPASS BROWSER WORKAROUND")
        logger.info("=" * 70)
        logger.info("")

    def detect_browser(self) -> Dict[str, Any]:
        """Detect current browser"""
        logger.info("🔍 Detecting browser...")

        browser_info = {
            "name": None,
            "path": None,
            "is_chromium": False,
            "user_agent": None
        }

        # Check for common Chromium browsers (Neo is Chromium-based)
        chromium_browsers = {
            "neo": "Neo (Chromium)",  # Check Neo first since user mentioned it
            "chrome": "Chrome",
            "msedge": "Edge (Chromium)",
            "brave": "Brave",
            "opera": "Opera",
            "vivaldi": "Vivaldi"
        }

        try:
            import psutil
            # First pass: Look for Neo specifically (user's preferred browser)
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if "neo" in proc_name:
                        browser_info["name"] = "Neo (Chromium)"
                        browser_info["path"] = proc.info['exe']
                        browser_info["is_chromium"] = True
                        logger.info(f"   ✅ Found: Neo (Chromium) - User's preferred browser")
                        logger.info(f"   Path: {proc.info['exe']}")
                        return browser_info
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Second pass: Look for other Chromium browsers
            for proc in psutil.process_iter(['name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    for key, display_name in chromium_browsers.items():
                        if key != "neo" and key in proc_name:  # Skip Neo, already checked
                            browser_info["name"] = display_name
                            browser_info["path"] = proc.info['exe']
                            browser_info["is_chromium"] = True
                            logger.info(f"   ✅ Found: {display_name}")
                            logger.info(f"   Path: {proc.info['exe']}")
                            return browser_info
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            logger.debug("psutil not available, using alternative detection")

        # Alternative: Check registry or common paths (Neo first)
        common_paths = {
            "Neo": r"C:\Program Files\Neo\neo.exe",
            "Neo (x86)": r"C:\Program Files (x86)\Neo\neo.exe",
            "Neo (Local)": rf"{os.environ.get('LOCALAPPDATA', '')}\Neo\neo.exe",
            "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        }

        for name, path in common_paths.items():
            if Path(path).exists():
                browser_info["name"] = name
                browser_info["path"] = path
                browser_info["is_chromium"] = True
                logger.info(f"   ✅ Found: {name}")
                return browser_info

        logger.warning("   ⚠️  No Chromium browser detected")
        return browser_info

    def generate_user_agent_override(self, browser_info: Dict[str, Any]) -> str:
        """Generate Chrome user agent for Chromium browsers"""
        logger.info("🔧 Generating user agent override...")

        # Standard Chrome user agent (latest)
        chrome_ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        if browser_info.get("is_chromium"):
            logger.info("   ✅ Chromium browser detected - can use Chrome user agent")
            logger.info(f"   User Agent: {chrome_ua[:80]}...")
            return chrome_ua
        else:
            logger.warning("   ⚠️  Not a Chromium browser - may have compatibility issues")
            return chrome_ua

    def create_browser_launch_script(self, browser_info: Dict[str, Any], url: str = "https://proton.me/pass") -> Path:
        """Create script to launch browser with proper user agent"""
        logger.info("📝 Creating browser launch script...")

        script_path = self.project_root / "scripts" / "python" / "launch_protonpass_browser.ps1"

        if browser_info.get("path"):
            browser_path = browser_info["path"]
            ua_override = self.generate_user_agent_override(browser_info)

            script_content = f"""# Launch ProtonPass in browser with Chrome user agent
# This workaround allows Chromium-based browsers (Neo, Edge, etc.) to work with ProtonPass

$browserPath = "{browser_path}"
$url = "{url}"
$userAgent = "{ua_override}"

# Launch browser with user agent override
Start-Process -FilePath $browserPath -ArgumentList @(
    "--user-agent=`"$userAgent`"",
    $url
)

Write-Output "Launched {browser_info.get('name', 'Browser')} with Chrome user agent"
Write-Output "URL: $url"
"""

            script_path.write_text(script_content)
            logger.info(f"   ✅ Created: {script_path}")
            return script_path
        else:
            logger.error("   ❌ No browser path found")
            return None

    def open_protonpass_gui(self) -> Dict[str, Any]:
        """Open ProtonPass GUI in browser with workaround"""
        logger.info("=" * 70)
        logger.info("🚀 OPENING PROTONPASS GUI")
        logger.info("=" * 70)
        logger.info("")

        browser_info = self.detect_browser()

        if not browser_info.get("is_chromium"):
            logger.warning("⚠️  No Chromium browser detected")
            logger.info("   Opening default browser...")
            import webbrowser
            webbrowser.open("https://proton.me/pass")
            return {"success": True, "method": "default_browser"}

        # Create launch script
        script_path = self.create_browser_launch_script(
            browser_info,
            url="https://proton.me/pass"
        )

        if script_path:
            # Execute script
            try:
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                logger.info("   ✅ Browser launched with user agent override")
                return {
                    "success": True,
                    "method": "chromium_with_ua_override",
                    "browser": browser_info.get("name"),
                    "script": str(script_path)
                }
            except Exception as e:
                logger.error(f"   ❌ Failed to launch: {e}")
                # Fallback: open normally
                import webbrowser
                webbrowser.open("https://proton.me/pass")
                return {"success": True, "method": "fallback"}

        return {"success": False, "error": "Could not create launch script"}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ProtonPass Browser Workaround")
    parser.add_argument("--open", "-o", action="store_true", help="Open ProtonPass GUI")
    parser.add_argument("--detect", "-d", action="store_true", help="Detect browser")

    args = parser.parse_args()

    workaround = ProtonPassBrowserWorkaround()

    if args.open:
        result = workaround.open_protonpass_gui()
        print(f"\n✅ Result: {result}")
    elif args.detect:
        browser_info = workaround.detect_browser()
        print(f"\n✅ Browser: {browser_info.get('name', 'Unknown')}")
        print(f"   Chromium: {browser_info.get('is_chromium', False)}")
        print(f"   Path: {browser_info.get('path', 'Unknown')}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()