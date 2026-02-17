#!/usr/bin/env python3
"""
MANUS-NEO ElevenLabs Setup Helper

Simple helper that:
1. Launches NEO browser to ElevenLabs signup
2. Provides step-by-step instructions
3. Monitors clipboard for API key
4. Stores key in Azure Key Vault automatically
"""

import os
import sys
import subprocess
import time
import re
from pathlib import Path
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MANUS-NEO-ElevenLabs")


def find_neo_browser() -> Optional[Path]:
    """Find NEO browser executable"""
    import winreg

    neo_paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "Application" / "neo.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "Neo" / "neo.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Neo" / "neo.exe",
        Path.home() / "AppData" / "Local" / "Neo" / "Application" / "neo.exe",
    ]

    # Check registry
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\neo.exe") as key:
            path = winreg.QueryValue(key, None)
            neo_paths.insert(0, Path(path))
    except:
        pass

    for path in neo_paths:
        if path.exists():
            logger.info(f"✅ Found NEO browser: {path}")
            return path

    # Try to find in common locations
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Neo") as key:
            path = winreg.QueryValue(key, "Path")
            if path and Path(path).exists():
                logger.info(f"✅ Found NEO browser (registry): {path}")
                return Path(path)
    except:
        pass

    logger.warning("⚠️  NEO browser not found in standard locations")
    return None


def launch_neo_to_url(url: str) -> bool:
    """Launch NEO browser to specific URL"""
    neo_exe = find_neo_browser()

    if not neo_exe:
        logger.error("❌ NEO browser not found")
        print("\n🔍 NEO Browser Not Found")
        print("="*70)
        print("Please install NEO browser or provide the path manually.")
        print("\nOr, manually open NEO browser and navigate to:")
        print(f"   {url}")
        return False

    try:
        logger.info(f"🌐 Launching NEO browser: {url}")
        subprocess.Popen([str(neo_exe), url], shell=False)
        time.sleep(2)
        logger.info("✅ NEO browser launched")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to launch NEO: {e}")
        return False


def monitor_clipboard_for_api_key(timeout: int = 300) -> Optional[str]:
    """
    Monitor clipboard for API key pattern

    Args:
        timeout: Maximum seconds to wait

    Returns:
        API key if found, None otherwise
    """
    try:
        import win32clipboard
    except ImportError:
        logger.warning("⚠️  pywin32 not installed - clipboard monitoring disabled")
        logger.info("   Install with: pip install pywin32")
        return None

    logger.info(f"📋 Monitoring clipboard for API key (timeout: {timeout}s)...")
    logger.info("   Copy your ElevenLabs API key to clipboard when ready")

    start_time = time.time()
    last_clipboard = ""

    while time.time() - start_time < timeout:
        try:
            win32clipboard.OpenClipboard()
            try:
                clipboard_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                # Check if clipboard changed
                if clipboard_data != last_clipboard:
                    last_clipboard = clipboard_data

                    # Look for API key patterns
                    # ElevenLabs keys are typically long alphanumeric strings
                    patterns = [
                        r'sk[-_][a-zA-Z0-9]{20,}',  # sk_ prefix
                        r'[a-f0-9]{32,}',  # Hex string (32+ chars)
                        r'[A-Za-z0-9_-]{30,}',  # Long alphanumeric
                    ]

                    for pattern in patterns:
                        matches = re.findall(pattern, clipboard_data)
                        if matches:
                            # Return longest match (most likely the key)
                            api_key = max(matches, key=len)
                            if len(api_key) >= 30:  # Reasonable minimum
                                logger.info(f"✅ API key detected in clipboard: {api_key[:20]}...")
                                return api_key

                time.sleep(1)  # Check every second
            except Exception:
                win32clipboard.CloseClipboard()
                time.sleep(1)
        except Exception as e:
            logger.debug(f"Clipboard check error: {e}")
            time.sleep(1)

    logger.warning("⏱️  Timeout reached - no API key detected in clipboard")
    return None


def store_api_key_in_vault(api_key: str) -> bool:
    """Store ElevenLabs API key in Azure Key Vault"""
    try:
        logger.info("🔐 Storing API key in Azure Key Vault...")
        result = subprocess.run([
            "az", "keyvault", "secret", "set",
            "--vault-name", "jarvis-lumina",
            "--name", "elevenlabs-api-key",
            "--value", api_key
        ], capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            logger.info("✅ API key stored in Azure Key Vault!")
            logger.info("   Secret name: elevenlabs-api-key")
            return True
        else:
            logger.error(f"❌ Failed to store key: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error storing key: {e}")
        return False


def print_instructions():
    """Print step-by-step instructions"""
    print("\n" + "="*70)
    print("🎙️  ElevenLabs API Key Setup Instructions")
    print("="*70)
    print()
    print("STEP 1: Sign Up (if you haven't already)")
    print("   → Click 'Sign Up' button")
    print("   → Use your email and create a password")
    print("   → Verify your email if required")
    print()
    print("STEP 2: Get Your API Key")
    print("   → After login, click your profile icon (top right)")
    print("   → Go to 'Profile' or 'Settings'")
    print("   → Find 'API Key' section")
    print("   → Click 'Show' or 'Copy' button")
    print("   → OR navigate directly to: https://elevenlabs.io/app/settings/api-keys")
    print()
    print("STEP 3: Copy API Key")
    print("   → Select and copy the API key (Ctrl+C)")
    print("   → This script will detect it automatically!")
    print()
    print("="*70)
    print()


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS-NEO ElevenLabs Setup Helper")
        parser.add_argument("--url", type=str, default="https://elevenlabs.io",
                           help="URL to open (default: ElevenLabs homepage)")
        parser.add_argument("--monitor-clipboard", action="store_true",
                           help="Monitor clipboard for API key")
        parser.add_argument("--key", type=str,
                           help="API key to store directly (skip clipboard monitoring)")

        args = parser.parse_args()

        # If key provided directly, just store it
        if args.key:
            if store_api_key_in_vault(args.key):
                print("\n✅ Success! ElevenLabs API key stored in Azure Key Vault")
                print("   You can now use it with the Hybrid TTS System")
                return
            else:
                print("\n❌ Failed to store API key")
                return

        # Launch NEO browser
        print_instructions()

        if launch_neo_to_url(args.url):
            print("✅ NEO browser launched!")
            print()
        else:
            print("⚠️  Could not launch NEO automatically")
            print(f"   Please manually open NEO and go to: {args.url}")
            print()

        # Monitor clipboard if requested
        if args.monitor_clipboard:
            api_key = monitor_clipboard_for_api_key(timeout=300)
            if api_key:
                if store_api_key_in_vault(api_key):
                    print("\n" + "="*70)
                    print("✅ SUCCESS!")
                    print("="*70)
                    print("ElevenLabs API key stored in Azure Key Vault")
                    print("You can now use it with: python scripts/python/hybrid_tts_system.py")
                    print("="*70)
                    return
                else:
                    print("\n❌ Failed to store API key")
            else:
                print("\n⏱️  No API key detected in clipboard")
                print("\nYou can manually store it with:")
                print('   az keyvault secret set --vault-name jarvis-lumina --name elevenlabs-api-key --value "YOUR_KEY_HERE"')
        else:
            print("\n💡 Tip: Run with --monitor-clipboard to automatically detect")
            print("   when you copy your API key!")
            print("\nOr store manually:")
            print('   az keyvault secret set --vault-name jarvis-lumina --name elevenlabs-api-key --value "YOUR_KEY_HERE"')


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()