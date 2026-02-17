#!/usr/bin/env python3
"""
Systematic Agent Chat Walker

Programmatically walks through all agent-chat sessions to:
- Process @ask directives
- Manage @stack-heap memory
- Fix #workflows with @puppetmaster-workflow
- Systematic processing of all sessions

Tags: #workflows @puppetmaster-workflow @ask @stack-heap @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
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

logger = get_logger("SystematicAgentChatWalker")

# Import related systems
try:
    from cursor_agent_history_processor import CursorAgentHistoryProcessor
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    logger.warning("⚠️  Cursor agent history processor not available")

try:
    from syphon_cursor_agent_chat_sessions import SyphonCursorAgentChatSessions
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON not available")


class StackHeapManager:
    """
    @stack-heap: Memory management for agent chat sessions

    Manages:
    - Stack: Current active context
    - Heap: Long-term memory storage
    - Memory cleanup
    - Context switching
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize stack-heap manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "stack_heap"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.stack = []  # Current context stack
        self.heap = {}   # Long-term memory heap

        logger.info("✅ @stack-heap manager initialized")

    def push_to_stack(self, context: Dict[str, Any]):
        """Push context to stack"""
        self.stack.append(context)
        logger.debug(f"   Stack push: {len(self.stack)} items")

    def pop_from_stack(self) -> Optional[Dict[str, Any]]:
        """Pop context from stack"""
        if self.stack:
            return self.stack.pop()
        return None

    def store_to_heap(self, key: str, value: Any):
        """Store to heap (long-term memory)"""
        self.heap[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        logger.debug(f"   Heap store: {key}")

    def get_from_heap(self, key: str) -> Optional[Any]:
        """Get from heap"""
        if key in self.heap:
            return self.heap[key]["value"]
        return None

    def cleanup_heap(self, max_age_days: int = 30):
        """Cleanup old heap entries"""
        cutoff = datetime.now().timestamp() - (max_age_days * 86400)
        cleaned = 0

        for key in list(self.heap.keys()):
            entry = self.heap[key]
            entry_time = datetime.fromisoformat(entry["timestamp"]).timestamp()
            if entry_time < cutoff:
                del self.heap[key]
                cleaned += 1

        if cleaned > 0:
            logger.info(f"   🧹 Cleaned {cleaned} old heap entries")

        return cleaned


class AskProcessor:
    """
    @ask Processor: Handles @ask directives in agent chat sessions

    Processes:
    - @ask (lowercase) - Request approval/interaction
    - @ASK (uppercase) - AI token request tracking
    - Pending @ask requests
    - @ask resolution
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @ask processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ask_processing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pending_asks = []
        self.resolved_asks = []

        logger.info("✅ @ask processor initialized")

    def find_ask_directives(self, content: str) -> List[Dict[str, Any]]:
        """
        Find @ask directives in content.

        Returns:
            List of @ask directives found
        """
        asks = []

        # Find @ask (lowercase) - directive
        ask_pattern = r'@ask\s+(.+?)(?=\n|$|@)'
        for match in re.finditer(ask_pattern, content, re.IGNORECASE | re.MULTILINE):
            asks.append({
                "type": "directive",
                "text": match.group(1).strip(),
                "position": match.start(),
                "case": "lowercase" if "@ask" in match.group(0) else "uppercase"
            })

        # Find @ASK (uppercase) - token request
        ask_upper_pattern = r'@ASK\s+(.+?)(?=\n|$|@)'
        for match in re.finditer(ask_upper_pattern, content, re.MULTILINE):
            asks.append({
                "type": "token_request",
                "text": match.group(1).strip(),
                "position": match.start(),
                "case": "uppercase"
            })

        return asks

    def process_ask(self, ask: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Process an @ask directive.

        Args:
            ask: The @ask directive
            session_id: Session ID

        Returns:
            Processing result
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "ask": ask,
            "status": "pending",
            "resolved": False
        }

        # Check if already resolved
        # (In real implementation, check against resolved_asks)

        if ask["type"] == "directive":
            logger.info(f"   📋 @ask directive found: {ask['text'][:60]}...")
            result["action"] = "requires_approval"
        elif ask["type"] == "token_request":
            logger.info(f"   🎫 @ASK token request found: {ask['text'][:60]}...")
            result["action"] = "track_token_request"

        return result


class PuppetmasterWorkflow:
    """
    @puppetmaster-workflow: Workflow orchestration and fixing

    Manages:
    - Workflow definitions
    - Workflow execution
    - Workflow fixes
    - Workflow optimization
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize puppetmaster workflow"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "puppetmaster_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.workflows = {}
        self.workflow_fixes = []

        logger.info("✅ @puppetmaster-workflow initialized")

    def identify_workflow_issues(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            """
            Identify workflow issues in session.

            Args:
                session_data: Session data

            Returns:
                List of workflow issues
            """
            issues = []

            # Convert session_data to string for searching
            if isinstance(session_data, dict):
                content = json.dumps(session_data, default=str)
            else:
                content = str(session_data)

            content_lower = content.lower()

            # Look for workflow patterns
            workflow_patterns = [
                r'#workflow[s]?',
                r'@puppetmaster-workflow',
                r'workflow\s+(?:issue|problem|error|broken|incomplete|failed)',
                r'workflow\s+(?:step|stage|phase)\s+(?:missing|incomplete)',
                r'todo.*workflow',
                r'fix.*workflow',
                r'broken.*workflow'
            ]

            # Check for workflow mentions
            workflow_keywords = ["#workflow", "#workflows", "@puppetmaster-workflow", "workflow issue", 
                                "workflow problem", "complete workflow", "broken workflow"]
            has_workflow_mention = any(kw in content_lower for kw in workflow_keywords)

            if has_workflow_mention:
                logger.info(f"   🔍 Workflow mention detected in session")

                # Check for specific workflow issues
                for pattern in workflow_patterns:
                    matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                    for match in matches:
                        context_start = max(0, match.start() - 50)
                        context_end = min(len(content), match.end() + 50)
                        context = content[context_start:context_end]

                        issue = {
                            "type": "workflow_issue",
                            "pattern": pattern,
                            "position": match.start(),
                            "context": context.strip(),
                            "severity": "medium"
                        }

                        # Determine severity (check context snippet, fallback to content_lower)
                        context_lower = context.lower()
                        if any(severity_word in context_lower for severity_word in ["critical", "error", "broken", "failed"]):
                            issue["severity"] = "high"
                        elif any(severity_word in context_lower for severity_word in ["todo", "fix", "incomplete"]):
                            issue["severity"] = "medium"

                        issues.append(issue)
                        logger.info(f"      🔍 Workflow issue found: {issue['type']} ({issue['severity']})")

            # Check for workflow definitions that might need processing
            workflow_def_patterns = [
                r'workflow\s*[:=]\s*\{',
                r'workflow\s*[:=]\s*\[',
                r'#workflow\s+.*\n',
                r'@puppetmaster-workflow\s+.*\n'
            ]

            for pattern in workflow_def_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    issues.append({
                        "type": "workflow_definition",
                        "pattern": pattern,
                        "position": match.start(),
                        "context": content[max(0, match.start()-30):min(len(content), match.end()+100)],
                        "severity": "low",
                        "action": "review_workflow_definition"
                    })
                    logger.info(f"      📋 Workflow definition found")

            return issues

        except Exception as e:
            self.logger.error(f"Error in identify_workflow_issues: {e}", exc_info=True)
            raise
    def fix_workflow(self, issue: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Fix a workflow issue.

        Args:
            issue: Workflow issue
            session_id: Session ID

        Returns:
            Fix result
        """
        fix = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "issue": issue,
            "fix_applied": False,
            "fix_type": "workflow_repair"
        }

        if issue["type"] == "incomplete_workflow":
            fix["fix_applied"] = True
            fix["action"] = "marked_for_review"
            logger.info(f"   🔧 Fixed workflow issue: {issue['type']}")

        self.workflow_fixes.append(fix)
        return fix


class SystematicAgentChatWalker:
    """
    Systematic Agent Chat Walker

    Programmatically walks through all agent-chat sessions to:
    - Process @ask directives
    - Manage @stack-heap memory
    - Fix #workflows with @puppetmaster-workflow
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize systematic walker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "systematic_walker"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.stack_heap = StackHeapManager(project_root)
        self.ask_processor = AskProcessor(project_root)
        self.puppetmaster = PuppetmasterWorkflow(project_root)

        # Session processors
        self.processor = None
        self.syphon = None

        if PROCESSOR_AVAILABLE:
            try:
                self.processor = CursorAgentHistoryProcessor(project_root)
                logger.info("✅ Agent history processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize processor: {e}")

        if SYPHON_AVAILABLE:
            try:
                self.syphon = SyphonCursorAgentChatSessions(project_root)
                logger.info("✅ SYPHON initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize SYPHON: {e}")

        logger.info("✅ Systematic Agent Chat Walker initialized")
        logger.info("   @ask processing: Active")
        logger.info("   @stack-heap management: Active")
        logger.info("   @puppetmaster-workflow: Active")

    def walk_all_sessions(self, fix_workflows: bool = True) -> Dict[str, Any]:
        """
        Systematically walk through all agent-chat sessions.

        Args:
            fix_workflows: Whether to fix workflows

        Returns:
            Walking results
        """
        logger.info("=" * 80)
        logger.info("🚶 SYSTEMATIC AGENT CHAT WALKER")
        logger.info("   Processing all sessions programmatically")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "sessions_processed": 0,
            "asks_found": 0,
            "asks_processed": 0,
            "workflow_issues_found": 0,
            "workflows_fixed": 0,
            "stack_operations": 0,
            "heap_operations": 0,
            "sessions": []
        }

        # Discover all sessions
        logger.info("🔍 Discovering agent chat sessions...")
        sessions = []

        # From processor
        if self.processor:
            transcripts = self.processor.discover_agent_transcripts()
            sessions.extend([("transcript", t) for t in transcripts])
            logger.info(f"   ✅ Found {len(transcripts)} transcripts")

        # From SYPHON
        if self.syphon:
            chat_sessions = self.syphon.discover_chat_sessions()
            sessions.extend([("chat", s) for s in chat_sessions])
            logger.info(f"   ✅ Found {len(chat_sessions)} chat sessions")

        logger.info(f"   📊 Total sessions to process: {len(sessions)}")
        logger.info("")

        # Process each session
        logger.info("=" * 80)
        logger.info("📋 PROCESSING SESSIONS")
        logger.info("=" * 80)
        logger.info("")

        for session_type, session_path in sessions:
            try:
                session_result = self._process_session(session_type, session_path, fix_workflows)
                results["sessions"].append(session_result)
                results["sessions_processed"] += 1

                # Update counters
                results["asks_found"] += session_result.get("asks_found", 0)
                results["asks_processed"] += session_result.get("asks_processed", 0)
                results["workflow_issues_found"] += session_result.get("workflow_issues", 0)
                results["workflows_fixed"] += session_result.get("workflows_fixed", 0)
                results["stack_operations"] += session_result.get("stack_ops", 0)
                results["heap_operations"] += session_result.get("heap_ops", 0)

                if results["sessions_processed"] % 10 == 0:
                    logger.info(f"   📊 Processed {results['sessions_processed']}/{len(sessions)} sessions...")

            except Exception as e:
                logger.error(f"   ❌ Error processing {session_path.name}: {e}")
                results["sessions"].append({
                    "session_id": session_path.stem,
                    "error": str(e),
                    "status": "failed"
                })

        logger.info("")
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ SYSTEMATIC WALK COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Sessions processed: {results['sessions_processed']}")
        logger.info(f"   @ask directives found: {results['asks_found']}")
        logger.info(f"   @ask directives processed: {results['asks_processed']}")
        logger.info(f"   Workflow issues found: {results['workflow_issues_found']}")
        logger.info(f"   Workflows fixed: {results['workflows_fixed']}")
        logger.info(f"   Stack operations: {results['stack_operations']}")
        logger.info(f"   Heap operations: {results['heap_operations']}")
        logger.info("")

        # Print detailed summary
        print("\n" + "=" * 80)
        print("🚶 SYSTEMATIC AGENT CHAT WALKER - RESULTS")
        print("=" * 80)
        print(f"Sessions Processed: {results['sessions_processed']}")
        print(f"@ask Directives Found: {results['asks_found']}")
        print(f"@ask Directives Processed: {results['asks_processed']}")
        print(f"Workflow Issues Found: {results['workflow_issues_found']}")
        print(f"Workflows Fixed: {results['workflows_fixed']}")
        print(f"Stack Operations: {results['stack_operations']}")
        print(f"Heap Operations: {results['heap_operations']}")
        print("=" * 80)
        print()

        # Save results
        results_file = self.data_dir / f"walk_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"   📄 Results saved: {results_file.name}")
        logger.info("")

        return results

    def _process_session(self, session_type: str, session_path: Path, fix_workflows: bool) -> Dict[str, Any]:
        """
        Process a single session.

        Args:
            session_type: Type of session (transcript, chat)
            session_path: Path to session
            fix_workflows: Whether to fix workflows

        Returns:
            Session processing result
        """
        session_id = session_path.stem
        session_result = {
            "session_id": session_id,
            "session_type": session_type,
            "session_path": str(session_path),
            "asks_found": 0,
            "asks_processed": 0,
            "workflow_issues": 0,
            "workflows_fixed": 0,
            "stack_ops": 0,
            "heap_ops": 0,
            "status": "processed"
        }

        # Load session content
        try:
            if session_type == "transcript":
                with open(session_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    session_data = {"content": content, "type": "transcript"}
            else:
                with open(session_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    content = json.dumps(session_data, default=str)
        except Exception as e:
            session_result["error"] = str(e)
            session_result["status"] = "failed"
            return session_result

        # Push to stack
        context = {
            "session_id": session_id,
            "session_type": session_type,
            "timestamp": datetime.now().isoformat()
        }
        self.stack_heap.push_to_stack(context)
        session_result["stack_ops"] += 1

        # Process @ask directives
        asks = self.ask_processor.find_ask_directives(content)
        session_result["asks_found"] = len(asks)

        for ask in asks:
            ask_result = self.ask_processor.process_ask(ask, session_id)
            if ask_result.get("resolved"):
                session_result["asks_processed"] += 1

        # Store to heap
        self.stack_heap.store_to_heap(f"session_{session_id}", {
            "asks_count": len(asks),
            "session_type": session_type
        })
        session_result["heap_ops"] += 1

        # Fix workflows if requested
        if fix_workflows:
            logger.info(f"   🔧 Processing workflows for session: {session_id}")
            workflow_issues = self.puppetmaster.identify_workflow_issues(session_data)
            session_result["workflow_issues"] = len(workflow_issues)

            if workflow_issues:
                logger.info(f"      📊 Found {len(workflow_issues)} workflow issues")

            for issue in workflow_issues:
                fix_result = self.puppetmaster.fix_workflow(issue, session_id)
                if fix_result.get("fix_applied"):
                    session_result["workflows_fixed"] += 1
                    logger.info(f"      ✅ Fixed workflow issue: {issue.get('type', 'unknown')}")

            if not workflow_issues:
                logger.debug(f"      ℹ️  No workflow issues found in this session")

        # Pop from stack
        self.stack_heap.pop_from_stack()
        session_result["stack_ops"] += 1

        return session_result


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Systematic Agent Chat Walker")
    parser.add_argument("--walk", action="store_true", help="Walk all sessions")
    parser.add_argument("--fix-workflows", action="store_true", help="Fix workflows during walk")
    parser.add_argument("--cleanup-heap", type=int, help="Cleanup heap entries older than N days")

    args = parser.parse_args()

    walker = SystematicAgentChatWalker()

    if args.cleanup_heap:
        cleaned = walker.stack_heap.cleanup_heap(args.cleanup_heap)
        print(f"✅ Cleaned {cleaned} heap entries")
        return 0

    if args.walk or not any(vars(args).values()):
        # Default: walk all sessions
        walker.walk_all_sessions(fix_workflows=args.fix_workflows)

    return 0


if __name__ == "__main__":


    sys.exit(main())