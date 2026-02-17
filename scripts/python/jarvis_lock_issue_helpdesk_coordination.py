#!/usr/bin/env python3
"""
JARVIS Lock Issue - Helpdesk & Company-Wide Coordination
@RR (Roast & Repair) for persistent lock issue with full coordination

Features:
- Helpdesk ticket creation
- Company-wide coordination
- SYPHON intelligence extraction
- Agent chat session history tracking
- Full workflow from inception to archival

@JARVIS @RR @HELPDESK @SUPPORT @SYPHON "THIS IS THE WAY" - MANDO
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Helpdesk integration
from scripts.python.jarvis_helpdesk_integration import JARVISHelpdeskIntegration

# SYPHON integration
try:
    from scripts.python.syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False

# Agent collaboration
try:
    from src.cfservices.services.jarvis_core.agent_collaboration import AgentCollaborationSystem
    AGENT_COLLAB_AVAILABLE = True
except ImportError:
    AGENT_COLLAB_AVAILABLE = False

# Armoury Crate integration
from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLockHelpdesk")


@dataclass
class ChatSessionHistory:
    """Agent chat session history from inception to archival"""
    session_id: str
    inception_time: datetime
    agents_involved: List[str]
    messages: List[Dict[str, Any]] = field(default_factory=list)
    issues_tracked: List[str] = field(default_factory=list)
    resolutions: List[str] = field(default_factory=list)
    archived: bool = False
    archive_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LockIssueHelpdeskCoordination:
    """
    Lock Issue Helpdesk & Company-Wide Coordination

    "THIS IS THE WAY." - MANDO

    Coordinates:
    - Helpdesk ticket creation
    - Company-wide agent coordination
    - SYPHON intelligence extraction
    - Agent chat session history
    - Full workflow from inception to archival
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize coordination system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Helpdesk integration
        try:
            self.helpdesk = JARVISHelpdeskIntegration(project_root=self.project_root)
            logger.info("✅ Helpdesk integration initialized")
        except Exception as e:
            logger.warning(f"⚠️  Helpdesk not available: {e}")
            self.helpdesk = None

        # SYPHON integration
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(self.project_root)
                logger.info("✅ SYPHON system initialized - 'This is the way.'")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Agent collaboration
        if AGENT_COLLAB_AVAILABLE:
            try:
                self.agent_collab = AgentCollaborationSystem(project_root=self.project_root)
                logger.info("✅ Agent collaboration system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Agent collaboration not available: {e}")
                self.agent_collab = None
        else:
            self.agent_collab = None

        # Armoury Crate integration
        self.armoury_crate = create_armoury_crate_integration()

        # Session history storage
        self.sessions_dir = self.project_root / "data" / "agent_chat_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir = self.sessions_dir / "archived"
        self.archive_dir.mkdir(exist_ok=True)

        # Active sessions
        self.active_sessions: Dict[str, ChatSessionHistory] = {}

        logger.info("✅ Lock Issue Helpdesk Coordination initialized")
        logger.info("   'This is the way.' - MANDO")

    async def create_helpdesk_ticket_for_lock_issue(self) -> Dict[str, Any]:
        """Create helpdesk ticket for persistent lock issue"""
        logger.info("🎫 Creating helpdesk ticket for persistent lock issue...")

        issue_description = """
        PERSISTENT LOCK ISSUE - @RR REQUIRED

        Problem: FN and Windows key locks persist despite multiple attempts

        Symptoms:
        - Lock symbols visible on FN and WINKEY buttons
        - Multiple unlock attempts failed
        - Registry modifications attempted
        - UI automation attempted
        - Long press methods attempted

        Impact:
        - fn+F4 keyboard shortcut may not work
        - Function keys may not work as expected
        - User experience degraded

        Priority: HIGH
        Category: Hardware/Keyboard
        """

        # Use SYPHON to extract intelligence
        if self.syphon:
            actionable_items = self.syphon._extract_actionable_items(issue_description)
            tasks = self.syphon._extract_tasks(issue_description, "Lock Issue")
            logger.info(f"📊 SYPHON extracted {len(actionable_items)} actionable items, {len(tasks)} tasks")

        # Create helpdesk ticket (using workflow execution)
        if self.helpdesk:
            try:
                # Use workflow execution to create ticket
                ticket_result = await self.helpdesk.execute_workflow_with_verification({
                    "workflow_name": "create_lock_issue_ticket",
                    "workflow_data": {
                        "title": "Persistent FN and Windows Key Lock Issue",
                        "description": issue_description,
                        "priority": "high",
                        "category": "hardware",
                        "tags": ["@RR", "@LOCK", "@FN", "@WINKEY", "@SYPHON"]
                    }
                })

                if ticket_result.get("success"):
                    logger.info(f"✅ Helpdesk ticket workflow executed")
                    return {"success": True, "ticket_id": "workflow_executed", "result": ticket_result}
                else:
                    logger.warning(f"⚠️  Helpdesk workflow had issues: {ticket_result.get('message', 'Unknown')}")
                    return {"success": False, "error": ticket_result.get('message', 'Unknown')}
            except Exception as e:
                logger.error(f"❌ Helpdesk ticket creation failed: {e}")
                return {"success": False, "error": str(e)}
        else:
            logger.warning("⚠️  Helpdesk not available")
            return {"success": False, "error": "Helpdesk not available"}

    def start_chat_session(self, session_id: Optional[str] = None, agents: Optional[List[str]] = None) -> ChatSessionHistory:
        """Start a new agent chat session"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = ChatSessionHistory(
            session_id=session_id,
            inception_time=datetime.now(),
            agents_involved=agents or ["JARVIS", "SYPHON", "HELPDESK"]
        )

        self.active_sessions[session_id] = session

        logger.info(f"🚀 Chat session started: {session_id}")
        logger.info(f"   Agents: {', '.join(session.agents_involved)}")
        logger.info(f"   Inception: {session.inception_time.isoformat()}")

        return session

    def add_message_to_session(
        self,
        session_id: str,
        agent: str,
        message: str,
        message_type: str = "chat"
    ):
        """Add message to chat session"""
        if session_id not in self.active_sessions:
            logger.warning(f"⚠️  Session {session_id} not found, creating new session")
            self.start_chat_session(session_id)

        session = self.active_sessions[session_id]

        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message": message,
            "type": message_type
        }

        session.messages.append(message_entry)

        logger.debug(f"💬 Message added to {session_id} from {agent}")

    def track_issue_in_session(self, session_id: str, issue: str):
        """Track an issue in the session"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        if issue not in session.issues_tracked:
            session.issues_tracked.append(issue)
            logger.info(f"📋 Issue tracked in {session_id}: {issue}")

    def add_resolution_to_session(self, session_id: str, resolution: str):
        """Add resolution to session"""
        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]
        session.resolutions.append(resolution)
        logger.info(f"✅ Resolution added to {session_id}: {resolution}")

    def archive_session(self, session_id: str) -> bool:
        """Archive a chat session"""
        if session_id not in self.active_sessions:
            logger.warning(f"⚠️  Session {session_id} not found")
            return False

        session = self.active_sessions[session_id]
        session.archived = True
        session.archive_time = datetime.now()

        # Save to archive
        try:
            archive_file = self.archive_dir / f"{session_id}_archived.json"
            with open(archive_file, "w", encoding="utf-8") as f:
                # Convert datetime to ISO string for JSON
                session_dict = asdict(session)
                session_dict["inception_time"] = session.inception_time.isoformat()
                if session.archive_time:
                    session_dict["archive_time"] = session.archive_time.isoformat()
                json.dump(session_dict, f, indent=2, ensure_ascii=False)

            # Remove from active sessions
            del self.active_sessions[session_id]

            logger.info(f"📦 Session archived: {session_id}")
            logger.info(f"   Duration: {(session.archive_time - session.inception_time).total_seconds():.1f}s")
            logger.info(f"   Messages: {len(session.messages)}")
            logger.info(f"   Issues: {len(session.issues_tracked)}")
            logger.info(f"   Resolutions: {len(session.resolutions)}")

            return True
        except Exception as e:
            logger.error(f"❌ Archive failed: {e}")
            return False

    def save_session(self, session_id: str) -> bool:
        """Save session to disk (before archival)"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]

        try:
            session_file = self.sessions_dir / f"{session_id}.json"
            session_dict = asdict(session)
            session_dict["inception_time"] = session.inception_time.isoformat()
            if session.archive_time:
                session_dict["archive_time"] = session.archive_time.isoformat()

            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Session saved: {session_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Save failed: {e}")
            return False

    async def coordinate_lock_issue_resolution(self) -> Dict[str, Any]:
        """
        Coordinate lock issue resolution with full workflow

        "THIS IS THE WAY." - MANDO
        """
        logger.info("=" * 70)
        logger.info("🎯 LOCK ISSUE COORDINATION - 'THIS IS THE WAY.' - MANDO")
        logger.info("=" * 70)

        # Start chat session
        session = self.start_chat_session(
            agents=["JARVIS", "SYPHON", "HELPDESK", "ARMOURY_CRATE", "DIAGNOSTICS"]
        )

        # Add initial message
        self.add_message_to_session(
            session.session_id,
            "JARVIS",
            "Lock issue coordination initiated. 'This is the way.' - MANDO",
            "system"
        )

        # Track issue
        self.track_issue_in_session(session.session_id, "Persistent FN and Windows Key Locks")

        # Step 1: Create helpdesk ticket
        self.add_message_to_session(
            session.session_id,
            "HELPDESK",
            "Creating helpdesk ticket for lock issue..."
        )
        ticket = await self.create_helpdesk_ticket_for_lock_issue()

        if ticket.get("success"):
            self.add_message_to_session(
                session.session_id,
                "HELPDESK",
                f"✅ Ticket created: {ticket.get('ticket_id', 'Unknown')}"
            )
        else:
            self.add_message_to_session(
                session.session_id,
                "HELPDESK",
                f"⚠️  Ticket creation failed: {ticket.get('error', 'Unknown')}"
            )

        # Step 2: SYPHON intelligence extraction
        if self.syphon:
            self.add_message_to_session(
                session.session_id,
                "SYPHON",
                "Extracting intelligence about lock issue..."
            )

            issue_text = "FN and Windows key locks persist. Multiple unlock attempts failed."
            actionable = self.syphon._extract_actionable_items(issue_text)
            tasks = self.syphon._extract_tasks(issue_text, "Lock Issue")

            self.add_message_to_session(
                session.session_id,
                "SYPHON",
                f"📊 Extracted {len(actionable)} actionable items, {len(tasks)} tasks"
            )

        # Step 3: Company-wide coordination
        if self.agent_collab:
            self.add_message_to_session(
                session.session_id,
                "AGENT_COLLAB",
                "Initiating company-wide coordination..."
            )

            try:
                collab_session = self.agent_collab.start_collaboration_session(
                    agent_ids=["jarvis", "syphon", "helpdesk", "diagnostics"],
                    task_description="Resolve persistent FN and Windows key lock issue",
                    oversight_level="strict"
                )

                self.add_message_to_session(
                    session.session_id,
                    "AGENT_COLLAB",
                    f"✅ Collaboration session started: {collab_session.session_id}"
                )
            except Exception as e:
                self.add_message_to_session(
                    session.session_id,
                    "AGENT_COLLAB",
                    f"⚠️  Collaboration failed: {e}"
                )

        # Step 4: Attempt lock resolution
        self.add_message_to_session(
            session.session_id,
            "ARMOURY_CRATE",
            "Attempting comprehensive lock resolution..."
        )

        # Check current lock states
        lock_result = await self.armoury_crate.process_request({
            'action': 'spy_keyboard_locks'
        })

        if lock_result.get('success'):
            lock_states = lock_result.get('lock_states', {})
            self.add_message_to_session(
                session.session_id,
                "ARMOURY_CRATE",
                f"📊 Current lock states: {json.dumps(lock_states, indent=2)}"
            )

        # Attempt unlock
        unlock_result = await self.armoury_crate.process_request({
            'action': 'repair_keyboard_control'
        })

        if unlock_result.get('success'):
            self.add_message_to_session(
                session.session_id,
                "ARMOURY_CRATE",
                "✅ Keyboard control repair attempted"
            )
            self.add_resolution_to_session(
                session.session_id,
                "Keyboard control repair executed"
            )
        else:
            self.add_message_to_session(
                session.session_id,
                "ARMOURY_CRATE",
                f"⚠️  Repair had issues: {unlock_result.get('message', 'Unknown')}"
            )

        # Step 5: Save session
        self.save_session(session.session_id)

        # Step 6: Archive session (after coordination complete)
        # Note: Don't archive immediately - keep active for monitoring
        # self.archive_session(session.session_id)

        return {
            "success": True,
            "session_id": session.session_id,
            "ticket": ticket,
            "messages_count": len(session.messages),
            "issues_tracked": session.issues_tracked,
            "resolutions": session.resolutions,
            "message": "Lock issue coordination complete. 'This is the way.' - MANDO"
        }


async def main():
    """Main coordination workflow"""
    print("=" * 70)
    print("🎯 LOCK ISSUE HELPDESK COORDINATION")
    print("   'THIS IS THE WAY.' - MANDO")
    print("=" * 70)
    print()

    coordinator = LockIssueHelpdeskCoordination()

    # Run coordination
    result = await coordinator.coordinate_lock_issue_resolution()

    print()
    print("=" * 70)
    print("✅ COORDINATION COMPLETE")
    print("=" * 70)
    print(f"Session ID: {result.get('session_id')}")
    print(f"Messages: {result.get('messages_count')}")
    print(f"Issues Tracked: {len(result.get('issues_tracked', []))}")
    print(f"Resolutions: {len(result.get('resolutions', []))}")
    print()
    print("'This is the way.' - MANDO")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())