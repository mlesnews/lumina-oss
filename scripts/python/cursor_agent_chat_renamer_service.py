#!/usr/bin/env python3
"""
Cursor Agent Chat Renamer Service - Background Service

Runs as a background service to continuously rename agent chats.
Can be run as a Windows service or background task.
"""

import asyncio
import sys
from pathlib import Path

# Add scripts to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from cursor_agent_chat_renamer import CursorAgentChatRenamer


class CursorAgentRenamerService:
    """Background service for renaming agent chats"""

    def __init__(self):
        self.renamer = CursorAgentChatRenamer()
        self.running = False

    async def start(self):
        """Start the service"""
        self.running = True
        self.renamer.logger.info("🚀 Starting Cursor Agent Chat Renamer Service")
        await self.renamer.monitor_and_rename()

    def stop(self):
        """Stop the service"""
        self.running = False
        self.renamer.logger.info("🛑 Stopping service")


async def main():
    """Main entry point for service"""
    service = CursorAgentRenamerService()

    try:
        await service.start()
    except KeyboardInterrupt:
        service.stop()
    except Exception as e:
        print(f"❌ Service error: {e}")
        sys.exit(1)


if __name__ == "__main__":



    asyncio.run(main())