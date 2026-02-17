#!/usr/bin/env python3
"""
Grammarly AI-Driven CLI - Auto-Accept Corrections

AI-driven workflow that automatically accepts all Grammarly corrections
without manual GUI interaction. This is the workflow that needs to happen.

Tags: #GRAMMARLY #AI_DRIVEN #AUTO_ACCEPT #CLI #LUMINA_CORE
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GrammarlyAIDrivenCLI")


@dataclass
class GrammarlyCorrection:
    """A Grammarly correction"""
    original: str
    corrected: str
    type: str  # "grammar", "spelling", "style", etc.
    confidence: float
    suggestion: str
    position: int  # Character position


@dataclass
class GrammarlyResult:
    """Result of Grammarly check with auto-accept"""
    original_text: str
    corrected_text: str
    corrections: List[GrammarlyCorrection]
    auto_accepted: bool
    corrections_count: int


class GrammarlyAIDrivenCLI:
    """
    AI-Driven Grammarly CLI - Auto-Accepts All Corrections

    This is the workflow that needs to happen:
    1. Check text with Grammarly
    2. Get all corrections
    3. Auto-accept ALL corrections (no manual GUI clicking)
    4. Return corrected text
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI-driven Grammarly CLI"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Try to import Grammarly integration
        try:
            from grammarly_integration import GrammarlyIntegration
            self.grammarly = GrammarlyIntegration(project_root=self.project_root)
            logger.info("✅ Grammarly Integration available")
        except ImportError:
            self.grammarly = None
            logger.warning("⚠️  Grammarly Integration not available")

        # Try to import Grammarly CLI
        try:
            from grammarly_cli import GrammarlyCLI
            self.cli = GrammarlyCLI()
            logger.info("✅ Grammarly CLI available")
        except ImportError:
            self.cli = None
            logger.warning("⚠️  Grammarly CLI not available")

    def check_and_auto_accept(
        self,
        text: str,
        auto_accept_all: bool = True
    ) -> GrammarlyResult:
        """
        Check text with Grammarly and auto-accept all corrections

        This is the AI-driven workflow - no manual GUI interaction needed.

        Args:
            text: Text to check
            auto_accept_all: If True, automatically accept all corrections

        Returns:
            GrammarlyResult with corrected text
        """
        if not text or len(text.strip()) == 0:
            return GrammarlyResult(
                original_text=text,
                corrected_text=text,
                corrections=[],
                auto_accepted=False,
                corrections_count=0
            )

        logger.info("   🔍 Checking text with Grammarly (AI-driven, auto-accept)...")

        # Method 1: Use Grammarly CLI if available
        if self.cli:
            try:
                result = self.cli.check_text(text, show_details=True)

                corrections = []
                if result.get("corrections"):
                    for corr in result["corrections"]:
                        corrections.append(GrammarlyCorrection(
                            original=corr.get("original", ""),
                            corrected=corr.get("corrected", ""),
                            type=corr.get("type", "unknown"),
                            confidence=0.9,
                            suggestion=corr.get("corrected", ""),
                            position=corr.get("position", 0)
                        ))

                corrected_text = result.get("corrected", text)

                logger.info(f"   ✅ Found {len(corrections)} corrections - AUTO-ACCEPTED")

                return GrammarlyResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    corrections=corrections,
                    auto_accepted=True,
                    corrections_count=len(corrections)
                )
            except Exception as e:
                logger.warning(f"   ⚠️  Grammarly CLI failed: {e}")

        # Method 2: Use Grammarly Integration
        if self.grammarly:
            try:
                grammar_result = self.grammarly.check_grammar(text)

                corrections = []
                if grammar_result.corrections:
                    for corr in grammar_result.corrections:
                        corrections.append(GrammarlyCorrection(
                            original=corr.get("original", text),
                            corrected=corr.get("corrected", text),
                            type=corr.get("type", "grammar"),
                            confidence=grammar_result.confidence,
                            suggestion=corr.get("suggestions", [""])[0] if corr.get("suggestions") else "",
                            position=corr.get("start", 0)
                        ))

                corrected_text = grammar_result.corrected_text

                logger.info(f"   ✅ Found {len(corrections)} corrections - AUTO-ACCEPTED")

                return GrammarlyResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    corrections=corrections,
                    auto_accepted=True,
                    corrections_count=len(corrections)
                )
            except Exception as e:
                logger.warning(f"   ⚠️  Grammarly Integration failed: {e}")

        # Fallback: No corrections (text is fine or Grammarly not available)
        logger.warning("   ⚠️  Grammarly not available - returning original text")
        return GrammarlyResult(
            original_text=text,
            corrected_text=text,
            corrections=[],
            auto_accepted=False,
            corrections_count=0
        )

    def process_transcript(
        self,
        transcript: str,
        auto_accept: bool = True
    ) -> str:
        """
        Process a voice transcript through Grammarly with auto-accept

        This is the workflow: transcript → Grammarly → auto-accept → corrected

        Args:
            transcript: Voice transcript text
            auto_accept: Auto-accept all corrections

        Returns:
            Corrected transcript
        """
        logger.info("   🎤 Processing transcript through Grammarly (AI-driven)...")

        result = self.check_and_auto_accept(transcript, auto_accept)

        if result.corrections_count > 0:
            logger.info(f"   ✅ Auto-accepted {result.corrections_count} corrections")
            logger.info(f"   📝 Original: {result.original_text[:50]}...")
            logger.info(f"   ✅ Corrected: {result.corrected_text[:50]}...")
        else:
            logger.info("   ✅ No corrections needed")

        return result.corrected_text


# Global instance
_grammarly_ai_cli_instance = None


def get_grammarly_ai_cli() -> GrammarlyAIDrivenCLI:
    """Get or create global AI-driven Grammarly CLI"""
    global _grammarly_ai_cli_instance
    if _grammarly_ai_cli_instance is None:
        _grammarly_ai_cli_instance = GrammarlyAIDrivenCLI()
        logger.info("✅ Grammarly AI-Driven CLI initialized - AUTO-ACCEPT WORKFLOW ACTIVE")
    return _grammarly_ai_cli_instance


def check_and_auto_accept(text: str) -> str:
    """Check text and auto-accept all corrections (AI-driven)"""
    cli = get_grammarly_ai_cli()
    result = cli.check_and_auto_accept(text, auto_accept_all=True)
    return result.corrected_text


def process_transcript(transcript: str) -> str:
    """Process transcript through Grammarly with auto-accept"""
    cli = get_grammarly_ai_cli()
    return cli.process_transcript(transcript, auto_accept=True)


if __name__ == "__main__":
    # Test
    cli = get_grammarly_ai_cli()

    test_text = "This is a test sentance with erors."
    print(f"\n📝 Original: {test_text}")

    result = cli.check_and_auto_accept(test_text)
    print(f"✅ Corrected: {result.corrected_text}")
    print(f"🔧 Corrections: {result.corrections_count}")
    print(f"🤖 Auto-accepted: {result.auto_accepted}")
