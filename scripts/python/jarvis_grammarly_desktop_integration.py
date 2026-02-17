#!/usr/bin/env python3
"""
JARVIS Grammarly Desktop Integration

Full integration of Grammarly Desktop CLI API with JARVIS system.
Provides seamless grammar checking for JARVIS outputs and user inputs.

Tags: #JARVIS #GRAMMARLY_DESKTOP #INTEGRATION #GRAMMAR_CHECKING @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from grammarly_desktop_cli_api import (
        GrammarlyDesktopCLI,
        JARVISGrammarlyIntegration
    )
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("JARVISGrammarlyDesktop")


class JARVISGrammarlyDesktopBridge:
    """
    Bridge between JARVIS and Grammarly Desktop

    Provides:
    - Auto-checking of JARVIS outputs
    - User input grammar checking
    - Seamless integration with JARVIS workflows
    - Integration with DOIT and SYPHON systems
    """

    def __init__(self):
        """Initialize JARVIS-Grammarly Desktop bridge"""
        self.integration = JARVISGrammarlyIntegration()
        self.auto_check_enabled = True
        self.auto_improve_jarvis = True  # Auto-improve JARVIS outputs

        logger.info("=" * 80)
        logger.info("🤖 JARVIS-GRAMMARLY DESKTOP BRIDGE")
        logger.info("=" * 80)
        logger.info("   Integration ready")
        logger.info(f"   Auto-check: {self.auto_check_enabled}")
        logger.info(f"   Auto-improve JARVIS: {self.auto_improve_jarvis}")
        logger.info("=" * 80)

    def check_jarvis_output(self, text: str, auto_apply: bool = False) -> Dict[str, Any]:
        """
        Check JARVIS output text with Grammarly Desktop

        Args:
            text: Text to check
            auto_apply: If True, automatically apply corrections if score is high

        Returns:
            Dict with original, corrected, score, suggestions
        """
        logger.info("🔍 Checking JARVIS output via Grammarly Desktop...")

        result = self.integration.check_text(text)

        # Auto-apply if enabled and score is good
        if auto_apply and result["score"] > 0.9 and result["suggestions"]:
            corrected = result["corrected"]
            logger.info(f"✅ Auto-applied corrections (score: {result['score']:.0%})")
            return {
                **result,
                "auto_applied": True,
                "final_text": corrected
            }

        return {
            **result,
            "auto_applied": False,
            "final_text": result["corrected"]
        }

    def check_user_input(self, text: str) -> Dict[str, Any]:
        """Check user input before processing"""
        logger.info("🔍 Checking user input via Grammarly Desktop...")

        result = self.integration.check_text(text)

        # If significant issues found, suggest corrections
        if result["score"] < 0.8:
            logger.warning(f"⚠️  User input has grammar issues (score: {result['score']:.0%})")
            logger.info(f"   Suggestions: {result['suggestions_count']}")

        return result

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        status = self.integration.grammarly_cli.get_status()

        return {
            **status,
            "jarvis_integration": True,
            "auto_check_enabled": self.auto_check_enabled,
            "auto_improve_jarvis": self.auto_improve_jarvis,
            "integration_ready": True
        }

    def improve_jarvis_response(self, response: str) -> str:
        """
        Improve JARVIS response using Grammarly Desktop

        This can be called automatically after JARVIS generates responses.
        """
        if not self.auto_improve_jarvis:
            return response

        try:
            result = self.check_jarvis_output(response, auto_apply=True)
            if result.get("auto_applied"):
                return result["final_text"]
        except Exception as e:
            logger.warning(f"⚠️  Failed to improve JARVIS response: {e}")

        return response

    def check_before_sending(self, text: str, source: str = "user") -> Dict[str, Any]:
        """
        Check text before sending (for user inputs or JARVIS outputs)

        Args:
            text: Text to check
            source: "user" or "jarvis"

        Returns:
            Dict with check results and improved text
        """
        if source == "user":
            result = self.check_user_input(text)
        else:
            result = self.check_jarvis_output(text)

        return {
            **result,
            "source": source,
            "recommended_text": result["final_text"] if result["score"] < 0.9 else text
        }

    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Convenience method to check any text

        Uses the integration's check_text method.
        """
        return self.integration.check_text(text)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Grammarly Desktop Integration")
        parser.add_argument("--text", "-t", help="Text to check")
        parser.add_argument("--check-jarvis-output", action="store_true", help="Check as JARVIS output")
        parser.add_argument("--check-user-input", action="store_true", help="Check as user input")
        parser.add_argument("--status", action="store_true", help="Show integration status")
        parser.add_argument("--auto-apply", action="store_true", help="Auto-apply corrections")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        bridge = JARVISGrammarlyDesktopBridge()

        if args.status:
            status = bridge.get_integration_status()
            if args.json:
                import json
                print(json.dumps(status, indent=2))
            else:
                print("=" * 80)
                print("📊 JARVIS-GRAMMARLY DESKTOP INTEGRATION STATUS")
                print("=" * 80)
                for key, value in status.items():
                    print(f"  {key}: {value}")
                print("=" * 80)

        elif args.text:
            if args.check_jarvis_output:
                result = bridge.check_jarvis_output(args.text, args.auto_apply)
            elif args.check_user_input:
                result = bridge.check_user_input(args.text)
            else:
                result = bridge.integration.check_text(args.text)

            if args.json:
                import json
                print(json.dumps(result, indent=2))
            else:
                print("=" * 80)
                print("📝 GRAMMARLY CHECK RESULTS")
                print("=" * 80)
                print(f"Score: {result['score']:.0%}")
                print(f"Suggestions: {result['suggestions_count']}")
                if result.get('suggestions'):
                    print("\nSuggestions:")
                    for s in result['suggestions'][:5]:
                        print(f"  • {s['original']} → {s['corrected']} ({s['type']})")
                print("=" * 80)

        else:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())