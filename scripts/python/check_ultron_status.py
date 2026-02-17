#!/usr/bin/env python3
"""
Quick ULTRON Status Check

Checks if ULTRON is properly configured as local-only.

Tags: #CHECK #ULTRON #LOCAL
@JARVIS
"""

import json
from pathlib import Path
import logging
logger = logging.getLogger("check_ultron_status")


def check_ultron_status():
    try:
        """Quick status check"""
        settings_file = Path(".cursor/settings.json")

        if not settings_file.exists():
            print("❌ Settings file not found")
            return

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        print("=" * 60)
        print("ULTRON Configuration Status")
        print("=" * 60)
        print()

        sections = [
            "cursor.agent.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.inlineCompletion.customModels"
        ]

        all_good = True

        for section_key in sections:
            models = settings.get(section_key, [])
            ultron = next((m for m in models if m.get("name") == "ULTRON"), None)

            if ultron:
                local_only = ultron.get("localOnly", False)
                provider = ultron.get("provider", "")
                skip_provider = ultron.get("skipProviderSelection", False)
                api_base = ultron.get("apiBase", "")

                status = "✅" if (local_only and provider == "ollama" and skip_provider) else "❌"

                print(f"{section_key}:")
                print(f"  {status} localOnly: {local_only}")
                print(f"  {status} provider: {provider}")
                print(f"  {status} skipProviderSelection: {skip_provider}")
                print(f"  {status} apiBase: {api_base}")
                print()

                if not (local_only and provider == "ollama" and skip_provider):
                    all_good = False

        default_model = settings.get("cursor.agent.defaultModel", "")
        print(f"Default Agent Model: {default_model}")
        print()

        if all_good:
            print("✅ ULTRON is correctly configured as LOCAL ONLY")
            print("⚠️  If errors persist, restart Cursor")
        else:
            print("❌ ULTRON configuration needs fixing")
            print("   Run: python scripts/python/fix_ultron_local_only.py")

    except Exception as e:
        logger.error(f"Error in check_ultron_status: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    check_ultron_status()
