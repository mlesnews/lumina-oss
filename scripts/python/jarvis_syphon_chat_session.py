#!/usr/bin/env python3
"""
JARVIS @SYPHON - Chat Session Extraction
Extracts entire AI chat session from Cursor IDE

@SYPHON extracts intelligence and data from chat sessions.
This extracts the entire current chat session for analysis.

Tags: #JARVIS #SYPHON #EXTRACTION #CHAT #SESSION #INTELLIGENCE
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("JARVISSyphon")


class JARVISSyphonChatSession:
    """
    JARVIS @SYPHON Chat Session Extractor

    Extracts entire chat session from Cursor IDE for:
    - Intelligence extraction
    - Pattern analysis
    - Knowledge capture
    - System learning
    """

    def __init__(self, project_root: Path):
        """Initialize SYPHON extractor"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.syphon_path = self.data_path / "syphon"
        self.syphon_path.mkdir(parents=True, exist_ok=True)

        # Chat sessions path
        self.chat_sessions_path = self.syphon_path / "chat_sessions"
        self.chat_sessions_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("🔍 JARVIS @SYPHON Chat Session Extractor initialized")

    def extract_chat_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """
            Extract chat session data

            Args:
                session_data: Chat session data including messages, context, etc.

            Returns:
                Extracted intelligence and structured data
            """
            self.logger.info("🔍 @SYPHON extracting chat session...")

            timestamp = datetime.now()
            session_id = f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # Extract intelligence
            extracted = {
                "session_id": session_id,
                "timestamp": timestamp.isoformat(),
                "extraction_type": "chat_session",
                "source": "cursor_ide",
                "session_data": session_data,
                "intelligence": {
                    "topics": self._extract_topics(session_data),
                    "decisions": self._extract_decisions(session_data),
                    "actions": self._extract_actions(session_data),
                    "patterns": self._extract_patterns(session_data),
                    "knowledge": self._extract_knowledge(session_data),
                    "metrics": self._extract_metrics(session_data)
                },
                "metadata": {
                    "message_count": len(session_data.get("messages", [])),
                    "user_messages": sum(1 for m in session_data.get("messages", []) if m.get("role") == "user"),
                    "assistant_messages": sum(1 for m in session_data.get("messages", []) if m.get("role") == "assistant"),
                    "duration": self._calculate_duration(session_data),
                    "files_mentioned": self._extract_files(session_data),
                    "systems_mentioned": self._extract_systems(session_data)
                }
            }

            # Save extracted data
            output_file = self.chat_sessions_path / f"{session_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(extracted, f, indent=2, ensure_ascii=False)

            # Also save to main extracted_data.json
            self._append_to_extracted_data(extracted)

            self.logger.info(f"✅ @SYPHON extracted session: {session_id}")
            self.logger.info(f"   Topics: {len(extracted['intelligence']['topics'])}")
            self.logger.info(f"   Decisions: {len(extracted['intelligence']['decisions'])}")
            self.logger.info(f"   Actions: {len(extracted['intelligence']['actions'])}")

            return extracted

        except Exception as e:
            self.logger.error(f"Error in extract_chat_session: {e}", exc_info=True)
            raise
    def _extract_topics(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract topics discussed"""
        topics = set()
        messages = session_data.get("messages", [])

        # Look for key topics in messages
        topic_keywords = [
            "time tracking", "analytics", "metrics",
            "project manager", "batch", "workflow",
            "cursor ide", "agents", "editor",
            "system resources", "performance", "bottleneck"
        ]

        for message in messages:
            content = message.get("content", "").lower()
            for keyword in topic_keywords:
                if keyword in content:
                    topics.add(keyword)

        return sorted(list(topics))

    def _extract_decisions(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decisions made"""
        decisions = []
        messages = session_data.get("messages", [])

        # Look for decision patterns
        decision_indicators = ["decided", "chose", "selected", "will use", "going to"]

        for message in messages:
            content = message.get("content", "")
            if any(indicator in content.lower() for indicator in decision_indicators):
                decisions.append({
                    "message": content[:200],
                    "timestamp": message.get("timestamp", ""),
                    "role": message.get("role", "")
                })

        return decisions

    def _extract_actions(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actions taken"""
        actions = []
        messages = session_data.get("messages", [])

        # Look for action patterns
        action_indicators = ["created", "implemented", "added", "updated", "fixed", "tracking"]

        for message in messages:
            content = message.get("content", "")
            if any(indicator in content.lower() for indicator in action_indicators):
                actions.append({
                    "action": content[:200],
                    "timestamp": message.get("timestamp", ""),
                    "role": message.get("role", "")
                })

        return actions

    def _extract_patterns(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract patterns"""
        patterns = []

        # Extract common patterns
        messages = session_data.get("messages", [])
        user_patterns = []
        assistant_patterns = []

        for message in messages:
            if message.get("role") == "user":
                user_patterns.append(message.get("content", "")[:100])
            elif message.get("role") == "assistant":
                assistant_patterns.append(message.get("content", "")[:100])

        # Identify patterns
        if len(user_patterns) > 0:
            patterns.append(f"User message patterns: {len(user_patterns)} messages")
        if len(assistant_patterns) > 0:
            patterns.append(f"Assistant response patterns: {len(assistant_patterns)} responses")

        return patterns

    def _extract_knowledge(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract knowledge/insights"""
        knowledge = []
        messages = session_data.get("messages", [])

        # Extract key knowledge points
        knowledge_keywords = ["learned", "understood", "discovered", "found", "realized"]

        for message in messages:
            content = message.get("content", "")
            if any(keyword in content.lower() for keyword in knowledge_keywords):
                knowledge.append(content[:300])

        return knowledge

    def _extract_metrics(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics"""
        messages = session_data.get("messages", [])

        return {
            "total_messages": len(messages),
            "user_messages": sum(1 for m in messages if m.get("role") == "user"),
            "assistant_messages": sum(1 for m in messages if m.get("role") == "assistant"),
            "average_message_length": sum(len(m.get("content", "")) for m in messages) / len(messages) if messages else 0,
            "files_referenced": len(self._extract_files(session_data)),
            "systems_referenced": len(self._extract_systems(session_data))
        }

    def _extract_files(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract files mentioned"""
        files = set()
        messages = session_data.get("messages", [])

        # Look for file paths
        import re
        file_pattern = r'[a-zA-Z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]+\.\w+|/[^/]+(?:\.[^/]+)?'

        for message in messages:
            content = message.get("content", "")
            matches = re.findall(file_pattern, content)
            files.update(matches)

        return sorted(list(files))

    def _extract_systems(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract systems mentioned"""
        systems = set()
        messages = session_data.get("messages", [])

        system_keywords = ["JARVIS", "MARVIN", "SYPHON", "WakaTime", "Cursor", "Project Manager", "@Agents", "@Editor"]

        for message in messages:
            content = message.get("content", "")
            for keyword in system_keywords:
                if keyword in content:
                    systems.add(keyword)

        return sorted(list(systems))

    def _calculate_duration(self, session_data: Dict[str, Any]) -> Optional[float]:
        """Calculate session duration"""
        messages = session_data.get("messages", [])
        if len(messages) < 2:
            return None

        # Try to get timestamps
        timestamps = []
        for message in messages:
            ts = message.get("timestamp")
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except:
                    pass

        if len(timestamps) >= 2:
            duration = (timestamps[-1] - timestamps[0]).total_seconds()
            return duration

        return None

    def _append_to_extracted_data(self, extracted: Dict[str, Any]):
        """Append to main extracted_data.json"""
        extracted_data_file = self.syphon_path / "extracted_data.json"

        if extracted_data_file.exists():
            try:
                with open(extracted_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Handle case where file contains a list instead of dict
                if isinstance(data, list):
                    data = {"extractions": data}
            except:
                data = {"extractions": []}
        else:
            data = {"extractions": []}

        if "extractions" not in data or not isinstance(data, dict):
            data = {"extractions": []}

        if not isinstance(data.get("extractions"), list):
            data["extractions"] = []

        data["extractions"].append(extracted)
        data["last_updated"] = datetime.now().isoformat()

        with open(extracted_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @SYPHON Chat Session Extractor")
        parser.add_argument("--extract", type=str, help="Extract from session JSON file")
        parser.add_argument("--session-id", type=str, help="Session ID to extract")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        syphon = JARVISSyphonChatSession(project_root)

        if args.extract:
            # Load session from file
            session_file = Path(args.extract)
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                extracted = syphon.extract_chat_session(session_data)
                print(f"✅ Extracted session: {extracted['session_id']}")
            else:
                print(f"❌ Session file not found: {session_file}")
        else:
            print("Usage: --extract <session_file.json>")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()