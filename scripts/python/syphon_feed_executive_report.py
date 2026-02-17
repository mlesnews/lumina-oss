#!/usr/bin/env python3
"""
Feed Executive Report into @SYPHON
Processes executive portfolio reports for intelligence extraction

Tags: #SYPHON #EXECUTIVE #REPORT #INTELLIGENCE
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_syphon_chat_session import JARVISSyphonChatSession
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JARVISSyphonChatSession = None

logger = get_logger("SyphonFeedReport")


def feed_executive_report_to_syphon(report_path: Path, project_root: Path) -> Dict[str, Any]:
    try:
        """
        Feed executive portfolio report into @SYPHON for intelligence extraction

        Args:
            report_path: Path to executive report markdown file
            project_root: Project root directory

        Returns:
            Extracted intelligence from report
        """
        logger.info(f"🔍 Feeding executive report into @SYPHON: {report_path}")

        # Read report
        if not report_path.exists():
            logger.error(f"❌ Report not found: {report_path}")
            return {"error": "Report not found"}

        report_content = report_path.read_text(encoding='utf-8')

        # Create session data structure
        session_data = {
            "messages": [
                {
                    "role": "user",
                    "content": f"Executive Portfolio Report: {report_path.name}\n\n{report_content[:5000]}"  # First 5000 chars
                },
                {
                    "role": "assistant",
                    "content": "Report processed by @SYPHON intelligence extraction system."
                }
            ],
            "metadata": {
                "report_type": "executive_portfolio",
                "report_path": str(report_path),
                "report_size": len(report_content)
            }
        }

        # Extract intelligence using SYPHON
        if JARVISSyphonChatSession:
            syphon = JARVISSyphonChatSession(project_root)
            extracted = syphon.extract_chat_session(session_data)

            logger.info("✅ Executive report fed into @SYPHON")
            logger.info(f"   Topics extracted: {len(extracted.get('intelligence', {}).get('topics', []))}")
            logger.info(f"   Decisions extracted: {len(extracted.get('intelligence', {}).get('decisions', []))}")
            logger.info(f"   Actions extracted: {len(extracted.get('intelligence', {}).get('actions', []))}")

            return extracted
        else:
            # Fallback: Save directly to syphon
            syphon_path = project_root / "data" / "syphon"
            syphon_path.mkdir(parents=True, exist_ok=True)

            report_data = {
                "type": "executive_portfolio_report",
                "title": report_path.stem,
                "timestamp": datetime.now().isoformat(),
                "content": report_content,
                "topics": [
                    "360_bubble_orientation",
                    "micro_macro_relationship",
                    "bell_curve_ascendency",
                    "unknown_relationship",
                    "dimensional_expansion",
                    "submarine_analogy"
                ],
                "classification": "strategic_technical_analysis"
            }

            output_file = syphon_path / f"executive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding='utf-8')

            logger.info(f"✅ Executive report saved to @SYPHON: {output_file}")
            return report_data


    except Exception as e:
        logger.error(f"Error in feed_executive_report_to_syphon: {e}", exc_info=True)
        raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Feed Executive Report into @SYPHON")
        parser.add_argument("--report", type=str, help="Path to executive report markdown file")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        if args.report:
            report_path = Path(args.report)
            if not report_path.is_absolute():
                report_path = project_root / report_path
        else:
            # Default: Use the executive portfolio report we just created
            report_path = project_root / "docs" / "system" / "EXECUTIVE_PORTFOLIO_ORIENTATION_UNKNOWN.md"

        result = feed_executive_report_to_syphon(report_path, project_root)

        if args.json:
            print(json.dumps(result, indent=2, default=str, ensure_ascii=False))
        else:
            print("✅ Executive report fed into @SYPHON")
            if "intelligence" in result:
                intel = result["intelligence"]
                print(f"   Topics: {len(intel.get('topics', []))}")
                print(f"   Decisions: {len(intel.get('decisions', []))}")
                print(f"   Actions: {len(intel.get('actions', []))}")
            elif "topics" in result:
                print(f"   Topics: {len(result.get('topics', []))}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()