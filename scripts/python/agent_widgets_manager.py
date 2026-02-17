#!/usr/bin/env python3
"""
Agent Widgets Manager

Manages agent widgets for Cursor IDE and system-wide.
Creates and configures agent widgets for all virtual assistants.

Tags: #AGENT_WIDGETS #VIRTUAL_ASSISTANTS #CURSOR #IDE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AgentWidgetsManager")


class AgentWidgetsManager:
    """
    Agent Widgets Manager

    Manages agent widgets for all virtual assistants.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize agent widgets manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Agent Widgets Manager initialized")

    def create_widgets_config(self) -> Path:
        try:
            """Create agent widgets configuration"""
            config_file = self.config_dir / "agent_widgets.json"

            widgets_config = {
                "version": "1.0.0",
                "description": "Agent Widgets Configuration - All Virtual Assistants",
                "enabled": True,
                "auto_start": True,
                "widgets": [
                    {
                        "id": "jarvis_va_widget",
                        "name": "JARVIS VA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/jarvis_default_va.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "top-right",
                        "priority": 1,
                        "first_impression": True
                    },
                    {
                        "id": "jarvis_chat_widget",
                        "name": "JARVIS Chat Widget",
                        "type": "chat",
                        "script": "scripts/python/jarvis_va_chat_coordinator.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "top-left",
                        "priority": 2,
                        "first_impression": True
                    },
                    {
                        "id": "imva_widget",
                        "name": "IMVA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/jarvis_ironman_bobblehead_gui.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "bottom-right",
                        "priority": 3
                    },
                    {
                        "id": "acva_widget",
                        "name": "ACVA Widget",
                        "type": "virtual_assistant",
                        "script": "scripts/python/jarvis_acva_combat_demo.py",
                        "enabled": True,
                        "auto_start": True,
                        "position": "bottom-left",
                        "priority": 4
                    }
                ],
                "startup_order": [
                    "jarvis_va_widget",
                    "jarvis_chat_widget",
                    "imva_widget",
                    "acva_widget"
                ],
                "startup_delay_seconds": 2
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(widgets_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Agent widgets config created: {config_file.name}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in create_widgets_config: {e}", exc_info=True)
            raise
    def start_all_widgets(self) -> Dict[str, Any]:
        """Start all agent widgets"""
        logger.info("=" * 80)
        logger.info("🚀 STARTING AGENT WIDGETS")
        logger.info("=" * 80)
        logger.info("")

        config_file = self.config_dir / "agent_widgets.json"
        if not config_file.exists():
            self.create_widgets_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        result = {
            "timestamp": datetime.now().isoformat(),
            "widgets_started": 0,
            "widgets_failed": 0,
            "widgets": []
        }

        for widget_id in config.get("startup_order", []):
            widget = next((w for w in config["widgets"] if w["id"] == widget_id), None)
            if widget and widget.get("enabled", False):
                logger.info(f"   🚀 Starting: {widget['name']}")
                try:
                    script_path = self.project_root / widget["script"]
                    if script_path.exists():
                        import subprocess
                        subprocess.Popen(
                            ["python", str(script_path)],
                            cwd=str(self.project_root)
                        )
                        result["widgets_started"] += 1
                        result["widgets"].append({
                            "id": widget_id,
                            "name": widget["name"],
                            "status": "started"
                        })
                        logger.info(f"      ✅ Started")
                    else:
                        logger.warning(f"      ⚠️  Script not found: {script_path}")
                        result["widgets_failed"] += 1
                except Exception as e:
                    logger.error(f"      ❌ Failed: {e}")
                    result["widgets_failed"] += 1

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ AGENT WIDGETS STARTUP COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Started: {result['widgets_started']}")
        logger.info(f"   Failed: {result['widgets_failed']}")
        logger.info("")

        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Widgets Manager")
    parser.add_argument("--create-config", action="store_true", help="Create widgets config")
    parser.add_argument("--start", action="store_true", help="Start all widgets")

    args = parser.parse_args()

    manager = AgentWidgetsManager()

    if args.start:
        manager.start_all_widgets()
    elif args.create_config:
        manager.create_widgets_config()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())