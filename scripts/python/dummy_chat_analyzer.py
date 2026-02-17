#!/usr/bin/env python3
"""
The Dummy: Chat Session Analyzer
Scans chat sessions for similar requests and prepares them for consolidation

@JARVIS @MARVIN @DUMMY @CHAT_ANALYZER @BAU
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from dummy_consolidator import DummyConsolidator, ChatRequest
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("DummyChatAnalyzer")


class ChatSessionAnalyzer:
    """Analyzes chat sessions to extract requests for consolidation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.chat_dir = project_root / "data" / "agent_chat_history"
        self.chat_dir.mkdir(parents=True, exist_ok=True)

    def scan_chat_sessions(self, session_ids: Optional[List[str]] = None) -> List[ChatRequest]:
        """
        Scan chat sessions for requests

        Args:
            session_ids: Optional list of specific session IDs to scan

        Returns:
            List of extracted chat requests
        """
        requests = []

        # Scan chat directory
        if not self.chat_dir.exists():
            logger.warning(f"Chat directory does not exist: {self.chat_dir}")
            return requests

        # Get session files
        if session_ids:
            session_files = [self.chat_dir / f"{session_id}.json" for session_id in session_ids]
        else:
            session_files = list(self.chat_dir.glob("*.json"))

        for session_file in session_files:
            if not session_file.exists():
                continue

            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # Extract requests from session
                session_requests = self._extract_requests_from_session(session_data, session_file.stem)
                requests.extend(session_requests)

            except Exception as e:
                logger.error(f"Error reading session {session_file}: {e}")

        logger.info(f"📊 Scanned {len(session_files)} sessions, extracted {len(requests)} requests")
        return requests

    def _extract_requests_from_session(self, session_data: Dict[str, Any], session_id: str) -> List[ChatRequest]:
        try:
            """Extract requests from a session data structure"""
            requests = []

            # Common session structures
            messages = session_data.get("messages", [])
            if not messages:
                messages = session_data.get("history", [])
            if not messages:
                messages = session_data.get("chat", [])

            for i, message in enumerate(messages):
                # Look for user requests
                role = message.get("role", "").lower()
                content = message.get("content", "")

                if role in ["user", "human"] and content:
                    request = ChatRequest(
                        request_id=f"{session_id}_req_{i}",
                        chat_session_id=session_id,
                        timestamp=message.get("timestamp", datetime.now().isoformat()),
                        content=content,
                        context={
                            "message_index": i,
                            "session_metadata": session_data.get("metadata", {})
                        }
                    )
                    requests.append(request)

            return requests

        except Exception as e:
            self.logger.error(f"Error in _extract_requests_from_session: {e}", exc_info=True)
            raise
    def analyze_and_consolidate(self, session_ids: Optional[List[str]] = None,
                                similarity_threshold: float = 0.6) -> List:
        """
        Analyze chat sessions and consolidate similar requests

        Args:
            session_ids: Optional list of session IDs to analyze
            similarity_threshold: Similarity threshold for consolidation

        Returns:
            List of consolidated requests
        """
        # Scan sessions
        requests = self.scan_chat_sessions(session_ids)

        if not requests:
            logger.info("No requests found to consolidate")
            return []

        # Create consolidator
        consolidator = DummyConsolidator(self.project_root)

        # Process requests
        consolidated = consolidator.process_chat_requests(
            requests,
            similarity_threshold=similarity_threshold,
            cleanup=True,
            archive=True
        )

        return consolidated


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze chat sessions and consolidate requests")
    parser.add_argument("--sessions", nargs="+", help="Specific session IDs to analyze")
    parser.add_argument("--threshold", type=float, default=0.6,
                       help="Similarity threshold for consolidation (0-1)")

    args = parser.parse_args()

    analyzer = ChatSessionAnalyzer(project_root)
    consolidated = analyzer.analyze_and_consolidate(
        session_ids=args.sessions,
        similarity_threshold=args.threshold
    )

    print(f"\n✅ Consolidated {len(consolidated)} requests")
    for consolidated_req in consolidated:
        print(f"   - {consolidated_req.consolidated_id}: {consolidated_req.intent}")


if __name__ == "__main__":



    main()