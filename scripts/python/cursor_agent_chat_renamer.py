#!/usr/bin/env python3
"""
Cursor Agent Chat History Renamer - Dynamic Scaling with Activity Reset

Renames active Cursor IDE agent chat histories dynamically:
- Baseline: 30 minutes
- Active work: Extends to 1 hour or longer
- Activity reset: Like screensaver - resets timer on activity
- Monitors pinned and all agent chats

Location: Cursor IDE → New Agent button → Pinned agents / More (three dots)
"""

import asyncio
import json
import logging
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
# @SYPHON: Decision tree logic can be integrated here if needed
# For now, using simple activity-based logic

class CursorAgentChatRenamer:
    """
    Cursor Agent Chat History Renamer

    Dynamically renames agent chat histories based on activity:
    - Baseline interval: 30 minutes
    - Active work extends to 1+ hour
    - Activity resets timer (screensaver concept)
    """

    def __init__(self):
        # Cursor IDE storage paths (Windows)
        self.app_data = Path(os.environ.get('APPDATA', ''))
        self.local_app_data = Path(os.environ.get('LOCALAPPDATA', ''))

        # Try common Cursor storage locations
        self.cursor_paths = [
            self.local_app_data / "Cursor" / "User" / "globalStorage",
            self.app_data / "Cursor" / "User" / "globalStorage",
            Path.home() / ".cursor" / "User" / "globalStorage"
        ]

        # Setup logger first
        self.logger = self._setup_logging()

        self.chat_history_dir = None
        self._find_chat_history_dir()

        # Configuration
        self.baseline_interval = 30 * 60  # 30 minutes
        self.active_extension = 60 * 60   # 1 hour when active
        self.activity_reset_window = 20 * 60  # 20 minutes (screensaver concept)
        self.max_interval = 2 * 60 * 60  # 2 hours max

        # Tracking
        self.active_chats: Dict[str, Dict] = {}  # chat_id -> {last_activity, rename_count, original_name}
        self.activity_log: List[Tuple[str, float]] = []  # (chat_id, timestamp)

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("CursorAgentRenamer")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 💬 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _find_chat_history_dir(self):
        try:
            """Find Cursor chat history directory"""
            # Primary location: User/History (main chat history location)
            history_dir = self.app_data / "Cursor" / "User" / "History"
            if history_dir.exists():
                self.chat_history_dir = history_dir
                self.logger.info(f"✅ Found Cursor History directory: {history_dir}")
                return

            # Try globalStorage locations
            for base_path in self.cursor_paths:
                if base_path.exists():
                    # Try common chat history locations in globalStorage
                    possible_paths = [
                        base_path / "cursor.agent" / "chat_history",
                        base_path / "agent" / "chats",
                        base_path / "chat_history",
                        base_path / "agent_chats"
                    ]

                    for path in possible_paths:
                        if path.exists():
                            self.chat_history_dir = path
                            self.logger.info(f"✅ Found chat history: {path}")
                            return

            # Fallback: try to find in AppData by searching
            search_paths = [
                self.local_app_data / "Cursor",
                self.app_data / "Cursor",
                Path.home() / ".cursor"
            ]

            for search_path in search_paths:
                if search_path.exists():
                    # Search for chat-related directories
                    for root, dirs, files in os.walk(search_path):
                        if "chat" in root.lower() and "history" in root.lower():
                            self.chat_history_dir = Path(root)
                            self.logger.info(f"✅ Found chat history (searched): {self.chat_history_dir}")
                            return

        except Exception as e:
            self.logger.error(f"Error in _find_chat_history_dir: {e}", exc_info=True)
            raise
    def get_chat_files(self) -> List[Path]:
        try:
            """Get all chat history files"""
            if not self.chat_history_dir or not self.chat_history_dir.exists():
                self.logger.warning("⚠️ Chat history directory not found")
                return []

            chat_files = []

            # Look for JSON files (common format for Cursor)
            # Filter out entries.json (file edit history, not chat)
            for json_file in self.chat_history_dir.rglob("*.json"):
                if json_file.name.lower() == "entries.json":
                    continue

                # Filter by size (chats are usually >1KB)
                if json_file.stat().st_size > 1000:
                    chat_files.append(json_file)

            return chat_files

        except Exception as e:
            self.logger.error(f"Error in get_chat_files: {e}", exc_info=True)
            raise
    def detect_activity(self, chat_file: Path) -> bool:
        """
        Detect if chat is actively being used

        Checks:
        - File modification time (recent changes)
        - File size changes
        - Metadata updates
        """
        try:
            stat = chat_file.stat()
            mtime = stat.st_mtime
            size = stat.st_size

            # Check if modified in last activity window
            time_since_modify = time.time() - mtime

            if time_since_modify < self.activity_reset_window:
                return True

            # Check if chat_id is in recent activity log
            chat_id = self._get_chat_id(chat_file)
            if chat_id in self.active_chats:
                last_activity = self.active_chats[chat_id].get('last_activity', 0)
                if time.time() - last_activity < self.activity_reset_window:
                    return True

            return False

        except Exception as e:
            self.logger.error(f"❌ Error detecting activity for {chat_file}: {e}")
            return False

    def _get_chat_id(self, chat_file: Path) -> str:
        """Get unique chat ID from file"""
        # Try to read chat ID from file
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('id', data.get('chatId', str(chat_file.stem)))
        except:
            return str(chat_file.stem)

    def calculate_rename_interval(self, chat_id: str, is_active: bool) -> int:
        """
        Calculate rename interval based on activity

        - Baseline: 30 minutes
        - Active: Extends to 1 hour or longer
        - Max: 2 hours
        """
        if not is_active:
            return self.baseline_interval

        # Active work extends interval
        if chat_id in self.active_chats:
            rename_count = self.active_chats[chat_id].get('rename_count', 0)
            # Extend based on how many times we've renamed (longer active sessions)
            extension = min(rename_count * 15 * 60, self.active_extension)  # +15 min per rename, max 1 hour
            return self.baseline_interval + extension

        return self.baseline_interval + (self.active_extension // 2)  # Start with 30 min extension

    def generate_rename(self, chat_file: Path, chat_id: str, is_active: bool) -> str:
        """Generate new name for chat file"""
        try:
            # Try to read current chat data
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract meaningful info
            messages = data.get('messages', [])
            first_user_msg = next((m for m in messages if m.get('role') == 'user'), None)

            if first_user_msg:
                content = first_user_msg.get('content', '')[:50]
                # Create name from first message
                safe_name = "".join(c for c in content if c.isalnum() or c in (' ', '-', '_')).strip()
                if safe_name:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                    status = "ACTIVE" if is_active else "IDLE"
                    return f"{safe_name}_{timestamp}_{status}"

        except Exception as e:
            self.logger.debug(f"Could not read chat data: {e}")

        # Fallback naming
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        status = "ACTIVE" if is_active else "IDLE"
        chat_num = hash(chat_id) % 10000
        return f"AgentChat_{chat_num}_{timestamp}_{status}"

    def rename_chat(self, chat_file: Path) -> bool:
        """Rename a chat file"""
        try:
            chat_id = self._get_chat_id(chat_file)
            is_active = self.detect_activity(chat_file)

            # Initialize tracking
            if chat_id not in self.active_chats:
                self.active_chats[chat_id] = {
                    'last_activity': time.time(),
                    'rename_count': 0,
                    'original_name': chat_file.name
                }

            # Update activity
            if is_active:
                self.active_chats[chat_id]['last_activity'] = time.time()
                # Reset rename count on activity (screensaver concept)
                self.active_chats[chat_id]['rename_count'] = 0

            # Check if it's time to rename
            last_rename = self.active_chats[chat_id].get('last_rename', 0)
            interval = self.calculate_rename_interval(chat_id, is_active)

            if time.time() - last_rename < interval:
                return False  # Not time yet

            # Generate new name
            new_name = self.generate_rename(chat_file, chat_id, is_active)

            # Preserve extension
            new_path = chat_file.parent / f"{new_name}{chat_file.suffix}"

            # Rename
            chat_file.rename(new_path)

            # Update tracking
            self.active_chats[chat_id]['last_rename'] = time.time()
            self.active_chats[chat_id]['rename_count'] += 1
            self.activity_log.append((chat_id, time.time()))

            self.logger.info(f"✅ Renamed: {chat_file.name} → {new_name} ({'ACTIVE' if is_active else 'IDLE'})")

            return True

        except Exception as e:
            self.logger.error(f"❌ Error renaming {chat_file}: {e}")
            return False

    async def monitor_and_rename(self, check_interval: int = 60):
        """
        Monitor and rename chats continuously

        Args:
            check_interval: Seconds between checks (default 60)
        """
        self.logger.info("🔄 Starting agent chat history renamer...")
        self.logger.info(f"   Baseline: {self.baseline_interval // 60} min")
        self.logger.info(f"   Active extension: {self.active_extension // 60} min")
        self.logger.info(f"   Activity reset: {self.activity_reset_window // 60} min (screensaver)")

        while True:
            try:
                chat_files = self.get_chat_files()

                if not chat_files:
                    self.logger.debug("No chat files found, waiting...")
                    await asyncio.sleep(check_interval)
                    continue

                self.logger.info(f"📋 Found {len(chat_files)} chat files")

                renamed_count = 0
                for chat_file in chat_files:
                    if self.rename_chat(chat_file):
                        renamed_count += 1

                if renamed_count > 0:
                    self.logger.info(f"✅ Renamed {renamed_count} chats")

                # Clean old activity log (keep last hour)
                current_time = time.time()
                self.activity_log = [(cid, ts) for cid, ts in self.activity_log 
                                    if current_time - ts < 3600]

                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                self.logger.info("🛑 Stopping renamer...")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitor loop: {e}")
                await asyncio.sleep(check_interval)


async def main():
    """Main execution"""
    renamer = CursorAgentChatRenamer()

    if not renamer.chat_history_dir:
        print("⚠️ Could not find Cursor chat history directory")
        print("   Please check Cursor IDE installation")
        print("   Common locations:")
        for path in renamer.cursor_paths:
            print(f"     - {path}")
        return

    print(f"✅ Found chat history: {renamer.chat_history_dir}")
    print()
    print("💬 Cursor Agent Chat Renamer")
    print("=" * 80)
    print("Dynamic scaling with activity reset (screensaver concept)")
    print()
    print("Press Ctrl+C to stop")
    print()

    await renamer.monitor_and_rename()


if __name__ == "__main__":



    asyncio.run(main())