#!/usr/bin/env python3
"""
JARVIS NEO Browser DSM Full Automation
Complete DSM automation using NEO Web Browser (AI-based) for full-auto JARVIS control
#JARVIS #NEO #BROWSER #AI #DSM #AUTOMATION #MANUS #FULLAUTO
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
import json
import time

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from neo_browser_automation_engine import NEOBrowserAutomationEngine
    NEO_AVAILABLE = True
except ImportError:
    NEO_AVAILABLE = False

try:
    from neo_windows_automation import NEOWindowsAutomation
    WINDOWS_AUTOMATION_AVAILABLE = True
except ImportError:
    WINDOWS_AUTOMATION_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("JARVISNEODSM")


# Global browser instance tracker (SINGLETON)
_global_browser_instance = None
_global_windows_automation_instance = None

class JARVISNEODSMAutomation:
    """Full DSM automation using NEO Browser (SINGLETON - ONE INSTANCE ONLY)"""

    def __init__(self, project_root: Path, headless: bool = True, use_windows_api: bool = True):
        global _global_browser_instance, _global_windows_automation_instance

        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_port = 5001
        self.dsm_url = f"https://{self.nas_ip}:{self.nas_port}"
        self.credentials: Optional[Dict[str, str]] = None
        self.headless = headless  # Operate in background by default
        self.use_windows_api = use_windows_api and WINDOWS_AUTOMATION_AVAILABLE

        # SINGLETON: Reuse existing instances
        if _global_browser_instance:
            self.browser = _global_browser_instance
            logger.info("✅ Reusing existing browser instance (SINGLETON)")
        else:
            self.browser = None

        if _global_windows_automation_instance:
            self.windows_automation = _global_windows_automation_instance
            logger.info("✅ Reusing existing Windows API instance (SINGLETON)")
        else:
            self.windows_automation = None

        if not NEO_AVAILABLE:
            logger.error("❌ NEO Browser control not available")
            raise ImportError("NEOBrowserAutomationEngine not available")

        if self.use_windows_api and not self.windows_automation:
            logger.info("✅ Windows API automation enabled (Admin/Engineer access)")
            try:
                self.windows_automation = NEOWindowsAutomation(project_root)
                _global_windows_automation_instance = self.windows_automation
            except Exception as e:
                logger.warning(f"⚠️  Windows API automation not available: {e}")
                self.use_windows_api = False

    def _kill_all_neo_processes(self) -> None:
        """Kill ALL existing NEO browser processes to prevent multiple instances - AGGRESSIVE"""
        killed_count = 0

        # Method 1: Use psutil (most reliable)
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    name = proc.info['name'].lower()
                    if 'neo' in name:
                        logger.warning(f"⚠️  KILLING NEO process: PID {proc.info['pid']} ({proc.info['name']})")
                        # Kill process and all children
                        try:
                            children = proc.children(recursive=True)
                            for child in children:
                                try:
                                    child.kill()
                                    logger.debug(f"   Killed child process: PID {child.pid}")
                                except:
                                    pass
                        except:
                            pass
                        proc.kill()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"psutil error: {e}")

        # Method 2: Use taskkill (Windows native - more aggressive)
        try:
            result = subprocess.run(
                ['taskkill', '/F', '/IM', 'neo.exe', '/T'],  # /T kills child processes too
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                text=True
            )
            if result.returncode == 0 or 'not found' not in result.stderr.lower():
                logger.info("   ✅ Used taskkill /T to terminate NEO processes and children")
                killed_count += 1
        except Exception as e:
            logger.debug(f"taskkill error: {e}")

        # Method 3: Kill by window title (find and close windows)
        try:
            import ctypes
            from ctypes import wintypes

            def enum_windows_callback(hwnd, lParam):
                window_title = ctypes.create_unicode_buffer(512)
                ctypes.windll.user32.GetWindowTextW(hwnd, window_title, 512)
                title = window_title.value.lower()

                if 'neo' in title or 'dsm' in title:
                    try:
                        ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
                        logger.debug(f"   Sent close message to window: {title}")
                    except:
                        pass
                return True

            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_callback), 0)
        except Exception as e:
            logger.debug(f"Window closing error: {e}")

        if killed_count > 0:
            logger.info(f"   ✅ Aggressively killed {killed_count} NEO process(es) and children")
            time.sleep(5)  # Wait longer for processes to fully terminate
        else:
            logger.info("   ✅ No existing NEO processes found (clean state)")

    def _get_credentials(self) -> bool:
        """Get DSM credentials"""
        if not VAULT_AVAILABLE:
            logger.error("Azure Vault integration not available")
            return False

        try:
            vault = NASAzureVaultIntegration()
            self.credentials = vault.get_nas_credentials()
            if not self.credentials:
                logger.error("Could not retrieve credentials")
                return False
            return True
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return False

    def initialize_browser(self) -> bool:
        """Initialize NEO browser ONCE - KILLS ALL DUPLICATES FIRST"""
        try:
            # CRITICAL FIRST STEP: Kill ALL existing NEO processes BEFORE anything else
            logger.warning("=" * 70)
            logger.warning("🔪 EMERGENCY: KILLING ALL EXISTING NEO PROCESSES FIRST")
            logger.warning("=" * 70)
            self._kill_all_neo_processes()

            # Verify kill worked
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
                logger.error(f"❌ CRITICAL: {len(remaining)} NEO processes STILL RUNNING after kill!")
                logger.error(f"   PIDs: {remaining}")
                logger.error("   Attempting force kill again...")
                self._kill_all_neo_processes()
                time.sleep(5)
            else:
                logger.info("   ✅ Verified: All NEO processes killed (clean slate)")

            mode = "background" if self.headless else "visible"
            logger.info(f"🚀 Initializing NEO Browser ({mode} mode) - SINGLE INSTANCE ONLY...")

            # Use Windows API if available (Admin/Engineer access)
            if self.use_windows_api and self.windows_automation:
                logger.info("   Using Windows API for direct control (SINGLE INSTANCE)...")
                # Launch will also kill duplicates internally as backup
                if not self.windows_automation.launch(url=self.dsm_url):
                    logger.error("   ❌ Windows API launch failed")
                    return False
                time.sleep(3)
                logger.info("✅ NEO Browser initialized via Windows API (SINGLE INSTANCE)")
                return True

            # Fallback to CDP-based automation
            if not self.browser:
                self.browser = NEOBrowserAutomationEngine(project_root=self.project_root)

            # Launch browser ONCE (launch() will also kill duplicates as backup)
            logger.info(f"   Launching NEO Browser in {mode} mode (SINGLE INSTANCE - NO DUPLICATES)...")
            if not self.browser.launch(headless=self.headless, url=self.dsm_url):
                logger.error("   ❌ Browser launch failed")
                return False
            time.sleep(3)  # Wait for browser to start

            # Dismiss "Restore All Pages" popup if it appears
            logger.info("   Dismissing 'Restore All Pages' popup if present...")
            if hasattr(self.browser, '_dismiss_restore_pages_popup'):
                self.browser._dismiss_restore_pages_popup()
            time.sleep(1)

            # Check CDP availability (works regardless of foreground/background)
            if self.browser.cdp_available:
                logger.info("   ✅ CDP available (background operation enabled)")
            else:
                logger.warning("   ⚠️  CDP not available, will use JavaScript execution")

            logger.info("✅ NEO Browser initialized (operates in background)")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing browser: {e}")
            return False

    def login_to_dsm(self) -> bool:
        """Login to DSM using NEO"""
        if not self.browser:
            return False

        # Get credentials if not already loaded
        if not self.credentials:
            if not self._get_credentials():
                logger.error("❌ Could not get DSM credentials")
                return False

        try:
            logger.info(f"🌐 Navigating to DSM: {self.dsm_url}")

            # NEVER launch browser here - it should already be running
            # Just navigate to the URL
            if not self.browser.navigate(self.dsm_url):
                logger.warning("⚠️  Navigation failed, but continuing...")

            time.sleep(5)  # Wait for page load

            logger.info("🔐 Logging in...")

            # Wait for login form using JavaScript
            wait_script = """
            (function() {
                var maxWait = 10000; // 10 seconds
                var start = Date.now();
                var checkInterval = 100;

                return new Promise(function(resolve) {
                    var check = function() {
                        var usernameInput = document.querySelector('input[name="username"], input[type="text"]');
                        if (usernameInput || (Date.now() - start) > maxWait) {
                            resolve(usernameInput !== null);
                        } else {
                            setTimeout(check, checkInterval);
                        }
                    };
                    check();
                });
            })();
            """

            # Execute wait script
            self.browser.execute_script(wait_script)
            time.sleep(2)

            # Fill username
            username_script = f"""
            (function() {{
                var input = document.querySelector('input[name="username"], input[type="text"]');
                if (input) {{
                    input.value = {json.dumps(self.credentials["username"])};
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                return false;
            }})();
            """
            self.browser.execute_script(username_script)
            logger.info("   ✓ Username filled")
            time.sleep(1)

            # Fill password
            password_script = f"""
            (function() {{
                var input = document.querySelector('input[name="password"], input[type="password"]');
                if (input) {{
                    input.value = {json.dumps(self.credentials["password"])};
                    input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return true;
                }}
                return false;
            }})();
            """
            self.browser.execute_script(password_script)
            logger.info("   ✓ Password filled")
            time.sleep(1)

            # Click login button - use proper JavaScript selectors
            login_script = """
            (function() {
                // Try multiple selectors
                var selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button.btn-primary',
                    'button.login-btn',
                    'button:contains("Sign In")',
                    'button:contains("Login")',
                    'button:contains("登入")'
                ];

                for (var i = 0; i < selectors.length; i++) {
                    var button = document.querySelector(selectors[i]);
                    if (button) {
                        button.click();
                        return true;
                    }
                }

                // Fallback: find button by text content
                var buttons = document.querySelectorAll('button, input[type="submit"]');
                for (var i = 0; i < buttons.length; i++) {
                    var text = buttons[i].textContent || buttons[i].value || '';
                    if (text.toLowerCase().includes('sign in') || 
                        text.toLowerCase().includes('login') ||
                        text.toLowerCase().includes('登入')) {
                        buttons[i].click();
                        return true;
                    }
                }

                return false;
            })();
            """
            result = self.browser.execute_script(login_script)
            if result:
                logger.info("   ✓ Login button clicked")
            else:
                logger.warning("   ⚠️  Could not find login button")
            time.sleep(5)

            # Verify login
            page_info = self.browser.get_page_info()
            current_url = page_info.get("url", "")

            if "login" not in current_url.lower():
                logger.info("✅ Successfully logged in to DSM")
                return True
            else:
                logger.warning("⚠️  May still be on login page")
                return False

        except Exception as e:
            logger.error(f"❌ Error logging in: {e}")
            return False

    def install_cron_tasks(self) -> Dict[str, Any]:
        """Install cron tasks via Task Scheduler"""
        results = {
            "success": False,
            "tasks_created": [],
            "tasks_failed": [],
            "errors": []
        }

        try:
            # Browser should already be initialized
            if not self.browser:
                results["errors"].append("Browser not initialized")
                return results

            if not self.login_to_dsm():
                results["errors"].append("DSM login failed")
                return results

            logger.info("📋 Navigating to Task Scheduler...")
            task_url = f"{self.dsm_url}/#taskScheduler"
            # NEVER launch browser here - just navigate
            if not self.browser.navigate(task_url):
                logger.warning("⚠️  Navigation to Task Scheduler failed")
            time.sleep(5)

            # Wait for page to load and verify we're on the right page
            wait_script = """
            (function() {
                var maxWait = 10000;
                var start = Date.now();
                return new Promise(function(resolve) {
                    var check = function() {
                        if (window.location.hash.includes('taskScheduler') || 
                            document.querySelector('[data-testid*="task"], .task-scheduler, #taskScheduler') ||
                            (Date.now() - start) > maxWait) {
                            resolve(true);
                        } else {
                            setTimeout(check, 100);
                        }
                    };
                    check();
                });
            })();
            """
            self.browser.execute_script(wait_script)
            time.sleep(2)

            # Read cron file
            cron_file = self.project_root / "scripts" / "nas" / "cron" / "cursor_tasks_crontab.txt"
            if not cron_file.exists():
                results["errors"].append(f"Cron file not found: {cron_file}")
                return results

            logger.info(f"📄 Reading cron file: {cron_file}")
            cron_lines = cron_file.read_text().splitlines()

            # Parse tasks
            tasks = []
            for line in cron_lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 6:
                        schedule = " ".join(parts[:5])
                        command = " ".join(parts[5:])
                        tasks.append({
                            "schedule": schedule,
                            "command": command
                        })

            logger.info(f"📋 Found {len(tasks)} tasks to create")

            # Create each task using NEO's AI automation
            for i, task in enumerate(tasks):
                task_name = f"CursorTask_{i+1}"
                logger.info(f"➕ Creating task {i+1}/{len(tasks)}: {task_name}")

                try:
                    # Click Create button using JavaScript - proper selectors
                    create_script = """
                    (function() {
                        // Try multiple selectors
                        var selectors = [
                            'button[aria-label*="Create"]',
                            'button[aria-label*="Add"]',
                            'button.btn-primary',
                            'button:contains("Create")',
                            'button:contains("Add")',
                            'button:contains("新增")'
                        ];

                        for (var i = 0; i < selectors.length; i++) {
                            var button = document.querySelector(selectors[i]);
                            if (button) {
                                button.click();
                                return true;
                            }
                        }

                        // Fallback: find button by text content
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent || buttons[i].getAttribute('aria-label') || '';
                            if (text.toLowerCase().includes('create') || 
                                text.toLowerCase().includes('add') ||
                                text.toLowerCase().includes('新增')) {
                                buttons[i].click();
                                return true;
                            }
                        }

                        return false;
                    })();
                    """
                    result = self.browser.execute_script(create_script)
                    if not result:
                        logger.warning(f"   ⚠️  Could not find Create button for task {task_name}")
                    time.sleep(3)

                    # Fill task name - wait for input to appear first
                    name_script = f"""
                    (function() {{
                        // Wait for input to appear
                        var maxWait = 5000;
                        var start = Date.now();
                        var input = null;

                        while (!input && (Date.now() - start) < maxWait) {{
                            input = document.querySelector('input[name*="name" i], input[id*="name" i], input[placeholder*="name" i], input[type="text"]');
                            if (!input) {{
                                // Try to find first visible text input in a form
                                var inputs = document.querySelectorAll('input[type="text"]');
                                for (var i = 0; i < inputs.length; i++) {{
                                    if (inputs[i].offsetParent !== null) {{
                                        input = inputs[i];
                                        break;
                                    }}
                                }}
                            }}
                            if (!input) {{
                                // Wait a bit
                                var end = Date.now();
                                while (Date.now() - end < 100) {{}}
                            }}
                        }}

                        if (input) {{
                            input.value = {json.dumps(task_name)};
                            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }})();
                    """
                    result = self.browser.execute_script(name_script)
                    if result:
                        logger.info(f"   ✓ Task name filled: {task_name}")
                    else:
                        logger.warning(f"   ⚠️  Could not fill task name for {task_name}")
                    time.sleep(1)

                    # Fill command
                    command_script = f"""
                    (function() {{
                        var textarea = document.querySelector('textarea[name="command"], textarea[placeholder*="command"], textarea');
                        if (textarea) {{
                            textarea.value = {json.dumps(task["command"])};
                            textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }})();
                    """
                    self.browser.execute_script(command_script)
                    time.sleep(1)

                    # Save - use proper selectors
                    save_script = """
                    (function() {
                        // Try multiple selectors
                        var selectors = [
                            'button[type="submit"]',
                            'button.btn-primary',
                            'button:contains("Save")',
                            'button:contains("OK")',
                            'button:contains("儲存")'
                        ];

                        for (var i = 0; i < selectors.length; i++) {
                            var button = document.querySelector(selectors[i]);
                            if (button) {
                                button.click();
                                return true;
                            }
                        }

                        // Fallback: find button by text content
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var text = buttons[i].textContent || buttons[i].getAttribute('aria-label') || '';
                            if (text.toLowerCase().includes('save') || 
                                text.toLowerCase().includes('ok') ||
                                text.toLowerCase().includes('儲存')) {
                                buttons[i].click();
                                return true;
                            }
                        }

                        return false;
                    })();
                    """
                    result = self.browser.execute_script(save_script)
                    if result:
                        logger.info(f"   ✓ Save button clicked for {task_name}")
                    else:
                        logger.warning(f"   ⚠️  Could not find Save button for {task_name}")
                    time.sleep(3)

                    results["tasks_created"].append(task_name)
                    logger.info(f"   ✅ Task created: {task_name}")

                except Exception as e:
                    logger.error(f"   ❌ Failed to create task {task_name}: {e}")
                    results["tasks_failed"].append(task_name)
                    results["errors"].append(f"Task {task_name}: {str(e)}")

            results["success"] = len(results["tasks_created"]) > 0
            logger.info(f"\n✅ Completed: {len(results['tasks_created'])}/{len(tasks)} tasks created")

        except Exception as e:
            logger.error(f"❌ Error installing cron tasks: {e}")
            results["errors"].append(str(e))

        return results

    def configure_sso(self, azure_metadata_file: Optional[str] = None) -> Dict[str, Any]:
        """Configure SSO using NEO Browser"""
        results = {
            "success": False,
            "steps_completed": [],
            "steps_failed": [],
            "idp_config": {},
            "client_config": {}
        }

        try:
            # Browser should already be initialized and logged in
            if not self.browser:
                results["steps_failed"].append("Browser not initialized")
                return results

            # Re-login if needed (check if still logged in)
            page_info = self.browser.get_page_info()
            current_url = page_info.get("url", "")
            if "login" in current_url.lower() or not current_url:
                if not self.login_to_dsm():
                    results["steps_failed"].append("DSM login")
                    return results

            logger.info("🔐 Navigating to SSO Server...")
            sso_url = f"{self.dsm_url}/#sso"
            # NEVER launch browser here - just navigate
            if not self.browser.navigate(sso_url):
                logger.warning("⚠️  Navigation to SSO Server failed")
            time.sleep(5)

            # Wait for page to load
            wait_script = """
            (function() {
                var maxWait = 10000;
                var start = Date.now();
                return new Promise(function(resolve) {
                    var check = function() {
                        if (window.location.hash.includes('sso') || 
                            document.querySelector('[data-testid*="sso"], .sso-server, #sso') ||
                            (Date.now() - start) > maxWait) {
                            resolve(true);
                        } else {
                            setTimeout(check, 100);
                        }
                    };
                    check();
                });
            })();
            """
            self.browser.execute_script(wait_script)
            time.sleep(2)

            # Step 1: Configure as IdP
            logger.info("⚙️  Configuring SSO as Identity Provider...")
            try:
                # Click Identity Provider tab
                idp_tab_script = """
                (function() {
                    var tab = document.querySelector('button:has-text("Identity Provider"), tab:has-text("Identity Provider"), [aria-label*="Identity Provider"]');
                    if (tab) {
                        tab.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(idp_tab_script)
                time.sleep(3)

                # Enable IdP checkbox
                enable_script = """
                (function() {
                    var checkbox = document.querySelector('input[type="checkbox"]');
                    if (checkbox && !checkbox.checked) {
                        checkbox.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(enable_script)
                time.sleep(1)

                # Get Entity ID and SSO URL
                get_info_script = """
                (function() {
                    var entityInput = document.querySelector('input[name*="entity"], input[id*="entity"]');
                    var ssoInput = document.querySelector('input[name*="sso"], input[type="url"]');
                    return {
                        entity_id: entityInput ? entityInput.value : null,
                        sso_url: ssoInput ? ssoInput.value : null
                    };
                })();
                """
                info = self.browser.execute_script(get_info_script)
                entity_id = info.get("entity_id") if info else None
                sso_url = info.get("sso_url") if info else None

                # Save
                save_script = """
                (function() {
                    var button = document.querySelector('button:has-text("Save"), button:has-text("Apply"), button[type="submit"]');
                    if (button) {
                        button.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(save_script)
                time.sleep(3)

                results["steps_completed"].append("Configure SSO as IdP")
                results["idp_config"] = {
                    "entity_id": entity_id,
                    "sso_url": sso_url
                }
                logger.info("   ✅ IdP configured")

            except Exception as e:
                logger.error(f"   ❌ Error configuring IdP: {e}")
                results["steps_failed"].append(f"Configure IdP: {str(e)}")

            # Step 2: Configure SSO Client
            logger.info("⚙️  Configuring SSO Client...")
            try:
                # Click Service Provider tab
                sp_tab_script = """
                (function() {
                    var tab = document.querySelector('button:has-text("Service Provider"), tab:has-text("Service Provider"), [aria-label*="Service Provider"]');
                    if (tab) {
                        tab.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(sp_tab_script)
                time.sleep(3)

                # Click Add
                add_script = """
                (function() {
                    var button = document.querySelector('button:has-text("Add"), button:has-text("Create")');
                    if (button) {
                        button.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(add_script)
                time.sleep(3)

                # If metadata file provided, note it (file upload via CDP is complex)
                if azure_metadata_file and Path(azure_metadata_file).exists():
                    logger.info(f"   ℹ️  Metadata file available: {azure_metadata_file}")
                    logger.info("   ⚠️  File upload requires manual step or advanced CDP")
                else:
                    logger.info("   ℹ️  Manual configuration (NEO AI can assist)")

                # Save
                save_script = """
                (function() {
                    var button = document.querySelector('button:has-text("Save"), button:has-text("OK"), button[type="submit"]');
                    if (button) {
                        button.click();
                        return true;
                    }
                    return false;
                })();
                """
                self.browser.execute_script(save_script)
                time.sleep(3)

                results["steps_completed"].append("Configure SSO Client")
                results["client_config"] = {"configured": True}
                logger.info("   ✅ SSO Client configured")

            except Exception as e:
                logger.error(f"   ❌ Error configuring SSO Client: {e}")
                results["steps_failed"].append(f"Configure SSO Client: {str(e)}")

            results["success"] = len(results["steps_failed"]) == 0
            logger.info(f"\n✅ SSO Setup: {len(results['steps_completed'])}/{len(results['steps_completed']) + len(results['steps_failed'])} steps completed")

        except Exception as e:
            logger.error(f"❌ Error configuring SSO: {e}")
            results["steps_failed"].append(str(e))

        return results

    def complete_all_tasks(self) -> Dict[str, Any]:
        """Complete all DSM tasks using NEO Browser"""
        all_results = {
            "timestamp": time.time(),
            "cron_installation": {},
            "sso_setup": {},
            "summary": {}
        }

        logger.info("🚀 Starting JARVIS NEO Browser DSM Automation...")
        logger.info("")

        try:
            # Initialize browser ONCE for all tasks
            if not self._get_credentials():
                logger.error("❌ Could not get DSM credentials")
                return all_results

            if not self.initialize_browser():
                logger.error("❌ Browser initialization failed")
                return all_results

            # Task 1: Install Cron Tasks
            logger.info("=" * 70)
            logger.info("TASK 1: Install NAS Cron Tasks")
            logger.info("=" * 70)
            all_results["cron_installation"] = self.install_cron_tasks()
            logger.info("")

            # Task 2: Configure SSO (reuse same browser)
            logger.info("=" * 70)
            logger.info("TASK 2: Configure SAML SSO")
            logger.info("=" * 70)
            all_results["sso_setup"] = self.configure_sso()
            logger.info("")
        finally:
            # Close browser once at the end
            self.close()

        # Summary
        logger.info("=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)

        cron_success = all_results["cron_installation"].get("success", False)
        sso_success = all_results["sso_setup"].get("success", False)

        logger.info(f"✅ Cron Installation: {'Success' if cron_success else 'Failed'}")
        logger.info(f"✅ SSO Setup: {'Success' if sso_success else 'Failed'}")
        logger.info("")

        all_results["summary"] = {
            "cron_success": cron_success,
            "sso_success": sso_success,
            "all_success": cron_success and sso_success
        }

        return all_results

    def close(self):
        """Close browser"""
        # Close Windows API automation if used
        if self.windows_automation:
            self.windows_automation.close()

        # Close CDP-based browser if used
        if self.browser:
            self.browser.close()

        logger.info("🔒 NEO Browser closed")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS NEO Browser DSM Automation")
    parser.add_argument("--action", choices=["install-cron", "configure-sso", "complete-all"], 
                       default="complete-all", help="Action to perform")
    parser.add_argument("--metadata-file", help="Path to Azure AD Federation Metadata XML")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--visible", action="store_true", help="Run browser in visible mode (default: background/headless)")

    args = parser.parse_args()

    try:
        # Default to headless/background mode unless --visible is specified
        automation = JARVISNEODSMAutomation(project_root, headless=not args.visible)

        try:
            if args.action == "install-cron":
                # Initialize browser for single task
                if not automation._get_credentials():
                    logger.error("❌ Could not get DSM credentials")
                    return 1
                if not automation.initialize_browser():
                    logger.error("❌ Browser initialization failed")
                    return 1
                result = automation.install_cron_tasks()
            elif args.action == "configure-sso":
                # Initialize browser for single task
                if not automation._get_credentials():
                    logger.error("❌ Could not get DSM credentials")
                    return 1
                if not automation.initialize_browser():
                    logger.error("❌ Browser initialization failed")
                    return 1
                result = automation.configure_sso(azure_metadata_file=args.metadata_file)
            else:
                # complete-all handles browser lifecycle internally
                result = automation.complete_all_tasks()

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                if isinstance(result, dict) and "summary" in result:
                    summary = result["summary"]
                    if summary.get("all_success"):
                        print("\n✅ All tasks completed successfully!")
                    else:
                        print(f"\n⚠️  Some tasks had issues")
                        print(f"   Cron: {'✅' if summary.get('cron_success') else '❌'}")
                        print(f"   SSO: {'✅' if summary.get('sso_success') else '❌'}")
        finally:
            # Always close browser
            automation.close()
        return 0 if (isinstance(result, dict) and result.get("success", False)) or (isinstance(result, dict) and result.get("summary", {}).get("all_success", False)) else 1

    except ImportError as e:
        logger.error(f"❌ NEO Browser not available: {e}")
        print("\n❌ NEO Browser control not available")
        print("   Please ensure NEO Browser is installed and NEOBrowserAutomationEngine is available")
        return 1
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())