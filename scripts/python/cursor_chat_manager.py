#!/usr/bin/env python3
"""
Cursor Chat Manager - Pin, Archive, Rename Chats

Manages Cursor IDE agent chats:
- Pin chats
- Archive chats
- Rename chats dynamically
- Integration with session ask resolver
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class CursorChatManager:
    """
    Cursor Chat Manager

    Manages agent chats in Cursor IDE:
    - Pin/unpin
    - Archive/unarchive
    - Rename
    """

    def __init__(self):
        self.app_data = Path(os.environ.get('APPDATA', ''))
        self.history_dir = self.app_data / "Cursor" / "User" / "History"

        # Metadata file for pins/archives
        self.metadata_file = self.history_dir / ".chat_metadata.json"

        self.logger = self._setup_logging()
        self.metadata = self._load_metadata()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("CursorChatManager")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 💬 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _load_metadata(self) -> Dict[str, Any]:
        """Load chat metadata (pins, archives)"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading metadata: {e}")

        return {
            'pinned': [],
            'archived': [],
            'renames': {}
        }

    def _save_metadata(self):
        """Save chat metadata"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")

    def pin_chat(self, chat_file: Path) -> bool:
        """Pin a chat"""
        try:
            chat_id = self._get_chat_id(chat_file)

            if chat_id not in self.metadata['pinned']:
                self.metadata['pinned'].append(chat_id)
                self._save_metadata()
                self.logger.info(f"📌 Pinned chat: {chat_file.name}")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Error pinning chat: {e}")
            return False

    def unpin_chat(self, chat_file: Path) -> bool:
        """Unpin a chat"""
        try:
            chat_id = self._get_chat_id(chat_file)

            if chat_id in self.metadata['pinned']:
                self.metadata['pinned'].remove(chat_id)
                self._save_metadata()
                self.logger.info(f"📌 Unpinned chat: {chat_file.name}")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Error unpinning chat: {e}")
            return False

    def archive_chat(self, chat_file: Path, archive_name: Optional[str] = None) -> bool:
        """Archive a chat"""
        try:
            chat_id = self._get_chat_id(chat_file)

            # Create archive directory
            archive_dir = self.history_dir / "archived"
            archive_dir.mkdir(exist_ok=True)

            # Move to archive
            if archive_name is None:
                archive_name = f"{chat_file.stem}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            archive_path = archive_dir / f"{archive_name}{chat_file.suffix}"
            chat_file.rename(archive_path)

            # Update metadata
            if chat_id not in self.metadata['archived']:
                self.metadata['archived'].append(chat_id)
            if chat_id in self.metadata['pinned']:
                self.metadata['pinned'].remove(chat_id)

            self._save_metadata()
            self.logger.info(f"📦 Archived chat: {chat_file.name} → {archive_path.name}")

            return True
        except Exception as e:
            self.logger.error(f"Error archiving chat: {e}")
            return False

    def rename_chat(self, chat_file: Path, new_name: str) -> bool:
        """Rename a chat"""
        try:
            chat_id = self._get_chat_id(chat_file)

            # Preserve extension
            new_path = chat_file.parent / f"{new_name}{chat_file.suffix}"

            # Rename
            chat_file.rename(new_path)

            # Track rename
            self.metadata['renames'][chat_id] = {
                'old_name': chat_file.name,
                'new_name': new_path.name,
                'timestamp': datetime.now().isoformat()
            }
            self._save_metadata()

            self.logger.info(f"✏️ Renamed chat: {chat_file.name} → {new_path.name}")

            return True
        except Exception as e:
            self.logger.error(f"Error renaming chat: {e}")
            return False

    def pin_archive_rename_chat(self, chat_file: Path, final_name: str) -> bool:
        """
        Complete workflow: Pin, Archive, Rename

        For resolved and approved sessions
        """
        try:
            # Step 1: Pin
            self.pin_chat(chat_file)

            # Step 2: Rename with final status
            status_name = f"{final_name}_VERIFIED_APPROVED_{datetime.now().strftime('%Y%m%d')}"
            self.rename_chat(chat_file, status_name)

            # Step 3: Archive
            self.archive_chat(chat_file, status_name)

            self.logger.info(f"✅ Completed pin/archive/rename workflow for: {chat_file.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error in pin/archive/rename workflow: {e}")
            return False

    def _get_chat_id(self, chat_file: Path) -> str:
        """Get chat ID from file"""
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('id', data.get('chatId', str(chat_file.stem)))
        except:
            return str(chat_file.stem)


def main():
    """Main execution"""
    manager = CursorChatManager()

    print("💬 Cursor Chat Manager")
    print("=" * 80)
    print(f"History directory: {manager.history_dir}")
    print(f"Pinned chats: {len(manager.metadata['pinned'])}")
    print(f"Archived chats: {len(manager.metadata['archived'])}")


if __name__ == "__main__":



    main()