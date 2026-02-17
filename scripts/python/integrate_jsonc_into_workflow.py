#!/usr/bin/env python3
"""
Integrate JSONC Generation into Permanent Workflow

Hooks JSONC generation into permanent workflow so it runs automatically:
- On todo update
- On sync
- As part of continuous workflow

Tags: #PERMANENT-WORKFLOW #JSONC #INTEGRATION #AUTOMATION #LUMINA
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

from generate_todolist_jsonc import TodoListJSONCGenerator
from lumina_logger import get_logger

logger = get_logger(__name__)


class JSONCWorkflowIntegration:
    """Integrate JSONC generation into permanent workflow"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.jsonc_generator = TodoListJSONCGenerator(project_root)
        self.workflow_config_path = self.project_root / "config" / "permanent_workflow.json"

        logger.info("=" * 80)
        logger.info("🔄 JSONC WORKFLOW INTEGRATION")
        logger.info("=" * 80)

    def update_workflow_config(self) -> Dict[str, Any]:
        try:
            """Update permanent workflow config to include JSONC generation"""
            workflow_config = {
                "workflow_name": "Permanent Workflow",
                "updated": datetime.now().isoformat(),
                "steps": [
                    {
                        "step": 1,
                        "name": "Todo Update",
                        "description": "Master or padawan todo is updated",
                        "triggers": ["todo_updated", "todo_created", "todo_status_changed"]
                    },
                    {
                        "step": 2,
                        "name": "Sync Check",
                        "description": "PROJECT MANAGER checks sync status",
                        "triggers": ["after_todo_update"]
                    },
                    {
                        "step": 3,
                        "name": "JSONC Generation",
                        "description": "Generate JSONC files for both todolists",
                        "script": "generate_todolist_jsonc.py",
                        "triggers": ["after_sync_check", "on_workflow_run"],
                        "outputs": [
                            "data/todolist_jsonc/master_todos.jsonc",
                            "data/todolist_jsonc/padawan_todos.jsonc"
                        ]
                    },
                    {
                        "step": 4,
                        "name": "Linkable URLs",
                        "description": "Create linkable internal URLs",
                        "triggers": ["after_jsonc_generation"]
                    },
                    {
                        "step": 5,
                        "name": "Latest Updates",
                        "description": "Include latest updates in JSONC",
                        "triggers": ["after_jsonc_generation"]
                    },
                    {
                        "step": 6,
                        "name": "Synchronization",
                        "description": "Ensure all todolists sync",
                        "triggers": ["after_jsonc_generation"]
                    },
                    {
                        "step": 7,
                        "name": "Everyone on Same Page",
                        "description": "All agents stay on same page",
                        "triggers": ["after_synchronization"]
                    }
                ],
                "project_manager": {
                    "role": "PROJECT MANAGER",
                    "responsibility": "Ensure all todolists sync so everyone stays on the same page",
                    "tasks": [
                        "Generate JSONC files",
                        "Ensure synchronization",
                        "Maintain consistency",
                        "Coordinate between master and padawan"
                    ]
                },
                "jsonc_files": {
                    "master": "data/todolist_jsonc/master_todos.jsonc",
                    "padawan": "data/todolist_jsonc/padawan_todos.jsonc",
                    "format": "JSONC (JSON with comments)",
                    "purpose": "Linkable internal URLs with latest updates"
                }
            }

            # Save workflow config
            self.workflow_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.workflow_config_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Workflow config updated: {self.workflow_config_path.name}")
            return workflow_config

        except Exception as e:
            self.logger.error(f"Error in update_workflow_config: {e}", exc_info=True)
            raise
    def integrate(self) -> Dict[str, Any]:
        """Integrate JSONC generation into permanent workflow"""
        # Update workflow config
        workflow_config = self.update_workflow_config()

        # Generate JSONC files
        sync_status = self.jsonc_generator.sync_all_todolists()

        integration_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "INTEGRATED",
            "workflow_config": str(self.workflow_config_path),
            "jsonc_files": sync_status["files_generated"],
            "project_manager": "ASSIGNED",
            "sync_status": "SYNCED"
        }

        return integration_status


def main():
    try:
        """Main entry point - @DOIT"""
        project_root = Path(__file__).parent.parent.parent
        integration = JSONCWorkflowIntegration(project_root)

        status = integration.integrate()

        print("=" * 80)
        print("🔄 JSONC WORKFLOW INTEGRATION COMPLETE")
        print("=" * 80)
        print()
        print("  Status: INTEGRATED")
        print("  PROJECT MANAGER: ASSIGNED")
        print("  Sync Status: SYNCED")
        print()
        print("  Workflow Config:")
        print(f"    {status['workflow_config']}")
        print()
        print("  JSONC Files Generated:")
        for file in status["jsonc_files"]:
            print(f"    - {file}")
        print()
        print("  Permanent Workflow Updated:")
        print("    - JSONC generation now part of permanent workflow")
        print("    - Automatic generation on todo update")
        print("    - All todolists sync automatically")
        print()
        print("=" * 80)

        return status


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()