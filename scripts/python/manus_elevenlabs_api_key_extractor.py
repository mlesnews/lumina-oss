#!/usr/bin/env python3
"""
MANUS ElevenLabs API Key Extractor

Uses MANUS to control Neo browser and extract ElevenLabs API key,
then automatically configures it for Lumina.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from manus_neo_browser_control import MANUSNEOBrowserControl
    NEO_BROWSER_AVAILABLE = True
except ImportError:
    NEO_BROWSER_AVAILABLE = False
    MANUSNEOBrowserControl = None

logger = get_logger("MANUSElevenLabsExtractor")


class MANUSElevenLabsAPIKeyExtractor:
    """
    Extract ElevenLabs API key from Neo browser using MANUS

    Automatically finds and extracts the API key, then configures it.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if not NEO_BROWSER_AVAILABLE:
            self.logger.error("Neo browser control not available")
            raise ImportError("Neo browser control not available")

        # Connect to existing Neo browser via CDP (don't launch new one)
        self.browser = MANUSNEOBrowserControl(headless=False)
        # Try to connect to existing browser
        if not self.browser.is_running():
            self.logger.info("   Neo browser not detected via CDP, trying to connect...")
            # Browser might be running but CDP not enabled, that's okay
        self.api_key = None

    def extract_api_key_from_page(self) -> Optional[str]:
        """
        Extract API key from current Neo browser page

        Tries multiple methods to find the API key on the page.
        """
        self.logger.info("🔍 Extracting ElevenLabs API key from Neo browser...")

        # First, check if we can connect via CDP
        if not self.browser.cdp_available:
            self.logger.warning("⚠️  CDP not available - cannot extract automatically")
            self.logger.info("   Please ensure Neo browser is running with remote debugging enabled")
            return None

        try:
            # Get current page info
            page_info = self.browser.get_page_info()
            self.logger.info(f"   Current page: {page_info.get('url', 'unknown')}")

            # Method 1: Try to extract from page content
            page_content = self.browser.execute_script("""
                // Look for API key in various places
                let apiKey = null;

                // Check for input fields with API key
                const inputs = document.querySelectorAll('input[type="text"], input[type="password"]');
                for (let input of inputs) {
                    const value = input.value;
                    if (value && value.length > 20 && /^[a-zA-Z0-9]+$/.test(value)) {
                        apiKey = value;
                        break;
                    }
                }

                // Check for text content with API key pattern
                if (!apiKey) {
                    const bodyText = document.body.innerText;
                    const apiKeyMatch = bodyText.match(/[a-zA-Z0-9]{20,}/);
                    if (apiKeyMatch) {
                        apiKey = apiKeyMatch[0];
                    }
                }

                // Check for code blocks or pre elements
                if (!apiKey) {
                    const codeBlocks = document.querySelectorAll('code, pre');
                    for (let block of codeBlocks) {
                        const text = block.innerText;
                        const match = text.match(/[a-zA-Z0-9]{20,}/);
                        if (match) {
                            apiKey = match[0];
                            break;
                        }
                    }
                }

                // Check for data attributes
                if (!apiKey) {
                    const elements = document.querySelectorAll('[data-api-key], [data-key], [data-token]');
                    for (let el of elements) {
                        const key = el.getAttribute('data-api-key') || 
                                   el.getAttribute('data-key') || 
                                   el.getAttribute('data-token');
                        if (key && key.length > 20) {
                            apiKey = key;
                            break;
                        }
                    }
                }

                return apiKey;
            """)

            if page_content and len(page_content) > 20:
                self.logger.info(f"✅ Found potential API key: {page_content[:20]}...")
                return page_content

            # Method 2: Try to find "Create API Key" button and click it
            self.logger.info("   Looking for 'Create API Key' or 'Generate' button...")

            create_button = self.browser.execute_script("""
                // Find buttons that might create/generate API key
                const buttons = document.querySelectorAll('button, a, [role="button"]');
                for (let btn of buttons) {
                    const text = btn.innerText.toLowerCase();
                    if (text.includes('create') && text.includes('api') && text.includes('key') ||
                        text.includes('generate') ||
                        text.includes('new api key') ||
                        text.includes('add api key')) {
                        return btn.innerText;
                    }
                }
                return null;
            """)

            if create_button:
                self.logger.info(f"   Found button: {create_button}")
                # Could click it, but for now just log

            # Method 3: Check localStorage/sessionStorage
            self.logger.info("   Checking browser storage...")

            storage_key = self.browser.execute_script("""
                // Check localStorage
                for (let i = 0; i < localStorage.length; i++) {
                    const key = localStorage.key(i);
                    if (key && (key.includes('api') || key.includes('key') || key.includes('token'))) {
                        const value = localStorage.getItem(key);
                        if (value && value.length > 20) {
                            return value;
                        }
                    }
                }

                // Check sessionStorage
                for (let i = 0; i < sessionStorage.length; i++) {
                    const key = sessionStorage.key(i);
                    if (key && (key.includes('api') || key.includes('key') || key.includes('token'))) {
                        const value = sessionStorage.getItem(key);
                        if (value && value.length > 20) {
                            return value;
                        }
                    }
                }

                return null;
            """)

            if storage_key:
                self.logger.info(f"✅ Found key in storage: {storage_key[:20]}...")
                return storage_key

            # Method 4: Look for visible API key on page
            visible_key = self.browser.execute_script("""
                // Look for text that looks like an API key
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );

                let node;
                while (node = walker.nextNode()) {
                    const text = node.textContent.trim();
                    // API keys are usually 20+ alphanumeric characters
                    if (text.length >= 20 && /^[a-zA-Z0-9]+$/.test(text)) {
                        // Check if it's in a context that suggests it's an API key
                        const parent = node.parentElement;
                        if (parent) {
                            const parentText = parent.innerText.toLowerCase();
                            if (parentText.includes('api') || parentText.includes('key')) {
                                return text;
                            }
                        }
                    }
                }

                return null;
            """)

            if visible_key:
                self.logger.info(f"✅ Found visible API key: {visible_key[:20]}...")
                return visible_key

            self.logger.warning("⚠️  Could not automatically extract API key")
            return None

        except Exception as e:
            self.logger.error(f"❌ Error extracting API key: {e}")
            return None

    def get_api_key_from_user(self) -> Optional[str]:
        """Get API key from user input (fallback)"""
        self.logger.info("📝 Please provide your ElevenLabs API key:")
        self.logger.info("   1. Copy it from the ElevenLabs page")
        self.logger.info("   2. Or find it at: https://elevenlabs.io/app/settings/api-keys")

        # Try to get from clipboard if possible
        try:
            import pyperclip
            clipboard = pyperclip.paste()
            if clipboard and len(clipboard) > 20 and clipboard.replace('-', '').replace('_', '').isalnum():
                self.logger.info(f"   Found in clipboard: {clipboard[:20]}...")
                use_clipboard = input("   Use clipboard content? (y/n): ").strip().lower()
                if use_clipboard == 'y':
                    return clipboard
        except:
            pass

        # Manual input
        api_key = input("   Enter your ElevenLabs API key: ").strip()
        return api_key if api_key else None

    def configure_api_key(self, api_key: str) -> Dict[str, Any]:
        """
        Configure the extracted API key for Lumina

        Stores in Azure Key Vault and sets environment variable.
        """
        self.logger.info(f"🔐 Configuring API key for Lumina...")

        results = {
            'environment_variable': False,
            'key_vault': False,
            'error': None
        }

        # Set environment variable (for current session)
        try:
            import os
            os.environ['ELEVENLABS_API_KEY'] = api_key
            results['environment_variable'] = True
            self.logger.info("✅ API key set in environment variable")
        except Exception as e:
            results['error'] = str(e)
            self.logger.warning(f"⚠️  Could not set environment variable: {e}")

        # Store in Azure Key Vault (permanent)
        try:
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_client = AzureKeyVaultClient()
            success = vault_client.set_secret("elevenlabs-api-key", api_key)

            if success:
                results['key_vault'] = True
                self.logger.info("✅ API key stored in Azure Key Vault")
            else:
                self.logger.warning("⚠️  Could not store in Key Vault")
        except Exception as e:
            self.logger.warning(f"⚠️  Key Vault storage error: {e}")

        return results

    def extract_and_configure(self) -> Dict[str, Any]:
        """
        Extract API key from Neo browser and configure it

        Returns:
            Dictionary with extraction and configuration results
        """
        self.logger.info("="*80)
        self.logger.info("MANUS ELEVENLABS API KEY EXTRACTION")
        self.logger.info("="*80)

        # Extract from page
        api_key = self.extract_api_key_from_page()

        # If not found, try user input
        if not api_key:
            self.logger.info("   Automatic extraction failed, trying user input...")
            api_key = self.get_api_key_from_user()

        if not api_key:
            return {
                'success': False,
                'error': 'API key not found or provided'
            }

        # Configure
        config_results = self.configure_api_key(api_key)

        # Test
        self.logger.info("🧪 Testing voice output...")
        try:
            from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

            tts = JARVISElevenLabsTTS(project_root=self.project_root)
            if tts.api_key:
                test_result = tts.speak("JARVIS voice is now configured. Can you hear me?")

                return {
                    'success': True,
                    'api_key_extracted': True,
                    'api_key_length': len(api_key),
                    'configuration': config_results,
                    'voice_test': test_result
                }
            else:
                return {
                    'success': False,
                    'error': 'API key not configured in TTS'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Voice test error: {e}',
                'configuration': config_results
            }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS ElevenLabs API Key Extractor")
        parser.add_argument("--extract", action="store_true", help="Extract and configure API key")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        if not NEO_BROWSER_AVAILABLE:
            print("❌ Neo browser control not available")
            return 1

        extractor = MANUSElevenLabsAPIKeyExtractor(project_root)

        if args.extract:
            result = extractor.extract_and_configure()

            if result.get('success'):
                print("\n✅ API key extracted and configured!")
                print(f"   Key length: {result.get('api_key_length')} characters")
                if result.get('voice_test'):
                    print("   ✅ Voice test successful!")
            else:
                print(f"\n❌ Error: {result.get('error', 'unknown')}")
        else:
            print("Usage:")
            print("  --extract  : Extract API key from Neo browser and configure")
            print()
            print("Make sure ElevenLabs page is open in Neo browser first!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()