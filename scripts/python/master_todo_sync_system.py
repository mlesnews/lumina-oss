#!/usr/bin/env python3
"""
Master TODO Sync System
Synchronizes the Master TODO List with session progress and @ASK chain.

Implementation of Blueprint m006-2.
Links:
- MASTER_TODO.md (Source of truth for human readability)
- one_ring_blueprint.json (Source of truth for architecture)
- master_todos.json (Structured data for automation)
- holocron_master.ipynb (Interactive view)

Tags: #TODO #SYNC #MASTER_TODO #BLUEPRINT @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("MasterTodoSync")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MasterTodoSync")

try:
    from scripts.python.master_todo_from_ask_chain import MasterTodoFromAskChain
except ImportError:
    logger.error("❌ MasterTodoFromAskChain not available")
    sys.exit(1)


class MasterTodoSyncSystem:
    """Synchronizes all Master TODO sources"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.structured_todo_file = self.project_root / "data" / "todo" / "master_todos.json"
        self.markdown_todo_file = self.project_root / "MASTER_TODO.md"

        self.ask_chain_system = MasterTodoFromAskChain(self.project_root)

    def sync_all(self) -> bool:
        """Perform full synchronization"""
        logger.info("🔄 Initiating full Master TODO synchronization...")

        try:
            # 1. Generate report from ask chain
            report = self.ask_chain_system.generate_master_todo_report()
            linked_items = report.get('linked_items', [])

            # 2. Update Structured JSON
            self._update_structured_json(linked_items)

            # 3. Update Blueprint JSON
            self._update_blueprint_json(linked_items)

            # 4. (Optional) Update Markdown - usually human-edited, so be careful
            # self._update_markdown(linked_items)

            logger.info("✅ Full synchronization completed")
            return True
        except Exception as e:
            logger.error(f"❌ Synchronization failed: {e}")
            return False

    def _update_structured_json(self, linked_items: List[Dict[str, Any]]):
        try:
            """Update data/todo/master_todos.json"""
            if not self.structured_todo_file.exists():
                logger.warning(f"⚠️  Structured TODO file not found: {self.structured_todo_file}")
                return

            with open(self.structured_todo_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Update timestamps and metadata
            data["timestamp"] = datetime.now().isoformat()

            # Merge linked items into todos
            # This is a simple merge - in production, would be more complex
            current_todos = data.get("todos", [])

            # Track existing IDs
            existing_ids = {t.get("id") for s in current_todos for t in (s.get("subtasks", []) if "subtasks" in s else [s])}

            # Add new items from ask chain if they don't exist
            for item in linked_items:
                # Create a simple ID from the ask text
                ask_id = f"ask-{abs(hash(item['ask_text'])) % 10000:04d}"
                if ask_id not in existing_ids:
                    new_todo = {
                        "id": ask_id,
                        "content": item["ask_text"],
                        "status": item["status"],
                        "priority": item["priority"],
                        "category": item["category"],
                        "created": item["timestamp"] or datetime.now().strftime("%Y-%m-%d"),
                        "source": "ask_chain"
                    }
                    current_todos.append(new_todo)
                    existing_ids.add(ask_id)

            data["todos"] = current_todos

            with open(self.structured_todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Updated structured TODO file: {self.structured_todo_file}")

        except Exception as e:
            self.logger.error(f"Error in _update_structured_json: {e}", exc_info=True)
            raise
    def _update_blueprint_json(self, linked_items: List[Dict[str, Any]]):
        try:
            """Update config/one_ring_blueprint.json"""
            if not self.blueprint_file.exists():
                logger.warning(f"⚠️  Blueprint file not found: {self.blueprint_file}")
                return

            with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Update metadata
            data["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()
            data["blueprint_metadata"]["last_synced"] = datetime.now().isoformat()

            # Update master_todos section (match the structure of the blueprint)
            # Note: blueprint.master_todos is a list of top-level items
            # We'll just update the status of existing ones if matched
            blueprint_todos = data.get("master_todos", [])

            for b_todo in blueprint_todos:
                # Try to find match in linked items
                for item in linked_items:
                    if b_todo["content"].lower() in item["ask_text"].lower():
                        # Update status if item from ask chain is 'completed'
                        if item["status"] == "completed" and b_todo["status"] != "completed":
                            logger.info(f"✨ Marking blueprint task as completed: {b_todo['content']}")
                            b_todo["status"] = "completed"
                        break

            data["master_todos"] = blueprint_todos

            with open(self.blueprint_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"✅ Updated Blueprint: {self.blueprint_file}")


        except Exception as e:
            self.logger.error(f"Error in _update_blueprint_json: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    sync_system = MasterTodoSyncSystem(project_root)
    sync_system.sync_all()
    return 0


if __name__ == "__main__":

    main()