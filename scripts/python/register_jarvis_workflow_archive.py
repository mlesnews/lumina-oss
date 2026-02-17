#!/usr/bin/env python3
"""
Register JARVIS Workflow Archive Automation with JARVIS System

Registers the workflow archive automation as a JARVIS automated task.

Tags: #JARVIS #REGISTRATION #AUTOMATION #WORKFLOW #ARCHIVE @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RegisterJARVISWorkflowArchive")


def register_workflow_archive_automation(project_root: Path) -> Dict[str, Any]:
    """
    Register JARVIS Workflow Archive Automation with JARVIS system.

    Args:
        project_root: Path to project root

    Returns:
        Registration result
    """
    logger.info("📝 Registering JARVIS Workflow Archive Automation...")

    # Configuration file
    config_file = project_root / "config" / "jarvis_automations.json"
    config_file.parent.mkdir(parents=True, exist_ok=True)

    # Load existing config
    automations = {}
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                automations = json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Error loading existing config: {e}")
            automations = {}

    # Register workflow archive automation
    automations["workflow_archive_automation"] = {
        "name": "JARVIS Workflow Archive Automation",
        "type": "automated_workflow",
        "enabled": True,
        "module": "scripts/python/jarvis_workflow_archive_automation.py",
        "class": "JARVISWorkflowArchiveAutomation",
        "description": "Automatically archives AI agent history workflows that are finished and backed up to GitLens with PR",
        "features": [
            "workflow_discovery",
            "completion_detection",
            "pr_backup_verification",
            "automatic_archiving",
            "archive_review_integration"
        ],
        "schedule": {
            "type": "continuous",
            "interval_seconds": 3600,
            "enabled": True
        },
        "fullauto": True,
        "integration_points": {
            "gitlens": "jarvis_gitlens_automation",
            "workflow_manager": "cursor_chat_session_workflow_manager",
            "archive_review": "archive_review_system"
        },
        "data_directory": "data/jarvis_workflow_archive",
        "tags": ["#WORKFLOW", "#ARCHIVE", "#AUTOMATION", "#GITLENS", "#PR", "#FULLAUTO", "@JARVIS", "@DOIT"]
    }

    # Save config
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(automations, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Registered in {config_file}")
    except Exception as e:
        logger.error(f"❌ Error saving config: {e}")
        return {"success": False, "error": str(e)}

    # Also register in lumina extensions if available
    extensions_file = project_root / "config" / "lumina_extensions_integration.json"
    if extensions_file.exists():
        try:
            with open(extensions_file, 'r', encoding='utf-8') as f:
                extensions = json.load(f)

            if "extensions" not in extensions:
                extensions["extensions"] = {}

            extensions["extensions"]["jarvis_workflow_archive_automation"] = {
                "name": "JARVIS Workflow Archive Automation",
                "type": "automated_workflow",
                "enabled": True,
                "module": "scripts/python/jarvis_workflow_archive_automation.py",
                "class": "JARVISWorkflowArchiveAutomation",
                "features": [
                    "workflow_discovery",
                    "completion_detection",
                    "pr_backup_verification",
                    "automatic_archiving"
                ]
            }

            with open(extensions_file, 'w', encoding='utf-8') as f:
                json.dump(extensions, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Registered in {extensions_file}")
        except Exception as e:
            logger.warning(f"⚠️  Could not register in extensions: {e}")

    return {
        "success": True,
        "config_file": str(config_file),
        "automation": automations["workflow_archive_automation"]
    }


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Register JARVIS Workflow Archive Automation"
        )
        parser.add_argument("--project-root", type=Path,
                           help="Project root directory (auto-detects if not provided)")

        args = parser.parse_args()

        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = Path(__file__).parent.parent.parent

        print("="*80)
        print("📝 REGISTERING JARVIS WORKFLOW ARCHIVE AUTOMATION")
        print("="*80)
        print()

        result = register_workflow_archive_automation(project_root)

        if result.get("success"):
            print("✅ Registration successful!")
            print(f"   Config: {result.get('config_file')}")
            print()
            print("📋 Next steps:")
            print("   1. Run: python scripts/python/jarvis_workflow_archive_automation.py --process")
            print("   2. Or enable continuous monitoring:")
            print("      python scripts/python/jarvis_workflow_archive_automation.py --monitor")
            print()
        else:
            print(f"❌ Registration failed: {result.get('error')}")
            print()

        print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()