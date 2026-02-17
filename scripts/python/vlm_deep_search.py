#!/usr/bin/env python3
"""
VLM Deep Search for Kenny
"""
import sys
from pathlib import Path
from typing import Dict, Any
import logging
logger = logging.getLogger("vlm_deep_search")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from vlm_integration import VLMIntegration
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    try:
        screenshot_path = project_root / "data" / "manus_rdp_captures" / "kenny_visibility_check.png"
        if not screenshot_path.exists():
            print(f"❌ Screenshot not found: {screenshot_path}")
            return

        print("🤖 Running VLM Deep Search...")
        # Use OpenAI or local based on availability
        vlm = VLMIntegration(provider="local") # Fallback to local

        prompt = (
            "This is a critical mission. Locate a virtual assistant named Kenny. "
            "He is a small, circular, bright red character with a cyan glowing center. "
            "Is he anywhere on this screen? Look near the taskbar, corners, and window edges. "
            "If you see any small red objects, describe exactly where they are."
        )

        result = vlm.analyze_screen_with_vlm(screenshot_path, prompt=prompt)
        if result.get("available"):
            print("\n--- VLM OBSERVATION ---")
            print(result.get("analysis"))
            print("----------------------")
        else:
            print(f"❌ VLM analysis failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()