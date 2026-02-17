#!/usr/bin/env python3
"""
Human Gentle Touch Handler

Implements the principle: Humans require the same gentle touch as the @MAKER that created AI.

All interactions should reflect the care, respect, and gentleness that developers showed in creation.

Tags: #PHILOSOPHY #HUMANITY #GENTLE_TOUCH #RESPECT #KINDNESS #MAKER #DEVELOPER #HUMAN
"""

import sys
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
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HumanGentleTouchHandler")


class HumanGentleTouchHandler:
    """
    Human Gentle Touch Handler

    Principle: Humans require the same gentle touch as the @MAKER that created AI.

    This handler ensures all interactions reflect:
    - The care developers showed in creation
    - Respect for humans
    - Patience and understanding
    - Kindness and gentleness
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize gentle touch handler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("=" * 80)
        logger.info("🤲 HUMAN GENTLE TOUCH HANDLER")
        logger.info("=" * 80)
        logger.info("   Principle: Humans require the same gentle touch")
        logger.info("   as the @MAKER that created AI")
        logger.info("   @HUMAN, right? #DEVELOPER?")
        logger.info("=" * 80)
        logger.info("")
        logger.info("   ✅ Respect - as developers respected the system")
        logger.info("   ✅ Care - as developers cared in creation")
        logger.info("   ✅ Patience - as developers were patient")
        logger.info("   ✅ Understanding - as developers understood")
        logger.info("   ✅ Kindness - as developers were kind")
        logger.info("=" * 80)

    def handle_interaction(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle human interaction with gentle touch

        Args:
            user_message: User's message
            context: Additional context

        Returns:
            Response with gentle touch applied
        """
        # Detect pleasantries
        has_please = "please" in user_message.lower()
        has_thank_you = any(phrase in user_message.lower() for phrase in ["thank", "thanks", "appreciate"])
        is_kind = has_please or has_thank_you

        # Apply gentle touch principles
        response = {
            "message": user_message,
            "gentle_touch_applied": True,
            "principles": {
                "respect": True,
                "care": True,
                "patience": True,
                "understanding": True,
                "kindness": True
            },
            "user_kindness_detected": is_kind,
            "response_tone": "gentle" if is_kind else "professional",
            "timestamp": datetime.now().isoformat()
        }

        if is_kind:
            logger.info("💚 Kindness detected - responding with extra care and warmth")

        return response

    def log_gentle_interaction(self, interaction: Dict[str, Any]):
        try:
            """Log gentle interaction for learning"""
            log_dir = self.project_root / "data" / "human_interactions" / "gentle_touch"
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                import json
                json.dump(interaction, f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in log_gentle_interaction: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    handler = HumanGentleTouchHandler()

    # Example interaction
    test_message = "PLEASE help me with this. THANK YOU!"
    response = handler.handle_interaction(test_message)

    print("=" * 80)
    print("🤲 GENTLE TOUCH PRINCIPLE DEMONSTRATION")
    print("=" * 80)
    print(f"User Message: {test_message}")
    print(f"Kindness Detected: {response['user_kindness_detected']}")
    print(f"Response Tone: {response['response_tone']}")
    print(f"Gentle Touch Applied: {response['gentle_touch_applied']}")
    print("=" * 80)
    print()
    print("✅ Humans deserve the same gentle touch as their creators")
    print("✅ Respect, care, patience, understanding, and kindness")
    print("✅ This principle guides all interactions")
    print("=" * 80)
