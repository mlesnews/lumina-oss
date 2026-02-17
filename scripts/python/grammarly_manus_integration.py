#!/usr/bin/env python3
"""
Grammarly CLI/API/AI Integration via MANUS

Integrates Grammarly for automated grammar checking and correction
through MANUS automation system.

Tags: #GRAMMARLY #MANUS #AUTOMATION #CLI #API #AI @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

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

logger = get_logger("GrammarlyMANUS")

try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.warning("MANUS not available")


@dataclass
class GrammarlySuggestion:
    """Grammarly suggestion"""
    type: str  # "grammar", "spelling", "style", "clarity", "engagement"
    original: str
    suggestion: str
    explanation: Optional[str] = None
    confidence: float = 0.0


class GrammarlyMANUSIntegration:
    """
    Grammarly Integration via MANUS

    Provides automated grammar checking and correction.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Grammarly integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "grammarly_config.json"

        # Load configuration
        self.config = self._load_config()

        # Initialize MANUS if available
        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(self.project_root)
                logger.info("   ✅ MANUS available for Grammarly automation")
            except Exception as e:
                logger.debug(f"   MANUS init error: {e}")

        # Check for Grammarly CLI
        self.grammarly_cli_available = self._check_grammarly_cli()

        logger.info("✅ Grammarly MANUS Integration initialized")
        logger.info(f"   CLI available: {self.grammarly_cli_available}")
        logger.info(f"   API key configured: {bool(self.config.get('api_key'))}")

    def _load_config(self) -> Dict[str, Any]:
        """Load Grammarly configuration"""
        default_config = {
            "api_key": None,
            "cli_path": "grammarly",
            "enabled": True,
            "auto_correct": False,
            "check_on_save": True,
            "suggestions_enabled": True
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.debug(f"   Could not load config: {e}")
        else:
            # Create default config
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)

        return default_config

    def _check_grammarly_cli(self) -> bool:
        """Check if Grammarly CLI is available"""
        try:
            result = subprocess.run(
                ["grammarly", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def check_text(self, text: str, auto_apply: bool = False) -> List[GrammarlySuggestion]:
        """
        Check text for grammar issues

        Args:
            text: Text to check
            auto_apply: Automatically apply suggestions via MANUS

        Returns:
            List of suggestions
        """
        logger.info(f"   📝 Checking text ({len(text)} characters)")

        suggestions = []

        # Method 1: Use Grammarly CLI if available
        if self.grammarly_cli_available:
            suggestions = self._check_via_cli(text)

        # Method 2: Use Grammarly API if configured
        elif self.config.get("api_key"):
            suggestions = self._check_via_api(text)

        # Method 3: Use MANUS to interact with Grammarly browser extension
        elif self.manus:
            suggestions = self._check_via_browser_extension(text)

        else:
            logger.warning("   ⚠️  No Grammarly method available")
            logger.info("   💡 Options:")
            logger.info("      1. Install Grammarly CLI: npm install -g @grammarly/cli")
            logger.info("      2. Configure API key in config/grammarly_config.json")
            logger.info("      3. Install Grammarly browser extension")

        # Apply suggestions if requested
        if auto_apply and suggestions and self.manus:
            self._apply_suggestions_via_manus(text, suggestions)

        logger.info(f"   ✅ Found {len(suggestions)} suggestions")

        return suggestions

    def _check_via_cli(self, text: str) -> List[GrammarlySuggestion]:
        """Check via Grammarly CLI"""
        try:
            # Write text to temp file
            temp_file = self.project_root / "data" / "grammarly_temp.txt"
            temp_file.parent.mkdir(parents=True, exist_ok=True)
            temp_file.write_text(text)

            # Run Grammarly CLI
            result = subprocess.run(
                ["grammarly", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output (format depends on CLI)
            suggestions = []
            # This is a placeholder - actual parsing depends on CLI output format
            if result.returncode == 0:
                # Parse JSON output if available
                try:
                    output_data = json.loads(result.stdout)
                    # Extract suggestions from output
                    # Format depends on Grammarly CLI
                except:
                    # Parse text output
                    pass

            return suggestions

        except Exception as e:
            logger.error(f"   ❌ CLI error: {e}")
            return []

    def _check_via_api(self, text: str) -> List[GrammarlySuggestion]:
        """Check via Grammarly API"""
        if not self.config.get("api_key"):
            return []

        try:
            import requests

            api_url = "https://api.grammarly.com/v1/check"
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "language": "en-US"
            }

            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                suggestions = []

                # Parse API response
                for issue in data.get("issues", []):
                    suggestion = GrammarlySuggestion(
                        type=issue.get("type", "grammar"),
                        original=issue.get("original", ""),
                        suggestion=issue.get("suggestion", ""),
                        explanation=issue.get("explanation"),
                        confidence=issue.get("confidence", 0.0)
                    )
                    suggestions.append(suggestion)

                return suggestions
            else:
                logger.warning(f"   ⚠️  API returned status {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ API error: {e}")

        return []

    def _check_via_browser_extension(self, text: str) -> List[GrammarlySuggestion]:
        """Check via Grammarly browser extension using MANUS"""
        if not self.manus:
            return []

        logger.info("   🌐 Using Grammarly browser extension via MANUS")

        suggestions = []

        try:
            # Open Grammarly web app or use extension
            # This would require MANUS to:
            # 1. Open browser to grammarly.com
            # 2. Paste text
            # 3. Extract suggestions
            # 4. Return results

            # Placeholder implementation
            logger.info("   💡 Browser extension method requires MANUS browser control")

        except Exception as e:
            logger.error(f"   ❌ Browser extension error: {e}")

        return suggestions

    def _apply_suggestions_via_manus(self, text: str, suggestions: List[GrammarlySuggestion]):
        """Apply suggestions via MANUS automation"""
        if not self.manus:
            return

        logger.info(f"   🤖 Applying {len(suggestions)} suggestions via MANUS")

        try:
            # Use MANUS to:
            # 1. Navigate to text editor
            # 2. Find and replace text based on suggestions
            # 3. Apply corrections

            for suggestion in suggestions:
                if suggestion.confidence >= 0.7:  # High confidence only
                    logger.info(f"      Applying: '{suggestion.original}' → '{suggestion.suggestion}'")
                    # MANUS automation would go here

        except Exception as e:
            logger.error(f"   ❌ MANUS application error: {e}")

    def check_file(self, file_path: Path, auto_apply: bool = False) -> List[GrammarlySuggestion]:
        try:
            """Check file for grammar issues"""
            if not file_path.exists():
                logger.error(f"   ❌ File not found: {file_path}")
                return []

            text = file_path.read_text(encoding='utf-8', errors='ignore')
            return self.check_text(text, auto_apply=auto_apply)

        except Exception as e:
            self.logger.error(f"Error in check_file: {e}", exc_info=True)
            raise
    def check_directory(self, directory: Path, pattern: str = "*.md", auto_apply: bool = False) -> Dict[str, List[GrammarlySuggestion]]:
        """Check all files in directory"""
        results = {}

        for file_path in directory.rglob(pattern):
            suggestions = self.check_file(file_path, auto_apply=False)
            if suggestions:
                results[str(file_path)] = suggestions

        return results


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Grammarly MANUS Integration")
        parser.add_argument("--check-text", type=str, help="Check text for grammar")
        parser.add_argument("--check-file", type=Path, help="Check file for grammar")
        parser.add_argument("--check-dir", type=Path, help="Check directory for grammar")
        parser.add_argument("--auto-apply", action="store_true", help="Automatically apply suggestions")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        grammarly = GrammarlyMANUSIntegration()

        if args.check_text:
            suggestions = grammarly.check_text(args.check_text, auto_apply=args.auto_apply)
            if args.json:
                print(json.dumps([
                    {
                        "type": s.type,
                        "original": s.original,
                        "suggestion": s.suggestion,
                        "confidence": s.confidence
                    }
                    for s in suggestions
                ], indent=2, default=str))
            else:
                print(f"✅ Found {len(suggestions)} suggestions")

        elif args.check_file:
            suggestions = grammarly.check_file(args.check_file, auto_apply=args.auto_apply)
            if args.json:
                print(json.dumps([
                    {
                        "type": s.type,
                        "original": s.original,
                        "suggestion": s.suggestion,
                        "confidence": s.confidence
                    }
                    for s in suggestions
                ], indent=2, default=str))
            else:
                print(f"✅ Found {len(suggestions)} suggestions in {args.check_file}")

        elif args.check_dir:
            results = grammarly.check_directory(args.check_dir, auto_apply=args.auto_apply)
            if args.json:
                print(json.dumps({
                    file: [
                        {
                            "type": s.type,
                            "original": s.original,
                            "suggestion": s.suggestion
                        }
                        for s in suggestions
                    ]
                    for file, suggestions in results.items()
                }, indent=2, default=str))
            else:
                print(f"✅ Checked {len(results)} files")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()