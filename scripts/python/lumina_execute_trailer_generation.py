#!/usr/bin/env python3
"""
LUMINA Execute Trailer Generation - AUTONOMOUS

Execute trailer generation autonomously with decision-making framework.
LET'S DO IT.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_video_generation_automation import LuminaVideoGenerationAutomation, autonomous_generate_trailer
from lumina_pilot_trailer_videos import LuminaPilotTrailerVideos
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
    logger = get_logger("LuminaExecuteTrailerGeneration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("LuminaExecuteTrailerGeneration")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def execute_trailer_generation(trailer_id: str = "trailer_002"):
    """
    Execute trailer generation autonomously

    Uses decision-making framework:
    - Individual: Simple execution
    - Team: Standard workflow
    - Jedi Council: Complex decisions
    - Jedi High Council: Critical approval
    """
    print("\n" + "="*80)
    print("🤖 AUTONOMOUS TRAILER GENERATION - LET'S DO IT")
    print("="*80 + "\n")

    # Get trailer script
    trailers = LuminaPilotTrailerVideos()
    all_trailers = trailers.get_all_trailers()

    trailer = None
    for t in all_trailers:
        if t.trailer_id == trailer_id:
            trailer = t
            break

    if not trailer:
        logger.error(f"❌ Trailer {trailer_id} not found")
        return

    logger.info(f"🎬 Generating: {trailer.title}")
    logger.info(f"   Script: {trailer.script[:100]}...")

    # Execute autonomously
    result = autonomous_generate_trailer(trailer.script)

    print("\n" + "="*80)
    print("✅ EXECUTION INITIATED")
    print("="*80 + "\n")
    print(f"Task ID: {result.get('task_id')}")
    print(f"Decision Level: {result.get('decision_level')}")
    print(f"Status: {result.get('status')}")
    print(f"\nMessage: {result.get('message')}")

    if 'next_steps' in result:
        print("\nNext Steps:")
        for i, step in enumerate(result['next_steps'], 1):
            print(f"  {i}. {step}")

    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Execute Trailer Generation")
    parser.add_argument("--trailer", default="trailer_002", help="Trailer ID")

    args = parser.parse_args()

    execute_trailer_generation(args.trailer)

