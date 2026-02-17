#!/usr/bin/env python3
"""
JARVIS Full Control Over Neo Browser

Complete JARVIS control over Neo Browser with:
- Automatic cookie export
- Full browser automation (like JARVIS browser)
- MANUS integration
- Secure API/CLI interface

Tags: #JARVIS #NEO #BROWSER #FULL_CONTROL #MANUS #API #CLI @JARVIS @LUMINA
"""

import sys
import json
import time
import sqlite3
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
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
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNeoFullControl")

# Import existing Neo automation
try:
    from neo_browser_automation_engine import NEOBrowserAutomationEngine
    from jarvis_neo_browser_integration import JARVISNEOBrowserIntegration
except ImportError:
    logger.warning("⚠️  Neo browser automation modules not found")
    NEOBrowserAutomationEngine = None
    JARVISNEOBrowserIntegration = None


class JARVISNeoFullControl:
    """
    JARVIS Full Control Over Neo Browser

    Provides complete control like JARVIS browser with:
    - Automatic cookie export
    - Full automation (navigate, click, fill, etc.)
    - MANUS integration
    - Secure API/CLI
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Neo Full Control"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"

        # Cookie export paths
        self.cookies_export_dir = self.config_dir / "neo_cookies"
        self.cookies_export_dir.mkdir(parents=True, exist_ok=True)
        self.youtube_cookies_file = self.config_dir / "neo_youtube_cookies.txt"

        # Initialize automation engines
        self.automation_engine: Optional[NEOBrowserAutomationEngine] = None
        self.integration: Optional[JARVISNEOBrowserIntegration] = None

        # Neo browser paths
        self.neo_user_data = Path.home() / "AppData" / "Local" / "Neo" / "User Data"
        self.neo_cookies_db = self.neo_user_data / "Default" / "Cookies"

        logger.info("✅ JARVIS Neo Full Control initialized")
        logger.info("   🎯 Full JARVIS control over Neo Browser")
        logger.info("   🤖 MANUS integration ready")

    def initialize_automation(self) -> bool:
        """Initialize Neo browser automation engines"""
        try:
            if NEOBrowserAutomationEngine:
                self.automation_engine = NEOBrowserAutomationEngine(self.project_root)
                logger.info("   ✅ Automation engine initialized")

            if JARVISNEOBrowserIntegration:
                self.integration = JARVISNEOBrowserIntegration(self.project_root)
                logger.info("   ✅ Integration initialized")

            return True
        except Exception as e:
            logger.warning(f"   ⚠️  Automation initialization warning: {e}")
            return False

    def export_cookies_automatically(self, domain: str = "youtube.com") -> bool:
        """
        Automatically export cookies from Neo browser

        Uses multiple methods:
        1. Direct database access (if available)
        2. Browser automation to export via extension
        3. CDP cookie extraction
        """
        logger.info("=" * 80)
        logger.info("🍪 Automatic Cookie Export from Neo Browser")
        logger.info("=" * 80)
        logger.info("")

        # Method 1: Direct database access (fastest)
        if self._export_cookies_from_database(domain):
            logger.info("   ✅ Cookies exported via database access")
            return True

        # Method 2: Browser automation (if database fails)
        if self._export_cookies_via_automation(domain):
            logger.info("   ✅ Cookies exported via automation")
            return True

        # Method 3: CDP extraction
        if self._export_cookies_via_cdp(domain):
            logger.info("   ✅ Cookies exported via CDP")
            return True

        logger.warning("   ⚠️  Could not export cookies automatically")
        return False

    def _export_cookies_from_database(self, domain: str) -> bool:
        """Export cookies directly from Neo's cookie database"""
        try:
            if not self.neo_cookies_db.exists():
                logger.debug(f"   Cookie database not found: {self.neo_cookies_db}")
                return False

            # Copy database to temp location (Neo may have it locked)
            import tempfile
            temp_db = Path(tempfile.gettempdir()) / f"neo_cookies_{int(time.time())}.db"
            shutil.copy2(self.neo_cookies_db, temp_db)

            # Read cookies from database
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()

            # Query cookies for domain
            cursor.execute("""
                SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
                FROM cookies
                WHERE host_key LIKE ? OR host_key LIKE ?
            """, (f"%{domain}%", f"%.{domain}%"))

            cookies = cursor.fetchall()
            conn.close()
            temp_db.unlink()  # Clean up

            if not cookies:
                logger.debug(f"   No cookies found for {domain}")
                return False

            # Format as Netscape cookies.txt
            cookies_lines = ["# Netscape HTTP Cookie File\n"]
            for cookie in cookies:
                name, value, host, path, expires, secure, httponly = cookie
                # Convert expires_utc (Chrome epoch) to Unix timestamp
                expires_unix = (expires / 1000000) - 11644473600 if expires else 0
                secure_flag = "TRUE" if secure else "FALSE"
                httponly_flag = "TRUE" if httponly else "FALSE"

                cookies_lines.append(
                    f"{host}\t{secure_flag}\t{path}\t{httponly_flag}\t{expires_unix}\t{name}\t{value}\n"
                )

            # Save to file
            with open(self.youtube_cookies_file, 'w', encoding='utf-8') as f:
                f.writelines(cookies_lines)

            logger.info(f"   ✅ Exported {len(cookies)} cookies for {domain}")
            logger.info(f"   📁 Saved to: {self.youtube_cookies_file}")
            return True

        except Exception as e:
            logger.debug(f"   Database export failed: {e}")
            return False

    def _export_cookies_via_automation(self, domain: str) -> bool:
        """Export cookies using browser automation"""
        if not self.automation_engine:
            if not self.initialize_automation():
                return False

        try:
            # Launch browser
            if not self.automation_engine.launch(headless=True):
                return False

            # Navigate to domain to ensure cookies are loaded
            self.automation_engine.navigate(f"https://{domain}")
            time.sleep(3)

            # Extract cookies via JavaScript
            cookie_script = """
            (function() {
                var cookies = document.cookie.split(';').map(function(c) {
                    var parts = c.trim().split('=');
                    return {name: parts[0], value: parts.slice(1).join('=')};
                });
                return cookies;
            })();
            """

            cookies = self.automation_engine.execute_script(cookie_script)

            if cookies:
                # Format as cookies.txt
                cookies_lines = ["# Netscape HTTP Cookie File\n"]
                for cookie in cookies:
                    cookies_lines.append(
                        f"{domain}\tFALSE\t/\tFALSE\t0\t{cookie['name']}\t{cookie['value']}\n"
                    )

                with open(self.youtube_cookies_file, 'w', encoding='utf-8') as f:
                    f.writelines(cookies_lines)

                self.automation_engine.close()
                logger.info(f"   ✅ Exported {len(cookies)} cookies via automation")
                return True

            self.automation_engine.close()
            return False

        except Exception as e:
            logger.debug(f"   Automation export failed: {e}")
            if self.automation_engine:
                self.automation_engine.close()
            return False

    def _export_cookies_via_cdp(self, domain: str) -> bool:
        """Export cookies using Chrome DevTools Protocol"""
        if not self.automation_engine:
            if not self.initialize_automation():
                return False

        try:
            # Launch browser and navigate to domain first
            if not self.automation_engine.launch(headless=True):
                return False

            # Navigate to domain to ensure cookies are loaded
            self.automation_engine.navigate(f"https://{domain}")
            time.sleep(3)  # Wait for page and cookies to load

            # Get cookies via CDP - try multiple methods
            # Method 1: Network.getAllCookies (CDP method)
            logger.info("   Trying Network.getAllCookies via CDP...")
            result = self.automation_engine.cdp_command("Network.getAllCookies")

            logger.debug(f"   CDP result keys: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}")
            logger.debug(f"   CDP result: {json.dumps(result, indent=2, default=str)[:500]}")

            cookies = []
            if "error" not in result:
                # Check different response formats
                if "result" in result:
                    result_data = result["result"]
                    if isinstance(result_data, dict):
                        cookies = result_data.get("cookies", [])
                    elif isinstance(result_data, list):
                        cookies = result_data
                elif "cookies" in result:
                    cookies = result["cookies"]
                elif isinstance(result, list):
                    cookies = result
                elif isinstance(result, dict):
                    # Try to find cookies in nested structure
                    for key, value in result.items():
                        if isinstance(value, dict) and "cookies" in value:
                            cookies = value["cookies"]
                            break
                        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict) and "name" in value[0]:
                            cookies = value
                            break

                logger.info(f"   Found {len(cookies)} cookies via Network.getAllCookies")

            # If we got cookies, log first few for debugging
            if cookies and len(cookies) > 0:
                logger.debug(f"   Sample cookie: {json.dumps(cookies[0] if isinstance(cookies[0], dict) else str(cookies[0]), indent=2)[:200]}")

            # Method 2: If no cookies, try Runtime.evaluate to get document.cookie
            if not cookies:
                logger.info("   Trying document.cookie via JavaScript...")
                cookie_script = f"""
                (function() {{
                    var cookies = document.cookie.split(';').map(function(c) {{
                        var parts = c.trim().split('=');
                        return {{
                            name: parts[0],
                            value: parts.slice(1).join('='),
                            domain: '{domain}',
                            path: '/',
                            secure: window.location.protocol === 'https:',
                            httpOnly: false
                        }};
                    }});
                    return cookies;
                }})();
                """
                js_cookies = self.automation_engine.execute_script(cookie_script)
                if js_cookies:
                    cookies = js_cookies

            # Filter for domain (case-insensitive)
            domain_lower = domain.lower()
            domain_cookies = []
            for c in cookies:
                cookie_domain = str(c.get("domain", "")).lower()
                # Match exact domain or subdomain
                if domain_lower in cookie_domain or cookie_domain.endswith(f".{domain_lower}"):
                    domain_cookies.append(c)

            logger.debug(f"   Filtered to {len(domain_cookies)} cookies for {domain}")

            if domain_cookies:
                # Format as cookies.txt
                cookies_lines = ["# Netscape HTTP Cookie File\n"]
                for cookie in domain_cookies:
                    # Handle both CDP format and JS format
                    if isinstance(cookie, dict):
                        cookie_domain = cookie.get("domain", domain)
                        cookie_name = cookie.get("name", "")
                        cookie_value = cookie.get("value", "")
                        expires = cookie.get("expires", 0)
                        secure = "TRUE" if cookie.get("secure", False) else "FALSE"
                        httponly = "TRUE" if cookie.get("httpOnly", False) else "FALSE"
                        path = cookie.get("path", "/")
                    else:
                        continue

                    cookies_lines.append(
                        f"{cookie_domain}\t{secure}\t{path}\t{httponly}\t{expires}\t{cookie_name}\t{cookie_value}\n"
                    )

                with open(self.youtube_cookies_file, 'w', encoding='utf-8') as f:
                    f.writelines(cookies_lines)

                self.automation_engine.close()
                logger.info(f"   ✅ Exported {len(domain_cookies)} cookies via CDP")
                return True

            self.automation_engine.close()
            logger.debug(f"   No cookies found for {domain}")
            return False

        except Exception as e:
            logger.debug(f"   CDP export failed: {e}")
            if self.automation_engine:
                self.automation_engine.close()
            return False

    # JARVIS Browser Control Methods
    def navigate(self, url: str) -> bool:
        """Navigate to URL (JARVIS control)"""
        if not self.automation_engine:
            if not self.initialize_automation():
                return False

        if not self.automation_engine.is_running():
            self.automation_engine.launch()

        return self.automation_engine.navigate(url)

    def click(self, selector: str) -> bool:
        """Click element (JARVIS control)"""
        if not self.automation_engine:
            return False
        return self.automation_engine.click(selector)

    def fill(self, selector: str, text: str) -> bool:
        """Fill input (JARVIS control)"""
        if not self.automation_engine:
            return False
        return self.automation_engine.fill(selector, text)

    def execute_script(self, script: str) -> Any:
        """Execute JavaScript (JARVIS control)"""
        if not self.automation_engine:
            return None
        return self.automation_engine.execute_script(script)

    def screenshot(self, path: str) -> bool:
        """Take screenshot (JARVIS control)"""
        if not self.automation_engine:
            return False
        return self.automation_engine.screenshot(path)

    def get_page_info(self) -> Dict[str, Any]:
        """Get current page info (JARVIS control)"""
        if not self.automation_engine:
            return {}
        return self.automation_engine.get_page_info()

    def close(self):
        """Close browser (JARVIS control)"""
        if self.automation_engine:
            self.automation_engine.close()


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Full Control Over Neo Browser")
        parser.add_argument("--export-cookies", metavar="DOMAIN", default="youtube.com",
                           help="Export cookies for domain (default: youtube.com)")
        parser.add_argument("--navigate", metavar="URL", help="Navigate to URL")
        parser.add_argument("--click", metavar="SELECTOR", help="Click element")
        parser.add_argument("--fill", nargs=2, metavar=("SELECTOR", "TEXT"),
                           help="Fill input field")
        parser.add_argument("--screenshot", metavar="PATH", help="Take screenshot")
        parser.add_argument("--info", action="store_true", help="Get page info")

        args = parser.parse_args()

        control = JARVISNeoFullControl()

        if args.export_cookies:
            control.export_cookies_automatically(args.export_cookies)
        elif args.navigate:
            control.navigate(args.navigate)
            time.sleep(3)
            control.close()
        elif args.click:
            control.click(args.click)
        elif args.fill:
            control.fill(args.fill[0], args.fill[1])
        elif args.screenshot:
            control.screenshot(args.screenshot)
        elif args.info:
            info = control.get_page_info()
            print(json.dumps(info, indent=2))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()