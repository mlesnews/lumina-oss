#!/usr/bin/env python3
"""
Extract All User Intents from Historical Sources

Finds all user requests/intents from:
- Chat transcripts
- Session logs
- Documentation
- Code comments
- Task lists
- Implementation plans

Identifies duplicates, consolidates, and tracks fulfillment status.

Tags: #INTENT #EXTRACTION #CONSOLIDATION #TRACKING @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ExtractUserIntents")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExtractUserIntents")


class UserIntentExtractor:
    """
    Extract and consolidate all user intents from historical sources
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.intents_dir = self.project_root / "data" / "user_intents"
        self.intents_dir.mkdir(parents=True, exist_ok=True)

        # Intent patterns to look for
        self.intent_patterns = [
            r"please\s+(.+?)(?:\.|$)",
            r"i\s+(?:would\s+)?like\s+(?:to\s+)?(.+?)(?:\.|$)",
            r"can\s+you\s+(.+?)(?:\.|$)",
            r"could\s+you\s+(.+?)(?:\.|$)",
            r"i\s+want\s+(?:to\s+)?(.+?)(?:\.|$)",
            r"i\s+need\s+(?:to\s+)?(.+?)(?:\.|$)",
            r"fix\s+(.+?)(?:\.|$)",
            r"update\s+(.+?)(?:\.|$)",
            r"implement\s+(.+?)(?:\.|$)",
            r"create\s+(.+?)(?:\.|$)",
            r"add\s+(.+?)(?:\.|$)",
            r"@doit",
            r"@roast",
            r"@ask",
            r"@fix",
        ]

        logger.info("="*80)
        logger.info("🔍 USER INTENT EXTRACTION SYSTEM")
        logger.info("="*80)
        logger.info("")

    def extract_all_intents(self) -> Dict[str, Any]:
        try:
            """
            Extract all user intents from all sources

            Returns:
                Comprehensive intent extraction report
            """
            logger.info("🔍 Extracting user intents from all sources...")
            logger.info("")

            all_intents = []

            # 1. Extract from chat transcripts
            logger.info("   📝 Extracting from chat transcripts...")
            transcript_intents = self._extract_from_transcripts()
            all_intents.extend(transcript_intents)
            logger.info(f"      Found {len(transcript_intents)} intents in transcripts")

            # 2. Extract from session logs
            logger.info("   📋 Extracting from session logs...")
            session_intents = self._extract_from_sessions()
            all_intents.extend(session_intents)
            logger.info(f"      Found {len(session_intents)} intents in sessions")

            # 3. Extract from documentation
            logger.info("   📚 Extracting from documentation...")
            doc_intents = self._extract_from_documentation()
            all_intents.extend(doc_intents)
            logger.info(f"      Found {len(doc_intents)} intents in documentation")

            # 4. Extract from task lists
            logger.info("   ✅ Extracting from task lists...")
            task_intents = self._extract_from_tasks()
            all_intents.extend(task_intents)
            logger.info(f"      Found {len(task_intents)} intents in tasks")

            # 5. Analyze and consolidate
            logger.info("")
            logger.info("   🔄 Analyzing and consolidating intents...")
            consolidated = self._consolidate_intents(all_intents)

            # 6. Identify duplicates and repetitions
            duplicates = self._identify_duplicates(consolidated)

            # 7. Track fulfillment status
            fulfillment = self._track_fulfillment(consolidated)

            # 8. Generate report
            report = {
                "extraction_date": datetime.now().isoformat(),
                "total_intents_found": len(all_intents),
                "unique_intents": len(consolidated),
                "duplicates": duplicates,
                "fulfillment_status": fulfillment,
                "consolidated_intents": consolidated,
                "overlooked_intents": [i for i in consolidated if i.get("fulfillment_status") == "overlooked"]
            }

            # Save report
            report_file = self.intents_dir / "all_intents_extraction_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("="*80)
            logger.info("✅ INTENT EXTRACTION COMPLETE")
            logger.info("="*80)
            logger.info(f"   Total Intents Found: {len(all_intents)}")
            logger.info(f"   Unique Intents: {len(consolidated)}")
            logger.info(f"   Duplicates: {len(duplicates)}")
            logger.info(f"   Overlooked: {len(report['overlooked_intents'])}")
            logger.info(f"   Report: {report_file}")
            logger.info("")

            return report

        except Exception as e:
            self.logger.error(f"Error in extract_all_intents: {e}", exc_info=True)
            raise
    def _extract_from_transcripts(self) -> List[Dict[str, Any]]:
        """Extract intents from chat transcripts"""
        intents = []
        # Try multiple possible locations
        possible_dirs = [
            Path.home() / ".cursor" / "projects" / "c-Users-mlesn-Dropbox-my-projects-lumina",
            Path.home() / ".cursor" / "projects" / "c-Users-mlesn-Dropbox-my-projects-lumina" / "agent-transcripts",
            self.project_root / "data" / "agent_sessions"
        ]

        transcripts_dir = None
        for dir_path in possible_dirs:
            if dir_path.exists():
                transcripts_dir = dir_path
                break

        if not transcripts_dir:
            logger.warning(f"Transcripts directory not found in any expected location")
            return intents

        for transcript_file in transcripts_dir.glob("*.txt"):
            try:
                with open(transcript_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract user messages
                    user_messages = re.findall(r'user:\s*(.+?)(?=\nassistant:|\nuser:|\Z)', content, re.DOTALL | re.IGNORECASE)
                    for msg in user_messages:
                        intent = self._parse_intent_from_text(msg, transcript_file.name)
                        if intent:
                            intents.append(intent)
            except Exception as e:
                logger.warning(f"Error reading {transcript_file}: {e}")

        return intents

    def _extract_from_sessions(self) -> List[Dict[str, Any]]:
        """Extract intents from session logs"""
        intents = []
        sessions_dir = self.project_root / "data" / "agent_sessions"

        if not sessions_dir.exists():
            return intents

        for session_file in sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    # Extract user messages/intents from session
                    if isinstance(session_data, dict):
                        messages = session_data.get("messages", [])
                        for msg in messages:
                            if msg.get("role") == "user":
                                intent = self._parse_intent_from_text(msg.get("content", ""), session_file.name)
                                if intent:
                                    intents.append(intent)
            except Exception as e:
                logger.warning(f"Error reading {session_file}: {e}")

        return intents

    def _extract_from_documentation(self) -> List[Dict[str, Any]]:
        """Extract intents from documentation"""
        intents = []
        docs_dir = self.project_root / "docs"

        if not docs_dir.exists():
            return intents

        for doc_file in docs_dir.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Look for TODO, FIXME, or explicit intent statements
                    todo_pattern = r'(?:TODO|FIXME|INTENT|REQUEST):\s*(.+?)(?:\n|$)'
                    matches = re.findall(todo_pattern, content, re.IGNORECASE)
                    for match in matches:
                        intent = {
                            "intent_text": match.strip(),
                            "source": str(doc_file.relative_to(self.project_root)),
                            "source_type": "documentation",
                            "timestamp": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
                        }
                        intents.append(intent)
            except Exception as e:
                logger.warning(f"Error reading {doc_file}: {e}")

        return intents

    def _extract_from_tasks(self) -> List[Dict[str, Any]]:
        """Extract intents from task lists"""
        intents = []
        tasks_file = self.project_root / "data" / "ask_database" / "implementation_plan_tasks.json"

        if not tasks_file.exists():
            return intents

        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
                asks = tasks_data.get("asks", {})
                for ask_id, ask_data in asks.items():
                    intent = {
                        "intent_text": ask_data.get("title", ""),
                        "description": ask_data.get("description", ""),
                        "source": "implementation_plan_tasks.json",
                        "source_type": "task",
                        "ask_id": ask_id,
                        "status": ask_data.get("status", "pending"),
                        "timestamp": ask_data.get("created_at", datetime.now().isoformat())
                    }
                    intents.append(intent)
        except Exception as e:
            logger.warning(f"Error reading {tasks_file}: {e}")

        return intents

    def _parse_intent_from_text(self, text: str, source: str) -> Optional[Dict[str, Any]]:
        """Parse intent from text using patterns"""
        text = text.strip()
        if not text or len(text) < 5:
            return None

        # Check for intent patterns
        for pattern in self.intent_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                intent_text = matches[0].strip() if matches else text[:100]
                return {
                    "intent_text": intent_text,
                    "full_text": text,
                    "source": source,
                    "source_type": "transcript",
                    "timestamp": datetime.now().isoformat()
                }

        # If no pattern match but text looks like intent
        if any(keyword in text.lower() for keyword in ["please", "fix", "update", "implement", "create", "add", "@doit", "@roast"]):
            return {
                "intent_text": text[:100],
                "full_text": text,
                "source": source,
                "source_type": "transcript",
                "timestamp": datetime.now().isoformat()
            }

        return None

    def _consolidate_intents(self, intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate similar intents"""
        # Group by normalized intent text
        groups = defaultdict(list)
        for intent in intents:
            normalized = self._normalize_intent(intent.get("intent_text", ""))
            groups[normalized].append(intent)

        consolidated = []
        for normalized, group in groups.items():
            # Use most complete intent as base
            base_intent = max(group, key=lambda x: len(x.get("full_text", x.get("intent_text", ""))))

            consolidated_intent = {
                "intent_id": f"intent_{len(consolidated) + 1:04d}",
                "intent_text": base_intent.get("intent_text", ""),
                "normalized_text": normalized,
                "repetition_count": len(group),
                "sources": [i.get("source") for i in group],
                "source_types": list(set(i.get("source_type") for i in group)),
                "first_seen": min(i.get("timestamp", "") for i in group),
                "last_seen": max(i.get("timestamp", "") for i in group),
                "fulfillment_status": "unknown",
                "implementation_status": "unknown"
            }

            # Merge additional fields
            if "description" in base_intent:
                consolidated_intent["description"] = base_intent["description"]
            if "ask_id" in base_intent:
                consolidated_intent["ask_id"] = base_intent["ask_id"]
            if "status" in base_intent:
                consolidated_intent["implementation_status"] = base_intent["status"]

            consolidated.append(consolidated_intent)

        return consolidated

    def _normalize_intent(self, text: str) -> str:
        """Normalize intent text for comparison"""
        # Lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove common words
        text = re.sub(r'\b(please|can you|could you|i want|i need|to)\b', '', text)
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def _identify_duplicates(self, intents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify duplicate/repeated intents"""
        duplicates = []
        for intent in intents:
            if intent.get("repetition_count", 1) > 1:
                duplicates.append({
                    "intent_id": intent.get("intent_id"),
                    "intent_text": intent.get("intent_text"),
                    "repetition_count": intent.get("repetition_count"),
                    "sources": intent.get("sources", [])
                })
        return duplicates

    def _track_fulfillment(self, intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track fulfillment status of intents"""
        status_counts = defaultdict(int)
        for intent in intents:
            status = intent.get("fulfillment_status", "unknown")
            status_counts[status] += 1

            # Try to determine fulfillment from implementation status
            impl_status = intent.get("implementation_status", "unknown")
            if impl_status == "completed":
                intent["fulfillment_status"] = "fulfilled"
            elif impl_status == "pending":
                intent["fulfillment_status"] = "pending"
            elif impl_status == "in_progress":
                intent["fulfillment_status"] = "in_progress"
            elif status == "unknown" and intent.get("repetition_count", 1) > 5:
                # High repetition suggests overlooked
                intent["fulfillment_status"] = "overlooked"

        return {
            "status_distribution": dict(status_counts),
            "total_tracked": len(intents)
        }


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        extractor = UserIntentExtractor(project_root)
        report = extractor.extract_all_intents()

        logger.info("")
        logger.info("="*80)
        logger.info("✅ EXTRACTION COMPLETE")
        logger.info("="*80)
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())