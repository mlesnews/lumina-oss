#!/usr/bin/env python3
"""
NEO Browser Automation Engine
Full automation engine specifically for NEO Browser (no Chromium/Playwright)
#JARVIS #NEO #BROWSER #AUTOMATION #MANUS
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
import logging
import json
import time
import subprocess
import os
import sqlite3
import shutil
import requests
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
from dataclasses import dataclass

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NEOAutomationEngine")


@dataclass
class NEOElement:
    """Represents a DOM element in NEO browser"""
    selector: str
    tag: Optional[str] = None
    text: Optional[str] = None
    attributes: Dict[str, str] = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


class NEOBrowserAutomationEngine:
    """
    Full automation engine for NEO Browser

    Uses multiple methods:
    1. Chrome DevTools Protocol (CDP) - Primary method
    2. JavaScript execution - DOM manipulation
    3. File system access - Cookies, settings
    4. Process control - Browser lifecycle
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.neo_exe = Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "Application" / "neo.exe"
        self.neo_user_data = Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "User Data"
        self.cdp_port = 9222
        self.cdp_endpoint = f"http://localhost:{self.cdp_port}"
        self.process: Optional[subprocess.Popen] = None
        self.cdp_available = False
        self.session_id: Optional[str] = None
        self.ws_url: Optional[str] = None

        if not self.neo_exe.exists():
            raise FileNotFoundError(f"NEO browser not found at: {self.neo_exe}")

        logger.info("✅ NEO Browser Automation Engine initialized")
        logger.info(f"   NEO Path: {self.neo_exe}")

    def _kill_existing_neo_processes(self) -> None:
        """Kill any existing NEO browser processes to prevent multiple instances"""
        try:
            import psutil
            killed = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'neo' in proc.info['name'].lower() or 'neo.exe' in proc.info['name'].lower():
                        logger.warning(f"⚠️  Killing existing NEO process: PID {proc.info['pid']}")
                        proc.kill()
                        killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if killed > 0:
                logger.info(f"   ✅ Killed {killed} existing NEO process(es) to prevent duplicates")
                time.sleep(2)  # Wait for processes to terminate
        except ImportError:
            logger.warning("⚠️  psutil not available, cannot kill existing processes")
        except Exception as e:
            logger.debug(f"Error killing existing processes: {e}")

    def connect_to_existing(self, url: Optional[str] = None) -> bool:
        """
        Connect to existing NEO browser session (DO NOT launch new instance)

        This method connects to an already-running NEO browser via CDP.
        Use this when you want to reuse an existing logged-in session.
        """
        try:
            logger.info("🔍 Connecting to existing NEO browser session...")

            # Check if CDP endpoint is available
            try:
                response = requests.get(f"{self.cdp_endpoint}/json", timeout=2)
                if response.status_code == 200:
                    tabs = response.json()
                    logger.info(f"   ✅ Found existing NEO browser with {len(tabs)} tab(s)")

                    # Find DSM tab if URL provided
                    if url:
                        for tab in tabs:
                            if url in tab.get("url", ""):
                                logger.info(f"   ✅ Found existing DSM tab: {tab.get('url')}")
                                self.session_id = tab.get("id")
                                self.ws_url = tab.get("webSocketDebuggerUrl")
                                self.cdp_available = True
                                return True

                    # Use first available tab
                    if tabs:
                        first_tab = tabs[0]
                        self.session_id = first_tab.get("id")
                        self.ws_url = first_tab.get("webSocketDebuggerUrl")
                        self.cdp_available = True
                        logger.info(f"   ✅ Connected to existing tab: {first_tab.get('url', 'N/A')}")

                        # Navigate to URL if provided
                        if url:
                            self.navigate(url)

                        return True
                    else:
                        logger.warning("   ⚠️  No tabs found in existing browser")
                        return False
                else:
                    logger.warning(f"   ⚠️  CDP endpoint returned status {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                logger.warning(f"   ⚠️  Could not connect to existing browser: {e}")
                logger.info("   💡 No existing browser found - you may need to launch one first")
                return False

        except Exception as e:
            logger.error(f"❌ Error connecting to existing browser: {e}")
            return False

    def launch(self, url: Optional[str] = None, headless: bool = True, reuse_existing: bool = True) -> bool:
        """
        Launch NEO browser with CDP enabled (operates in background) - SINGLE INSTANCE ONLY

        Args:
            url: URL to navigate to
            headless: Run in headless mode
            reuse_existing: If True, try to connect to existing browser first (default: True)
        """
        # Try to connect to existing browser first if requested
        if reuse_existing:
            logger.info("🔍 Attempting to reuse existing browser session...")
            if self.connect_to_existing(url):
                logger.info("   ✅ Reusing existing browser session (no new launch needed)")
                return True
            logger.info("   ⚠️  No existing session found, launching new browser...")

        try:
            # CRITICAL: Kill any existing NEO browser processes FIRST (AGGRESSIVE)
            logger.warning("🔪 KILLING all existing NEO processes before launch...")
            self._kill_existing_neo_processes()

            # Verify no processes remain
            import psutil
            remaining = []
            try:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'neo' in proc.info['name'].lower():
                            remaining.append(proc.info['pid'])
                    except:
                        pass
            except:
                pass

            if remaining:
                logger.error(f"❌ {len(remaining)} NEO processes still running, force killing again...")
                self._kill_existing_neo_processes()
                time.sleep(3)

            args = [str(self.neo_exe)]

            # Enable remote debugging (works in background)
            args.append(f"--remote-debugging-port={self.cdp_port}")

            # Automation flags for background operation
            args.extend([
                # No extensions loaded - user uses ProtonPass (not Dashlane)
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-blink-features=AutomationControlled",
                "--user-data-dir=" + str(self.neo_user_data),
                "--disable-gpu",  # Better for background operation
                "--no-sandbox",  # Required for background automation
                "--disable-dev-shm-usage",  # Prevents crashes in background
                "--disable-session-crashed-bubble",  # Disable crash recovery popup
                "--disable-infobars",  # Disable info bars
                "--disable-notifications",  # Disable notifications
                "--disable-popup-blocking",  # Allow popups (we'll handle them)
            ])

            if headless:
                args.append("--headless=new")
                logger.info("   Running in headless mode (background)")
            else:
                # Even in visible mode, ensure it works in background
                args.append("--disable-background-timer-throttling")
                args.append("--disable-backgrounding-occluded-windows")
                args.append("--disable-renderer-backgrounding")
                logger.info("   Running in visible mode (background-capable)")

            if url:
                args.append(url)

            logger.info(f"🚀 Launching NEO browser...")
            # Launch process - works in background regardless of headless mode
            # Use CREATE_NO_WINDOW for background operation (Windows)
            creation_flags = 0
            if headless:
                creation_flags = subprocess.CREATE_NO_WINDOW
            elif os.name == 'nt':  # Windows
                # Even in visible mode, allow background operation
                creation_flags = 0

            self.process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creation_flags
            )

            # Wait for CDP with retries (longer wait - NEO may take time to start CDP)
            max_retries = 20  # Increased retries
            logger.info(f"   Waiting for CDP to become available (max {max_retries} seconds)...")
            for i in range(max_retries):
                time.sleep(1)

                # After 3 seconds, try to dismiss "Restore All Pages" popup
                if i == 3:
                    logger.info("   Dismissing 'Restore All Pages' popup if present...")
                    self._dismiss_restore_pages_popup()

                if self._connect_cdp():
                    logger.info(f"✅ NEO browser launched with CDP on port {self.cdp_port}")
                    # Dismiss popup again after CDP connects (popup might appear after CDP)
                    time.sleep(1)
                    self._dismiss_restore_pages_popup()
                    break
                if i % 5 == 0 and i > 0:  # Log progress every 5 seconds
                    logger.debug(f"   Still waiting for CDP... ({i}/{max_retries})")
                if i == max_retries - 1:
                    logger.warning("⚠️  NEO browser launched but CDP not available after retries")
                    logger.warning("   This may be normal - NEO may need more time or CDP may be disabled")
                    logger.warning("   Automation will continue using fallback methods")
                    # Try to dismiss popup one more time
                    self._dismiss_restore_pages_popup()

            return True

        except Exception as e:
            logger.error(f"❌ Failed to launch NEO: {e}")
            return False

    def _dismiss_restore_pages_popup(self) -> None:
        """Dismiss 'Restore All Pages' popup using CDP or Windows API"""
        try:
            # Method 1: Use CDP if available
            if self.cdp_available:
                # Execute JavaScript to dismiss popup
                dismiss_script = """
                (function() {
                    // Try to find and click "Don't Restore" or "Cancel" button
                    var buttons = document.querySelectorAll('button, [role="button"]');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].textContent || buttons[i].innerText || '';
                        if (text.toLowerCase().includes('don\'t restore') || 
                            text.toLowerCase().includes('cancel') ||
                            text.toLowerCase().includes('no') ||
                            text.toLowerCase().includes('close')) {
                            buttons[i].click();
                            return true;
                        }
                    }
                    // Try pressing Escape key
                    var event = new KeyboardEvent('keydown', {
                        key: 'Escape',
                        code: 'Escape',
                        keyCode: 27,
                        which: 27,
                        bubbles: true
                    });
                    document.dispatchEvent(event);
                    return false;
                })();
                """
                self.execute_script(dismiss_script)
                logger.debug("   Attempted to dismiss restore pages popup via CDP")

            # Method 2: Use Windows API to send Escape key
            try:
                import ctypes
                from ctypes import wintypes

                # Find NEO window
                def enum_windows_callback(hwnd, lParam):
                    window_title = ctypes.create_unicode_buffer(512)
                    ctypes.windll.user32.GetWindowTextW(hwnd, window_title, 512)
                    title = window_title.value.lower()

                    if 'neo' in title:
                        # Send Escape key
                        VK_ESCAPE = 0x1B
                        WM_KEYDOWN = 0x0100
                        WM_KEYUP = 0x0101
                        ctypes.windll.user32.PostMessageW(hwnd, WM_KEYDOWN, VK_ESCAPE, 0)
                        ctypes.windll.user32.PostMessageW(hwnd, WM_KEYUP, VK_ESCAPE, 0)
                        logger.debug(f"   Sent Escape key to NEO window: {title}")
                    return True

                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
            except Exception as e:
                logger.debug(f"   Windows API popup dismissal failed: {e}")

        except Exception as e:
            logger.debug(f"   Error dismissing popup: {e}")

    def _connect_cdp(self, target_url: Optional[str] = None) -> bool:
        """Connect to Chrome DevTools Protocol - IMPROVED with better error handling"""
        try:
            # Try to connect to CDP endpoint
            response = requests.get(f"{self.cdp_endpoint}/json", timeout=10)
            if response.status_code == 200:
                sessions = response.json()
                if sessions:
                    # Find target session
                    target_session = None

                    # If target_url specified, find matching session
                    if target_url:
                        for session in sessions:
                            url = session.get("url", "").lower()
                            if target_url.lower() in url:
                                target_session = session
                                logger.info(f"   Found target session: {session.get('title', 'N/A')}")
                                break

                    # If no target or not found, prefer main page (not extensions)
                    if not target_session:
                        for session in sessions:
                            # Prefer pages with "proton" or "fidelity" in title/url
                            title = (session.get("title", "") or "").lower()
                            url = (session.get("url", "") or "").lower()
                            if ("proton" in title or "proton" in url or "fidelity" in title or "fidelity" in url) and "extension" not in url:
                                target_session = session
                                logger.info(f"   Found relevant session: {session.get('title', 'N/A')}")
                                break

                    # Fallback: find main page session (not extensions)
                    if not target_session:
                        for session in sessions:
                            if session.get("type") == "page" and "extension" not in session.get("url", "").lower():
                                target_session = session
                                break

                    # Final fallback: first session
                    if not target_session:
                        target_session = sessions[0]

                    self.session_id = target_session["id"]
                    self.ws_url = target_session.get("webSocketDebuggerUrl")
                    self.cdp_available = True
                    logger.info(f"✅ CDP connected (session: {target_session.get('title', 'N/A')})")
                    logger.debug(f"   URL: {target_session.get('url', 'N/A')}")
                    logger.debug(f"   WebSocket URL: {self.ws_url}")
                    return True
                else:
                    logger.debug("CDP endpoint returned empty sessions list")
            else:
                logger.debug(f"CDP endpoint returned HTTP {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"CDP connection refused: {e} (browser may still be starting)")
        except requests.exceptions.Timeout as e:
            logger.debug(f"CDP connection timeout: {e}")
        except Exception as e:
            logger.debug(f"CDP connection failed: {e}")

        self.cdp_available = False
        return False

    def cdp_command(self, method: str, params: Dict[str, Any] = None, wait_for_response: bool = True) -> Dict[str, Any]:
        """Execute CDP command using HTTP (more compatible with NEO)"""
        if not self.cdp_available:
            return {"error": "CDP not available"}

        try:
            # Get session if not already available
            if not self.session_id:
                response = requests.get(f"{self.cdp_endpoint}/json", timeout=5)
                if response.status_code == 200:
                    sessions = response.json()
                    if sessions:
                        self.session_id = sessions[0]["id"]
                        self.ws_url = sessions[0].get("webSocketDebuggerUrl")
                    else:
                        return {"error": "No CDP sessions available"}
                else:
                    return {"error": "Could not get CDP sessions"}

            # Use WebSocket for CDP (more reliable for Neo)
            if WEBSOCKET_AVAILABLE and self.ws_url:
                try:
                    import websocket
                    # Try with origin header first
                    try:
                        ws = websocket.create_connection(
                            self.ws_url, 
                            timeout=10,
                            origin="http://localhost:9222"
                        )
                    except Exception as origin_error:
                        # If origin fails, try without (some browsers don't check)
                        logger.debug(f"Origin header failed: {origin_error}, trying without")
                        ws = websocket.create_connection(self.ws_url, timeout=10)

                    command_id = int(time.time() * 1000) % 1000000
                    payload = {
                        "id": command_id,
                        "method": method,
                        "params": params or {}
                    }
                    logger.debug(f"Sending CDP command: {method} (ID: {command_id})")
                    ws.send(json.dumps(payload))

                    if wait_for_response:
                        # Wait for response with matching ID
                        timeout = time.time() + 10
                        while time.time() < timeout:
                            try:
                                response_text = ws.recv()
                                response_data = json.loads(response_text)
                                logger.debug(f"CDP response: {response_data.get('id')} == {command_id}?")

                                if response_data.get("id") == command_id:
                                    ws.close()
                                    if "error" in response_data:
                                        logger.debug(f"CDP error: {response_data['error']}")
                                    return response_data

                                # If it's an event, continue waiting
                                if "method" in response_data:
                                    logger.debug(f"CDP event: {response_data.get('method')}")
                                    continue
                            except websocket.WebSocketTimeoutException:
                                logger.debug("WebSocket timeout waiting for response")
                                break
                            except Exception as recv_error:
                                logger.debug(f"Error receiving WebSocket message: {recv_error}")
                                break

                    ws.close()
                    return {"error": "No response received"}
                except Exception as e:
                    logger.debug(f"WebSocket failed: {e}, trying HTTP fallback")
                    import traceback
                    logger.debug(traceback.format_exc())

            # Fallback to HTTP-based CDP
            # Try different endpoint formats
            endpoints = [
                f"{self.cdp_endpoint}/json/rpc",
                f"{self.cdp_endpoint}/json/{method}",
            ]

            payload = {
                "id": 1,
                "method": method,
                "params": params or {}
            }

            for cdp_url in endpoints:
                try:
                    response = requests.post(cdp_url, json=payload, timeout=10)
                    if response.status_code == 200:
                        result = response.json()
                        if "error" not in result:
                            return result
                except Exception as e:
                    logger.debug(f"HTTP endpoint {cdp_url} failed: {e}")
                    continue

            return {"error": f"All CDP endpoints failed for method: {method}"}

        except Exception as e:
            logger.debug(f"CDP command failed: {e}")
            return {"error": str(e)}

    def navigate(self, url: str) -> bool:
        """Navigate to URL"""
        if not self.cdp_available:
            logger.warning("⚠️  CDP not available, cannot navigate programmatically")
            logger.info(f"   Please navigate manually to: {url}")
            return False

        result = self.cdp_command("Page.navigate", {"url": url})
        if "error" not in result:
            time.sleep(2)  # Wait for navigation
            return True
        return False

    def execute_script(self, script: str, return_value: bool = True) -> Any:
        """Execute JavaScript in browser (works in background)"""
        if not self.cdp_available:
            logger.warning("⚠️  CDP not available, cannot execute script")
            return None

        # Wrap script in expression if it contains 'return' at top level
        # CDP requires expressions, not statements
        expression = script
        if script.strip().startswith("return "):
            # Already has return, use as-is but wrap in IIFE if needed
            expression = f"({script})"
        elif "return" in script and not script.strip().startswith("("):
            # Has return but not wrapped - wrap in IIFE
            expression = f"(function() {{ {script} }})()"

        params = {
            "expression": expression,
            "returnByValue": return_value,
            "userGesture": False  # Don't require user interaction (background operation)
        }
        result = self.cdp_command("Runtime.evaluate", params)

        if "error" not in result and "result" in result:
            result_data = result["result"]

            # Check for JavaScript errors
            if "exceptionDetails" in result_data:
                error_desc = result_data.get("result", {}).get("description", "Unknown error")
                logger.debug(f"JavaScript error: {error_desc}")
                return None

            if return_value and "value" in result_data:
                return result_data["value"]
            elif "result" in result_data:
                # Nested result structure
                nested = result_data["result"]
                if isinstance(nested, dict) and "value" in nested:
                    return nested["value"]
                return nested
            return result_data
        elif "error" in result:
            logger.debug(f"CDP error: {result['error']}")

        return None

    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        try:
            """Wait for element to appear"""
            script = f"""
            (function() {{
                var maxWait = {timeout * 1000};
                var start = Date.now();
                var checkInterval = 100;

                return new Promise(function(resolve) {{
                    var check = function() {{
                        var element = document.querySelector({json.dumps(selector)});
                        if (element || (Date.now() - start) > maxWait) {{
                            resolve(element !== null);
                        }} else {{
                            setTimeout(check, checkInterval);
                        }}
                    }};
                    check();
                }});
            }})();
            """

            result = self.execute_script(script)
            return result is True

        except Exception as e:
            self.logger.error(f"Error in wait_for_element: {e}", exc_info=True)
            raise
    def find_element(self, selector: str) -> Optional[NEOElement]:
        try:
            """Find element by selector"""
            script = f"""
            (function() {{
                var element = document.querySelector({json.dumps(selector)});
                if (element) {{
                    return {{
                        tag: element.tagName,
                        text: element.innerText || element.textContent || '',
                        attributes: Array.from(element.attributes).reduce(function(acc, attr) {{
                            acc[attr.name] = attr.value;
                            return acc;
                        }}, {{}})
                    }};
                }}
                return null;
            }})();
            """

            result = self.execute_script(script)
            if result:
                return NEOElement(
                    selector=selector,
                    tag=result.get("tag"),
                    text=result.get("text"),
                    attributes=result.get("attributes", {})
                )
            return None

        except Exception as e:
            self.logger.error(f"Error in find_element: {e}", exc_info=True)
            raise
    def click(self, selector: str) -> bool:
        try:
            """Click element"""
            script = f"""
            (function() {{
                var element = document.querySelector({json.dumps(selector)});
                if (element) {{
                    element.click();
                    return true;
                }}
                return false;
            }})();
            """

            result = self.execute_script(script)
            return result is True

        except Exception as e:
            self.logger.error(f"Error in click: {e}", exc_info=True)
            raise
    def fill(self, selector: str, text: str) -> bool:
        try:
            """Fill input field"""
            script = f"""
            (function() {{
                var element = document.querySelector({json.dumps(selector)});
                if (element) {{
                    element.value = {json.dumps(text)};
                    element.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    element.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                return false;
            }})();
            """

            result = self.execute_script(script)
            return result is True

        except Exception as e:
            self.logger.error(f"Error in fill: {e}", exc_info=True)
            raise
    def get_text(self, selector: str) -> Optional[str]:
        """Get element text"""
        element = self.find_element(selector)
        return element.text if element else None

    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get element attribute"""
        element = self.find_element(selector)
        if element and element.attributes:
            return element.attributes.get(attribute)
        return None

    def screenshot(self, path: str) -> bool:
        """Take screenshot"""
        result = self.cdp_command("Page.captureScreenshot", {"format": "png"})
        if "error" not in result and "result" in result:
            import base64
            image_data = base64.b64decode(result["result"]["data"])
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(image_data)
            logger.info(f"📸 Screenshot saved: {path}")
            return True
        return False

    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        try:
            response = requests.get(f"{self.cdp_endpoint}/json", timeout=5)
            if response.status_code == 200:
                sessions = response.json()
                if sessions:
                    return {
                        "title": sessions[0].get("title", ""),
                        "url": sessions[0].get("url", ""),
                        "type": sessions[0].get("type", "")
                    }
        except Exception:
            pass
        return {}

    def wait_for_navigation(self, timeout: int = 30) -> bool:
        """Wait for page navigation to complete"""
        script = """
        (function() {
            return document.readyState === 'complete';
        })();
        """

        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self.execute_script(script)
            if result:
                return True
            time.sleep(0.5)
        return False

    def close(self):
        """Close browser"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("🔒 NEO browser closed")
            except subprocess.TimeoutExpired:
                self.process.kill()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.process = None
                self.cdp_available = False

    def is_running(self) -> bool:
        """Check if browser is running"""
        if self.process:
            return self.process.poll() is None
        return False


def main():
    """Test NEO Browser Automation Engine"""
    import argparse

    parser = argparse.ArgumentParser(description="NEO Browser Automation Engine")
    parser.add_argument("--url", help="URL to navigate to")
    parser.add_argument("--test", action="store_true", help="Run test automation")

    args = parser.parse_args()

    try:
        engine = NEOBrowserAutomationEngine(project_root)

        if args.test:
            logger.info("🧪 Running test automation...")
            engine.launch(url="https://www.google.com")
            time.sleep(3)

            page_info = engine.get_page_info()
            logger.info(f"Page: {page_info.get('title', 'N/A')}")

            engine.screenshot("test_screenshot.png")

            engine.close()
        elif args.url:
            engine.launch(url=args.url)
            time.sleep(10)  # Keep open
            engine.close()
        else:
            logger.info("✅ NEO Browser Automation Engine ready")
            logger.info("   Use --url to navigate or --test to run test")

        return 0
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())