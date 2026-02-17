#!/usr/bin/env python3
"""
Count Incomplete Sessions
Counts all incomplete agent chat sessions across all locations
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CountIncompleteSessions")

def count_incomplete_sessions(project_root: Path) -> dict:
    """Count incomplete sessions in various locations"""
    stats = {
        "r5_sessions": {"total": 0, "incomplete": 0},
        "resumed_sessions": {"total": 0},
        "by_type": defaultdict(int),
        "by_date_range": {
            "last_24h": 0,
            "last_week": 0,
            "last_month": 0,
            "older": 0
        }
    }

    # Check R5 sessions directory
    sessions_dir = project_root / "data" / "r5_living_matrix" / "sessions"
    resumed_dir = project_root / "data" / "resumed_sessions"

    # Get list of already resumed sessions
    resumed_ids = set()
    if resumed_dir.exists():
        for resumed_file in resumed_dir.glob("resumed_*.json"):
            try:
                with open(resumed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_id = data.get("session_id") or resumed_file.stem
                    resumed_ids.add(session_id)
            except:
                pass
        stats["resumed_sessions"]["total"] = len(resumed_ids)

    # Scan R5 sessions
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.json"))
        stats["r5_sessions"]["total"] = len(session_files)

        now = datetime.now()

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                session_id = data.get("session_id", session_file.stem)

                # Skip if already resumed
                if session_id in resumed_ids:
                    continue

                messages = data.get("messages", [])

                # Check if incomplete (few messages)
                if len(messages) < 3:
                    stats["r5_sessions"]["incomplete"] += 1

                    # Determine type from filename
                    filename_lower = session_file.name.lower()
                    if "cursor" in filename_lower or "chat" in filename_lower:
                        session_type = "cursor_chat"
                    elif "ciao" in filename_lower:
                        session_type = "ciao"
                    elif "vscode" in filename_lower:
                        session_type = "vscode"
                    else:
                        session_type = "other"

                    stats["by_type"][session_type] += 1

                    # Get timestamp
                    try:
                        timestamp_str = data.get("timestamp", "")
                        if timestamp_str:
                            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        else:
                            timestamp = datetime.fromtimestamp(session_file.stat().st_mtime)

                        age = (now - timestamp.replace(tzinfo=None)).total_seconds()

                        if age < 86400:  # 24 hours
                            stats["by_date_range"]["last_24h"] += 1
                        elif age < 604800:  # 1 week
                            stats["by_date_range"]["last_week"] += 1
                        elif age < 2592000:  # 1 month
                            stats["by_date_range"]["last_month"] += 1
                        else:
                            stats["by_date_range"]["older"] += 1
                    except:
                        stats["by_date_range"]["older"] += 1

            except Exception as e:
                logger.debug(f"Error reading {session_file.name}: {e}")
                continue

    return stats

def main():
    try:
        project_root = Path(__file__).parent.parent.parent

        logger.info("=" * 60)
        logger.info("📊 COUNTING INCOMPLETE SESSIONS")
        logger.info("=" * 60)
        logger.info("")

        stats = count_incomplete_sessions(project_root)

        logger.info(f"Total R5 session files: {stats['r5_sessions']['total']}")
        logger.info(f"Incomplete sessions: {stats['r5_sessions']['incomplete']}")
        logger.info(f"Already resumed: {stats['resumed_sessions']['total']}")
        logger.info(f"Remaining incomplete: {stats['r5_sessions']['incomplete']}")
        logger.info("")
        logger.info("By type:")
        for session_type, count in sorted(stats['by_type'].items()):
            logger.info(f"  {session_type}: {count}")
        logger.info("")
        logger.info("By date range:")
        logger.info(f"  Last 24 hours: {stats['by_date_range']['last_24h']}")
        logger.info(f"  Last week: {stats['by_date_range']['last_week']}")
        logger.info(f"  Last month: {stats['by_date_range']['last_month']}")
        logger.info(f"  Older: {stats['by_date_range']['older']}")
        logger.info("")
        logger.info("=" * 60)

        # Output count for piping to wc
        print(f"\nTotal incomplete sessions: {stats['r5_sessions']['incomplete']}")
        print(f"Total session files: {stats['r5_sessions']['total']}")

        return stats['r5_sessions']['incomplete']

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(0)



    count = main()