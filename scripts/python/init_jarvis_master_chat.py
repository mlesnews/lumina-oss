#!/usr/bin/env python3
"""
Initialize JARVIS Master Chat Session

Sets up and maintains the permanently pinned master JARVIS chat session
that consolidates all agents.

Tags: #JARVIS #MASTER #CHAT #INIT #PINNED
@JARVIS @TEAM @DOIT
"""

import sys
from pathlib import Path
import json

# Add project root to sys.path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

from jarvis_master_chat_session import JARVISMasterChatSession
from lumina_logger import get_logger

logger = get_logger("InitJARVISMasterChat")


def update_cursor_settings():
    """Update Cursor IDE settings to include pinned master session"""
    cursor_settings_file = project_root / ".cursor" / "settings.json"

    if not cursor_settings_file.exists():
        logger.warning(f"⚠️  Cursor settings file not found: {cursor_settings_file}")
        return False

    try:
        # Read existing settings
        with open(cursor_settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Add pinned session configuration
        if "cursor.chat.pinnedSessions" not in settings:
            settings["cursor.chat.pinnedSessions"] = []

        # Check if master session already configured
        master_session_exists = any(
            session.get("sessionId") == "jarvis_master_chat"
            for session in settings.get("cursor.chat.pinnedSessions", [])
        )

        if not master_session_exists:
            settings["cursor.chat.pinnedSessions"].append({
                "sessionId": "jarvis_master_chat",
                "sessionName": "JARVIS Master Chat - All Agents",
                "pinned": True,
                "permanent": True,
                "autoOpen": True,
                "model": "ULTRON",
                "description": "Master JARVIS chat session consolidating all agents"
            })
            logger.info("✅ Added master session to Cursor settings")
        else:
            logger.info("ℹ️  Master session already configured in Cursor settings")

        # Set as default session
        settings["cursor.chat.defaultSession"] = "jarvis_master_chat"
        settings["cursor.chat.alwaysOpenPinned"] = True

        # Write updated settings
        with open(cursor_settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        logger.info("✅ Updated Cursor IDE settings")
        return True

    except Exception as e:
        logger.error(f"❌ Error updating Cursor settings: {e}")
        return False


def main():
    """Initialize master chat session"""
    print("\n" + "=" * 80)
    print("🚀 INITIALIZING JARVIS MASTER CHAT SESSION")
    print("=" * 80 + "\n")

    # Initialize manager
    print("📦 Initializing master chat session manager...")
    manager = JARVISMasterChatSession()
    print("✅ Manager initialized\n")

    # Consolidate all agents
    print("🔄 Consolidating all agents into master session...")
    result = manager.consolidate_all_agents()
    print(f"✅ Consolidated {result['agent_count']} agents")
    print(f"   Agents: {', '.join(result['consolidated_agents'])}")
    print()

    # Ensure pinned
    print("📌 Ensuring session is permanently pinned...")
    manager.ensure_pinned()
    print("✅ Session is permanently pinned\n")

    # Update Cursor settings
    print("⚙️  Updating Cursor IDE settings...")
    if update_cursor_settings():
        print("✅ Cursor settings updated")
        print("   ⚠️  Please restart Cursor IDE to apply pinned session")
    else:
        print("⚠️  Could not update Cursor settings automatically")
        print("   Please manually add pinned session configuration")
    print()

    # Show summary
    print("📋 Master Session Summary:")
    print("-" * 80)
    summary = manager.get_session_summary()
    print(f"Session ID: {summary['session_id']}")
    print(f"Session Name: {summary['session_name']}")
    print(f"Pinned: {summary['pinned']}")
    print(f"Permanent: {summary['permanent']}")
    print(f"Consolidated Agents: {summary['agent_count']}")
    print(f"Total Messages: {summary['message_count']}")
    print()

    print("=" * 80)
    print("✅ JARVIS MASTER CHAT SESSION INITIALIZED")
    print("=" * 80)
    print("\n📌 The master session is now permanently pinned and ready to use.")
    print("   All agent interactions will flow through this unified interface.")
    print("   Restart Cursor IDE to see the pinned session.\n")


if __name__ == "__main__":


    main()