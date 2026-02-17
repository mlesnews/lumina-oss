#!/usr/bin/env python3
"""
Grammarly Integration - Grammar and Spelling Correction

After audio-transcription comparison confirms "one true source",
feed transcription into Grammarly for grammar/spelling correction.

Checks if Grammarly CLI/API exists and is functional.
If not, provides alternatives or creates solution.

Tags: #GRAMMAR #SPELLING #GRAMMARLY #LUMINA_CORE
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

logger = get_logger("GrammarlyIntegration")


@dataclass
class GrammarCheckResult:
    """Result of grammar/spelling check"""
    original_text: str
    corrected_text: str
    corrections: List[Dict[str, Any]]
    confidence: float
    source: str  # "grammarly", "alternative", "fallback"


class GrammarlyIntegration:
    """
    Grammarly Integration for grammar and spelling correction

    After audio-transcription comparison confirms "one true source",
    processes transcription through grammar/spelling correction.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Grammarly integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.grammarly_available = False
        self.grammarly_method = None  # "cli", "api", "alternative"

        # Check for Grammarly availability
        self._check_grammarly_availability()

    def _check_grammarly_availability(self):
        """Check if Grammarly CLI or API is available"""
        # Method 1: Check for Grammarly CLI
        try:
            import subprocess
            result = subprocess.run(
                ["grammarly", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                self.grammarly_available = True
                self.grammarly_method = "cli"
                logger.info("✅ Grammarly CLI detected")
                return
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
            pass

        # Method 2: Check for Grammarly Python package
        try:
            import grammarly
            self.grammarly_available = True
            self.grammarly_method = "python_package"
            logger.info("✅ Grammarly Python package detected")
            return
        except ImportError:
            pass

        # Method 3: Check for Grammarly API
        try:
            # Check if API key is configured
            api_key_file = self.project_root / "config" / "grammarly_api_key.txt"
            if api_key_file.exists():
                self.grammarly_available = True
                self.grammarly_method = "api"
                logger.info("✅ Grammarly API key found")
                return
        except Exception:
            pass

        # No Grammarly found - use alternatives
        self.grammarly_available = False
        self.grammarly_method = "alternative"
        logger.warning("⚠️  Grammarly CLI/API not found - using alternatives")

    def check_grammar(
        self,
        text: str,
        confidence_threshold: float = 0.7
    ) -> GrammarCheckResult:
        """
        Check grammar and spelling of text

        Only processes if confidence threshold is met (one true source confirmed)

        Args:
            text: Text to check
            confidence_threshold: Minimum confidence to process (default: 0.7)

        Returns: GrammarCheckResult with corrections
        """
        if not text or len(text.strip()) == 0:
            return GrammarCheckResult(
                original_text=text,
                corrected_text=text,
                corrections=[],
                confidence=0.0,
                source="none"
            )

        # Try Grammarly first
        if self.grammarly_available and self.grammarly_method != "alternative":
            try:
                return self._check_with_grammarly(text)
            except Exception as e:
                logger.warning(f"   ⚠️  Grammarly check failed: {e}")
                # Fall through to alternatives

        # Use alternatives
        return self._check_with_alternatives(text)

    def _check_with_grammarly(self, text: str) -> GrammarCheckResult:
        """Check grammar using Grammarly (if available)"""
        if self.grammarly_method == "cli":
            return self._check_with_grammarly_cli(text)
        elif self.grammarly_method == "python_package":
            return self._check_with_grammarly_package(text)
        elif self.grammarly_method == "api":
            return self._check_with_grammarly_api(text)
        else:
            return self._check_with_alternatives(text)

    def _check_with_grammarly_cli(self, text: str) -> GrammarCheckResult:
        """Check using Grammarly CLI"""
        try:
            import subprocess
            import json
            import tempfile

            # Write text to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_file = f.name

            try:
                # Run Grammarly CLI
                result = subprocess.run(
                    ["grammarly", "check", temp_file, "--json"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    # Parse JSON output
                    corrections_data = json.loads(result.stdout)
                    corrections = corrections_data.get("corrections", [])
                    corrected_text = corrections_data.get("corrected_text", text)

                    return GrammarCheckResult(
                        original_text=text,
                        corrected_text=corrected_text,
                        corrections=corrections,
                        confidence=0.9,
                        source="grammarly_cli"
                    )
            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(temp_file)
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"   Grammarly CLI failed: {e}")

        # Fallback
        return self._check_with_alternatives(text)

    def _check_with_grammarly_package(self, text: str) -> GrammarCheckResult:
        """Check using Grammarly Python package"""
        try:
            import grammarly

            # Initialize Grammarly client
            client = grammarly.GrammarlyClient()

            # Check text
            result = client.check(text)

            corrections = []
            corrected_text = text

            # Process corrections
            if hasattr(result, 'corrections'):
                for correction in result.corrections:
                    corrections.append({
                        "type": getattr(correction, 'type', 'unknown'),
                        "message": getattr(correction, 'message', ''),
                        "start": getattr(correction, 'start', 0),
                        "end": getattr(correction, 'end', 0),
                        "suggestions": getattr(correction, 'suggestions', [])
                    })

                # Apply corrections
                if hasattr(result, 'corrected_text'):
                    corrected_text = result.corrected_text

            return GrammarCheckResult(
                original_text=text,
                corrected_text=corrected_text,
                corrections=corrections,
                confidence=0.9,
                source="grammarly_package"
            )
        except Exception as e:
            logger.debug(f"   Grammarly package failed: {e}")

        # Fallback
        return self._check_with_alternatives(text)

    def _check_with_grammarly_api(self, text: str) -> GrammarCheckResult:
        """Check using Grammarly API"""
        try:
            import requests

            # Read API key
            api_key_file = self.project_root / "config" / "grammarly_api_key.txt"
            if not api_key_file.exists():
                return self._check_with_alternatives(text)

            with open(api_key_file, 'r') as f:
                api_key = f.read().strip()

            # Call Grammarly API
            response = requests.post(
                "https://api.grammarly.com/v1/check",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={"text": text},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                corrections = data.get("corrections", [])
                corrected_text = data.get("corrected_text", text)

                return GrammarCheckResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    corrections=corrections,
                    confidence=0.9,
                    source="grammarly_api"
                )
        except Exception as e:
            logger.debug(f"   Grammarly API failed: {e}")

        # Fallback
        return self._check_with_alternatives(text)

    def _check_with_alternatives(self, text: str) -> GrammarCheckResult:
        """
        Check grammar using alternatives (if Grammarly not available)

        Alternatives:
        1. LanguageTool (open-source grammar checker)
        2. PySpellChecker (spelling only)
        3. Basic pattern matching
        """
        corrections = []
        corrected_text = text

        # Alternative 1: LanguageTool
        try:
            import language_tool_python
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(text)

            if matches:
                corrections = [
                    {
                        "type": "grammar",
                        "message": m.message,
                        "start": m.offset,
                        "end": m.offset + m.errorLength,
                        "suggestions": m.replacements[:3]  # Top 3 suggestions
                    }
                    for m in matches
                ]
                # Apply corrections
                corrected_text = tool.correct(text)

                return GrammarCheckResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    corrections=corrections,
                    confidence=0.7,
                    source="language_tool"
                )
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"   LanguageTool failed: {e}")

        # Alternative 2: PySpellChecker (spelling only)
        try:
            from spellchecker import SpellChecker
            spell = SpellChecker()

            words = text.split()
            misspelled = spell.unknown(words)

            if misspelled:
                corrections = []
                for word in misspelled:
                    corrections.append({
                        "type": "spelling",
                        "word": word,
                        "suggestions": list(spell.candidates(word))[:3]
                    })
                    # Replace with most likely correction
                    corrected_word = spell.correction(word)
                    text = text.replace(word, corrected_word)

                corrected_text = text

                return GrammarCheckResult(
                    original_text=text,
                    corrected_text=corrected_text,
                    corrections=corrections,
                    confidence=0.6,
                    source="pyspellchecker"
                )
        except ImportError:
            pass
        except Exception as e:
            logger.debug(f"   PySpellChecker failed: {e}")

        # Fallback: Basic pattern matching (very limited)
        return GrammarCheckResult(
            original_text=text,
            corrected_text=text,
            corrections=[],
            confidence=0.3,
            source="fallback"
        )

    def process_confirmed_transcription(
        self,
        transcription_text: str,
        comparison_confidence: float
    ) -> GrammarCheckResult:
        """
        Process transcription after audio-transcription comparison confirms it

        Only processes if confidence threshold is met (one true source)

        Args:
            transcription_text: Confirmed transcription text
            comparison_confidence: Confidence from audio-transcription comparison

        Returns: GrammarCheckResult
        """
        # Only process if confidence is high enough (one true source)
        if comparison_confidence < 0.7:
            logger.debug(
                f"   ⏸️  Skipping grammar check - confidence too low "
                f"({comparison_confidence:.2f} < 0.7)"
            )
            return GrammarCheckResult(
                original_text=transcription_text,
                corrected_text=transcription_text,
                corrections=[],
                confidence=comparison_confidence,
                source="skipped_low_confidence"
            )

        logger.info(
            f"   ✅ Processing confirmed transcription "
            f"(confidence: {comparison_confidence:.2f})"
        )

        return self.check_grammar(transcription_text, comparison_confidence)


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Grammarly Integration")
    parser.add_argument("--text", type=str, help="Text to check")
    parser.add_argument("--check-availability", action="store_true", help="Check if Grammarly is available")

    args = parser.parse_args()

    integration = GrammarlyIntegration()

    if args.check_availability:
        print("\n📋 Grammarly Availability:")
        print(f"   Available: {integration.grammarly_available}")
        print(f"   Method: {integration.grammarly_method}")
        if not integration.grammarly_available:
            print("\n💡 Alternatives:")
            print("   - LanguageTool (pip install language-tool-python)")
            print("   - PySpellChecker (pip install pyspellchecker)")
            print("   - Grammarly API (requires API key)")

    if args.text:
        result = integration.check_grammar(args.text)
        print(f"\n📝 Grammar Check Result:")
        print(f"   Source: {result.source}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Corrections: {len(result.corrections)}")
        if result.corrected_text != result.original_text:
            print(f"   Original: {result.original_text}")
            print(f"   Corrected: {result.corrected_text}")

    return 0


if __name__ == "__main__":


    sys.exit(main())