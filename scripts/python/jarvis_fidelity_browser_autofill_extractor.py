#!/usr/bin/env python3
"""
JARVIS Fidelity Browser Autofill Extractor
Uses browser autofill to get credentials, then extracts from form

This approach:
1. Navigates to Fidelity login page
2. Waits for browser/ProtonPass extension to autofill credentials
3. Extracts username and password from filled form fields
4. Uses credentials for @MANUS automation

Tags: #FIDELITY #BROWSER #AUTOFILL #AUTOMATION #JARVIS #@MANUS
"""

import sys
import json
import time
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

logger = get_logger("JARVISFidelityBrowserAutofillExtractor")


class JARVISFidelityBrowserAutofillExtractor:
    """
    Extract Fidelity credentials using browser autofill

    Navigates to Fidelity login, triggers autofill, extracts from form
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize extractor"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.fidelity_login_url = "https://digital.fidelity.com/ftgw/digital/login"

        logger.info("=" * 70)
        logger.info("🤖 JARVIS FIDELITY BROWSER AUTOFILL EXTRACTOR")
        logger.info("=" * 70)
        logger.info("   Using browser autofill to extract credentials")
        logger.info("   Fully automated - NO MANUAL STEPS")
        logger.info("")

    def extract_via_autofill(self) -> Dict[str, Any]:
        """
        Extract credentials using browser autofill

        Uses Neo browser automation to:
        1. Navigate to Fidelity login
        2. Trigger autofill
        3. Extract from form fields
        """
        logger.info("=" * 70)
        logger.info("🚀 EXTRACTING CREDENTIALS VIA BROWSER AUTOFILL")
        logger.info("=" * 70)
        logger.info("")

        try:
            from neo_browser_automation_engine import NEOBrowserAutomationEngine

            logger.info("✅ Neo Browser Automation Engine found")

            # Initialize Neo automation
            neo = NEOBrowserAutomationEngine(self.project_root)

            # Connect to existing Neo instance or launch
            if not neo._connect_cdp():
                logger.info("   Launching Neo browser...")
                if not neo.launch(url=self.fidelity_login_url, headless=False):
                    return {"success": False, "error": "Failed to launch Neo browser"}
            else:
                logger.info("   Connected to existing Neo instance")
                neo.navigate(self.fidelity_login_url)
                time.sleep(3)

            logger.info("✅ Neo browser ready")
            logger.info("")

            # Step 1: Navigate to Fidelity login
            logger.info("STEP 1: Navigating to Fidelity login page...")
            logger.info(f"   URL: {self.fidelity_login_url}")
            neo.navigate(self.fidelity_login_url)
            time.sleep(5)  # Wait for page load and potential autofill

            # Step 2: Trigger autofill by focusing on username field
            logger.info("")
            logger.info("STEP 2: Triggering browser autofill...")

            trigger_autofill_script = """
            // Find username/email input field
            const usernameSelectors = [
                'input[type="email"]',
                'input[name*="user" i]',
                'input[name*="login" i]',
                'input[id*="user" i]',
                'input[id*="login" i]',
                'input[placeholder*="user" i]',
                'input[placeholder*="email" i]'
            ];

            let usernameField = null;
            for (const selector of usernameSelectors) {
                usernameField = document.querySelector(selector);
                if (usernameField) break;
            }

            if (usernameField) {
                // Focus and click to trigger autofill
                usernameField.focus();
                usernameField.click();

                // Trigger autofill dropdown
                usernameField.dispatchEvent(new Event('focus', { bubbles: true }));
                usernameField.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowDown', bubbles: true }));

                // Wait a moment for autofill
                setTimeout(() => {
                    // Try to accept autofill (usually first option)
                    const event = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
                    usernameField.dispatchEvent(event);
                }, 500);

                return JSON.stringify({ success: true, message: 'Autofill triggered on username field' });
            }

            return JSON.stringify({ success: false, message: 'Username field not found' });
            """

            trigger_result = neo.execute_script(trigger_autofill_script)
            if trigger_result:
                try:
                    result_data = json.loads(trigger_result)
                    logger.info(f"   Autofill trigger: {result_data.get('message', 'Unknown')}")
                except:
                    logger.info(f"   Autofill trigger: {trigger_result}")

            time.sleep(3)  # Wait for autofill to complete

            # Step 3: Extract credentials from form fields
            logger.info("")
            logger.info("STEP 3: Extracting credentials from form fields...")

            extract_script = """
            // Extract username and password from form fields
            const result = { username: null, password: null };

            // Find username field
            const usernameSelectors = [
                'input[type="email"]',
                'input[name*="user" i]',
                'input[name*="login" i]',
                'input[id*="user" i]',
                'input[id*="login" i]'
            ];

            for (const selector of usernameSelectors) {
                const field = document.querySelector(selector);
                if (field && field.value) {
                    result.username = field.value;
                    break;
                }
            }

            // Find password field
            const passwordField = document.querySelector('input[type="password"]');
            if (passwordField && passwordField.value) {
                result.password = passwordField.value;
            }

            // If password is masked, try to reveal it
            if (!result.password) {
                // Look for reveal/show password button
                const revealButton = document.querySelector('button[aria-label*="show" i], button[aria-label*="reveal" i], button[type="button"]');
                if (revealButton) {
                    revealButton.click();
                    // Wait and check again
                    setTimeout(() => {
                        const textField = document.querySelector('input[type="text"][name*="pass" i]');
                        if (textField && textField.value) {
                            result.password = textField.value;
                        }
                    }, 500);
                }
            }

            return JSON.stringify(result);
            """

            credentials_json = neo.execute_script(extract_script)
            time.sleep(1)  # Wait for any reveal operations

            # Try extraction again if first attempt didn't get password
            if credentials_json:
                try:
                    credentials = json.loads(credentials_json)
                    if not credentials.get("password"):
                        # Try one more time after reveal
                        credentials_json = neo.execute_script(extract_script)
                        if credentials_json:
                            credentials = json.loads(credentials_json)
                except:
                    pass

            if credentials_json:
                try:
                    credentials = json.loads(credentials_json)

                    if credentials.get("username") and credentials.get("password"):
                        logger.info("   ✅ Credentials extracted from form")
                        logger.info(f"   Username: ✅")
                        logger.info(f"   Password: ✅")

                        return {
                            "success": True,
                            "username": credentials["username"],
                            "password": credentials["password"],
                            "source": "browser_autofill_fidelity_login"
                        }
                    else:
                        logger.warning("   ⚠️  Partial credentials found")
                        logger.info(f"   Username: {'✅' if credentials.get('username') else '❌'}")
                        logger.info(f"   Password: {'✅' if credentials.get('password') else '❌'}")

                        if credentials.get("username"):
                            # We have username, password might be in browser but not filled yet
                            logger.info("   💡 Username found - password may need manual trigger")
                            return {
                                "success": False,
                                "username": credentials.get("username"),
                                "password": None,
                                "source": "browser_autofill_partial",
                                "next_step": "Password may need to be filled manually or extracted differently"
                            }
                except json.JSONDecodeError:
                    logger.error("   ❌ Failed to parse credentials JSON")

            logger.warning("   ⚠️  No credentials extracted from form")
            return {"success": False, "error": "No credentials found in form fields"}

        except ImportError as e:
            logger.error(f"❌ Neo browser automation not available: {e}")
            return {"success": False, "error": f"Neo automation not available: {e}"}
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return {"success": False, "error": str(e)}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Browser Autofill Extractor")
    parser.add_argument("--extract", "-e", action="store_true", help="Extract credentials via autofill")

    args = parser.parse_args()

    extractor = JARVISFidelityBrowserAutofillExtractor()

    if args.extract:
        result = extractor.extract_via_autofill()
        if result.get("success"):
            print(f"\n✅ Credentials extracted successfully!")
            print(f"   Username: {result['username']}")
            print(f"   Password: {'***' if result['password'] else 'Not found'}")
            print(f"   Source: {result['source']}")
        else:
            print(f"\n⚠️  Extraction result: {result.get('error', 'Unknown error')}")
            if result.get("username"):
                print(f"   Username found: {result['username']}")
                print(f"   Next: {result.get('next_step', 'Try alternative method')}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()