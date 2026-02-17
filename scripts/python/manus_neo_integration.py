#!/usr/bin/env python3
"""
MANUS-NEO Browser Integration Layer

High-level integration for MANUS to control NEO browser.
This provides simple, intuitive interfaces for common automation tasks.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Import the full control system
from manus_neo_browser_control import MANUSNEOBrowserControl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MANUS-NEO-Integration")


class MANUSNEOIntegration:
    """
    MANUS-NEO Browser Integration

    High-level interface for MANUS to control NEO browser.
    Simplifies common automation tasks.
    """

    def __init__(self):
        self.browser = MANUSNEOBrowserControl(headless=False)
        logger.info("✅ MANUS-NEO Integration initialized")

    def open_website(self, url: str) -> bool:
        """Open a website in NEO browser"""
        logger.info(f"🌐 Opening: {url}")
        return self.browser.launch(url)

    def get_cookies_for_domain(self, domain: str) -> list:
        """Get all cookies for a specific domain"""
        logger.info(f"🍪 Getting cookies for: {domain}")

        # Launch browser if not running
        if not self.browser.is_running():
            self.browser.launch()

        return self.browser.get_cookies(domain=domain)

    def automate_elevenlabs_setup(self) -> Dict[str, Any]:
        """
        Automate ElevenLabs account setup and API key retrieval

        Returns:
            Dict with success status and API key if successful
        """
        logger.info("🎙️  Starting ElevenLabs setup automation...")

        # Step 1: Open ElevenLabs
        if not self.browser.launch("https://elevenlabs.io"):
            return {"success": False, "error": "Failed to launch browser"}

        import time
        time.sleep(3)

        # Step 2: Navigate to signup/login
        # User will manually complete signup/login

        # Step 3: Navigate to API key page
        logger.info("   → Navigate to API key page...")
        self.browser.navigate("https://elevenlabs.io/app/settings/api-keys")
        time.sleep(3)

        # Step 4: Extract API key from page
        api_key = self.browser.extract_api_key_from_page("elevenlabs.io")

        if api_key:
            logger.info(f"   ✅ API key found: {api_key[:20]}...")

            # Step 5: Store in Azure Key Vault
            import subprocess
            try:
                result = subprocess.run([
                    "az", "keyvault", "secret", "set",
                    "--vault-name", "jarvis-lumina",
                    "--name", "elevenlabs-api-key",
                    "--value", api_key
                ], capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    logger.info("   ✅ API key stored in Azure Key Vault")
                    return {
                        "success": True,
                        "api_key": api_key,
                        "message": "API key retrieved and stored"
                    }
                else:
                    return {
                        "success": True,
                        "api_key": api_key,
                        "vault_error": result.stderr,
                        "message": "API key retrieved but vault storage failed"
                    }
            except Exception as e:
                return {
                    "success": True,
                    "api_key": api_key,
                    "vault_error": str(e),
                    "message": "API key retrieved but vault storage failed"
                }
        else:
            return {
                "success": False,
                "error": "API key not found on page",
                "message": "Please ensure you're on the API key page and the key is visible"
            }

    def close(self):
        """Close browser"""
        self.browser.close()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS-NEO Browser Integration")
    parser.add_argument("--open", type=str, help="Open URL")
    parser.add_argument("--cookies", type=str, help="Get cookies for domain")
    parser.add_argument("--elevenlabs", action="store_true", help="Automate ElevenLabs setup")

    args = parser.parse_args()

    integration = MANUSNEOIntegration()

    try:
        if args.open:
            integration.open_website(args.open)
            print(f"\n✅ Browser opened: {args.open}")
            print("Press Enter to close...")
            input()

        elif args.cookies:
            cookies = integration.get_cookies_for_domain(args.cookies)
            print(f"\n🍪 Cookies for {args.cookies}:")
            for cookie in cookies[:10]:
                print(f"  {cookie['name']}: {cookie['value'][:50]}")

        elif args.elevenlabs:
            result = integration.automate_elevenlabs_setup()
            print("\n" + "="*70)
            if result.get("success"):
                print("✅ ElevenLabs Setup Complete!")
                if result.get("api_key"):
                    print(f"   API Key: {result['api_key'][:30]}...")
                if result.get("vault_error"):
                    print(f"   ⚠️  Vault error: {result['vault_error']}")
                    print("\n   You can store manually with:")
                    print(f'   az keyvault secret set --vault-name jarvis-lumina --name elevenlabs-api-key --value "{result["api_key"]}"')
            else:
                print("❌ Setup Incomplete")
                print(f"   {result.get('error', 'Unknown error')}")
            print("="*70)
            print("\nPress Enter to close browser...")
            input()

        else:
            parser.print_help()

    finally:
        integration.close()


if __name__ == "__main__":



    main()