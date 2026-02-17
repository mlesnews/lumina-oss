#!/usr/bin/env python3
"""
Find @ask by Request ID in recent chat histories

Searches through recent chat histories (last 3 days) to find the original @ask
that generated a specific Request ID.

Tags: #BAU #RETRY #@ASK #REQUEST_ID @JARVIS @LUMINA
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

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

logger = get_logger("FindAskByRequestID")


def search_chat_histories_for_request_id(
    request_id: str,
    project_root: Path,
    days_back: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Search recent chat histories for Request ID

    Args:
        request_id: The Request ID to search for
        project_root: Project root directory
        days_back: Number of days to search back

    Returns:
        Found entry with @ask text if found, None otherwise
    """
    logger.info(f"🔍 Searching chat histories for Request ID: {request_id}")
    logger.info(f"   Searching last {days_back} days")

    cutoff_date = datetime.now() - timedelta(days=days_back)
    data_dir = project_root / "data"

    # Search directories
    search_dirs = [
        data_dir / "agent_chat_sessions",
        data_dir / "agent_sessions",
        data_dir / "syphon" / "chat_sessions",
        data_dir / "syphon" / "current_chat_sessions",
        data_dir / "resumed_sessions",
        data_dir / "ask_tracking",
    ]

    found_entries = []

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        logger.info(f"   Searching: {search_dir}")

        # Search JSON files
        for json_file in search_dir.glob("*.json"):
            try:
                # Check file modification time
                file_time = datetime.fromtimestamp(json_file.stat().st_mtime)
                if file_time < cutoff_date:
                    continue

                # Read and search file
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Check if Request ID is in file
                    if request_id in content:
                        logger.info(f"   ✅ Found in: {json_file.name}")

                        # Try to parse as JSON
                        try:
                            data = json.loads(content)
                            found_entries.append({
                                "file": str(json_file),
                                "file_time": file_time.isoformat(),
                                "data": data
                            })
                        except json.JSONDecodeError:
                            # Not JSON, but contains Request ID - search for context
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if request_id in line:
                                    # Get context around the line
                                    context_start = max(0, i - 10)
                                    context_end = min(len(lines), i + 10)
                                    context = '\n'.join(lines[context_start:context_end])

                                    found_entries.append({
                                        "file": str(json_file),
                                        "file_time": file_time.isoformat(),
                                        "context": context,
                                        "line_number": i + 1
                                    })
                                    break
                        break  # Found it, no need to continue
            except Exception as e:
                logger.debug(f"   Error reading {json_file}: {e}")
                continue

    if not found_entries:
        logger.warning(f"   ⚠️  No entries found for Request ID: {request_id}")
        return None

    # Get most recent entry
    latest_entry = max(found_entries, key=lambda x: x["file_time"])

    logger.info(f"   ✅ Found {len(found_entries)} entry(ies)")
    logger.info(f"   Most recent: {latest_entry['file']}")

    return latest_entry


def extract_ask_from_entry(entry: Dict[str, Any]) -> Optional[str]:
    """
    Extract @ask text from entry

    Args:
        entry: Entry dictionary

    Returns:
        @ask text if found, None otherwise
    """
    data = entry.get("data")
    context = entry.get("context", "")

    # Try to find @ask in structured data
    if data:
        # Check various possible structures
        if isinstance(data, dict):
            # Check for messages array
            messages = data.get("messages", [])
            if not messages and "content" in data:
                messages = [data]

            for msg in messages:
                if isinstance(msg, dict):
                    content = msg.get("content", "") or msg.get("text", "") or msg.get("message", "")
                    if content and ("@ask" in content.lower() or "@ask" in str(msg).lower()):
                        return content

            # Check for ask_text field
            if "ask_text" in data:
                return data["ask_text"]

            # Check for user_message or user_input
            for key in ["user_message", "user_input", "user_query", "query", "input"]:
                if key in data:
                    value = data[key]
                    if isinstance(value, str) and ("@ask" in value.lower() or len(value) > 10):
                        return value

    # Try to find @ask in context text
    if context:
        lines = context.split('\n')
        for i, line in enumerate(lines):
            if "@ask" in line.lower():
                # Get the ask text (might span multiple lines)
                ask_lines = [line]
                # Look ahead for continuation
                for j in range(i + 1, min(i + 5, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('{') and not next_line.startswith('"'):
                        ask_lines.append(next_line)
                    else:
                        break
                return '\n'.join(ask_lines).strip()

    return None


def find_ask_by_request_id(request_id: str, days_back: int = 3) -> Optional[Dict[str, Any]]:
    """
    Find @ask by Request ID

    Args:
        request_id: The Request ID to search for
        days_back: Number of days to search back

    Returns:
        Dictionary with @ask text and metadata if found
    """
    project_root = Path(__file__).parent.parent.parent

    entry = search_chat_histories_for_request_id(request_id, project_root, days_back)

    if not entry:
        return None

    ask_text = extract_ask_from_entry(entry)

    result = {
        "request_id": request_id,
        "found": True,
        "file": entry["file"],
        "file_time": entry["file_time"],
        "ask_text": ask_text,
        "raw_entry": entry
    }

    if ask_text:
        logger.info(f"   ✅ Extracted @ask text: {ask_text[:100]}...")
    else:
        logger.warning(f"   ⚠️  Could not extract @ask text from entry")
        logger.info(f"   Raw entry available for manual inspection")

    return result


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Find @ask by Request ID in recent chat histories"
        )
        parser.add_argument(
            "request_id",
            help="Request ID to search for"
        )
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Number of days to search back (default: 3)"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        result = find_ask_by_request_id(args.request_id, args.days)

        if args.json:
            if result:
                print(json.dumps(result, indent=2, default=str))
            else:
                print(json.dumps({"found": False, "request_id": args.request_id}, indent=2))
        else:
            if result:
                print(f"\n✅ Found @ask for Request ID: {args.request_id}")
                print("=" * 60)
                print(f"File: {result['file']}")
                print(f"Time: {result['file_time']}")
                if result.get('ask_text'):
                    print(f"\n@ask Text:")
                    print(f"  {result['ask_text']}")
                else:
                    print(f"\n⚠️  Could not extract @ask text")
                    print(f"   Raw entry available in result")
            else:
                print(f"\n❌ No @ask found for Request ID: {args.request_id}")
                print(f"   Searched last {args.days} days")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()