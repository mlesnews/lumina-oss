#!/usr/bin/env python3
"""
JARVIS Resume Session with @doit

Resumes a previous agent chat session in the same state and immediately
begins work with "@doit" command.

Features:
- Loads previous session state
- Restores conversation context
- Immediately executes "@doit" to begin work
- No manual intervention needed
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_fulltime_super_agent import get_jarvis_fulltime
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    print("⚠️  JARVIS not available")

try:
    from jarvis_use_mapped_shortcuts import JARVISShortcutExecutor
    SHORTCUTS_AVAILABLE = True
except ImportError:
    SHORTCUTS_AVAILABLE = False


class JARVISSessionResumer:
    """Resume JARVIS session with @doit"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.sessions_dir = project_root / "data" / "r5_living_matrix" / "sessions"
        self.resumed_dir = project_root / "data" / "resumed_sessions"
        self.resumed_dir.mkdir(parents=True, exist_ok=True)

        if JARVIS_AVAILABLE:
            self.jarvis = get_jarvis_fulltime()
        else:
            self.jarvis = None

        if SHORTCUTS_AVAILABLE:
            self.shortcuts = JARVISShortcutExecutor(project_root)
        else:
            self.shortcuts = None

    def find_session(self, session_id: Optional[str] = None, 
                     latest: bool = True) -> Optional[Dict[str, Any]]:
        """Find a session to resume"""
        if not self.sessions_dir.exists():
            print(f"❌ Sessions directory not found: {self.sessions_dir}")
            return None

        # Find session files
        if session_id:
            # Find specific session
            pattern = f"*{session_id}*.json"
            session_files = list(self.sessions_dir.glob(pattern))
        else:
            # Find all cursor chat sessions
            session_files = list(self.sessions_dir.glob("cursor_chat_json*.json"))

        if not session_files:
            print(f"❌ No sessions found")
            return None

        # Sort by modification time
        if latest:
            session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        # Load the session
        session_file = session_files[0]
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            session_data["_file_path"] = str(session_file)
            return session_data
        except Exception as e:
            print(f"❌ Failed to load session: {e}")
            return None

    def restore_session_state(self, session_data: Dict[str, Any]) -> str:
        """Restore session state and return conversation ID"""
        if not self.jarvis:
            print("❌ JARVIS not available")
            return None

        # Extract session info
        session_id = session_data.get("session_id", f"resumed_{int(time.time())}")
        messages = session_data.get("messages", [])

        print(f"🔄 Restoring session: {session_id}")
        print(f"   Messages: {len(messages)}")

        # Start new conversation (or resume existing)
        conv_id = self.jarvis.start_voice_conversation()

        # Restore conversation history
        if messages:
            print("   📝 Restoring conversation history...")
            for msg in messages:
                content = msg.get("content", msg.get("message", ""))
                role = msg.get("role", msg.get("speaker", "human"))

                if content:
                    self.jarvis.speak(conv_id, content, speaker=role)

        print(f"✅ Session restored: {conv_id}")
        return conv_id

    def execute_doit(self, conv_id: str, context: Optional[str] = None) -> bool:
        """Execute @doit to begin work immediately"""
        if not self.jarvis:
            return False

        print()
        print("🚀 Executing @doit - JARVIS beginning work immediately...")
        print()

        # Build @doit command with context
        doit_command = "@doit"
        if context:
            doit_command = f"@doit {context}"

        # Send @doit command
        self.jarvis.speak(conv_id, doit_command, speaker="human")

        # Get response
        time.sleep(1)  # Wait for processing
        history = self.jarvis.get_conversation_history(conv_id)

        if history:
            for turn in reversed(history):
                if turn.get('speaker') == 'jarvis':
                    response = turn.get('message', '')
                    print(f"🤖 JARVIS: {response}")
                    print()
                    break

        print("✅ @doit executed - JARVIS is working!")
        return True

    def resume_and_doit(self, session_id: Optional[str] = None,
                           context: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Resume session and immediately execute @doit"""
            print("="*80)
            print("🔄 JARVIS Resume Session with @doit")
            print("="*80)
            print()

            # Find session
            print("🔍 Finding session...")
            session_data = self.find_session(session_id)

            if not session_data:
                return {"success": False, "error": "Session not found"}

            # Restore session state
            print()
            print("📥 Restoring session state...")
            conv_id = self.restore_session_state(session_data)

            if not conv_id:
                return {"success": False, "error": "Failed to restore session"}

            # Execute @doit
            print()
            doit_success = self.execute_doit(conv_id, context)

            # Save resumed session info
            resumed_info = {
                "original_session_id": session_data.get("session_id"),
                "resumed_conv_id": conv_id,
                "resumed_at": datetime.now().isoformat(),
                "doit_executed": doit_success,
                "message_count": len(session_data.get("messages", []))
            }

            output_file = self.resumed_dir / f"resumed_{session_data.get('session_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(resumed_info, f, indent=2)

            print()
            print("="*80)
            print("✅ SESSION RESUMED AND @DOIT EXECUTED")
            print("="*80)
            print(f"   Conversation ID: {conv_id}")
            print(f"   Resume info saved: {output_file.name}")
            print()

            return {
                "success": True,
                "conversation_id": conv_id,
                "original_session_id": session_data.get("session_id"),
                "resumed_at": datetime.now().isoformat(),
                "doit_executed": doit_success
            }


        except Exception as e:
            self.logger.error(f"Error in resume_and_doit: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Resume JARVIS session and execute @doit immediately"
    )
    parser.add_argument('--session-id', type=str, help='Specific session ID to resume')
    parser.add_argument('--latest', action='store_true', default=True,
                       help='Resume latest session (default)')
    parser.add_argument('--context', type=str, help='Additional context for @doit')

    args = parser.parse_args()

    resumer = JARVISSessionResumer()

    result = resumer.resume_and_doit(
        session_id=args.session_id,
        context=args.context
    )

    if result.get("success"):
        print("✅ Success!")
        print(f"   Conversation ID: {result.get('conversation_id')}")
        print(f"   @doit executed: {result.get('doit_executed')}")
    else:
        print(f"❌ Failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":


    main()