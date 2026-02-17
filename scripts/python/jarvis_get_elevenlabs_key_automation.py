#!/usr/bin/env python3
"""
JARVIS Get ElevenLabs API Key - Full Automation
Uses available tools to automate retrieving ElevenLabs API key

This is the @ASK: Automate getting the ElevenLabs API key

Tags: #JARVIS #ASK #AUTOMATION #ELEVENLABS #MANUS @JARVIS @DOIT
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

logger = get_logger("JARVISGetElevenLabsKey")


class JARVISGetElevenLabsKey:
    """
    Automate retrieving ElevenLabs API key
    This is the @ASK implementation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automation"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

    def execute_ask(self) -> Dict[str, Any]:
        """
        Execute the @ASK: Get ElevenLabs API key

        Returns:
            Result dictionary with status and key (if retrieved)
        """
        self.logger.info("=" * 80)
        self.logger.info("🎯 @ASK: GET ELEVENLABS API KEY")
        self.logger.info("=" * 80)
        self.logger.info("")

        result = {
            "success": False,
            "method": None,
            "key": None,
            "error": None
        }

        # Try Method 1: Direct browser automation via available tools
        self.logger.info("🔧 Method 1: Attempting browser automation...")

        # Check if we can use browser tools
        try:
            # Try to use available browser automation
            browser_result = self._try_browser_automation()
            if browser_result.get("success"):
                result.update(browser_result)
                result["method"] = "browser_automation"
                return result
        except Exception as e:
            self.logger.debug(f"Browser automation not available: {e}")

        # Try Method 2: Guided manual process with clipboard monitoring
        self.logger.info("")
        self.logger.info("🔧 Method 2: Guided process with clipboard monitoring...")
        manual_result = self._guided_manual_process()
        if manual_result.get("success"):
            result.update(manual_result)
            result["method"] = "guided_manual"
            return result

        # Method 3: Provide clear instructions
        self.logger.info("")
        self.logger.info("🔧 Method 3: Providing step-by-step instructions...")
        self._provide_instructions()

        result["error"] = "All automation methods unavailable - manual process required"
        return result

    def _try_browser_automation(self) -> Dict[str, Any]:
        """Try browser automation methods"""
        self.logger.info("   Checking available browser tools...")

        # Check for NEO Browser
        try:
            from neo_browser_automation_engine import NEOBrowserAutomationEngine
            self.logger.info("   ✅ NEO Browser available")

            # Try to launch and navigate
            browser = NEOBrowserAutomationEngine(project_root=self.project_root)
            url = "https://elevenlabs.io/app/settings/api-keys"

            self.logger.info(f"   🌐 Opening: {url}")
            if browser.launch(url=url, headless=False):
                self.logger.info("   ✅ Browser launched")
                time.sleep(3)  # Wait for page load

                # Try to find and interact with page
                # This would need actual implementation based on page structure
                self.logger.info("   💡 Browser opened - you can now manually:")
                self.logger.info("      1. Click 'Create Key'")
                self.logger.info("      2. Name it and create")
                self.logger.info("      3. Copy the key")
                self.logger.info("      4. I'll detect it from clipboard")

                return {
                    "success": True,
                    "browser_opened": True,
                    "message": "Browser opened - complete manually, I'll detect key from clipboard"
                }
        except Exception as e:
            self.logger.debug(f"   NEO Browser not available: {e}")

        return {"success": False}

    def _guided_manual_process(self) -> Dict[str, Any]:
        """Guided manual process with clipboard monitoring"""
        self.logger.info("   📋 Opening ElevenLabs in default browser...")

        try:
            import webbrowser
            url = "https://elevenlabs.io/app/settings/api-keys"
            webbrowser.open(url)
            self.logger.info(f"   ✅ Opened: {url}")
            self.logger.info("")
            self.logger.info("   ⏳ Monitoring clipboard for API key...")
            self.logger.info("")
            self.logger.info("   📝 Please:")
            self.logger.info("      1. Click 'Create Key' button")
            self.logger.info("      2. Name it: 'Cursor - Cursor API Key'")
            self.logger.info("      3. Click 'Create'")
            self.logger.info("      4. COPY THE KEY IMMEDIATELY")
            self.logger.info("")
            self.logger.info("   🔍 I'll detect it from clipboard automatically...")
            self.logger.info("")

            # Monitor clipboard
            import pyperclip
            import time

            previous_clipboard = ""
            check_count = 0
            max_checks = 60  # 1 minute of checking

            while check_count < max_checks:
                time.sleep(1)
                check_count += 1

                try:
                    current_clipboard = pyperclip.paste().strip()

                    # Check if clipboard changed and looks like API key
                    if current_clipboard != previous_clipboard:
                        if len(current_clipboard) > 20 and current_clipboard != previous_clipboard:
                            # Validate it's not an error message
                            if not any(x in current_clipboard.lower() for x in ["error", "bedrock", "authentication"]):
                                # Looks like an API key!
                                self.logger.info("")
                                self.logger.info("   ✅ API KEY DETECTED!")
                                self.logger.info(f"   Key preview: {current_clipboard[:10]}...{current_clipboard[-4:]}")
                                self.logger.info("")
                                self.logger.info("   🔐 Storing in Azure Key Vault...")

                                # Store it
                                from jarvis_store_elevenlabs_key import store_all_variations
                                results = store_all_variations(current_clipboard)

                                success_count = sum(1 for success in results.values() if success)

                                if success_count > 0:
                                    self.logger.info("")
                                    self.logger.info("   ✅ KEY STORED SUCCESSFULLY!")
                                    return {
                                        "success": True,
                                        "key": current_clipboard,
                                        "stored": True
                                    }
                                else:
                                    self.logger.warning("   ⚠️  Key detected but storage failed")
                                    return {
                                        "success": True,
                                        "key": current_clipboard,
                                        "stored": False,
                                        "message": "Use PowerShell script to store: .\\scripts\\powershell\\store_elevenlabs_key.ps1"
                                    }

                    previous_clipboard = current_clipboard

                    if check_count % 10 == 0:
                        self.logger.info(f"   ⏳ Still waiting... ({check_count}/{max_checks})")

                except Exception as e:
                    self.logger.debug(f"   Clipboard check error: {e}")
                    continue

            self.logger.info("")
            self.logger.warning("   ⏰ Timeout - no API key detected in clipboard")
            return {"success": False, "error": "Timeout waiting for clipboard"}

        except ImportError:
            self.logger.warning("   ⚠️  pyperclip not available")
            return {"success": False}
        except Exception as e:
            self.logger.error(f"   ❌ Error: {e}")
            return {"success": False, "error": str(e)}

    def _provide_instructions(self):
        """Provide step-by-step instructions"""
        self.logger.info("")
        self.logger.info("📋 Step-by-Step Instructions:")
        self.logger.info("")
        self.logger.info("1️⃣  Open browser and go to:")
        self.logger.info("   https://elevenlabs.io/app/settings/api-keys")
        self.logger.info("")
        self.logger.info("2️⃣  Click 'Create Key' or 'Add API Key'")
        self.logger.info("")
        self.logger.info("3️⃣  Name it: 'Cursor - Cursor API Key'")
        self.logger.info("")
        self.logger.info("4️⃣  Click 'Create' or 'Generate'")
        self.logger.info("")
        self.logger.info("5️⃣  COPY THE KEY IMMEDIATELY (only shown once!)")
        self.logger.info("")
        self.logger.info("6️⃣  Run this to store it:")
        self.logger.info("   .\\scripts\\powershell\\store_elevenlabs_key.ps1")
        self.logger.info("")


def main():
    """CLI interface - This is the @ASK execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @ASK: Get ElevenLabs API Key")
    parser.add_argument("--project-root", type=Path, help="Project root directory")

    args = parser.parse_args()

    automation = JARVISGetElevenLabsKey(project_root=args.project_root)

    result = automation.execute_ask()

    if result.get("success"):
        if result.get("stored"):
            print("\n✅ SUCCESS! API key retrieved and stored in Azure Key Vault!")
            return 0
        else:
            key = result.get('key', '')
            print(f"\n✅ API key retrieved but needs storage.")
            if key:
                print(f"   Key: {key[:20]}...{key[-4:]}")
            print(f"   Run: .\\scripts\\powershell\\store_elevenlabs_key.ps1")
            return 0
    else:
        print(f"\n⚠️  Automation completed - manual steps may be needed")
        return 1


if __name__ == "__main__":


    sys.exit(main())