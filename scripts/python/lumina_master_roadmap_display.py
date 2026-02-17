#!/usr/bin/env python3
"""
Lumina Master Roadmap Display - Persistent Focus & Productivity

Master todo list (One Ring) - persistent, overarching todos across all initiatives.
Distinguishes from Padawan/Subagent todo lists which are session-specific (per initiative).

Terminology:
- Master Todo List = One Ring = Persistent todos across all initiatives
- Padawan Todo List = Subagent Todo List = Session-specific todos (per initiative)
- Initiative = Individual agent chat session scope

Features:
- Always-visible master roadmap in chat (collapsed by default)
- Focus tracking and productivity metrics
- Integration with existing todo systems
- Distinguishes Master (persistent) vs Padawan (session/initiative-specific)
- Quick status updates
- Priority-based organization

Tags: #ROADMAP #PRODUCTIVITY #FOCUS #MASTER-TODO #PADAWAN #INITIATIVE @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaMasterRoadmap")


class LuminaMasterRoadmapDisplay:
    """
    Master Roadmap Display - Always Visible in Chat

    Provides persistent visibility of master roadmap and todos to maintain focus.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Data directory
        self.data_dir = self.project_root / "data" / "roadmap"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Roadmap file
        self.roadmap_file = self.data_dir / "master_roadmap.json"

        # Load existing roadmap
        self.roadmap = self._load_roadmap()

        # Integration with existing todo systems
        self.todo_tracker = None
        self.master_todo_display = None
        self._init_integrations()

        self.logger.info("✅ Lumina Master Roadmap Display initialized")

    def _init_integrations(self):
        """Initialize integrations with existing todo systems"""
        try:
            from master_todo_tracker import MasterTodoTracker
            self.todo_tracker = MasterTodoTracker(self.project_root)
            self.logger.info("✅ Integrated with MasterTodoTracker")
        except ImportError:
            self.logger.debug("MasterTodoTracker not available")

        try:
            from cursor_ide_master_todo_display import CursorIDEMasterTodoDisplay
            self.master_todo_display = CursorIDEMasterTodoDisplay(self.project_root)
            self.logger.info("✅ Integrated with CursorIDEMasterTodoDisplay")
        except ImportError:
            self.logger.debug("CursorIDEMasterTodoDisplay not available")

    def _load_roadmap(self) -> Dict[str, Any]:
        """Load master roadmap"""
        if self.roadmap_file.exists():
            try:
                with open(self.roadmap_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading roadmap: {e}")

        # Default roadmap structure
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "focus_areas": [],
            "current_sprint": [],
            "backlog": [],
            "completed": [],
            "blockers": [],
            "notes": []
        }

    def _save_roadmap(self):
        """Save roadmap to file"""
        try:
            self.roadmap["last_updated"] = datetime.now().isoformat()
            with open(self.roadmap_file, 'w', encoding='utf-8') as f:
                json.dump(self.roadmap, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving roadmap: {e}")

    def get_master_roadmap_display(self, include_completed: bool = False, expanded: bool = False) -> str:
        """
        Get master roadmap formatted for chat display

        Args:
            include_completed: Include completed items
            expanded: If False, show collapsed summary view (default)
        """
        lines = []

        # Header - supports multiple terminology
        lines.append("=" * 80)
        lines.append("📋 **MASTER TODO LIST** (One Ring)")
        lines.append("   *Persistent todos across all initiatives*")
        lines.append("   *Note: Padawan/Subagent todos are session-specific (per initiative)*")
        lines.append("=" * 80)
        lines.append("")

        # If collapsed, show summary only
        if not expanded:
            return self._get_collapsed_view()

        # Expanded view (full details)
        return self._get_expanded_view(include_completed)

    def _get_collapsed_view(self) -> str:
        """Get collapsed summary view (default)"""
        lines = []

        current_focus = self.roadmap.get("current_sprint", [])
        blockers = self.roadmap.get("blockers", [])
        backlog = self.roadmap.get("backlog", [])

        # Quick stats
        in_progress = len([i for i in current_focus if i.get("status") == "in_progress"])
        pending = len([i for i in current_focus if i.get("status") == "pending"])
        completed_today = len([i for i in self.roadmap.get("completed", []) 
                               if i.get("completed_date", "").startswith(datetime.now().strftime("%Y-%m-%d"))])

        lines.append("**📊 Quick Summary:**")
        lines.append(f"- 🔄 In Progress: {in_progress} | ⏳ Pending: {pending} | ✅ Completed Today: {completed_today}")
        lines.append(f"- 🚫 Blockers: {len(blockers)} | 📚 Backlog: {len(backlog)}")
        lines.append("")

        # Top 3 focus items (collapsed)
        if current_focus:
            lines.append("**🎯 Top Focus Items:**")
            for i, item in enumerate(current_focus[:3], 1):
                status = item.get("status", "pending")
                priority = item.get("priority", "medium")
                title = item.get("title", item.get("content", "Untitled"))

                status_emoji = {"in_progress": "🔄", "pending": "⏳", "blocked": "🚫"}.get(status, "⚪")
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")

                lines.append(f"  {i}. {status_emoji} {priority_emoji} {title[:60]}")

            if len(current_focus) > 3:
                lines.append(f"  ... and {len(current_focus) - 3} more items")
            lines.append("")

        # Blockers (always show even collapsed)
        if blockers:
            lines.append("**🚫 Blockers:**")
            for blocker in blockers[:2]:  # Top 2
                lines.append(f"  - 🔴 {blocker.get('title', 'Unknown blocker')[:60]}")
            if len(blockers) > 2:
                lines.append(f"  ... and {len(blockers) - 2} more blockers")
            lines.append("")

        lines.append("💡 *Type 'show master todo' or 'expand roadmap' to see full details*")
        lines.append("")
        lines.append("**Terminology:**")
        lines.append("- **Master Todo** = Persistent across all initiatives (this list)")
        lines.append("- **Padawan/Subagent Todo** = Session-specific (per initiative/chat session)")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def _get_expanded_view(self, include_completed: bool = False) -> str:
        """Get expanded full view"""
        lines = []

        # Current Focus
        current_focus = self.roadmap.get("current_sprint", [])
        if current_focus:
            lines.append("## 🎯 **CURRENT FOCUS** (Active Sprint)")
            lines.append("")
            for i, item in enumerate(current_focus, 1):  # All items when expanded
                status = item.get("status", "pending")
                priority = item.get("priority", "medium")
                title = item.get("title", item.get("content", "Untitled"))

                status_emoji = {
                    "in_progress": "🔄",
                    "pending": "⏳",
                    "blocked": "🚫",
                    "review": "👀"
                }.get(status, "⚪")

                priority_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(priority, "⚪")

                lines.append(f"{i}. {status_emoji} {priority_emoji} **{title}**")
                if item.get("description"):
                    lines.append(f"   └─ {item['description'][:80]}...")
            lines.append("")
        else:
            lines.append("## 🎯 **CURRENT FOCUS**")
            lines.append("*No active focus items. Add items to maintain productivity.*")
            lines.append("")

        # Blockers
        blockers = self.roadmap.get("blockers", [])
        if blockers:
            lines.append("## 🚫 **BLOCKERS** (Address Immediately)")
            lines.append("")
            for blocker in blockers:
                lines.append(f"- 🔴 **{blocker.get('title', 'Unknown blocker')}**")
                if blocker.get("description"):
                    lines.append(f"  └─ {blocker['description']}")
            lines.append("")

        # Focus Areas
        focus_areas = self.roadmap.get("focus_areas", [])
        if focus_areas:
            lines.append("## 📋 **FOCUS AREAS**")
            lines.append("")
            for area in focus_areas:
                name = area.get("name", "Unknown")
                progress = area.get("progress", 0)
                lines.append(f"- **{name}** - {progress}% complete")
            lines.append("")

        # Backlog Preview
        backlog = self.roadmap.get("backlog", [])
        if backlog:
            lines.append(f"## 📚 **BACKLOG** ({len(backlog)} items)")
            lines.append("")
            for item in backlog[:3]:  # Top 3
                priority = item.get("priority", "medium")
                priority_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(priority, "⚪")
                lines.append(f"- {priority_emoji} {item.get('title', 'Untitled')}")
            if len(backlog) > 3:
                lines.append(f"  ... and {len(backlog) - 3} more items")
            lines.append("")

        # Integration with Master Todos (distinct from Padawan/Subagent todos)
        if self.master_todo_display:
            try:
                master_todos = self.master_todo_display.get_master_todo_markdown(include_completed=False)
                if master_todos and "No master todos" not in master_todos:
                    lines.append("---")
                    lines.append("")
                    lines.append("## 📋 **INTEGRATED MASTER TODOS**")
                    lines.append("*These are persistent Master todos (not Padawan/Subagent session todos)*")
                    lines.append("")
                    lines.append(master_todos)
                    lines.append("")
            except Exception as e:
                self.logger.debug(f"Could not get master todos: {e}")

        # Note about Padawan/Subagent todos
        lines.append("---")
        lines.append("")
        lines.append("**Note:** Padawan/Subagent todo lists are session-specific (per initiative).")
        lines.append("They appear in individual agent chat sessions, not in this master list.")
        lines.append("")

        # Productivity Metrics
        lines.append("---")
        lines.append("")
        lines.append("## 📊 **PRODUCTIVITY METRICS**")
        lines.append("")

        # Calculate metrics
        total_items = len(current_focus) + len(backlog)
        in_progress = len([i for i in current_focus if i.get("status") == "in_progress"])
        completed_today = len([i for i in self.roadmap.get("completed", []) 
                               if i.get("completed_date", "").startswith(datetime.now().strftime("%Y-%m-%d"))])

        lines.append(f"- **Active Items:** {len(current_focus)}")
        lines.append(f"- **In Progress:** {in_progress}")
        lines.append(f"- **Blocked:** {len(blockers)}")
        lines.append(f"- **Completed Today:** {completed_today}")
        lines.append(f"- **Total Backlog:** {len(backlog)}")
        lines.append("")

        # Last Updated
        last_updated = self.roadmap.get("last_updated", "unknown")
        lines.append(f"*Last updated: {last_updated}*")
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def add_focus_item(self, title: str, description: str = "", priority: str = "medium", 
                      status: str = "pending", make_top_priority: bool = False) -> Dict[str, Any]:
        """Add item to current focus"""
        item = {
            "id": f"focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "created": datetime.now().isoformat()
        }

        if "current_sprint" not in self.roadmap:
            self.roadmap["current_sprint"] = []

        # If top priority, insert at beginning
        if make_top_priority:
            self.roadmap["current_sprint"].insert(0, item)
            item["priority"] = "critical"
            item["status"] = "in_progress"
        else:
            self.roadmap["current_sprint"].append(item)

        self._save_roadmap()

        self.logger.info(f"✅ Added focus item: {title} (priority: {item['priority']})")
        return item

    def update_focus_item(self, item_id: str, updates: Dict[str, Any]):
        """Update focus item"""
        for item in self.roadmap.get("current_sprint", []):
            if item.get("id") == item_id:
                item.update(updates)
                item["updated"] = datetime.now().isoformat()
                self._save_roadmap()
                self.logger.info(f"✅ Updated focus item: {item_id}")
                return item
        return None

    def complete_focus_item(self, item_id: str):
        """Mark focus item as completed"""
        for i, item in enumerate(self.roadmap.get("current_sprint", [])):
            if item.get("id") == item_id:
                completed_item = self.roadmap["current_sprint"].pop(i)
                completed_item["status"] = "completed"
                completed_item["completed_date"] = datetime.now().isoformat()

                if "completed" not in self.roadmap:
                    self.roadmap["completed"] = []
                self.roadmap["completed"].append(completed_item)

                self._save_roadmap()
                self.logger.info(f"✅ Completed focus item: {item_id}")
                return completed_item
        return None

    def add_blocker(self, title: str, description: str = ""):
        """Add blocker"""
        blocker = {
            "id": f"blocker_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "title": title,
            "description": description,
            "created": datetime.now().isoformat()
        }

        if "blockers" not in self.roadmap:
            self.roadmap["blockers"] = []

        self.roadmap["blockers"].append(blocker)
        self._save_roadmap()

        self.logger.info(f"🚫 Added blocker: {title}")
        return blocker

    def remove_blocker(self, blocker_id: str):
        """Remove blocker"""
        blockers = self.roadmap.get("blockers", [])
        for i, blocker in enumerate(blockers):
            if blocker.get("id") == blocker_id:
                removed = blockers.pop(i)
                self._save_roadmap()
                self.logger.info(f"✅ Removed blocker: {blocker_id}")
                return removed
        return None

    def display_roadmap(self, expanded: bool = False):
        """Display roadmap in chat

        Args:
            expanded: If True, show full expanded view. If False, show collapsed summary (default)
        """
        roadmap_display = self.get_master_roadmap_display(expanded=expanded)
        print(roadmap_display)
        return roadmap_display

    def expand_roadmap(self):
        """Display expanded roadmap view"""
        return self.display_roadmap(expanded=True)

    def collapse_roadmap(self):
        """Display collapsed roadmap view"""
        return self.display_roadmap(expanded=False)


def get_master_roadmap(project_root: Optional[Path] = None) -> LuminaMasterRoadmapDisplay:
    """Get global master roadmap instance"""
    return LuminaMasterRoadmapDisplay(project_root)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Master Roadmap Display")
    parser.add_argument("--display", action="store_true", help="Display roadmap in chat")
    parser.add_argument("--add-focus", type=str, action="append", help="Add focus item (title) - can use multiple times")
    parser.add_argument("--add-blocker", type=str, help="Add blocker (title)")
    parser.add_argument("--complete", type=str, help="Complete focus item (ID)")
    parser.add_argument("--expanded", action="store_true", help="Show expanded view (default: collapsed)")
    parser.add_argument("--collapsed", action="store_true", help="Show collapsed view (default)")

    args = parser.parse_args()

    roadmap = get_master_roadmap()

    if args.add_focus:
        for focus_title in args.add_focus:
            roadmap.add_focus_item(focus_title)
            print(f"✅ Added focus item: {focus_title}")

    if args.add_blocker:
        roadmap.add_blocker(args.add_blocker)
        print(f"🚫 Added blocker: {args.add_blocker}")

    if args.complete:
        roadmap.complete_focus_item(args.complete)
        print(f"✅ Completed item: {args.complete}")

    if args.display or not any([args.add_focus, args.add_blocker, args.complete]):
        expanded = args.expanded and not args.collapsed
        roadmap.display_roadmap(expanded=expanded)


if __name__ == "__main__":


    main()