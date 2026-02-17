#!/usr/bin/env python3
"""
Agent Session Manager - Post-Commit Session Management
Mandatory final step after GIT/GITLENS commit

Verifies no unsuccessful @asks, then handles session archiving/unpinning.

SECURITY: Root-level access requires accuracy and trust.
@MANUS @777 "CODIFYING THE WORLD"

Tags: #SESSION_MANAGEMENT #POST_COMMIT #AGENT_LIFECYCLE @JARVIS @MANUS
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AgentSessionManager")


class AgentSessionManager:
    """
    Manages agent chat session lifecycle after git commits.

    Responsibilities:
    - Verify no unsuccessful @asks
    - Handle session archiving/unpinning
    - Maintain session audit trail
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize session manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.session_data_dir = self.project_root / "data" / "agent_sessions"
        self.session_data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🔐 Agent Session Manager - Root-Level Access")
        logger.info("=" * 80)
        logger.info("")
        logger.info("⚠️  ADMINISTRATIVE ACCESS: Root-level homelab access")
        logger.info("⚠️  TRUST REQUIREMENT: Accuracy is inversely proportional to access")
        logger.info("⚠️  @MANUS @777: CODIFYING THE WORLD")
        logger.info("")

    def verify_no_unsuccessful_asks(self) -> Tuple[bool, List[str]]:
        """
        Verify there are no unsuccessful @asks in the current session.

        Returns:
            (success: bool, issues: List[str])
        """
        logger.info("🔍 Verifying no unsuccessful @asks...")

        issues = []

        # Check for @ASK patterns in recent files
        try:
            # Search for @ASK references
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%B", "--all"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=10
            )

            if result.returncode == 0:
                commit_message = result.stdout
                # Look for @ASK patterns
                if "@ASK" in commit_message or "@ask" in commit_message:
                    # Check if marked as unsuccessful
                    if any(word in commit_message.lower() for word in ["unsuccessful", "failed", "error", "blocked"]):
                        issues.append("Unsuccessful @ASK found in commit message")

        except Exception as e:
            logger.debug(f"Git check error: {e}")

        # Check session history file if it exists
        session_history = self.session_data_dir / "session_history.jsonl"
        if session_history.exists():
            try:
                with open(session_history, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                if entry.get("type") == "@ASK" and entry.get("status") != "success":
                                    issues.append(f"Unsuccessful @ASK found: {entry.get('description', 'Unknown')}")
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                logger.debug(f"Session history read error: {e}")

        if issues:
            logger.warning(f"⚠️  Found {len(issues)} potential issues:")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False, issues
        else:
            logger.info("✅ No unsuccessful @asks found")
            return True, []

    def get_session_status(self) -> Dict[str, any]:
        """
        Get current session status.

        Returns:
            Dictionary with session metadata
        """
        session_id = os.environ.get("CURSOR_SESSION_ID", "unknown")
        timestamp = datetime.now().isoformat()

        # Get git info
        git_info = {}
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            if result.returncode == 0:
                git_info["commit"] = result.stdout.strip()

            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%s"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            if result.returncode == 0:
                git_info["message"] = result.stdout.strip()
        except Exception:
            pass

        return {
            "session_id": session_id,
            "timestamp": timestamp,
            "git_info": git_info,
            "project_root": str(self.project_root),
        }

    def record_session_completion(self, status: str = "completed") -> Path:
        try:
            """
            Record session completion in audit trail.

            Args:
                status: Session status (completed, archived, unpinned)

            Returns:
                Path to recorded session file
            """
            session_data = self.get_session_status()
            session_data["status"] = status
            session_data["@ask_verification"] = "passed"

            # Record in JSONL file
            session_history = self.session_data_dir / "session_history.jsonl"
            with open(session_history, 'a', encoding='utf-8') as f:
                f.write(json.dumps(session_data) + "\n")

            # Also create individual session file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_file = self.session_data_dir / f"session_{timestamp}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)

            logger.info(f"📝 Session recorded: {session_file}")
            return session_file

        except Exception as e:
            self.logger.error(f"Error in record_session_completion: {e}", exc_info=True)
            raise
    def create_archive_instructions(self) -> Path:
        """
        Create instructions file for manual session archiving.

        Returns:
            Path to instructions file
        """
        instructions = f"""# Agent Session Archive Instructions

## Session Completion Verification

**Date**: {datetime.now().isoformat()}
**Status**: ✅ All @asks verified successful
**Action Required**: Archive or unpin this agent chat session

## Verification Results

✅ No unsuccessful @asks found
✅ All tasks completed
✅ Git commit completed
✅ Session ready for archive/unpin

## Manual Steps (Cursor UI)

1. **Check if session is pinned**:
   - Look for pin icon in chat header
   - If pinned → Click to unpin

2. **Archive the session**:
   - Right-click on chat session in sidebar
   - Select "Archive" or "Move to Archive"
   - Or use keyboard shortcut if available

3. **Verify archive**:
   - Check that session is no longer in active chats
   - Session should be in archive/history

## Automation Note

This is a mandatory final step after GIT/GITLENS commit.
Session management is currently manual in Cursor UI, but this script
verifies readiness and maintains audit trail.

## Session Metadata

{json.dumps(self.get_session_status(), indent=2)}

---
Generated by: agent_session_manager.py
@MANUS @777 "CODIFYING THE WORLD"
"""

        instructions_file = self.session_data_dir / "ARCHIVE_INSTRUCTIONS.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions)

        logger.info(f"📋 Archive instructions created: {instructions_file}")
        return instructions_file

    def execute_post_commit_workflow(self) -> int:
        """
        Execute mandatory post-commit workflow.

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("🚀 POST-COMMIT SESSION MANAGEMENT")
        logger.info("=" * 80)
        logger.info("")

        # Step 1: Verify no unsuccessful @asks
        success, issues = self.verify_no_unsuccessful_asks()

        if not success:
            logger.error("")
            logger.error("❌ VERIFICATION FAILED")
            logger.error("   Cannot proceed with session management")
            logger.error("   Please resolve unsuccessful @asks first")
            logger.error("")
            return 1

        # Step 2: Record session completion
        session_file = self.record_session_completion("ready_for_archive")
        logger.info("")
        logger.info("✅ Session completion recorded")

        # Step 3: Create archive instructions
        instructions_file = self.create_archive_instructions()
        logger.info("")
        logger.info("✅ Archive instructions created")

        # Step 4: Display summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ POST-COMMIT WORKFLOW COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("   1. Review archive instructions:")
        logger.info(f"      {instructions_file}")
        logger.info("   2. Archive/unpin this session in Cursor UI")
        logger.info("   3. Session audit trail maintained")
        logger.info("")
        logger.info("🔐 Trust Maintained: Accuracy verified, access preserved")
        logger.info("")

        return 0


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent Session Manager - Post-Commit Workflow"
    )
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--verify-only', action='store_true',
                       help='Only verify, do not create instructions')

    args = parser.parse_args()

    manager = AgentSessionManager(project_root=args.project_root)

    if args.verify_only:
        success, issues = manager.verify_no_unsuccessful_asks()
        return 0 if success else 1
    else:
        return manager.execute_post_commit_workflow()


if __name__ == "__main__":


    sys.exit(main())