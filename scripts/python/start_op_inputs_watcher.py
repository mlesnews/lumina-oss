#!/usr/bin/env python3
"""
Start JARVIS @OP @INPUTS Watcher & Learner

Quick start script to activate the watcher and integrate with master chat.

Tags: #WATCHER #LEARNER #@OP #@INPUTS @JARVIS @DOIT
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from jarvis_op_inputs_watcher_learner import JARVISOPInputsWatcherLearner
from jarvis_master_chat_session import JARVISMasterChatSession

def main():
    """Start the watcher and notify master chat"""
    print("👁️  Starting JARVIS @OP @INPUTS Watcher & Learner...")

    # Initialize watcher
    watcher = JARVISOPInputsWatcherLearner()

    # Start watching
    watcher.start_watching()

    # Notify master chat
    try:
        master_chat = JARVISMasterChatSession()
        master_chat.add_message(
            agent_id="jarvis",
            agent_name="JARVIS (CTO Superagent)",
            message="👁️  @OP @INPUTS Watcher & Learner is now active. Watching your operations and learning from your inputs. Ready to automate based on learned patterns.",
            message_type="system",
            metadata={
                "watcher": "active",
                "learning": "enabled",
                "automation": "ready"
            }
        )
        print("✅ Notified master chat session")
    except Exception as e:
        print(f"⚠️  Could not notify master chat: {e}")

    print("✅ Watcher is now active!")
    print("   - Watching operations (@op)")
    print("   - Learning from inputs (@inputs)")
    print("   - Ready to automate based on patterns")
    print("\n   Press Ctrl+C to stop")

    try:
        import time
        while watcher.watching:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watcher...")
        watcher.stop_watching()
        print("✅ Watcher stopped")

    return 0

if __name__ == "__main__":


    sys.exit(main())