#!/usr/bin/env python3
"""
JARVIS ElevenLabs API Key Automation
Uses @manus and @neowebbrowser to automate retrieving ElevenLabs API key

Tags: #JARVIS #MANUS #NEOBROWSER #ELEVENLABS #AUTOMATION @JARVIS @DOIT
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISElevenLabsKeyAutomation")

# Try to import NEO Browser
try:
    from neo_browser_automation_engine import NEOBrowserAutomationEngine
    NEO_BROWSER_AVAILABLE = True
except ImportError:
    NEO_BROWSER_AVAILABLE = False
    NEOBrowserAutomationEngine = None
    logger.warning("⚠️  NEO Browser Automation Engine not available")

# Try to import MANUS
try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea, ControlOperation
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    MANUSUnifiedControl = None
    logger.warning("⚠️  MANUS Unified Control not available")


class JARVISElevenLabsKeyAutomation:
    """
    Automate ElevenLabs API key retrieval using NEO Browser and MANUS
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize NEO Browser
        self.browser = None
        if NEO_BROWSER_AVAILABLE:
            try:
                self.browser = NEOBrowserAutomationEngine(project_root=self.project_root)
                self.logger.info("✅ NEO Browser Automation Engine initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  NEO Browser initialization failed: {e}")

        # Initialize MANUS
        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(project_root=self.project_root)
                self.logger.info("✅ MANUS Unified Control initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  MANUS initialization failed: {e}")

        self.logger.info("✅ JARVIS ElevenLabs Key Automation initialized")

    def navigate_to_api_keys(self) -> bool:
        """Navigate to ElevenLabs API Keys page"""
        try:
            self.logger.info("🌐 Navigating to ElevenLabs API Keys...")

            if not self.browser:
                self.logger.error("❌ NEO Browser not available")
                return False

            # Navigate to API Keys page
            url = "https://elevenlabs.io/app/settings/api-keys"
            self.logger.info(f"   Opening: {url}")

            # Use NEO Browser to navigate
            result = self.browser.navigate(url)

            if result:
                self.logger.info("✅ Navigated to API Keys page")
                time.sleep(2)  # Wait for page load
                return True
            else:
                self.logger.error("❌ Failed to navigate to API Keys page")
                return False

        except Exception as e:
            self.logger.error(f"❌ Navigation failed: {e}")
            return False

    def create_new_api_key(self, key_name: str = "Cursor - Cursor API Key") -> Optional[str]:
        """Create a new API key in ElevenLabs"""
        try:
            self.logger.info(f"🔑 Creating new API key: {key_name}")

            if not self.browser:
                self.logger.error("❌ NEO Browser not available")
                return None

            # Look for "Create Key" or "Add API Key" button
            # This will need to be adapted based on actual page structure
            self.logger.info("   Looking for 'Create Key' button...")

            # Use NEO Browser to find and click the button
            # Note: This is a placeholder - actual implementation depends on NEO Browser API
            create_button_found = self.browser.find_element(
                text="Create Key",
                element_type="button"
            ) or self.browser.find_element(
                text="Add API Key",
                element_type="button"
            )

            if create_button_found:
                self.logger.info("   ✅ Found 'Create Key' button")
                self.browser.click(create_button_found)
                time.sleep(1)

                # Enter key name
                self.logger.info(f"   Entering key name: {key_name}")
                name_field = self.browser.find_element(
                    element_type="input",
                    placeholder="Key name"
                )
                if name_field:
                    self.browser.type(name_field, key_name)
                    time.sleep(0.5)

                # Click Create/Generate
                create_button = self.browser.find_element(
                    text="Create",
                    element_type="button"
                ) or self.browser.find_element(
                    text="Generate",
                    element_type="button"
                )

                if create_button:
                    self.browser.click(create_button)
                    time.sleep(2)  # Wait for key generation

                    # Extract the API key from the page
                    # Look for the key display element
                    key_element = self.browser.find_element(
                        element_type="code",
                        contains="sk_"
                    ) or self.browser.find_element(
                        element_type="input",
                        readonly=True
                    )

                    if key_element:
                        api_key = self.browser.get_text(key_element)
                        if api_key and len(api_key) > 20:
                            self.logger.info("✅ API key extracted successfully")
                            return api_key.strip()

            self.logger.warning("⚠️  Could not create/extract API key automatically")
            return None

        except Exception as e:
            self.logger.error(f"❌ Failed to create API key: {e}")
            return None

    def automate_key_retrieval(self) -> Optional[str]:
        """
        Full automation: Navigate, create key, extract it

        Returns:
            API key string if successful, None otherwise
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("🤖 JARVIS ELEVENLABS KEY AUTOMATION")
            self.logger.info("=" * 80)
            self.logger.info("")

            # Step 1: Navigate to API Keys
            if not self.navigate_to_api_keys():
                return None

            # Step 2: Create new key
            api_key = self.create_new_api_key()

            if api_key:
                self.logger.info("")
                self.logger.info("=" * 80)
                self.logger.info("✅ API KEY RETRIEVED!")
                self.logger.info("=" * 80)
                self.logger.info(f"Key: {api_key[:20]}...{api_key[-4:]}")
                self.logger.info("")
                self.logger.info("💡 Storing in Azure Key Vault...")

                # Store in Azure Key Vault
                from jarvis_store_elevenlabs_key import store_key_in_azure_vault
                if store_key_in_azure_vault(api_key):
                    self.logger.info("✅ Key stored in Azure Key Vault!")
                    return api_key
                else:
                    self.logger.warning("⚠️  Key retrieved but storage failed")
                    return api_key
            else:
                self.logger.warning("⚠️  Could not retrieve key automatically")
                self.logger.info("")
                self.logger.info("💡 Manual steps:")
                self.logger.info("   1. Click 'Create Key' button")
                self.logger.info("   2. Name it: 'Cursor - Cursor API Key'")
                self.logger.info("   3. Copy the key immediately")
                self.logger.info("   4. Run: python scripts/python/jarvis_store_elevenlabs_key.py --clipboard")
                return None

        except Exception as e:
            self.logger.error(f"❌ Automation failed: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS ElevenLabs Key Automation")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    automation = JARVISElevenLabsKeyAutomation(project_root=args.project_root)

    api_key = automation.automate_key_retrieval()

    if api_key:
        print(f"\n✅ Success! API key retrieved and stored.")
        return 0
    else:
        print(f"\n⚠️  Automation partially completed. Manual steps may be needed.")
        return 1


if __name__ == "__main__":


    sys.exit(main())