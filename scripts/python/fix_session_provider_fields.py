#!/usr/bin/env python3
"""
Fix Agent Chat Session Provider Fields

Fixes all agent chat session files by adding missing model and provider fields.
This prevents Cursor from defaulting to Bedrock for Ollama models (ULTRON, KAIJU).

Tags: #FIX #BEDROCK #SESSIONS #PROVIDER #ULTRON
@JARVIS @MARVIN
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixSessionProviderFields")

# Model to provider mapping
MODEL_PROVIDER_MAP = {
    "ULTRON": "ollama",
    "KAIJU": "ollama",
    "qwen2.5:72b": "ollama",
    "llama3": "ollama",
    "llama3.1": "ollama",
    "llama3.2": "ollama"
}

DEFAULT_MODEL = "ULTRON"
DEFAULT_PROVIDER = "ollama"


class SessionProviderFixer:
    """Fix agent chat session files by adding model and provider fields"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fixer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.agent_sessions_dir = self.project_root / "data" / "agent_chat_sessions"

        logger.info("✅ Session Provider Fixer initialized")

    def fix_session_file(self, session_file: Path, dry_run: bool = False) -> Dict[str, Any]:
        """Fix a single session file"""
        result = {
            "file": session_file.name,
            "fixed": False,
            "changes": [],
            "error": None
        }

        try:
            # Read session file
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            original_data = json.dumps(session_data, sort_keys=True)

            # Check if model is missing
            if "model" not in session_data or not session_data.get("model"):
                session_data["model"] = DEFAULT_MODEL
                result["changes"].append(f"Added model: {DEFAULT_MODEL}")

            model = session_data["model"]

            # Check if provider is missing or incorrect
            if "provider" not in session_data or not session_data.get("provider"):
                # Determine provider based on model
                if model in MODEL_PROVIDER_MAP:
                    provider = MODEL_PROVIDER_MAP[model]
                else:
                    provider = DEFAULT_PROVIDER

                session_data["provider"] = provider
                result["changes"].append(f"Added provider: {provider} for model {model}")
            else:
                # Check if provider is correct for the model
                if model in MODEL_PROVIDER_MAP:
                    expected_provider = MODEL_PROVIDER_MAP[model]
                    if session_data.get("provider") != expected_provider:
                        session_data["provider"] = expected_provider
                        result["changes"].append(f"Fixed provider: {expected_provider} for model {model}")

            # Update metadata with model config
            if "metadata" not in session_data:
                session_data["metadata"] = {}

            if "model_config" not in session_data["metadata"]:
                session_data["metadata"]["model_config"] = {
                    "model": session_data["model"],
                    "provider": session_data.get("provider", DEFAULT_PROVIDER),
                    "configured_at": datetime.now().isoformat(),
                    "note": "Provider set to prevent Bedrock routing for Ollama models"
                }
            else:
                # Update existing model_config
                session_data["metadata"]["model_config"]["model"] = session_data["model"]
                session_data["metadata"]["model_config"]["provider"] = session_data.get("provider", DEFAULT_PROVIDER)
                session_data["metadata"]["model_config"]["updated_at"] = datetime.now().isoformat()

            # Check if changes were made
            new_data = json.dumps(session_data, sort_keys=True)
            if original_data != new_data:
                result["fixed"] = True

                if not dry_run:
                    # Write fixed session file
                    with open(session_file, 'w', encoding='utf-8') as f:
                        json.dump(session_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"   ✅ Fixed: {session_file.name}")
                else:
                    logger.info(f"   [DRY RUN] Would fix: {session_file.name}")
            else:
                logger.debug(f"   ✓ No changes needed: {session_file.name}")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"   ❌ Error fixing {session_file.name}: {e}")

        return result

    def fix_all_sessions(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Fix all agent chat session files"""
            logger.info("=" * 80)
            logger.info("🔧 FIXING AGENT CHAT SESSION PROVIDER FIELDS")
            logger.info("=" * 80)
            logger.info("")

            if dry_run:
                logger.info("⚠️  DRY RUN MODE - No files will be modified")
                logger.info("")

            if not self.agent_sessions_dir.exists():
                logger.error(f"❌ Agent sessions directory does not exist: {self.agent_sessions_dir}")
                return {
                    "success": False,
                    "error": "Agent sessions directory does not exist",
                    "fixed": 0,
                    "total": 0
                }

            # Find all session files
            session_files = sorted(self.agent_sessions_dir.glob("*.json"))
            logger.info(f"📋 Found {len(session_files)} session files")
            logger.info("")

            results = []
            fixed_count = 0
            error_count = 0

            for session_file in session_files:
                result = self.fix_session_file(session_file, dry_run=dry_run)
                results.append(result)

                if result["fixed"]:
                    fixed_count += 1
                    if result["changes"]:
                        for change in result["changes"]:
                            logger.info(f"      {change}")

                if result["error"]:
                    error_count += 1

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ FIX COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Total sessions: {len(session_files)}")
            logger.info(f"   Fixed: {fixed_count}")
            logger.info(f"   Errors: {error_count}")
            logger.info("")

            # Save report
            report = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "total_sessions": len(session_files),
                "fixed": fixed_count,
                "errors": error_count,
                "results": results
            }

            output_dir = self.project_root / "data" / "diagnostics"
            output_dir.mkdir(parents=True, exist_ok=True)
            report_file = output_dir / f"session_provider_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Report saved: {report_file.name}")
            logger.info("")

            return report


        except Exception as e:
            self.logger.error(f"Error in fix_all_sessions: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix Agent Chat Session Provider Fields")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't modify files)")

        args = parser.parse_args()

        print("\n" + "=" * 80)
        print("🔧 FIX AGENT CHAT SESSION PROVIDER FIELDS")
        print("=" * 80 + "\n")

        project_root = Path(args.project_root) if args.project_root else None

        fixer = SessionProviderFixer(project_root=project_root)
        result = fixer.fix_all_sessions(dry_run=args.dry_run)

        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total sessions: {result.get('total_sessions', 0)}")
        print(f"Fixed: {result.get('fixed', 0)}")
        print(f"Errors: {result.get('errors', 0)}")
        print()

        if args.dry_run:
            print("⚠️  This was a DRY RUN - no files were modified")
            print("   Run without --dry-run to apply fixes")
            print()

        print("=" * 80)
        print("✅ Complete")
        print("=" * 80 + "\n")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()