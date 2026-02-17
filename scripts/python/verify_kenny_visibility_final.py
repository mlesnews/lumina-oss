#!/usr/bin/env python3
"""
Verify Kenny Visibility - Final Version
Uses MDV to capture screen and VLM to analyze if Kenny is visible.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_auto_mdv_activator import JARVISAutoMDVActivator
    from vlm_integration import VLMIntegration
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VerifyKennyVisibility")

def main():
    try:
        logger.info("📹 Verifying Kenny visibility via MDV...")

        # 1. Initialize MDV Activator
        activator = JARVISAutoMDVActivator(project_root=project_root)

        # 2. Capture current view
        logger.info("📸 Capturing desktop view...")
        screenshot_path = activator.capture_current_view()

        if not screenshot_path or not screenshot_path.exists():
            logger.error("❌ Failed to capture screenshot")
            return

        logger.info(f"✅ Screenshot captured: {screenshot_path}")

        # 3. Analyze with VLM
        logger.info("🤖 Analyzing screenshot with VLM...")
        vlm = VLMIntegration(provider="local") # Use local model first

        prompt = (
            "Look for a small, circular, red character on the desktop. "
            "It should be 'Hot Rod Red' with a gold glow and a hexagonal helmet. "
            "This is Kenny, the virtual assistant. "
            "Is Kenny visible on the screen? If so, where is he located? "
            "Also, look for any window frames that might have popped up and closed."
        )

        analysis = vlm.analyze_screen_with_vlm(screenshot_path, prompt=prompt)

        if analysis.get("available"):
            logger.info("📊 VLM Analysis Result:")
            print("-" * 40)
            print(analysis.get("analysis"))
            print("-" * 40)
        else:
            logger.warning(f"⚠️ VLM analysis not available: {analysis.get('error')}")
            # Fallback to just reporting the path so I can read it
            print(f"SCREENSHOT_PATH: {screenshot_path}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()