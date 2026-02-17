#!/usr/bin/env python3
"""
Extract Unfinished @asks from Cursor Chat Sessions

Scans all ingested R5 sessions to find unfinished @ask requests that need completion.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("extract_unfinished_asks")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

# Directories to search
R5_SESSIONS_DIR = project_root / "scripts" / "data" / "r5_living_matrix" / "sessions"
CURSOR_HISTORY_DIR = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "History"
INGESTION_RESULT_FILE = project_root / "data" / "cursor_ingestion_result.json"



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class UnfinishedAskExtractor:
    """Extract unfinished @ask requests from chat sessions"""

    def __init__(self):
        self.unfinished_asks = []
        self.patterns = [
            r'@ask\s+(.+?)(?=\n|$)',
            r'@ASK\s+(.+?)(?=\n|$)',
            r'please\s+(.+?)(?=\?|$|\n)',
            r'can you\s+(.+?)(?=\?|$|\n)',
            r'could you\s+(.+?)(?=\?|$|\n)',
            r'need\s+to\s+(.+?)(?=\?|$|\n)',
            r'would you\s+(.+?)(?=\?|$|\n)',
            r'todo[:\s]+(.+?)(?=\n|$)',
            r'pending[:\s]+(.+?)(?=\n|$)',
            r'unfinished[:\s]+(.+?)(?=\n|$)',
        ]

    def extract_from_content(self, content: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """Extract unfinished @asks from content"""
        asks = []
        content_lower = content.lower()

        # Check for explicit @ask mentions
        for pattern in self.patterns[:2]:  # @ask patterns
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                ask_text = match.group(1).strip()
                if len(ask_text) > 10:  # Filter out very short matches
                    asks.append({
                        "type": "@ask",
                        "text": ask_text,
                        "full_match": match.group(0),
                        "source": source,
                        "extracted_at": datetime.now().isoformat()
                    })

        # Check for pending/unfinished keywords
        if any(keyword in content_lower for keyword in ['pending', 'unfinished', 'todo', 'need to', 'can you', 'could you']):
            # Look for context around these keywords
            for pattern in self.patterns[2:]:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    ask_text = match.group(1).strip()
                    if len(ask_text) > 10:
                        asks.append({
                            "type": "implicit_request",
                            "text": ask_text,
                            "full_match": match.group(0),
                            "source": source,
                            "extracted_at": datetime.now().isoformat()
                        })

        return asks

    def scan_r5_sessions(self) -> List[Dict[str, Any]]:
        """Scan R5 session files for unfinished @asks"""
        all_asks = []

        if not R5_SESSIONS_DIR.exists():
            print(f"⚠️  R5 sessions directory not found: {R5_SESSIONS_DIR}")
            return all_asks

        session_files = list(R5_SESSIONS_DIR.glob("*.json"))
        print(f"📊 Scanning {len(session_files)} R5 session files...")

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8', errors='ignore') as f:
                    session_data = json.load(f)

                # Extract from messages
                messages = session_data.get("messages", [])
                for msg in messages:
                    content = msg.get("content", "")
                    if content:
                        asks = self.extract_from_content(content, source=str(session_file.name))
                        for ask in asks:
                            ask["session_file"] = str(session_file.name)
                            ask["message_role"] = msg.get("role", "unknown")
                            all_asks.append(ask)

                # Extract from metadata
                metadata = session_data.get("metadata", {})
                metadata_str = json.dumps(metadata)
                if metadata_str:
                    asks = self.extract_from_content(metadata_str, source=str(session_file.name))
                    for ask in asks:
                        ask["session_file"] = str(session_file.name)
                        ask["source_type"] = "metadata"
                        all_asks.append(ask)

            except Exception as e:
                print(f"⚠️  Error processing {session_file.name}: {e}")
                continue

        return all_asks

    def scan_cursor_history(self) -> List[Dict[str, Any]]:
        """Scan Cursor history directories for unfinished @asks"""
        all_asks = []

        if not CURSOR_HISTORY_DIR.exists():
            print(f"⚠️  Cursor history directory not found: {CURSOR_HISTORY_DIR}")
            return all_asks

        print(f"📊 Scanning Cursor history directories...")
        history_dirs = [d for d in CURSOR_HISTORY_DIR.iterdir() if d.is_dir()]
        print(f"   Found {len(history_dirs)} history directories")

        # Limit scanning to avoid excessive processing
        for history_dir in history_dirs[:100]:  # Scan first 100 directories
            json_files = list(history_dir.glob("*.json"))
            for json_file in json_files[:10]:  # Max 10 files per directory
                try:
                    with open(json_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Try to parse as JSON
                    try:
                        data = json.loads(content)
                        content = json.dumps(data)
                    except:
                        pass  # Use raw content

                    asks = self.extract_from_content(content, source=str(json_file.name))
                    for ask in asks:
                        ask["history_dir"] = str(history_dir.name)
                        ask["file_path"] = str(json_file)
                        all_asks.append(ask)

                except Exception as e:
                    continue  # Skip files that can't be read

        return all_asks

    def generate_report(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary report of unfinished @asks"""
        report = {
            "total_asks": len(asks),
            "by_type": {},
            "by_source": {},
            "extraction_date": datetime.now().isoformat(),
            "asks": asks
        }

        # Count by type
        for ask in asks:
            ask_type = ask.get("type", "unknown")
            report["by_type"][ask_type] = report["by_type"].get(ask_type, 0) + 1

        # Count by source
        for ask in asks:
            source = ask.get("source", "unknown")
            report["by_source"][source] = report["by_source"].get(source, 0) + 1

        return report


def main():
    try:
        """Main entry point"""
        print("🔍 Extracting Unfinished @asks from Chat Sessions")
        print("=" * 60)

        extractor = UnfinishedAskExtractor()

        # Scan R5 sessions
        print("\n📂 Scanning R5 Living Context Matrix sessions...")
        r5_asks = extractor.scan_r5_sessions()
        print(f"   Found {len(r5_asks)} potential @asks in R5 sessions")

        # Scan Cursor history (limited to avoid excessive processing)
        print("\n📂 Scanning Cursor history directories (limited scan)...")
        cursor_asks = extractor.scan_cursor_history()
        print(f"   Found {len(cursor_asks)} potential @asks in Cursor history")

        # Combine results
        all_asks = r5_asks + cursor_asks
        print(f"\n✅ Total unfinished @asks found: {len(all_asks)}")

        # Generate report
        report = extractor.generate_report(all_asks)

        # Save report
        output_file = project_root / "data" / "unfinished_asks_report.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report saved to: {output_file}")

        # Print summary
        print("\n📊 Summary:")
        print(f"   Total @asks: {report['total_asks']}")
        print(f"   By type: {report['by_type']}")
        print(f"\n   Top sources:")
        sorted_sources = sorted(report['by_source'].items(), key=lambda x: x[1], reverse=True)[:10]
        for source, count in sorted_sources:
            print(f"     - {source}: {count}")

        return report


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(0 if report['total_asks'] > 0 else 1)



    report = main()