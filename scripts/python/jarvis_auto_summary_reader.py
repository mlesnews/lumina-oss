#!/usr/bin/env python3
"""
JARVIS Auto Summary Reader

Automatically reads summaries to user when available.
Integrates with JARVIS systems to read summaries intelligently.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_summary_reader import JARVISSummaryReader
    SUMMARY_READER_AVAILABLE = True
except ImportError:
    SUMMARY_READER_AVAILABLE = False
    JARVISSummaryReader = None

logger = get_logger("JARVISAutoSummaryReader")


class JARVISAutoSummaryReader:
    """
    Automatically reads summaries to user

    Monitors for summaries and reads them intelligently
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if SUMMARY_READER_AVAILABLE:
            self.reader = JARVISSummaryReader(project_root)
        else:
            self.reader = None
            self.logger.warning("Summary reader not available")

    def read_summary(self, text: str, max_tokens: int = 500) -> Dict[str, Any]:
        """Read a summary"""
        if not self.reader:
            return {
                'success': False,
                'error': 'Summary reader not available'
            }

        return self.reader.read_summary(text, max_tokens=max_tokens, skip_code=True)

    def read_file_summary(self, file_path: Path, max_tokens: int = 500) -> Dict[str, Any]:
        """Read summary from file"""
        if not self.reader:
            return {
                'success': False,
                'error': 'Summary reader not available'
            }

        return self.reader.read_file_summary(file_path, max_tokens)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Auto Summary Reader")
        parser.add_argument("--text", type=str, help="Text to read")
        parser.add_argument("--file", type=str, help="File to read")
        parser.add_argument("--max-tokens", type=int, default=500, help="Max tokens")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        auto_reader = JARVISAutoSummaryReader(project_root)

        if args.file:
            result = auto_reader.read_file_summary(Path(args.file), args.max_tokens)
        elif args.text:
            result = auto_reader.read_summary(args.text, args.max_tokens)
        else:
            print("Usage:")
            print("  --text 'text'     : Read text")
            print("  --file path       : Read file")
            print("  --max-tokens 500  : Max tokens")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()