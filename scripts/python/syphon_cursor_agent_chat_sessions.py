#!/usr/bin/env python3
"""
@SYPHON: Cursor IDE Agent Chat Sessions & Workflow Analysis

Extracts and analyzes Cursor IDE agent chat sessions and workflows.
Part of the flow: @syphon => @pipe => @peak <=> @reality

Tags: #SYPHON #CURSOR_IDE #AGENT_CHAT #WORKFLOW #ANALYSIS @JARVIS @LUMINA @RR
"""

import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from cursor_agent_history_processor import (ChatStatus,
                                                CursorAgentHistoryProcessor)
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonCursorAgentChatSessions")


class SyphonCursorAgentChatSessions:
    """
    @SYPHON: Cursor IDE Agent Chat Sessions & Workflow Analysis

    Extracts intelligence from agent chat sessions:
    - Session patterns
    - Workflow analysis
    - Agent interactions
    - Request tracking
    - Tool usage patterns
    - Error patterns
    - Completion patterns
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize SYPHON for Cursor agent chat sessions.

        Args:
            project_root: Path to project root
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        # Chat session directories
        self.chat_sessions_dir = self.data_dir / "agent_chat_sessions"
        self.agent_sessions_dir = self.data_dir / "agent_sessions"

        # SYPHON output directory
        self.syphon_output_dir = self.data_dir / "syphon" / "cursor_agent_chat"
        self.syphon_output_dir.mkdir(parents=True, exist_ok=True)

        # Cursor transcript processor
        self.transcript_processor = CursorAgentHistoryProcessor(project_root)

        logger.info("🔍 @SYPHON: Cursor Agent Chat Sessions initialized")
        logger.info(f"   Chat sessions: {self.chat_sessions_dir}")
        logger.info(f"   Agent sessions: {self.agent_sessions_dir}")
        logger.info(f"   Output: {self.syphon_output_dir}")

    def discover_chat_sessions(self) -> List[Path]:
        try:
            """
            Discover all agent chat session files.

            Returns:
                List of chat session file paths
            """
            sessions = []

            # Discover JSON chat sessions
            if self.chat_sessions_dir.exists():
                for session_file in self.chat_sessions_dir.glob("*.json"):
                    sessions.append(session_file)

            # Discover agent sessions
            if self.agent_sessions_dir.exists():
                for session_file in self.agent_sessions_dir.glob("*.json"):
                    sessions.append(session_file)

            # Discover Cursor transcripts
            transcripts = self.transcript_processor.discover_agent_transcripts()
            sessions.extend(transcripts)

            logger.info(f"📊 Discovered {len(sessions)} chat sessions")
            return sessions

        except Exception as e:
            self.logger.error(f"Error in discover_chat_sessions: {e}", exc_info=True)
            raise
    def extract_session_intelligence(self, session_path: Path) -> Dict[str, Any]:
        """
        Extract intelligence from a chat session.

        Args:
            session_path: Path to session file

        Returns:
            Extracted intelligence
        """
        try:
            # Read session file
            if session_path.suffix == ".json":
                with open(session_path, encoding="utf-8") as f:
                    session_data = json.load(f)
            else:
                # Text transcript
                with open(session_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    session_data = {"content": content, "type": "transcript"}

            # Extract intelligence
            intelligence = {
                "session_id": session_path.stem,
                "file_path": str(session_path),
                "file_type": session_path.suffix,
                "extracted_at": datetime.now().isoformat(),
                "agents": self._extract_agents(session_data),
                "messages": self._extract_messages(session_data),
                "workflow": self._extract_workflow(session_data),
                "tools_used": self._extract_tools(session_data),
                "request_ids": self._extract_request_ids(session_data),
                "errors": self._extract_errors(session_data),
                "completions": self._extract_completions(session_data),
                "patterns": self._extract_patterns(session_data),
                "metadata": self._extract_metadata(session_data)
            }

            return intelligence

        except Exception as e:
            logger.error(f"Error extracting intelligence from {session_path.name}: {e}")
            return {
                "session_id": session_path.stem,
                "error": str(e),
                "extracted_at": datetime.now().isoformat()
            }

    def _extract_agents(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract agents involved in session"""
        agents = []

        # Check for agents_involved field
        if "agents_involved" in session_data:
            agents.extend(session_data["agents_involved"])

        # Extract from messages
        if "messages" in session_data:
            for msg in session_data["messages"]:
                if "agent" in msg:
                    agent = msg["agent"]
                    if agent not in agents:
                        agents.append(agent)

        # Extract from content (text transcripts)
        if "content" in session_data:
            content = session_data["content"]
            # Look for agent mentions
            agent_pattern = r'(JARVIS|SYPHON|ACE|IMVA|HELPDESK|ARMOURY_CRATE|DIAGNOSTICS|MARVIN|WOPR|ULTRON|KAIJU)'
            found_agents = re.findall(agent_pattern, content, re.IGNORECASE)
            agents.extend(found_agents)

        return list(set(agents))

    def _extract_messages(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract message statistics"""
        stats = {
            "total": 0,
            "by_agent": defaultdict(int),
            "by_type": defaultdict(int),
            "user_messages": 0,
            "assistant_messages": 0,
            "system_messages": 0
        }

        if "messages" in session_data:
            for msg in session_data["messages"]:
                stats["total"] += 1

                if "agent" in msg:
                    stats["by_agent"][msg["agent"]] += 1

                if "type" in msg:
                    stats["by_type"][msg["type"]] += 1

                msg_type = msg.get("type", "").lower()
                if "user" in msg_type:
                    stats["user_messages"] += 1
                elif "assistant" in msg_type or "agent" in msg_type:
                    stats["assistant_messages"] += 1
                elif "system" in msg_type:
                    stats["system_messages"] += 1

        # Convert defaultdicts to regular dicts
        stats["by_agent"] = dict(stats["by_agent"])
        stats["by_type"] = dict(stats["by_type"])

        return stats

    def _extract_workflow(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow patterns"""
        workflow = {
            "steps": [],
            "transitions": [],
            "decision_points": [],
            "loops": [],
            "parallel_actions": []
        }

        if "messages" in session_data:
            messages = session_data["messages"]
            for i, msg in enumerate(messages):
                # Extract workflow steps
                if "agent" in msg and "message" in msg:
                    workflow["steps"].append({
                        "step": i + 1,
                        "agent": msg["agent"],
                        "action": msg.get("message", "")[:100],
                        "timestamp": msg.get("timestamp", "")
                    })

                # Detect transitions
                if i > 0:
                    prev_agent = messages[i-1].get("agent")
                    curr_agent = msg.get("agent")
                    if prev_agent != curr_agent:
                        workflow["transitions"].append({
                            "from": prev_agent,
                            "to": curr_agent,
                            "step": i + 1
                        })

        # Extract from content (text transcripts)
        if "content" in session_data:
            content = session_data["content"]
            # Look for workflow patterns
            if re.search(r"workflow|process|step|stage", content, re.IGNORECASE):
                workflow["has_workflow_mentions"] = True

        return workflow

    def _extract_tools(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract tools used in session"""
        tools = []

        if "messages" in session_data:
            for msg in session_data["messages"]:
                message_text = str(msg.get("message", ""))
                # Look for tool mentions
                tool_pattern = r'(tool|function|api|script|command|execute|run)'
                if re.search(tool_pattern, message_text, re.IGNORECASE):
                    # Try to extract tool name
                    tool_match = re.search(r'(\w+_tool|\w+_function|\w+\.py)', message_text, re.IGNORECASE)
                    if tool_match:
                        tools.append(tool_match.group(1))

        # Extract from content
        if "content" in session_data:
            content = session_data["content"]
            # Look for [Tool call] patterns
            tool_calls = re.findall(r'\[Tool call\]\s+(\w+)', content, re.IGNORECASE)
            tools.extend(tool_calls)

        return list(set(tools))

    def _extract_request_ids(self, session_data: Dict[str, Any]) -> List[str]:
        """Extract request IDs from session"""
        request_ids = []

        # UUID pattern
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

        # Check messages
        if "messages" in session_data:
            for msg in session_data["messages"]:
                message_text = str(msg.get("message", ""))
                found_ids = re.findall(uuid_pattern, message_text, re.IGNORECASE)
                request_ids.extend(found_ids)

        # Check content
        if "content" in session_data:
            found_ids = re.findall(uuid_pattern, session_data["content"], re.IGNORECASE)
            request_ids.extend(found_ids)

        return list(set(request_ids))

    def _extract_errors(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract errors from session"""
        errors = []

        if "messages" in session_data:
            for msg in session_data["messages"]:
                message_text = str(msg.get("message", ""))
                if re.search(r'error|exception|failed|❌|traceback', message_text, re.IGNORECASE):
                    errors.append({
                        "agent": msg.get("agent", "unknown"),
                        "message": message_text[:200],
                        "timestamp": msg.get("timestamp", "")
                    })

        # Check content
        if "content" in session_data:
            content = session_data["content"]
            error_lines = re.findall(r'.*error.*|.*exception.*|.*failed.*', content, re.IGNORECASE | re.MULTILINE)
            for line in error_lines[:10]:  # Limit to 10
                errors.append({
                    "source": "content",
                    "message": line.strip()[:200]
                })

        return errors

    def _extract_completions(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract completion indicators"""
        completions = []

        if "messages" in session_data:
            for msg in session_data["messages"]:
                message_text = str(msg.get("message", ""))
                if re.search(r'✅|complete|done|finished|success', message_text, re.IGNORECASE):
                    completions.append({
                        "agent": msg.get("agent", "unknown"),
                        "message": message_text[:200],
                        "timestamp": msg.get("timestamp", "")
                    })

        # Check resolutions
        if "resolutions" in session_data:
            for resolution in session_data["resolutions"]:
                completions.append({
                    "type": "resolution",
                    "message": str(resolution)
                })

        return completions

    def _extract_patterns(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from session"""
        patterns = {
            "has_todos": False,
            "has_workflow": False,
            "has_coordination": False,
            "has_errors": False,
            "has_completions": False,
            "agent_collaboration": False,
            "tool_usage": False
        }

        content_str = json.dumps(session_data, default=str)

        # Check for patterns
        patterns["has_todos"] = bool(re.search(r'todo|@todo|task|pending', content_str, re.IGNORECASE))
        patterns["has_workflow"] = bool(re.search(r'workflow|process|step|stage', content_str, re.IGNORECASE))
        patterns["has_coordination"] = bool(re.search(r'coordinate|collaborate|team|agent.*agent', content_str, re.IGNORECASE))
        patterns["has_errors"] = bool(re.search(r'error|exception|failed|❌', content_str, re.IGNORECASE))
        patterns["has_completions"] = bool(re.search(r'✅|complete|done|finished', content_str, re.IGNORECASE))
        patterns["agent_collaboration"] = len(self._extract_agents(session_data)) > 1
        patterns["tool_usage"] = len(self._extract_tools(session_data)) > 0

        return patterns

    def _extract_metadata(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from session"""
        metadata = {}

        # Standard fields
        for field in ["session_id", "inception_time", "archived", "archive_time", "metadata"]:
            if field in session_data:
                metadata[field] = session_data[field]

        # Issues tracked
        if "issues_tracked" in session_data:
            metadata["issues_tracked"] = session_data["issues_tracked"]

        # File metadata
        return metadata

    def analyze_all_sessions(self) -> Dict[str, Any]:
        try:
            """
            Analyze all chat sessions and extract intelligence.

            Returns:
                Comprehensive analysis
            """
            logger.info("=" * 80)
            logger.info("🔍 @SYPHON: ANALYZING CURSOR AGENT CHAT SESSIONS")
            logger.info("=" * 80)
            logger.info("")

            # Discover sessions
            sessions = self.discover_chat_sessions()

            if not sessions:
                logger.warning("⚠️  No chat sessions found")
                return {"error": "No sessions found"}

            logger.info(f"📊 Processing {len(sessions)} sessions...")
            logger.info("")

            # Extract intelligence from each session
            all_intelligence = []
            aggregated = {
                "total_sessions": len(sessions),
                "agents": defaultdict(int),
                "tools": defaultdict(int),
                "request_ids": [],
                "errors": [],
                "completions": [],
                "workflow_patterns": defaultdict(int),
                "by_status": defaultdict(int)
            }

            for session_path in sessions:
                logger.info(f"   🔍 Extracting: {session_path.name}")
                intelligence = self.extract_session_intelligence(session_path)
                all_intelligence.append(intelligence)

                # Aggregate data
                for agent in intelligence.get("agents", []):
                    aggregated["agents"][agent] += 1

                for tool in intelligence.get("tools_used", []):
                    aggregated["tools"][tool] += 1

                aggregated["request_ids"].extend(intelligence.get("request_ids", []))
                aggregated["errors"].extend(intelligence.get("errors", []))
                aggregated["completions"].extend(intelligence.get("completions", []))

                # Workflow patterns
                patterns = intelligence.get("patterns", {})
                for pattern, value in patterns.items():
                    if value:
                        aggregated["workflow_patterns"][pattern] += 1

            # Convert defaultdicts to regular dicts
            aggregated["agents"] = dict(aggregated["agents"])
            aggregated["tools"] = dict(aggregated["tools"])
            aggregated["workflow_patterns"] = dict(aggregated["workflow_patterns"])
            aggregated["by_status"] = dict(aggregated["by_status"])

            # Remove duplicates from request_ids
            aggregated["request_ids"] = list(set(aggregated["request_ids"]))

            # Create comprehensive analysis
            analysis = {
                "extracted_at": datetime.now().isoformat(),
                "total_sessions": len(sessions),
                "sessions_analyzed": len(all_intelligence),
                "aggregated": aggregated,
                "session_intelligence": all_intelligence,
                "summary": self._generate_summary(aggregated, all_intelligence)
            }

            # Save analysis
            output_file = self.syphon_output_dir / f"cursor_agent_chat_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ @SYPHON: ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Sessions analyzed: {len(all_intelligence)}")
            logger.info(f"   Output saved: {output_file.name}")
            logger.info("")

            # Print summary
            self._print_summary(analysis["summary"])

            return analysis

        except Exception as e:
            self.logger.error(f"Error in analyze_all_sessions: {e}", exc_info=True)
            raise
    def _generate_summary(self, aggregated: Dict[str, Any], intelligence: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary from analysis"""
        summary = {
            "top_agents": sorted(
                aggregated["agents"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "top_tools": sorted(
                aggregated["tools"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            "total_errors": len(aggregated["errors"]),
            "total_completions": len(aggregated["completions"]),
            "unique_request_ids": len(aggregated["request_ids"]),
            "workflow_patterns": aggregated["workflow_patterns"],
            "sessions_with_errors": sum(1 for i in intelligence if i.get("errors")),
            "sessions_with_completions": sum(1 for i in intelligence if i.get("completions")),
            "sessions_with_workflow": sum(1 for i in intelligence if i.get("patterns", {}).get("has_workflow", False))
        }

        return summary

    def _print_summary(self, summary: Dict[str, Any]):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("📊 @SYPHON: CURSOR AGENT CHAT SESSIONS ANALYSIS SUMMARY")
        print("=" * 80)
        print()

        print("🤖 Top Agents:")
        for agent, count in summary.get("top_agents", [])[:5]:
            print(f"   {agent}: {count} sessions")
        print()

        print("🛠️  Top Tools:")
        for tool, count in summary.get("top_tools", [])[:5]:
            print(f"   {tool}: {count} uses")
        print()

        print("📈 Statistics:")
        print(f"   Total Errors: {summary.get('total_errors', 0)}")
        print(f"   Total Completions: {summary.get('total_completions', 0)}")
        print(f"   Unique Request IDs: {summary.get('unique_request_ids', 0)}")
        print(f"   Sessions with Errors: {summary.get('sessions_with_errors', 0)}")
        print(f"   Sessions with Completions: {summary.get('sessions_with_completions', 0)}")
        print(f"   Sessions with Workflow: {summary.get('sessions_with_workflow', 0)}")
        print()

        print("🔄 Workflow Patterns:")
        for pattern, count in summary.get("workflow_patterns", {}).items():
            print(f"   {pattern}: {count} sessions")
        print()

        print("=" * 80)
        print()


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="@SYPHON: Cursor IDE Agent Chat Sessions Analysis")
        parser.add_argument("--analyze", action="store_true", help="Analyze all chat sessions")
        parser.add_argument("--session", help="Analyze specific session file")

        args = parser.parse_args()

        syphon = SyphonCursorAgentChatSessions()

        if args.session:
            # Analyze single session
            session_path = Path(args.session)
            if not session_path.exists():
                session_path = syphon.chat_sessions_dir / args.session
                if not session_path.exists():
                    print(f"❌ Session not found: {args.session}")
                    return 1

            intelligence = syphon.extract_session_intelligence(session_path)
            print("\n" + "=" * 80)
            print(f"🔍 @SYPHON: SESSION INTELLIGENCE - {session_path.name}")
            print("=" * 80)
            print(json.dumps(intelligence, indent=2, ensure_ascii=False, default=str))
            print("=" * 80)

        else:
            # Analyze all sessions
            analysis = syphon.analyze_all_sessions()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())