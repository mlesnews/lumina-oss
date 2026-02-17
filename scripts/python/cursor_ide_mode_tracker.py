#!/usr/bin/env python3
"""
Cursor IDE Mode Time Tracker
Tracks time spent in @Agents mode vs @Editor mode

Tracks and displays time spent in:
- @Agents mode (chat, agent interactions)
- @Editor mode (code editing, file navigation)

Tags: #CURSOR #IDE #TIME-TRACKING #ANALYTICS #AGENTS #EDITOR
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIDEModeTracker")


class CursorIDEModeTracker:
    """
    Cursor IDE Mode Time Tracker

    Tracks time spent in:
    - @Agents mode (chat, agent interactions)
    - @Editor mode (code editing, file navigation)
    """

    MODE_AGENTS = "@Agents"
    MODE_EDITOR = "@Editor"

    def __init__(self, project_root: Path):
        """Initialize mode tracker"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.tracker_data_path = self.data_path / "cursor_ide_mode_tracker"
        self.tracker_data_path.mkdir(parents=True, exist_ok=True)

        # Data files
        self.sessions_file = self.tracker_data_path / "sessions.json"
        self.daily_stats_file = self.tracker_data_path / "daily_stats.json"
        self.current_session_file = self.tracker_data_path / "current_session.json"

        # Current state
        self.current_mode = None
        self.mode_start_time = None
        self.current_session = self._load_current_session()

        # Load historical data
        self.sessions = self._load_sessions()
        self.daily_stats = self._load_daily_stats()

        self.logger.info("⏱️  Cursor IDE Mode Tracker initialized")

    def _load_current_session(self) -> Dict[str, Any]:
        """Load current session"""
        if self.current_session_file.exists():
            try:
                with open(self.current_session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    # Restore mode start time if session is active
                    if session.get("active") and session.get("current_mode"):
                        self.current_mode = session.get("current_mode")
                        mode_start = session.get("mode_start_time")
                        if mode_start:
                            self.mode_start_time = datetime.fromisoformat(mode_start)
                    return session
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading current session: {e}")

        return {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "active": True,
            "current_mode": None,
            "mode_start_time": None,
            "time_by_mode": {
                self.MODE_AGENTS: 0.0,
                self.MODE_EDITOR: 0.0
            }
        }

    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load historical sessions"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading sessions: {e}")

        return []

    def _load_daily_stats(self) -> Dict[str, Any]:
        """Load daily statistics"""
        if self.daily_stats_file.exists():
            try:
                with open(self.daily_stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading daily stats: {e}")

        return {}

    def _save_current_session(self):
        """Save current session"""
        self.current_session["current_mode"] = self.current_mode
        self.current_session["mode_start_time"] = self.mode_start_time.isoformat() if self.mode_start_time else None

        try:
            with open(self.current_session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving current session: {e}")

    def _save_sessions(self):
        """Save sessions"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving sessions: {e}")

    def _save_daily_stats(self):
        """Save daily statistics"""
        try:
            with open(self.daily_stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.daily_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving daily stats: {e}")

    def switch_mode(self, mode: str):
        """
        Switch to a different mode

        Args:
            mode: Either "@Agents" or "@Editor"
        """
        now = datetime.now()

        # If switching from a previous mode, record the time
        if self.current_mode and self.mode_start_time:
            elapsed = (now - self.mode_start_time).total_seconds()
            self.current_session["time_by_mode"][self.current_mode] += elapsed

            # Update daily stats
            today = now.strftime("%Y-%m-%d")
            if today not in self.daily_stats:
                self.daily_stats[today] = {
                    self.MODE_AGENTS: 0.0,
                    self.MODE_EDITOR: 0.0
                }
            self.daily_stats[today][self.current_mode] += elapsed

            self.logger.info(f"⏱️  Recorded {elapsed:.1f}s in {self.current_mode} mode")

        # Switch to new mode
        self.current_mode = mode
        self.mode_start_time = now

        self._save_current_session()
        self._save_daily_stats()

        self.logger.info(f"🔄 Switched to {mode} mode")

    def get_current_time(self) -> Dict[str, float]:
        """Get current time in each mode (including active session)"""
        now = datetime.now()
        time_by_mode = self.current_session["time_by_mode"].copy()

        # Add current active mode time
        if self.current_mode and self.mode_start_time:
            elapsed = (now - self.mode_start_time).total_seconds()
            time_by_mode[self.current_mode] = time_by_mode.get(self.current_mode, 0.0) + elapsed

        return time_by_mode

    def get_today_stats(self) -> Dict[str, Any]:
        """Get today's statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_stats = self.daily_stats.get(today, {
            self.MODE_AGENTS: 0.0,
            self.MODE_EDITOR: 0.0
        }).copy()

        # Add current session time
        current_time = self.get_current_time()
        today_stats[self.MODE_AGENTS] += current_time.get(self.MODE_AGENTS, 0.0)
        today_stats[self.MODE_EDITOR] += current_time.get(self.MODE_EDITOR, 0.0)

        total = today_stats[self.MODE_AGENTS] + today_stats[self.MODE_EDITOR]

        return {
            "date": today,
            "time_by_mode": today_stats,
            "total_time": total,
            "percentages": {
                self.MODE_AGENTS: (today_stats[self.MODE_AGENTS] / total * 100) if total > 0 else 0.0,
                self.MODE_EDITOR: (today_stats[self.MODE_EDITOR] / total * 100) if total > 0 else 0.0
            }
        }

    def get_weekly_stats(self) -> Dict[str, Any]:
        """Get weekly statistics"""
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())

        weekly_stats = {
            self.MODE_AGENTS: 0.0,
            self.MODE_EDITOR: 0.0
        }

        for i in range(7):
            date = (week_start + timedelta(days=i)).strftime("%Y-%m-%d")
            day_stats = self.daily_stats.get(date, {})
            weekly_stats[self.MODE_AGENTS] += day_stats.get(self.MODE_AGENTS, 0.0)
            weekly_stats[self.MODE_EDITOR] += day_stats.get(self.MODE_EDITOR, 0.0)

        # Add current session if today is in this week
        if now.strftime("%Y-%m-%d") >= week_start.strftime("%Y-%m-%d"):
            current_time = self.get_current_time()
            weekly_stats[self.MODE_AGENTS] += current_time.get(self.MODE_AGENTS, 0.0)
            weekly_stats[self.MODE_EDITOR] += current_time.get(self.MODE_EDITOR, 0.0)

        total = weekly_stats[self.MODE_AGENTS] + weekly_stats[self.MODE_EDITOR]

        return {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "time_by_mode": weekly_stats,
            "total_time": total,
            "percentages": {
                self.MODE_AGENTS: (weekly_stats[self.MODE_AGENTS] / total * 100) if total > 0 else 0.0,
                self.MODE_EDITOR: (weekly_stats[self.MODE_EDITOR] / total * 100) if total > 0 else 0.0
            }
        }

    def end_session(self):
        """End current session and save to history"""
        if self.current_mode and self.mode_start_time:
            now = datetime.now()
            elapsed = (now - self.mode_start_time).total_seconds()
            self.current_session["time_by_mode"][self.current_mode] += elapsed

            # Update daily stats
            today = now.strftime("%Y-%m-%d")
            if today not in self.daily_stats:
                self.daily_stats[today] = {
                    self.MODE_AGENTS: 0.0,
                    self.MODE_EDITOR: 0.0
                }
            self.daily_stats[today][self.current_mode] += elapsed

        # Finalize session
        self.current_session["end_time"] = datetime.now().isoformat()
        self.current_session["active"] = False

        # Save to history
        self.sessions.append(self.current_session.copy())
        self._save_sessions()

        # Start new session
        self.current_session = {
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "active": True,
            "current_mode": None,
            "mode_start_time": None,
            "time_by_mode": {
                self.MODE_AGENTS: 0.0,
                self.MODE_EDITOR: 0.0
            }
        }
        self.current_mode = None
        self.mode_start_time = None

        self._save_current_session()
        self.logger.info("✅ Session ended and saved")

    def get_cursor_ide_display(self) -> str:
        """Get formatted display for Cursor IDE chat"""
        today_stats = self.get_today_stats()
        current_time = self.get_current_time()

        markdown = []
        markdown.append("## ⏱️ Cursor IDE Mode Time Tracker")
        markdown.append("")
        markdown.append("### 📊 Today's Statistics")
        markdown.append("")

        # Format time
        def format_time(seconds: float) -> str:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"

        agents_time = today_stats["time_by_mode"][self.MODE_AGENTS]
        editor_time = today_stats["time_by_mode"][self.MODE_EDITOR]
        total_time = today_stats["total_time"]

        markdown.append(f"**@Agents Mode:** {format_time(agents_time)} ({today_stats['percentages'][self.MODE_AGENTS]:.1f}%)")
        markdown.append("")
        markdown.append(f"**@Editor Mode:** {format_time(editor_time)} ({today_stats['percentages'][self.MODE_EDITOR]:.1f}%)")
        markdown.append("")
        markdown.append(f"**Total Time:** {format_time(total_time)}")
        markdown.append("")

        # Current mode
        if self.current_mode:
            current_elapsed = (datetime.now() - self.mode_start_time).total_seconds() if self.mode_start_time else 0
            markdown.append(f"**Current Mode:** {self.current_mode} (active for {format_time(current_elapsed)})")
        else:
            markdown.append("**Current Mode:** None (not tracking)")

        markdown.append("")
        markdown.append("---")
        markdown.append("")

        # Weekly stats
        weekly_stats = self.get_weekly_stats()
        markdown.append("### 📈 Weekly Statistics")
        markdown.append("")
        markdown.append(f"**@Agents Mode:** {format_time(weekly_stats['time_by_mode'][self.MODE_AGENTS])} ({weekly_stats['percentages'][self.MODE_AGENTS]:.1f}%)")
        markdown.append("")
        markdown.append(f"**@Editor Mode:** {format_time(weekly_stats['time_by_mode'][self.MODE_EDITOR])} ({weekly_stats['percentages'][self.MODE_EDITOR]:.1f}%)")
        markdown.append("")
        markdown.append(f"**Total Time:** {format_time(weekly_stats['total_time'])}")
        markdown.append("")

        return "\n".join(markdown)

    def display_in_chat(self):
        """Display time tracking in Cursor IDE chat"""
        markdown = self.get_cursor_ide_display()
        print(markdown)
        return markdown


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Mode Time Tracker")
        parser.add_argument("--switch-agents", action="store_true", help="Switch to @Agents mode")
        parser.add_argument("--switch-editor", action="store_true", help="Switch to @Editor mode")
        parser.add_argument("--display", action="store_true", help="Display time tracking")
        parser.add_argument("--today", action="store_true", help="Show today's stats")
        parser.add_argument("--week", action="store_true", help="Show weekly stats")
        parser.add_argument("--end-session", action="store_true", help="End current session")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = CursorIDEModeTracker(project_root)

        if args.switch_agents:
            tracker.switch_mode(tracker.MODE_AGENTS)
            print(f"✅ Switched to {tracker.MODE_AGENTS} mode")

        elif args.switch_editor:
            tracker.switch_mode(tracker.MODE_EDITOR)
            print(f"✅ Switched to {tracker.MODE_EDITOR} mode")

        elif args.display:
            tracker.display_in_chat()

        elif args.today:
            stats = tracker.get_today_stats()
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"\n📊 Today's Statistics ({stats['date']})")
                print(f"@Agents: {stats['time_by_mode'][tracker.MODE_AGENTS]:.1f}s ({stats['percentages'][tracker.MODE_AGENTS]:.1f}%)")
                print(f"@Editor: {stats['time_by_mode'][tracker.MODE_EDITOR]:.1f}s ({stats['percentages'][tracker.MODE_EDITOR]:.1f}%)")
                print(f"Total: {stats['total_time']:.1f}s")

        elif args.week:
            stats = tracker.get_weekly_stats()
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"\n📈 Weekly Statistics (Week starting {stats['week_start']})")
                print(f"@Agents: {stats['time_by_mode'][tracker.MODE_AGENTS]:.1f}s ({stats['percentages'][tracker.MODE_AGENTS]:.1f}%)")
                print(f"@Editor: {stats['time_by_mode'][tracker.MODE_EDITOR]:.1f}s ({stats['percentages'][tracker.MODE_EDITOR]:.1f}%)")
                print(f"Total: {stats['total_time']:.1f}s")

        elif args.end_session:
            tracker.end_session()
            print("✅ Session ended")

        else:
            tracker.display_in_chat()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()