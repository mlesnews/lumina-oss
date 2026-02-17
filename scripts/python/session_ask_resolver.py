#!/usr/bin/env python3
"""
Session Ask Resolver - Verify, Validate, and Archive

Checks for unresolved asks at end of session.
If verified, validated, and verified again by upper management,
then pins/archives/renames the chat in Cursor IDE.

Workflow:
1. Extract all asks from session
2. Verify completion
3. Validate with JARVIS
4. Verify with MARVIN
5. If approved: Pin, Archive, Rename chat
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Import verification systems
from dual_todo_system import DualTodoSystem
from todo_verification_workflow import TodoVerificationWorkflow


@dataclass
class SessionAsk:
    """Session ask/request"""
    ask_id: str
    ask_text: str
    resolved: bool = False
    verification_status: str = "pending"  # pending, verified, validated, approved
    jarvis_review: Optional[Dict] = None
    marvin_review: Optional[Dict] = None
    completion_evidence: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SessionAskResolver:
    """
    Session Ask Resolver

    Extracts asks from session, verifies completion,
    validates with upper management, then archives chat.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.project_root = Path(__file__).parent.parent.parent
        self.session_id = session_id or f"session_{int(time.time())}"

        self.dual_system = DualTodoSystem()
        self.verification_workflow = TodoVerificationWorkflow()

        self.asks: List[SessionAsk] = []

        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("SessionAskResolver")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - ✅ %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def extract_asks_from_session(self, session_context: Dict[str, Any]) -> List[SessionAsk]:
        """
        Extract asks/requests from session context

        Looks for:
        - @ask patterns
        - User requests
        - TODO items
        - Action items
        """
        asks = []

        # Extract from session messages
        messages = session_context.get('messages', [])

        for i, msg in enumerate(messages):
            content = msg.get('content', '')

            # Look for @ask patterns
            if '@ask' in content.lower() or 'ask' in content.lower():
                # Extract ask text
                ask_text = self._extract_ask_text(content)
                if ask_text:
                    asks.append(SessionAsk(
                        ask_id=f"ask_{self.session_id}_{i}",
                        ask_text=ask_text
                    ))

        # Extract from todos
        master_todos = self.dual_system.get_master_todos()
        for todo in master_todos:
            if todo.status.value == "complete":
                asks.append(SessionAsk(
                    ask_id=f"todo_{todo.id}",
                    ask_text=todo.title,
                    resolved=True,
                    completion_evidence=[f"Todo marked complete: {todo.title}"]
                ))

        self.asks = asks
        return asks

    def _extract_ask_text(self, content: str) -> Optional[str]:
        """Extract ask text from content"""
        import re

        # Pattern 1: @ask followed by text
        pattern1 = r'@ask[:\s]+([^@\n]+?)(?=@|\n|$)'
        match = re.search(pattern1, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Pattern 2: "I want" or "please"
        pattern2 = r'(?:i want|please|can you|could you)[:\s]+([^.\n]+)'
        match = re.search(pattern2, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return None

    async def verify_all_asks(self) -> Dict[str, Any]:
        """
        Verify all asks are resolved

        Returns verification status
        """
        unresolved = []
        resolved = []

        for ask in self.asks:
            if ask.resolved:
                resolved.append(ask)
            else:
                unresolved.append(ask)

        return {
            'total': len(self.asks),
            'resolved': len(resolved),
            'unresolved': len(unresolved),
            'unresolved_asks': [a.ask_text for a in unresolved],
            'all_resolved': len(unresolved) == 0
        }

    async def validate_with_management(self) -> Dict[str, Any]:
        """
        Validate with upper management (JARVIS/MARVIN)

        Returns validation results
        """
        validation_results = {
            'jarvis_approved': False,
            'marvin_approved': False,
            'fully_approved': False,
            'notes': []
        }

        # JARVIS systematic review
        for ask in self.asks:
            if ask.resolved:
                # Check if there's corresponding todo
                master_todos = self.dual_system.get_master_todos()
                matching_todos = [t for t in master_todos if ask.ask_text.lower() in t.title.lower()]

                if matching_todos:
                    # Verify with JARVIS
                    jarvis_result = await self.verification_workflow.jarvis_review(matching_todos[0].id)
                    ask.jarvis_review = jarvis_result

                    if jarvis_result.get('verified', False):
                        ask.verification_status = "verified"
                        validation_results['jarvis_approved'] = True

        # MARVIN philosophical review
        for ask in self.asks:
            if ask.verification_status == "verified":
                matching_todos = [t for t in self.dual_system.get_master_todos() 
                                if ask.ask_text.lower() in t.title.lower()]

                if matching_todos:
                    marvin_result = await self.verification_workflow.marvin_review(matching_todos[0].id)
                    ask.marvin_review = marvin_result

                    if marvin_result.get('verified', False):
                        ask.verification_status = "validated"
                        validation_results['marvin_approved'] = True

        # Final approval
        all_validated = all(a.verification_status == "validated" for a in self.asks if a.resolved)
        validation_results['fully_approved'] = all_validated

        return validation_results

    async def archive_chat_if_approved(self, validation_results: Dict[str, Any]) -> bool:
        """
        Archive chat if all asks are resolved and approved

        Actions:
        1. Pin the chat
        2. Archive it
        3. Rename with final status
        """
        if not validation_results.get('fully_approved', False):
            self.logger.info("⚠️ Not approved for archiving - some asks unresolved or unverified")
            return False

        self.logger.info("✅ All asks resolved and approved - proceeding with archive")

        # Import cursor chat manager
        try:
            from cursor_chat_manager import CursorChatManager

            manager = CursorChatManager()

            # Find current session chat file
            # In real implementation, would identify from session context
            session_summary = f"Session_{self.session_id}_Verified"

            self.logger.info("📌 Pinning chat...")
            self.logger.info("📦 Archiving chat...")
            self.logger.info("✏️ Renaming chat with final status...")

            # Get all chat files and find the most recent one for this session
            chat_files = [f for f in manager.history_dir.glob("*.json") 
                         if f.stat().st_size > 1000]

            if chat_files:
                # Use most recent chat file
                most_recent = max(chat_files, key=lambda p: p.stat().st_mtime)

                # Complete workflow: Pin, Archive, Rename
                manager.pin_archive_rename_chat(most_recent, session_summary)

                self.logger.info(f"✅ Chat archived: {most_recent.name}")
                return True

            self.logger.warning("⚠️ No chat files found to archive")
            return False

        except ImportError:
            self.logger.warning("⚠️ Cursor chat manager not available")
            return False

    async def resolve_session(self, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete session resolution workflow

        1. Extract asks
        2. Verify completion
        3. Validate with management
        4. Archive if approved
        """
        self.logger.info("🔍 Starting session ask resolution...")

        # Step 1: Extract asks
        asks = self.extract_asks_from_session(session_context)
        self.logger.info(f"📋 Found {len(asks)} asks in session")

        # Step 2: Verify
        verification = await self.verify_all_asks()
        self.logger.info(f"✅ Verification: {verification['resolved']}/{verification['total']} resolved")

        if verification['unresolved'] > 0:
            self.logger.warning(f"⚠️ {verification['unresolved']} unresolved asks:")
            for ask in verification['unresolved_asks']:
                self.logger.warning(f"   - {ask}")

        # Step 3: Validate with management
        if verification['all_resolved']:
            validation = await self.validate_with_management()
            self.logger.info(f"🔍 Validation: JARVIS={validation['jarvis_approved']}, MARVIN={validation['marvin_approved']}")

            # Step 4: Archive if approved
            if validation['fully_approved']:
                archived = await self.archive_chat_if_approved(validation)
                if archived:
                    self.logger.info("✅ Session archived successfully")

        return {
            'session_id': self.session_id,
            'asks': len(asks),
            'verification': verification,
            'validation': validation if verification['all_resolved'] else None,
            'archived': archived if verification['all_resolved'] else False
        }


async def main():
    """Main execution - check session asks"""
    resolver = SessionAskResolver()

    # Create session context (in real use, this would come from Cursor IDE)
    session_context = {
        'messages': [
            {'content': 'Create trailer videos for pilot episode'},
            {'content': 'SYPHON video/audio breakdown with @ask-requested'},
            {'content': 'Git/GitLens integration marked as complete'},
            {'content': 'Master to-do list system'},
            {'content': 'Cursor agent chat history renamer'}
        ]
    }

    result = await resolver.resolve_session(session_context)

    print("\n📋 Session Ask Resolution Report")
    print("=" * 80)
    print(f"Session ID: {result['session_id']}")
    print(f"Total Asks: {result['asks']}")
    print(f"Resolved: {result['verification']['resolved']}/{result['asks']}")
    print(f"Unresolved: {result['verification']['unresolved']}")

    if result['verification']['all_resolved']:
        print("\n✅ All asks resolved!")
        if result.get('validation'):
            print(f"   JARVIS Approved: {result['validation']['jarvis_approved']}")
            print(f"   MARVIN Approved: {result['validation']['marvin_approved']}")
            print(f"   Fully Approved: {result['validation']['fully_approved']}")
    else:
        print("\n⚠️ Unresolved asks:")
        for ask in result['verification']['unresolved_asks']:
            print(f"   - {ask}")


if __name__ == "__main__":



    asyncio.run(main())