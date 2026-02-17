#!/usr/bin/env python3
"""
Short@Tag + Dewey Catalog Integrated Watcher
Combines short@tag context enhancement with Dewey Decimal cataloging

Automatically:
1. Watches chat sessions for changes
2. Enhances context with short@tags as @rules
3. Updates Dewey Decimal catalog
4. Maintains synchronized organization

Tags: #SHORTAG #DEWEY #WATCHER #INTEGRATION #CONTEXT @JARVIS
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from shortag_chat_context_enhancer import ShortagChatContextEnhancer
from dewey_decimal_chat_catalog import DeweyDecimalChatCatalog

logger = get_logger("ShortagDeweyWatcher")


class ShortagDeweyIntegratedWatcher:
    """
    Integrated watcher for short@tag context enhancement and Dewey cataloging

    Combines both systems to provide:
    - Real-time context enhancement with short@tags as @rules
    - Automatic Dewey Decimal cataloging
    - Synchronized updates
    """

    def __init__(self, project_root: Optional[Path] = None, watch_interval: int = 30):
        """Initialize integrated watcher"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.watch_interval = watch_interval
        self.logger = logger

        # Initialize systems
        self.context_enhancer = ShortagChatContextEnhancer(project_root)
        self.dewey_catalog = DeweyDecimalChatCatalog(project_root)

        # Track last scan
        self.last_scan_time = datetime.now()
        self.session_timestamps: Dict[str, float] = {}

        logger.info("👁️  Short@Tag + Dewey Integrated Watcher initialized")
        logger.info(f"   Watch interval: {watch_interval}s")

    def watch_and_update(self, max_iterations: Optional[int] = None) -> None:
        """Watch for changes and update both systems"""
        self.logger.info("👁️  Starting integrated watcher...")
        self.logger.info("   Press Ctrl+C to stop")

        iteration = 0
        try:
            while True:
                iteration += 1
                if max_iterations and iteration > max_iterations:
                    break

                self.logger.debug(f"🔍 Scan iteration {iteration}...")
                self._scan_and_update()

                time.sleep(self.watch_interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Watcher stopped by user")
        except Exception as e:
            self.logger.error(f"❌ Watcher error: {e}", exc_info=True)

    def _scan_and_update(self) -> None:
        """Scan sessions and update both systems"""
        updated_enhancements = 0
        updated_catalog = 0

        # Scan master chat session
        master_chat_file = self.project_root / "data" / "master_chat" / "master_session.json"
        if master_chat_file.exists():
            mtime = master_chat_file.stat().st_mtime
            session_id = "jarvis_master_chat"

            if session_id not in self.session_timestamps or self.session_timestamps[session_id] < mtime:
                try:
                    with open(master_chat_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session_title = data.get('session_name', 'JARVIS Master Chat')
                        content = json.dumps(data)
                        messages = data.get('messages', [])

                        # Enhance context
                        enhancement = self.context_enhancer.enhance_session_context(
                            session_id, session_title, content
                        )
                        updated_enhancements += 1

                        # Update catalog
                        self.dewey_catalog.add_or_update_session(
                            session_id=session_id,
                            session_title=session_title,
                            content=content,
                            agent_count=len(data.get('consolidated_agents', [])),
                            message_count=len(messages),
                            created_at=data.get('created_at'),
                            last_updated=data.get('last_activity')
                        )
                        updated_catalog += 1

                        self.session_timestamps[session_id] = mtime
                        self.logger.info(f"📝 Updated: {session_title} (enhanced + cataloged)")
                except Exception as e:
                    self.logger.warning(f"⚠️  Error updating master chat: {e}")

        # Scan agent chat sessions
        sessions_dir = self.project_root / "data" / "agent_chat_sessions"
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                mtime = session_file.stat().st_mtime
                session_id = session_file.stem

                if session_id not in self.session_timestamps or self.session_timestamps[session_id] < mtime:
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            session_title = data.get('session_name') or data.get('title') or session_id
                            content = json.dumps(data)
                            messages = data.get('messages', [])

                            # Enhance context
                            enhancement = self.context_enhancer.enhance_session_context(
                                session_id, session_title, content
                            )
                            updated_enhancements += 1

                            # Update catalog
                            self.dewey_catalog.add_or_update_session(
                                session_id=session_id,
                                session_title=session_title,
                                content=content,
                                agent_count=len(data.get('agents', [])),
                                message_count=len(messages),
                                created_at=data.get('created_at'),
                                last_updated=data.get('last_updated') or data.get('last_activity')
                            )
                            updated_catalog += 1

                            self.session_timestamps[session_id] = mtime
                            self.logger.info(f"📝 Updated: {session_title} (enhanced + cataloged)")
                    except Exception as e:
                        self.logger.warning(f"⚠️  Error updating {session_file}: {e}")

        if updated_enhancements > 0 or updated_catalog > 0:
            self.logger.info(f"✅ Updated {updated_enhancements} enhancements, {updated_catalog} catalog entries")

    def initial_scan(self) -> Dict[str, Any]:
        """Perform initial full scan"""
        self.logger.info("🔍 Performing initial integrated scan...")

        # Enhance all sessions
        enhancements = self.context_enhancer.enhance_all_sessions()

        # Scan and catalog all sessions
        catalog_result = self.dewey_catalog.scan_and_catalog_sessions()

        result = {
            "enhancements": len(enhancements),
            "catalog_entries": catalog_result.get("sessions_cataloged", 0),
            "total_sessions": catalog_result.get("sessions_found", 0)
        }

        self.logger.info(f"✅ Initial scan complete: {result['enhancements']} enhanced, {result['catalog_entries']} cataloged")
        return result


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Short@Tag + Dewey Integrated Watcher")
    parser.add_argument("--watch", action="store_true", help="Start watching for changes")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    parser.add_argument("--scan", action="store_true", help="Perform initial scan")
    parser.add_argument("--iterations", type=int, help="Max watch iterations")

    args = parser.parse_args()

    watcher = ShortagDeweyIntegratedWatcher(watch_interval=args.interval)

    if args.scan:
        watcher.initial_scan()

    if args.watch:
        watcher.watch_and_update(max_iterations=args.iterations)
    elif not args.scan:
        parser.print_help()


if __name__ == "__main__":


    main()