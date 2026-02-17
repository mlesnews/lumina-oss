#!/usr/bin/env python3
"""
JARVIS Export IDE Problems
Exports IDE problems to JSON file for processing by monitor and auto-fix systems.

This script helps bridge the gap between IDE Problems panel and automated systems.

Usage:
    python jarvis_export_ide_problems.py --export-template  # Show export template
    python jarvis_export_ide_problems.py --read-lints       # Use read_lints tool (if available)

Tags: #JARVIS #IDE #PROBLEMS #EXPORT @helpdesk @r2d2
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISExportIDEProblems")

PROJECT_ROOT = script_dir.parent.parent
EXPORTED_PROBLEMS_FILE = PROJECT_ROOT / "data" / "ide_problems" / "exported_problems.json"
EXPORT_TEMPLATE_FILE = PROJECT_ROOT / "data" / "ide_problems" / "problems_export_template.json"


def show_export_template():
    try:
        """Show template for manual export from IDE Problems panel."""
        logger.info("="*80)
        logger.info("📋 IDE PROBLEMS EXPORT TEMPLATE")
        logger.info("="*80)
        logger.info("")
        logger.info("To export problems from Cursor IDE:")
        logger.info("")
        logger.info("1. Open Problems panel (Ctrl+Shift+M)")
        logger.info("2. Right-click in Problems panel")
        logger.info("3. Select 'Export' or 'Copy All'")
        logger.info("4. Save as JSON using the template below")
        logger.info("")
        logger.info("Template format:")
        logger.info("")

        template = [
            {
                "file": "relative/path/to/file.py",
                "line": 42,
                "column": 10,
                "severity": "error|warning|info|hint",
                "message": "Problem description",
                "source": "pylint|mypy|flake8|typescript|etc",
                "code": "optional-error-code"
            }
        ]

        print(json.dumps(template, indent=2))
        logger.info("")
        logger.info("Save exported problems to:")
        logger.info(f"  {EXPORTED_PROBLEMS_FILE}")
        logger.info("")
        logger.info("Then run:")
        logger.info("  python scripts/python/jarvis_proactive_ide_problem_monitor.py --check")
        logger.info("")


    except Exception as e:
        logger.error(f"Error in show_export_template: {e}", exc_info=True)
        raise
def save_exported_problems(problems: List[Dict[str, Any]]):
    """Save exported problems to file."""
    try:
        EXPORTED_PROBLEMS_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": datetime.now().isoformat(),
            "total": len(problems),
            "problems": problems
        }

        with open(EXPORTED_PROBLEMS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Exported {len(problems)} problems to {EXPORTED_PROBLEMS_FILE}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save exported problems: {e}")
        return False


def process_read_lints_output(lints_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process read_lints tool output into standard format."""
    problems = []

    for lint in lints_data:
        problem = {
            "file": lint.get("file", lint.get("path", "unknown")),
            "line": lint.get("line", lint.get("lineNumber", 0)),
            "column": lint.get("column", lint.get("columnNumber", 0)),
            "severity": lint.get("severity", lint.get("level", "warning")),
            "message": lint.get("message", lint.get("text", "")),
            "source": lint.get("source", lint.get("provider", "unknown")),
            "code": lint.get("code", lint.get("errorCode"))
        }
        problems.append(problem)

    return problems


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Export IDE Problems")
    parser.add_argument('--export-template', action='store_true',
                       help='Show export template for manual export')
    parser.add_argument('--read-lints', action='store_true',
                       help='Note: read_lints tool must be called externally via AI assistant')
    parser.add_argument('--save', type=str,
                       help='Save problems from JSON file (path to JSON file)')

    args = parser.parse_args()

    if args.export_template:
        show_export_template()

    elif args.save:
        try:
            with open(args.save, encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                problems = data
            elif isinstance(data, dict) and 'problems' in data:
                problems = data['problems']
            else:
                logger.error("Invalid JSON format")
                return

            save_exported_problems(problems)
        except Exception as e:
            logger.error(f"Failed to save: {e}")

    elif args.read_lints:
        logger.info("="*80)
        logger.info("⚠️  READ_LINTS TOOL INTEGRATION")
        logger.info("="*80)
        logger.info("")
        logger.info("The read_lints tool is available via the AI assistant interface.")
        logger.info("To use it:")
        logger.info("")
        logger.info("1. Ask AI assistant to read linter errors")
        logger.info("2. AI will call read_lints tool")
        logger.info("3. Results will be saved to exported_problems.json")
        logger.info("")
        logger.info("Or manually export from IDE Problems panel and use --save option")
        logger.info("")

    else:
        show_export_template()


if __name__ == "__main__":


    main()