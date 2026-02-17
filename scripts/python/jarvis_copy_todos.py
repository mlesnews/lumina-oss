#!/usr/bin/env python3
"""
JARVIS Copy To-Dos to Clipboard
Generates the dual Master/Padawan to-do report and copies it to the system clipboard.

Tags: #TODO #CLIPBOARD #UTILITY @AUTO @JARVIS  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import pyperclip
from pathlib import Path
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from generate_chat_todo_report import generate_chat_todo_report
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    # Inline fallback if import fails
    def generate_chat_todo_report():
        return "Error: Could not import report generator."

logger = get_logger("JARVISCopyTodos")

def main():
    """Generate and copy to-do report"""
    try:
        report = generate_chat_todo_report()

        if report and "Error" not in report:
            pyperclip.copy(report)
            logger.info("✅ LUMINA To-Do Lists copied to clipboard.")
            print(f"\n--- REPORT PREVIEW ---\n{report[:200]}...\n--- END PREVIEW ---\n")
            return True
        else:
            logger.error(f"❌ Failed to generate report: {report}")
            return False

    except Exception as e:
        logger.error(f"❌ Clipboard copy error: {e}", exc_info=True)
        return False

if __name__ == "__main__":


    main()