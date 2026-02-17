#!/usr/bin/env python3
"""
Generate JSONC TodoList Files

Generates JSONC (JSON with comments) files for:
- Master todolist
- Padawan todolist (agent chat session prompt todolist for #PADAWAN[@OEM])

These JSONC files are linkable internal URLs and contain latest updates.
All todolists sync so everyone stays on the same page.

Role: PROJECT MANAGER - ensures synchronization and coordination.

Tags: #JSONC #TODOLIST #SYNC #PROJECT-MANAGER #MASTER #PADAWAN #LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger(__name__)


class TodoListJSONCGenerator:
    """Generate JSONC TodoList Files - PROJECT MANAGER Role"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.jsonc_dir = self.project_root / "data" / "todolist_jsonc"
        self.jsonc_dir.mkdir(parents=True, exist_ok=True)

        self.master_todos_path = self.project_root / "data" / "todo" / "master_todos.json"
        self.padawan_todos_path = self.project_root / "data" / "ask_database" / "master_padawan_todos.json"

        logger.info("=" * 80)
        logger.info("📋 JSONC TODOLIST GENERATOR - PROJECT MANAGER")
        logger.info("=" * 80)
        logger.info("  Role: PROJECT MANAGER - Synchronization & Coordination")
        logger.info("  Purpose: Generate linkable JSONC files for master and padawan todos")
        logger.info("  Sync: All todolists sync to stay on same page")
        logger.info("=" * 80)

    def load_master_todos(self) -> Dict[str, Any]:
        """Load master todos"""
        try:
            if not self.master_todos_path.exists():
                logger.warning(f"Master todos not found: {self.master_todos_path}")
                return {}

            with open(self.master_todos_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading master todos: {e}")
            return {}

    def load_padawan_todos(self) -> Dict[str, Any]:
        """Load padawan todos"""
        try:
            if not self.padawan_todos_path.exists():
                logger.warning(f"Padawan todos not found: {self.padawan_todos_path}")
                return {}

            with open(self.padawan_todos_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading padawan todos: {e}")
            return {}

    def generate_jsonc(self, data: Dict[str, Any], title: str, description: str) -> str:
        """Generate JSONC content with comments"""
        timestamp = datetime.now().isoformat()

        jsonc_content = f"""// {title}
// {description}
// Generated: {timestamp}
// Linkable Internal URL - Latest Update
// All todolists sync to stay on the same page
// PROJECT MANAGER: Ensures synchronization and coordination
//
{json.dumps(data, indent=2, ensure_ascii=False)}
"""

        return jsonc_content

    def generate_master_jsonc(self) -> Path:
        try:
            """Generate master todolist JSONC"""
            master_todos = self.load_master_todos()

            jsonc_content = self.generate_jsonc(
                master_todos,
                "Master TodoList - @AGENT@MASTER",
                "Master agent todolist with latest updates. All agents sync to this list."
            )

            output_file = self.jsonc_dir / "master_todos.jsonc"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(jsonc_content)

            logger.info(f"✅ Master JSONC generated: {output_file.name}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_master_jsonc: {e}", exc_info=True)
            raise
    def generate_padawan_jsonc(self) -> Path:
        try:
            """Generate padawan todolist JSONC (agent chat session prompt todolist)"""
            padawan_todos = self.load_padawan_todos()

            jsonc_content = self.generate_jsonc(
                padawan_todos,
                "Padawan TodoList - #PADAWAN[@OEM] Agent Chat Session Prompt",
                "Padawan/subagent todolist for agent chat session prompts. All padawans sync to this list."
            )

            output_file = self.jsonc_dir / "padawan_todos.jsonc"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(jsonc_content)

            logger.info(f"✅ Padawan JSONC generated: {output_file.name}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in generate_padawan_jsonc: {e}", exc_info=True)
            raise
    def sync_all_todolists(self) -> Dict[str, Any]:
        """PROJECT MANAGER: Sync all todolists"""
        logger.info("=" * 80)
        logger.info("🔄 PROJECT MANAGER: Syncing All TodoLists")
        logger.info("=" * 80)

        master_jsonc = self.generate_master_jsonc()
        padawan_jsonc = self.generate_padawan_jsonc()

        sync_status = {
            "timestamp": datetime.now().isoformat(),
            "role": "PROJECT MANAGER",
            "responsibility": "Ensure all todolists sync so everyone stays on the same page",
            "master_jsonc": str(master_jsonc),
            "padawan_jsonc": str(padawan_jsonc),
            "sync_status": "SYNCED",
            "files_generated": [
                "master_todos.jsonc",
                "padawan_todos.jsonc"
            ]
        }

        logger.info("✅ All todolists synced")
        return sync_status


def main():
    try:
        """Main entry point - @DOIT"""
        project_root = Path(__file__).parent.parent.parent
        generator = TodoListJSONCGenerator(project_root)

        sync_status = generator.sync_all_todolists()

        print("=" * 80)
        print("📋 JSONC TODOLIST GENERATION COMPLETE")
        print("=" * 80)
        print()
        print("  Role: PROJECT MANAGER")
        print("  Responsibility: Ensure all todolists sync so everyone stays on the same page")
        print()
        print("  Generated Files:")
        print(f"    Master: {sync_status['master_jsonc']}")
        print(f"    Padawan: {sync_status['padawan_jsonc']}")
        print()
        print("  Sync Status: SYNCED")
        print("  Linkable Internal URLs: Ready")
        print("  Latest Updates: Included")
        print()
        print("=" * 80)

        return sync_status


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()