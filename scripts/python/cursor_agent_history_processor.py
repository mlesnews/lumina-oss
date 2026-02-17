#!/usr/bin/env python3
"""
Cursor IDE Agent History Processor

Processes all Cursor IDE agent history from inception to present:
1. Discovers all agent transcripts
2. Analyzes status of each chat/request
3. Archives completed chats/requests
4. Provides comprehensive status overview

Tags: #CURSOR_IDE #AGENT_HISTORY #ARCHIVE #WORKFLOW #STATUS @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorAgentHistoryProcessor")


class ChatStatus(Enum):
    """Chat/Request status"""
    UNKNOWN = "unknown"
    ACTIVE = "active"
    COMPLETED = "completed"
    STALLED = "stalled"
    ERROR = "error"
    ARCHIVED = "archived"
    IN_PROGRESS = "in_progress"
    NEEDS_FOLLOWUP = "needs_followup"


class CursorAgentHistoryProcessor:
    """
    Cursor IDE Agent History Processor

    Processes all agent history from inception to present:
    - Discovers all transcripts
    - Analyzes status
    - Archives completed
    - Provides status overview
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_agent_history"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.archive_dir = self.data_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.status_dir = self.data_dir / "status"
        self.status_dir.mkdir(parents=True, exist_ok=True)

        # Cursor transcript locations
        self.cursor_projects_dir = Path.home() / ".cursor" / "projects"

        # Processing results
        self.processed_chats = []
        self.archived_chats = []
        self.status_summary = {}

        logger.info("✅ Cursor Agent History Processor initialized")

    def discover_agent_transcripts(self) -> List[Path]:
        try:
            """
            Discover all Cursor IDE agent transcripts from inception to present

            Returns:
                List of transcript file paths
            """
            logger.info("=" * 80)
            logger.info("🔍 DISCOVERING CURSOR IDE AGENT TRANSCRIPTS")
            logger.info("=" * 80)

            transcripts = []

            # Search in .cursor/projects directories
            if self.cursor_projects_dir.exists():
                for project_dir in self.cursor_projects_dir.iterdir():
                    if project_dir.is_dir():
                        agent_transcripts_dir = project_dir / "agent-transcripts"
                        if agent_transcripts_dir.exists():
                            for transcript_file in agent_transcripts_dir.glob("*.txt"):
                                transcripts.append(transcript_file)
                                logger.info(f"   ✅ Found: {transcript_file.name}")

            # Also check workspace .cursor directories
            cursor_dirs = [
                self.project_root / ".cursor",
                Path.home() / ".cursor"
            ]

            for cursor_dir in cursor_dirs:
                if cursor_dir.exists():
                    # Look for any transcript-like files
                    for transcript_file in cursor_dir.rglob("*.txt"):
                        if "agent" in transcript_file.name.lower() or "transcript" in transcript_file.name.lower():
                            if transcript_file not in transcripts:
                                transcripts.append(transcript_file)
                                logger.info(f"   ✅ Found: {transcript_file.name}")

            logger.info(f"\n   📊 Total transcripts discovered: {len(transcripts)}")

            return transcripts

        except Exception as e:
            self.logger.error(f"Error in discover_agent_transcripts: {e}", exc_info=True)
            raise
    def analyze_transcript_status(self, transcript_path: Path) -> Dict[str, Any]:
        """
        Analyze status of a transcript

        Args:
            transcript_path: Path to transcript file

        Returns:
            Status analysis
        """
        try:
            with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Get file metadata
            stat = transcript_path.stat()
            created_time = datetime.fromtimestamp(stat.st_ctime)
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            # Extract transcript ID from filename
            transcript_id = transcript_path.stem

            # Analyze content for status indicators
            status = self._determine_status(content, created_time, modified_time)

            # Extract key information
            analysis = {
                "transcript_id": transcript_id,
                "file_path": str(transcript_path),
                "file_name": transcript_path.name,
                "status": status.value,
                "created": created_time.isoformat(),
                "modified": modified_time.isoformat(),
                "size_bytes": stat.st_size,
                "line_count": len(content.splitlines()),
                "indicators": self._extract_status_indicators(content),
                "metadata": {
                    "analyzed_at": datetime.now().isoformat(),
                    "analyzer_version": "1.0.0"
                }
            }

            return analysis

        except Exception as e:
            logger.error(f"   ❌ Error analyzing {transcript_path.name}: {e}")
            return {
                "transcript_id": transcript_path.stem,
                "file_path": str(transcript_path),
                "status": ChatStatus.ERROR.value,
                "error": str(e)
            }

    def _determine_status(
        self,
        content: str,
        created_time: datetime,
        modified_time: datetime
    ) -> ChatStatus:
        """
        Determine status from content and timestamps

        Args:
            content: Transcript content
            created_time: File creation time
            modified_time: File modification time

        Returns:
            ChatStatus
        """
        # Check for completion indicators
        completion_indicators = [
            r"✅.*complete",
            r"COMPLETE",
            r"Status.*complete",
            r"finished",
            r"done",
            r"resolved",
            r"successfully"
        ]

        for pattern in completion_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return ChatStatus.COMPLETED

        # Check for error indicators
        error_indicators = [
            r"❌.*error",
            r"ERROR",
            r"failed",
            r"exception",
            r"traceback"
        ]

        for pattern in error_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return ChatStatus.ERROR

        # Check for stalled indicators
        stalled_indicators = [
            r"stall",
            r"stuck",
            r"blocked",
            r"pending",
            r"waiting"
        ]

        for pattern in stalled_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                return ChatStatus.STALLED

        # Check modification time (if not modified recently, likely completed)
        time_since_modification = (datetime.now() - modified_time).total_seconds()
        days_since_modification = time_since_modification / 86400

        if days_since_modification > 7:
            # Not modified in 7+ days, likely completed
            return ChatStatus.COMPLETED

        # Check if content ends with completion-like patterns
        if content.strip().endswith(("✅", "complete", "done", "finished")):
            return ChatStatus.COMPLETED

        # Default to in_progress if recently modified
        if days_since_modification < 1:
            return ChatStatus.IN_PROGRESS

        return ChatStatus.UNKNOWN

    def _extract_status_indicators(self, content: str) -> Dict[str, Any]:
        """Extract status indicators from content"""
        indicators = {
            "has_completion": False,
            "has_error": False,
            "has_stall": False,
            "has_todo": False,
            "has_request_id": False,
            "request_ids": [],
            "tool_calls": 0,
            "user_messages": 0,
            "assistant_messages": 0
        }

        # Check for completion
        if re.search(r"✅|complete|done|finished", content, re.IGNORECASE):
            indicators["has_completion"] = True

        # Check for errors
        if re.search(r"❌|error|exception|failed", content, re.IGNORECASE):
            indicators["has_error"] = True

        # Check for stalls
        if re.search(r"stall|stuck|blocked", content, re.IGNORECASE):
            indicators["has_stall"] = True

        # Check for TODOs
        if re.search(r"TODO|todo|@TODO", content, re.IGNORECASE):
            indicators["has_todo"] = True

        # Extract Request IDs (UUID format)
        request_id_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        request_ids = re.findall(request_id_pattern, content, re.I)
        if request_ids:
            indicators["has_request_id"] = True
            indicators["request_ids"] = list(set(request_ids))

        # Count messages
        indicators["user_messages"] = len(re.findall(r'^user:', content, re.MULTILINE | re.IGNORECASE))
        indicators["assistant_messages"] = len(re.findall(r'^assistant:', content, re.MULTILINE | re.IGNORECASE))
        indicators["tool_calls"] = len(re.findall(r'\[Tool call\]|tool_name', content, re.IGNORECASE))

        return indicators

    def archive_completed_chat(self, transcript_path: Path, analysis: Dict[str, Any]) -> bool:
        """
        Archive a completed chat/request

        Args:
            transcript_path: Path to transcript
            analysis: Status analysis

        Returns:
            True if archived successfully
        """
        try:
            # Create archive filename with date
            date_str = datetime.now().strftime('%Y%m%d')
            archive_filename = f"{analysis['transcript_id']}_{date_str}.txt"
            archive_path = self.archive_dir / archive_filename

            # Copy to archive
            import shutil
            shutil.copy2(transcript_path, archive_path)

            # Create archive metadata
            archive_metadata = {
                "transcript_id": analysis["transcript_id"],
                "original_path": str(transcript_path),
                "archived_path": str(archive_path),
                "archived_at": datetime.now().isoformat(),
                "status": analysis["status"],
                "analysis": analysis
            }

            metadata_path = self.archive_dir / f"{analysis['transcript_id']}_{date_str}_metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(archive_metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"   ✅ Archived: {transcript_path.name}")

            return True

        except Exception as e:
            logger.error(f"   ❌ Error archiving {transcript_path.name}: {e}")
            return False

    def process_all_history(
        self,
        archive_completed: bool = True,
        from_inception: bool = True
    ) -> Dict[str, Any]:
        """
        Process all Cursor IDE agent history from inception to present

        Args:
            archive_completed: Whether to archive completed chats
            from_inception: Process from inception (all time)

        Returns:
            Processing results
        """
        logger.info("=" * 80)
        logger.info("📊 PROCESSING CURSOR IDE AGENT HISTORY")
        logger.info("   From Inception to Present")
        logger.info("=" * 80)
        logger.info("")

        # Discover all transcripts
        transcripts = self.discover_agent_transcripts()

        if not transcripts:
            logger.warning("   ⚠️  No transcripts found")
            return {
                "success": False,
                "error": "No transcripts found",
                "processed": 0,
                "archived": 0
            }

        logger.info("")
        logger.info("=" * 80)
        logger.info("📋 ANALYZING TRANSCRIPT STATUS")
        logger.info("=" * 80)
        logger.info("")

        # Process each transcript
        status_counts = {}
        for transcript_path in transcripts:
            analysis = self.analyze_transcript_status(transcript_path)
            self.processed_chats.append(analysis)

            status = analysis.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            logger.info(f"   [{status.upper()}] {transcript_path.name}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 STATUS SUMMARY")
        logger.info("=" * 80)
        logger.info("")

        for status, count in sorted(status_counts.items()):
            logger.info(f"   {status}: {count}")

        # Archive completed chats
        if archive_completed:
            logger.info("")
            logger.info("=" * 80)
            logger.info("📦 ARCHIVING COMPLETED CHATS")
            logger.info("=" * 80)
            logger.info("")

            completed_chats = [
                (t, a) for t, a in zip(transcripts, self.processed_chats)
                if a.get("status") == ChatStatus.COMPLETED.value
            ]

            for transcript_path, analysis in completed_chats:
                if self.archive_completed_chat(transcript_path, analysis):
                    self.archived_chats.append(analysis["transcript_id"])

        # Save processing results
        results = {
            "timestamp": datetime.now().isoformat(),
            "processed_count": len(self.processed_chats),
            "archived_count": len(self.archived_chats),
            "status_summary": status_counts,
            "processed_chats": self.processed_chats,
            "archived_chats": self.archived_chats,
            "metadata": {
                "from_inception": from_inception,
                "archive_completed": archive_completed
            }
        }

        # Save results
        results_file = self.status_dir / f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Processed: {len(self.processed_chats)}")
        logger.info(f"   Archived: {len(self.archived_chats)}")
        logger.info(f"   Results saved: {results_file.name}")
        logger.info("")

        return results

    def get_status_overview(self) -> Dict[str, Any]:
        """Get comprehensive status overview"""
        if not self.processed_chats:
            # Process if not already done
            self.process_all_history(archive_completed=False)

        overview = {
            "total_chats": len(self.processed_chats),
            "by_status": {},
            "by_date": {},
            "recent_chats": [],
            "oldest_chat": None,
            "newest_chat": None,
            "archived_count": len(self.archived_chats)
        }

        # Count by status
        for chat in self.processed_chats:
            status = chat.get("status", "unknown")
            overview["by_status"][status] = overview["by_status"].get(status, 0) + 1

        # Group by date
        for chat in self.processed_chats:
            created = chat.get("created", "")
            if created:
                date = created.split("T")[0]
                overview["by_date"][date] = overview["by_date"].get(date, 0) + 1

        # Get recent chats (last 10)
        sorted_chats = sorted(
            self.processed_chats,
            key=lambda x: x.get("modified", ""),
            reverse=True
        )[:10]
        overview["recent_chats"] = [
            {
                "transcript_id": c["transcript_id"],
                "status": c["status"],
                "modified": c.get("modified", "")
            }
            for c in sorted_chats
        ]

        # Find oldest and newest
        if self.processed_chats:
            sorted_by_created = sorted(
                self.processed_chats,
                key=lambda x: x.get("created", "")
            )
            overview["oldest_chat"] = sorted_by_created[0].get("created", "")
            overview["newest_chat"] = sorted_by_created[-1].get("created", "")

        return overview


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Agent History Processor")
    parser.add_argument("--process", action="store_true", help="Process all history")
    parser.add_argument("--archive", action="store_true", help="Archive completed chats")
    parser.add_argument("--status", action="store_true", help="Show status overview")
    parser.add_argument("--from-inception", action="store_true", default=True, help="Process from inception")

    args = parser.parse_args()

    processor = CursorAgentHistoryProcessor()

    if args.process or args.archive:
        processor.process_all_history(
            archive_completed=args.archive,
            from_inception=args.from_inception
        )
    elif args.status:
        overview = processor.get_status_overview()
        print("\n📊 Cursor IDE Agent History Status Overview\n")
        print(f"Total Chats: {overview['total_chats']}")
        print(f"Archived: {overview['archived_count']}")
        print(f"\nBy Status:")
        for status, count in sorted(overview['by_status'].items()):
            print(f"  {status}: {count}")
        print(f"\nOldest Chat: {overview.get('oldest_chat', 'N/A')}")
        print(f"Newest Chat: {overview.get('newest_chat', 'N/A')}")
    else:
        # Default: Process and show status
        processor.process_all_history(archive_completed=True)
        overview = processor.get_status_overview()
        print("\n📊 Status Overview\n")
        print(f"Total: {overview['total_chats']}")
        print(f"Archived: {overview['archived_count']}")
        for status, count in sorted(overview['by_status'].items()):
            print(f"  {status}: {count}")

    return 0


if __name__ == "__main__":


    sys.exit(main())