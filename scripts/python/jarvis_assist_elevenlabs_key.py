#!/usr/bin/env python3
"""
JARVIS Assisted ElevenLabs Key Retrieval
Guides user through process and stores key when ready

Tags: #JARVIS #ELEVENLABS #ASSISTED @JARVIS @DOIT
"""

import sys
from pathlib import Path
from typing import Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAssistElevenLabsKey")


def assist_key_retrieval() -> Optional[str]:
    """
    Assist user in retrieving and storing ElevenLabs API key
    """
    logger.info("=" * 80)
    logger.info("🤖 JARVIS ELEVENLABS KEY ASSISTANT")
    logger.info("=" * 80)
    logger.info("")

    logger.info("📋 Step-by-Step Guide:")
    logger.info("")
    logger.info("1️⃣  Open your browser and go to:")
    logger.info("   https://elevenlabs.io/app/settings/api-keys")
    logger.info("")
    logger.info("2️⃣  Click 'Create Key' or 'Add API Key' button")
    logger.info("")
    logger.info("3️⃣  Name it: 'Cursor - Cursor API Key'")
    logger.info("")
    logger.info("4️⃣  Click 'Create' or 'Generate'")
    logger.info("")
    logger.info("5️⃣  COPY THE KEY IMMEDIATELY (it only shows once!)")
    logger.info("")
    logger.info("6️⃣  Once copied, I'll store it in Azure Key Vault")
    logger.info("")
    logger.info("=" * 80)
    logger.info("⏳ Waiting for you to copy the key to clipboard...")
    logger.info("=" * 80)
    logger.info("")
    logger.info("💡 After you copy the key, run:")
    logger.info("   python scripts/python/jarvis_store_elevenlabs_key.py --clipboard --all-variations")
    logger.info("")
    logger.info("   OR just tell me 'ready' and I'll check clipboard and store it!")
    logger.info("")

    return None


def check_and_store_from_clipboard() -> bool:
    """Check clipboard and store if valid key found"""
    try:
        import pyperclip
        clipboard_content = pyperclip.paste().strip()

        # Validate it looks like an API key
        if not clipboard_content or len(clipboard_content) < 20:
            logger.warning("⚠️  Clipboard doesn't contain a valid API key")
            return False

        if "error" in clipboard_content.lower() or "bedrock" in clipboard_content.lower():
            logger.warning("⚠️  Clipboard contains error message, not API key")
            return False

        logger.info("✅ Valid API key detected in clipboard!")
        logger.info(f"   Key preview: {clipboard_content[:10]}...{clipboard_content[-4:]}")
        logger.info("")
        logger.info("🔐 Storing in Azure Key Vault...")

        # Import and use storage function
        from jarvis_store_elevenlabs_key import store_all_variations
        results = store_all_variations(clipboard_content)

        success_count = sum(1 for success in results.values() if success)

        if success_count > 0:
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ API KEY STORED SUCCESSFULLY!")
            logger.info("=" * 80)
            logger.info(f"   Stored under {success_count} name variations")
            logger.info("   JARVIS can now use TTS!")
            return True
        else:
            logger.error("❌ Failed to store key")
            return False

    except ImportError:
        logger.error("❌ pyperclip not available. Install: pip install pyperclip")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Assisted ElevenLabs Key Retrieval")
    parser.add_argument("--check-clipboard", action="store_true", help="Check clipboard and store if valid key found")

    args = parser.parse_args()

    if args.check_clipboard:
        success = check_and_store_from_clipboard()
        return 0 if success else 1
    else:
        assist_key_retrieval()
        return 0


if __name__ == "__main__":


    sys.exit(main())