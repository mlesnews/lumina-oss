#!/usr/bin/env python3
"""
JARVIS Task Consolidator
Consolidates redundant or duplicated tasks in the master todo list.
Identifies patterns and provides a cleaner view for the operator.

Tags: #TODO #CONSOLIDATION #CLEANUP @AUTO @JARVIS  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
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

logger = get_logger("TaskConsolidator")


class TaskConsolidator:
    """
    Consolidates redundant or duplicated tasks in the master todo list.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.todo_file = self.project_root / "data" / "todo" / "master_todos.json"

    def consolidate_tasks(self) -> Dict[str, Any]:
        """Identify and consolidate duplicated tasks"""
        self.logger.info("="*80)
        self.logger.info("CONSOLIDATING MASTER TODO LIST")
        self.logger.info("="*80)

        if not self.todo_file.exists():
            return {"success": False, "error": "master_todos.json not found"}

        try:
            with open(self.todo_file, 'r', encoding='utf-8') as f:
                todos = json.load(f)

            # 1. Identify duplicates by title
            by_title = {}
            for task_id, task in todos.items():
                title = task.get("title", "Untitled")
                if title not in by_title:
                    by_title[title] = []
                by_title[title].append(task_id)

            duplicates = {t: ids for t, ids in by_title.items() if len(ids) > 1}
            self.logger.info(f"📋 Found {len(duplicates)} duplicated task titles")

            # 2. Perform Consolidation
            new_todos = todos.copy()
            consolidated_count = 0

            for title, ids in duplicates.items():
                # Keep the first ID, remove the rest
                primary_id = ids[0]
                others = ids[1:]

                # Merge notes and metadata
                primary_task = new_todos[primary_id]
                for other_id in others:
                    other_task = new_todos[other_id]

                    # Merge notes
                    if "notes" in other_task:
                        if "notes" not in primary_task:
                            primary_task["notes"] = []
                        primary_task["notes"].extend(other_task["notes"])

                    # Remove the duplicate
                    del new_todos[other_id]
                    consolidated_count += 1

                self.logger.info(f"   ✅ Consolidated '{title}': merged {len(others)} duplicates")

            if consolidated_count > 0:
                # Save updated list
                # Backup first
                backup_path = self.todo_file.with_suffix('.json.bak')
                shutil.copy2(self.todo_file, backup_path)

                with open(self.todo_file, 'w', encoding='utf-8') as f:
                    json.dump(new_todos, f, indent=2, ensure_ascii=False)

                self.logger.info(f"✅ Successfully consolidated {consolidated_count} tasks.")
            else:
                self.logger.info("ℹ️  No duplicates found.")

            return {
                "success": True,
                "consolidated": consolidated_count,
                "duplicates_found": len(duplicates),
                "total_tasks": len(new_todos)
            }

        except Exception as e:
            self.logger.error(f"❌ Consolidation error: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import shutil
    consolidator = TaskConsolidator()
    result = consolidator.consolidate_tasks()
    print(json.dumps(result, indent=2))
